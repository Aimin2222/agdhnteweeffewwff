from lab_common import *
from PIL import Image,ImageDraw
import numpy as np,itertools
scope=extract('effects.py',{'_enable_expr','_build_video_effect_filters'},{'math':math,'Template':object})
names=['radial_blur','zoom_blur','glint','panel_wipe','stretch_wipe','focus_blur','vr_blur','sphere_blur','chroma_leak','flash'];rows=[]
for name,k,(w,h) in itertools.product(names,[.15,.5,.9],[(1920,1080),(1366,768),(1280,720)]):
 graph=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={name:k}),1.2,[(.3,.3),(.7,.7)],False)
 args=['-f','lavfi','-i',f'testsrc2=s={w}x{h}:r=30:d=1.2','-vf',','.join(graph+['scale=320:180']),'-frames:v','36','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 r=ff(args);arr=np.frombuffer(r.stdout,np.uint8).reshape(-1,180,320,3) if r.returncode==0 else []
 record={'fx':name,'strength':k,'size':[w,h],'graph':graph,'rc':r.returncode,'decoded_frames':len(arr),'expected_frames':36,'means':[float(x.mean()) for x in arr],'stderr':r.stderr.decode(errors='replace'),'scope':'isolated original CPU graph; output then resized320x180 for diagnostic'};rows.append(record)
 if w==1920 and k==.5 and len(arr):
  nums=[0,8,9,10,20,21,22,35];sheet=Image.new('RGB',(1280,408),'#e8edf4');d=ImageDraw.Draw(sheet)
  for i,n in enumerate(nums):
   n=min(n,len(arr)-1);x=i%4*320;y=i//4*204;sheet.paste(Image.fromarray(arr[n]),(x,y+24));d.text((x+3,y+3),f'{name} t={n/30:.3f}',fill='black')
  sheet.save(O/f'FX_{name}_EXPANDED.jpg',quality=94)
 save('EXISTING_FX_EXPANDED_V4.json',{'cases':rows,'planned':90,'scope':'real frame processing, no product/LoL PASS; old IDs unchanged'})
 print(name,k,w,len(arr),flush=True)
# Isolate the pink temporal output seen in original zoom graph, without changing product.
base=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'zoom_blur':.5}),1.2,[(.3,.3)],False)[0]
tests={'original':base,'without_tmix':base.split(',tmix=')[0],'tmix_only':"tmix=frames=3:weights='1 2 1':scale=4",'constant_scale':"scale=1920:1080,crop=1920:1080:x='(iw-ow)/2':y='(ih-oh)/2',tmix=frames=3:weights='1 2 1':scale=4"}
isolation=[]
for tag,graph in tests.items():
 r=ff(['-f','lavfi','-i','testsrc2=s=1920x1080:r=30:d=1.2','-vf',graph+',scale=320:180','-frames:v','36','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);a=np.frombuffer(r.stdout,np.uint8).reshape(-1,180,320,3)
 isolation.append({'variant':tag,'graph':graph,'rc':r.returncode,'frames':len(a),'spatial_std_per_frame':[float(z.std(axis=(0,1)).mean()) for z in a],'mean_rgb_per_frame':[z.mean(axis=(0,1)).tolist() for z in a]})
save('ZOOM_TEMPORAL_ISOLATION_V4.json',{'cases':isolation,'not_applied_to_product':True})
