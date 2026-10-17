"""Inspect rendered native VFX PNGs without modifying any media.
Usage: qa_motion_native.py CATALOG_JSON LABEL
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,re,sys
import numpy as np
ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(a):
 entry=next(x for x in a['outputs'] if x['file'].endswith('/impact_2048_rgba.png'))
 p=Path(entry['file']);assert sha(p)==entry['sha256']
 with Image.open(p) as im:
  assert im.mode=='RGBA' and list(im.size)==[2048,1152]
  alpha=np.asarray(im.getchannel('A'))
 edge=np.r_[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]
 assert (alpha==0).any() and (alpha>0).any()
 return dict(key=a['key'],file=entry['file'],sha256=entry['sha256'],mode='RGBA',
  dimensions=[2048,1152],edge_nonzero=int((edge>0).sum()),
  edge_max_alpha=int(edge.max()),transparent_pixels=int((alpha==0).sum()),
  final_approved=False)
def main(path,label):
 assert re.fullmatch('[a-z0-9_-]+',label)
 source=Path(path);data=source.read_bytes();catalog=json.loads(data)
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,catalog['assets']))
 result=dict(count=len(rows),catalog=source.as_posix(),
  catalog_snapshot_sha256=hashlib.sha256(data).hexdigest(),
  checked_utc=datetime.now(timezone.utc).isoformat(),scope='native_vfx_png_technical_only',
  all_rgba_2048=True,edge_warning_count=sum(x['edge_nonzero']>0 for x in rows),
  final_approved=0,assets=rows)
 out=ROOT/'qa'/('motion_native_'+label+'.json');assert not out.exists()
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='assets'}))
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
