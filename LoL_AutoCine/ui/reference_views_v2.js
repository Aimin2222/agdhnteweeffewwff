/* Work LD/LN visual contract adapted to the real AutoCine UI29 runtime.
   No discontinued research demo code or synthetic match state is imported. */
(() => {
  'use strict';
  const token=window.AUTOCINE_TOKEN, variant=window.AUTOCINE_VARIANT;
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const url=p=>`${p}${p.includes('?')?'&':'?'}token=${encodeURIComponent(token)}`;
  const labels={main:'メイン',easy:'かんたん',detail:'詳細編集',camera:'カメラ',curve:'カーブ',color:'色調整',material:'素材',export:'出力'};
  let state=null,view='main',selectedKey=-1,selectedScene=null,refreshing=false,frameSeq=0,frameTag=null,lastFrameRequest=0;
  const frameTimes=[];
  function button(label,command,data={},extra=''){return `<button type="button" data-action="${command}" data-data='${esc(JSON.stringify(data))}' ${extra}>${label}</button>`;}
  function section(title,content,extra=''){return `<section class="section ${extra}"><h3>${title}</h3>${content}</section>`;}
  function note(message){$('#message').textContent=message;}
  async function snapshot(){
    if(refreshing)return;refreshing=true;
    try{const response=await fetch(url('/api/state'),{cache:'no-store'});if(!response.ok)throw Error('状態を取得できません');
      state=await response.json();
      if(!$('#inspector-body').contains(document.activeElement))render();
    }catch(error){note(error.message);}finally{refreshing=false;}
  }
  async function action(command,data={}){
    try{const response=await fetch(url('/api/action'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:command,data})});
      const result=await response.json();if(!response.ok)throw Error(result.error||'操作に失敗しました');
      state=result;render();note(`${command} を実行しました。実状態を確認してください。`);
    }catch(error){note(`${command}: ${error.message}`);}
  }
  function route(to){location.assign(url(to==='candidate3'?'/ui/T-A-M':`/ui3/reference/${to}`));}
  function numberControl(label,key,min,max,step,value,kind='camera_number',suffix=''){
    const val=Number(value??0);
    return `<div class="number-control"><div class="control-caption"><label for="num-${kind}-${key}">${label}</label><small>${suffix}</small></div><div class="number-fields"><input type="range" min="${min}" max="${max}" step="${step}" value="${val}" data-pair="${kind}:${key}" aria-label="${label} スライダー"><input id="num-${kind}-${key}" type="number" min="${min}" max="${max}" step="${step}" value="${val}" data-pair="${kind}:${key}" data-kind="${kind}" data-key="${key}" data-camera="${kind==='camera_number'?key:''}" aria-label="${label} 数値"></div></div>`;
  }
  function modeButtons(){return `<div class="choice-grid">${[['manual','既存・手動'],['fixed_auto','固定＋自動構図'],['full_auto','フルオート']].map(([key,label])=>button(label,'camera_mode',{value:key},state.camera.mode===({manual:'従来の手動カメラ',fixed_auto:'固定視点＋自動構図補正',full_auto:'フルオートシネマ'}[key])?'class="active"':'')).join('')}</div>`;}
  function cameraControls(){
    const c=state.camera,v=c.values||{};
    return section('カメラ制御 <small>設定デモではなく実App状態</small>',modeButtons()+`<p class="note">採用済みの三人称カメラ計算は変更しません。実カメラ送信はLoL接続時に確認してください。</p>`)+
      section('対象サイド <small>TargetLockは別設定</small>',`<div class="choice-grid">${['auto','BLUE','RED'].map(key=>button(key==='auto'?'自動':key,'camera_side',{value:key},c.side_key===key?'class="active"':'')).join('')}</div>`)+
      section('視点スタイル',`<select id="camera-style" aria-label="視点スタイル">${['third','third_cinema','geo_aim','cinema','fps','orbit','lolnam_cinema','follow','cinema_top','top'].map(key=>`<option value="${key}" ${c.style_key===key?'selected':''}>${key}</option>`).join('')}</select>`)+
      section('画角とポジション',numberControl('距離','third_dist',500,1400,1,v.third_dist,'camera_number','ゲーム内単位')+
        numberControl('高さ','cam_height',0,900,1,v.cam_height,'camera_number','ゲーム内単位')+
        numberControl('回転角','third_yaw',-180,180,.5,v.third_y,'camera_number','°')+
        numberControl('回り込み','motion_arc',0,45,.5,v.motion_arc,'camera_number','°')+
        numberControl('ドリー','motion_dolly',0,15,.5,v.motion_dolly,'camera_number','%')+
        `<p class="note">Work画像の絶対FOV入力は、この既存カメラ設定APIと別です。値を偽装しません。</p>`);
  }
  function keyControls(){
    const list=state.keyframes||[],scene=state.scenes.find(x=>x.selected);
    if(!scene)return section('キーフレーム・FOV',`<p class="status-note">実シーンを選択すると、既存シーンエディタのキーを編集できます。</p>${button('リプレイを開く','open_replay')}`);
    if(selectedKey>=list.length)selectedKey=-1;
    const current=selectedKey<0?{time:0,yaw:0,zoom:0,fov:0}:list[selectedKey];
    return section('キーフレーム・FOV',`<p class="note">キル瞬間＝0秒。FOVは絶対値ではなく、既存カメラへの補正量（−15°～＋15°）です。</p>
      <div class="key-list">${list.map((frame,index)=>`<button type="button" data-key-index="${index}" class="${selectedKey===index?'active':''}">${Number(frame.time).toFixed(1)}s　FOV ${Number(frame.fov)>=0?'+':''}${frame.fov}°</button>`).join('')||'<small>このシーンのキーはまだありません</small>'}</div>
      <div class="key-fields"><label>時刻（キル相対秒）<input id="key-time" type="number" min="-15" max="15" step="0.1" value="${current.time}"></label><label>FOV補正（°）<input id="key-fov" type="number" min="-15" max="15" step="0.5" value="${current.fov}"></label></div>
      <div class="key-fields"><label>回転補正（°）<input id="key-yaw" type="number" min="-70" max="70" step="0.5" value="${current.yaw}"></label><label>寄り補正（%）<input id="key-zoom" type="number" min="-30" max="30" step="0.5" value="${current.zoom}"></label></div>
      <div class="inline-actions"><button type="button" id="key-upsert">＋ 追加／更新</button><button type="button" id="key-remove" ${selectedKey<0?'disabled':''}>選択キーを削除</button></div>`)+
      section('保存と確認',`<label class="form-row">補間方式 <select disabled><option>既存の連続曲線</option></select></label><p class="note">linear／hold／自由Bezier接線は未対応。画像の選択肢を成功扱いしません。</p>
        <div class="inline-actions">${button('このシーンに保存','scene_save')}${button('実LoLで動きを確認','keyframe_preview')}${button('元に戻す','scene_undo')}</div>`);
  }
  function frameControls(){
    const f=state.frame,cards=f.ui3_cards||f.cards||[], motions=[['instant','一気に表示'],['slide_left','左から'],['slide_right','右から'],['slide_up','下から'],['slide_down','上から'],['pop','ポップ']];
    return section('キルフレーム <small>実素材カタログ</small>',`<div class="asset-grid">${cards.map(item=>`<button type="button" class="asset-card ${f.id===item.id?'active':''}" data-action="frame" data-data='${esc(JSON.stringify({id:item.id}))}'><img src="${url(`/api/asset/${encodeURIComponent(item.id)}`)}" alt="${esc(item.label)}の実素材"><strong>${esc(item.label)}</strong><small>${item.status==='approved'?'正式合格':'確認用'}</small></button>`).join('')}</div><p class="note">この画像は実カタログの素材。承認状態は各カードに表示しています。</p>${button('素材図鑑の全候補','work_gallery')} ${button('既存37バッジ','legacy_frame_gallery')}`)+
      section('同名FX・強さ',`<p>現在の同名FX：${esc(f.effect_id||'なし')}</p><div class="choice-grid">${button('控えめ','effect_strength',{value:'weak'},f.strength==='weak'?'class="active"':'')}${button('強め','effect_strength',{value:'strong'},f.strength==='strong'?'class="active"':'')}</div>${button('FX詳細設定','work_settings')}`)+
      section('登場アニメ 6種類',`<div class="choice-grid motion-grid">${motions.map(([key,label])=>button(label,'motion',{value:key})).join('')}</div>`);
  }
  function colorControls(){
    const fx=state.scene_fx||{override:false,values:{}},v=fx.values;
    return section('映像の色・FX <small>選択シーン</small>',`<p class="note">ここは実シーンFX値です。Work画像の露出・彩度・LUTとは別の処理です。</p><label><input id="fx-override" type="checkbox" ${fx.override?'checked':''} ${state.selected_scene_index===null?'disabled':''}> このシーンだけ色・FXを上書き</label>`)+
      section('既存の映像処理',numberControl('色温度','temperature',-1,1,.05,v.temperature,'scene_fx_number','−1～＋1')+
        numberControl('ブルーム','bloom',0,1,.05,v.bloom,'scene_fx_number','0～1')+
        numberControl('Focus Blur','focus_blur',0,1,.05,v.focus_blur,'scene_fx_number','0～1')+
        numberControl('DOFぼかし','dof_blur',0,20,.5,v.dof_blur,'scene_fx_number','0～20')+
        numberControl('キル瞬間の強調','highlight_pulse',0,1,.05,v.highlight_pulse,'scene_fx_number','0～1')+
        `<p class="note">露出・彩度・LUT・比較スプリットはこの画面から実処理へ未接続です。</p><div class="inline-actions">${button('このシーンに保存','scene_save')}${button('既存の色設定を開く','native_editor_zone',{zone:'color'})}</div>`);
  }
  function exportControls(){
    const o=state.output,qa=state.qa.selftest;
    return section('出力する前に設定を確認',`<p class="status-note">${o.busy?'書き出し中':'実LoL・GPU・音声・MP4はこの試験で未検証'}</p>${button('プロジェクトを保存','project_export',{},'class="primary"')} ${button('プロジェクトを開く','project_import')}`)+
      section('動画設定',`<label class="form-row">フレームレート <select id="fps"><option value="60" ${String(o.fps).startsWith('60')?'selected':''}>60 fps</option><option value="144" ${String(o.fps).startsWith('144')?'selected':''}>144 fps</option></select></label>
        <label class="form-row">エンコーダ方針 <select id="encoder"><option value="auto" ${String(o.encoder_policy).startsWith('自動')?'selected':''}>自動（NVENC優先）</option><option value="gpu" ${String(o.encoder_policy).startsWith('GPU')?'selected':''}>GPU優先</option><option value="cpu" ${String(o.encoder_policy).startsWith('CPU')?'selected':''}>CPU優先</option></select></label>
        <label class="form-row">LoLゲーム音のみ <input id="game-audio" type="checkbox" ${o.game_audio?'checked':''}></label><label class="form-row">HUD <select id="hud"><option value="hidden" ${o.hud==='hidden'?'selected':''}>非表示</option><option value="full" ${o.hud==='full'?'selected':''}>表示</option></select></label>
        <p class="note">出力先：${esc(o.path)}</p>${button('出力先を選ぶ','output_folder')}`)+
      section('実動画を作成',`<div class="stack">${button('チェックしたシーンで作成','export_checked',{},'class="primary"')}${button('選択シーンで作成','export_selected')}${button('書き出し停止','cancel_job')}</div>`)+
      section('結果・診断',`<p class="note">自動QA：${esc(qa.status)} ${qa.passed??''}件通過</p>${button('自動QAを実行','automatic_qa')} ${button('診断ログを開く','diagnostics')}`);
  }
  function prepareControls(){
    const r=state.replay;return section('リプレイと対象',`<p class="status-note">${r.connected?`接続中・${r.player_count}人`:'LoL未接続。試合データ待ちです。'}</p><div class="stack">${button('リプレイを開く','open_replay')}${button('準備','prepare')}${button('試合全体スキャン','scan')}</div><label class="form-row">TargetLock対象 <select id="target-slot"><option value="">未選択</option>${r.players.map(p=>`<option value="${Number(p.slot)}" ${r.target_slot===p.slot?'selected':''}>${esc(p.side)} ${esc(p.name)}</option>`).join('')}</select></label>`);
  }
  function inspector(){
    const c=state.camera,selected=state.scenes.find(x=>x.selected);
    if(view==='main')return section('初心者はここから',`<h2>ワンクリックで<br>見せ場を、作品へ。</h2><p class="note">スキャンした実シーンを選び、カメラと演出を確認します。</p><button type="button" class="primary" data-view="easy">かんたん編集へ</button>`)+
      section('このショットの設定',`<div class="grid2"><div class="metric"><strong>${esc(c.side_key||'自動')}</strong><small>対象サイド</small></div><div class="metric"><strong>—</strong><small>絶対FOV・未接続</small></div><div class="metric"><strong>${state.checked_count}</strong><small>出力対象</small></div><div class="metric"><strong>${state.output.game_audio?'有効':'無効'}</strong><small>LoLゲーム音のみ</small></div></div>`)+
      section('仕上げを選ぶ',`<div class="stack"><button data-view="camera">カメラ・構図を確認</button><button data-view="material">キルフレーム・FXを選ぶ</button><button data-view="detail">詳細編集へ</button></div>`)+prepareControls();
    if(view==='easy')return section('かんたん',`<p class="status-note">3つだけ決めて、実シーンを確認します。</p><button data-view="detail">細かく調整する</button>`)+
      section('01 カメラ',modeButtons())+section('02 雰囲気',`<p class="note">色プリセットは映像処理への対応が未確認です。既存の実FXを調整できます。</p><button data-view="color">色・FXを調整</button>`)+
      section('03 キル演出',`<button data-view="material">キルフレームと同名FXを選ぶ</button> ${button('演出を確認','preview_play')}`);
    if(view==='camera')return cameraControls()+prepareControls();
    if(view==='detail'||view==='curve')return section(view==='curve'?'カーブ':'詳細編集',`<p class="note">選択シーン：${selected?`${esc(selected.killer)} → ${esc(selected.victim)}`:'なし'}。下のトラックとキーを操作できます。</p>`)+keyControls()+section('関連する調整',`<div class="inline-actions"><button data-view="camera">カメラ</button><button data-view="color">色・FX</button><button data-view="material">素材</button></div>`);
    if(view==='color')return colorControls();
    if(view==='material')return frameControls();
    if(view==='export')return exportControls();
    return '';
  }
  function render(){
    if(!state)return;
    const inspectorScroll=$('#inspector-body').scrollTop;
    const replay=state.replay,scenes=state.scenes,selected=scenes.find(x=>x.selected);
    if(selectedScene!==state.selected_scene_index){selectedKey=-1;selectedScene=state.selected_scene_index;}
    $('#connection').textContent=replay.connected?'LoL 接続中':'LoL 未接続';
    $('#scene-count').textContent=String(scenes.length);
    $('#scan-note').textContent=state.scan.status||'未スキャン';
    $('#scene-title').textContent=selected?`${Number(selected.time).toFixed(2)}秒のシーン`:'シーン未選択';
    $('#inspector-title').textContent=labels[view];
    $('#inspector-status').textContent=replay.connected?'実状態を表示':'未接続';
    $('#scene-list').innerHTML=scenes.map(x=>`<div class="scene-card ${x.selected?'selected':''}"><input type="checkbox" data-check="${x.index}" ${x.checked?'checked':''} aria-label="シーン${x.index+1}を書き出す"><div data-scene="${x.index}" tabindex="0" role="button"><span class="time">${String(x.index+1).padStart(2,'0')}　${Number(x.time).toFixed(2)}秒</span><strong>${esc(x.multikill>1?`${x.multikill}連続キル`:x.role==='assist'?'アシスト':'キル')}</strong><small>${esc(x.killer)} → ${esc(x.victim)}</small></div></div>`).join('')||'<p class="empty-note">実シーンは未取得です。リプレイ接続後にスキャンしてください。</p>';
    $('#shot-strip').innerHTML=(scenes.map(x=>`<button data-action="select_scene" data-data='${esc(JSON.stringify({index:x.index}))}' class="${x.selected?'active':''}">${x.index+1}　${Number(x.time).toFixed(1)}秒</button>`).join('')||'<small>ショット未取得</small>')+
      (variant==='ln'?'<button type="button" id="open-shot-checks">☑ 対象を選ぶ</button>':'');
    $('#shot-check-list').innerHTML=scenes.map(x=>`<label class="shot-check-row"><input type="checkbox" data-check="${x.index}" ${x.checked?'checked':''}> ${Number(x.time).toFixed(1)}秒　${esc(x.role==='assist'?'アシスト':'キル')}　${esc(x.killer)} → ${esc(x.victim)}</label>`).join('')||'<p>実シーンは未取得です。スキャン後に選べます。</p>';
    $('#inspector-body').innerHTML=inspector();
    $('#inspector-body').scrollTop=inspectorScroll;
    $$('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===view));
    $('#theme').value=state.workspace.theme;
    document.body.classList.toggle('dark',state.workspace.theme==='dark'||state.workspace.theme==='system'&&matchMedia('(prefers-color-scheme:dark)').matches);
    $('#trim-pre').value=state.trim.pre;$('#trim-post').value=state.trim.post;
    $('#preview-fps').textContent=`ミラー実測 ${state.preview.measured_fps||'—'} fps / 画面 ${frameTimes.length||'—'} fps`;
    $('#timeline-summary').textContent=`${scenes.length} シーン / ${state.keyframes.length} キー / 選択 ${selected?selected.index+1:'なし'}`;
    drawTimeline();
    if(!state.preview.mirror_requested){$('#mirror-image').hidden=true;$('#preview-offline').hidden=false;$('#preview-offline').innerHTML=replay.connected?'ミラー停止中<br><small>開始すると実映像を表示します</small>':'LoL未接続・実ミラー待機中<br><small>見本映像ではありません</small>';frameTag=null;frameTimes.length=0;}
  }
  function drawTimeline(){
    const keys=state.keyframes||[],before=Number(state.trim.pre)||4,after=Number(state.trim.post)||3,span=before+after;
    const ticks=Array.from({length:8},(_,index)=>`<span class="timeline-tick" style="left:${index/7*100}%">${(index/7*span-before).toFixed(1)}s</span>`).join('');
    $('#timeline-tracks').innerHTML=`<div class="timeline-ticks">${ticks}</div>`+[0,1,2].map(row=>`<div class="track-row">${row===0?keys.map((frame,index)=>`<button type="button" class="key-marker ${selectedKey===index?'active':''}" style="left:${Math.max(1,Math.min(99,(Number(frame.time)+before)/span*100))}%" data-key-index="${index}" title="${frame.time}s / FOV補正 ${frame.fov}°"></button>`).join(''):row===1?'<span class="track-reference">Yaw・寄りは同じ既存キーに保存</span>':'<span class="track-reference">演出の時刻は既存シーン設定を参照</span>'}</div>`).join('');
  }
  async function frame(){
    if(!state?.preview.mirror_requested||document.hidden){setTimeout(frame,200);return;}
    const hz=Math.max(1,Math.min(144,parseInt(state.preview.target_hz,10)||60)),wait=1000/hz-(performance.now()-lastFrameRequest);
    if(wait>1){setTimeout(()=>requestAnimationFrame(frame),wait);return;}
    lastFrameRequest=performance.now();
    try{const response=await fetch(url(`/api/frame.jpg?seq=${++frameSeq}`),{cache:'no-store',headers:frameTag?{'If-None-Match':frameTag}:{}});
      if(response.status===304){requestAnimationFrame(frame);return;}
      if(!response.ok)throw Error('frame unavailable');
      const image=$('#mirror-image'),old=image.dataset.objectUrl,next=URL.createObjectURL(await response.blob());image.src=next;image.dataset.objectUrl=next;
      await image.decode();image.hidden=false;$('#preview-offline').hidden=true;if(old)URL.revokeObjectURL(old);frameTag=response.headers.get('ETag');
      const now=performance.now();frameTimes.push(now);while(frameTimes.length&&frameTimes[0]<now-1000)frameTimes.shift();
      $('#preview-fps').textContent=`ミラー実測 ${state.preview.measured_fps||'—'} fps / 画面 ${frameTimes.length} fps`;
    }catch{frameTag=null;frameTimes.length=0;if($('#mirror-image').hidden){$('#preview-offline').hidden=false;$('#preview-offline').textContent='実ミラーフレーム待機中';}}
    requestAnimationFrame(frame);
  }
  document.addEventListener('click',event=>{
    const target=event.target,routeButton=target.closest('[data-route]');if(routeButton){route(routeButton.dataset.route);return;}
    if(target.id==='open-shot-checks'){$('#shot-check-dialog').showModal();return;}
    if(target.id==='shot-check-close'){$('#shot-check-dialog').close();return;}
    if(target.id==='help-open'){$('#help-dialog').showModal();return;}
    if(target.id==='help-close'){$('#help-dialog').close();return;}
    const key=target.closest('[data-key-index]');if(key){selectedKey=Number(key.dataset.keyIndex);render();return;}
    if(target.id==='key-upsert'){
      const data={index:selectedKey<0?null:selectedKey};for(const field of ['time','fov','yaw','zoom'])data[field]=Number($(`#key-${field}`).value);
      action('keyframe_upsert',data);return;
    }
    if(target.id==='key-remove'){action('keyframe_remove',{index:selectedKey});selectedKey=-1;return;}
    const tab=target.closest('[data-view]');if(tab){view=tab.dataset.view;render();return;}
    const scene=target.closest('[data-scene]');if(scene){action('select_scene',{index:Number(scene.dataset.scene)});return;}
    const command=target.closest('[data-action]');if(command){let data={};try{data=JSON.parse(command.dataset.data||'{}');}catch{}action(command.dataset.action,data);}
  });
  document.addEventListener('input',event=>{const target=event.target;if(!target.dataset.pair)return;const mate=$$(`[data-pair="${target.dataset.pair}"]`).find(x=>x!==target);if(mate)mate.value=target.value;});
  document.addEventListener('change',event=>{
    const target=event.target;
    if(target.dataset.check!==undefined){action('check_scene',{index:Number(target.dataset.check),checked:target.checked});return;}
    if(target.dataset.kind){action(target.dataset.kind,{key:target.dataset.key,value:Number(target.value)});return;}
    if(target.dataset.pair){const [kind,key]=target.dataset.pair.split(':');action(kind,{key,value:Number(target.value)});return;}
    if(target.id==='fx-override')action('scene_fx_override',{value:target.checked});
    else if(target.id==='camera-style')action('camera_style',{value:target.value});
    else if(target.id==='target-slot'&&target.value)action('target_lock',{slot:Number(target.value)});
    else if(target.id==='theme')action('theme',{value:target.value});
    else if(target.id==='trim-pre'||target.id==='trim-post')action('trim',{key:target.id==='trim-pre'?'pre':'post',value:Number(target.value)});
    else if(target.id==='fps')action('output_fps',{value:Number(target.value)});
    else if(target.id==='encoder')action('encoder_policy',{value:target.value});
    else if(target.id==='game-audio')action('game_audio',{value:target.checked});
    else if(target.id==='hud')action('hud',{value:target.value});
  });
  document.addEventListener('keydown',event=>{if(event.key==='Enter'&&event.target.matches('[data-scene]'))action('select_scene',{index:Number(event.target.dataset.scene)});});
  matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>state&&render());
  snapshot();setInterval(snapshot,1100);requestAnimationFrame(frame);
})();
