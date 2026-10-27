from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json,html,hashlib
R=Path(__file__).resolve().parents[2];O=R/'outputs/c3_ui_refinement_20261027'
FONT='C:/Windows/Fonts/meiryo.ttc'
PAL={'light':dict(bg='#eef2f6',panel='#fafbfc',raised='#ffffff',text='#22364c',muted='#53667b',line='#cbd6e1',control='#7b8fa7',accent='#1763a6',selected='#e4effa',soft='#dfe7ef',teal='#14766f',warn='#9b4939'),'dark':dict(bg='#1f2834',panel='#283442',raised='#303e4e',text='#e9eff6',muted='#b7c7d8',line='#4b5e73',control='#8c9fb5',accent='#9acbff',selected='#3a536d',soft='#354557',teal='#92d9d0',warn='#f4c0a5')}
class Art:
 def __init__(self,w,h,dark=False):
  self.w,self.h=w,h;self.p=PAL['dark' if dark else 'light'];self.im=Image.new('RGB',(w,h),self.p['bg']);self.d=ImageDraw.Draw(self.im);self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" xml:lang="ja">',f'<rect width="{w}" height="{h}" fill="{self.p["bg"]}"/>'];self.components=[];self.small=w<1500
 def rec(self,id,kind,box,label='',**extra):self.components.append(dict(id=id,kind=kind,box=[round(x,2) for x in box],label=label,**extra))
 def rect(self,b,fill=None,r=7,stroke=None,sw=1):
  fill=fill or self.p['panel'];stroke=stroke or self.p['line'];self.d.rounded_rectangle(b,radius=r,fill=fill,outline=stroke,width=sw);x,y,x2,y2=b;self.svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def line(self,pts,color=None,width=1):
  color=color or self.p['line'];self.d.line(pts,fill=color,width=width);s=' '.join(f'{x},{y}' for x,y in pts);self.svg.append(f'<polyline points="{s}" fill="none" stroke="{color}" stroke-width="{width}"/>')
 def circle(self,x,y,r,fill,stroke=None,sw=1):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=sw);self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
 def text(self,x,y,s,size=15,color=None,bold=False,maxw=None):
  f=ImageFont.truetype(FONT,size,index=1 if bold else 0);original=s
  if maxw:
   while s and self.d.textlength(s,font=f)>maxw:s=s[:-1]
   if s!=original:s=s[:-1]+'…'
  self.d.text((x,y),s,font=f,fill=color or self.p['text']);self.svg.append(f'<text x="{x}" y="{y}" font-family="Meiryo, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color or self.p["text"]}" dominant-baseline="text-before-edge">{html.escape(s)}</text>')
 def center(self,b,s,size=15,color=None,bold=False):
  f=ImageFont.truetype(FONT,size,index=1 if bold else 0);tw=self.d.textlength(s,font=f);self.text(b[0]+max(5,(b[2]-b[0]-tw)/2),b[1]+(b[3]-b[1]-size*1.4)/2,s,size,color,bold,maxw=b[2]-b[0]-10)
 def panel(self,id,b,title='',scroll=False):
  self.rect(b);self.rec(id,'panel',b,title,scroll=scroll)
  if title:self.text(b[0]+14,b[1]+10,title,16 if self.small else 18,bold=True)
 def button(self,id,b,s,selected=False,primary=False,disabled=False):
  fill=self.p['accent'] if primary else self.p['selected'] if selected else self.p['raised'];fg=('#203448' if self.p is PAL['dark'] else '#ffffff') if primary else self.p['muted'] if disabled else self.p['accent'] if selected else self.p['text'];border=self.p['accent'] if selected or primary else self.p['control'];self.rect(b,fill,6,border,2 if selected else 1);self.center(b,('✓ ' if selected else '')+s,13 if self.small else 15,fg,primary or selected);self.rec(id,'button',b,s,selected=selected,disabled=disabled)
 def check(self,id,x,y,label='',checked=True,width=180):
  self.rect((x,y,x+24,y+24),self.p['accent'] if checked else self.p['raised'],4,self.p['accent'] if checked else self.p['control'])
  if checked:self.line([(x+5,y+12),(x+10,y+17),(x+19,y+7)],'#203448' if self.p is PAL['dark'] else '#fff',2)
  if label:self.text(x+33,y+2,label,13 if self.small else 15,maxw=width-34)
  self.rec(id,'checkbox',(x-4,y-4,x+width,y+30),label,checked=checked)
 def slider(self,id,b,label,value,unit='',fraction=.5):
  x,y,x2,y2=b;self.text(x,y,label,13 if self.small else 15);fy=y+29;end=x2-84;self.line([(x,fy+8),(end,fy+8)],self.p['soft'],5);self.line([(x,fy+8),(x+(end-x)*fraction,fy+8)],self.p['accent'],5);self.circle(x+(end-x)*fraction,fy+8,6,self.p['accent']);self.rect((x2-72,fy-8,x2,fy+24),self.p['raised'],5,self.p['control']);self.center((x2-72,fy-8,x2,fy+24),str(value)+unit,13 if self.small else 15);self.rec(id,'slider+number',b,label,value=value,unit=unit)
 def field(self,id,b,label,value):
  self.text(b[0],b[1],label,13 if self.small else 15);v=(b[0],b[1]+25,b[2],b[3]);self.rect(v,self.p['raised'],5,self.p['control']);self.text(v[0]+10,v[1]+7,str(value),13 if self.small else 15,maxw=v[2]-v[0]-18);self.rec(id,'field',b,label,value=value)
 def save(self,name):
  path=O/'screens'/name;self.im.save(path.with_suffix('.png'));self.svg.append('</svg>');path.with_suffix('.svg').write_text('\n'.join(self.svg),'utf8');return dict(id=name,file='screens/'+name+'.png',vector='screens/'+name+'.svg',size=[self.w,self.h],theme='dark' if self.p is PAL['dark'] else 'light',components=self.components,kind='静止デザイン。動作実装・実機検証ではない')

def stage(a,b):
 x,y,x2,y2=b;w=x2-x;h=y2-y;X=lambda t:x+t*w;Y=lambda t:y+t*h
 original=a.im.copy();a.svg.append(f'<defs><clipPath id="preview-clip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#preview-clip)">')
 a.rect(b,'#193340',0,'#193340');a.line([(X(t),Y(.18+.52*math.sin(t*2.1))) for t in [i/70 for i in range(71)]],'#356f7b',max(3,int(h*.16)));a.line([(X(.04),Y(.96)),(X(.48),Y(.49)),(X(.98),Y(.04))],'#7b8d7c',max(3,int(h*.18)))
 for i in range(30):
  t=(i*73%91)/100+.03;u=(i*31%85)/100+.05;a.circle(X(t),Y(u),h*(.022+i%3*.006),'#315b55')
 a.circle(X(.47),Y(.56),h*.043,'#17394d','#97d6e4',3);a.center((X(.44),Y(.52),X(.50),Y(.60)),'B',int(h*.04),'#ace4f2',True);a.circle(X(.66),Y(.34),h*.033,'#5d3942','#edb3a8',3);a.center((X(.63),Y(.31),X(.69),Y(.37)),'R',int(h*.03),'#edb3a8',True)
 a.rect((x+12,y+12,x+216,y+40),'#18303e',4,'#577b89');a.text(x+20,y+17,'合成プレビュー・映像例',12,'#e3f0f3');a.text(x+18,y2-29,'AutoCine  /  SHOT STUDY',12,'#d6ecee');a.rec('mirror-image','fixed-preview',b,'16:9 合成図。LoL実映像ではない',aspect=16/9)
 clip=(math.ceil(x),math.ceil(y),math.floor(x2),math.floor(y2));original.paste(a.im.crop(clip),clip[:2]);a.im=original;a.d=ImageDraw.Draw(a.im);a.svg.append('</g>')

def replay(a,b):
 x,y,x2,y2=b;s=a.small;pad=12
 a.panel('replay-target',b,'1. リプレイ準備・対象',True)
 a.field('replay-file',(x+pad,y+44,x2-pad,y+109),'リプレイファイル','sample_match.rofl')
 a.button('prepare',(x+pad,y+121,x2-pad,y+159),'準備状態を確認',primary=True)
 a.text(x+pad,y+174,'TargetLock  /  注目プレイヤー',12 if s else 14,bold=True)
 row=26 if s else 32;start=y+205;names=['注目プレイヤー','味方プレイヤー2','味方プレイヤー3','味方プレイヤー4','味方プレイヤー5','相手プレイヤー1','相手プレイヤー2']
 maxrows=min(len(names),max(2,int((y2-start-70)//row)))
 for i,n in enumerate(names[:maxrows]):
  yy=start+i*row
  if i==0:a.rect((x+8,yy-2,x2-8,yy+row-3),a.p['selected'],4,a.p['selected'])
  a.circle(x+23,yy+10,7,a.p['accent'] if i==0 else a.p['soft']);a.text(x+40,yy,n,12 if s else 14,bold=i==0,maxw=x2-x-54)
 a.text(x+pad,y2-62,'他のプレイヤーを表示 ▾',12,a.p['muted']);a.button('preset',(x+pad,y2-38,x2-pad,y2-8),'テンプレート・参考')

def scenes(a,b):
 x,y,x2,y2=b;s=a.small;a.panel('scene-list',b,'2. 試合全体から見せ場を選ぶ',True)
 a.button('scan',(x+12,y+43,x2-12,y+82),'試合全体スキャン',primary=True)
 a.text(x+12,y+93,'検出結果の表示例  /  5シーン',12 if s else 14,a.p['muted'])
 opts=['すべて','キル','アシスト'];bw=(x2-x-32)/3
 for i,n in enumerate(opts):a.button('filter-'+str(i),(x+12+i*(bw+4),y+121,x+12+i*(bw+4)+bw,y+153),n,selected=i==0)
 rows=[('12:34','ダブルキル'),('15:02','アシスト'),('18:11','集団戦'),('22:07','追撃の一瞬'),('27:15','トリプルキル')];rh=53 if s else 72;top=y+170
 for i,(t,n) in enumerate(rows):
  yy=top+i*rh
  if yy+rh>y2-78:break
  a.rect((x+10,yy,x2-10,yy+rh-5),a.p['selected'] if i==0 else a.p['raised'],6,a.p['accent'] if i==0 else a.p['line'],2 if i==0 else 1);a.check('scene-check-'+str(i),x+19,yy+12,'',i in [0,2],25);a.text(x+56,yy+7,t,12,a.p['muted']);a.text(x+56,yy+25,n,13 if s else 16,bold=i==0,maxw=x2-x-68)
 a.text(x+12,y2-68,'行の選択 ≠ 出力チェック',12,a.p['muted']);a.button('scene-jump',(x+12,y2-42,x2-12,y2-9),'選択シーンへ移動')

def timeline(a,b,curve=False):
 x,y,x2,y2=b;s=a.small;a.panel('timeline-editor',b,'キーフレーム・カーブ' if curve else 'タイムライン・詳細編集')
 a.button('track-switch',(x+250,y+7,x+350,y+39),'FOV ▾',selected=True);a.button('add-key',(x2-260,y+7,x2-140,y+39),'＋ キーを追加');a.button('curve-toggle',(x2-130,y+7,x2-12,y+39),'カーブ' if curve else 'キーフレーム',selected=True)
 labelw=152 if s else 210;rightw=218 if s else 296;px=x+labelw;py=y+67;px2=x2-rightw-16;bottom=y2-30;ph=bottom-py
 for i,n in enumerate(['FOV','Yaw','Zoom']):
  a.text(x+18,py+10+i*34,n,13,a.p['accent'] if i==0 else a.p['muted'],True)
 for i in range(13):
  xx=px+(px2-px)*i/12;a.line([(xx,py),(xx,bottom)],a.p['line']);a.text(xx+2,py-23,str(i)+'s',11,a.p['muted'])
 def Y(v):return py+10+(100-v)/80*max(25,ph-25)
 if curve:
  pts=[]
  for i in range(121):
   t=i/10
   if t<=1:v=40
   elif t<=5:u=(t-1)/4;v=40+24*(u*u*(3-2*u))
   elif t<=10:u=(t-5)/5;v=64-16*(u*u*(3-2*u))
   else:v=48
   pts.append((px+(px2-px)*t/12,Y(v)))
  a.line(pts,a.p['accent'],3)
 else:
  for yy in [py+17,py+51,py+85]:
   if yy<bottom:a.line([(px,yy),(px2,yy)],a.p['line'])
 for i,(t,v) in enumerate([(1,40),(5,64),(10,48)]):
  xx=px+(px2-px)*t/12;yy=Y(v) if curve else py+17;a.circle(xx,yy,6,'#d69a57' if i==1 else a.p['accent'],a.p['text'] if i==1 else a.p['panel'],2);a.rec('key-'+str(i),'keyframe-hit-target',(xx-16,yy-16,xx+16,yy+16),'時刻と値を編集',time=t,value=v)
 play=px+(px2-px)*5.5/12;a.line([(play,py-3),(play,bottom)],a.p['text'],2)
 rx=x2-rightw;a.text(rx+8,y+53,'選択キーの値',14,bold=True);a.field('key-time',(rx+8,y+79,x2-14,y+137),'時刻（秒）','5.000');a.field('key-value',(rx+8,y+145,x2-14,y+204),'FOV（°）','64.0')
 if y2-y>260:a.button('blend',(rx+8,y+216,x2-14,y+252),'補間方式を選ぶ ▾')
 a.text(x+16,y2-24,'焦点：12:34 ダブルキル　/　キーの移動はUndo可能',11 if s else 13,a.p['muted'])

def quick(a,b,variant='P',easy=False):
 x,y,x2,y2=b;s=a.small;a.panel('lower-edit',b)
 a.button('easy-toggle',(x+12,y+8,x+125,y+42),'かんたん編集',selected=easy);a.button('detail-toggle',(x+131,y+8,x+244,y+42),'詳細編集',selected=not easy)
 for i,n in enumerate(['シーン','カメラ','色・FX','出力']):a.button('edit-tab-'+str(i),(x+268+i*82,y+8,x+344+i*82,y+42),n,selected=i==1)
 a.text(x2-327,y+17,'適用先：このシーン  ▾',12 if s else 14,a.p['muted'])
 yy=y+59;h=y2-yy-12
 if variant=='S' or easy:
  groups=[('カメラ',['安定した視点','寄りを作る','広く見せる']),('キルフレーム',['シンプル','明るい輪郭','対決レイアウト']),('エフェクト',['控えめ','輝き','勢い'])];gw=(x2-x-48)/3
  for i,(title,labels) in enumerate(groups):
   xx=x+12+i*(gw+12);a.text(xx+8,yy,title,14 if s else 17,bold=True);a.button('open-picker-'+str(i),(xx+gw-88,yy-1,xx+gw,yy+29),'選ぶ ▸')
   for j,n in enumerate(labels):
    cw=(gw-20)/3;left=xx+j*(cw+10);top=yy+39;hh=max(54,h-43);a.rect((left,top,left+cw,top+hh),a.p['selected'] if j==0 else a.p['raised'],6,a.p['accent'] if j==0 else a.p['control'],2 if j==0 else 1);a.circle(left+cw*.5,top+min(26,hh*.34),min(11,cw*.1),a.p['accent'] if i==0 else '#967e4a' if i==1 else a.p['teal']);a.center((left,top+max(30,hh-35),left+cw,top+hh),('✓ ' if j==0 else '')+n,11 if s else 14);a.rec(f'quick-card-{i}-{j}','thumbnail-card',(left,top,left+cw,top+hh),n,selected=j==0)
 else:
  gw=(x2-x-60)/3
  for i,n in enumerate(['既存カメラ','固定＋自動構図','フルオート候補']):
   xx=x+16+i*(gw*.52);cw=gw*.50;a.button('camera-mode-'+str(i),(xx,yy+12,xx+cw,yy+min(h-7,88)),n,selected=i==0)
  mid=x+(x2-x)*.51;a.text(mid,yy,'対象サイド',13,a.p['muted']);a.button('side-blue',(mid,yy+30,mid+88,yy+68),'BLUE',selected=True);a.button('side-red',(mid+96,yy+30,mid+184,yy+68),'RED');a.text(mid,yy+min(90,h-30),'TargetLock：注目プレイヤー',12 if s else 14)
  sx=x+(x2-x)*.70;ww=(x2-sx-28)/2;a.slider('fov',(sx,yy,sx+ww,yy+70),'FOV',48,'°');a.slider('yaw',(sx+ww+20,yy,x2-14,yy+70),'Yaw',32,'°',.6)
  if h>100:a.button('parameter-source',(sx,yy+85,x2-14,min(yy+122,y2-8)),'値の入力元：手動 ／ キー適用 ▾')

def make(name,variant='P',mode='main',w=1920,h=1080,dark=False,overlay=None):
 a=Art(w,h,dark);s=a.small;header=52 if s else 56;status=24;gap=8 if s else 12;bottomh=(236 if s else 320) if mode in ['studio','curve'] else (188 if s else 256);by=h-status-gap-bottomh;top=header+gap;bodybottom=by-gap
 left=232 if s else 320;right=284 if s else 376;cx=gap+left+gap;rx=w-gap-right;cw=rx-gap-cx
 a.rect((0,0,w,header),a.p['panel'],0,a.p['line']);a.text(16,12,'AutoCine',20 if s else 24,a.p['accent'],True);a.text(175 if s else 220,16,'候補3ベース / '+('C3-P 精密編集' if variant=='P' else 'C3-S ショット仕上げ'),11 if s else 15,a.p['muted'])
 actions=[('リプレイ',110),('準備',72),('基本設定',102),('ログ',66),('作成内容を確認',154)];total=sum(z[1] for z in actions)+8*4;x=w-gap-total
 for i,(n,bw) in enumerate(actions):a.button('header-action-'+str(i),(x,9,x+bw,header-8),n,primary=i==4);x+=bw+8
 replay(a,(gap,top,gap+left,bodybottom));scenes(a,(rx,top,w-gap,bodybottom))
 a.panel('mirror-panel',(cx,top,rx-gap,bodybottom),'ミラープレビュー',False);a.text(cx+180,top+12,'合成見本',12,a.p['muted']);a.button('preview-compare',(rx-gap-139,top+8,rx-gap-12,top+38),'調整前と比較')
 stage_top=top+(40 if not s else 36);stage_bottom=bodybottom-(54 if not s else 48);availh=stage_bottom-stage_top;ph=min(availh,cw*9/16);pw=ph*16/9;px=cx+(cw-pw)/2;py=stage_top+(availh-ph)/2;stage(a,(px,py,px+pw,py+ph))
 ty=bodybottom-43;buttons=[('ミラー開始',100),('停止',64),('演出を再生',120),('プレビュー停止',126)];x=cx+12
 if s:buttons=[('ミラー開始',86),('停止',54),('演出を再生',108),('停止',54)]
 for i,(n,bw) in enumerate(buttons):a.button('transport-'+str(i),(x,ty,x+bw,bodybottom-9),n,selected=i==2);x+=bw+7
 a.text(rx-gap-(145 if s else 205),ty+7,'12:34  /  録画しない',11 if s else 14,a.p['muted'])
 if mode in ['studio','curve']:timeline(a,(gap,by,w-gap,h-status-gap),curve=mode=='curve')
 else:quick(a,(gap,by,w-gap,h-status-gap),variant,easy=mode=='easy')
 a.text(14,h-21,'● LoL未接続の表示例　/　設定はシーン別に保持',11 if s else 13,a.p['muted']);a.text(w-(530 if not s else 460),h-21,'追加比較案・未採用  /  静止デザイン（実機テストではない）',11 if s else 13,a.p['muted'])
 if overlay=='camera':camera_drawer(a)
 if overlay=='asset':asset_drawer(a)
 if overlay=='export':export_dialog(a)
 return a.save(name)

def camera_drawer(a):
 x=a.w-620;y=96;bottom=a.h-42;a.panel('camera-drawer',(x,y,a.w-12,bottom),'カメラと演出 / このシーン',True);a.button('drawer-close',(a.w-61,y+8,a.w-24,y+43),'×')
 a.text(x+20,y+65,'設定を変えても中央のミラーは表示したまま',14,a.p['muted']);a.text(x+20,y+112,'カメラの動作',18,bold=True)
 for i,n in enumerate(['既存カメラ','固定＋構図補正','フルオート候補']):a.button('drawer-mode-'+str(i),(x+20+i*188,y+151,x+196+i*188,y+208),n,selected=i==0)
 a.text(x+20,y+234,'FOVの入力元',16,bold=True);a.button('base-source',(x+20,y+270,x+290,y+310),'手動の現在値',selected=True);a.button('key-source',(x+303,y+270,a.w-32,y+310),'キーフレーム')
 a.slider('drawer-fov',(x+24,y+342,a.w-36,y+410),'FOV（手動）',48,'°');a.slider('drawer-distance',(x+24,y+424,a.w-36,y+492),'距離',850,'');a.slider('drawer-height',(x+24,y+506,a.w-36,y+574),'高さ',350,'')
 a.text(x+20,y+605,'FX / 登場アニメ',18,bold=True);a.button('drawer-FX',(x+20,y+646,x+294,y+694),'エフェクトを選ぶ ▸');a.button('drawer-motion',(x+306,y+646,a.w-32,y+694),'6種類の登場アニメ ▸');a.text(x+24,y+722,'正式状態はカタログから取得。枠とFXは別扱い。',14,a.p['muted']);a.button('drawer-cancel',(x+20,bottom-59,x+201,bottom-17),'キャンセル');a.button('drawer-apply',(x+215,bottom-59,a.w-32,bottom-17),'このシーンへ適用',primary=True)

def asset_drawer(a):
 x=a.w-660;y=96;bottom=a.h-42;a.panel('asset-drawer',(x,y,a.w-12,bottom),'キルフレームを選ぶ',True);a.button('asset-close',(a.w-61,y+8,a.w-24,y+43),'×');a.text(x+20,y+64,'適用先：12:34 ダブルキル / このシーンだけ',14,a.p['muted']);a.button('asset-filter',(x+20,y+103,x+210,y+143),'正式承認済み',selected=True);a.button('asset-review',(x+222,y+103,x+421,y+143),'確認用を表示');a.text(x+20,y+164,'図形見本（既存素材の変更ではありません）',14,a.p['muted'])
 for i,n in enumerate(['Simple / 見本','金の輪郭 / 見本','青い縁 / 見本','対決レイアウト / 見本']):
  xx=x+20+i%2*306;yy=y+211+i//2*204;a.rect((xx,yy,xx+290,yy+184),a.p['selected'] if i==0 else a.p['raised'],8,a.p['accent'] if i==0 else a.p['control'],2 if i==0 else 1);a.rect((xx+14,yy+13,xx+276,yy+123),'#20394c',5,'#668294');color=['#bce2f5','#dcc38e','#8dbbd5','#d9b0b5'][i];a.circle(xx+75,yy+68,29,'#25445a',color,3);a.circle(xx+216,yy+68,29,'#25445a',color,3);a.line([(xx+111,yy+68),(xx+177,yy+68)],color,3);a.text(xx+14,yy+136,('✓ ' if i==0 else '')+n,16,bold=i==0);a.rec('asset-card-'+str(i),'material-card',(xx,yy,xx+290,yy+184),n)
 a.text(x+22,y+649,'確認用の使用は正式承認を意味しません。',15,a.p['muted']);a.text(x+22,y+686,'ユーザー不採用素材は推薦・自動選択から除外。',14,a.p['muted']);a.button('asset-cancel',(x+20,bottom-59,x+205,bottom-17),'キャンセル');a.button('asset-apply',(x+217,bottom-59,a.w-32,bottom-17),'このシーンへ適用',primary=True)

def export_dialog(a):
 x=542;y=172;w=838;bottom=918;a.panel('export-review',(x,y,x+w,bottom),'動画を作成する前に確認');a.button('export-close',(x+w-54,y+9,x+w-18,y+43),'×');a.text(x+26,y+64,'チェックした2シーンを書き出す',22,bold=True);a.text(x+26,y+105,'初心者の既定：既存カメラ・控えめな演出・LoLゲーム音のみ',16,a.p['muted'])
 pairs=[('出力対象','12:34 ダブルキル / 18:11 集団戦'),('動画設定','1920×1080 / 60fps / MP4'),('カメラ','選択済みのモードを使用（TargetLock保持）'),('音声','LoLゲーム音のみ / BGMなし'),('保存先','ユーザーが選んだ出力フォルダー')]
 for i,(k,v) in enumerate(pairs):
  yy=y+169+i*66;a.text(x+28,yy,k,15,a.p['muted']);a.text(x+176,yy,v,16,maxw=w-205);a.line([(x+24,yy+47),(x+w-24,yy+47)])
 a.rect((x+24,y+533,x+w-24,y+615),a.p['selected'],7,a.p['line']);a.text(x+40,y+548,'準備状態：LoLへの接続確認が必要です',17,a.p['accent'],True);a.text(x+40,y+579,'未接続では実際の録画・動画作成を開始しない',14,a.p['muted']);a.button('export-back',(x+24,bottom-68,x+237,bottom-22),'編集へ戻る');a.button('export-prepare',(x+249,bottom-68,x+w-24,bottom-22),'接続・準備を確認',primary=True)

if __name__=='__main__':
 configs=[('C3P_main_light',dict()),('C3P_detail_light',dict(mode='studio')),('C3P_camera_drawer',dict(overlay='camera')),('C3P_main_dark',dict(dark=True)),('C3P_main_1366x768',dict(w=1366,h=768)),('C3S_main_light',dict(variant='S')),('C3S_easy_light',dict(variant='S',mode='easy')),('C3S_curve_light',dict(variant='S',mode='curve')),('C3S_asset_drawer',dict(variant='S',overlay='asset')),('C3S_export_review',dict(variant='S',overlay='export')),('C3S_main_dark',dict(variant='S',dark=True)),('C3S_main_1366x768',dict(variant='S',w=1366,h=768))]
 rows=[make(n,**cfg) for n,cfg in configs];(O/'specs/SCREEN_LAYOUTS.json').write_text(json.dumps({'screens':rows,'not_interactive':True,'originals_unchanged':True},ensure_ascii=False,indent=2),'utf8');print('static designs',len(rows))
