"""Regression checks for product administration, guest flow and paid advertising."""
import csv,io,json,re
from pathlib import Path
from PIL import Image
import pytest
from app import ROOT
from test_site import app,client,csrf,post,user,login_as,signed_event,member_status
import inventory

def listing_fields():
    return dict(display_name='Local technician',age='28',gender='male',experience_years='8',experience='Solar and battery repairs',specialty='Solar repair',bio='Solar and battery repairs',bio_ar='صيانة الطاقة الشمسية والبطاريات',location='Tyre',location_ar='صور',phone='+96171234567',website='https://example.com/')

def product_fields():
    return dict(name='New sensor',name_ar='حساس جديد',category='sensors',description='A new sensor.',description_ar='حساس جديد.',price_usd='2.75',image_path='images/photos/b-arduino-uno.jpg',is_active='true')

def photo():
    out=io.BytesIO();Image.new('RGB',(80,60),'yellow').save(out,'PNG');out.seek(0);return out

@pytest.mark.parametrize('path',['/admin/products','/admin/products/new','/admin/products/import','/admin/products.csv'])
def test_inventory_owner_only(app,client,path):
    assert client.get(path).status_code==302
    login_as(client,user(app));assert client.get(path).status_code==403

@pytest.mark.parametrize('language',['en','ar'])
@pytest.mark.parametrize('path',['/admin/products','/admin/products/new','/admin/products/import'])
def test_inventory_pages_bilingual(app,client,path,language):
    login_as(client,user(app,role='admin'))
    with client.session_transaction() as session:session['language']=language
    response=client.get(path);assert response.status_code==200
    assert f'lang="{language}"'.encode() in response.data

def test_public_click_preserves_product_and_guide_destination(app,client):
    uid=user(app)
    for target in ['/shop/product/tv-109','/advisor']:
        response=client.get('/login',query_string={'next':target});assert target.encode() in response.data
        response=post(client,'/login',dict(email='member@example.com',password='correct-password',next=target))
        assert response.location==target and client.get(target).status_code==200
        assert client.get('/').location=='/shop';post(client,'/logout')

def test_registration_preserves_guide_destination(client):
    result=post(client,'/register',dict(full_name='New person',email='newperson@example.com',phone='12345678',password='correct-password',confirm_password='correct-password',next='/advisor'))
    assert result.location=='/advisor' and client.get('/').location=='/shop'

def test_owner_add_upload_persist_snapshot_and_hide(app,client):
    login_as(client,user(app,role='admin'))
    fields=product_fields();fields['photo']=(photo(),'actual.png');fields['image_path']=''
    response=post(client,'/admin/products/new',fields);assert response.status_code==302
    with app.app_context():
        p=inventory.items(app.get_db())[-1];assert p['price_cents']==275 and p['name_ar']=='حساس جديد'
        assert inventory.valid_image(p['image_path'],ROOT,Path(app.instance_path))
        csv_file=Path(app.instance_path)/'products.csv';export=csv_file.read_bytes()
        assert export.startswith(b'\xef\xbb\xbf') and 'حساس جديد' in export.decode('utf-8-sig')
    assert client.get('/shop/product/'+p['id']).status_code==200
    assert ('/media/products/'+p['image_path'].split('/')[-1]).encode() in client.get('/shop/product/'+p['id']).data
    media=client.get('/media/products/'+p['image_path'].split('/')[-1]);assert media.status_code==200 and media.mimetype=='image/webp'
    fields=product_fields();fields['image_path']=p['image_path'];fields['is_active']='false'
    post(client,f"/admin/products/{p['id']}/edit",fields)
    assert client.get('/shop/product/'+p['id']).status_code==404
    with app.app_context():assert inventory.get(app.get_db(),p['id'])['is_active'] is False

def test_bad_image_price_or_category_saves_nothing(app,client):
    login_as(client,user(app,role='admin'))
    for field,value in [('price_usd','nan'),('price_usd','-1'),('price_usd','1.234'),('category','no'),('image_path','../../app.py')]:
        values=product_fields();values[field]=value;assert post(client,'/admin/products/new',values).status_code==200
    values=product_fields();values['photo']=(io.BytesIO(b'<script>alert(1)</script>'),'malicious.jpg')
    post(client,'/admin/products/new',values)
    with app.app_context():assert len(inventory.items(app.get_db()))==116

def csv_upload(client,raw):
    return post(client,'/admin/products/import',{'csv_file':(io.BytesIO(raw),'products.csv')})

def test_csv_preview_import_duplicate_token_and_reboot(app,client):
    login_as(client,user(app,role='admin'))
    with app.app_context():
        p=inventory.items(app.get_db())[0];p=dict(p,price_cents=1234,name_ar='اختبار CSV')
        new=dict(p,id='',name='New CSV product',name_ar='منتج CSV جديد')
        raw=inventory.csv_bytes([p,new])
    result=csv_upload(client,raw);assert result.status_code==200
    token=re.search(rb'name="commit_token" value="([^"]+)"',result.data).group(1).decode()
    with app.app_context():assert len(inventory.items(app.get_db()))==116
    result=post(client,'/admin/products/import',{'commit_token':token});assert result.status_code==302
    with app.app_context():
        assert len(inventory.items(app.get_db()))==117
        assert inventory.get(app.get_db(),p['id'])['price_cents']==1234
        assert inventory.get(app.get_db(),p['id'])['name_ar']=='اختبار CSV'
    assert post(client,'/admin/products/import',{'commit_token':token}).status_code==200
    with app.app_context():
        assert len(inventory.items(app.get_db()))==117
        inventory.initialize(app.get_db(),json.loads((ROOT/'data/products.json').read_text(encoding='utf-8')))
        assert inventory.get(app.get_db(),p['id'])['price_cents']==1234
    export=client.get('/admin/products.csv');assert export.status_code==200 and b'New CSV product' in export.data

def test_csv_invalid_batch_has_no_commit_and_no_partial_changes(app,client):
    login_as(client,user(app,role='admin'))
    with app.app_context():
        p=inventory.items(app.get_db())[0];raw=inventory.csv_bytes([p]).decode('utf-8-sig')
    raw=raw.replace('boards','made-up-category').replace('kits','made-up-category').encode('utf-8')
    response=csv_upload(client,raw);assert b'name="commit_token"' not in response.data
    with app.app_context():assert len(inventory.items(app.get_db()))==116

def test_csv_stale_preview_rejected(app,client):
    login_as(client,user(app,role='admin'))
    with app.app_context():raw=inventory.csv_bytes([inventory.items(app.get_db())[0]])
    response=csv_upload(client,raw);token=re.search(rb'name="commit_token" value="([^"]+)"',response.data).group(1).decode()
    post(client,'/admin/products/new',product_fields())
    response=post(client,'/admin/products/import',{'commit_token':token});assert b'preview expired' in response.data

def test_csv_escapes_excel_formulas():
    item=dict(product_fields(),id='tv-999',price_cents=0,is_active=True,name='=HYPERLINK("bad")')
    raw=inventory.csv_bytes([item]);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    assert rows[0]['name'].startswith("'=") and inventory.unescape_cell(rows[0]['name'])==item['name']

@pytest.mark.parametrize('language',['en','ar'])
def test_technician_application_unpaid_hidden_and_edit_review(app,client,language):
    uid=user(app);login_as(client,uid)
    with client.session_transaction() as session:session['language']=language
    assert post(client,'/technicians',listing_fields()).status_code==302
    with app.app_context():
        p=dict(app.get_db().execute('SELECT * FROM technician_profiles').fetchone());assert p['payment_status']=='unpaid'
    owner=app.test_client();login_as(owner,user(app,email='owner@example.com',role='admin'))
    post(owner,f"/admin/technician/{p['id']}/approve")
    with app.app_context():assert app.get_db().execute('SELECT approval_status FROM technician_profiles').fetchone()[0]=='pending'
    assert client.get('/membership/apply?checkout=success').status_code==200
    assert post(client,'/api/payments/checkout',json_data={'purpose':'technician'}).status_code==503
    assert b'id="listing-checkout-button"' not in client.get('/membership/apply').data

def test_technician_card_payment_verified_amount_owner_purpose_and_approval(app,client,monkeypatch):
    from urllib.parse import parse_qs
    import app as module
    uid=user(app);login_as(client,uid);post(client,'/technicians',listing_fields())
    with app.app_context():pid=app.get_db().execute('SELECT id FROM technician_profiles').fetchone()[0]
    app.config.update(STRIPE_SECRET_KEY='test',STRIPE_WEBHOOK_SECRET='whsec_test',STRIPE_TECHNICIAN_PRICE_ID='price_listing',PUBLIC_BASE_URL='https://example.com')
    def checkout(request,timeout):
        values=parse_qs(request.data.decode());assert values['line_items[0][price]']==['price_listing']
        assert values['payment_method_types[0]']==['card'] and values['metadata[purpose]']==['technician']
        return io.BytesIO(json.dumps({'id':'cs_listing','url':'https://checkout.stripe.com/c/pay/cs_listing','amount_total':2500,'currency':'usd'}).encode())
    monkeypatch.setattr(module,'urlopen',checkout)
    assert post(client,'/api/payments/checkout',json_data={'purpose':'technician','amount':1,'price_id':'bad'}).status_code==200
    event={'id':'evt_listing_wrong_amount','type':'checkout.session.completed','data':{'object':{'id':'cs_listing','client_reference_id':str(uid),'payment_status':'paid','mode':'payment','amount_total':1,'currency':'usd'}}}
    assert signed_event(client,event).status_code==200
    with app.app_context():assert app.get_db().execute('SELECT payment_status FROM technician_profiles').fetchone()[0]=='unpaid'
    event['id']='evt_wrong_owner';event['data']['object'].update(amount_total=2500,client_reference_id='999')
    assert signed_event(client,event).status_code==200
    event['id']='evt_paid';event['data']['object']['client_reference_id']=str(uid)
    assert signed_event(client,event).status_code==200 and signed_event(client,event).status_code==200
    assert member_status(app,uid)=='none' # Advertising payment must not grant guide membership.
    with app.app_context():
        row=app.get_db().execute('SELECT * FROM technician_profiles').fetchone();assert row['payment_status']=='paid' and row['approval_status']=='pending'
        assert app.get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1
    owner=app.test_client();login_as(owner,user(app,email='owner@example.com',role='admin'))
    post(owner,f'/admin/technician/{pid}/approve')
    visitor=app.test_client();login_as(visitor,user(app,email='viewer@example.com'))
    assert b'Local technician' in visitor.get('/membership').data
    assert post(client,'/api/payments/checkout',json_data={'purpose':'technician'}).status_code==409
    post(client,'/technicians',dict(listing_fields(),display_name='Changed technician'))
    assert b'Changed technician' not in visitor.get('/membership').data

def test_malicious_listing_link_escaped_or_rejected(app,client):
    login_as(client,user(app))
    fields=listing_fields();fields['website']='javascript:alert(1)'
    post(client,'/technicians',fields)
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM technician_profiles').fetchone()[0]==0

def test_invalid_unicode_csrf_returns_400(client):
    csrf(client);assert client.post('/register',data={'csrf_token':'رمز خاطئ'}).status_code==400

def test_catalog_coverage_images_and_exact_source_pages(app,client):
    login_as(client,user(app));catalogs=client.get('/api/catalogs').get_json()['catalogs']
    assert {c['brand'] for c in catalogs}=={'Growatt','Deye','Felicity','Gospower','SAKO','MUST','Bluesun','SOROTEC','Voltronic'}
    for c in catalogs:
        assert (ROOT/'static'/c['image']).is_file()
        pairs=[(e['type'],e['code']) for e in c['entries']];assert len(set(pairs))==len(pairs)
        for e in c['entries']:
            assert e['page']>0 and e['name_ar'] and e['steps']
            result=client.get('/api/lookup',query_string={'model':c['id'],'type':e['type'],'code':e['code']})
            assert result.status_code==200 and result.get_json()['source']['page']==e['page']
    result=client.get('/api/lookup',query_string={'model':'sorotec-revo-ii-v4','type':'Warning','code':'07'}).get_json()
    assert 'inconsistent' in result['manual_note']
    assert client.get('/api/lookup',query_string={'model':'sorotec-revo-ii-v4','type':'Warning','code':'39'}).status_code==404
    assert client.get('/api/lookup',query_string={'model':'voltronic-axpert-vmiii-v1','type':'Warning','code':'E9'}).status_code==200

def test_public_page_seo_and_csp_no_inline_theme(client,app):
    app.config['PUBLIC_BASE_URL']='https://www.techversecompany.com'
    body=client.get('/').data
    assert b'rel="canonical"' in body and b'hreflang="ar"' in body
    assert b'theme-init.js' in body and b'<script>try' not in body
    assert b'/ar' in client.get('/sitemap.xml').data
