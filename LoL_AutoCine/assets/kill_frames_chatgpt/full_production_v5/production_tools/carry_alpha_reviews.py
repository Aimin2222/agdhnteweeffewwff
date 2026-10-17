"""Retain raw visual findings for exact alpha-one-only derivatives.
Run after adoption, with image generation and review writers idle.
This records pixel proof, not a claim of a second visual inspection or final approval.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(manifest_path):
 manifest_path=Path(manifest_path);manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 plan=json.loads((ROOT/'production.json').read_text(encoding='utf-8'))
 assert plan['alpha_cleanup_adoption']['manifest_sha256']==sha(manifest_path)
 records={r['key']:r for r in manifest['assets']}
 path=ROOT/'qa/visual_reviews.json';raw_bytes=path.read_bytes()
 reviews=json.loads(raw_bytes);old={r['key']:r for r in reviews['assets']}
 updated=[]
 for asset in plan['assets']:
  record=records[asset['key']];review=old[asset['key']]
  assert asset['sha256']==record['output_sha256']==sha(Path(asset['output']))
  assert sha(Path(record['input_file']))==record['input_sha256']
  if record['input_sha256']==record['output_sha256']:
   updated.append(review);continue
  if review['sha256']==record['output_sha256'] and review.get('raw_visual_review_sha256')==record['input_sha256']:
   updated.append(review);continue
  assert review['sha256']==record['input_sha256'],'Raw visual comparison missing'
  assert review['reference']==asset.get('comparison_reference',asset['reference'])
  assert asset['processing_provenance']['raw_generated_sha256']==record['input_sha256']
  new=dict(review)
  new.update(file=asset['output'],sha256=asset['sha256'],final_approved=False,
   raw_visual_review_sha256=review['sha256'],
   visual_review='raw_original_comparison_retained_with_exact_alpha1_only_pixel_verification',
   derivative_verification=dict(manifest=manifest_path.as_posix(),manifest_sha256=sha(manifest_path),
    rgb_exactly_preserved=True,alpha_0_and_2_to_255_exactly_preserved=True,
    alpha1_pixels_removed=record['alpha1_pixels_removed'],
    actual_new_visual_inspection=False,final_approved=False))
  updated.append(new)
 backup=ROOT/'qa'/('visual_reviews_before_alpha_'+hashlib.sha256(raw_bytes).hexdigest()[:16]+'.json')
 if not backup.exists():backup.write_bytes(raw_bytes)
 reviews.update(assets=updated,count=len(updated),final_approved=0,
  alpha_cleanup_review_method='Raw source/candidate visual findings retained by exact permitted pixel-difference proof; not a new visual inspection.',
  original_review_backup=backup.as_posix(),original_review_backup_sha256=sha(backup))
 temporary=path.with_suffix('.writing.json')
 temporary.write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
 temporary.replace(path)
 print(json.dumps(dict(retained=len(updated),final_approved=0)))
if __name__=='__main__':main(sys.argv[1])
