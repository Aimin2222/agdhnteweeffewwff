from lab_common import *
import numpy as np,hashlib,itertools,io,sys
from PIL import Image,ImageDraw,ImageFont
scope=extract('effects.py',{'_enable_expr','_build_video_effect_filters'},{'math':math,'Template':object});rows=[];font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',15)
sets=[('single',[1.]),('two_short',[.5,.6]),('two_long',[.3,2.2]),('three',[.3,1.4,2.7]),('dense',[.5,.55,.6,.65]),('edges',[0.,1.5,2.95]),('empty',[]),('retimed',[.4,1.6,2.4])]
def fixed_graph(events,k,d=3):
 if not events:return []
 amp=.25+.55*k;terms=[f'({amp:.6f}*exp(-18*abs(t-{t:.6f})))' for t in events]
 body=terms[0]
 for term in terms[1:]:body=f'max({body},{term})'
 enable='+'.join(f'between(t,{t:.6f},{min(d,t+.15):.6f})' for t in events)
 return [f"eq=brightness='{body}':eval=frame:enable='{enable}'"]
for label,ev in ([] if '--fx-only' in sys.argv else sets):
 for k in [.15,.45,.9]:
  for revision in ['legacy_v1','candidate_max_v2']:
   try:
    graph=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':k}),3,[(x,x) for x in ev],False) if revision=='legacy_v1' else fixed_graph(ev,k)
    p=ff(['-f','lavfi','-i','color=c=gray:s=320x180:r=60:d=3','-vf',','.join(graph+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1'])
    arr=np.frombuffer(p.stdout,np.uint8).reshape(-1,180,320) if not p.returncode else np.empty((0,180,320));means=arr.mean((1,2)) if len(arr) else []
    measurements=[{'event':t,'frame':min(len(means)-1,round(t*60)),'gray':float(means[min(len(means)-1,round(t*60))])} for t in ev] if len(means) else []
    result={'case':label,'strength':k,'revision':revision,'events':ev,'graph':graph,'return_code':p.returncode,'decoded_frames':len(arr),'measurements':measurements,'stderr':p.stderr.decode(errors='replace'),'scope':'isolated research FFmpeg; candidate not applied to product'}
    if label in ['three','dense'] and k==.45:
     sheet=Image.new('RGB',(320*len(ev),210),'#e8edf4');d=ImageDraw.Draw(sheet)
     for j,m in enumerate(measurements):sheet.paste(Image.fromarray(arr[m['frame']]).convert('RGB'),(320*j,30));d.text((320*j+4,3),f"{m['event']}s mean {m['gray']:.1f}",font=font,fill='black')
     sheet.save(O/f'FLASH_{label}_{revision}.jpg',quality=91)
    if label=='three' and k==.45:
     out=O/f'FLASH_{revision}_COMPARISON.mp4';v=ff(['-f','lavfi','-i','color=c=gray:s=640x360:r=60:d=3','-vf',','.join(graph),'-c:v','libx264','-preset','ultrafast','-crf','23',str(out)]);result['comparison_video_rc']=v.returncode
   except Exception as e:result={'case':label,'strength':k,'revision':revision,'events':ev,'result':'EXCEPTION','exception':type(e).__name__,'message':str(e),'scope':'isolated helper; normal caller reachability separate'}
   rows.append(result)
if rows:save('FLASH_REVISION_RESULTS_V4.json',{'cases':rows,'executed':len(rows),'candidate_status':'research only, never changes existing ID/template/production graph','revision_policy':'absent revision retains legacy; candidate applies only after explicit product decision'})
print('flash cases',len(rows),flush=True)
fxrows=[]
for name in ['radial_blur','zoom_blur','glint','panel_wipe','stretch_wipe','focus_blur','vr_blur','sphere_blur','chroma_leak','flash']:
 for w,h in [(1920,1080),(1366,768),(1280,720)]:
  graph=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={name:.5}),1,[(.3,.3),(.7,.7)],False)
  p=ff(['-f','lavfi','-i',f'testsrc2=s={w}x{h}:r=30:d=1','-vf',','.join(graph),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
  dims=None
  if p.returncode==0:
   im=Image.open(io.BytesIO(p.stdout));dims=list(im.size)
   if w==1920:im.thumbnail((960,540));im.save(O/f'FX_{name}_FIRST_FRAME.jpg',quality=91)
  record={'fx':name,'strength':.5,'input_size':[w,h],'filter_output_size':dims,'graph':graph,'first_frame_return_code':p.returncode,'stderr':p.stderr.decode(errors='replace')[-1800:],'size_preserved':dims==[w,h]}
  # Test 18-frame actual output; diagnostics scale happens AFTER original graph and is declared.
  args=['-f','lavfi','-i',f'testsrc2=s={w}x{h}:r=30:d=0.6','-vf',','.join(graph+['scale=640:360']),'-frames:v','18']
  out=O/f'FX_{name}_ARTIFICIAL.mp4' if w==1920 else None
  r=ff(args+(['-c:v','libx264','-preset','ultrafast','-crf','23',str(out)] if out else ['-f','null','-']))
  record.update(video_or_null_rc=r.returncode,diagnostic_output_resize=[640,360],stderr_temporal=r.stderr.decode(errors='replace')[-1800:]);fxrows.append(record)
 print('FX',name,'done',flush=True)
save('EXISTING_FX_EXECUTION_V4.json',{'cases':fxrows,'executed':len(fxrows),'not_product_pass':True,'preview_mode_not_compared':True})
