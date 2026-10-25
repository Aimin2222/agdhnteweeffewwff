from lab_common import *
import urllib.request,urllib.parse,hashlib,zipfile,time,concurrent.futures
state=load(W/'upload_state_final.json');commit=state['commit'];repo='Aimin2222/agdhnteweeffewwff';prefix='LoL_AutoCine/research/integrated_20261022/v4_final_20261025/';baseline='bbf941857f103fe49355a7a317189d97b52b1d62'
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AutoCine-V4-save-verification'}),timeout=120) as r:return r.read()
new=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{state["tree"]}?recursive=1'));old=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{baseline}?recursive=1'));assert not new['truncated'] and not old['truncated']
oldmap={x['path']:x['sha'] for x in old['tree'] if x['type']=='blob'};newmap={x['path']:x['sha'] for x in new['tree'] if x['type']=='blob'}
changed=[p for p in oldmap.keys()|newmap.keys() if oldmap.get(p)!=newmap.get(p)];outside=[p for p in changed if not p.startswith(prefix)];assert not outside,outside
manifest=load(W/'upload_manifest.json');assert len(changed)==len(manifest)
assert all(newmap[prefix+x['name']]==x['git_sha'] for x in manifest)
cache=W/'remote_download_verification';cache.mkdir(exist_ok=True)
def one(a):
 url=f'https://raw.githubusercontent.com/{repo}/{commit}/'+urllib.parse.quote(prefix+a['name'],safe='/');dest=cache/a['name'];dest.parent.mkdir(parents=True,exist_ok=True);attempts=[]
 for attempt in range(1,4):
  try:
   h=hashlib.sha256();n=0
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AutoCine-V4-save-verification'}),timeout=120) as r,dest.open('wb') as f:
    while True:
     b=r.read(1048576)
     if not b:break
     f.write(b);h.update(b);n+=len(b)
   actual=h.hexdigest();assert actual==a['sha256'] and n==a['bytes'],(a['name'],actual,n)
   row={'path':a['name'],'bytes':n,'sha256':actual,'matches':True,'attempts':attempt,'url':url}
   if a['name'].endswith('.zip'):
    with zipfile.ZipFile(dest) as z:assert z.testzip() is None;row['zip_crc_pass']=True;row['members']=len(z.namelist())
   print('verified',a['name'],flush=True);return row
  except Exception as e:attempts.append(type(e).__name__+':'+str(e));time.sleep(1)
 raise RuntimeError(str({'file':a['name'],'errors':attempts}))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,sorted(manifest,key=lambda x:x['bytes'],reverse=True)))
content=load(O/'CONTENT_MANIFEST_V4.json');expected={x['path']:x['sha256'] for x in content['files']};expected['CONTENT_MANIFEST_V4.json']=hashlib.sha256((O/'CONTENT_MANIFEST_V4.json').read_bytes()).hexdigest();seen={}
for a in manifest:
 if not a['name'].endswith('.zip'):continue
 with zipfile.ZipFile(cache/a['name']) as z:
  for name in z.namelist():
   assert name.startswith('AutoCine_V4/') and '..' not in Path(name).parts
   rel=name[len('AutoCine_V4/'):];sha=hashlib.sha256(z.read(name)).hexdigest();assert expected[rel]==sha
   assert rel not in seen;seen[rel]=sha
assert set(seen)==set(expected),(set(expected)-set(seen))
protection=load(O/'PROTECTION_RECHECK_V4.json');roots={'source':OLD/'source_readonly','work_asset':OLD/'asset_samples','original':Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository'),'legacy37':OLD/'legacy_asset_cache_v3'};protected_changes=[]
sourcehash={x['path']:x['sha256'] for x in load(OLD/'source_hashes.json')['files']};assethash={x['path']:x['actual_sha256'] for x in load(V3/'ASSET_FULL_QA_V2.json')['items']};originalhash={x['path']:x['sha256'] for x in load(V3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files']};legacyhash={x['path']:x['sha256'] for x in load(V3/'LEGACY_BADGE_PROTECTION_V3.json')['items']};maps={'source':sourcehash,'work_asset':assethash,'original':originalhash,'legacy37':legacyhash}
for a in protection['checks']:
 p=roots[a['group']]/a['path'];sha=hashlib.sha256(p.read_bytes()).hexdigest()
 if sha!=maps[a['group']][a['path']]:protected_changes.append(a)
assert not protected_changes
result={'verified_content_commit':commit,'tree':state['tree'],'baseline_tree':baseline,'remote_files':len(rows),'remote_file_sha256_match':all(x['matches'] for x in rows),'remote_zip_count':sum(x['path'].endswith('.zip') for x in rows),'remote_zip_member_sha256_verified':len(seen),'remote_zip_crc_all_pass':True,'outside_v4_prefix_changed':outside,'old_files_deleted':len(set(oldmap)-set(newmap)),'protected_files_rehashed':len(protection['checks']),'protected_hash_changes':protected_changes,'full_zip':load(W/'package_result.json')['full'],'files':rows,'scope':'fixed-commit raw bytes redownloaded, tree diff and every archive member checked; final receipt commit is subsequent metadata only'}
save('SAVE_VERIFICATION_V4.json',result);print(json.dumps({k:v for k,v in result.items() if k!='files'}),flush=True)
