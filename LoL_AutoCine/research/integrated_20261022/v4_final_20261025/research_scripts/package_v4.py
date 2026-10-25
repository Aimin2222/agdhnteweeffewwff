from lab_common import *
import hashlib,zipfile,re,html,shutil,ast,csv
shutil.copy2(Path(__file__),O/'research_scripts/package_v4.py')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
# Validate outputs before sealing. Publication receipts are deliberately external to the sealed package.
errors=[]
def check(name,condition):
 if not condition:errors.append(name)
check('native652',load(O/'FRAME652_TWELVE_CRITERIA_V4.json')['original_detail_viewed']==652)
check('no_asset_hash_change',load(O/'PROTECTION_RECHECK_V4.json')['different_or_missing']==0)
check('features70',len(load(O/'ALL_70_FEATURE_INTEGRATION_V4.json')['features'])==70)
check('tests14',len(load(O/'T01_T14_STATE_V4.json')['tests'])==14)
check('proposals19',len(load(O/'PROPOSAL19_ROADMAP_V4.json')['proposals'])==19)
check('recipes6',len(load(O/'SIX_RECIPES_V4.json')['recipes'])==6)
check('motion144',len(load(O/'MOTION_RENDER_EXECUTION_V4.json')['cases'])==144)
check('motion_decode_all',all(a['status']=='PASS' for a in load(O/'MOTION_RENDER_EXECUTION_V4.json')['cases']))
check('fx_moving35',len(load(O/'FX_MOVING_EXECUTION_V4.json')['cases'])==35)
check('fx90',len(load(O/'EXISTING_FX_EXPANDED_V4.json')['cases'])==90)
check('fx90_frames',all(a['decoded_frames']==36 and a['rc']==0 for a in load(O/'EXISTING_FX_EXPANDED_V4.json')['cases']))
check('settings119',load(O/'SETTINGS_PROJECT_ROUNDTRIP_V4.json')['passed']==119)
allfiles=sorted(p for p in O.rglob('*') if p.is_file() and p.suffix not in ['.zip'] and p.name not in ['CONTENT_MANIFEST_V4.json','DOCUMENT_VALIDATION_V4.json','SAVE_RECEIPT_V4.json','SAVE_VERIFICATION_V4.json','LOCAL_FINAL_RECEIPT_V4.json'])
for p in allfiles:
 if p.suffix=='.json':
  try:load(p)
  except Exception as e:errors.append(p.name+':JSON:'+str(e))
 if p.suffix=='.py':
  try:ast.parse(p.read_text('utf-8-sig'))
  except Exception as e:errors.append(p.name+':syntax:'+str(e))
text=(O/'index.html').read_text('utf-8')
for href in re.findall(r'(?:href|src)="([^"]+)"',text):
 if not href.startswith(('http','#')):check('html-link:'+href,(O/html.unescape(href)).is_file())
for i in list(range(1,16))+[17,18]:check('document'+str(i),len(list(O.glob(f'{i:02d}_*.md')))==1)
check('handoff16',(O/'16_CHATGPT_HANDOFF_V4.txt').is_file())
save('DOCUMENT_VALIDATION_V4.json',{'errors':errors,'state':'PASS' if not errors else 'FAIL','scope':'research documents/links/counts/JSON/script syntax, not product validation'})
assert not errors,errors
# Describe all deliverable groups, not "18 documents = all research PASS".
groups=[['01','総合報告','01_FINAL_RESEARCH_REPORT_V4_JA.md'],['02','動画20作品','VIDEO_FINAL_LEDGER_V4.json'],['03','652原寸','FRAME652_TWELVE_CRITERIA_V4.json'],['04','35FX','FX_COMPOSITION_MATRIX_V4.json'],['05','原本19制約','SOURCE19_SEARCH_V4.json'],['06','6motion','MOTION_RENDER_EXECUTION_V4.json'],['07','CPU Flash','FLASH_COMPAT_REVISION_V4.json'],['08','既存FX','EXISTING_FX_EXPANDED_V4.json'],['09','カメラ/6recipe','SIX_RECIPES_V4.json'],['10','自動画質','WARNING_QA_EXPANDED_V4.json'],['11','GPU/AV','AV_PTS_REVIEW_V4.json'],['12','T01–14','T01_T14_STATE_V4.json'],['13','既存修正','13_CODEX_EXISTING_FIX_INSTRUCTIONS_V4_JA.md'],['14','新仕様/PR','14_NEW_FEATURE_SPEC_AND_PR_PLAN_V4_JA.md'],['15','残件/実機','15_REMAINING_AND_WINDOWS_PACKAGE_V4_JA.md'],['16','ChatGPT','16_CHATGPT_HANDOFF_V4.txt'],['17','日本語HTML','index.html'],['18','ZIP一式','CONTENT_MANIFEST_V4.json']]
save('DELIVERABLE18_GROUPS_V4.json',{'groups':[{'id':i,'group':n,'entry':p,'artifact_available':True,'research_scope':'see per-ledger completion limits'} for i,n,p in groups]})
# Main GitHub tree keeps readable documentation and ledgers; media is losslessly packed in ordinary ZIPs.
media=[p for p in allfiles if p.suffix.lower() in ['.jpg','.png','.mp4','.mkv']]
limit=40_000_000;bins=[];sizes=[]
for p in sorted(media,key=lambda p:p.stat().st_size,reverse=True):
 n=next((i for i,s in enumerate(sizes) if s+p.stat().st_size<=limit),len(bins))
 if n==len(bins):bins.append([]);sizes.append(0)
 bins[n].append(p);sizes[n]+=p.stat().st_size
archive_map={p.relative_to(O).as_posix():f'archives/AutoCine_V4_media_{i+1:02d}.zip' for i,ps in enumerate(bins) for p in ps}
download='# ダウンロードと開き方\n\nローカルのAutoCine_Research_V4_20261025.zipは資料・画像・人工動画の全体です。展開後AutoCine_V4/index.htmlを開いてください。\n\nGitHubでは大きさ制限に合わせ、下の通常ZIPをすべてダウンロードして同じフォルダへ展開してください。結合ツールは不要、各ZIPを個別に開けます。ドキュメントはGitHubのフォルダにもそのまま保存します。\n\n'
for i in range(len(bins)):download+=f'- [画像・動画 {i+1}/{len(bins)}](archives/AutoCine_V4_media_{i+1:02d}.zip)\n'
download+='\nメディアZIPにはそれぞれAutoCine_V4/以下の一部の画像・動画を収録します。DOCUMENTS ZIPも同じ場所へ展開すると閲覧ページが全画像へ接続します。\n\n- [閲覧ページ・報告書・全台帳・研究スクリプト](archives/AutoCine_V4_documents.zip)\n\nCONTENT_MANIFESTのSHA256が各展開ファイルの正本です。SAVE_RECEIPTと遠隔照合記録はZIP封印後に作成するためZIP外で渡します。第三者YouTube動画/画面の転載は含みません。\n'
(O/'DOWNLOADS_V4.md').write_text(download,'utf-8')
(O/'README.md').write_text('# LoL AutoCine V4研究\n\n[ダウンロードと開き方](DOWNLOADS_V4.md) / [ChatGPTへ送る報告](16_CHATGPT_HANDOFF_V4.txt) / [総合報告](01_FINAL_RESEARCH_REPORT_V4_JA.md)\n\n本体変更なし・UI未選定・素材承認変更なし。原寸652確認と全条件合格は別、T01–14製品完全PASS0。実機/元資料/ユーザー判断が必要な残件は15番。\n\nGitHubのHTML rawは展開前の画像へ接続しません。documents ZIPと全media ZIPを同じ場所へ展開してindex.htmlを開くか、ローカル全体ZIPを使ってください。\n','utf-8')
allfiles=sorted(p for p in O.rglob('*') if p.is_file() and p.name not in ['CONTENT_MANIFEST_V4.json','SAVE_RECEIPT_V4.json','SAVE_VERIFICATION_V4.json','LOCAL_FINAL_RECEIPT_V4.json'])
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'git_blob':blob(p),'remote_media_archive':archive_map.get(p.relative_to(O).as_posix())} for p in allfiles]
save('CONTENT_MANIFEST_V4.json',{'files':manifest,'count':len(manifest),'self_excluded':True,'receipts_external':True,'remote_layout':'readable documents + archives containing exact media bytes; all ZIPs merge under AutoCine_V4/'})
allfiles.append(O/'CONTENT_MANIFEST_V4.json')
packages=R/'outputs/AutoCine_V4_packages_20261025';packages.mkdir(exist_ok=True)
def makezip(path,files):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(files):z.write(p,'AutoCine_V4/'+p.relative_to(O).as_posix())
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for p in files:assert hashlib.sha256(z.read('AutoCine_V4/'+p.relative_to(O).as_posix())).hexdigest()==digest(p)
 return {'name':path.name,'bytes':path.stat().st_size,'sha256':digest(path),'git_sha':blob(path),'members':len(files),'crc_and_member_sha_pass':True}
archiveinfo=[]
for i,ps in enumerate(bins):archiveinfo.append(makezip(packages/f'AutoCine_V4_media_{i+1:02d}.zip',ps))
docs=[p for p in allfiles if p not in media];archiveinfo.append(makezip(packages/'AutoCine_V4_documents.zip',docs))
full=R/'outputs/AutoCine_Research_V4_20261025.zip';fullinfo=makezip(full,allfiles)
(packages/'ARCHIVE_HASHES_V4.json').write_text(json.dumps({'archives':archiveinfo,'local_full_archive':fullinfo},ensure_ascii=False,indent=2),'utf-8')
uploads=[{'name':p.relative_to(O).as_posix(),'local':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'git_sha':blob(p)} for p in docs]
# A few direct comparison images make GitHub review convenient without unpacking.
uploads +=[{'name':p.name,'local':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'git_sha':blob(p)} for p in media if p.parent==O and p.suffix.lower() in ['.jpg','.png']]
for info in archiveinfo:
 p=packages/info['name'];uploads.append({**info,'name':'archives/'+info['name'],'local':str(p)})
p=packages/'ARCHIVE_HASHES_V4.json';uploads.append({'name':p.name,'local':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'git_sha':blob(p)})
(W/'upload_manifest.json').write_text(json.dumps(uploads,ensure_ascii=False,indent=2),'utf-8')
(W/'package_result.json').write_text(json.dumps({'full':fullinfo,'remote_archives':archiveinfo,'remote_files':len(uploads),'total_remote_bytes':sum(x['bytes'] for x in uploads)},ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'full':fullinfo,'archives':archiveinfo,'upload_files':len(uploads),'upload_bytes':sum(x['bytes'] for x in uploads)}))
