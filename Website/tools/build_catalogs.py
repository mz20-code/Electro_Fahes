"""Model-specific bilingual fault catalog, reviewed against manufacturer manuals."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

STEPS={
 'service': [('Record the code and contact a qualified service technician if it persists.','سجّل الرمز وتواصل مع فني صيانة مؤهل إذا استمر العطل.')],
 'heat': [('Keep external ventilation openings clear and let the unit cool.','اترك فتحات التهوية الخارجية خالية من العوائق واترك الجهاز يبرد.'),('Ask a technician to inspect cooling if the alarm returns.','اطلب من فني فحص نظام التبريد إذا عاد التنبيه.')],
 'fan': [('Check for visible obstruction at the external air vents without opening the unit.','تحقّق من وجود عوائق ظاهرة عند فتحات الهواء الخارجية دون فتح الجهاز.'),('Fan wiring and replacement require a qualified technician.','يجب أن يفحص فني مؤهل توصيلات المروحة ويستبدلها عند الحاجة.')],
 'load': [('Reduce connected loads using their normal controls.','خفّض الأحمال المتصلة باستخدام مفاتيحها العادية.'),('If the alarm remains, arrange an inspection.','إذا استمر التنبيه، اطلب فحص الجهاز.')],
 'low_battery': [('Check the displayed battery charge level and available charging supply.','تحقّق من مستوى شحن البطارية الظاهر ومن توفر مصدر للشحن.'),('Ask your installer to check battery condition and the configured battery type.','اطلب من المركّب فحص حالة البطارية ونوعها المحدد في الإعدادات.')],
 'battery': [('Ask the installer to verify battery compatibility, charging settings, and isolated wiring.','اطلب من المركّب التحقق من توافق البطارية وإعدادات الشحن والتوصيلات بعد عزل التغذية.')],
 'pv': [('Stop using the affected system and ask the installer to verify the PV string design against this model’s limits.','أوقف استخدام النظام المتأثر واطلب من المركّب التحقق من تصميم سلاسل الألواح وفق حدود هذا الطراز.')],
 'wiring': [('A qualified installer must isolate all supplies and inspect the relevant wiring.','يجب أن يعزل مركّب مؤهل جميع مصادر التغذية ويفحص التوصيلات المعنية.')],
 'parallel': [('Ask the installer to verify parallel settings, phase arrangement, and communication cables for this model.','اطلب من المركّب التحقق من إعدادات التوازي وتوزيع الأطوار وكابلات الاتصال لهذا الطراز.')],
 'bms': [('Ask the installer to check the battery protocol, communication cable, and compatible firmware.','اطلب من المركّب فحص بروتوكول البطارية وكابل الاتصال وتوافق البرامج الثابتة.'),('Keep BMS protections enabled.','اترك وسائل حماية نظام إدارة البطارية مفعّلة.')],
 'grid': [('Check whether utility power is available. A technician should verify voltage and frequency.','تحقّق من توفر كهرباء الشبكة. يجب أن يفحص فني الجهد والتردد.')],
 'settings': [('Check the recent settings change with your installer and follow the model’s manual.','راجع التغيير الأخير في الإعدادات مع المركّب واتبع دليل الطراز.')],
 'firmware': [('Firmware changes should be performed by the installer using files approved for the exact model.','يجب أن يُجري المركّب تحديثات البرنامج الثابت باستخدام ملفات معتمدة للطراز المحدد.')],
 'auto': [('Monitor the display; this message can accompany a normal control transition. Contact the installer if it persists.','راقب الشاشة؛ قد تظهر هذه الرسالة أثناء انتقال عادي في التحكم. تواصل مع المركّب إذا استمرت.')],
}

def rows(block,kind,page):
 out=[]
 for line in block.strip().splitlines():
  code,en,ar,action=line.split('|')
  out.append({'code':code,'type':kind,'name':en,'name_ar':ar,'action':action,'page':page,'steps':[{'en':e,'ar':a} for e,a in STEPS[action]]})
 return out

growatt=rows('''
01|Cooling fan stopped|توقّف مروحة التبريد|fan
02|Inverter overheated|ارتفاع حرارة العاكس|heat
03|Battery overvoltage|ارتفاع جهد البطارية|battery
04|Battery undervoltage|انخفاض جهد البطارية|low_battery
05|Output short circuit|قصر في خرج العاكس|wiring
06|Output overvoltage|ارتفاع جهد الخرج|service
07|Overload timeout|انتهاء مهلة زيادة الحمل|load
08|DC bus overvoltage|ارتفاع جهد ناقل التيار المستمر|service
09|DC bus startup failure|فشل بدء تشغيل ناقل التيار المستمر|service
51|Overcurrent or surge|تيار زائد أو اندفاع تيار|service
52|DC bus undervoltage|انخفاض جهد ناقل التيار المستمر|service
53|Inverter startup failure|فشل بدء تشغيل العاكس|service
55|DC voltage in AC output|وجود جهد مستمر في الخرج المتناوب|service
56|Open battery connection|انقطاع اتصال البطارية|battery
57|Current sensor failure|خلل حساس التيار|service
58|Output undervoltage|انخفاض جهد الخرج|service
60|Negative power fault|عطل القدرة السالبة|parallel
61|PV input overvoltage|ارتفاع جهد دخل الألواح|pv
62|Internal communication failure|خلل الاتصال الداخلي|service
80|CAN communication failure|خلل اتصال CAN|parallel
81|Parallel host lost|فقدان الجهاز الرئيسي في التوازي|parallel
''','Fault',35)+rows('''
01|Cooling fan stopped during operation|توقّف مروحة التبريد أثناء التشغيل|fan
02|High temperature|ارتفاع الحرارة|heat
03|Battery overcharge warning|تنبيه زيادة شحن البطارية|battery
04|Low battery warning|تنبيه انخفاض شحن البطارية|low_battery
07|Overload warning|تنبيه زيادة الحمل|load
10|Output power reduced|خفض قدرة الخرج|grid
12|Solar charging paused: low battery|توقف الشحن الشمسي بسبب انخفاض جهد البطارية|low_battery
13|Solar charging paused: high PV voltage|توقف الشحن الشمسي بسبب ارتفاع جهد الألواح|pv
14|Solar charger overload|زيادة حمل الشاحن الشمسي|load
15|Different utility inputs in parallel|اختلاف مداخل الشبكة في نظام التوازي|parallel
16|Parallel input phase mismatch|اختلاف طور الدخل في التوازي|parallel
17|Parallel output phase missing|فقدان طور الخرج في التوازي|parallel
18|Buck converter overcurrent|زيادة تيار المحول الخافض|service
19|Battery disconnected|انقطاع اتصال البطارية|battery
20|BMS communication failure|خلل الاتصال بنظام إدارة البطارية|bms
21|Insufficient PV power|قدرة الألواح غير كافية|pv
22|Battery required for parallel operation|البطارية مطلوبة لتشغيل التوازي|parallel
25|Parallel inverter capacity mismatch|اختلاف قدرات العواكس المتوازية|parallel
''','Warning',36)

deye=rows('''
F08|GFDI relay fault|خلل ريليه كشف العطل الأرضي GFDI|service
F13|Operating mode changed|تغيير وضع التشغيل|auto
F18|Hardware AC overcurrent|تيار متناوب زائد تكشفه الدارة|load
F20|Hardware DC overcurrent|تيار مستمر زائد تكشفه الدارة|load
F22|Emergency stop fault|عطل الإيقاف الطارئ|service
F23|Transient AC leakage overcurrent|تيار تسرب متناوب زائد عابر|wiring
F24|DC insulation resistance fault|خلل مقاومة عزل التيار المستمر|wiring
F26|DC bus imbalance|عدم توازن ناقل التيار المستمر|service
F29|Parallel CAN bus fault|خلل ناقل CAN في التوازي|parallel
''','Fault',40)+rows('''
F34|AC overcurrent|زيادة التيار المتناوب|load
F35|Utility grid unavailable|غياب كهرباء الشبكة|grid
F41|Parallel system stopped|توقّف نظام التوازي|parallel
F42|Low AC line voltage|انخفاض جهد خط الشبكة|grid
F47|High grid frequency|ارتفاع تردد الشبكة|grid
F48|Low grid frequency|انخفاض تردد الشبكة|grid
F56|Low DC bus voltage|انخفاض جهد ناقل التيار المستمر|low_battery
F58|BMS communication fault|خلل الاتصال بنظام إدارة البطارية|bms
F63|Arc detection fault (US feature)|عطل كشف القوس الكهربائي (ميزة للسوق الأمريكي)|wiring
F64|High heatsink temperature|ارتفاع حرارة المبدد الحراري|heat
''','Fault',41)

felicity=rows('''
01|Fan stopped|توقّف المروحة|fan
02|Overload|زيادة الحمل|load
03|Low battery|انخفاض شحن البطارية|low_battery
50|BMS firmware mismatch|عدم توافق البرنامج الثابت لنظام إدارة البطارية|firmware
51|BMS blocks charging|نظام إدارة البطارية يمنع الشحن|bms
52|BMS blocks discharging|نظام إدارة البطارية يمنع التفريغ|bms
53|BMS requests charging|نظام إدارة البطارية يطلب الشحن|auto
80|BMS communication fault|خلل الاتصال بنظام إدارة البطارية|bms
''','Warning',22)
for code in range(54,66):felicity+=rows(f'{code}|Battery BMS reports an issue|نظام إدارة البطارية يبلغ عن مشكلة|bms','Warning',22)
felicity+=rows('''
01|DC bus overvoltage|ارتفاع جهد ناقل التيار المستمر|service
02|DC bus undervoltage|انخفاض جهد ناقل التيار المستمر|service
03|DC bus startup failure|فشل بدء تشغيل ناقل التيار المستمر|service
04|Inverter startup failure|فشل بدء تشغيل العاكس|service
05|Software overcurrent detection|اكتشاف تيار زائد برمجيًا|service
06|Hardware overcurrent detection|اكتشاف تيار زائد بواسطة الدارة|service
''','Fault',22)+rows('''
07|Output undervoltage|انخفاض جهد الخرج|load
08|Output overvoltage|ارتفاع جهد الخرج|service
09|Output short circuit|قصر في الخرج|wiring
10|Overload timeout|انتهاء مهلة زيادة الحمل|load
11|Battery overvoltage|ارتفاع جهد البطارية|battery
12|DC/DC converter overcurrent|زيادة تيار محول DC/DC|service
13|PV input overvoltage|ارتفاع جهد دخل الألواح|pv
14|PV port short circuit|قصر في منفذ الألواح|wiring
15|Abnormal PV power|قدرة ألواح غير طبيعية|pv
16|PV port overcurrent|زيادة تيار منفذ الألواح|service
17|Fan stopped|توقّف المروحة|fan
18|PV converter overheated|ارتفاع حرارة محول الألواح|heat
19|Battery converter overheated|ارتفاع حرارة محول البطارية|heat
20|Inverter circuit overheated|ارتفاع حرارة دارة العاكس|heat
21|Internal temperature too high|ارتفاع الحرارة الداخلية|heat
22|DC/DC current sensor fault|خلل حساس تيار محول DC/DC|service
23|Second DC/DC current sensor fault|خلل حساس تيار محول DC/DC الثاني|service
24|Inverter current sensor fault|خلل حساس تيار العاكس|service
25|Output current sensor fault|خلل حساس تيار الخرج|service
26|Sharing-current sensor fault|خلل حساس تيار المشاركة|service
27|AC input/output wiring reversed|عكس توصيل دخل وخرج التيار المتناوب|wiring
28|Single unit configured in parallel system|إعداد جهاز منفرد ضمن نظام توازي|parallel
29|DC/DC startup failure|فشل بدء تشغيل محول DC/DC|service
31|Convert H circuit overheated|ارتفاع حرارة دارة Convert H|heat
32|LLC transformer overheated|ارتفاع حرارة محول LLC|heat
33|LLC circuit overcurrent|زيادة تيار دارة LLC|service
34|Hardware DC/DC overcurrent|تيار زائد في DC/DC تكشفه الدارة|service
35|DC bus overvoltage|ارتفاع جهد ناقل التيار المستمر|service
40|CAN data lost|فقدان بيانات CAN|parallel
41|Host data lost|فقدان بيانات الجهاز الرئيسي|parallel
42|Synchronization data lost|فقدان بيانات المزامنة|parallel
43|Reverse current into inverter|تيار عكسي إلى العاكس|parallel
44|Inverter firmware versions differ|اختلاف إصدارات البرامج الثابتة للعواكس|firmware
''','Fault',23)

gospower=rows('''
01|Overload|زيادة الحمل|load
02|Upper fan stopped|توقّف المروحة العلوية|fan
03|Lower fan stopped|توقّف المروحة السفلية|fan
04|High grid voltage|ارتفاع جهد الشبكة|grid
05|Parallel outputs not interconnected|مخارج التوازي غير موصولة معًا|parallel
06|Remote shutdown enabled|تفعيل الإيقاف عن بُعد|settings
''','Warning',26)+rows('''
01|DC bus overvoltage|ارتفاع جهد ناقل التيار المستمر|service
02|DC bus undervoltage|انخفاض جهد ناقل التيار المستمر|service
03|DC bus startup failure|فشل بدء تشغيل ناقل التيار المستمر|service
10|Inverter startup failure|فشل بدء تشغيل العاكس|service
11|Software overcurrent detection|اكتشاف تيار زائد برمجيًا|service
12|Hardware overcurrent detection|اكتشاف تيار زائد بواسطة الدارة|service
13|Output undervoltage|انخفاض جهد الخرج|load
14|Output overvoltage|ارتفاع جهد الخرج|service
15|Output short circuit|قصر في الخرج|wiring
16|Inverter current sensor fault|خلل حساس تيار العاكس|service
17|Reverse current into inverter|تيار عكسي إلى العاكس|parallel
20|Overload timeout|انتهاء مهلة زيادة الحمل|load
21|Output current sensor fault|خلل حساس تيار الخرج|service
22|Sharing-current sensor fault|خلل حساس تيار المشاركة|service
23|AC input/output wiring reversed|عكس توصيل دخل وخرج التيار المتناوب|wiring
24|Output relay fault|خلل ريليه الخرج|service
30|Battery overvoltage|ارتفاع جهد البطارية|battery
31|DC/DC converter overcurrent|زيادة تيار محول DC/DC|service
32|DC/DC current sensor fault|خلل حساس تيار محول DC/DC|service
33|Second DC/DC current sensor fault|خلل حساس تيار محول DC/DC الثاني|service
34|DC/DC startup failure|فشل بدء تشغيل محول DC/DC|service
35|Hardware DC/DC overcurrent|تيار زائد في DC/DC تكشفه الدارة|service
36|LLC circuit overcurrent|زيادة تيار دارة LLC|service
37|LLC hardware fault|خلل في دارة LLC|service
40|PV input overvoltage|ارتفاع جهد دخل الألواح|pv
41|PV port short circuit|قصر في منفذ الألواح|wiring
''','Fault',26)+rows('''
42|Abnormal PV power|قدرة ألواح غير طبيعية|service
43|PV port overcurrent|زيادة تيار منفذ الألواح|service
44|PV current sensor fault|خلل حساس تيار الألواح|service
45|Excess PV1 input power|زيادة قدرة دخل الألواح PV1|pv
46|Excess PV2 input power|زيادة قدرة دخل الألواح PV2|pv
50|Fan stopped|توقّف المروحة|fan
51|PV circuit overheated|ارتفاع حرارة دارة الألواح|heat
52|Inverter circuit overheated|ارتفاع حرارة دارة العاكس|heat
53|Convert L circuit overheated|ارتفاع حرارة دارة Convert L|heat
54|Convert H circuit overheated|ارتفاع حرارة دارة Convert H|heat
55|LLC transformer overheated|ارتفاع حرارة محول LLC|heat
60|CAN data lost|فقدان بيانات CAN|parallel
61|Host data lost|فقدان بيانات الجهاز الرئيسي|parallel
62|Synchronization data lost|فقدان بيانات المزامنة|parallel
63|Inverter firmware versions differ|اختلاف إصدارات البرامج الثابتة للعواكس|firmware
64|Parallel output currents differ|اختلاف تيارات الخرج في التوازي|parallel
65|Parallel output modes differ|اختلاف أوضاع الخرج في التوازي|parallel
66|Single unit configured in parallel system|إعداد جهاز منفرد ضمن نظام توازي|parallel
92|DSP–MCU communication failure|خلل الاتصال بين DSP وMCU|service
''','Fault',27)

catalogs=[]
def model(id,brand,name,entries,source,source_ar,url,edition,image,specs=None,source_file=None):
 catalogs.append({'id':id,'brand':brand,'model':name,'verified':True,'image':image,'entries':entries,
   'source':{'title':source,'title_ar':source_ar,'url':url,'edition':edition,'local_file':'/static/manuals/'+source_file if source_file else None},'specs':specs or []})
def spec(en,ar,value):return {'label':en,'label_ar':ar,'value':value}

for power,pv,ac,total in [(3500,4500,60,80),(5000,6000,80,100)]:
 model('growatt-spf-'+str(power)+'-es','Growatt','SPF '+str(power)+' ES',growatt,
  'Growatt SPF 3500/5000 ES user manual','دليل استخدام Growatt SPF 3500/5000 ES',
  '/static/manuals/Growatt_SPF_3500_5000_ES_202109.pdf','2021-09','images/growatt-es.png',[
   spec('Rated output','قدرة الخرج الاسمية',str(power)+' W'),spec('Battery system','جهد منظومة البطارية','48 V DC'),
   spec('AC output','خرج التيار المتناوب','230 V AC ±5%'),spec('Maximum PV array power','القدرة القصوى لمصفوفة الألواح',str(pv)+' W'),
   spec('PV voltage limit (Voc)','حد جهد الدارة المفتوحة للألواح','450 V DC'),spec('MPPT operating range','مجال عمل MPPT','120–430 V DC'),
   spec('Maximum AC charge current','أقصى تيار شحن من الشبكة',str(ac)+' A'),
   spec('Maximum combined charge current','أقصى تيار شحن إجمالي',str(total)+' A')],
  'Growatt_SPF_3500_5000_ES_202109.pdf')
for power in [12,14,16]:
 model('deye-sun-'+str(power)+'k-sg01lp1-eu','Deye',f'SUN-{power}K-SG01LP1-EU',deye,
  'Deye SUN-12/14/16K-SG01LP1-EU user manual','دليل استخدام Deye SUN-12/14/16K-SG01LP1-EU',
  'https://www.deyeinverter.com/deyeinverter/2024/02/03/instructions_sun-12-16k-sg01lp1-eu_240203_en.pdf',
  '2024-02-03, V3','images/brands/Deye.jpg')
model('felicity-ivem6048-ii','Felicity','IVEM6048-II',felicity,
 'Felicity IVEM6048-II user guide','دليل استخدام Felicity IVEM6048-II',
 'https://doc.felicitysolar.com/manual/Inverter/IVEM6048-II/IVEM6048-II%20User%20Guide%20-EN.pdf',
 'Manufacturer English guide, reviewed 2026-10-11','images/brands/Felicity.webp')
for power in [4,6,12]:
 model('gospower-gpeo-'+str(power)+'kl1','Gospower',f'GPEO-{power}KL1',gospower,
  'Gospower GPEO 4/6/12 kVA user manual','دليل استخدام Gospower GPEO 4/6/12 kVA',
  'https://pl.gospowerpv.com/storage/uploads/mp4/202408/19/gpeo-series-user-manual-4kva-12kva.pdf',
  'Version 0.3','images/brands/Gospower.jpg')

sako_faults=[]
for e in growatt:
 if e['type']=='Fault' and e['code'] in {'01','02','03','04','05','06','07','08','09','51','52','53','55','56','57','58'}:
  sako_faults.append(dict(e,page=17))
sako_faults+=rows('59|PV voltage exceeds limit|جهد الألواح يتجاوز الحد|pv','Fault',17)
sako_warnings=rows('''
01|Fan stopped during operation|توقّف المروحة أثناء التشغيل|fan
02|High temperature|ارتفاع الحرارة|heat
03|Battery overcharge warning|تنبيه زيادة شحن البطارية|battery
04|Low battery|انخفاض شحن البطارية|low_battery
07|Overload|زيادة الحمل|load
10|Output power reduced|خفض قدرة الخرج|grid
15|Low PV power|انخفاض قدرة الألواح|pv
16|High AC input during bus startup|ارتفاع جهد الشبكة أثناء بدء تشغيل الناقل|grid
Eq|Battery equalization active|معادلة شحن البطارية مفعّلة|auto
bp|Battery not connected|البطارية غير متصلة|battery
''','Warning',17)
for power in [3,5]:
 entries=[dict(e) for e in sako_faults]+sako_warnings
 for e in entries:
  if e['type']=='Fault' and e['code']=='05':
   e['name']='Output short circuit or internal converter overheating'
   e['name_ar']='قصر في الخرج أو ارتفاع حرارة المحول الداخلي'
  if e['type']=='Fault' and e['code']=='06' and power==3:
   e['name']='Abnormal output voltage';e['name_ar']='جهد خرج غير طبيعي'
 model(f'sako-sunon-{power}kw','SAKO',f'SUNON {power} kW',entries,
  'SAKO SUNON 3–5 kW user manual','دليل استخدام SAKO SUNON 3–5 kW',
  'https://sakopower.com/wp-content/uploads/2022/03/SUNON-Solar-Inverter-User-Manual-.pdf',
  'Manufacturer SUNON 3–5 kW edition','images/brands/Sako.webp')

# Records without a checked exact-model source remain unpublished.
pending=[
 {'brand':'Bluesun','model':'BSM-5000LV-48H','url':'https://www.bluesunpv.com/downloads/','image':'images/brands/BSM.jpg'},
 {'brand':'MUST','model':None,'url':'https://www.mustpower.com/','image':'images/brands/Must.webp'},
 {'brand':'SOROTEC','model':None,'url':'https://www.sorotecpower.com/download/','image':'images/brands/Sorotech.webp'},
 {'brand':'Voltronic','model':None,'url':'https://voltronicpower.com/','image':'images/brands/Voltronic.webp'},
]
for c in catalogs:
 if c['brand']=='Growatt':c['spec_pages']=[39,40]
 c['source']['edition_ar']=c['source']['edition'].replace('Version','الإصدار').replace('Manufacturer English guide, reviewed','دليل المصنّع بالإنجليزية، مراجعة').replace('Manufacturer SUNON 3–5 kW edition','إصدار المصنّع SUNON 3–5 kW')
addition_file=ROOT/'data/catalogs_additions.json'
if addition_file.exists():
 additions=json.loads(addition_file.read_text(encoding='utf-8'))
 by_id={c['id']:c for c in catalogs};by_id.update({c['id']:c for c in additions['catalogs']})
 catalogs=list(by_id.values());pending=additions['pending']
local_manuals={'Deye':'Deye_SUN_12_16K_20240203.pdf','Felicity':'Felicity_IVEM6048_II.pdf','Gospower':'Gospower_GPEO_V03.pdf','SAKO':'SAKO_SUNON_3_5KW.pdf'}
for c in catalogs:
 filename=local_manuals.get(c['brand'])
 if filename and (ROOT/'static/manuals'/filename).is_file():c['source']['local_file']='/static/manuals/'+filename
 c.setdefault('image_match','family');c['reviewed_on']='2026-10-12'
(ROOT/'data/catalogs.json').write_text(json.dumps({'catalogs':catalogs,'pending':pending},ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified catalogs',len(catalogs),'fault/warning records',sum(len(c['entries']) for c in catalogs))
