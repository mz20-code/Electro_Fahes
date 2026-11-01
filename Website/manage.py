"""Owner setup. Creates an administrator without distributing a default password."""
import argparse, getpass, re
from werkzeug.security import generate_password_hash
from app import app

def main():
    parser=argparse.ArgumentParser(description='TechVerse owner setup / إعداد TechVerse')
    parser.add_argument('command',choices=['create-admin','set-whatsapp','check'])
    args=parser.parse_args()
    with app.app_context():
        db=app.get_db()
        if args.command=='check':
            print('Database ready. / قاعدة البيانات جاهزة.')
            import inventory,json
            from app import ROOT
            print('Products / المنتجات:',len(inventory.items(db)),'. Catalogs / الأدلة:',len(json.loads((ROOT/'data/catalogs.json').read_text(encoding='utf-8'))['catalogs']))
        elif args.command=='set-whatsapp':
            raw=input('Company WhatsApp, international format / رقم واتساب الشركة بالصيغة الدولية: ').strip()
            number=re.sub(r'[\s()+-]','',raw)
            if not re.fullmatch(r'[1-9]\d{7,14}',number):raise SystemExit('Invalid number / رقم غير صالح')
            db.execute("INSERT INTO site_settings(key,value) VALUES('whatsapp_number',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(number,));db.commit()
            print('Saved. / تم الحفظ.')
        else:
            email=input('Administrator email / بريد المسؤول: ').strip().lower()
            if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise SystemExit('Invalid email / بريد غير صالح')
            name=input('Full name / الاسم الكامل: ').strip()
            if not name:raise SystemExit('Name required / الاسم مطلوب')
            password=getpass.getpass('Password (8+ characters) / كلمة المرور (8 أحرف على الأقل): ')
            confirm=getpass.getpass('Confirm password / تأكيد كلمة المرور: ')
            if not 8<=len(password)<=256 or password!=confirm:raise SystemExit('Invalid or mismatched password / كلمة المرور غير صالحة أو غير متطابقة')
            if db.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
                raise SystemExit('Account exists. No changes made. Use a new owner email. / الحساب موجود. استخدم بريدًا جديدًا للمسؤول.')
            db.execute("INSERT INTO users(full_name,email,password,role,membership_status) VALUES(?,?,?,'admin','active')",(name,email,generate_password_hash(password)));db.commit()
            print('Administrator created. Sign in, then open /admin. / أُنشئ المسؤول. سجّل الدخول ثم افتح /admin.')

if __name__=='__main__':main()
