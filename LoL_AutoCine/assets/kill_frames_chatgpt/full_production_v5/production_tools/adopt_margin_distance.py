"""Adopt authorized alpha1 + isolated margin-dot derivatives after generation stops.
Preserves every previous PNG, source review and candidate history. Never approves art.
Usage: adopt_margin_distance.py MANIFEST --generation-idle
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,msvcrt,sys
import numpy as np
from PIL import Image
from frame_runner import OUT,load,write
from clean_margin_dots_distance import selection

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pixels(p):
 with Image.open(p) as im:
  assert im.mode=='RGBA' and max(im.size)>=2048
  return np.array(im),im.size,{k:im.info.get(k) for k in ['icc_profile','gamma','srgb','chromaticity']}

def main(path):
 path=Path(path);m=read(path)
 assert m['count']==652 and m['all_rgb_and_protected_art_unchanged'] and m['all_nonselected_alpha_unchanged']
 onepath=Path(m['input_manifest']);assert sha(onepath)==m['input_manifest_sha256']
 one=read(onepath);assert one['count']==652 and one['rgb_and_other_alpha_preserved_all'] and one['raw_inputs_unchanged_all']
 auth=OUT/'qa/alpha_cleanup_authorization_20261017.json';assert read(auth)['threshold_rule']=='alpha == 1 -> 0' and read(auth)['authorized']
 auth23=Path(m['authorization']);a23=read(auth23)
 assert sha(auth23)==m['authorization_sha256'] and a23['authorized'] and a23['alpha_values']==[2,3]
 assert a23['max_component_box']==[8,8] and a23['padding_px']==24 and a23['max_component_pixels']==64 and a23['connectivity']==8
 first={x['key']:x for x in one['assets']};last={x['key']:x for x in m['assets']}
 rvpath=OUT/'qa/visual_reviews.json'
 with (OUT/'production.lock').open('a+b') as lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
  try:
   plan=load();assert len(plan['assets'])==652
   rvbytes=rvpath.read_bytes();rv=json.loads(rvbytes);reviews={x['key']:x for x in rv['assets']}
   checked=[]
   for a in plan['assets']:
    r=first[a['key']];s=last[a['key']];v=reviews[a['key']]
    raw=Path(r['input_file']);v1=Path(r['output_file']);target=Path(s['output_file'])
    assert a['output']==raw.as_posix() and a['sha256']==r['input_sha256']==sha(raw),'Stale raw snapshot'
    assert v['sha256']==a['sha256'] and v['reference']==a.get('comparison_reference',a['reference']),'Raw source comparison missing'
    assert s['raw_generated_file']==r['input_file'] and s['raw_generated_sha256']==r['input_sha256']
    assert s['input_file']==r['output_file'] and s['input_sha256']==r['output_sha256']==sha(v1)
    assert s['output_sha256']==sha(target)
    p,size,meta=pixels(raw);p1,size1,meta1=pixels(v1);p3,size3,meta3=pixels(target)
    assert size==size1==size3 and meta==meta1==meta3
    expected=p.copy();expected[:,:,3][expected[:,:,3]==1]=0
    assert np.array_equal(expected,p1)
    selected,protected,count=selection(p1[:,:,3]);expected[:,:,3][selected]=0
    assert int(selected.sum())==s['removed_pixels'] and np.array_equal(expected,p3)
    assert np.array_equal(p3[protected],p1[protected])
    checked.append((a,r,s,v,int((p3[:,:,3]==0).sum())))
   backup=OUT/'qa'/('visual_reviews_before_margin_'+hashlib.sha256(rvbytes).hexdigest()[:16]+'.json')
   if not backup.exists():backup.write_bytes(rvbytes)
   updated=[]
   for a,r,s,v,zeros in checked:
    old={k:x for k,x in a.items() if k not in ['candidate_history','original_reference']}
    a.setdefault('candidate_history',[]).append(old)
    a.update(output=s['output_file'],sha256=s['output_sha256'],bytes=s['bytes'],dimensions=s['dimensions'],mode='RGBA',alpha_zero_pixels=zeros,edge_alpha_nonzero=s['edge_nonzero_after'],final_approved=False,effect_status='pending_after_frame',repair_required=v['repair_required'],visual_review='raw_comparison_retained_with_exact_authorized_pixel_proof')
    flags=[x for x in a.get('quality_flags',[]) if x!='outer_edge_alpha_residue']
    if s['edge_nonzero_after']:flags.append('outer_edge_alpha_residue')
    a['quality_flags']=flags
    a['processing_provenance']=dict(method='alpha1 to zero, then isolated alpha2/3 margin dots only',raw_generated_file=r['input_file'],raw_generated_sha256=r['input_sha256'],alpha1_file=r['output_file'],alpha1_sha256=r['output_sha256'],alpha1_manifest=onepath.as_posix(),alpha1_manifest_sha256=sha(onepath),manifest=path.as_posix(),manifest_sha256=sha(path),authorization=auth.as_posix(),margin_authorization=auth23.as_posix(),all_rgb_unchanged=True,protected_art_and_glow_unchanged=True,alpha1_pixels_removed=r['alpha1_pixels_removed'],margin_pixels_removed=s['removed_pixels'],final_approved=False)
    a.pop('reused_exact_part',None);a.pop('original_reference',None)
    nv=dict(v);nv.update(file=a['output'],sha256=a['sha256'],raw_visual_review_sha256=v['sha256'],final_approved=False,visual_review=a['visual_review'],derivative_verification=dict(manifest=path.as_posix(),manifest_sha256=sha(path),actual_new_visual_inspection=False,all_rgb_unchanged=True,protected_art_and_glow_unchanged=True,only_permitted_alpha_changes=True,final_approved=False))
    updated.append(nv)
   rv.update(assets=updated,count=652,final_approved=0,original_review_backup=backup.as_posix(),original_review_backup_sha256=sha(backup),alpha_cleanup_review_method='Raw source comparison retained by exact authorized pixel proof; no claim of new visual inspection.')
   temp=rvpath.with_suffix('.writing.json');temp.write_text(json.dumps(rv,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(rvpath)
   plan['last_updated_utc']=datetime.now(timezone.utc).isoformat();plan['alpha_cleanup_adoption']=dict(manifest=path.as_posix(),manifest_sha256=sha(path),count=652,status='review_not_final',final_approved=0)
   write(plan)
   proof=dict(count=652,final_approved=0,manifest=path.as_posix(),manifest_sha256=sha(path),source_review_backup=backup.as_posix(),all_raw_and_previous_versions_preserved=True,all_rgb_and_protected_art_unchanged=True,actual_new_visual_inspection=False,edge_issues_after=m['edge_issues_after'])
   (OUT/'qa/margin_distance_adoption_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
   print(json.dumps(proof))
  finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
if __name__=='__main__':
 assert len(sys.argv)==3 and sys.argv[2]=='--generation-idle'
 main(sys.argv[1])
