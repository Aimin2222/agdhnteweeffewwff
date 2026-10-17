"""Adopt exact alpha-one cleanup after generation jobs have stopped.
Preserves raw PNGs and history; requires fresh original comparison after adoption.
Usage: adopt_micro_alpha.py CLEANUP_MANIFEST --generation-idle
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, msvcrt, sys
import numpy as np
from PIL import Image
from frame_runner import OUT, load, write

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def adopt(manifest_path):
 manifest_path=Path(manifest_path)
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 auth_path=OUT/'qa/alpha_cleanup_authorization_20261017.json'
 auth=json.loads(auth_path.read_text(encoding='utf-8'))
 assert auth['authorized'] and auth['threshold_rule']=='alpha == 1 -> 0'
 assert manifest['count']==652 and manifest['rgb_and_other_alpha_preserved_all']
 assert manifest['raw_inputs_unchanged_all']
 records={r['key']:r for r in manifest['assets']}
 assert len(records)==652
 with (OUT/'production.lock').open('a+b') as lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
  try:
   plan=load();assert len(plan['assets'])==652
   verified=[]
   for asset in plan['assets']:
    record=records[asset['key']]
    source=Path(record['input_file']);target=Path(record['output_file'])
    assert asset['output']==source.as_posix(),'Stale manifest path'
    assert asset['sha256']==record['input_sha256']==sha(source),'Stale raw SHA'
    assert sha(target)==record['output_sha256']
    with Image.open(source) as im:
     assert im.mode=='RGBA'
     before=np.array(im);size=list(im.size)
    with Image.open(target) as im:
     assert im.mode=='RGBA' and list(im.size)==size
     after=np.array(im)
    assert size==record['dimensions'] and max(size)>=2048
    expected=before.copy()
    expected[:,:,3][expected[:,:,3]==1]=0
    assert np.array_equal(expected,after),'Unauthorized pixel change'
    assert int((before[:,:,3]==1).sum())==record['alpha1_pixels_removed']
    verified.append((asset,record))
   changed=0
   for asset,record in verified:
    if record['input_file']==record['output_file']:continue
    old={k:v for k,v in asset.items() if k not in ['candidate_history','original_reference']}
    asset.setdefault('candidate_history',[]).append(old)
    asset.update(output=record['output_file'],sha256=record['output_sha256'],bytes=record['bytes'],
     dimensions=record['dimensions'],mode='RGBA',alpha_zero_pixels=record['alpha_zero_pixels_after'],
     edge_alpha_nonzero=record['outer_border_nonzero_after'],
     visual_review='pending_comparison_after_authorized_alpha_cleanup',
     effect_status='pending_after_frame',final_approved=False)
    asset['processing_provenance']=dict(
     method='alpha == 1 -> 0; all RGB and other alpha unchanged',
     raw_generated_file=record['input_file'],raw_generated_sha256=record['input_sha256'],
     authorization=auth_path.as_posix(),manifest=manifest_path.as_posix(),
     manifest_sha256=sha(manifest_path),rgb_exactly_preserved=True,
     alpha_0_and_2_to_255_exactly_preserved=True,alpha1_pixels_removed=record['alpha1_pixels_removed'],
     final_approved=False)
    flags=[v for v in asset.get('quality_flags',[]) if v!='outer_edge_alpha_residue']
    if record['outer_border_nonzero_after']:flags.append('outer_edge_alpha_residue')
    asset['quality_flags']=flags
    asset.pop('reused_exact_part',None);asset.pop('original_reference',None)
    changed+=1
   plan['last_updated_utc']=datetime.now(timezone.utc).isoformat()
   plan['alpha_cleanup_adoption']=dict(manifest=manifest_path.as_posix(),
    manifest_sha256=sha(manifest_path),count=changed,final_approved=0,
    status='review_required_after_alpha1_only_cleanup')
   write(plan)
   print(json.dumps(dict(adopted=changed,final_approved=0,
    outer_border_issues_after=manifest['outer_border_issues_after'])))
  finally:
   lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

if __name__=='__main__':
 assert len(sys.argv)==3 and sys.argv[2]=='--generation-idle','Finish generation jobs before adoption'
 adopt(sys.argv[1])
