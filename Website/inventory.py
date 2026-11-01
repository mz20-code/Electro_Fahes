"""Private mutable inventory and a validated, Excel-friendly CSV round trip."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import csv, io, json, os, re, secrets, tempfile
from PIL import Image, ImageOps, UnidentifiedImageError

CATEGORIES=['boards','sensors','communication','displays','robotics','power','connections','components','kits','repair']
FIELDS=['id','name','name_ar','category','price_usd','description','description_ar','image_path','is_active']
ID=re.compile(r'tv-\d{3,10}\Z')

def initialize(conn,seed):
    conn.execute('CREATE TABLE IF NOT EXISTS inventory(id TEXT PRIMARY KEY,payload TEXT NOT NULL,updated_at TEXT DEFAULT(datetime(\'now\')))')
    for item in seed:
        item=dict(item,is_active=item.get('is_active',True))
        conn.execute('INSERT OR IGNORE INTO inventory(id,payload) VALUES(?,?)',(item['id'],json.dumps(item,ensure_ascii=False)))
    conn.commit()

def items(conn,include_hidden=False):
    result=[json.loads(row['payload']) for row in conn.execute('SELECT payload FROM inventory ORDER BY CAST(SUBSTR(id,4) AS INTEGER)')]
    return result if include_hidden else [item for item in result if item.get('is_active',True)]

def get(conn,product_id):
    row=conn.execute('SELECT payload FROM inventory WHERE id=?',(product_id,)).fetchone()
    return json.loads(row['payload']) if row else None

def text(value,limit,required=False):
    value=str(value or '').strip()
    if len(value)>limit or any(ord(c)<32 and c not in '\n\r\t' for c in value) or (required and not value):raise ValueError('invalid_product')
    return value

def price(value):
    value=str(value or '').strip()
    if not value:return None
    try:
        number=Decimal(value)
        if not number.is_finite() or number<0 or number>1000000 or number!=number.quantize(Decimal('.01')):raise ValueError('invalid_price')
        return int(number*100)
    except (InvalidOperation,ValueError):raise ValueError('invalid_price')

def valid_image(path,root,private_dir):
    if not isinstance(path,str) or not path or '\\' in path or '..' in path or path.startswith('/') or len(path)>200:return False
    if path.startswith('uploads/'):
        return bool(re.fullmatch(r'uploads/[a-f0-9]{32}\.webp',path)) and (private_dir/'product_images'/path.split('/')[1]).is_file()
    if not path.startswith('images/') or Path(path).suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):return False
    return (root/'static'/path).is_file()

def save_image(upload,private_dir):
    raw=upload.stream.read(5*1024*1024+1)
    if not raw or len(raw)>5*1024*1024:raise ValueError('invalid_photo')
    try:
        with Image.open(io.BytesIO(raw)) as check:
            if check.format not in ('JPEG','PNG','WEBP') or check.width*check.height>20_000_000 or min(check.size)<40:raise ValueError('invalid_photo')
            check.verify()
        with Image.open(io.BytesIO(raw)) as image:
            image.load();image=ImageOps.exif_transpose(image);image=image.convert('RGBA' if image.mode in ('RGBA','LA') else 'RGB')
            image.thumbnail((1600,1600))
            folder=private_dir/'product_images';folder.mkdir(parents=True,exist_ok=True)
            name=secrets.token_hex(16)+'.webp';target=folder/name
            image.save(target,'WEBP',quality=90)
        return 'uploads/'+name
    except (OSError,UnidentifiedImageError,Image.DecompressionBombError,ValueError):raise ValueError('invalid_photo')

def validate(values,root,private_dir,existing=None):
    product=dict(existing or {})
    product['name']=text(values.get('name'),160,True);product['name_ar']=text(values.get('name_ar'),160,True)
    product['description']=text(values.get('description'),1500,True);product['description_ar']=text(values.get('description_ar'),1500,True)
    category=values.get('category','')
    if category not in CATEGORIES:raise ValueError('invalid_category')
    product['category']=category;product['price_cents']=price(values.get('price_usd'))
    product['price_status']='confirmed' if product['price_cents'] is not None else 'request'
    image_path=values.get('image_path') or product.get('image_path','')
    if not valid_image(image_path,root,private_dir):raise ValueError('invalid_photo')
    product['image_path']=image_path;product['image_kind']='photo'
    if not existing or image_path!=existing.get('image_path'):
        product['photo_source']={'credit':'TechVerse','source_url':'','match_type':'supplied'}
    active=str(values.get('is_active','true')).lower()
    if active not in ('true','false','1','0'):raise ValueError('invalid_product')
    product['is_active']=active in ('true','1')
    product.setdefault('aliases',[]);product.setdefault('sources',[])
    return product

def save(conn,product,product_id=None):
    conn.execute('BEGIN IMMEDIATE')
    try:
        if not product_id:
            number=conn.execute('SELECT COALESCE(MAX(CAST(SUBSTR(id,4) AS INTEGER)),0)+1 FROM inventory').fetchone()[0]
            product_id=f'tv-{number:03d}'
        if not ID.fullmatch(product_id):raise ValueError('invalid_product')
        product=dict(product,id=product_id)
        conn.execute('INSERT INTO inventory(id,payload) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,updated_at=datetime(\'now\')',(product_id,json.dumps(product,ensure_ascii=False)))
        conn.commit();return product
    except Exception:conn.rollback();raise

def safe_cell(value):
    value=str(value or '')
    return "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r','\n')) or value.startswith(('\t','\r','\n')) else value

def unescape_cell(value):
    return value[1:] if value.startswith("'") and value[1:].lstrip().startswith(('=','+','-','@')) else value

def csv_bytes(products):
    output=io.StringIO(newline='');writer=csv.DictWriter(output,fieldnames=FIELDS);writer.writeheader()
    for item in products:
        row={key:item.get(key,'') for key in FIELDS}
        row['price_usd']='' if item['price_cents'] is None else f"{item['price_cents']/100:.2f}"
        row['is_active']='true' if item.get('is_active',True) else 'false'
        writer.writerow({key:safe_cell(value) if key not in ('price_usd','is_active') else value for key,value in row.items()})
    return ('\ufeff'+output.getvalue()).encode('utf-8')

def snapshot(conn,private_dir):
    # Serialize snapshots with inventory mutations so a late writer cannot restore an older CSV.
    conn.execute('BEGIN IMMEDIATE')
    path=None
    try:
        data=csv_bytes(items(conn,True));private_dir.mkdir(parents=True,exist_ok=True)
        fd,path=tempfile.mkstemp(prefix='products-',suffix='.tmp',dir=private_dir)
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(path,private_dir/'products.csv');conn.commit()
    except Exception:conn.rollback();raise
    finally:
        if path and os.path.exists(path):os.unlink(path)

def parse_csv(raw,conn,root,private_dir):
    if len(raw)>2*1024*1024:raise ValueError('invalid_csv')
    try:
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''))
        if reader.fieldnames!=FIELDS:raise ValueError('invalid_csv')
        prepared=[];seen=set();errors=[]
        for line,row in enumerate(reader,2):
            if line>2001:raise ValueError('invalid_csv')
            try:
                if None in row or any(value is None for value in row.values()):raise ValueError('invalid_csv')
                values={key:unescape_cell(value) for key,value in row.items()}
                product_id=values['id'].strip()
                if product_id and (not ID.fullmatch(product_id) or product_id in seen):raise ValueError('invalid_product')
                if product_id:seen.add(product_id)
                existing=get(conn,product_id) if product_id else None
                prepared.append((product_id or None,validate(values,root,private_dir,existing)))
            except ValueError as error:errors.append({'line':line,'error':str(error)})
        if not prepared and not errors:raise ValueError('invalid_csv')
        return prepared,errors
    except (UnicodeDecodeError,csv.Error):raise ValueError('invalid_csv')

def merge(conn,prepared):
    own_transaction=not conn.in_transaction
    if own_transaction:conn.execute('BEGIN IMMEDIATE')
    try:
        number=conn.execute('SELECT COALESCE(MAX(CAST(SUBSTR(id,4) AS INTEGER)),0)+1 FROM inventory').fetchone()[0]
        assigned={pid for pid,_ in prepared if pid}
        for product_id,product in prepared:
            if not product_id:
                while f'tv-{number:03d}' in assigned:number+=1
                product_id=f'tv-{number:03d}';number+=1
            product=dict(product,id=product_id)
            conn.execute('INSERT INTO inventory(id,payload) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,updated_at=datetime(\'now\')',(product_id,json.dumps(product,ensure_ascii=False)))
        if own_transaction:conn.commit()
    except Exception:
        if own_transaction:conn.rollback()
        raise
