from lab_common import *
from PIL import Image,ImageDraw
import numpy as np
old=load(O/'FLASH_REVISION_RESULTS_V4.json')['cases'];new=load(O/'FLASH_COMPAT_REVISION_V4.json')['cases'];rows=[]
for strength in [.15,.45]:
 graphs=[next(x['graph'] for x in old if x['case']=='three' and x['strength']==strength and x['revision']==rev) for rev in ['legacy_v1','candidate_max_v2']]+[next(x['graph'] for x in new if x['case']=='three' and x['strength']==strength)]
 sheet=Image.new('RGB',(1280,3*120),'#e8edf4');d=ImageDraw.Draw(sheet)
 for i,(rev,g) in enumerate(zip(['legacy_v1','rejected_v2','candidate_v3'],graphs)):
  r=ff(['-f','lavfi','-i','color=c=gray:s=160x90:r=60:d=3','-vf',','.join(g+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1']);a=np.frombuffer(r.stdout,np.uint8).reshape(-1,90,160);ts=[.3,.4,.5,1.4,1.5,2.7,2.8,2.95]
  for j,t in enumerate(ts):
   im=Image.fromarray(a[round(t*60)]).convert('RGB');sheet.paste(im,(j*160,i*120+30));d.text((j*160+3,i*120+2),f'{rev} k={strength} t={t}',fill='black');d.text((j*160+3,i*120+15),f'gray={a[round(t*60)].mean():.1f}',fill='black')
  rows.append({'strength':strength,'revision':rev,'frames':len(a),'graph':g,'gray_per_frame':a.mean((1,2)).tolist(),'scope':'same source/strength/time, uncompressed artificial comparison'})
 sheet.save(O/f'FLASH_SAME_STRENGTH_{str(strength).replace(".","p")}.jpg',quality=94)
 if strength==.15:
  graph='[0:v]split=2[a][b];[a]'+','.join(graphs[0])+'[old];[b]'+','.join(graphs[2])+'[new];[old][new]hstack=inputs=2[out]'
  r=ff(['-f','lavfi','-i','color=c=gray:s=320x180:r=60:d=3','-filter_complex',graph,'-map','[out]','-c:v','libx264','-preset','ultrafast','-crf','20',str(O/'FLASH_LEGACY_V3_SAME_STRENGTH.mp4')]);assert r.returncode==0,r.stderr
save('FLASH_SAME_STRENGTH_V4.json',{'cases':rows,'left_video':'legacy_v1','right_video':'candidate_v3','video_strength':.15,'product_changes':False})
log=load(O/'FX_FIRST_AND_TEMPORAL_VISUAL_LOG_V4.json');log['strength_clarification']='Original v3 COMPAT sheet k=.15, old/v2 three sheets k=.45; compare new SAME_STRENGTH .15/.45 sheets for true side-by-side.';save('FX_FIRST_AND_TEMPORAL_VISUAL_LOG_V4.json',log)
