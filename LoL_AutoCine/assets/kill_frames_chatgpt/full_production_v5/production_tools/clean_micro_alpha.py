"""User-authorized derivative: set alpha==1 to zero, preserving RGB and all other alpha.

Builds separate PNGs only. Never overwrites art or adopts outputs into production.json.
Usage from repository root: clean_micro_alpha.py SNAPSHOT_JSON
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from PIL import Image
import numpy as np
import hashlib,json,sys

ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
OUT=ROOT/'alpha_cleanup_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def edge(a):return np.r_[a[0],a[-1],a[:,0],a[:,-1]]

def build_one(a):
 source=Path(a['output']);expected=a['sha256'];assert sha(source)==expected
 with Image.open(source) as im:
  assert im.mode=='RGBA' and max(im.size)>=2048
  before=np.array(im);size=list(im.size);info=dict(im.info);original=im.copy()
 alpha=before[:,:,3];mask=alpha==1;n=int(mask.sum())
 target=source
 if n:
  target=OUT/'frames'/a['number']/(a['id']+'.from_'+expected[:16]+'.alpha0.png')
  target.parent.mkdir(parents=True,exist_ok=True)
  after_alpha=alpha.copy();after_alpha[mask]=0
  if not target.exists():
   original.putalpha(Image.fromarray(after_alpha))
   options={k:info[k] for k in ['icc_profile','exif','dpi'] if k in info}
   temporary=target.with_suffix('.writing.png');original.save(temporary,format='PNG',compress_level=6,**options)
   with Image.open(temporary) as im:check=np.array(im)
   assert np.array_equal(check[:,:,:3],before[:,:,:3])
   assert np.array_equal(check[:,:,3],after_alpha)
   temporary.replace(target)
 with Image.open(target) as im:
  assert im.mode=='RGBA' and list(im.size)==size
  after=np.array(im)
 assert np.array_equal(after[:,:,:3],before[:,:,:3]),'RGB changed'
 assert np.array_equal(after[:,:,3][~mask],alpha[~mask]),'Alpha other than one changed'
 assert (after[:,:,3][mask]==0).all() and not (after[:,:,3]==1).any()
 assert int((alpha!=after[:,:,3]).sum())==n
 assert sha(source)==expected,'Input raw PNG changed'
 eb=edge(alpha);ea=edge(after[:,:,3])
 return dict(key=a['key'],input_file=source.as_posix(),input_sha256=expected,output_file=target.as_posix(),output_sha256=sha(target),bytes=target.stat().st_size,dimensions=size,mode='RGBA',alpha1_pixels_removed=n,rgb_exactly_preserved=True,alpha_0_and_2_to_255_exactly_preserved=True,raw_input_unchanged=True,outer_border_nonzero_before=int((eb>0).sum()),outer_border_max_alpha_before=int(eb.max()),outer_border_nonzero_after=int((ea>0).sum()),outer_border_max_alpha_after=int(ea.max()),alpha_zero_pixels_after=int((after[:,:,3]==0).sum()),source_partial=a['source_partial'],palette_reference=a['palette_reference'],final_approved=False)

def main(snapshot):
 authorization=ROOT/'qa/alpha_cleanup_authorization_20261017.json';assert authorization.is_file(),'Explicit user authorization record is required'
 auth=json.loads(authorization.read_text(encoding='utf-8'));assert auth['authorized'] and auth['threshold_rule']=='alpha == 1 -> 0'
 plan=json.loads(Path(snapshot).read_text(encoding='utf-8'));assert len(plan['assets'])==652 and all(a['status']!='pending' for a in plan['assets'])
 OUT.mkdir(exist_ok=True);records=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for f in as_completed([pool.submit(build_one,a) for a in plan['assets']]):
   records.append(f.result())
   if len(records)%100==0:print('alpha-only derivative verified: '+str(len(records)),flush=True)
 records.sort(key=lambda a:a['key'])
 result=dict(status='authorized_alpha1_only_derivatives_review_not_final',input_snapshot=Path(snapshot).as_posix(),input_snapshot_sha256=sha(Path(snapshot)),authorization=authorization.as_posix(),count=len(records),created_utc=datetime.now(timezone.utc).isoformat(),rgb_and_other_alpha_preserved_all=True,raw_inputs_unchanged_all=True,with_alpha1_removed=sum(a['alpha1_pixels_removed']>0 for a in records),outer_border_issues_after=sum(a['outer_border_nonzero_after']>0 for a in records),final_approved=0,assets=records)
 folder=OUT/'checkpoints';folder.mkdir(exist_ok=True);dest=folder/('cleanup_'+Path(snapshot).stem+'.json')
 assert not dest.exists(),'Preserve published cleanup snapshots'
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(manifest=dest.as_posix(),**{k:v for k,v in result.items() if k not in ['assets','input_snapshot','authorization']})))

if __name__=='__main__':main(sys.argv[1])
