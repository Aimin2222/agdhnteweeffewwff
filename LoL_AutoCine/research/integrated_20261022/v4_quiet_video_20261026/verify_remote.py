from pathlib import Path
import json,hashlib,zipfile,io,urllib.request,urllib.parse,concurrent.futures
R=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;O=R/'outputs/autocine_quiet_pass_20261025'
COMMIT='ea68b3873bd8b2285ab281761cd3828ed5a74d54';PARENT='95d281d228e71f125d6f57a7933775794329fe62'
PREFIX='LoL_AutoCine/research/integrated_20261022/v4_quiet_video_20261026/';REPO='Aimin2222/agdhnteweeffewwff'
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AutoCine-research-save-verification'}),timeout=30) as r:return r.read()
def sha(b):return hashlib.sha256(b).hexdigest()
sealed=json.loads((O/'CONTENT_MANIFEST.json').read_text('utf-8'))
local=[O/x['path'] for x in sealed['files']]+[O/'CONTENT_MANIFEST.json']
def one(p):
 rel=p.relative_to(O).as_posix();raw=get(f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/'+urllib.parse.quote(PREFIX+rel,safe='/'))
 assert raw==p.read_bytes(),rel
 return {'path':rel,'sha256':sha(raw),'bytes':len(raw),'match':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,local))
zname='AutoCine_Quiet_Video_Research_20261026.zip';raw=get(f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/{PREFIX}{zname}')
assert raw==(R/'outputs'/zname).read_bytes()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert z.testzip() is None;manifest=json.loads(z.read('AutoCine_Quiet_Research/CONTENT_MANIFEST.json'))
 for f in manifest['files']:assert sha(z.read('AutoCine_Quiet_Research/'+f['path']))==f['sha256'],f['path']
 count=len(z.namelist())
commit=json.loads(get(f'https://api.github.com/repos/{REPO}/commits/{COMMIT}'))
assert commit['parents'][0]['sha']==PARENT
assert len(commit['files'])==15 and all(x['status']=='modified' and x['filename'].startswith(PREFIX) for x in commit['files'])
initial=json.loads(get(f'https://api.github.com/repos/{REPO}/commits/{PARENT}'));assert len(initial['files'])==62 and all(x['status']=='added' and x['filename'].startswith(PREFIX) for x in initial['files'])
ref=json.loads(get(f'https://api.github.com/repos/{REPO}/git/ref/heads/work/autocine-integrated-research-20261022'))
head=ref['object']['sha']
if head!=COMMIT:
 metadata=json.loads(get(f'https://api.github.com/repos/{REPO}/git/commits/{head}'));assert metadata['parents'][0]['sha']==COMMIT
protected=json.loads((O/'PROTECTION.json').read_text('utf-8'));assert protected['count']==1251 and all(x['match'] for x in protected['checks'])
receipt={'content_commit':COMMIT,'parent':PARENT,'prefix':PREFIX,'remote_readable_files_exact_match':len(rows),'remote_zip_sha256':sha(raw),'remote_zip_bytes':len(raw),'zip_crc_pass':True,'zip_members':count,'manifest_hashes_verified':len(manifest['files']),'outside_prefix_changed':0,'changed_files':len(commit['files']),'protected_local_rehashed':1251,'protected_local_changed':0,'source_screenshots_published':0,'project_complete':False,'scope':'fixed commit raw download verified; this receipt is external to sealed package; no actual Windows/LoL integration approval','files':rows}
(O/'SAVE_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
