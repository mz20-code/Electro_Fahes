"""Checks for the exact revised homepage, directory, photos, catalogs and contact flow."""
from pathlib import Path
import json,sqlite3
import pytest
from app import create_app,ROOT,RELEASE
from test_site import app,client,user,login_as,post
from test_updates import listing_fields

@pytest.mark.parametrize('language',['en','ar'])
def test_membership_only_has_directory_and_advertise_button(app,client,language):
    uid=user(app);login_as(client,uid)
    with client.session_transaction() as s:s['language']=language
    response=client.get('/membership')
    assert response.status_code==200 and b'href="/membership/apply"' in response.data
    assert b'id="display_name"' not in response.data and b'checkout-button' not in response.data
    visible=response.data.split(b'<main id="main">',1)[1].split(b'</main>',1)[0]
    assert b'chat subscription' not in visible.lower() and b'paid membership' not in visible.lower()
    assert client.get('/technicians').location=='/membership'
    body=client.get('/membership/apply').data
    for field in ['display_name','age','gender','experience_years','experience','location','phone']:
        assert f'name="{field}"'.encode() in body

@pytest.mark.parametrize('field,value',[('age',''),('age','0'),('age','121'),('age','twenty'),('gender',''),('gender','invented'),('experience_years','-1'),('experience_years','99'),('experience',''),('phone','<script>'),('phone','12')])
def test_incomplete_application_cannot_be_paid_or_appear(app,client,field,value):
    login_as(client,user(app));fields=listing_fields();fields[field]=value
    # Remove legacy duplicate text fields to test the new single biography input.
    fields.pop('bio',None);fields.pop('bio_ar',None)
    response=post(client,'/membership/apply',fields)
    assert response.status_code==200
    with app.app_context():assert app.get_db().execute('SELECT COUNT(*) FROM technician_profiles').fetchone()[0]==0
    assert post(client,'/api/payments/checkout',json_data={'purpose':'technician'}).status_code==400

@pytest.mark.parametrize('language',['en','ar'])
def test_directory_excludes_unpaid_unapproved_and_incomplete(app,client,language):
    uid=user(app);login_as(client,uid)
    post(client,'/membership/apply',listing_fields())
    viewer=app.test_client();login_as(viewer,user(app,email='viewer@example.com'))
    with viewer.session_transaction() as s:s['language']=language
    def body():return viewer.get('/membership').data
    assert b'Local technician' not in body()
    with app.app_context():
        conn=app.get_db();conn.execute("UPDATE technician_profiles SET payment_status='paid'");conn.commit()
    assert b'Local technician' not in body()
    with app.app_context():
        conn=app.get_db();conn.execute("UPDATE technician_profiles SET approval_status='approved'");conn.commit()
    assert b'Local technician' in body() and b'+96171234567' in body()
    assert b'id="display_name"' not in body()
    with app.app_context():
        conn=app.get_db();conn.execute("UPDATE technician_profiles SET age=NULL");conn.commit()
    assert b'Local technician' not in body()

@pytest.mark.parametrize('language',['en','ar'])
def test_no_product_counts_no_videos_and_company_phone(app,client,language):
    with client.session_transaction() as s:s['language']=language
    public=client.get('/').data
    assert b'results-count' not in public and b'<span>116</span>' not in public
    assert b'https://wa.me/96181676140?' in public and b'+961 81 676 140' in public
    login_as(client,user(app))
    shop=client.get('/shop').data
    assert b'results-count' not in shop and b'<span>116</span>' not in shop
    video=client.get('/videos').data
    assert b'<video' not in video and b'<iframe' not in video and b'learning-card' not in video
    assert b'docs.arduino.cc' not in video
    assert b'https://wa.me/96181676140?' in client.get('/contact').data

@pytest.mark.parametrize('entry',['/','/ar','/en','/home','/index'])
def test_signed_in_cannot_open_any_homepage(app,client,entry):
    login_as(client,user(app));response=client.get(entry)
    assert response.status_code==302 and response.location=='/shop'
    page=client.get('/shop').data
    assert b'>Home</a>' not in page and b'href="/" class="wordmark"' not in page
    assert response.headers['X-TechVerse-Release']==RELEASE

@pytest.mark.parametrize('language',['en','ar'])
def test_visible_inverter_photos_and_full_selected_catalog(app,client,language):
    login_as(client,user(app))
    with client.session_transaction() as s:s['language']=language
    data=json.loads((ROOT/'data/catalogs.json').read_text(encoding='utf-8'))
    body=client.get('/advisor').data
    assert b'class="inverter-model-grid"' in body and b'brand-thumbnail' in body
    for c in data['catalogs']:
        assert f'data-select-model="{c["id"]}"'.encode() in body
        assert f'/static/{c["image"]}'.encode() in body
        response=client.get('/advisor',query_string={'model':c['id']})
        assert response.status_code==200
        tag=f'id="catalog-{c["id"]}" data-catalog-model="{c["id"]}" open'.encode()
        assert tag in response.data
        assert (c['source'].get('local_file') or c['source']['url']).encode() in response.data.replace(b'&amp;',b'&')
    assert b'id="chat-form"' in body # Registered guide user needs no advertising payment.

def test_existing_database_migrates_and_preserves_owner_number_changes(tmp_path,monkeypatch):
    directory=tmp_path/'instance';directory.mkdir();database=directory/'old.db'
    conn=sqlite3.connect(database)
    conn.executescript("CREATE TABLE site_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL); INSERT INTO site_settings VALUES('whatsapp_number','96170000000'); CREATE TABLE technician_profiles(id INTEGER PRIMARY KEY,user_id INTEGER UNIQUE,display_name TEXT,specialty TEXT,bio TEXT,bio_ar TEXT,location TEXT,location_ar TEXT,phone TEXT,website TEXT,payment_status TEXT,approval_status TEXT,created_at TEXT,updated_at TEXT);")
    conn.commit();conn.close();monkeypatch.setenv('TECHVERSE_INSTANCE_DIR',str(directory))
    application=create_app({'TESTING':True,'DATABASE':str(database),'SECRET_KEY':'test'})
    with application.app_context():
        conn=application.get_db();columns={row[1] for row in conn.execute('PRAGMA table_info(technician_profiles)')}
        assert {'age','gender','experience_years'}<=columns
        assert conn.execute("SELECT value FROM site_settings WHERE key='whatsapp_number'").fetchone()[0]=='96181676140'
        conn.execute("UPDATE site_settings SET value='96181111222' WHERE key='whatsapp_number'");conn.commit()
    second=create_app({'TESTING':True,'DATABASE':str(database),'SECRET_KEY':'test'})
    with second.app_context():assert second.get_db().execute("SELECT value FROM site_settings WHERE key='whatsapp_number'").fetchone()[0]=='96181111222'
