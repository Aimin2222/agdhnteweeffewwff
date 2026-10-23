from pathlib import Path
import ast,json,math,subprocess,hashlib,numpy as np
from types import SimpleNamespace
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_integrated_research_20261022';O=R/'outputs/autocine_final_research_v3_20261024';O.mkdir(exist_ok=True)
FF='${FFMPEG_EXE}'
S=W/'source_readonly/LoL_AutoCine/core'
scope={'math':math,'Template':object}
def extract(path,names):
    for fn in ast.parse(path.read_text('utf-8-sig')).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path.name),'exec'),scope)
scope['MOTION_STYLES']={x:x for x in ['instant','slide_left','slide_right','slide_up','slide_down','pop']}
extract(S/'kill_icons.py',{'normalize_motion','badge_motion_xy','badge_plan'})
extract(S/'effects.py',{'_enable_expr','_build_video_effect_filters'})
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',17)
def ff(args):
    p=subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],capture_output=True)
    return p
res={'scope':'Isolated AST functions from immutable source and artificial input; no product imports/edits, no LoL, no GPU runtime.', 'source_commit':'fb03e0390805125fc063f4599af6c2541a653abf','ffmpeg_version':subprocess.run([FF,'-version'],capture_output=True,text=True).stdout.splitlines()[0],'cases':[]}
events=[(.5,.5),(1.5,1.5),(2.5,2.5)]
filters=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':.7}),3,events,False)
p=ff(['-f','lavfi','-i','color=c=gray:s=320x180:r=60:d=3','-vf',','.join(filters)+',format=gray','-f','rawvideo','-pix_fmt','gray','pipe:1'])
assert p.returncode==0,p.stderr.decode(errors='replace')
a=np.frombuffer(p.stdout,np.uint8).reshape(-1,180,320);means=a.mean(axis=(1,2))
peaks=[{'event_seconds':t,'frame':int(t*60),'mean_gray_at_event':float(means[int(t*60)]),'local_peak':float(max(means[max(0,int(t*60)-2):int(t*60)+4]))} for t,_ in events]
res['cases'].append({'id':'FX-FLASH-MULTI','execution':'EXECUTED','result':'REPRODUCED_ISOLATED_FIRST_EVENT_ONLY','graph':filters,'peaks':peaks,'note':'Enable covers all three events, brightness envelope centers only events[0][0]. End-to-end application impact still requires current-branch/live test.'})
sheet=Image.new('RGB',(960,240),'#e1e8ef');d=ImageDraw.Draw(sheet)
for i,(t,_) in enumerate(events):
    sheet.paste(Image.fromarray(a[int(t*60)]).convert('RGB'),(i*320,45));d.text((i*320+10,8),f'{t:.1f}s mean={means[int(t*60)]:.1f}',font=font,fill='black')
sheet.save(O/'FLASH_MULTI_EVENT_PROOF.png')
try:scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':.7}),3,[],False);empty='NO_EXCEPTION'
except Exception as e:empty=type(e).__name__
res['cases'].append({'id':'FX-FLASH-EMPTY','execution':'EXECUTED','result':empty,'note':'Isolated helper only. Caller event generation and product exposure need confirmation.'})
for name,k in [('radial_blur',.4),('radial_blur',.8),('zoom_blur',.4),('glint',.5),('panel_wipe',.5),('stretch_wipe',.5)]:
    fs=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={name:k}),1,events,False)
    p=ff(['-f','lavfi','-i','testsrc2=s=320x180:r=60:d=1','-vf',','.join(fs),'-frames:v','12','-f','null','-'])
    res['cases'].append({'id':f'FX-{name}-{k}','execution':'EXECUTED','result':'GRAPH_EXECUTES' if p.returncode==0 else 'GRAPH_FAILED','return_code':p.returncode,'graph':fs,'stderr':p.stderr.decode(errors='replace')[-1500:],'note':'Graph execution is not perceptual equivalence to reference videos or GPU.'})
# Motion samples model source expressions analytically. Badge PNG is representative, not per-asset product assembly.
qa=json.loads((R/'outputs/autocine_integrated_research_v2_20261022/ASSET_FULL_QA_V2.json').read_text('utf-8'))
representative=next(x for x in qa['items'] if x['id']=='083/a_simple_main')
badge=Image.open(W/'asset_samples'/representative['path']).convert('RGBA');badge.thumbnail((480,160))
def offset(m,t,w,h):
    u=max(0,min(1,1-t/.260));ease=u*u*(3-2*u)
    return {'instant':(0,0),'slide_left':(-(w+20)*ease,0),'slide_right':((w+20)*ease,0),'slide_up':(0,(h+20)*ease),'slide_down':(0,-(h+20)*ease),'pop':(16*math.exp(-18*max(0,t))*math.cos(28*max(0,t)),0)}[m]
motionrows=[]
for m in scope['MOTION_STYLES']:
    canvas=Image.new('RGB',(1440,620),(224,231,240));draw=ImageDraw.Draw(canvas)
    for i,t in enumerate([0,.05,.1,.15,.2,.26,.4,1.0]):
        cell=Image.new('RGBA',(360,260),(25,34,44,255));bd=badge.copy();bd.thumbnail((260,87));bx=360-bd.width-20;by=35
        dx,dy=offset(m,t,360,260);cell.alpha_composite(bd,(round(bx+dx),round(by+dy)))
        dd=ImageDraw.Draw(cell);dd.rectangle((0,220,359,259),fill=(70,85,105));dd.text((6,225),'SYNTHETIC HUD',font=font,fill='white')
        x=i%4*360;y=i//4*310;canvas.paste(cell.convert('RGB'),(x,y+30));draw.text((x+5,y+3),m+f'  t={t:.3f}',font=font,fill='black')
    canvas.save(O/f'MOTION_{m}_SEQUENCE.jpg',quality=92)
    samples=[]
    for w,h in [(1920,1080),(1366,768),(1280,720)]:
        samples.append({'output':[w,h],'offset_at_0':offset(m,0,w,h),'offset_at_260ms':offset(m,.26,w,h),'offset_at_1s':offset(m,1,w,h)})
    motionrows.append({'motion':m,'numeric_samples':samples,'source_ffmpeg_expression':scope['badge_motion_xy']('right-top',m,0,'W-w-32','62'), 'alpha_animation':False,'exit_animation_in_helper':False,'scope':'Analytic source-equation reconstruction, representative PNG; not final product video per 687 assets.'})
    # FFmpeg executes exact source expression with a synthetic color rectangle at 1080p60.
    x,y=scope['badge_motion_xy']('right-top',m,.4,'W-w-32','62')
    graph=f"[0:v][1:v]overlay=x='{x}':y='{y}':enable='between(t,0.4,1.8)'[v]"
    p=ff(['-f','lavfi','-i','color=c=0x233544:s=1920x1080:r=60:d=2.2','-f','lavfi','-i','color=c=0x3090e0:s=480x160:r=60:d=2.2','-filter_complex',graph,'-map','[v]','-an','-c:v','libx264','-preset','ultrafast','-crf','25','-pix_fmt','yuv420p',str(O/f'MOTION_{m}_SYNTHETIC_1080p60.mp4')])
    res['cases'].append({'id':'MOTION-'+m,'execution':'EXECUTED','result':'VIDEO_RENDERED' if not p.returncode else 'RENDER_FAILED','graph':graph,'stderr':p.stderr.decode(errors='replace')[-1000:]})
planned=scope['badge_plan']([('synthetic',t) for t in [.5,.6,.7,.8,1.0]],3,1.55)
res['badge_plan_overlap']=planned
res['badge_plan_max_active']=int(max(sum(x['start']<=t<x['end'] for x in planned) for t in np.arange(0,3,.001)))
assert res['badge_plan_max_active']<=3
(O/'SYNTHETIC_EXECUTION_V3.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),'utf-8')
(O/'MOTION_NUMERIC_REVIEW_V3.json').write_text(json.dumps(motionrows,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'cases':len(res['cases']),'flash':peaks,'empty_event_result':empty,'max_badges':res['badge_plan_max_active']}))
