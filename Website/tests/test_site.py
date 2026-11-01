"""Behavior checks: real accounts, private conversations, exact catalogs and payments."""
from pathlib import Path
import hashlib, hmac, json, re, time
import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app, ROOT
from i18n import translations

@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.setenv('TECHVERSE_INSTANCE_DIR',str(tmp_path/'instance'))
    return create_app({'TESTING':True,'DATABASE':str(tmp_path/'test.db'),'SECRET_KEY':'test-only-key',
        'OPENAI_API_KEY':'','STRIPE_SECRET_KEY':'','STRIPE_WEBHOOK_SECRET':'','STRIPE_PRICE_ID':'','PUBLIC_BASE_URL':''})

@pytest.fixture
def client(app):return app.test_client()

def csrf(client):
    client.get('/')
    with client.session_transaction() as session:return session['csrf']

def post(client,path,data=None,json_data=None):
    token=csrf(client)
    if json_data is not None:return client.post(path,json=json_data,headers={'X-CSRF-Token':token})
    return client.post(path,data={**(data or {}),'csrf_token':token})

def user(app,email='member@example.com',role='user',status='none'):
    with app.app_context():
        db=app.get_db();uid=db.execute('INSERT INTO users(full_name,email,password,role,membership_status,phone) VALUES(?,?,?,?,?,?)',
            ('Test Member',email,generate_password_hash('correct-password'),role,status,'+96171234567')).lastrowid;db.commit();return uid

def login_as(client,uid):
    with client.session_transaction() as s:s['user_id']=uid

def member_status(app,uid):
    with app.app_context():return app.get_db().execute('SELECT membership_status FROM users WHERE id=?',(uid,)).fetchone()[0]

PUBLIC=['/','/contact','/about','/privacy','/login','/register']
PRIVATE=['/membership/apply','/shop','/shop/all','/advisor','/membership','/cart','/learn','/videos','/companies','/sources','/sources/photos','/shop/product/tv-001']
@pytest.mark.parametrize('language',['en','ar'])
@pytest.mark.parametrize('path',PUBLIC)
def test_public_pages(client,path,language):
    with client.session_transaction() as s:s['language']=language
    response=client.get(path);assert response.status_code==200
    assert f'lang="{language}"'.encode() in response.data
    assert ('dir="rtl"' if language=='ar' else 'dir="ltr"').encode() in response.data
    assert response.headers['X-Content-Type-Options']=='nosniff'
    assert b'csrf-token' in response.data

@pytest.mark.parametrize('language',['en','ar'])
@pytest.mark.parametrize('path',PRIVATE)
def test_signed_in_pages(app,client,path,language):
    login_as(client,user(app))
    with client.session_transaction() as s:s['language']=language
    response=client.get(path);assert response.status_code==200
    assert f'lang="{language}"'.encode() in response.data
    assert ('dir="rtl"' if language=='ar' else 'dir="ltr"').encode() in response.data

@pytest.mark.parametrize('path',PRIVATE+['/settings','/admin','/companies/register'])
def test_anonymous_visitors_must_sign_in(client,path):
    response=client.get(path)
    assert response.status_code==302 and response.location.startswith('/login?next=')

@pytest.mark.parametrize('path',['/api/products','/api/catalogs','/api/lookup?model=growatt-spf-5000-es&code=01','/api/conversations'])
def test_anonymous_api_data_is_protected(client,path):
    response=client.get(path);assert response.status_code==401 and response.is_json
    assert response.get_json()['login_url']=='/login'

def test_welcome_signin_enter_and_logout_flow(app,client):
    page=client.get('/').data
    assert b'id="featured"' in page and b'id="shop-search"' not in page and b'entry-form-panel' not in page
    assert b'/login?next=/shop/product/tv-001' in page and b'/login?next=/advisor' in page
    assert b'data-add-cart' not in page and b'id="chat-form"' not in page
    user(app)
    response=post(client,'/login',{'email':'member@example.com','password':'correct-password','next':'/'})
    assert response.location=='/shop'
    assert client.get('/').location=='/shop' and client.get('/shop').status_code==200
    assert post(client,'/logout').location=='/'
    assert b'id="featured"' in client.get('/').data and client.get('/shop').status_code==302
    assert client.get('/api/products').status_code==401

@pytest.mark.parametrize('return_to',['/shop?category=boards','/advisor','https://untrusted.example/','//untrusted.example/','/\\untrusted.example/'])
def test_signin_return_paths(app,client,return_to):
    user(app)
    response=post(client,'/login',{'email':'member@example.com','password':'correct-password','next':return_to})
    assert response.location==(return_to if return_to.startswith(('/shop','/advisor')) else '/shop')

def test_startup_with_windows_cp1252_default(tmp_path,monkeypatch):
    original_read=Path.read_text
    # This is the exact failure raised by Windows for the Arabic UTF-8 data.
    with pytest.raises(UnicodeDecodeError):original_read(ROOT/'data/products.json',encoding='cp1252')
    def windows_read(path,*args,**kwargs):
        if not args and kwargs.get('encoding') is None:kwargs['encoding']='cp1252'
        return original_read(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',windows_read)
    application=create_app({'TESTING':True,'DATABASE':str(tmp_path/'windows.db'),'SECRET_KEY':'test-only-key'})
    client=application.test_client()
    assert client.get('/api/health').get_json()=={'ok':True,'products':116,'models':16}
    login_as(client,user(application))
    with client.session_transaction() as session:session['language']='ar'
    assert 'طقم أردوينو'.encode() in client.get('/shop').data
    result=client.get('/api/lookup',query_string={'model':'growatt-spf-5000-es','type':'Fault','code':'01'})
    assert result.status_code==200 and 'مروحة' in result.get_json()['name']

def test_catalog_generators_with_windows_cp1252_default(tmp_path,monkeypatch):
    import runpy
    original_read,original_write=Path.read_text,Path.write_text
    def windows_read(path,*args,**kwargs):
        if not args and kwargs.get('encoding') is None:kwargs['encoding']='cp1252'
        return original_read(path,*args,**kwargs)
    def windows_write(path,data,*args,**kwargs):
        if not args and kwargs.get('encoding') is None:kwargs['encoding']='cp1252'
        return original_write(path,data,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',windows_read);monkeypatch.setattr(Path,'write_text',windows_write)
    (tmp_path/'tools').mkdir();(tmp_path/'data').mkdir()
    for name in ['build_catalogs.py','build_product_images.py']:
        (tmp_path/'tools'/name).write_bytes((ROOT/'tools'/name).read_bytes())
    sample={'id':'tv-001','name':'Arduino UNO R3 kit','name_ar':'طقم أردوينو','category':'kits','image_path':'images/products/tv-001.svg'}
    (tmp_path/'data/products.json').write_bytes(json.dumps([sample],ensure_ascii=False).encode('utf-8'))
    runpy.run_path(str(tmp_path/'tools/build_catalogs.py'),run_name='__main__')
    catalog=json.loads((tmp_path/'data/catalogs.json').read_text(encoding='utf-8'))
    assert len(catalog['catalogs'])==11 and 'دليل' in catalog['catalogs'][0]['source']['title_ar']
    runpy.run_path(str(tmp_path/'tools/build_product_images.py'),run_name='__main__')
    assert '— product illustration' in (tmp_path/'static/images/products/tv-001.svg').read_text(encoding='utf-8')

def test_persistent_host_directory_keeps_accounts_and_session_secret(tmp_path,monkeypatch):
    directory=tmp_path/'persistent-data'
    monkeypatch.setenv('TECHVERSE_INSTANCE_DIR',str(directory));monkeypatch.setenv('SECRET_KEY','')
    first=create_app({'TESTING':True});uid=user(first)
    second=create_app({'TESTING':True})
    assert first.config['SECRET_KEY']==second.config['SECRET_KEY']
    assert Path(second.config['DATABASE']).parent==directory
    with second.app_context():assert second.get_db().execute('SELECT email FROM users WHERE id=?',(uid,)).fetchone()[0]=='member@example.com'
    assert (directory/'session.key').read_text(encoding='utf-8')==second.config['SECRET_KEY']

def test_photos_follow_names_when_inventory_rows_move():
    from tools.apply_product_photos import apply_photos
    items=[{'id':'tv-001','name':'MQ-9 Gas Sensor'},{'id':'tv-012','name':'Arduino UNO R3'}]
    assert apply_photos(items)==2
    assert items[0]['image_path']=='images/photos/s-mq-9.jpg'
    assert items[1]['image_path']=='images/photos/b-arduino-uno.jpg'

def test_entire_inventory_assets_and_translations():
    products=json.loads((ROOT/'data/products.json').read_text(encoding='utf-8'));audit=json.loads((ROOT/'data/import_audit.json').read_text(encoding='utf-8'))
    assert len(products)==116 and sum(p['price_cents'] is not None for p in products)==42
    assert len({p['id'] for p in products})==116
    for p in products:
        assert p['name_ar'] and p['description_ar'] and (ROOT/'static'/p['image_path']).is_file()
        assert 'cost' not in p and 'stock' not in p and p['category'] in ['boards','sensors','communication','displays','robotics','power','connections','components','kits','repair']
        assert p['image_kind']=='photo' and (ROOT/'static'/p['image_path']).stat().st_size>1000
        assert p['photo_source']['source_url'].startswith('https://') or p['photo_source']['match_type']=='supplied'
        assert p['photo_source']['match_type'] in ['exact','representative','supplied']
        assert Path(p['image_path']).suffix.lower() in ['.png','.jpg','.jpeg','.webp']
    assert translations['en'].keys()==translations['ar'].keys()
    assert all(translations['ar'].values())
    # Every literal UI lookup must have a matching bilingual string.
    for source in [*ROOT.glob('templates/*.html'),*ROOT.glob('static/js/*.js'),ROOT/'app.py']:
        for key in re.findall(r"\bt\(['\"]([^'\"]+)['\"]\)",source.read_text(encoding='utf-8')):assert key in translations['en'],(source,key)
    for key in ['cat_boards','cat_sensors','cat_communication','cat_displays','cat_robotics','cat_power','cat_connections','cat_components','cat_kits','status_none','status_pending','status_active','status_suspended']:
        assert key in translations['ar']

def test_csrf_is_required(client):
    assert client.post('/register',data={'email':'attacker@example.com'}).status_code==400
    assert client.post('/api/orders',json={}).status_code==400
    assert post(client,'/api/orders',json_data=[]).status_code==400

def test_registration_hashes_and_does_not_grant_paid_access(app,client):
    data={'full_name':'مستخدم تجريبي','email':'new@example.com','phone':'+96171234567','password':'correct-password','confirm_password':'correct-password'}
    response=post(client,'/register',data);assert response.status_code==302 and response.location=='/shop'
    assert client.get('/').location=='/shop'
    with app.app_context():
        row=app.get_db().execute('SELECT * FROM users WHERE email=?',(data['email'],)).fetchone()
        assert row['password']!=data['password'] and check_password_hash(row['password'],data['password'])
        assert row['membership_status']=='none';uid=row['id']
    assert client.get('/api/conversations').status_code==200
    assert post(client,'/membership').status_code==405 and member_status(app,uid)=='none'
    assert client.get('/membership?checkout=success').status_code==200
    assert member_status(app,uid)=='none'
    assert b'$' not in client.get('/membership').data

def test_registration_and_login_validation(app,client):
    data={'full_name':'Test','email':'invalid','phone':'123','password':'short','confirm_password':'other'}
    assert b'valid email' in post(client,'/register',data).data
    data.update(email='valid@example.com');assert b'at least 8' in post(client,'/register',data).data
    data.update(password='correct-password');assert b'do not match' in post(client,'/register',data).data
    uid=user(app)
    assert b'incorrect' in post(client,'/login',{'email':'member@example.com','password':'wrong'}).data
    response=post(client,'/login',{'email':'member@example.com','password':'correct-password','next':'https://untrusted.example/'})
    assert response.status_code==302 and response.location=='/shop'
    with client.session_transaction() as s:assert s['user_id']==uid
    assert post(client,'/logout').status_code==302 and client.get('/settings').status_code==302

def test_admin_payment_requires_real_confirmation_and_is_unique(app,client):
    uid=user(app);admin=user(app,'owner@example.com','admin','active');login_as(client,uid)
    assert client.get('/admin').status_code==403
    login_as(client,admin)
    assert client.get('/admin').status_code==200
    post(client,f'/admin/membership/{uid}',{'payment_reference':'receipt-1'})
    assert member_status(app,uid)=='none'
    post(client,f'/admin/membership/{uid}',{'payment_reference':'receipt-1','payment_confirmed':'yes'})
    assert member_status(app,uid)=='active'
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1
    post(client,f'/admin/membership/{uid}',{'payment_reference':'receipt-1','payment_confirmed':'yes'})
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1
    member_client=app.test_client();login_as(member_client,uid);assert member_client.get('/api/conversations').status_code==200
    post(client,f'/admin/membership/{uid}',{'action':'suspend'})
    assert member_client.get('/api/conversations').status_code==200

@pytest.mark.parametrize('language',['en','ar'])
def test_manual_chat_saves_private_history(app,client,language):
    uid=user(app,status='active');login_as(client,uid)
    with client.session_transaction() as s:s['language']=language
    result=post(client,'/api/chat',json_data={'model_id':'growatt-spf-5000-es','alarm_type':'Fault','message':'العطل ٠١' if language=='ar' else 'fault 01'}).get_json()
    assert result['mode']=='manual' and result['sources'][0]['page']==35
    assert ('مروحة' if language=='ar' else 'fan') in result['reply']
    cid=result['conversation_id'];history=client.get(f'/api/conversations/{cid}').get_json();assert len(history['messages'])==2
    other=user(app,'other@example.com',status='active');other_client=app.test_client();login_as(other_client,other)
    assert other_client.get(f'/api/conversations/{cid}').status_code==404
    assert post(other_client,'/api/chat',json_data={'conversation_id':cid,'model_id':'growatt-spf-5000-es','alarm_type':'Fault','message':'fault 02'}).status_code==404
    assert post(client,'/api/chat',json_data={'conversation_id':cid,'model_id':'growatt-spf-3500-es','alarm_type':'Fault','message':'fault 02'}).status_code==400
    response=client.delete(f'/api/conversations/{cid}',headers={'X-CSRF-Token':csrf(client)});assert response.status_code==200
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM messages WHERE conversation_id=?',(cid,)).fetchone()[0]==0

def test_codes_are_model_and_alarm_specific(app,client):
    login_as(client,user(app))
    catalogs=client.get('/api/catalogs').get_json()['catalogs'];assert len(catalogs)==16
    all_models={c['id']:c for c in catalogs}
    def lookup(model,code,kind='Fault'):return client.get('/api/lookup',query_string={'model':model,'type':kind,'code':code})
    assert 'fan' in lookup('growatt-spf-5000-es','1').get_json()['name'].lower()
    assert 'fan' in lookup('growatt-spf-5000-es','٠١').get_json()['name'].lower()
    assert 'timeout' in lookup('growatt-spf-5000-es','07').get_json()['name'].lower()
    assert 'timeout' not in lookup('growatt-spf-5000-es','07','Warning').get_json()['name'].lower()
    felicity=next(c['id'] for c in catalogs if c['brand']=='Felicity')
    assert 'undervoltage' in lookup(felicity,'07').get_json()['name'].lower()
    assert 'undervoltage' not in lookup(felicity,'27').get_json()['name'].lower()
    gospower=next(c['id'] for c in catalogs if c['brand']=='Gospower')
    assert lookup(gospower,'92').status_code==200 and lookup(gospower,'98').status_code==404
    sako=next(c['id'] for c in catalogs if c['brand']=='SAKO')
    assert 'battery' in lookup(sako,'56').get_json()['name'].lower()
    assert 'PV' in lookup(sako,'59').get_json()['name']
    assert lookup(sako,'Eq','Warning').status_code==200
    assert lookup('must','01').status_code==404
    specs={s['label']:s['value'] for s in all_models['growatt-spf-5000-es']['specs']}
    assert any('5000' in value for value in specs.values())
    assert client.get('/static/manuals/Growatt_SPF_3500_5000_ES_202109.pdf').status_code==200
    for catalog in catalogs:
        for url in [catalog['source']['url'],catalog['source'].get('local_file')]:
            if url and url.startswith('/'):assert client.get(url).status_code==200
        if catalog['image']:assert (ROOT/'static'/catalog['image']).is_file()

def test_orders_reprice_on_server_and_do_not_expose_costs(app,client):
    login_as(client,user(app))
    products=client.get('/api/products').get_json()['products'];priced=next(p for p in products if p['price_cents']);quote=next(p for p in products if p['price_cents'] is None)
    values={'full_name':'Customer','phone':'+96171234567','email':'customer@example.com','items':[{'id':priced['id'],'quantity':2,'price_cents':1},{'id':quote['id'],'quantity':3}]}
    result=post(client,'/api/orders',json_data=values);assert result.status_code==200
    assert result.get_json()['total_cents']==priced['price_cents']*2 and result.get_json()['whatsapp_configured']
    for invalid in [0,-1,100,'2',True,2.5]:
        values['items']=[{'id':priced['id'],'quantity':invalid}];assert post(client,'/api/orders',json_data=values).status_code==400
    values['items']=[{'id':'missing','quantity':1}];assert post(client,'/api/orders',json_data=values).status_code==400
    admin=user(app,'owner@example.com','admin','active');login_as(client,admin)
    assert client.get('/admin').status_code==200 # Includes saved order rows.

def test_company_approval_and_contact_requests(app,client):
    uid=user(app);login_as(client,uid)
    assert client.get('/companies/register').status_code==200
    fields=dict(company_name='Real Solar',company_name_ar='الشركة الحقيقية',description='Solar service',description_ar='خدمة الطاقة الشمسية',location='Tyre',location_ar='صور',phone='+96171234567',email='business@example.com',website='https://example.com/')
    assert post(client,'/companies/register',fields).status_code==302
    assert b'Real Solar' not in client.get('/companies').data
    with app.app_context():cid=app.get_db().execute('SELECT id FROM companies').fetchone()[0]
    admin=user(app,'owner@example.com','admin','active');login_as(client,admin)
    assert client.get('/admin').status_code==200
    post(client,f'/admin/company/{cid}/approve');assert b'Real Solar' in client.get('/companies').data
    result=post(client,'/contact',dict(full_name='Name',email='test@example.com',phone='12345678',topic='solar',message='<script>alert(1)</script>'))
    assert result.status_code==302
    body=client.get('/admin').data;assert b'&lt;script&gt;' in body and b'<script>alert(1)</script>' not in body

def test_whatsapp_uses_owner_number_in_both_languages(app,client):
    assert b'https://wa.me/96170000000' not in client.get('/').data
    admin=user(app,'owner@example.com','admin','active');login_as(client,admin)
    post(client,'/admin/settings',dict(whatsapp_number='fake',company_email=''))
    assert b'https://wa.me/' not in client.get('/').data
    post(client,'/admin/settings',dict(whatsapp_number='+961 71 234 567',company_email='owner@example.com'))
    assert b'https://wa.me/96171234567?' in client.get('/shop').data
    assert b'https://wa.me/96171234567?' in client.get('/shop/product/tv-001').data
    post(client,'/language/ar',{'next':'/contact'})
    assert 'تواصل معنا عبر واتساب'.encode() in client.get('/contact').data

def test_profile_password_changes(app,client):
    uid=user(app);login_as(client,uid)
    assert client.get('/settings').status_code==200
    post(client,'/settings',dict(action='profile',full_name='Updated Name',phone='+96171234567'))
    assert b'Updated Name' in client.get('/settings').data
    post(client,'/settings',dict(action='password',current_password='wrong',new_password='new-correct-password'))
    with app.app_context():assert check_password_hash(app.get_db().execute('SELECT password FROM users WHERE id=?',(uid,)).fetchone()[0],'correct-password')
    post(client,'/settings',dict(action='password',current_password='correct-password',new_password='new-correct-password'))
    with app.app_context():assert check_password_hash(app.get_db().execute('SELECT password FROM users WHERE id=?',(uid,)).fetchone()[0],'new-correct-password')

def signed_event(client,event,secret='whsec_test',stamp=None):
    raw=json.dumps(event).encode();stamp=str(stamp or int(time.time()));signature=hmac.new(secret.encode(),stamp.encode()+b'.'+raw,hashlib.sha256).hexdigest()
    return client.post('/api/payments/webhook',data=raw,content_type='application/json',headers={'Stripe-Signature':f't={stamp},v1={signature}'})

def test_stripe_signed_payment_only_known_checkout_and_deduplicates(app,client):
    app.config['STRIPE_WEBHOOK_SECRET']='whsec_test';uid=user(app,status='pending')
    event={'id':'evt_1','type':'checkout.session.completed','data':{'object':{'id':'cs_test','client_reference_id':str(uid),'mode':'payment','payment_status':'paid'}}}
    assert client.post('/api/payments/webhook',json=event).status_code==400
    assert signed_event(client,event,secret='wrong').status_code==400
    assert signed_event(client,event,stamp=int(time.time())-600).status_code==400
    assert signed_event(client,event).status_code==200 and member_status(app,uid)=='pending'
    with app.app_context():
        app.get_db().execute("INSERT INTO checkout_sessions(id,user_id,price_id) VALUES('cs_test',?,'price_test')",(uid,));app.get_db().commit()
    event['id']='evt_2';event['data']['object']['payment_status']='unpaid'
    assert signed_event(client,event).status_code==200 and member_status(app,uid)=='pending'
    event['id']='evt_3';event['data']['object']['payment_status']='paid'
    assert signed_event(client,event).status_code==200 and member_status(app,uid)=='active'
    assert signed_event(client,event).status_code==200
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1
    with app.app_context():
        app.get_db().execute("UPDATE users SET membership_status='suspended' WHERE id=?",(uid,));app.get_db().commit()
    event['id']='evt_4'
    assert signed_event(client,event).status_code==200 and member_status(app,uid)=='suspended'

def test_unconfigured_online_payment_is_not_displayed(app,client):
    uid=user(app);login_as(client,uid)
    assert b'id="checkout-button"' not in client.get('/membership').data
    assert post(client,'/api/payments/checkout',json_data={}).status_code==400
    app.config.update(STRIPE_SECRET_KEY='sk_test',STRIPE_PRICE_ID='price_test',PUBLIC_BASE_URL='https://example.com')
    assert b'id="checkout-button"' not in client.get('/membership').data # A webhook secret is also mandatory.

@pytest.mark.parametrize('path',['/static/csv_files/techverse.db','/static/csv_files/Products.csv','/static/session.key','/static/app.py'])
def test_private_files_not_served(client,path):assert client.get(path).status_code==404

def test_removed_technicians_and_no_demo_companies(app,client):
    login_as(client,user(app))
    assert client.get('/technicians').location=='/membership'
    assert b'id="display_name"' in client.get('/membership/apply').data
    assert b'No approved listings' in client.get('/companies').data

def test_connected_ai_uses_model_context_and_falls_back_honestly(app,client,monkeypatch):
    from urllib.error import URLError
    from io import BytesIO
    import app as module
    uid=user(app,status='active');login_as(client,uid);app.config['OPENAI_API_KEY']='test-server-key'
    def response(request,timeout):
        assert request.full_url=='https://api.openai.com/v1/responses'
        payload=json.loads(request.data)
        assert payload['store'] is False and 'SPF 5000 ES' in payload['instructions']
        assert 'SUN-16K-SG01LP1-EU' not in payload['instructions']
        assert payload['input'][-1]['role']=='user'
        return BytesIO(json.dumps({'output':[{'type':'message','content':[{'type':'output_text','text':'Checked model answer.'}]}]}).encode())
    monkeypatch.setattr(module,'urlopen',response)
    result=post(client,'/api/chat',json_data={'model_id':'growatt-spf-5000-es','alarm_type':'Fault','message':'fault 01'}).get_json()
    assert result['mode']=='ai' and result['reply']=='Checked model answer.'
    def unavailable(*args,**kwargs):raise URLError('unavailable')
    monkeypatch.setattr(module,'urlopen',unavailable)
    result=post(client,'/api/chat',json_data={'model_id':'growatt-spf-5000-es','alarm_type':'Fault','message':'fault 01'}).get_json()
    assert result['mode']=='manual' and result['notice'] and 'fan' in result['reply']
    assert b'test-server-key' not in client.get('/advisor').data

def test_old_chat_subscription_checkout_is_retired(app,client):
    uid=user(app);login_as(client,uid)
    app.config.update(STRIPE_SECRET_KEY='sk_test',STRIPE_PRICE_ID='price_owner',STRIPE_WEBHOOK_SECRET='whsec_test',PUBLIC_BASE_URL='https://techverse.example')
    assert post(client,'/api/payments/checkout',json_data={'purpose':'membership'}).status_code==400
    assert b'id="checkout-button"' not in client.get('/membership').data
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM checkout_sessions').fetchone()[0]==0
