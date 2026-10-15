"""Verify review PNG bytes locally and against a pinned GitHub commit."""
from pathlib import Path
import concurrent.futures, hashlib, json, sys, urllib.request, urllib.parse

root = Path(__file__).parent
commit = sys.argv[1]
records = []
for inventory_path in sorted((root/'review').glob('*/inventory.json')):
    inv = json.loads(inventory_path.read_text(encoding='utf-8'))
    if int(inv.get('source_number', '0')) < 16:
        continue
    for asset in inv['assets']:
        path = inventory_path.parent/asset['file']
        relative = 'LoL_AutoCine/assets/kill_frames_chatgpt/'+path.relative_to(root).as_posix()
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        assert sha == asset['sha256'], relative
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob == asset['git_blob_sha1'], relative
        records.append(dict(source_number=inv['source_number'], file=relative, bytes=len(data), sha256=sha, git_blob_sha1=blob))

def verify(record):
    url = 'https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/'+commit+'/'+urllib.parse.quote(record['file'],safe='/')
    with urllib.request.urlopen(url, timeout=90) as response:
        data = response.read()
    record['remote_sha256'] = hashlib.sha256(data).hexdigest()
    record['remote_bytes'] = len(data)
    record['remote_matches'] = record['remote_sha256'] == record['sha256'] and len(data) == record['bytes']
    assert record['remote_matches'], record['file']
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    verified = list(pool.map(verify,records))
report = dict(pinned_asset_commit=commit, branch='chatgpt/killframes-source-numbering-20261014', checked_png_count=len(verified), all_remote_bytes_match=True, final_approved_count=0, note='Byte verification confirms storage only; it does not confer visual or alpha approval.', assets=verified)
(root/'GITHUB_REVIEW_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='assets'}))
