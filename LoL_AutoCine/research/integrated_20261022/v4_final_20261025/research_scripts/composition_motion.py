"""Independent research renderer. Never writes source/catalog or approval state."""
from lab_common import *
import sys,hashlib,time,itertools,csv
sys.dont_write_bytecode=True
sys.path.insert(0,str(S.parent))
from PIL import Image,ImageDraw,ImageEnhance
import numpy as np
from core import work_kill_assets as k
k.ROOT=OLD/'asset_samples'
k.CATALOG=S.parent/'assets/work_kill_assets/catalog.json'
frames=k.catalog()['frames'];fx=k.catalog()['effects']
SHAPES={'round':'083/a_simple_main','square':'005/frame_02','octagon':'003/spirit_blossom_variant_1','landscape':'084/zaun_variant_1'}
ICON=[W/'official_icons'/f'{x}.png' for x in ['Yasuo','Jinx','Ahri','Zed']]
def pair(shape,effect='',power='strong',elapsed=.08,icons=(0,1)):
 t=SimpleNamespace(work_kill_frame_id=SHAPES[shape],work_kill_effect_id=effect,work_kill_review=True,work_kill_strength=power)
 layers=k._preview_layers(t,ICON[icons[0]],ICON[icons[1]],(1920,1080),1.)
 out=Image.new('RGBA',(384,layers[0][0].height))
 for im,a,d,*_ in layers:
  im=im.copy();v=a if not d else k.peak_opacity(elapsed,d)*k.strength(power)
  im.putalpha(im.getchannel('A').point(lambda p:round(p*v)));out.alpha_composite(im)
 return out
def background(size,kind='complex',phase=0):
 w,h=size;im=Image.new('RGB',size,{'light':'#e9edf2','dark':'#111923','complex':'#274235'}[kind]);d=ImageDraw.Draw(im)
 if kind=='complex':
  for z in range(25):
   x=(z*173+phase*29)%(w+160)-80;y=(z*97+phase*13)%h
   d.ellipse((x,y,x+110,y+70),fill=(25+z*7%120,45+z*13%100,30+z*19%100))
  for z in range(7):
   x=w//2+z*31-90;y=h//2+z*13-45;d.rectangle((x,y,x+42,y+6),fill='#39d85e' if z%2 else '#df3d3d');d.text((x,y-14),'NAME / HP',fill='white')
 d.rectangle((w-220,h-220,w-8,h-8),outline='#eaa629',width=3);d.text((w-212,h-211),'ARTIFICIAL MINIMAP',fill='#eaa629')
 d.rectangle((w//3,h-75,2*w//3,h-8),outline='#dce8fa',width=3);d.text((w//3+6,h-67),'ARTIFICIAL HUD',fill='#dce8fa')
 d.text((12,12),'V4 ARTIFICIAL SCENE / REAL RIOT STATIC ICONS / REVIEW GEOMETRY IS PROVISIONAL',fill='white' if kind!='light' else 'black')
 return im
def static():
 records=[];folder=O/'fx_composition';folder.mkdir(exist_ok=True)
 for n,e in enumerate(fx):
  sheet=Image.new('RGB',(1536,4*336+42),'#18202b');d=ImageDraw.Draw(sheet);d.text((12,12),f"{e['id']} | 4 shapes x weak/strong x light/dark/complex | each scene has 3 stacks | artificial, not LoL PASS",fill='white')
  for si,shape in enumerate(SHAPES):
   for pi,power in enumerate(['weak','strong']):
    for bi,bg in enumerate(['light','dark','complex']):
     scene=background((768,432),bg)
     badge=pair(shape,e['id'],power)
     for row in range(3):scene.paste(badge,(768-384-32,38+row*128),badge)
     # Full output fixture before montage resizing; save one per shape/effect/power/bg.
     arr=np.asarray(scene);white=float(np.mean(np.min(arr,axis=2)>240))
     records.append(dict(effect=e['id'],frame=SHAPES[shape],shape=shape,strength=power,background=bg,stack=3,static_executed=True,highlight_fraction=white,portrait_geometry='verified' if shape=='round' else 'provisional circular',formal_approval_changed=False,real_LoL=False))
     tile=scene.resize((256,144));x=(pi*3+bi)*256;y=42+si*336
     sheet.paste(tile,(x,y+20));d.text((x+4,y+3),f'{shape}/{power}/{bg}',fill='white')
     # Same image under a diagnostic global flash and independent grade; research combination, not app graph.
     grade=ImageEnhance.Color(scene).enhance(.75);flash=Image.blend(grade,Image.new('RGB',scene.size,'white'),.28)
     sheet.paste(flash.resize((256,144)),(x,y+176));d.text((x+4,y+163),'FLASH .28 + saturation .75',fill='white')
  sheet.save(folder/f"{n+1:02d}_{e['id']}.jpg",quality=93)
  print('fx',n+1,e['id'],flush=True)
 save('FX_COMPOSITION_MATRIX_V4.json',dict(cases=records,base_composites=len(records),flash_grade_composites=len(records),individual_visual_review='See separate visual log; generation alone is not visual approval',background='artificial; no actual LoL capture supplied',original_rendering_functions='unchanged work_kill_assets _preview_layers/render_pair/render_peak, ROOT redirected read-only cached images'))
def motion():
 folder=O/'motion';folder.mkdir(exist_ok=True);results=[]
 for shape,motion,(width,height),fps in itertools.product(SHAPES,MOTIONS,[(1920,1080),(1366,768),(1280,720)],[30,60]):
  # Render at the actual requested resolution. Same functions as mirror, manually supply event clock.
  keep=width==1920 and fps==60
  name=f'{shape}_{motion}_{width}_{fps}';path=folder/(name+'.mp4') if keep else W/'tmp'/(name+'.mp4')
  cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','ultrafast','-crf','28','-pix_fmt','yuv420p',str(path)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);N=round(2.7*fps);hashes=[];counts=[];stills=[]
  t=SimpleNamespace(work_kill_frame_id=SHAPES[shape],work_kill_effect_id='',work_kill_review=True,work_kill_strength='strong',kill_icon_position='right-top',kill_icon_scale=1.,kill_icon_duration=1.55,kill_icon_opacity=1.,kill_icon_motion=motion,kill_stack_gap=4)
  bg=background((width,height));last=None
  for j in range(N):
   now=j/fps;im=bg.copy();d=ImageDraw.Draw(im);x=int((now*200)%(width-100));d.rectangle((x,height//2,x+60,height//2+60),fill='#4d92c9')
   active=[z for z,at in enumerate([.3,.5,.7,.9]) if 0<=now-at<1.55][-3:];counts.append(len(active))
   for row,z in enumerate(active):
    overlay=k.render_preview_pair(t,ICON[z%4],ICON[(z+1)%4],now-[.3,.5,.7,.9][z],size=(width,height),row=row)
    im.paste(overlay,(0,0),overlay)
   b=im.tobytes();p.stdin.write(b)
   if j in [0,round(.35*fps),round(1.1*fps),N-1]:hashes.append(hashlib.sha256(b).hexdigest());stills.append(im.resize((640,360)))
  p.stdin.close();err=p.stderr.read().decode(errors='replace');rc=p.wait()
  decoded=ff(['-i',str(path),'-vf','scale=32:18','-f','rawvideo','-pix_fmt','rgb24','pipe:1']) if rc==0 else None
  actual=len(decoded.stdout)//(32*18*3) if decoded else 0
  result=dict(shape=shape,frame=SHAPES[shape],motion=motion,width=width,height=height,fps=fps,expected_frames=N,decoded_frames=actual,encode_rc=rc,decode_rc=decoded.returncode if decoded else None,max_stack=max(counts),snapshots_sha256=hashes,status='PASS' if rc==0 and actual==N else 'FAIL',scope='artificial mirror CPU renderer; not export/LoL/GPU parity',stderr=err,video_saved=keep)
  results.append(result)
  if keep:
   sheet=Image.new('RGB',(1280,720));[sheet.paste(im,((i%2)*640,(i//2)*360)) for i,im in enumerate(stills)];sheet.save(folder/(name+'.jpg'),quality=92)
  else:path.unlink(missing_ok=True)
  save('MOTION_RENDER_EXECUTION_V4.json',dict(cases=results,planned=144,scope='actual pixel rendering and full decoded frame counts, geometry labels provisional except083; no live LoL'))
  print('motion',len(results),name,result['status'],flush=True)
if __name__=='__main__':
 if '--motion' in sys.argv:motion()
 else:static()
