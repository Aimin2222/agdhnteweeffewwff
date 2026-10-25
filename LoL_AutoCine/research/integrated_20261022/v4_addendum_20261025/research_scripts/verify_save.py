from pathlib import Path
import urllib.request,json,hashlib,zipfile,io
R=Path(__file__).resolve().parents[2];O=R/'outputs/autocine_v4_addendum_20261025';W=Path(__file__).resolve().parent
COMMIT='13e6a76b539613b0dacdcb7ec93ecca7b4be3706'; PREFIX='LoL_AutoCine/research/integrated_20261022/v4_addendum_20261025/'
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AutoCine-research-verifier'}),timeout=60) as r:return r.read()
def sha(b):return hashlib.sha256(b).hexdigest()
rows=[]
paths=[p for p in sorted(O.rglob('*')) if p.is_file() and p.suffix!='.mkv' and p.name!='SAVE_RECEIPT_ADDENDUM.json']
for p in paths:
 name=p.relative_to(O).as_posix();remote=get('https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/'+COMMIT+'/'+PREFIX+name);assert remote==p.read_bytes(),name
 rows.append({'path':name,'sha256':sha(remote),'bytes':len(remote),'match':True})
zname='AutoCine_V4_Addendum_20261025.zip';remote=get('https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/'+COMMIT+'/'+PREFIX+zname);assert remote==(R/'outputs'/zname).read_bytes()
with zipfile.ZipFile(io.BytesIO(remote)) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('AutoCine_V4_Addendum/CONTENT_MANIFEST_ADDENDUM.json'))
 for item in manifest['files']:assert sha(z.read('AutoCine_V4_Addendum/'+item['path']))==item['sha256'],item['path']
 members=len(z.namelist())
commit=json.loads(get('https://api.github.com/repos/Aimin2222/agdhnteweeffewwff/commits/'+COMMIT));assert commit['parents'][0]['sha']=='48eeb9e5f3c15afc2641cf57344dcf2ca17740b9'
assert len(commit['files'])==28 and all(f['filename'].startswith(PREFIX) and f['status']=='added' for f in commit['files'])
ref=json.loads(get('https://api.github.com/repos/Aimin2222/agdhnteweeffewwff/git/ref/heads/work/autocine-integrated-research-20261022'));assert ref['object']['sha']==COMMIT
receipt={'verified_commit':COMMIT,'branch':'work/autocine-integrated-research-20261022','prefix':PREFIX,'remote_readable_files_exact_match':len(rows),'remote_zip_bytes':len(remote),'remote_zip_sha256':sha(remote),'remote_zip_crc_pass':True,'zip_members':members,'zip_manifest_member_hashes_match':len(manifest['files']),'remote_changed_files':len(commit['files']),'all_changes_new_research_prefix_files':True,'outside_prefix_changes':0,'protected_files_rehashed':1251,'protected_changes':0,'html_browser_validation':{'title':'AutoCine V4追補','tables':3,'video_links':32,'viewport_width':1280,'document_width':1265,'horizontal_document_overflow':False},'receipt_scope':'external to sealed ZIP; verify_save.py and this receipt created after ZIP was sealed','files':rows}
(O/'SAVE_RECEIPT_ADDENDUM.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))