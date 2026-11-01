"""Import public retail products without exposing workbook purchase costs."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv, json, re, zipfile, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def read_sheets(path):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for s in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
            target=rels[s.get('{'+NS['r']+'}id')]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            rows=[]
            for r in ET.fromstring(z.read(target)).findall('m:sheetData/m:row',NS):
                cells={}
                for c in r.findall('m:c',NS):
                    v=c.find('m:v',NS); value=v.text if v is not None else ''
                    if c.get('t')=='s':value=strings[int(value)]
                    elif c.get('t')=='inlineStr':value=''.join(c.find('m:is',NS).itertext())
                    cells[re.sub(r'\d','',c.get('r'))]=value or ''
                rows.append((int(r.get('r')),cells))
            yield s.get('name'),rows

ALIASES = {
    'hc-sr04 ultrasonic':'hc-sr04 ultrasonic sensor','dht11':'dht11 sensor',
    'pir motion':'pir motion sensor','ir obstacle':'ir obstacle sensor','mq-2':'mq-2 gas sensor',
    'ldr':'ldr light sensor (gl5506)','lcd1602 i2c':'lcd 1602 i2c','oled 1.3':'oled display (1.3")',
    '7 segment':'7-segment display','sg90 servo':'sg90 servo (180°)',
    'mg996r servo':'mg996r servo (180°)','l298n':'l298n driver','hc-05':'hc-05 bluetooth module',
    'nrf24l01':'nrf24l01+','robot wheels':'robot wheels',
}
def key(name):
    k=' '.join(name.strip().lower().split())
    return ALIASES.get(k,k)

def category(name):
    if 'devkit' in name.lower():return 'boards'
    n=name.lower()
    if any(x in n for x in ['kit','shield']):return 'kits'
    if any(x in n for x in ['arduino','esp32 dev','esp8266','esp32-cam','raspberry','esp-01']):return 'boards'
    if any(x in n for x in ['hc-05','hc-06','nrf24']):return 'communication'
    if any(x in n for x in ['sensor','hc-sr04','dht','mq-','pir','ldr','ds18','mpu','rc522','rfid','moisture','water level','rain','fingerprint']):return 'sensors'
    if any(x in n for x in ['display','lcd','oled','segment','digit','matrix']):return 'displays'
    if any(x in n for x in ['servo','motor','stepper','wheel','l298','esc','chassis']):return 'robotics'
    if any(x in n for x in ['buck','lm2596','tp4056','regulator','relay','battery holder']):return 'power'
    if any(x in n for x in ['cable','breadboard','jumper','header','terminal']):return 'connections'
    return 'components'

ARABIC = {
 'Arduino UNO R3 kit':'طقم أردوينو UNO R3','Arduino UNO super kit':'طقم أردوينو UNO المتكامل',
 'Arduino Nano V3':'أردوينو Nano V3','ESP32 Dev Board (CH340)':'لوحة تطوير ESP32 (CH340)',
 'ESP8266 NodeMCU':'لوحة ESP8266 NodeMCU','Arduino Mega 2560':'أردوينو Mega 2560',
 'HC-SR04 Ultrasonic Sensor':'حساس المسافة بالموجات فوق الصوتية HC-SR04',
 'DHT11 Sensor':'حساس الحرارة والرطوبة DHT11','DHT22 Sensor':'حساس الحرارة والرطوبة DHT22',
 'Real time clock module':'وحدة ساعة الوقت الحقيقي','MQ-2 Gas Sensor':'حساس الغاز MQ-2',
 'MQ-9 Gas Sensor':'حساس الغاز MQ-9','PIR Motion Sensor':'حساس الحركة PIR',
 'LDR Light Sensor (GL5506)':'مقاومة ضوئية LDR (GL5506)','Sound Sensor':'حساس الصوت',
 'IR Obstacle Sensor':'حساس العوائق بالأشعة تحت الحمراء','Flame Sensor':'حساس اللهب',
 'Joystick Module':'وحدة عصا التحكم','4×4 Keypad':'لوحة مفاتيح 4×4',
 'HC-05 Bluetooth Module':'وحدة بلوتوث HC-05','NRF24L01+':'وحدة اتصال لاسلكي NRF24L01+',
 '7-Segment Display':'شاشة سباعية المقاطع','LCD 1602 I2C':'شاشة LCD 1602 مع I2C',
 'MPU6050':'حساس الحركة والتسارع MPU6050','SG90 Servo (180°)':'محرك سيرفو SG90 (180°)',
 'MG996R Servo (180°)':'محرك سيرفو MG996R (180°)','Stepper Motor Kit':'طقم محرك خطوي',
 'DC Gear Motor':'محرك تيار مستمر مع علبة تروس','L298N Driver':'دارة قيادة المحركات L298N',
 'CNC Shield V3':'لوحة توسعة CNC V3','5V Gear Motor':'محرك مع علبة تروس 5V',
 'Robot Wheels':'عجلات روبوت','Smart Car Kit':'طقم سيارة ذكية','ESC':'متحكم سرعة إلكتروني ESC',
 'Breadboard (400-pin)':'لوحة تجارب (400 نقطة)','Jumper Wires':'أسلاك توصيل',
 'USB A-B Cable (0.3 m)':'كابل USB A-B (0.3 متر)','USB Micro Cable (0.3 m)':'كابل Micro USB (0.3 متر)',
 'USB-C Cable (0.5 m)':'كابل USB-C (0.5 متر)','OLED Display (1.3")':'شاشة OLED (1.3 بوصة)',
 'Buck Converter':'محول خافض للجهد','Sensor Shield':'لوحة توسعة للحساسات',
 'Arduino UNO R3':'أردوينو UNO R3','ESP32 DevKit':'لوحة تطوير ESP32 DevKit','ESP32-CAM':'لوحة ESP32-CAM مع كاميرا',
 'Breadboard 830':'لوحة تجارب 830 نقطة','Mini Breadboard':'لوحة تجارب صغيرة',
 'Jumper Wires M-M':'أسلاك توصيل ذكر–ذكر','Jumper Wires M-F':'أسلاك توصيل ذكر–أنثى',
 'Jumper Wires F-F':'أسلاك توصيل أنثى–أنثى','USB Micro Cable':'كابل Micro USB',
 'USB Type-C Cable':'كابل USB Type-C','Capacitor Kit':'طقم مكثفات','Potentiometer':'مقاومة متغيرة',
 'Push Buttons':'أزرار ضغط','LEDs':'مصابيح LED','RGB LEDs':'مصابيح LED متعددة الألوان',
 'Voltage Regulators':'منظمات جهد','Pin Headers':'صفوف دبابيس توصيل','Screw Terminals':'أطراف توصيل براغي',
 'MQ-135':'حساس الغاز MQ-135','Soil Moisture':'حساس رطوبة التربة','Water Level':'حساس مستوى الماء',
 'Rain Sensor':'حساس المطر','DS18B20':'حساس الحرارة DS18B20','OLED 0.96':'شاشة OLED (0.96 بوصة)',
 'MAX7219 Matrix':'مصفوفة LED مع MAX7219','4 Digit Display':'شاشة بأربع خانات',
 'TT Motor':'محرك TT مع علبة تروس','28BYJ-48 Stepper':'محرك خطوي 28BYJ-48',
 'HC-06':'وحدة بلوتوث HC-06','ESP-01':'وحدة Wi-Fi ESP-01','ESP-01 Adapter':'محوّل وحدة ESP-01',
 'LM2596':'محول خافض للجهد LM2596','TP4056':'وحدة شحن ليثيوم TP4056',
 '18650 Battery Holder':'حامل بطارية 18650','RFID RC522':'قارئ بطاقات RFID RC522',
 'Fingerprint Sensor':'حساس بصمة','pH Sensor':'حساس الحموضة pH','Turbidity Sensor':'حساس العكارة',
 'MQ-3':'حساس الغاز MQ-3','MQ-5':'حساس الغاز MQ-5','MQ-7':'حساس الغاز MQ-7',
 '1-Channel Relay':'وحدة ريليه بقناة واحدة','2-Channel Relay':'وحدة ريليه بقناتين',
 '4-Channel Relay':'وحدة ريليه بأربع قنوات','RTC DS3231':'وحدة ساعة الوقت الحقيقي DS3231',
 'Robot Chassis Kit':'طقم هيكل روبوت','BC547 Transistor':'ترانزستور BC547','BC557 Transistor':'ترانزستور BC557',
 'Arduino Micro':'أردوينو Micro','Arduino Pro Mini':'أردوينو Pro Mini',
 'Raspberry Pi Pico':'راسبيري باي Pico','Raspberry Pi Pico W':'راسبيري باي Pico W',
 'Brushless DC Motor':'محرك تيار مستمر دون فُرش','30A ESC':'متحكم سرعة إلكتروني ESC بقدرة 30A',
 'Color Sensor TCS3200':'حساس الألوان TCS3200','Arduino UNO Starter Kit':'طقم البداية أردوينو UNO',
 'ESP32 Starter Kit':'طقم البداية ESP32','37-in-1 Sensor Kit':'طقم 37 حساسًا','45-in-1 Sensor Kit':'طقم 45 حساسًا',
 'Robot Car Kit':'طقم سيارة روبوت','Line Follower Kit':'طقم روبوت تتبّع الخط',
 'Obstacle Avoidance Kit':'طقم روبوت تفادي العوائق','Bluetooth Robot Kit':'طقم روبوت بلوتوث',
 'Electronics Learning Kit':'طقم تعلّم الإلكترونيات','Breadboard Learning Kit':'طقم تعلّم لوحة التجارب',
}
DESCRIPTION = {
 'boards':('A development board for programmable electronics projects. Confirm the board variant and pinout before connecting components.', 'لوحة تطوير لمشاريع الإلكترونيات القابلة للبرمجة. تحقّق من إصدار اللوحة ومخطط الأرجل قبل توصيل المكونات.'),
 'sensors':('A sensing component for electronics experiments and automation. Confirm the supply voltage and interface for the supplied version.', 'مكوّن استشعار للتجارب الإلكترونية والأتمتة. تحقّق من جهد التغذية وواجهة الاتصال للإصدار المورّد.'),
 'communication':('A wireless communication module for connected electronics projects. Confirm wiring and logic levels before use.', 'وحدة اتصال لاسلكي للمشاريع الإلكترونية المتصلة. تحقّق من التوصيلات ومستويات الإشارات قبل الاستخدام.'),
 'displays':('A display for readings, messages, or project status. Confirm its driver and interface before connecting it.', 'شاشة لعرض القراءات والرسائل وحالة المشروع. تحقّق من دارة القيادة وواجهة الاتصال قبل توصيلها.'),
 'robotics':('A component for robot motion and control. Match the power supply and controller to the supplied part.', 'مكوّن لحركة الروبوت والتحكم به. استخدم مصدر تغذية ومتحكمًا مناسبين للقطعة المورّدة.'),
 'power':('A power or switching component. Confirm the supplied version and its electrical ratings before use.', 'مكوّن للتغذية أو التبديل الكهربائي. تحقّق من الإصدار والحدود الكهربائية قبل الاستخدام.'),
 'connections':('A connection accessory for building and prototyping circuits. Check connector type and dimensions.', 'ملحق توصيل لبناء الدارات والنماذج التجريبية. تحقّق من نوع الموصل والأبعاد.'),
 'components':('An electronic component for learning and circuit building. Ask us to confirm the supplied value, rating, and package.', 'مكوّن إلكتروني للتعلّم وبناء الدارات. تواصل معنا لتأكيد القيمة والحدود الكهربائية ونوع العبوة.'),
 'kits':('A kit or expansion board for electronics and robotics. Ask us for the exact included components before ordering.', 'طقم أو لوحة توسعة للإلكترونيات والروبوتات. تواصل معنا لمعرفة المحتويات الدقيقة قبل الطلب.'),
}

def import_catalog(first,second):
    products=[]; by_key={}; audit=[]
    def add(name,cents,source):
        name=' '.join(name.strip().split()); k=key(name)
        if k in by_key:
            p=by_key[k]; p['sources'].append(source); p['aliases'].append(name)
            if cents is not None and p['price_cents'] is None:p['price_cents']=cents
            audit.append({'source':source,'product_id':p['id'],'source_name':name})
            return
        cat=category(name)
        ar=ARABIC.get(name)
        if name.startswith('Resistors ('):
            name='Resistor assortment'; ar='مجموعة مقاومات'; cat='components'
        if ar is None:raise ValueError('Missing Arabic product name: '+name)
        p={'id':f'tv-{len(products)+1:03d}','name':name,'name_ar':ar,'aliases':[],
           'category':cat,'price_cents':cents,'price_status':'confirmed' if cents is not None else 'request',
           'description':DESCRIPTION[cat][0],'description_ar':DESCRIPTION[cat][1],
           'image_path':'','image_kind':'illustration','sources':[source]}
        p['image_path']='images/products/'+p['id']+'.svg'
        products.append(p);by_key[k]=p;audit.append({'source':source,'product_id':p['id'],'source_name':name})
    for sheet,rows in read_sheets(first):
        if not rows or rows[0][1].get('B')!='Item Name':continue
        for row,c in rows[1:]:
            if c.get('B') and c.get('A','').isdigit():
                price=c.get('F','')
                cents=int((Decimal(price)*100).quantize(Decimal('1'),ROUND_HALF_UP)) if price else None
                add(c['B'],cents,{'file':Path(first).name,'sheet':sheet,'row':row,'retail_cell':f'F{row}'})
    for sheet,rows in read_sheets(second):
        if not rows or rows[0][1].get('A')!='Item':continue
        for row,c in rows[1:]:
            if c.get('A'):
                # This workbook is a purchasing plan. Its summary calls these costs.
                # Never publish those numbers as customer retail prices.
                add(c['A'],None,{'file':Path(second).name,'sheet':sheet,'row':row,'retail_cell':None})
    try:from .apply_product_photos import apply_photos
    except ImportError:from apply_product_photos import apply_photos
    apply_photos(products)
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'source_rows':len(audit),'products':len(products),'confirmed_prices':sum(p['price_cents'] is not None for p in products),
            'request_prices':sum(p['price_cents'] is None for p in products),'mapping':audit,
            'pricing_note':'First workbook Our price column is retail; second workbook is a purchasing cost/stock plan. Costs are not public.'}
    (ROOT/'data/import_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print({k:v for k,v in report.items() if k!='mapping'})
    return products

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('first');parser.add_argument('second')
    args=parser.parse_args();import_catalog(args.first,args.second)
