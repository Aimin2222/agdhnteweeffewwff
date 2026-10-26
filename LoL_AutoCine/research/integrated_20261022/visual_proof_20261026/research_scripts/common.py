from pathlib import Path
import json,subprocess,hashlib,math,sys,ast
from fractions import Fraction as F
from types import SimpleNamespace as NS
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent;O=R/'outputs/autocine_visual_proof_20261026';O.mkdir(exist_ok=True)
OLD=R/'work/autocine_integrated_research_20261022';S=OLD/'source_readonly/LoL_AutoCine';A=OLD/'asset_samples';V4=R/'outputs/autocine_research_v4_20261025'
FF='C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb/work/runtime-bin/ffmpeg.exe'
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(n,a):p=O/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ff(args,data=None):
 p=subprocess.run([FF,'-hide_banner','-nostdin','-loglevel','error','-y',*map(str,args)],input=data,capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
 return p.stdout
def font(n=18):
 try:return ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',n)
 except OSError:return ImageFont.load_default()
def label(im,txt,xy=(8,4),size=18,fill='#eaf2fc'):ImageDraw.Draw(im).text(xy,txt,font=font(size),fill=fill)
def encode(path,frames,fps):
 path=O/path;path.parent.mkdir(exist_ok=True,parents=True);arr=np.asarray(frames,np.uint8);h,w=arr.shape[1:3]
 ff(['-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',path],arr.tobytes())
 # Decode every frame, not just a successful encoder exit.
 b=ff(['-i',path,'-f','rawvideo','-pix_fmt','rgb24','pipe:1']);actual=len(b)//(w*h*3);assert actual==len(arr)
 return {'path':path.relative_to(O).as_posix(),'frames':actual,'fps':str(fps),'sha256':sha(path),'decode':'PASS'}
def extract_effects():
 scope={'math':math,'Template':object}
 for n in ast.parse((S/'core/effects.py').read_text('utf-8-sig')).body:
  if isinstance(n,ast.FunctionDef) and n.name in ['_enable_expr','_build_video_effect_filters']:exec(compile(ast.Module(body=[n],type_ignores=[]),'pinned_effects','exec'),scope)
 return scope
def sheet(path,images,labels,cols=3,tile=(400,225)):
 w,h=tile;out=Image.new('RGB',(w*cols,(h+34)*math.ceil(len(images)/cols)),'#172333')
 for i,(im,txt) in enumerate(zip(images,labels)):
  p=ImageOps.contain(im.convert('RGB'),tile);x=i%cols*w;y=i//cols*(h+34);out.paste(p,(x+(w-p.width)//2,y+34));label(out,txt,(x+6,y+3),16)
 p=O/path;p.parent.mkdir(parents=True,exist_ok=True);out.save(p,quality=94)
def bg(size,light=False,phase=0):
 w,h=size;im=Image.new('RGB',size,'#e5e8ec' if light else '#172936');d=ImageDraw.Draw(im)
 for i in range(8):
  x=(i*91+phase*5)%(w+50)-50;y=(i*51)%(h-25);d.rectangle((x,y,x+40,y+14),fill=(50+i*20,80+i*13,65+i*17))
 d.rectangle((w-150,h-90,w-6,h-6),outline='#c79b49',width=2);d.text((w-140,h-80),'SYNTHETIC HUD',font=font(11),fill='#a16b29' if light else '#ecce87')
 return im
