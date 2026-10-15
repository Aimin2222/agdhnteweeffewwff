"""Read back a pinned GitHub archive and compare every added delivery file."""
from pathlib import Path
import hashlib,json,subprocess,sys,urllib.request,zipfile,time
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
commit=sys.argv[1];baseline='288b28a';archive=REPO/f'.delivery_verify_{commit[:8]}.zip'
url=f'https://codeload.github.com/Aimin2222/agdhnteweeffewwff/zip/{commit}'
request=urllib.request.Request(url,headers={'User-Agent':'AutoCine-asset-verification'})
with urllib.request.urlopen(request,timeout=240) as response,archive.open('wb') as f:
    amount=0;last=time.monotonic()
    while True:
        block=response.read(1024*1024)
        if not block:break
        f.write(block);amount+=len(block)
        if time.monotonic()-last>20:print('download_bytes',amount,flush=True);last=time.monotonic()
changed=subprocess.check_output(['git','diff','--name-only',baseline,commit],cwd=REPO,text=True).splitlines()
assert changed and all(p.startswith('LoL_AutoCine/assets/kill_frames_chatgpt/') for p in changed)
results=[]
tree=subprocess.check_output(['git','ls-tree','-r','-z',commit],cwd=REPO)
expected_blobs={}
for entry in tree.split(b'\0'):
    if entry:
        header,name=entry.split(b'\t',1);expected_blobs[name.decode('utf-8')]=header.split()[2].decode('ascii')
changed=sorted(name for name in expected_blobs if name.startswith('LoL_AutoCine/assets/kill_frames_chatgpt/'))
with zipfile.ZipFile(archive) as z:
    top=z.namelist()[0].split('/')[0]
    for name in changed:
        actual=z.read(top+'/'+name)
        blob=hashlib.sha1(b'blob '+str(len(actual)).encode()+b'\0'+actual).hexdigest()
        assert blob==expected_blobs[name],name
        results.append(dict(file=name,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),git_blob_sha1=blob,remote_matches=True))
report=dict(pinned_delivery_commit=commit,baseline=baseline,remote_source=url,checked_files=len(results),checked_pngs=sum(x['file'].endswith('.png') for x in results),all_remote_bytes_match=True,final_approved_count=0,note='Storage/content verification only. User adoption and game integration are not approved.',files=results)
(ROOT/'DELIVERY_REMOTE_VERIFICATION_V1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='files'}),flush=True)
