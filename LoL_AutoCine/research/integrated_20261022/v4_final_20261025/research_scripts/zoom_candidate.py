from lab_common import *
from PIL import Image,ImageDraw
import numpy as np
scope=extract('effects.py',{'_enable_expr','_build_video_effect_filters'},{'math':math,'Template':object});rows=[]
for k in [.15,.5,.9]:
 base=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'zoom_blur':k}),1.2,[(.3,.3)],False)[0]
 for rev,graph in [('legacy_scale4',base),('candidate_auto_normalize',base.replace(':scale=4',':scale=0')),('candidate_quarter',base.replace(':scale=4',':scale=0.25'))]:
  r=ff(['-f','lavfi','-i','testsrc2=s=1920x1080:r=30:d=1.2','-vf',graph+',scale=320:180','-frames:v','36','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);a=np.frombuffer(r.stdout,np.uint8).reshape(-1,180,320,3)
  rows.append({'strength':k,'revision':rev,'graph':graph,'rc':r.returncode,'frames':len(a),'spatial_std_mean':float(np.mean([z.std(axis=(0,1)).mean() for z in a])),'mean_rgb':a.mean(axis=(0,1,2)).tolist(),'not_product_revision':True})
  if k==.5:
   sheet=Image.new('RGB',(1280,204),'#e8edf4');d=ImageDraw.Draw(sheet)
   for i,n in enumerate([0,9,21,35]):sheet.paste(Image.fromarray(a[n]),(i*320,24));d.text((i*320+4,3),rev+f' frame{n}',fill='black')
   sheet.save(O/f'ZOOM_{rev}.jpg',quality=94)
save('ZOOM_CANDIDATE_RESULTS_V4.json',{'cases':rows,'status':'isolated saturation reproduced; two research normalization candidates, existing project must keep old revision','documentation':'https://ffmpeg.org/ffmpeg-filters.html#tmix','actual_LoL':'NOT_RUN'})
