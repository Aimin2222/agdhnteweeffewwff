"""Research-only ledgers and handoff; never mutate product or asset catalog."""
from lab_common import *
import copy,csv,hashlib,html,re,shutil,collections
DATE='2026-10-25 JST';BASE='fb03e0390805125fc063f4599af6c2541a653abf';UI='b32513ada0a5ada7585972e06716ff84829bcb23'
def md(name,text):(O/name).write_text(text.strip()+'\n','utf-8')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('|','／').replace('\n',' / ') for x in row)+' |' for row in rows)+'\n'
def csvout(name,rows):
 with (O/name).open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

# Keep the original twenty and all V3 observations; augment only evidenced V4 windows.
v=load(V3/'VIDEO_OBSERVATIONS_V3.json');videos=copy.deepcopy(v['videos']);notes=[]
for p in sorted((W/'video_evidence').glob('*notes.json')):
 data=load(p)
 if data.get('video')=='V08' and 'id' not in data:data['id']='V08'
 if isinstance(data,list):notes.extend(data)
 elif 'items' in data:notes.extend(data['items'])
 else:notes.append(data)
by={a['id']:a for a in videos};newids={'V07','V11','V21'}
for a in videos:
 a['v4_notes']=[n for n in notes if n.get('id')==a['id']]
 a['v4_sequences']=[]
 for p in sorted((W/'video_evidence').glob(a['id']+'*.json')):
  data=load(p)
  if 'screenshots' not in data:continue
  samples=[z for z in data['screenshots'] if not z.get('aborted') and z.get('time') is not None]
  if not samples:continue
  a['v4_sequences'].append({'label':p.stem,'start':samples[0]['time'],'last_screenshot':samples[-1]['time'],'player_end':data['end'].get('t'),'duration':samples[0].get('duration'),'count':len(samples),'timing_evidence':'video_timing/'+p.name,'sampling_ms':data.get('cadence_ms'),'method':'continuous player between sampled screenshots; transient subframe edits unresolved'})
 a['two_explicit_kill_ui_v4']=a['id'] in newids or a.get('two_explicit_kill_ui',False) or a.get('two_explicit_kills',False)
 a['audio_v4']='NOT_HEARD';a['whole_v4']='NEAR_COMPLETE_SAMPLED' if a['id'] in ['V06','V08','V21'] else 'PARTIAL_RANGES'
# V3 schema uses a different evidence flag; its documented ten IDs are retained explicitly.
oldten={'V04','V05','V06','V09','V12','V13','V20','V22','V23','V25'}
for a in videos:a['two_explicit_kill_ui_v4']=a['id'] in oldten|newids
save('VIDEO_FINAL_LEDGER_V4.json',{'date':DATE,'original_count':20,'originals_replaced':0,'works_with_played_ranges':20,'v4_additional_works':sum(bool(a['v4_sequences']) for a in videos),'two_explicit_notifications':13,'unresolved_originals':[a['id'] for a in videos if not a['two_explicit_kill_ui_v4']],'near_complete_sampled_works':['V06','V08','V21'],'full_frame_audio_analyses':0,'audio_heard':0,'videos':videos})
csvout('VIDEO_FINAL_LEDGER_V4.csv',[{'id':a['id'],'title':a['title'],'url':a['url'],'two_explicit_notifications':a['two_explicit_kill_ui_v4'],'coverage':a['whole_v4'],'audio':'NOT_HEARD','v4_ranges':'; '.join(f"{s['start']:.3f}–{s['last_screenshot']:.3f}" for s in a['v4_sequences']),'observed_v3':a.get('observed',''),'observed_v4':json.dumps(a['v4_notes'],ensure_ascii=False),'inference_v3':a.get('implementation_inference',''),'unverified':'FOV, exact speed, sound beat, whole original except noted near-complete works'} for a in videos])
timing=O/'video_timing';timing.mkdir(exist_ok=True)
for p in (W/'video_evidence').glob('*.json'):shutil.copy2(p,timing/p.name)

# Separate twelve criteria for every material. Viewing is not formal approval.
pixel=load(O/'NATIVE_PIXEL_LEDGER_V4.json');limit=load(V3/'SOURCE_LIMITATIONS_INHERITED_V3.json');limited={a['key'] for a in limit['assets']};native=load(O/'NATIVE_VISUAL_LOG_V4.json')['viewed']
assets=[]
criteria=['native_design','edge_crop','alpha','portrait_position','killer_victim','portrait_shape','original_fidelity','theme_expression','color_ornament','final_size','HUD','three_backgrounds']
for a in pixel['items']:
 b=copy.deepcopy(a);verified=a['portrait_geometry_verified']
 b['criteria']={
 'native_design':{'state':'VIEWED','evidence':'NATIVE_VISUAL_LOG_V4.json','note':native.get(a['id'],{}).get('note','')},
 'edge_crop':{'state':'REVIEW_REQUIRED' if a['edge_alpha_gt8'] else 'VIEWED_NO_OBVIOUS_EDGE_TOUCH','evidence':'native pixels + original-detail view','note':f"edge alpha>8 count={a['edge_alpha_gt8']}; edge contact alone is not damage"},
 'alpha':{'state':'METRICS_AND_COMPOSITE_VIEWED','evidence':'native pixels + FRAME_BACKGROUND_EXECUTION_V4.json','note':'low-alpha RGB must be judged after compositing; colored transparent RGB is not opacity defect'},
 'portrait_position':{'state':'VERIFIED_METADATA' if verified else 'PROVISIONAL_FALLBACK','evidence':'catalog portrait_boxes','note':'651 missing per-material portrait_boxes, fallback is not final geometry'},
 'killer_victim':{'state':'VIEWED_IN_SYNTHETIC_COMPOSITE','evidence':'frame_backgrounds','note':'Yasuo left, Jinx right; real replay victim resolution NOT_RUN'},
 'portrait_shape':{'state':'VERIFIED_ROUND_METADATA' if verified else 'REVIEW_REQUIRED','evidence':'original-detail + composite','note':'round fallback not guaranteed to fit rectangular/octagonal originals'},
 'original_fidelity':{'state':'BLOCKED_SOURCE' if a['id'] in limited else 'PARTIAL','evidence':'V3 SOURCE_EDGE_COMPARE_LOG + source hashes','note':'visual correspondence, not pixel-exact reconstruction;19 source constraints stay unresolved'},
 'theme_expression':{'state':'VIEWED','evidence':'native notes','note':'theme color/ornament observed; no external skin canonical approval inferred'},
 'color_ornament':{'state':'VIEWED','evidence':'native notes and3background sheet','note':'art approval remains user decision'},
 'final_size':{'state':'VIEWED_384PX_COMPOSITE','evidence':'frame_backgrounds','note':'384px badge crop fixture; actual output context/651 geometry still unverified'},
 'HUD':{'state':'PARTIAL_SYNTHETIC','evidence':'frame_backgrounds + ALL652_MOTION_GEOMETRY_V4.csv','note':'artificial HP/minimap collisions shown; actual LoL HUD NOT_RUN'},
 'three_backgrounds':{'state':'VIEWED','evidence':'FRAME_BACKGROUND_EXECUTION_V4.json','note':'light/dark/complex artificial backgrounds, no real LoL capture'}
 }
 b['overall']='PARTIAL';b['all_twelve_pass']=False;b['formal_approval_unchanged']=True;assets.append(b)
save('FRAME652_TWELVE_CRITERIA_V4.json',{'count':652,'original_detail_viewed':len(native),'three_background_viewed':652,'all_twelve_pass':0,'portrait_boxes_verified':1,'portrait_boxes_provisional':651,'criteria':criteria,'items':assets})
csvout('FRAME652_TWELVE_CRITERIA_V4.csv',[{'id':a['id'],'number':a['number'],'theme':a['theme'],'width':a['width'],'height':a['height'],'sha256_unchanged':a['sha256_unchanged'],'formal_status':a['formal_status'],'overall':a['overall'],**{k:a['criteria'][k]['state'] for k in criteria},'native_note':a['criteria']['native_design']['note']} for a in assets])
shutil.copy2(V3/'SOURCE_LIMITATIONS_INHERITED_V3.json',O/'SOURCE19_INHERITED_V4.json')

# Existing 70 feature contracts retain source IDs, fields and runtime limits.
features=load(V3/'ALL_70_FEATURE_INTEGRATION_V3.json');ft=features['features']
for a in ft:
 a['v4_ui_observed_head']=UI;a['ui_connection_review']='NOT_RUN: user UI not selected; no runtime adapter integration performed';a['windows_runtime_result']='NOT_RUN_LIVE'
 a['integration_gate']='UI29 completion -> user selects UI -> integrate existing functions -> Windows/LoL test -> research adoption -> new features'
 a['v4_evidence']=('CAMERA_SOURCE_MATH_V4.json; CAMERA_RECIPE_RULE_RESULTS_V4.json' if a['id'].startswith('CAM_') or a['id'] in ['FIXED','FULL'] else 'NATIVE_PIXEL_LEDGER_V4.json; FRAME652_TWELVE_CRITERIA_V4.json' if a['id'] in ['WORKFRAME','WORKFX','BADGE','MOTION'] else 'GPU_ENCODE_PROBE_V4.json' if a['id'] in ['NVENC','GPUFX'] else 'AV_PTS_REVIEW_V4.json' if a['id'] in ['AUDIO','AUDIOGUARD','BGM'] else 'EXISTING_FX_EXPANDED_V4.json' if a['id'].startswith('FX_') else 'V3 static source findings retained; live UI connection pending')
features.update(observed_ui_head=UI,status='70 rows preserved; runtime integration not completed',date=DATE);save('ALL_70_FEATURE_INTEGRATION_V4.json',features);csvout('ALL_70_FEATURE_INTEGRATION_V4.csv',ft)
test=load(V3/'T01_T14_TEST_MATRIX_V3.json');ev={
'T01':['PARTIAL','CAMERA_SOURCE_MATH_V4.json 48/48; CAMERA_RECIPE_RULE_RESULTS_V4.json 133/133','real BLUE/RED target, occlusion, TargetLock and3D camera not observed'],
'T02':['PARTIAL','independent event grouping/dedup/assist rules and time-map V3 fixtures','real match scan/seek/capture anchors absent'],
'T03':['PARTIAL','23472 geometry scenarios,144 mirror renders,35 moving-FX composites; Flash reproduced','real short/long multi-kill and actual HUD absent'],
'T04':['PARTIAL','camera finite-value48 checks; QA semantic fixtures only','no actual wall/dash/target images or engine collision oracle'],
'T05':['PARTIAL','WARNING_QA_EXPANDED_V4.json 56/56 declared fixture labels','metadata-based exclusions not video recognition; actual LoL false-positive rate unmeasured'],
'T06':['PARTIAL','687 preserved hashes;652 original-detail views and3backgrounds;35FX composition','651 portrait geometries,19 source limitations, actual LoL presentation not approved'],
'T07':['PARTIAL','144 actual mirror videos decoded;652x6x3x2 numeric cases;24 four-phase sheets viewed','GPU parity and actual LoL/HUD not executed'],
'T08':['REPRODUCED','PREVIEW_EXPORT_PARITY_V4.json same083 matches1080p bbox, differs1366/1280','isolated original CPU renderer; live final job parity not executed'],
'T09':['REPRODUCED','48 legacy/v2 +24 v3 +24 causal-gate Flash cases;single event3/3 bit equal in both candidates','v3 future pulse overlap exposed; causal-gate candidate tested; no product fix or live job pass'],
'T10':['PARTIAL','4 CPU/NVENC encode tests decode120/300; OpenCL failed twice incl alternative','GPU FX BLOCKED OpenCL device creation -12; NVENC is not GPU FX'],
'T11':['PARTIAL','12 artificial AV cases;10 within50ms,2 around-58.7ms need review','LoL process audio not captured; no heard-audio quality claim'],
'T12':['PARTIAL','6 recipe roundtrip/manual guards,133 independent rules','no adopted recipe / real same-take six outputs'],
'T13':['PARTIAL','1251 protected local files unchanged;70 rows retain IDs/settings contracts','old project GUI roundtrip and all selected UI connections not executed'],
'T14':['PARTIAL','V3 checkpoint/static contract and new handoff acceptance package','long-run resume, clean-PC distribution, cancelled live record NOT_RUN']}
for a in test['tests']:
 state,evidence,remain=ev[a['id']];a.update(status=state,execution_evidence=evidence,remaining_reason=remain,full_test_pass=False,live_status='BLOCKED_NO_REPLAY' if a['id'] not in ['T13','T14'] else 'NOT_RUN_INTEGRATION_OR_DISTRIBUTION',owner='Codex + user Windows/LoL after UI selection')
 if a['id']=='T13':a['execution_evidence']+='; actual Template/SceneProject119/119 independent roundtrip/undo/redo/version/keyframe tests'
test.update(date=DATE,full_product_pass_count=0,states=['PASS','FAIL','PARTIAL','REPRODUCED','BLOCKED','NOT_RUN']);save('T01_T14_STATE_V4.json',test)
csvout('T01_T14_STATE_V4.csv',[{k:a[k] for k in ['id','title','status','execution_evidence','remaining_reason','live_status','owner','full_test_pass']} for a in test['tests']])
recipes=load(V3/'SIX_RECIPE_PROPOSALS_V3.json')
changes={
'cinematic':'V06/V08/V21: use wide through fight; optional last-only character close. Neutral mild grade, no repeated fullscreen flash. Model/weapon anchor and replacement backgrounds need new implementation.',
'impact':'V06 explicit multi-kill progression: last-only optional pulse; fix multi-event timing before recipe use. Strong Flash is user option, never preapproved.',
'elegant':'V08 flowing close and pale scenes: preserve wide during fight, weak ornament; white background/DOF cannot be inferred as existing engine capability.',
'competitive':'V07/V11 notifications demonstrate event evidence; wide + clear target/HUD and low FX. Preserve original speed and manual camera.',
'montage':'V01/V02/V03/V15/V16/V24: wide pursuits and transitions; no per-kill close in next engagement. Split scenes and CG intro are separate new features.',
'low_load':'existing single take/manual baseline CPU graph; avoid multi-take and new depth features. NVENC probe success not GPU FX success.'}
for a in recipes['recipes']:
 a['revision']=2;a['v4_observation_change']=changes.get(a['id'],changes['low_load']);a['adopted']=False
 a['exceptions']={'unknown_team':'retain manual verified baseline, do not autoapprove','unknown_target':'skip cutaway, retain source scene','invalid_time_map':'reject job draft before recording','missing_asset':'report explicit missing ID, do not silently promote review','no_gpu_fx':'separate CPU capability from encoder fallback','audio_required_but_missing':'fail visibly; no desktop audio fallback','unknown_revision':'preserve file and refuse unsupported effect; do not rewrite'}
save('SIX_RECIPES_V4.json',recipes)
contract=load(V3/'RESEARCH_CONTRACTS_V3.json');contract['v4_status']='proposal; no product API implemented';contract['ShotPlan']['required_fields_v4']=['schema_version','processing_revision','source_patch','replay_hash','event_ids','team','target_id','legacy_camera_values','manual_overrides','settings_hash','asset_hashes','segments','time_maps','candidate_scores','rejection_reasons','confidence','fallback_reason'];contract['ShotPlan']['score_contract']={'unknown':'null, not zero','take_limit':3,'thresholds':'proposal only; no runtime default','retain':'all rejected scores/reasons and selected baseline','tie_break':'prefer verified baseline, then lower resource cost, stable ID'}
save('RESEARCH_CONTRACTS_V4.json',contract)
road=load(V3/'PROPOSAL_ROADMAP_V3.json')
for a in road['proposals']:
 a['v4_adoption']=False;a['stage']='after UI choice + existing70 integration + live QA + research adoption';a['rollback']='retain old IDs/project values/processing revision; disable only new candidate and keep baseline output'
 if a['id']=='A01':a['v4_evidence']='Flash v3 single-event3/3bit equality but future pulse can leak before event under overlap; causal-gated research candidate24 cases/single3/3 resolves sampled premature rise; v2 amplitude rejected'
 if a['id']=='B02':a['v4_evidence']='Zoom scale4 saturation isolated; auto-normalize/quarter candidates preserve detail, require new revision; no old look rewrite'
 if a['id']=='C02':a['v4_evidence']='preview/export non1080 bbox difference actually reproduced'
save('PROPOSAL19_ROADMAP_V4.json',road)

common='研究領域のみ。AutoCine本体・UI29・カメラ・FX・録画・GPU・音声・37バッジ・89原本・承認状態は変更していません。UIは未選定です。'
save('FX_REPOSITORY_BACKGROUND_VISUAL_V4.json',{'reviewed_sheets':35,'composites':560,'scope':'repository camera QA still cropped320x180 then enlarged; actual current LoL capture not verified','items':[{'file':p.relative_to(O).as_posix(),'viewed':True,'observation':'Both portraits identifiable; strong Arcade/Dawn/Infernal etc vertically bridge rows and compete with bright background beam. Provisional round masks misfit non-round originals. Original reference has no HUD evidence.','status':'REVIEW_REQUIRED','approved_changed':False} for p in sorted((O/'fx_repository_background').glob('*.jpg'))]})
md('01_FINAL_RESEARCH_REPORT_V4_JA.md',f'''# LoL AutoCine V4 総合研究報告
{DATE} / {common}

## 実施結果
{table(['項目','今回の証拠','残る範囲'],[
['動画','元20作品維持。未確定10作品すべて追加再生。明確な通知2件以上13/20、V3比+3','7作品は追加区間でも通知未確定。音声0/20、全作品全編ではない'],
['652フレーム','652/652 original-detail原寸PNG全体目視、native pixel、3人工背景合成を全件確認','12条件完全合格0、651肖像枠はfallback、19原本制約、実HUD未検証'],
['35FX','4形状×2強度×3背景=840、Flash/grade840、動背景35本decode、既存camera参照背景560合成','既存参照は320×180拡大、現在の実LoLではない。2時点比較35で全時間人手審査ではない'],
['6motion','144実描画条件全decode。全652×6×3解像度×2fps=23472幾何条件','人工CPU。GPU/実LoLは未合格'],
['Flash','旧/v2 48、v3 24、因果gate候補24。単一event3強度bit一致','v2非互換、v3短間隔で未来pulse混入を確認。因果gateも研究候補、製品修正なし'],
['既存FX','初回30条件、追加90条件を実処理。Zoom飽和と非1080寸法固定を確認','decode成功は画質合格ではない'],
['カメラ','旧10保持。数学48/48、独立ルール133/133','3D/BLUE-RED/TargetLock実機映像未検証'],
['QA/AV/GPU','56正常異常fixture、12AV、CPU/NVENC4encode','AV2条件要確認、OpenCL失敗、LoL音声未検証'],
['保護/保存','1251ファイルhash全一致、既存Template/SceneProject119/119独立試験','遠隔保存prefix検査は別の保存検証記録'],
['T01–14','全14状態/証拠/手順を台帳化','製品全体PASS 0/14']])}

## 優先する既存問題
1. CPU Flashの後続event減衰中心。旧単発の振幅・窓を維持したv3候補で回帰する。
2. Zoom Blurのtmix scale=4による人工映像飽和。比較画像・9候補条件と切り分け4条件あり。
3. 1366/1280出力のmirror/export素材座標差。1080pでは083の可視bbox一致、縮小解像度では不一致。
4. 651候補のportrait geometryは仮。円形fallbackを四角/八角等の正式実装として扱わない。
5. 30fps・2x人工AVはPCM/AACとも約−58.7ms。機械閾値の立上り/atempo過渡を含むのでLoL障害と断定しない。

## V3からの差分
原寸全体確認を652へ拡充。追加原本探索55,578候補から新hash0。動画の明確な2kill確認10→13。144motion・35動背景FX・Flash互換候補・48カメラ数学・90FX追加・56QA・12AV・4encodeを追加。新規提案19と70機能は採用/接続完了に変更しない。

## 未完了を閉じる条件
7動画のHUDなし区間から公式通知を推測で作れない。音声は聴取経路がなく未検証。元資料19は追加完全原本またはユーザーの別デザイン判断が必要。実LoLはport2999閉、研究範囲のrofl0。OpenCLは通常・代替・sandbox外再試行もdevice creation -12。必要データと手順は15番。Workで継続可能なのは長編の追加観察/人工試験/原本新規提供後の照合で、製品実機合格へは昇格できない。

## 保存
研究ブランチ work/autocine-integrated-research-20261022 / 新規v4_final_20261025のみ。固定commitとZIP SHAは保存レシートで確認してください。V1–V3を上書きしません。
''')
video_md='# 動画20作品の最終観察台帳\n\n20作品すべて既存IDを保持。V4は未確定10作品に追加区間、V06短編も追加確認。連続再生中の約1.6〜1.9秒間隔画面観測で、全フレーム解析・正確な速度/FOV・音声分析とは異なります。\n\n'
video_md+=table(['ID','作品','2通知','V4追加観測範囲','全体'],[[a['id'],f"[{a['title']}]({a['url']})",'確認' if a['two_explicit_kill_ui_v4'] else '未確定','; '.join(f"{s['start']:.2f}–{s['last_screenshot']:.2f}" for s in a['v4_sequences']),a['whole_v4']] for a in videos])
for a in videos:
 video_md+=f"\n## {a['id']} {a['title']}\n\n観測（V3継承）：{a.get('observed',a.get('camera',''))}\n\n推測（V3継承）：{a.get('implementation_inference',a.get('mapping',''))}\n\n"
 for n in a['v4_notes']:
  video_md+='V4追記：\n\n'+json.dumps(n,ensure_ascii=False,indent=2)+'\n\n'
video_md+='\n## AutoCineへの対応\n\n既存top/cinema_top/follow、手動FOV/yaw/zoom、カラー、6motion、既存badge/FXは基準出力へ使用可能。戦闘group-awareのwide維持・最後だけcutaway・次engage抑制は提案。人物/武器anchor、自由なmodel pose、白背景置換、外部CG intro、正確なbeat同期、画像からのbest shot採点は未実装扱い。ゲーム内skill発光を後処理FXと断定しない。V06の86–107連戦とV21の長いHerald戦をrecipe比較の根拠にし、killごとの寄りの連発を避ける。\n'
md('02_VIDEO20_FINAL_ANALYSIS_V4_JA.md',video_md)
md('03_FRAME652_NATIVE_AUDIT_V4_JA.md',f'''# 652原寸・12条件審査
652/652元PNG全体をoriginal detailで表示して目視しました。機械検査だけ/一覧縮小表示だけの件数ではありません。NATIVE_VISUAL_LOGの各ID・hash・メモが証拠です。追加で3人工背景上384px合成652/652を66ページに分けて目視しました。

12条件はFRAME652_TWELVE_CRITERIA_V4.json/CSVに各件別で保存。全件overall PARTIAL、完全12条件合格0。元のapproved1（083/a_simple_main）とreview651を維持。651のportrait_boxesがないため、fallback円が四角/八角等と合わない場合があります。左右は人工合成でkiller=Yasuo左、victim=Jinx右を確認し、実Replay解決を合格とはしません。

端接触74フラグは欠損確定ではありません。原本欠け、意図した装飾、微小alphaを分けます。原寸表示のRGB背景色だけで不透過と誤判定しないよう、083/palette_reference_06と086/dragonmancer_weakを再測定。透明画素率45.31%/68.01%、corner alpha0。後者max alpha254も記録。白い領域が意図したholeかは個別承認が必要です。

最終サイズ項目は384px crop fixtureの視認であり、動画全画面の実HUDや実人物を遮蔽しない保証ではありません。3背景はlight/dark/complex人工。生のLoL captureを使用した合格数0。

原本19制約は05番。素材hash/ID/番号/承認状態を変更しません。
''')
md('04_FX35_COMPOSITION_V4_JA.md','''# 35FX実合成
35×4形状×weak/strong×light/dark/complex=840組を実描画。各組に最大3段を配置。さらにFlash0.28と彩度0.75の診断合成840組。全35比較シートを目視。縮小タイル256×144なので元FXの全画素審査とは別です。V3原寸35確認を継承します。

動背景は35本、各1280×720/30fps/90frames。4形状を4象限に示し、前半weak、後半strong。全90frame decode35/35。弱0.40秒/強1.90秒の2時点シート全35を目視。人工HP線・名前・HUD・minimapとぶつかる配置を意図して可視化。実LoL映像ではありません。Riot公式static champion PNG（Yasuo/Jinx/Ahri/Zed、出典とhashはOFFICIAL_ICON_PROVENANCE）を使用。

観測：各組の左右顔は識別可能。強い交差光/縦装飾は3段の隣接行に合流しやすい。round083以外の肖像配置は暫定円fallbackで穴との不一致がある。Flash診断で明部の白wash/彩度減少。対策案はフレーム本体修正ではなく、検証済みportrait mask、最大3段間隔/安全領域、peak強度と表示時間、最後のkillだけclimaxという設定差分。全部新規提案、未採用。

全35の全時間を人手再生審査したとは記載しません。動画と比較画像を同梱し、実LoL HUD背景/全時間視認審査を残件にします。approved/review変更0。

追加：固定commitのリポジトリcamera_comparison_20261020.jpgからRED/BLUE各320×180の背景cropを取得し、960×540へ拡大。35×4形状×2強度×2参照背景=560合成を35シートにして全件目視。左右顔は見える一方、強Arcade/Dawn/Infernal等は段を縦につなぎ、背景の白beamとも競合。cropの低解像度/圧縮とHUD非表示のため、現在のLoL captureやHUD合格にはしません。offline mock_preview_offline.jpgも確認しましたが実captureの出典を確定できず、実LoL背景とは扱いません。参照出典/hashはFX_REPOSITORY_BACKGROUND_V4.json。
''')
md('05_SOURCE19_LIMITATIONS_V4_JA.md','''# 原本制約19件
8件はNo.004の完全原本不足、11件は039/083系のパレット参照制約。V3台帳のID/原本hash/crop/理由をSOURCE19_INHERITED_V4.jsonにそのまま継承。

追加探索はDocuments/Codexの画像/デザイン候補55,578パス。既知3原本の2コピーずつ6一致、新しいhash0。完全原本を発見したと扱いません。既知コピーの寸法は1536×1024、1536×1024、1448×1086。ユーザーの全ドライブや非公開クラウドを探索したという主張はありません。

閉じるためには完全な元編集データ/完全PNG、または「原本忠実再現ではなく独立再設計」とするユーザー判断が必要。想像の補完で忠実合格へ昇格しません。既知原本2コピーが同一hashであることは、不足が解消した証拠ではありません。
''')
geom=load(O/'MOTION_GEOMETRY_SUMMARY_V4.json')
md('06_MOTION6_VALIDATION_V4_JA.md',f'''# 6motion検証
instant / slide_left / slide_right / slide_up / slide_down / popを保持。popは16*exp(-18t)*cos(28t)の横減衰振動で、拡大に変更しません。

全652×6×3size×30/60=23,472シナリオ、active layer {geom['active_layer_samples']:,}サンプルを数式評価。5event、最大同時3。静止後端見切れ0条件、人工minimap bbox重なり{geom['scenarios_synthetic_minimap_hit']}条件。これはCPU export用固定幅384・step164の座標幾何です。mirrorの縮小スケーリングを再現した数値ではありません。

別に4形状×6motion×1920/1366/1280×30/60=144実際のmirror描画動画をencode/decode。全144で予定81/162frames一致。1080p60の24本を保存し、4時点シート24枚を目視。前/後は非表示、frameと左右portraitは同一overlayで動く。slideの画面外からの登場中の見切れは仕様で、静止中欠損とは別です。3非円形は仮portrait配置。

追加で同じ083をoriginal CPU export graphとmirrorで実描画。1080p可視bbox[1527,84,1866,200]が一致。1366ではexport[973,84,1312,200]対mirror[1086,60,1328,142]。1280ではexport[887,84,1226,200]対mirror[1018,56,1245,133]。変更前に出力の基準座標を決め、旧処理revisionを保持する必要があります。

全652×6を全pixel動画としてrenderした件数とは混同しません。GPU/CPU pixel差、実LoL/HUD、実際のvictim解決はNOT_RUN。144全decode成功は美術・LoL合格ではありません。
''')
md('07_CPU_FLASH_COMPATIBILITY_V4_JA.md','''# CPU Flash再現と互換候補
元_build_video_effect_filtersをASTで独立実行し、gray320×180/60fps/3秒で実測。8集合（single、two_short、two_long、three、dense、edges、empty、retimed）×3強度×旧/v2=48。旧empty helperのIndexError3件は直接呼出し再現で、通常jobの到達性とは別。残45decode成功。

旧式はenableに全eventを含める一方、指数減衰中心はevents[0][0]のみ。three強度.45ではgray255/127/127、v2は255/255/255。v2は振幅.25+.55kで旧.18+.65kと異なり、互換候補として却下。

v3は旧振幅を小数3桁で維持、旧窓を保持、各event中心のpulseの最大値を使用。emptyはno-op。8×3=24実測、single3強度で180frames各bit一致3/3。three強度.15は各event gray207（同梱v3比較画像）、強度.45では各event gray255です。v3の.15画像と旧/v2の.45画像は同一強度の比較ではなく、JSONの同強度行で照合してください。重複は加算して白飛びを増やさない。イベント時刻変換後はoutput時刻を一度だけ与え、seek切れ目を跨いで補間しない。

processing_revision欠落→legacy、明示新revisionだけv3。未知revisionは勝手にrewriteしない。旧project/goldenを保護し、new revisionの採用と製品修正は別PR・ユーザー判断。実LoL製品障害確定とは記載しません。実機は同一入力・旧単発・短間隔/長間隔連戦・速度変更・クリップ境界でT09を再実行。

強度注記の混同を防ぐため、FLASH_SAME_STRENGTH_0p15/0p45.jpgに旧/v2/v3を同じ入力・強度・8時点で並べました。全180frameのgray曲線はFLASH_SAME_STRENGTH_V4.json。0.15の旧/v3左右比較動画も保存。両シートを目視し、旧は後続pulse欠落、v2は.15の振幅が旧/v3と異なる、v3は単発の値と後続pulseを維持することを確認しました。

最終追加検証：v3のglobal union gateだけでは、前event窓が開いている間に未来eventの対称exp pulseが先に上昇します。.5/.6秒eventの34/60秒で、強度.15は旧150/v3 171、.45は旧169/v3 201、.9は旧196/v3 249。研究候補max_v4_causal_start_gateは各event前の項を0にして150/169/196へ戻しました。追加8×3=24条件、single旧bit一致3/3。FLASH_OVERLAP_CAUSAL_GATE.jpgとFLASH_GATED_REVISION_V4.jsonが証拠です。したがってv3を無条件の安全な修正として推奨せず、採用検討は因果gateも含む回帰後に行います。研究候補番号と製品processing revisionは同じ意味ではなく、製品側の自動変更は一切ありません。
''')
md('08_EXISTING_FX_ADDITIONAL_V4_JA.md','''# 既存FX追加検証
10FX×3sizeの初期30条件に加え、10×3強度(.15/.5/.9)×3sizeの90条件を1.2秒/36frames実処理。初期の保存10動画は18frames全decode。追加は出力raw36frame全取得。処理成功と画質合格を分けます。ハーネスd=.6構文失敗はd=0.6へ直し、失敗ログも保存。アプリ不具合には数えません。

Zoom Blurは元tmix weights1,2,1 scale4で人工映像がほぼ桃一色。without_tmixは空間標準偏差約122、tmix_only/constant_scaleは0、元はほぼ0。時間拡縮ではなく混合倍率を原因候補に絞れます。auto-normalize/scale.25候補は9条件で画像詳細が戻ることを比較。両候補は未採用、既存保存ID/見た目に無条件適用しません。FFmpegのscaleは重み付き和へ乗算する指定です。[公式tmix仕様](https://ffmpeg.org/ffmpeg-filters.html#tmix)。

focus_blur/vr_blur/sphere_blur/zoom_blurには1920×1080固定の中間/出力があり、1366/1280入力で寸法保持を破る条件をJSONに記録。最終jobでの再scale有無は追試が必要。

UI説明：radial_blur=時間方向残像（現行）、zoom_blur=ズーム揺動＋残像（旧版）、glint=輪郭強調＋明度/コントラスト、panel_wipe/stretch_wipe=黒から全面フェードイン、focus/VR/sphere=全体ぼかし、chroma_leak=キル窓RGBずれ、flash=全面明度pulse。真の放射状畳込み/局所glow/空間ワイプは新ID案として分ける。6名称を製品実装済みに書き換えない。
''')
md('09_CAMERA_AND_RECIPES_V4_JA.md','''# 自動カメラと6recipe
CAMERA_SOURCE_MATH48/48：旧10style×BLUE/REDの7時点、heading20条件、slowguard8条件でfinite/FOV/speed/dt・copy isolationを確認。値が有限でも画角が正しい保証ではありません。既存top/third等を削除しません。auto headingのORDER−12/CHAOS192、手動0/180は原文の暫定値であり、BLUE/RED実映像未合格。

独立ルール133/133：旧manual/fixed/full選択、approved不足fallback、除外/全除外例外、unknownmode、重複ID/assist除外、group間隔境界、manual/次戦闘不明/target死亡/visibility不足/side未承認でcutaway抑制、6recipe保存復元/手動保持。gap.5/1.5/3/5秒×4event列の感度例16。gap3秒・次戦闘余白1.5秒・可視性.9・最大3takeは提案値で製品既定ではありません。

設計：手動設定を最優先、戦闘group中wide、最後のkill後.4〜1.4秒の寄りは空白が検証できた場合だけ。unknownは高得点とせずnull、未承認side/対象逸失/地形外/強遮蔽/時刻map不正は候補不採用。全部不採用ならverified baseline。旧camera/TargetLock snapshotをtakeごとに保存・復元。fallbackで除外styleを復活させない。

ShotPlanはRESEARCH_CONTRACTS_V4.json。source patch/replay/event/target/team、legacy値、manual override、2段TimeMap、score/confidence/rejection、asset hash、revisionを保存。takeは最大3、同一入力/seed/costを記録。信頼度を画像品質の実証済み確率と表示しない。

SIX_RECIPES_V4.jsonに6案の既存/新規/保存/例外/差分を全件保持。Cinematic=wide＋最後だけ余韻、Impact=最後だけ任意pulse、Elegant=弱演出、Competitive=情報維持、Montage=groupと遷移、Low-load=単一take。V06/V21の連戦を根拠に、途中の寄り連発を抑える。適用はdraft→validate→差分表示→明示適用→immutable job snapshot。theme/view切替でcamera/project/previewを再生成しない。

レシピ比較は同一Replay・対象・scene・設定seedでbaseline+6出力、イベント前4/後2秒、速度map/kill/HUD/camera/FX/CPU/GPU/audioを保存し、T01/03/08/09/10/11/12を実機で審査。明確な入力不足は勝手に補わずfallback理由を表示。
''')
md('10_AUTOMATIC_QUALITY_QA_V4_JA.md','''# 自動画質QA拡充
14分類×正常/異常×30/60fps=56期待値一致。黒画面、静止、上下反転候補、frame落ち、音声欠落、AV差、過剰Flash、HUD/人物遮蔽、素材見切れ、死亡後gray、低体力赤、teleport、意図的暗転、正常cameraを含みます。

黒/静止は人工画像列、反転/遮蔽/ゲーム状態などの多くはfixtureのsemantic metadataを使用。映像認識器の精度56/56ではありません。警告が期待ラベルどおりかというルール検証です。実LoLのFP/FNは未測定。gray=死亡、red=低体力、white=FXを機械的に断定しない。意図した暗転/teleport区間や手動カメラも自動削除しない。

将来は警告中心、理由・区間・信頼度・既知ゲーム状態・ユーザーdismissを保存。自動再撮影/切捨ては既定off。比較fixtureに正常長回し、map切替、死亡、teleport、薄暗いskin、連続Flash、実遮蔽を追加し、人手annotationとのFP/FN/confusionを出すまで品質合格へ昇格禁止。
''')
md('11_GPU_AV_SYNC_V4_JA.md','''# GPU・encode・AV同期
Windowsネイティブでlibx264/h264_nvenc各2秒・5秒1080p60をencode、全120/300frames decode、4/4成功。CPU約.362/.748秒、NVENC約.813/1.157秒。この短い人工入力/CQとCRF非同等条件で速度/画質の優勝は決めません。

GPU FXは元GPUFullStage runtime probe、代替OpenCL avgblur、sandbox外の同条件再試行でdevice creation -12 Cannot allocate memory。NVENC成功でGPU FX成功に置き換えません。driver変更・インストール・UI29への介入なし。CPU代替で他研究は継続。

人工AVは30/60fps×.5/1/2x×PCM/AAC=12。white映像pulseと1kHz音をsource.5秒に配置。atempo/時刻変換後をvideo showinfo PTS、audio ashowinfo block PTS+sample indexで測定。単純frame-order offsetはAAC先頭時刻を落とすため旧診断値として残し、PTS再評価を採用。

10/12は±50ms以内、30fps2x PCM−58.791ms/AAC−58.625msは要確認。閾値立上り、frame量子化、atempo過渡を含み、サンプル聴取やLoL captureではありません。再検証は複数pulse/相互相関/先頭末尾/長尺driftを追加し、LoL専用録音を別試験。LoL音声合格0。実製品で固定補正58msを勝手に追加しない。
''')
md('12_T01_T14_STATE_V4_JA.md','# T01–T14状態\n\n製品全体PASS 0/14。PARTIAL/REPRODUCEDは研究証拠であって製品合格ではありません。各行の元V3入力/期待/手順/log要件をJSONに保持。\n\n'+table(['ID','試験','状態','今回の証拠','残件'],[[a['id'],a['title'],a['status'],a['execution_evidence'],a['remaining_reason']] for a in test['tests']]))
md('13_CODEX_EXISTING_FIX_INSTRUCTIONS_V4_JA.md','''# Codex向け既存問題の修正準備
まずUI29完成→ユーザーUI選択→既存70接続→Windows/LoL検証の順序を守る。以下は今すぐ製品変更する指示ではなく、採用後の独立PR仕様です。

## 1 CPU Flash
入力はFLASH_REVISION_RESULTSとflash_compat_revision.py。旧単発をbit保持、各後続eventで同じpulse、empty無害化。ただしhelper例外の通常到達性を先に調べる。window/丸め/速度mapを保護。旧revision欠落時legacy。single3強度+複数間隔+端+empty+retime全回帰。後続pulse欠落/旧single差分が出たら新revision無効化。

v3は短い重複窓で次event前のpulse項を漏らすことが追加再現できたため、そのまま採用しない。flash_gated_revision.pyのevent開始gate候補も比較する。単発bit一致だけでは複数eventの安全性を保証しない。

## 2 Zoom Blur
入力testsrc2/1.2秒30fps、元graph、tmix_only、without_tmix、constant_scale比較。scale4乗算で飽和する原因候補。研究候補auto0/quarter.25を評価するが、見た目変更なので新processing revisionで明示。真のradialblur追加とは別PR。明度/色/寸法/フレーム数を比較し、旧project goldenと一致するlegacyを保持。実job再現前にLoL不良確定と呼ばない。

## 3 mirror/export座標と固定解像度
PREVIEW_EXPORT_PARITYの3実描画を再現。非1080pで固定384exportに対しmirrorは384×width/1920。どの座標系を正式にするかは採用判断。レイヤのframe/peak/portraitを同じ変換へ、HUD safe areaも同じ空間へ。旧resolutionを無条件rewriteしない。FXの1920固定graphも最終chainで検査。

## 4 肖像枠・素材状態
651fallbackをapprovedにしない。元PNGやカタログstatusを上書きせず、検証済みgeometry/maskを別の明示更新として審査。killer/victim左右、hole、native alpha、最終寸法、3段/HUDを全件審査。19制約は元資料待ち。

## 共通回帰
旧37/原本89/Work687hash、70設定の型/単位/既定/未知field、manual camera/TargetLock、LoLプロセス音声required、GPUFXとencoder別、previewとexportの別command、job cancel/retry、保存/復元、theme状態保持。テスト失敗や例外原文は圧縮せず確認。RTK自動hookを入れず、本研究からクレジット削減を主張しない。
''')
md('14_NEW_FEATURE_SPEC_AND_PR_PLAN_V4_JA.md','''# 新機能仕様・19提案・PR分割
新提案はPROPOSAL19_ROADMAP_V4.jsonの19件を維持し、採用済み0。本体への実装0。ユーザーとChatGPTの採用判断後に着手。

'''+table(['順','PR範囲','合格条件','rollback'],[
['0','UI29候補を全維持し比較可能にする','ユーザー選択記録。勝手にE/A統一しない','候補画像/画面IDを削除しない'],
['1','採用UIの既存70adapterと設定保存','70行全command/model/ログ接続、unknownfield/手動値/テーマ保持、仮値の実行禁止','元UI/旧projectで開ける状態へ戻す'],
['2','既存CPU Flashとempty guard','採用済みrevisionのみ変更、単発bit回帰+全event検証','revision切替off/legacy維持'],
['3','Zoomと寸法/preview-export parity','同一入力3解像度のgolden、色/輪郭/時刻/旧保存互換','新graph/座標revisionoff'],
['4','素材geometry/FX safe area','ユーザー審査・元hash保持・37/89/652/35回帰','別metadata版を無効、承認状態保護'],
['5','Windows/LoL baseline実機T01–14','全14の証拠、BLUE/RED、TargetLock、録画、音声required、CPU/NVENC/GPU別','旧出力を比較用に残す、失敗新機能はoff'],
['6','event TimeMap/group ShotPlan','synthetic+実scene正解、manual優先、未知でbaseline、最大3takeは提案設定','保存planを残しbaselineで再出力'],
['7','6recipe draft/overrideとbest-shot optional','同一take比較、scoreとconfidence/不採用理由、未知値null','recipe適用差分を取消、元設定復元'],
['8','警告QA/checkpoint/audio/配布','誤警告率・長尺AV drift・失敗clipのみretry・PythonなしPC','QA自動変更off、checkpointから旧jobを保護'],
['9','真radial/glow/空間wipe/beat/CG','新IDと新規素材、負荷/著作権/同期を個別審査','旧IDへ代入せず新機能off']])+'''

各PRは独立fixture/期待値/実測/製品revision/変更前golden/rollback手順を添付。camera候補のtake最大3、group3秒、visibility.9は未検証の提案値。UI状態・テーマ変更はProjectState/preview/captureを再構築しない。LoLプロセス音声失敗をdesktop全音声に自動代替しない。選択UIの自動採用・素材自動承認は禁止。

'''+table(['提案ID','内容','難易度','依存','試験'],[[a['id'],a['title'],a['difficulty'],a['dependencies'],a['tests']] for a in road['proposals']]))
md('15_REMAINING_AND_WINDOWS_PACKAGE_V4_JA.md','''# 残件・実機検証パッケージ
## 必要な環境と入力
同patchで再生可能なROFL、LoL Replay API2999、BLUE/RED両陣営の対象とイベント正解、旧project/settings/golden出力、WGC/LoLプロセス音声helper、実GPU driver、採用UI記録、十分な空き容量。研究範囲Documents/Codexにrofl0、2999閉。勝手にLoL起動・camera POSTは行っていません。

## 実機手順
1. source commit/patch/OS/GPU/FFmpeg/helper/encoder/GPUFX能力、replay hashを記録。
2. 旧UIで同scene基準を保存。BLUE/RED各2scene、10camera、TargetLock on/off、左右逆位置、dash/壁/遮蔽/死亡/teleportを採取。
3. scan kill/assist/engage/no-killを正解照合。replay→capture→output TimeMapを保存しseek穴を跨がない。
4. 37badge/approved083/明示review候補の各motion・3段・HUD/HP、弱強FX、速度.5/1/2、30/60・3sizeを出力。651geometry未確定を見落とさない。
5. preview/厳密still/exportのbboxとevent同frameを比較。Flash単発/連戦/empty境界、Zoom飽和、固定1920graphを元revisionと比較。
6. CPU/NVENC/GPUFXを別に判定。GPUFX不可なら理由表示。LoL音声required時無音を成功にしない。他アプリ音混入を別音源で確認。
7. 長尺の先頭/中間/末尾でAV drift、cancel/retry、失敗clipだけ再出力、checkpoint整合、PythonなしPC配布を検証。
8. input/events/time_maps/ffmpeg_args/run_anonymized/output_probe/human_review/resultをT01–14別に保管し、証拠のある項目だけPASSへ。

## 未確定件数と担当
動画7/20の2通知未確定、音声20/20未聴取、全編精査17/20未完（3はほぼ全編の粗いサンプリング）。追加のブラウザー観察はWorkで継続可能ですが、HUDがないものを通知確認済みにはできません。
portrait geometry651、原本制約19、全652の実HUD審査、全35FXの実LoL/全時間人手審査、GPU FX parity、実LoL録画・音声・全14製品判定は未完。ユーザーの元資料/採用判断、Codexの製品統合、Windows/LoL入力が必要。
AV2条件とZoom/Flash/縮小mirror差は独立再現済み、製品jobへは未追試。未知値や再現ハーネス例外を実LoL障害確定にしない。

## 試した代替
原寸はテーマ別分割652・3背景66ページ、FX4形状人工背景/公式icon、144実pixel動画と全652幾何、GPUは別OpenCL filterとsandbox外再試行、AVはPCM/AAC/PTS再測定、動画は10未確定すべて別区間追加、原本は既知コピー探索55,578。全件合格の代替にはしていません。

## 再実行
research_scriptsは実行した研究用原文。Python/Pillow/numpy、FFmpeg、固定BASEのread-only core、元687素材・catalog・official icons、V3 JSONを必要とします。lab_commonのR/W/O/V3/OLD/S/FFを自分の研究用コピーに合わせる。製品checkoutへ出力しない。source_input_manifestでhash一致を確認し、flash_fx_lab→flash_compat_revision→fx_temporal_expanded→zoom_candidate、camera_math_qa/camera_recipe_rules、composition_motionを実行。ブラウザーobserverは当該computer-use実行環境専用で一般Pythonだけでは再生しません。元動画のダウンロードはしていません。
''')
md('16_CHATGPT_HANDOFF_V4.txt',f'''LoL AutoCine V4研究の実行結果です。UI未選定・採用未決定を維持。本体/UI29/承認状態は未変更。
652/652フレームの原寸全体を目視し、native pixel/3人工背景も全件確認。12条件完全合格0、portrait geometry651は仮、原本19制約は追加探索で解消せず。
35FX×4形状×2強度×3背景840＋Flash/grade840、動背景35本全decode。6motion144実描画条件全decode、652×6×3size×2fps=23,472幾何条件。
動画元20作品を維持、未確定10作品を追加再生。2明確通知は10→13/20。V06/V08/V21はほぼ全編を粗くサンプリング、全作品全編ではない。音声聴取0。
Flash旧/v2 48＋互換v3 24。v2は振幅非互換で却下、v3単発3/3bit一致。Zoom tmix scale4飽和、1366/1280mirror/export素材座標差も独立実描画で再現。
Flash v3の短間隔重複で未来pulseが早く現れる点も追加確認し、event開始gate候補24条件を比較、旧単発3/3bit一致と先行上昇抑制を確認。v3をそのまま採用しないことを明記しました。
既存FX追加90、カメラ数学48/48、独立ルール133/133、警告fixture56/56、CPU/NVENC4encode成功。GPUFXはOpenCL -12で不可。人工AV12の10は±50ms内、30fps2x2条件は約−58.7ms要確認。LoL音声/製品合格にはしていない。
1251保護hash一致。70機能台帳/19提案/6recipe/ShotPlan/PR分割・合格rollback/実機パッケージを保存。製品全体T01–14 PASS0。
既存camera参照背景にも35FXの560合成を追加して全35シート確認。Template90項目と既存操作50種を70機能へ対応付け、既存設定/SceneProject保存復元119試験も成功。これはGUI/LoL合格ではありません。
順序：UI29完成→ユーザーUI選択→既存70統合→Windows/LoL検証→ユーザーとChatGPTが研究採用→採用新機能実装。
保存先：研究ブランチwork/autocine-integrated-research-20261022、LoL_AutoCine/research/integrated_20261022/v4_final_20261025/。コミットとZIP照合はSAVE_RECEIPT/保存検証を参照。Work研究を全機能製品完成と解釈しないでください。
''')
md('17_REPRODUCTION_AND_PROTECTION_V4_JA.md',f'''# 再現・保護・証拠境界
{common}

基準source {BASE}。最新UI観測 {UI}。V3観測から764変更、core/assets変更0（観測時点差分）。これはUI29が機能接続完了した証拠ではありません。

保護再検査source438+素材687+原本89+badge37=1251/1251hash一致。元カタログもsource hashに含む。コードimportはdont_write_bytecode、研究コピーへROOTを読取切替し、製品patchはありません。遠隔GitHubは新V4prefixだけ、V1–3/UI29不変をtree差分で別検査します。

正本はJSONの実測・graph・stderr・source commit。人手確認ログは原寸652/FX35/背景652/phase24等の範囲を明示。encode/decode件数は人手全フレーム審査件数ではありません。人工test PASSは製品全体PASSではありません。

スクリプトは研究補助。再実行は15番で列挙した入力と環境が必要。巨大な元652/35/89/37を重複コピーせず、hash/出典を保存しています。Riot公式static iconと合成表示は研究検証用。第三者モンタージュ動画/スクリーンショットはGitHub/ZIPに転載せず、URL/時刻/観測文/プレイヤー状態JSONのみ同梱。

RTKは概要用途に限定、重要原文・例外・失敗・BLUE/RED・承認条件を生のまま確認。自動hook追加0、Work全体のクレジット削減は未実証。
''')
# Copy exact research scripts and input manifests, never product mutation.
scripts=O/'research_scripts';scripts.mkdir(exist_ok=True)
for p in W.glob('*.py'):shutil.copy2(p,scripts/p.name)
for p in W.glob('*.mjs'):shutil.copy2(p,scripts/p.name)
for src,dst in [(OLD/'source_hashes.json','SOURCE_INPUT_MANIFEST_V4.json'),(V3/'ASSET_FULL_QA_V2.json','ASSET_INPUT_MANIFEST_V4.json'),(V3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json','ORIGINAL89_INPUT_MANIFEST_V4.json'),(V3/'LEGACY_BADGE_PROTECTION_V3.json','LEGACY37_INPUT_MANIFEST_V4.json')]:shutil.copy2(src,O/dst)
save('REMAINING_STATUS_V4.json',{'date':DATE,'original_detail_viewed':652,'twelve_criteria_full_pass':0,'provisional_portrait_geometry':651,'source_constraints':19,'video_two_notifications':13,'video_unresolved':7,'audio_heard':0,'whole_work_near_complete_sampled':3,'product_T01_T14_full_pass':0,'GPU_FX':'BLOCKED','LoL_runtime':'BLOCKED_NO_REPLAY','native_encode':4,'UI_adopted':False,'research_proposals_adopted':0,'work_can_continue':['more long-video playback observations','full human temporal review of artificial videos','new source/image supplied fidelity checking','additional artificial test refinement'],'needs_external':['source19 complete originals or explicit independent design choice','verified651 portrait geometry/approval','LoL patch-matched ROFL and runningReplay2999','working OpenCL device','user UI/adoption decision','Codex product integration']})

# Self-contained Japanese report viewer. No external JS/CSS or product controls.
import runpy
runpy.run_path(str(W/'settings_bindings.py'),run_name='__main__')
shutil.copy2(W/'settings_bindings.py',scripts/'settings_bindings.py')
docs=sorted(O.glob('0*.md'))+sorted(O.glob('1*.md'))+[O/'16_CHATGPT_HANDOFF_V4.txt']
def rendered(text):
 def inline(t):
  return re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2">\1</a>',html.escape(t))
 out=[];ls=text.splitlines();i=0
 while i<len(ls):
  line=ls[i]
  if not line.strip():i+=1;continue
  if line.startswith('#'):
   n=min(4,len(line)-len(line.lstrip('#')));out.append(f'<h{n}>'+inline(line.lstrip('# ').strip())+f'</h{n}>');i+=1
  elif line.startswith('|'):
   t=[]
   while i<len(ls) and ls[i].startswith('|'):
    cells=[z.strip() for z in ls[i].strip('|').split('|')]
    if not all(re.fullmatch(r'[-: ]+',z) for z in cells):t.append(cells)
    i+=1
   out.append('<div class="scroll"><table>'+''.join('<tr>'+''.join(('<th>' if j==0 else '<td>')+inline(c)+('</th>' if j==0 else '</td>') for c in row)+'</tr>' for j,row in enumerate(t))+'</table></div>')
  else:
   p=[]
   while i<len(ls) and ls[i].strip() and not ls[i].startswith(('#','|')):p.append(ls[i]);i+=1
   out.append('<p class="prose">'+'<br>'.join(inline(z) for z in p)+'</p>')
 return ''.join(out)
cards=''.join(f'<details><summary>{html.escape(p.read_text("utf-8").splitlines()[0].lstrip("# "))}<a href="{p.name}" download>原文</a></summary><article>{rendered(p.read_text("utf-8"))}</article></details>' for p in docs)
gallery=''.join(f'<details><summary>{label}（{len(list((O/folder).glob("*.jpg")))}枚）</summary><div class="gallery">'+''.join(f'<figure><a href="{p.relative_to(O).as_posix()}"><img loading="lazy" src="{p.relative_to(O).as_posix()}" alt="{html.escape(p.stem)}"></a><figcaption>{html.escape(p.stem)}</figcaption></figure>' for p in sorted((O/folder).glob('*.jpg')))+'</div></details>' for folder,label in [('frame_backgrounds','652フレーム・3人工背景'),('fx_composition','35FX・形状/強度/背景/Flash比較'),('fx_moving','35FX・動背景2時点'),('fx_repository_background','35FX・既存camera参照背景'),('motion','6motion・4形状の4時点')])
rows=''.join(f'<tr data-search="{html.escape(a["id"]+a["name"])}"><td>{a["id"]}</td><td>{html.escape(a["name"])}</td><td>{html.escape(a["integration_tests"])}</td><td>接続未実行</td></tr>' for a in ft)
video_links=''.join(f'<li><a href="{p.relative_to(O).as_posix()}">{html.escape(p.relative_to(O).as_posix())}</a></li>' for p in sorted(O.rglob('*.mp4')))
index='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>LoL AutoCine V4研究</title><style>
:root{color-scheme:light dark;--bg:#f0f3f7;--panel:#fff;--ink:#182638;--line:#8798ac;--blue:#14599c}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 "Yu Gothic UI",Meiryo,sans-serif}header{background:var(--panel);border-bottom:1px solid var(--line);padding:24px max(24px,calc((100% - 1280px)/2))}main{max-width:1280px;margin:auto;padding:24px}h1{font-size:30px;margin:0}h2{font-size:25px}a{color:var(--blue)}button,input,select{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:7px;background:var(--panel);color:var(--ink)}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.metric,details,.notice{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px;margin:14px 0}.metric strong{font-size:30px;display:block}.notice{border-left:6px solid var(--blue)}summary{cursor:pointer;font-weight:bold}summary a{float:right;font-size:14px}.prose{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere}article{padding-top:12px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:15px}figure{margin:0}img{max-width:100%;height:auto}figcaption{font-size:14px;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;border-bottom:1px solid var(--line);text-align:left}.scroll{overflow:auto}li{overflow-wrap:anywhere}body.dark{--bg:#19212c;--panel:#242f3d;--ink:#e3eaf5;--line:#8091a7;--blue:#8fc4ff}@media(prefers-color-scheme:dark){body.system{--bg:#19212c;--panel:#242f3d;--ink:#e3eaf5;--line:#8091a7;--blue:#8fc4ff}}
</style><body class="system"><header><h1>LoL AutoCine｜V4研究結果</h1><p>原寸審査・映像観察・人工試験・実装引き継ぎ　2026年10月25日</p><label>配色 <select id="theme"><option value="system">Windowsに合わせる</option><option value="light">ライト</option><option value="dark">ダーク</option></select></label></header><main><div class="notice">UIは未選定。製品本体の変更・素材の正式承認はありません。人工試験の成功と実LoL合格を分けて表示しています。</div><div class="metrics"><div class="metric"><strong>652 / 652</strong>原寸全体を目視<br>12条件完全合格：0</div><div class="metric"><strong>13 / 20</strong>2件以上の明確なキル通知<br>音声聴取：0</div><div class="metric"><strong>144 条件</strong>6motion実描画・全decode<br>GPU/実LoLは未合格</div><div class="metric"><strong>0 / 14</strong>製品全体の完全PASS<br>研究証拠は各台帳参照</div></div><h2>資料とダウンロード</h2><p><a href="16_CHATGPT_HANDOFF_V4.txt">ChatGPTへ送る報告</a> ・ <a href="FRAME652_TWELVE_CRITERIA_V4.csv">652素材台帳</a> ・ <a href="ALL_70_FEATURE_INTEGRATION_V4.csv">70機能台帳</a> ・ <a href="T01_T14_STATE_V4.json">14試験台帳</a></p>'''+cards+'<h2>合成比較画像</h2><p>画像を押すと大きく開きます。人工背景・暫定portrait配置のため正式承認ではありません。</p>'+gallery+'<h2>70機能の接続確認表</h2><input id="filter" placeholder="機能名またはIDを検索" aria-label="機能検索"><div class="scroll"><table><thead><tr><th>ID</th><th>機能</th><th>対応試験</th><th>実機状態</th></tr></thead><tbody>'+rows+'</tbody></table></div><h2>人工検証動画</h2><p>リンク先で再生・保存できます。ブラウザーにより保存動作になります。元YouTube映像は同梱していません。</p><ul>'+video_links+'''</ul><p>保存commit・ZIP SHAは保存レシートを参照。</p></main><script>const t=document.getElementById('theme');try{t.value=localStorage.getItem('autocine-v4-report-theme')||'system'}catch{}function apply(){document.body.className=t.value;try{localStorage.setItem('autocine-v4-report-theme',t.value)}catch{}}apply();t.onchange=apply;document.getElementById('filter').oninput=e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('tr[data-search]').forEach(r=>r.hidden=!r.dataset.search.toLowerCase().includes(q))};</script></body></html>'''
(O/'index.html').write_text(index,'utf-8')
md('README.md','''# LoL AutoCine V4
ダウンロード後index.htmlを開いてください。資料01–17、JSON/CSV台帳、比較画像、人工動画、実行スクリプトを同梱。製品実装/素材承認は含みません。UI未選定、実LoL未合格です。

GitHubの単一ファイル制限のため、全体ZIPはローカル、GitHubには同じ内容を複数の通常ZIPへ分割して保存する場合があります。分割ZIPはすべて同一フォルダに展開してください。各ZIPは独立して開けます。マニフェストと保存レシートが正本です。
''')
print(json.dumps({'videos':len(videos),'v4_additional':sum(bool(a['v4_sequences']) for a in videos),'native':len(native),'features':len(ft),'tests':len(test['tests']),'docs':len(docs),'source_notes':len(notes)}))
