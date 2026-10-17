from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from PIL import Image
import hashlib,json,subprocess,sys
r=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((r/'production.json').read_text(encoding='utf-8'));assets=d['assets']
assert len(assets)==652 and not any(a['status']=='pending' for a in assets)
motion=json.loads((r/'motion_catalog.json').read_text(encoding='utf-8'));m={a['key']:a for a in motion['assets']}
reviews=json.loads((r/'qa/visual_reviews.json').read_text(encoding='utf-8'));v={a['key']:a for a in reviews['assets']}
assert len(m)==len(v)==652
flags=Counter();review_repairs=[]
for a in assets:
    a.pop('original_reference',None)
    if a['status']=='generated_review_pending':a.pop('reused_exact_part',None)
    a['source_reference']='LoL_AutoCine/assets/kill_concepts/'+a['source_file']
    p=Path(a['output']);assert sha(p)==a['sha256']
    with Image.open(p) as im:
        assert im.mode=='RGBA' and max(im.size)>=2048
        im.verify()
    assert v[a['key']]['sha256']==a['sha256']
    spec=Path(m[a['key']]['outputs'][0]['file']).parent/'motion.json';s=json.loads(spec.read_text(encoding='utf-8'))
    assert s['frame_sha256']==a['sha256']
    assert s['qa']['mp4_frames']==90 and s['qa']['duration_ms']==3000 and s['qa']['zero_at_clip_boundaries']
    for output in s['outputs']:assert sha(Path(output['file']))==output['sha256']
    a['effect_status']='rendered_review_pending';a['motion_spec']=spec.as_posix();a['motion_spec_sha256']=sha(spec)
    a['visual_review']=v[a['key']]['visual_review'];a['review_notes']=v[a['key']]['notes'];a['repair_required']=v[a['key']]['repair_required'];a['final_approved']=False
    flags.update(a.get('quality_flags',[]))
    if a['repair_required']:review_repairs.append(a['key'])
d.update(status='all_candidates_and_motion_produced_review_delivery',final_approved=0,counts=dict(Counter(a['status'] for a in assets)),motion_count=652,visual_comparison_count=652,strict_source_match_approved=0,completed_utc=datetime.now(timezone.utc).isoformat())
(r/'production.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
subprocess.run([sys.executable,'LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5/production_tools/verify_sources.py'],check=True)
summary=dict(status=d['status'],source_originals=89,frame_entries=652,motion_entries=652,visual_comparison_entries=652,final_approved=0,quality_flags=dict(flags),review_repair_keys=review_repairs,source_partial_entries=sum(a['source_partial'] for a in assets),palette_reference_entries=sum(a['palette_reference'] for a in assets),integration_tested=False,gpu_tested=False,lol_tested=False)
(r/'qa/delivery_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
