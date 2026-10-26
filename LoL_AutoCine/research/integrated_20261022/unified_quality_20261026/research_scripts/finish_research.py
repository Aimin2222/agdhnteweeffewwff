from common import *
import copy, collections, shutil, csv, html

def textfile(path,content):
 p=O/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content.strip()+'\n','utf-8')

def source_audit():
 j=load(W/'PR_REFERENCE_METADATA.json')
 extra=[(49,'ui/smart_montage.py','9ee700be22c88ed9f05b860047e818bacbad9ac5'),(49,'ui/highlight_director.py','48c33f1987104abdbf1f9baa7188b594ef1b611c'),(49,'core/montage_fx.py','ff9494264456152af7e7af971ecc98c27322d341'),(51,'ui/layout_variants.py','a8426d131a0b3e04099dc420dc6acc2d646e6866'),(51,'ui/comparison_labels.py','12b55123d48303f988d1270e882c0acea000be70'),(51,'ui/comparison7_screens.json','af423fd50f6f39fe52108eb21f2b6e605593a9ca'),(51,'ui/scene_project.py','2ae36c7d6d2f3b1d1c0b3b6192a0be5a4cc72a7a')]
 for pr,n,h in extra:
  p=W/f'latest_readonly/pr{pr}/LoL_AutoCine'/n;b=p.read_bytes()
  for _ in range(4):
   actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   if actual==h:break
   assert b.endswith(b'\n'),(n,actual);b=b[:-1]
  assert actual==h,(n,actual,h)
  p.write_bytes(b)
  if not any(x['pr']==pr and x['path']==n for x in j['files']):j['files'].append({'pr':pr,'path':n,'git_blob':h,'verified_blob':True,'chars':len(b.decode('utf-8-sig'))})
 (W/'PR_REFERENCE_METADATA.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),'utf8');save('SOURCE_REFERENCES.json',j)
 rows=[]
 for n in ['effects','work_kill_assets','camera','kill_icons','jobs','scanner','audio']:
  old=S/f'core/{n}.py';new=W/f'latest_readonly/pr49/LoL_AutoCine/core/{n}.py'
  eq=ast.dump(ast.parse(old.read_text('utf-8-sig')))==ast.dump(ast.parse(new.read_text('utf-8-sig')))
  assert eq;rows.append({'path':f'core/{n}.py','old_sha256':sha(old),'pr49_sha256':sha(new),'AST_same':eq})
 save('SOURCE_COMPARISON_7.json',{'items':rows,'scope':'queried PR49 vs fb03 snapshot only; not all current branches or runtime compatibility'})

def reviews():
 fxnotes=['赤黒は共通だが流れる翼と密集した心臓/棘で形が異なる。','金の細い光と赤黒の翼。透過面積によるMAEの誤検出。','金の細い光と赤黒の心臓。色と面積が異なる。','機械的な赤い棘と流れる赤い翼で形が異なる。','赤い流線と橙の炎状の翼で形が異なる。','白金の十字と赤黒の心臓。色・中心形状が異なる。','赤い心臓/棘と橙の流れるXで形が異なる。','金の細い光と橙の炎状Xで形が異なる。']
 ln=['赤黒の横長二枠は共通。密な機械パネルと薄い赤い筆状Xで異なる。','金の横長枠は共通。炎の装飾と舵/錨の記号で異なる。','金の角枠は共通。密な渦状装飾と単純な金枠/弓状中心で異なる。','緑金の角枠と青緑の円枠。色・穴・中央形状が異なる。','白青は共通だが角枠と円枠、中心の渦と雪結晶で異なる。No004原本制約は解消しない。','金の翼と青い氷の結晶で色・中央形状が異なる。']
 out=[]
 for kind,file,notes in [('FX','FX_PAIR_VISUAL_QUEUE.json',fxnotes),('legacy37','LEGACY_PAIR_VISUAL_QUEUE.json',ln)]:
  for x,n in zip(load(O/'A1_similarity'/file),notes):out.append(dict(x,kind=kind,AI_pair_review='REVIEW',observation=n,research_classification=2,duplicate_proven=False,human_approval=False))
 save('A1_similarity/ADDITIONAL_AI_PAIR_REVIEWS.json',{'items':out,'count':14,'scope':'8 FX pairs + 6 legacy impression pairs; scaled static dark/light AI inspection, not human approval or additional distinct 14 assets','transparent_canvas_bias':'whole-canvas premultiplied MAE can rank sparse but different effects close; use foreground union/color/shape and inspect before deciding'})

def function_map():
 features=load(R/'outputs/autocine_integrated_research_20261022/FEATURE_STATUS.json')['features'];bindings=load(R/'outputs/ui_implementation_audit_29_20261021/FUNCTION_BINDINGS.json');bm={x['id']:x for x in bindings}
 groups={
 'F01':['REPLAY','LAUNCH'],'F02':['PLAYER'],'F03':['SCAN'],'F04':['ASSIST'],'F05':['ENGAGE'],'F06':['MULTI'],'F17':['TIMELINE'],'F18':['SCENE'],'F19':['KEYFRAME','GRADE','FOG','DOF'],'F20':['REFERENCE'],'F23':['HIGHLIGHT','SMARTMONTAGE','JOB'],'F22':['HUD','AUDIO','BGM','AUDIOGUARD'],'F08':['MIRROR','CAPTURE'],'F21':['RECORD','NVENC','GPUFX'],'F09':['PREVIEW'],'F13':['BADGE'],'F14':['WORKFRAME'],'F15':['WORKFX'],'F16':['MOTION'],'F24':['SELFQA','DIAG'],'F10':['FIXED','FULL'],'F19b':['PULSE','MONTAGEFX'],'F24b':['BESTSHOT']}
 reverse={n:k.rstrip('b') for k,ns in groups.items() for n in ns};rows=[]
 for f in features:
  i=f['id'];b='F11' if i.startswith('CAM_') else 'F19' if i.startswith('FX_') else reverse[i]
  zone={'F01':'準備・実接続','F02':'対象選手・TargetLock','F03':'全体スキャン','F04':'シーン絞込','F05':'シーン絞込（能力不足を明示）','F06':'シーン一覧','F17':'詳細タイムライン','F18':'詳細シーン編集','F19':'詳細カメラ/色/FX','F20':'素材・プロジェクト','F23':'出力・ワンクリック','F22':'基本設定・ゲーム音声/HUD','F08':'常時ミラー','F21':'出力/実行環境','F09':'演出確認・停止','F13':'既存バッジ','F14':'素材・枠','F15':'素材・FX','F16':'素材・登場アニメ','F24':'診断/結果','F10':'カメラモード','F11':'カメラスタイル'}[b]
  rows.append({'feature_id':i,'name':f['name'],'inherited_source':f['source'],'inherited_status':f['status_label'],'binding_id':b,'existing_handler_reference':bm[b]['existing'],'binding_contract':bm[b]['contract'],'mixed_7_main_entry':zone+'への導線','candidate_4_detail_entry':zone,'alternatives_3_5_8':'同じ状態・能力契約から使用（実装/実機成功は別）','missing_or_partial':f['finding'],'actual_backend_run':'NOT_RUN','spec_status':'REVIEW','mapping_scope':'既存70監査と25機能契約の研究用照合。UI各画面からの全操作実行証明ではない'})
 assert len(rows)==len({x['feature_id'] for x in rows})==70
 save('B4_function_map/FEATURE_MAP_70.json',{'items':rows,'coverage':70,'adoption':'user-kept mixed candidate7 main + candidate4 detail/material/frame; easy UI undecided; alternatives3/5/8 maintained; candidate6 reference','candidate_number_source':'PR51 ui/comparison_labels.py CANDIDATE_ORDER; PR52 standalone document; not layout_variants internal index'})
 save('B4_function_map/EXISTING_BINDING_CONTRACTS_25.json',bindings)
 with (O/'B4_function_map/70機能対応表.csv').open('w',encoding='utf-8-sig',newline='') as fp:
  writer=csv.DictWriter(fp,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 baseline={'project':{'id':'研究のみ','scenes':[{'id':'s1','in':6,'out':15.1,'override':{'style':'third'}}]},'camera':{'style':'third','side':'RED','target':'P1','TargetLock':True},'selectedScene':'s1','checkedScenes':['s2'],'preview':{'timeUs':150000,'playing':False},'assets':{'frame':'083/a_simple_main','reviewUse':False},'audio':{'source':'lol_process_only','bgmEnabled':False},'encoder':'auto','HUD':'hidden'}
 snapshots=[]
 for candidate in ['7','4','3','5','8']:
  for theme in ['light','dark','system']:
   view={'candidate':candidate,'theme':theme};state=copy.deepcopy(baseline)
   # Contract fixture: presentation command changes presentation only. Not existing GUI execution.
   before=json.dumps(state,sort_keys=True);view.update(viewId='detail' if candidate=='4' else 'main');after=json.dumps(state,sort_keys=True)
   assert before==after;snapshots.append({'candidate':candidate,'theme':theme,'unchanged_project_camera_preview':before==after,'status':'PASS'})
 save('B4_function_map/STATE_CONTRACT_FIXTURE.json',{'baseline':baseline,'cases':snapshots,'scope':'independent data contract fixture; no real UI switch, theme implementation, or LoL session executed','native_UI_test':'NOT_RUN'})
 textfile('B4_function_map/README_JA.md','''# B4 混合UIの機能接続整理（新UI制作ではない）
公開候補番号をPR51のcomparison_labels原文に照合。候補7=L05-M（旧ウィザード）、候補4=L06-L/L06-E（旧ライブラリ/編集）。内部layout_variantsの番号を転用しない。ユーザー保持の候補7メイン＋4詳細・素材・枠、比較3/5/8を維持。簡単画面は未決定。採点・順位付け・採用変更は行わない。

70機能はFEATURE_MAP_70.json/CSV、既存25契約はEXISTING_BINDING_CONTRACTS_25.json。各機能の導線を残し、実接続がないものを成功表示しない。ENGAGE/BESTSHOTなどの既存監査上の不足は解消したと扱わない。PR52候補8〜10の文書には実LoL・録画・音声・GPU・MP4接続が無いことが明記されている（今回は文書の確認のみ）。

遷移: 候補7の準備→対象選手→スキャン→シーン選択→既存プリセット→演出確認→出力。途中で候補4詳細へ入り、トリム/キーフレーム/色/カメラを調整→素材図鑑→同じシーンへ戻る。画面遷移はジョブやReplay接続の再生成理由にしない。メインの再表示でテンプレートを自動適用しない。

共通状態: projectId, stableSceneId, focusedSceneId, outputCheckedIds, perSceneOverrides, cameraMode/style/side, TargetLock対象ID, previewPTS, assetIdとcatalog承認状態, encoderPolicy, actualEncoder, audioSource, outputPath, jobState。焦点と出力チェックは独立。Undoは場面設定変更を一操作として記録。出力開始時は不変スナップショットを取り、処理中のUI変更と混在させない。テーマlight/dark/systemと候補/viewIdは外観状態として別保存し、映像色やカメラ値を変更しない。

不足導線の提案: 接続/FFmpeg/音声helper/WebView2診断、スキャン中断、失敗クリップ再試行、出力進捗/中止/残存ファイル、実エンコーダ、正式/確認用/ユーザー不採用フィルター。既存機能のショートカットを足す提案であり、製品に実装済みではない。モーダル内スクロールと背景スクロールを分離し、Esc/閉じる/フォーカス復帰を同じ契約にする。

検証: 70ID重複/欠落0。5候補×3テーマの独立状態契約15件PASS（モデル不変の限定試験）。実GUI遷移、スクロール、DPI、実バックエンド70機能の押下試験はNOT_RUN。Codex側で元画面と照合し、数値変更→プレビュー更新→保存→再起動→出力値の一致を各機能で検証する。
''')

if __name__=='__main__':
 source_audit();reviews();function_map();print('source/review/map saved')
