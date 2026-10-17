"""User-authorized margin cleanup: only isolated alpha 2..3 dots.
Preserve RGB, dimensions, alpha>=4 and the artwork and glow edges within a 24px radius.
Usage: clean_margin_dots.py ALPHA1_CLEANUP_MANIFEST
"""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image
import json,hashlib,sys
import numpy as np,cv2
ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
OUT=ROOT/'alpha_cleanup_v3_margin_distance'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def edges(a):return np.r_[a[0],a[-1],a[:,0],a[:,-1]]
def selection(alpha):
 assert (alpha>=4).any(),'No visible artwork'
 distance=cv2.distanceTransform((alpha<4).astype('uint8'),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
 protected=distance<=24
 weak=((alpha>=2)&(alpha<=3)).astype('uint8')
 n,labels,stats,_=cv2.connectedComponentsWithStats(weak,connectivity=8)
 inside=np.bincount(labels[protected],minlength=n)>0
 eligible=(stats[:,cv2.CC_STAT_AREA]<=64)&(stats[:,cv2.CC_STAT_WIDTH]<=8)&(stats[:,cv2.CC_STAT_HEIGHT]<=8)&(~inside)
 eligible[0]=False
 return eligible[labels],protected,int(eligible.sum())
def build_one(r):
 source=Path(r['output_file']);raw=Path(r['input_file'])
 assert sha(raw)==r['input_sha256']
 assert sha(source)==r['output_sha256']
 with Image.open(source) as im:
  assert im.mode=='RGBA' and max(im.size)>=2048
  before=np.array(im);info=dict(im.info);original=im.copy();size=list(im.size)
 alpha=before[:,:,3];assert not (alpha==1).any()
 selected,protected,components=selection(alpha);count=int(selected.sum())
 target=source
 if count:
  target=OUT/'frames'/r['key'].split('/')[0]/(r['key'].split('/')[1]+'.from_'+r['output_sha256'][:16]+'.margin23.png')
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():
   after_alpha=alpha.copy();after_alpha[selected]=0
   original.putalpha(Image.fromarray(after_alpha))
   options={k:info[k] for k in ['icc_profile','exif','dpi'] if k in info}
   temporary=target.with_suffix('.writing.png')
   original.save(temporary,format='PNG',compress_level=6,**options)
   temporary.replace(target)
 with Image.open(target) as im:
  assert im.mode=='RGBA' and list(im.size)==size
  after=np.array(im)
  for key in ['icc_profile','gamma','srgb','chromaticity']:
   assert im.info.get(key)==info.get(key),'Color metadata changed'
 expected=before.copy();expected[:,:,3][selected]=0
 assert np.array_equal(after,expected),'Changes exceeded permitted dots'
 assert sha(source)==r['output_sha256'],'Alpha1-only input changed'
 assert sha(raw)==r['input_sha256'],'Generated raw input changed'
 assert np.array_equal(after[protected],before[protected])
 assert np.array_equal(after[:,:,3][alpha>=4],alpha[alpha>=4])
 ea=edges(after[:,:,3])
 return dict(key=r['key'],input_file=source.as_posix(),input_sha256=r['output_sha256'],
  raw_generated_file=r['input_file'],raw_generated_sha256=r['input_sha256'],
  output_file=target.as_posix(),output_sha256=sha(target),bytes=target.stat().st_size,
  dimensions=size,mode='RGBA',alpha2_removed=int(((alpha==2)&selected).sum()),
  alpha3_removed=int(((alpha==3)&selected).sum()),removed_pixels=count,components=components,
  protected_art_distance_px=24,protected_alpha_floor=4,protected_art_and_glow_unchanged=True,all_rgb_unchanged=True,
  all_nonselected_alpha_unchanged=True,alpha1_input_unchanged=True,raw_generated_input_unchanged=True,
  edge_nonzero_after=int((ea>0).sum()),edge_max_alpha_after=int(ea.max()),
  source_partial=r['source_partial'],palette_reference=r['palette_reference'],final_approved=False)
def main(path):
 auth_path=ROOT/'qa/margin_dot_distance_rule_authorization_20261017.json'
 auth=json.loads(auth_path.read_text(encoding='utf-8-sig'))
 assert auth['authorized'] and auth['alpha_values']==[2,3]
 assert auth['max_component_box']==[8,8]
 assert auth['padding_px']==24 and auth['max_component_pixels']==64 and auth['connectivity']==8
 source_manifest=Path(path);data=source_manifest.read_bytes();plan=json.loads(data)
 assert plan['count']==652 and plan['rgb_and_other_alpha_preserved_all']
 dest=OUT/'checkpoints'/('margin_distance_'+source_manifest.name)
 assert not dest.exists(),'Preserve published manifests; use a new input snapshot'
 dest.parent.mkdir(parents=True,exist_ok=True)
 rows=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(build_one,r) for r in plan['assets']]
  for f in as_completed(futures):
   rows.append(f.result())
   if len(rows)%100==0:print('Margin dot derivative verified: '+str(len(rows)),flush=True)
 result=dict(status='authorized_margin_distance_dot_derivatives_review_not_final',
  input_manifest=source_manifest.as_posix(),input_manifest_sha256=hashlib.sha256(data).hexdigest(),
  authorization=auth_path.as_posix(),authorization_sha256=sha(auth_path),
  count=len(rows),created_utc=datetime.now(timezone.utc).isoformat(),
  modified_files=sum(r['removed_pixels']>0 for r in rows),
  removed_pixels=sum(r['removed_pixels'] for r in rows),
  edge_issues_after=sum(r['edge_nonzero_after']>0 for r in rows),
  all_rgb_and_protected_art_unchanged=True,all_nonselected_alpha_unchanged=True,
  all_alpha1_inputs_preserved=True,final_approved=0,assets=sorted(rows,key=lambda a:a['key']))
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='assets'}))
if __name__=='__main__':main(sys.argv[1])
