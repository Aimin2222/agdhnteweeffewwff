"""Prepare built-in image edits and preserve all previous art candidates.

This script never calls an image API and never edits image pixels.
Run from the repository root: preview COUNT / jobs COUNT /
save INDEX EXPECTED_PREVIOUS_SHA GENERATED_PNG JOB_JSON.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,sys,msvcrt,time,shutil
from PIL import Image
import numpy as np
from frame_runner import SOURCE,OUT,PLAN,load,write,sha

def repair_jobs(count,preview=False):
 assert count>0
 d=load()
 if not preview:
  assert not any(a['status']=='pending' for a in d['assets']), 'Finish the first frame pass before starting repair image generation'
 reviews=json.loads((OUT/'qa/visual_reviews.json').read_text(encoding='utf-8'))['assets']
 technical={x['key']:x for x in json.loads((OUT/'qa/technical_snapshot.json').read_text(encoding='utf-8'))['assets']}
 by={a['key']:a for a in reviews};jobs=[]
 for a in sorted(d['assets'],key=lambda x:(max(x.get('dimensions',[9999]))>=2048,not by.get(x['key'],{}).get('repair_required',False),x['index'])):
  rv=by.get(a['key'])
  tv=technical.get(a['key'],{});edge_issue=tv.get('sha256')==a.get('sha256') and tv.get('edge_nonzero',0)>0
  if a['status']=='pending' or not rv or rv['sha256']!=a['sha256'] or not (rv.get('repair_required') or edge_issue) or a['source_partial']:
   continue
  notes=list(rv['notes']) if rv.get('repair_required') else []
  if edge_issue:notes.append('外周にalphaが0ではない画素が残っている。フレームや発光は保持し、外周と装飾のない余白を完全なalpha 0にする。薄い背景膜を残さない。')
  ref=a.get('comparison_reference',a['reference']);full=SOURCE/a['source_file']
  assert Path(ref).is_file() and full.is_file() and sha(full)==a['source_sha256']
  version=1
  dest=OUT/'frames'/a['number']/(a['id']+f'.generated_v5_{version}.png')
  while dest.exists():
   version+=1;dest=dest.with_name(a['id']+f'.generated_v5_{version}.png')
  colors={'039/palette_reference_01':'purple','039/palette_reference_03':'monochrome silver-white and black','039/palette_reference_04':'silver-white'}
  prompt=(f'Use case: precise-object-edit. Repair ONE isolated LoL AutoCine kill-frame, No.{a["number"]}, exact variant {a["id"]}. '
   'Image 1 is the authoritative complete crop for this variant. Image 2 is the whole original sheet, for context only. Image 3 is the existing generated candidate to correct. '
   'Reconstruct this exact reference design faithfully; preserve its portrait-border geometry, line thickness, palette, central ornament, spacing and supported native decoration. '
   'Repair these observed differences: '+ ' '.join(notes)+' '
   'Keep the structural central X/cross whenever the original contains it. Do not borrow adjacent strong/weak ornament, invent connectors, change left/right colors, or carry portrait hair accessories into the empty holes. '
   'Remove champion people, faces, hair and all writing. Native animal/mascot ornament is allowed only where it belongs to the frame in the exact source. '
   'Keep native solid black ornament such as an eclipse disc, dark orb, cat silhouette or castle opening where the reference depicts it; black ornament is not a transparency hole. Preserve blank paper talisman shapes while removing their writing. '
   'A rectangular portrait opening must stay rectangular, with the source corner shape; do not insert a circular hole, colored corner wedges or decorative plates. '
   'Both portrait holes and negative spaces must be empty alpha-zero. Every outer-border pixel must be alpha-zero: no nearly-transparent canvas tint, residue, paper, backdrop or checkerboard. '
   'Keep every supported decorative tip fully inside a generous transparent margin. Crisp native 2K-or-higher RGBA PNG, wide 3:1 composition, no upscaling. '
   'Output one usable transparent frame asset only, without a comparison sheet or caption.')
  if a['key'] in colors:prompt+=' This exact palette sample must use '+colors[a['key']]+', not the blue main sample.'
  jobs.append(dict(index=a['index'],key=a['key'],expected_previous_sha256=a['sha256'],reference=ref,full_source=full.as_posix(),edit_target=a['output'],output=dest.as_posix(),prompt=prompt,repair_notes=notes))
  if len(jobs)>=count:break
 print(json.dumps(jobs,ensure_ascii=True))

def save_repair(index,expected,generated,job_file):
 job=json.loads(Path(job_file).read_text(encoding='utf-8'))
 assert job['index']==index and job['expected_previous_sha256']==expected
 receipts=Path('v5_generation_receipts_tmp');receipts.mkdir(exist_ok=True)
 receipt=receipts/f'repair_{index:04d}_{int(time.time())}.json'
 receipt.write_text(json.dumps(dict(index=index,expected_previous_sha256=expected,generated_path=generated)),encoding='utf-8')
 with (OUT/'production.lock').open('a+b') as lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
  try:
   d=load();assert not any(x['status']=='pending' for x in d['assets'])
   a=d['assets'][index];assert a['sha256']==expected,'Stale repair job; preserve newer candidate'
   assert job['key']==a['key'] and job['reference']==a.get('comparison_reference',a['reference'])
   source=Path(generated)
   with Image.open(source) as im:
    assert im.mode=='RGBA' and max(im.size)>=2048
    dims=list(im.size);alpha=np.asarray(im.getchannel('A'));assert (alpha==0).any()
    edge=np.r_[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]
   version=1
   dest=OUT/'frames'/a['number']/(a['id']+f'.generated_v5_{version}.png')
   while dest.exists():
    version+=1;dest=dest.with_name(a['id']+f'.generated_v5_{version}.png')
   dest.parent.mkdir(parents=True,exist_ok=True)
   temporary=OUT/'staging'/a['number']/(a['id']+'.repair.png');temporary.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(source,temporary);assert sha(source)==sha(temporary);temporary.replace(dest)
   old={k:v for k,v in a.items() if k not in ['candidate_history','original_reference']}
   a.setdefault('candidate_history',[]).append(old)
   ref=a.get('comparison_reference',a['reference'])
   a.update(output=dest.as_posix(),sha256=sha(dest),bytes=dest.stat().st_size,mode='RGBA',dimensions=dims,reference=ref,reference_sha256=sha(Path(ref)),generator='built-in image_gen',generated_epoch=int(time.time()),visual_review='pending_original_comparison_after_repair',effect_status='pending_after_frame',status='generated_review_pending',final_approved=False,repair_required=True,repair_attempt=version,alpha_zero_pixels=int((alpha==0).sum()),edge_alpha_nonzero=int((edge>0).sum()),quality_flags=['outer_edge_alpha_residue'] if (edge>0).any() else [])
   if 'comparison_reference_crop_box' in a:a['reference_crop_box']=a['comparison_reference_crop_box']
   if a['palette_reference']:a['quality_flags'].append('tiny_palette_reference_not_independent_high_detail_original')
   a['repair_provenance']=dict(previous_sha256=expected,previous_file=old['output'],reference=ref,whole_original_sha256=a['source_sha256'],observed_notes=job['repair_notes'],status='new_candidate_requires_visual_review')
   a['prompt']=job['prompt'];a['generation_prompt']=job['prompt']
   a.pop('reused_exact_part',None)
   a.pop('original_reference',None)
   d['counts']=dict(Counter(x['status'] for x in d['assets']))
   d['saved_candidates']=sum(x['status']!='pending' for x in d['assets'])
   d.pop('generation_blocker',None);d['status']='production_in_progress'
   d['last_updated_utc']=datetime.now(timezone.utc).isoformat();write(d)
   print(json.dumps(dict(key=a['key'],file=a['output'],sha256=a['sha256'],dimensions=dims,final_approved=False)))
  finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

if __name__=='__main__':
 if sys.argv[1] in ['preview','jobs']:repair_jobs(int(sys.argv[2]),sys.argv[1]=='preview')
 elif sys.argv[1]=='save':save_repair(int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5])
 else:raise ValueError('Expected preview, jobs or save')
