from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
root=Path('LoL_AutoCine/assets/kill_frames_chatgpt')
old=json.loads((root/'full_production_v4/source_sha_verification.json').read_text(encoding='utf-8'))
rows=[]
for a in old['files']:
    source=Path(os.environ.get('AUTOCINE_KILL_SOURCE_DIR','LoL_AutoCine/assets/kill_concepts'))
    if not source.exists() and Path('../LoL_AutoCine/assets/kill_concepts').exists():source=Path('../LoL_AutoCine/assets/kill_concepts')
    p=source/a['file']
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest==a['sha256'],a['number']
    rows.append(dict(number=a['number'],file=a['file'],sha256=digest,matched_previous_manifest=True))
result=dict(count=len(rows),all_matched=True,checked_utc=datetime.now(timezone.utc).isoformat(),status='source_integrity_only_not_art_quality_approval',files=rows)
dest=root/'full_production_v5/qa/source_integrity.json';dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Original images unchanged:',len(rows))
