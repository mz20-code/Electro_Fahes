"""Create transparent, code-native product illustrations for the catalog."""
from pathlib import Path
import json, html

ROOT=Path(__file__).resolve().parents[1]

def rect(x,y,w,h,fill,rx=3,stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'
def circle(x,y,r,fill,stroke=None):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'
def line(x1,y1,x2,y2,color,width=2):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round"/>'
def text(x,y,value,size=12,color='#f2f4f7'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="Arial,sans-serif" font-weight="600" text-anchor="middle">{html.escape(value)}</text>'
def pins(x,y,count,horizontal=True):
    return ''.join(rect(x+i*10 if horizontal else x,y if horizontal else y+i*10,6,10,'#bdad7c',1) for i in range(count))

def board(label,w=190,h=110,color='#12637e',chip=True):
    x=(320-w)/2;y=(240-h)/2
    a=rect(x,y,w,h,color,9,'#65a0a0')
    for dx,dy in [(10,10),(w-10,10),(10,h-10),(w-10,h-10)]:a+=circle(x+dx,y+dy,4,'#c7aa63')+circle(x+dx,y+dy,2,'#061922')
    a+=rect(x+26,y+9,w-51,14,'#101619',2)+rect(x+26,y+h-22,w-51,14,'#101619',2)
    for i in range(int((w-57)/9)):
        a+=circle(x+30+i*9,y+16,2,'#bcaf74')+circle(x+30+i*9,y+h-15,2,'#bcaf74')
    a+=rect(x-10,y+35,35,30,'url(#metal)',3,'#808998')
    a+=rect(x-4,y+75,24,18,'#20252b',2)+circle(x+4,y+84,4,'#696f77')
    if chip:
        a+=rect(x+w*.44,y+35,w*.35,38,'#1b2229',4,'#687179')
        a+=pins(x+w*.44+5,y+28,int(w*.31/10))+pins(x+w*.44+5,y+73,int(w*.31/10))
    for i in range(4):
        a+=rect(x+31+i*12,y+39,8,17,'#45505a',2)+rect(x+31+i*12,y+60,8,8,'#c9b280',1)
    a+=text(160,y+h-31,label,10)
    return a

def sensor_base(w=125,h=77):
    return rect((320-w)/2,130,w,h,'#155b83',5,'#68a0bb')+pins((320-w)/2+25,207,min(4,int(w/20)))

def render(p):
    n=p['name'].lower();cat=p['category'];a=''
    if (' kit' in n or cat=='kits') and not any(v in n for v in ['devkit','capacitor','stepper']):
        if any(v in n for v in ['car','robot','follower','obstacle','chassis']):
            a=rect(98,48,126,150,'#e4a923',18,'#ffe28b')
            a+=rect(88,71,18,45,'#252a31',4)+rect(215,71,18,45,'#252a31',4)
            a+=rect(83,141,25,55,'#20252b',6)+rect(216,141,25,55,'#20252b',6)
            a+=rect(116,82,88,69,'#12637e',4)+rect(139,95,38,29,'#1d242a',3)
            a+=circle(136,58,13,'url(#metal)')+circle(188,58,13,'url(#metal)')
            a+=pins(117,153,8)+rect(135,171,48,10,'#687c83',2)
        elif 'shield' in n:
            a=board('SHIELD',180,125,'#267654',False)
            for i in range(4):a+=rect(114+i*26,100,18,63,['#e6c047','#dd6554','#367da1','#1b262b'][i],2)
        else:
            a=rect(63,44,195,163,'#34414d',13,'#829299')+rect(69,50,183,151,'#d7e1e4',9)
            a+=rect(82,69,88,64,'#11718e',5)+rect(98,86,45,24,'#273138',3)
            a+=rect(179,69,62,60,'#f4f5f5',5,'#a4afb7')
            for i in range(5):
                for j in range(4):a+=circle(186+i*10,77+j*12,1.5,'#657179')
            for i,c in enumerate(['#d65358','#41ae88','#336dad']):a+=circle(94+i*27,159,9,c)+line(94+i*27,168,94+i*27,185,'#a1aab1',3)
            a+=rect(174,149,61,36,'#277250',3)+circle(205,166,11,'url(#metal)')
    elif 'hc-sr04' in n:
        a=sensor_base(191,65)
        for x in [120,203]:a+=circle(x,111,40,'#aebdc5','#d9e2e7')+circle(x,111,33,'#354450')+circle(x,111,25,'#8c9aa4')
        for x in [120,203]:
            for i in range(-3,4):a+=line(x-21,111+i*6,x+21,111+i*6,'#424e57',1)
        a+=text(161,174,'HC-SR04',11)
    elif 'dht' in n:
        fill='#f4f1e9' if '22' in n else '#419ad2'
        a=rect(122,58,78,123,fill,9,'#7ca4b4')+pins(136,181,4)
        for i in range(4):
            for j in range(7):a+=rect(130+i*16,69+j*14,10,6,'#226582' if '11' in n else '#88989b',2)
    elif 'pir' in n:
        a=sensor_base(146,68)+circle(160,110,57,'#e6edf0','#c2d3df')
        for i in [-1,0,1]:a+=f'<ellipse cx="160" cy="110" rx="{15+abs(i)*17}" ry="55" fill="none" stroke="#b8c9d4" opacity=".7"/>'
        for y in [86,110,135]:a+=f'<ellipse cx="160" cy="{y}" rx="49" ry="10" fill="none" stroke="#b8c9d4" opacity=".6"/>'
    elif 'mq-' in n:
        a=sensor_base(128,75)+rect(125,57,71,94,'#b1aaa1',12,'#d8d4ca')
        a+=f'<ellipse cx="160" cy="63" rx="35" ry="16" fill="#92949a" stroke="#dbddd9"/>'
        for y in range(72,142,8):a+=line(129,y,190,y,'#686f75',1)
        for x in range(133,191,8):a+=line(x,66,x,147,'#d9ceba',1)
        a+=text(160,178,p['name'].split()[0],12)
    elif 'ph sensor' in n or 'turbidity' in n or 'ds18' in n:
        a=rect(73,98,87,58,'#266988',5)+rect(88,110,31,27,'#26303c',3)+pins(91,156,4)
        a+=f'<path d="M153,126 C245,45 210,55 242,108" fill="none" stroke="#626b73" stroke-width="5"/>'
        if 'ph' in n or 'ds18' in n:a+=rect(228,103,26,90,'url(#metal)',8)+rect(228,173,26,26,'#c8e2e9',7)+rect(234,99,14,16,'#151d25',2)
        else:a+=rect(217,97,53,83,'#6fa8b1',13,'#bcd7d9')+rect(227,116,33,25,'#182830',4)
    elif 'moisture' in n or 'water level' in n or 'rain' in n:
        a=rect(111,48,102,140,'#1d686f' if 'rain' in n else '#af5540',7,'#d2aa70')+pins(139,188,4)
        for i in range(7):a+=line(121+i*13,59,121+i*13,174,'#d1b276',4)
        if 'moisture' in n:a+=rect(148,108,27,86,'#000',0)
    elif 'fingerprint' in n:
        a=rect(108,66,110,120,'#414851',12,'#a8b2ba')+rect(122,80,82,68,'#7c2933',9,'#c46b64')
        for i in range(5):a+=f'<path d="M{131+i*5},130 C{117+i*8},80 {196-i*8},80 {195-i*5},130" fill="none" stroke="#e2a097" stroke-width="1.5"/>'
        a+=pins(126,186,6)
    elif 'rfid' in n or 'rc522' in n:
        a=rect(86,67,151,120,'#176581',5)+pins(127,187,8)
        for i in range(6):a+=rect(95+i*5,76+i*5,133-i*10,87-i*10,'none',9,'#abcfce')
        a+=rect(132,161,49,16,'#1c252c',3)
    elif 'ldr' in n:
        a=line(145,123,136,210,'#b6b9b9',4)+line(179,123,190,210,'#b6b9b9',4)+circle(160,99,50,'#e8c99a','#d5a979')
        a+=f'<path d="M139,66 H178 V82 H140 V98 H178 V114 H140 V132 H175" stroke="#9b5634" stroke-width="8" fill="none"/>'
    elif 'joystick' in n:
        a=sensor_base(144,66)+rect(126,108,68,58,'url(#metal)',7)+rect(145,88,30,60,'#323a42',5)+f'<ellipse cx="160" cy="78" rx="52" ry="28" fill="#292f36" stroke="#596570"/>'
    elif 'keypad' in n:
        a=rect(91,37,139,160,'#153d67',8,'#7a92a2')
        for i in range(4):
            for j in range(4):a+=rect(101+i*30,49+j*34,23,27,'#e4d9ca' if i<3 else '#bb4e4a',4)+text(112+i*30,67+j*34,str(j*3+i+1) if i<3 else ['A','B','C','D'][j],11,'#324255')
        a+=rect(143,197,31,21,'#bfaaa0',1)
    elif 'clock' in n or 'ds3231' in n:
        a=board('RTC',145,95,'#285f87',False)+circle(181,112,33,'url(#metal)','#c4cbd0')+circle(181,112,26,'#b4bfc7')
    elif cat=='sensors':
        a=sensor_base(142,97)+rect(101,86,44,42,'#232e35',5,'#a1b0b5')+rect(181,105,26,22,'#276db0',3)+circle(194,116,6,'url(#metal)')
        if 'sound' in n:a+=circle(124,100,21,'url(#metal)')+circle(124,100,14,'#283239')
        elif 'ir' in n or 'flame' in n:a+=circle(125,76,11,'#202731')+line(120,85,120,115,'#bac7c8',3)+circle(159,76,11,'#bedbe4')
        elif 'mpu' in n:a+=rect(137,98,40,40,'#202c35',4)+pins(111,85,8)
    elif 'servo' in n:
        a=rect(105,102,112,75,'#3a75ba' if 'sg90' in n else '#3b424a',8,'#9baabd')
        a+=rect(89,132,144,15,'#4294b9' if 'sg90' in n else '#aaafb1',3)+rect(123,82,73,28,'#3384bb' if 'sg90' in n else '#777f85',5)
        a+=circle(165,73,17,'#eaedf0')+rect(113,65,105,13,'#eef1f2',7)+circle(164,71,5,'#b0b9c1')
        a+=f'<path d="M210,163 C268,172 233,208 287,200" fill="none" stroke="#d16539" stroke-width="6"/>'
    elif 'wheel' in n:
        for x in [114,208]:
            a+=circle(x,124,55,'#202831','#66737c')+circle(x,124,39,'#dcaf3a')+circle(x,124,27,'#3f454c')+circle(x,124,9,'#dec67b')
            for dx,dy in [(0,-19),(0,19),(-19,0),(19,0)]:a+=circle(x+dx,124+dy,5,'#deb741')
    elif 'motor' in n or 'stepper' in n:
        if 'gear' in n or 'tt motor' in n:
            a=rect(79,92,130,74,'#edc837',12,'#fae78e')+rect(197,99,46,61,'url(#metal)',7)+rect(94,111,44,42,'#e1d6b8',6)+circle(116,131,19,'#edf0ee')+rect(57,124,46,12,'#b9c3cb',3)
        else:
            a=circle(157,122,63,'url(#metal)','#a5afb5')+rect(125,103,64,43,'#448bb4',6)+rect(151,45,13,76,'#d0d6d9',3)
            a+=rect(82,115,153,14,'#a8b4bc',4)
            a+=f'<path d="M211,147 C236,149 223,183 268,190" stroke="#bf5558" stroke-width="5" fill="none"/>'
    elif 'esc' in n:
        a=rect(109,85,118,76,'#305684',7,'#819dac')+text(167,129,'ESC',22)
        for i,c in enumerate(['#dc575d','#555e68','#e9ae47']):a+=f'<path d="M111,{99+i*21} C68,{90+i*28} 66,{80+i*40} 48,{80+i*40}" stroke="{c}" stroke-width="7" fill="none"/>'
        for i in range(3):a+=line(224,100+i*20,268,100+i*25,'#9faeb5',6)
    elif cat=='boards' or cat=='communication' or 'devkit' in n:
        label=p['name'].split(' (')[0].replace('Arduino ','')
        if 'pico' in n:a=board('PICO W' if 'w' in n else 'PICO',188,72,'#297b52')
        elif 'esp32' in n or 'esp8266' in n or 'nodemcu' in n:a=board('ESP32' if 'esp32' in n else 'ESP8266',136,130,'#28323b')+rect(156,97,49,43,'url(#metal)',3)+rect(135,54,58,27,'#253032',3)
        elif 'nano' in n or 'mini' in n or 'micro' in n:a=board(label,165,79,'#216080')
        elif cat=='communication':a=board(label,142,86,'#175783')+f'<path d="M119,93 V79 H138 V91 H156 V79 H173 V91 H190" stroke="#c2b574" stroke-width="3" fill="none"/>'
        else:a=board(label,211 if 'mega' in n else 196,123)
        if 'cam' in n:a+=rect(125,110,42,44,'#171e24',4)+circle(146,131,14,'#516870')+circle(146,131,8,'#0f273c')
    elif cat=='displays':
        if 'lcd' in n:
            a=rect(63,67,195,122,'#276b4d',6,'#82aa89')+rect(79,80,163,93,'#182c38',4)+rect(88,91,146,71,'#b2c682',2)
            a+=text(161,118,'TECHVERSE',15,'#29422b')+text(161,144,'16 x 2  I2C',12,'#29422b')+pins(106,189,12)
        elif 'oled' in n:
            a=rect(89,60,144,129,'#234c79',7,'#91a8b7')+rect(100,77,122,94,'#121e2c',3)
            a+=text(161,116,'TECHVERSE',13,'#69c8fc')+line(121,141,193,141,'#71d2ee',3)+pins(137,189,4)
        elif 'matrix' in n:
            a=rect(83,62,156,136,'#243a43',5)+rect(96,69,130,123,'#263033',3)
            for i in range(8):
                for j in range(8):a+=circle(105+i*16,78+j*15,5,'#e35d56' if i in [2,3,4,5] and j in [1,2,3,4,5,6] else '#623937')
        else:
            count=4 if '4 digit' in n else 1
            a=rect(77 if count==4 else 130,69,171 if count==4 else 59,108,'#333b43',6,'#a0a8ad')
            for i in range(count):
                x=84+i*41 if count==4 else 137
                for dy in [0,38,76]:a+=rect(x,80+dy,27,6,'#dc514d',3)
                for dx in [0,27]:
                    for dy in [7,46]:a+=rect(x+dx-3,80+dy,6,28,'#dc514d',3)
            a+=pins(99 if count==4 else 137,179,12 if count==4 else 5)
    elif 'relay' in n:
        count=4 if '4-' in n else 2 if '2-' in n else 1
        w=60*count+24;x=(320-w)/2
        a=rect(x,83,w,89,'#1a6b88',6)
        for i in range(count):a+=rect(x+12+i*60,95,51,54,'#3d83bd',4)+rect(x+12+i*60,159,51,21,'#65a76e',3)+text(x+37+i*60,126,'RELAY',9)
        a+=pins(x+16,73,3)
    elif 'battery holder' in n:
        a=rect(108,49,108,152,'#252c33',10,'#828d93')+rect(124,58,76,133,'#111b22',16)+line(142,70,181,70,'#b8c4cc',4)+line(137,183,186,183,'#b8c4cc',3)
        a+=f'<path d="M118,181 C66,181 51,211 84,223" stroke="#d85857" stroke-width="5" fill="none"/>'
    elif cat=='power':
        a=board(p['name'].split()[0],152,104,'#1c7291',False)
        a+=circle(137,102,26,'#a8b8bf')+circle(137,102,18,'#796a38')+rect(173,91,32,26,'#333c43',3)
        a+=rect(114,147,40,16,'#2b6093',2)+circle(193,144,14,'url(#metal)')
    elif 'breadboard' in n:
        w=129 if 'mini' in n else 207;h=109;x=(320-w)/2;y=69
        a=rect(x,y,w,h,'#eef1ef',6,'#adb8bd')
        for i in range(int((w-25)/8)):
            for j in [0,1,2,3,4,6,7,8,9,10]:a+=circle(x+14+i*8,y+15+j*7,1.3,'#6e7e81')
        a+=line(x+13,y+5,x+w-13,y+5,'#d26a61',1)+line(x+13,y+h-6,x+w-13,y+h-6,'#577fbd',1)
    elif 'cable' in n or 'jumper' in n:
        colors=['#c15a58','#579b95','#d4bd52','#638ec4'] if 'jumper' in n else ['#485563']
        for i,c in enumerate(colors):
            a+=f'<path d="M{79+i*14},61 C{20+i*15},220 {310-i*15},207 {250-i*16},80" fill="none" stroke="{c}" stroke-width="{5 if len(colors)>1 else 9}"/>'
            a+=rect(69+i*14,46,13 if len(colors)>1 else 25,31,'#566472',3)+rect(245-i*16,59,13 if len(colors)>1 else 25,31,'url(#metal)',3)
    elif 'resistor' in n:
        for i in range(6):
            y=57+i*24;a+=line(81,y,240,y,'#abb9c1',3)+rect(128,y-7,66,15,'#d6bd83',6)
            for j,c in enumerate(['#85533e','#262f37','#cc6344','#af973a']):a+=rect(138+j*13,y-7,4,15,c,0)
    elif 'capacitor' in n:
        for i in range(4):
            x=93+i*46;a+=line(x,127,x-4,194,'#b6c1c9',3)+line(x+14,127,x+18,194,'#b6c1c9',3)+rect(x-5,61+i*10,35,78-i*10,'#374b69',8,'#9cacb6')+f'<ellipse cx="{x+12}" cy="{67+i*10}" rx="16" ry="7" fill="#afbcc4"/>'
    elif 'led' in n:
        for i,c in enumerate(['#c85457','#46aa87','#4488cb']):
            x=99+i*58;a+=line(x-8,137,x-8,204,'#adbdc5',3)+line(x+8,137,x+8,195,'#adbdc5',3)+rect(x-19,69,38,76,c,18,'#d3dadb')+rect(x-22,131,44,10,c,3)+line(x-10,85,x-10,113,'#f2f4f3',3)
    elif 'transistor' in n or 'regulator' in n:
        a=rect(120,78,84,65,'#28323b',17,'#798a95')+pins(139,143,4)+text(163,119,p['name'].split()[0],12)
        for i in range(3):a+=line(143+i*18,151,136+i*24,204,'#aabbc6',4)
    elif 'potentiometer' in n:
        a=circle(161,135,48,'#497da5','#a3b3bd')+rect(120,123,81,25,'url(#metal)',5)+rect(151,51,19,83,'url(#metal)',4)+pins(140,175,4)
    elif 'push button' in n:
        for x,y in [(107,89),(201,139)]:a+=rect(x-32,y-25,67,61,'#bcc5c8',6)+circle(x,y,22,'#28323a')+pins(x-23,y+36,4)
    elif 'header' in n or 'terminal' in n:
        a=rect(83,103,155,47,'#58a881' if 'terminal' in n else '#28343e',5)
        for i in range(8):a+=circle(94+i*19,119,5,'url(#metal)')+line(94+i*19,149,94+i*19,187,'#d1be7e',4)
    else:a=board(p['name'].split()[0],155,104,'#217781')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" role="img"><title>'+html.escape(p['name'])+' — product illustration</title><defs><linearGradient id="metal" x1="0" x2="1"><stop stop-color="#758895"/><stop offset=".35" stop-color="#d7e0e5"/><stop offset=".6" stop-color="#b2c1ca"/><stop offset="1" stop-color="#6d838f"/></linearGradient></defs>'+a+'</svg>'

if __name__=='__main__':
    items=json.loads((ROOT/'data/products.json').read_text(encoding='utf-8'))
    out=ROOT/'static/images/products';out.mkdir(parents=True,exist_ok=True)
    illustrated=[p for p in items if p.get('image_kind','illustration')=='illustration' and p['image_path'].endswith('.svg')]
    for p in illustrated:(ROOT/'static'/p['image_path']).write_text(render(p),encoding='utf-8')
    print('Created',len(illustrated),'transparent SVG product illustrations; existing photographs preserved')
