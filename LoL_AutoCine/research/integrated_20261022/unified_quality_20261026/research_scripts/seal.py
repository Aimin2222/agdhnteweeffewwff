from common import *
from finish_research import textfile
import shutil,collections,zipfile,html,datetime,re
V3=R/'outputs/autocine_final_research_v3_20261024'
groups=[('source',OLD/'source_readonly',load(OLD/'source_hashes.json')['files'],'sha256'),('work_asset',A,load(V3/'ASSET_FULL_QA_V2.json')['items'],'actual_sha256'),('original',Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository'),load(V3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files'],'sha256'),('legacy37',OLD/'legacy_asset_cache_v3',load(V3/'LEGACY_BADGE_PROTECTION_V3.json')['items'],'sha256')]
checks=[];workhashes=collections.defaultdict(list)
for group,root,items,key in groups:
 for x in items:
  actual=sha(root/x['path']);checks.append({'group':group,'path':x['path'],'expected_sha256':x[key],'actual_sha256':actual,'match':actual==x[key]})
  if group=='work_asset':workhashes[actual].append(x['path'])
assert len(checks)==1251 and all(x['match'] for x in checks)
save('PROTECTION.json',{'count':1251,'changed':0,'checks':checks,'method':'whole-file SHA256 re-read in current stage','windows_settings_mutated':False})
save('A1_similarity/EXACT_DUPLICATE_REHASH_687.json',{'files':687,'duplicate_groups':[v for v in workhashes.values() if len(v)>1],'scope':'actual whole-file SHA256 now; not perceptual equivalence'})
sealed=[]
for n,h in [('AutoCine_Research_V4_20261025.zip','1ee3a7315713915c788ef5e55cdeb24e9fb914b2deb82439c0b2406736ad4543'),('AutoCine_V4_Addendum_20261025.zip','1ef56cc14d641b2d2d4da1282608c093c1db734e4d2127d393881bd4ddb2a31c'),('AutoCine_Quiet_Video_Research_20261026.zip','e0b1d62f69f74ce01934e5e76c94310d69ae5da05b45d249c4776cfc58f1119a'),('AutoCine_Research_UI_Continuation_20261026.zip','64823f6e215b029de671c379f2064bea3d0d3f6111dd030731810bf8a50cef55'),('AutoCine_Implementation_Quality_Audio_20261026.zip','e425d3b8c08751fe31a3696426dc8ade4b44180b636692036e2f6c1c5f84eb99'),('AutoCine_Visual_Proof_20261026_JA.zip','676ad11e8659c9dbf4157f8d30021b83963ea59a4cb1b0d83f73181b2df4381e')]:
 assert sha(R/'outputs'/n)==h;sealed.append({'file':n,'sha256':h,'unchanged':True})
save('SEALED_PREVIOUS_PACKAGES.json',sealed)

# The listed image inspections were performed with view_image, not inferred from encoder success.
visual=['A4_parity/comparison_'+m+'.png' for m in ['instant','pop','slide_left','slide_right','slide_up','slide_down']]+['A3_fx/flash_VFR.png','A3_fx/flash_headroom_patch.png','A3_fx/zoom_center_tracking_compare.png','A3_fx/combo_zoom_blur_flash.png','A3_fx/combo_focus_blur_glint.png','B1_camera/methods_compare.png','B2_oneclick/plan_compare.png','B3_audio/video_pulse_frames.png']
save('AI_VISUAL_QA_SCOPE.json',{'additional_representative_images':visual,'pair_images_inspected':38,'new_P2_images_inspected':24,'human_temporal_approval':False,'full_video_temporal_watching':False,'observations':['旧位置画像の登場中に画面端切れ/並び差が見える。共有列の2合成は同じ見た目。','headroom3強度が上限で同色に見え、強弱の見せ方として未完成。','時間blurは過去位置の二重像、宣言対象中心の空間blurは周囲を伸ばす。','zoom+旧flashの明るさ上昇が大きい。正規化だけで演出安全性は承認しない。','カメラ速度制限は急跳びを減らす一方、対象枠への遅れが見える。','AV画像は合成flashの前/中/後を確認。ゲーム映像ではない。'],'queue_file_note':'*_VISUAL_QUEUEは生成時NOT_RUNを保持する選定記録。実際の審査状態はAI_*REVIEWSを参照。'})

# Store research source and audited read-only references, no production modifications.
for p in W.glob('*.py'):
 d=O/'research_scripts'/p.name;d.parent.mkdir(exist_ok=True);shutil.copyfile(p,d)
for p in (W/'latest_readonly').rglob('*'):
 if p.is_file():
  d=O/'source_reference'/p.relative_to(W/'latest_readonly');d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)

textfile('CHATGPT_COPY_REPORT.txt','''LoL AutoCine統合品質研究（2026-10-26〜27）の研究納品を保存しました。製品修正・正式採用・LoL実機合格とは別です。
追加実証: 108条件3240frameの全アニメ時間比較。旧経路84FAIL/24REVIEW、共通RGBAを2合成器へ渡す候補108PASS（独立plannerや実GUI成功の証明ではありません）。Flash4合成clock列で先行RGB差分0。16他FX＋4組合せ、移動中心の時間/空間blur、4カメラ方式、4合成AV診断、6注入異常系を実行しました。
素材: 1464既存枠候補組とFX595組などを計測、38組AI画像比較。新規P2素材24件を審査し、継承140件と合わせ164/687。P2残523、人間の正式承認0、651暫定肖像形状と19原本制約は未解決です。ユーザー不採用5点は再推薦せず原本保護。数値類似を削除根拠にしません。
70機能の混合候補7メイン＋4詳細/素材/枠への接続表を作成し、比較3/5/8を保持。UI採点・正式採用・製品UI変更はありません。
実LoL/TargetLock/地形/実ゲーム音/GPU/NVENC/nativeDPI/クリーンPC配布/実concat・長尺同期はNOT_RUN。合成AVは実音源分析ではありません。参考20本は継承資料のみで今回の追加再生0本。
本体/UI29/main/素材承認/Windows設定を変更していません。保護1251fileと旧ZIP6点を再hash照合済み。
保存先: work/autocine-integrated-research-20261022 / LoL_AutoCine/research/integrated_20261022/unified_quality_20261026/
日本語ZIP・index.html・各A1〜B5報告・比較画像/動画・データ・再現script・Codex指示を収録。保存commit、ZIP hash、GitHub再download/実展開/全payload hashはZIP外SAVE_RECEIPT.jsonを参照してください。
追加のLeague Director/Lolnam Editor UI研究は未着手。今回の保存・完了報告後の別工程として分離しています。
''')

parts=['<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AutoCine 統合品質研究</title><style>body{max-width:1440px;margin:24px auto;padding:20px;background:#edf0f3;color:#203047;font:17px/1.7 system-ui}section,article{background:#fafbfc;padding:18px;margin:18px 0;border-radius:10px}a{color:#14559a}img,video{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px}summary{cursor:pointer}h1,h2{line-height:1.4}</style><h1>LoL AutoCine 統合品質研究</h1><p>研究候補・製品未統合。人間正式承認0。実LoL/GPU/nativeDPIはNOT_RUN。</p><p><a href="CHATGPT_COPY_REPORT.txt">ChatGPTへ報告文</a> / <a href="VALIDATION_REPORT.json">検証結果</a> / <a href="CODEX_HANDOFF_JA.md">Codex引継ぎ</a> / <a href="REPRODUCE_JA.md">再現条件</a></p>']
for p in [O/'README_JA.md',O/'NEW_VS_INHERITED_JA.md',O/'CODEX_HANDOFF_JA.md',O/'REPRODUCE_JA.md',O/'OPERATION_LOG_JA.md']:
 parts.append('<details><summary>'+html.escape(p.stem)+'</summary><pre>'+html.escape(p.read_text('utf8'))+'</pre></details>')
for folder in ['A1_similarity','A2_quality','A3_fx','A4_parity','B1_camera','B2_oneclick','B3_audio','B4_function_map','B5_distribution']:
 parts.append('<section><h2>'+folder+'</h2><details><summary>日本語報告・条件・限界</summary><pre>'+html.escape((O/folder/'README_JA.md').read_text('utf8'))+'</pre></details><p>')
 for p in sorted((O/folder).glob('*.json')):parts.append('<a href="'+p.relative_to(O).as_posix()+'">'+html.escape(p.name)+'</a> / ')
 parts.append('</p><div class="grid">')
 for p in sorted((O/folder).rglob('*.png')):
  rel=p.relative_to(O).as_posix();parts.append('<article><p>'+html.escape(p.stem)+'</p><a href="'+rel+'"><img loading="lazy" src="'+rel+'" alt="'+html.escape(p.stem)+'"></a>')
  v=p.with_suffix('.mp4')
  if v.exists():parts.append('<video controls muted playsinline preload="none" src="'+v.relative_to(O).as_posix()+'"></video>')
  parts.append('</article>')
 for p in sorted((O/folder).glob('*.mp4')):
  if p.with_suffix('.png').exists():continue
  rel=p.relative_to(O).as_posix();parts.append('<article><p>'+html.escape(p.stem)+'（B3は合成pulse音声。初期ミュート）</p><video controls muted playsinline preload="none" src="'+rel+'"></video></article>')
 parts.append('</div></section>')
parts.append('</html>');textfile('index.html',''.join(parts))

# Independent deliverable checks. Tests are not fabricated product release gates.
qc=[]
for p in O.rglob('*.json'):
 j=json.loads(p.read_text('utf-8-sig'),parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)));qc.append({'path':p.relative_to(O).as_posix(),'type':'json','status':'PASS'})
for p in O.rglob('*.png'):
 with Image.open(p) as im:im.verify()
 qc.append({'path':p.relative_to(O).as_posix(),'type':'png_decode','status':'PASS'})
for rel in re.findall(r'(?:src|href)="([^"]+)"',(O/'index.html').read_text('utf8')):
 assert (O/rel).is_file(),rel
qc.append({'type':'gallery_local_links','status':'PASS'})
classification=load(O/'A1_similarity/ASSET_CLASSIFICATION_RESEARCH.json')['items'];assert len(classification)==687
excluded=[x for x in classification if x['user_rejected']];assert len(excluded)==5 and all(not x['recommendation_eligible'] for x in excluded)
qc.append({'type':'excluded5_and_687_classification','status':'PASS'})
save('DELIVERY_QA.json',{'checks':qc,'counts':dict(collections.Counter(x['type'] for x in qc)),'videos':'encode/decode checks and actual PTS are in per-test JSON; not full AI temporal review','payload_images':len(list(O.rglob('*.png'))),'payload_videos':len(list(O.rglob('*.mp4'))),'additional_UI_research':'NOT_RUN'})
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['CONTENT_MANIFEST.json','SAVE_RECEIPT.json']:manifest.append({'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
save('CONTENT_MANIFEST.json',{'files':manifest,'self_excluded':True,'receipt_outside_zip':True})
archive=R/'outputs/AutoCine_Unified_Quality_20261027_JA.zip';assert not archive.exists(),'sealed archive must not be overwritten'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file() and p.name!='SAVE_RECEIPT.json':z.write(p,'AutoCine_Unified_Quality/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;members=len(z.infolist())
pack={'zip':str(archive),'zip_bytes':archive.stat().st_size,'zip_sha256':sha(archive),'zip_members':members,'payload_files':len(manifest),'images':len(list(O.rglob('*.png'))),'videos':len(list(O.rglob('*.mp4'))),'sealed':True}
(W/'package_result.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2),'utf8');print(json.dumps(pack,ensure_ascii=True))
