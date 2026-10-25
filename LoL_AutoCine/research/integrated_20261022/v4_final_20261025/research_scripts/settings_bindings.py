from lab_common import *
import csv
source=S/'effects.py';text=source.read_text('utf-8-sig');lines=text.splitlines();cls=next(x for x in ast.parse(text).body if isinstance(x,ast.ClassDef) and x.name=='Template')
fields=[]
for x in cls.body:
 if not isinstance(x,ast.AnnAssign):continue
 fields.append({'name':x.target.id,'type':ast.unparse(x.annotation),'default_expression':ast.unparse(x.value),'source_line':x.lineno,'source_text':lines[x.lineno-1].strip(),'source':f'LoL_AutoCine/core/effects.py#L{x.lineno}'})
raw=(S.parent/'ui/audit29_runtime.py').read_text('utf-8-sig');tree=ast.parse(raw);actions=[]
for x in ast.walk(tree):
 if isinstance(x,ast.Compare) and isinstance(x.left,ast.Name) and x.left.id=='action' and len(x.comparators)==1 and isinstance(x.comparators[0],ast.Constant):
  actions.append({'action':x.comparators[0].value,'line':x.lineno})
save('TEMPLATE_FIELDS_AND_RUNTIME_ACTIONS_V4.json',{'source_commit':'fb03e0390805125fc063f4599af6c2541a653abf','template_fields':fields,'runtime_actions':sorted(actions,key=lambda a:a['line']),'scope':'AST original declaration/action names, not live UI pass','invalid_template_module_correction':'Template resides in core/effects.py, not core/templates.py; V3 proposal filenames are candidate locations, not verified paths'})
features=load(O/'ALL_70_FEATURE_INTEGRATION_V4.json');commoncam=['style','intensity','camera_side','cam_height','dist_scale','third_elev','third_dist','third_yaw','motion_arc','motion_dolly','motion_profile','auto_director_strength','camera_control_mode','camera_auto_excluded','camera_auto_qa_approved']
groups={
'REPLAY':([],['connect']),'LAUNCH':([],['open_replay','prepare']),'PLAYER':([],['target_lock']),
'SCAN':(['pre','post','merge_multikill'],['scan']),'ASSIST':([],['event_mode']),'MULTI':(['merge_multikill','pre','post'],['scan']),
'SCENE':(['scene_keyframes','pre','post'],['scene_save','scene_undo','scene_redo','project_export','project_import']),'TIMELINE':(['pre','post','scene_keyframes'],['select_scene','jump_selected','check_scene']),
'KEYFRAME':(['scene_keyframes'],['native_editor_zone']),'HIGHLIGHT':(['smart_highlight_enabled','smart_highlight_style','smart_composition','highlight_pulse'],['export_smart']),
'SMARTMONTAGE':(['smart_montage'],['export_smart']),'HUD':(['hide_hud','keep_champion_bars'],['hud']),
'MIRROR':(['capture_fps'],['mirror_start','mirror_stop']),'CAPTURE':(['capture_fps'],['mirror_start','export_selected']),
'RECORD':(['capture_fps','fps','game_audio'],['export_selected','cancel_job']),'JOB':(['fps','encoder_policy'],['export_checked','export_all','cancel_job','output_folder']),
'AUDIO':(['game_audio','game_volume'],['game_audio','native_settings']),'AUDIOGUARD':(['game_audio'],['native_settings']),
'BGM':(['bgm_path','bgm_volume','bpm'],['native_editor_zone']),'NVENC':(['encoder_policy'],['encoder_policy']),
'GPUFX':([],['native_settings']),'GRADE':(['grade','grade_strength','temperature','contrast','vignette','grain','bloom','bars','exposure','vibrance','lut_path','curve_enabled','curve_points'],['native_editor_zone']),
'FOG':(['fog_enabled','fog_preset','fog_strength'],['native_editor_zone']),'DOF':([a['name'] for a in fields if a['name'].startswith('dof_')],['native_editor_zone']),
'PULSE':(['highlight_pulse'],['native_editor_zone']),'BADGE':([a['name'] for a in fields if a['name'].startswith(('kill_icon_','kill_frame_','kill_glow_','kill_mark_','kill_sparkle_','kill_stack_'))],['frame','native_settings']),
'WORKFRAME':(['work_kill_frame_id','work_kill_review','kill_icon_position','kill_icon_scale','kill_icon_duration','kill_icon_opacity','kill_stack_gap'],['frame','work_gallery','work_settings']),
'WORKFX':(['work_kill_effect_id','work_kill_review','work_kill_strength'],['work_settings','effect_strength']),
'MOTION':(['kill_icon_motion'],['motion']),'REFERENCE':(['reference_dna','reference_sources','template_origin'],['native_settings']),
'PREVIEW':(['video_effects'],['fx_enabled','preview_play','preview_stop','native_settings']),
'MONTAGEFX':(['montage_fx','transition'],['native_editor_zone']),'SELFQA':([],['native_settings']),'DIAG':([],['native_settings']),
'FIXED':(commoncam,['camera_mode','camera_side','camera_style','camera_number']),
'FULL':(commoncam,['camera_mode','camera_side','camera_style','camera_number']),
'ENGAGE':([],[]),'BESTSHOT':([],[])}
fn={a['name']:a for a in fields};an={a['action']:a for a in actions}
for a in features['features']:
 id=a['id']
 if id.startswith('FX_'):names=['video_effects'];cmd=['native_editor_zone'];effect=id[3:]
 elif id.startswith('CAM_'):names=commoncam;cmd=['camera_style','camera_mode','camera_side','camera_number'];effect=None
 else:names,cmd=groups[id];effect=None
 assert set(names)<=set(fn);assert set(cmd)<=set(an)
 a['template_fields_verified']=[fn[n] for n in names];a['runtime_action_declarations']=[an[n] for n in cmd];a['effect_dict_key']=effect
 a['binding_boundary']='Existing action only proves declared dispatcher route, not complete UI/function test. native_settings/native_editor_zone are fallback routes, not a dedicated direct control. Non-template state requires original App model.'
 a['ui_implementation_state']='NOT_RUN_RUNTIME'
 if id in ['ENGAGE','BESTSHOT']:a['binding_boundary']='NEW_PROPOSAL_NOT_CONNECTED; do not invent existing command or change status'
save('ALL_70_FEATURE_INTEGRATION_V4.json',features)
rows=[{'id':a['id'],'name':a['name'],'template_fields':','.join(z['name'] for z in a['template_fields_verified']),'runtime_actions':','.join(z['action'] for z in a['runtime_action_declarations']),'effect_key':a['effect_dict_key'] or '', 'source':a['source'],'runtime':'NOT_RUN','boundary':a['binding_boundary']} for a in features['features']]
with (O/'FEATURE70_BINDINGS_V4.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
doc='# 70機能・設定フィールド・旧操作の保持\n\ncore/effects.pyのTemplate宣言をASTで読み、型/既定式/行番号/注釈を全保存。ui/audit29_runtime.pyの宣言actionと70監査項目を対応付けました。専用操作がない項目をnative_settingsへ案内することと、専用操作が実装済みであることを混同しません。ENGAGE/BESTSHOTは未実装提案を維持。\n\n'
doc+='|ID|既存Templateキー|宣言済みaction（実動未検証）|\n|---|---|---|\n'+'\n'.join(f"|{a['id']}|{a['template_fields']}|{a['runtime_actions']}|" for a in rows)
doc+='\n\n## UIから失われやすい項目\n\nscene_keyframes/merge_multikill/対象slot/checked scene順序、manual yaw/zoom/FOV単位とcamera_side、旧10style・除外・陣営QA、game_audio requiredとgame/BGM volume、encoder_policyとGPUFXの別状態、curve_points/LUT/fog/DOF形状と半径/feather、旧37色/glow/mark/sparkle、kill_stack_gap/位置/scale/秒/opacity/motion、Work frame/effect/review/strength、reference metadata、montage_fxとtransition、capture_fpsと最終fps。簡単↔詳細、タブ/theme/画面ID変更、保存再起動で値を消さない。\n\n## 接続検査\n\n各70行で、元設定→新画面表示→変更→model→保存→再開→job snapshot→最終出力→ログを往復照合。declared dispatcherだけで接続合格にしない。current adapterのoutput_fpsは60/144許可であり、研究の30fps人工試験をUI30fps対応済みとはしない。camera_numberは有限値/範囲も原文どおり追試。旧Templateのcenter_mosaic退役処理など、既存移行例外まで未知field一般論で復活させない。\n\nTemplateの実際の位置はcore/effects.pyです。V3提案のcore/templates.py等は想定変更先に過ぎず、存在確認済み実装先ではないことを訂正します。採用直前に最新headの変更原文を再確認してください。\n'
(O/'18_UI70_BINDINGS_AND_LOST_SETTINGS_V4_JA.md').write_text(doc,'utf-8')
print(json.dumps({'template_fields':len(fields),'actions':len(actions),'feature_bindings':len(rows)}))
