from pathlib import Path
import json,ast,math,subprocess
from types import SimpleNamespace
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_research_v4_20261025';O=R/'outputs/autocine_research_v4_20261025';V3=R/'outputs/autocine_final_research_v3_20261024';OLD=R/'work/autocine_integrated_research_20261022';S=OLD/'source_readonly/LoL_AutoCine/core'
FF='C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb/work/runtime-bin/ffmpeg.exe'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(name,data):
 p=O/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
def extract(file,names,scope=None):
 scope={} if scope is None else scope
 for fn in ast.parse((S/file).read_text('utf-8-sig')).body:
  if isinstance(fn,(ast.FunctionDef,ast.ClassDef)) and fn.name in names:
   if isinstance(fn,ast.FunctionDef):fn.decorator_list=[]
   exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),scope)
 return scope
def ff(args,timeout=120):return subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],capture_output=True,timeout=timeout)
MOTIONS=['instant','slide_left','slide_right','slide_up','slide_down','pop']
