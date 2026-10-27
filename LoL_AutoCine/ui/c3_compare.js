/* C3 comparison controls use the same authenticated App adapter as T-A-M. */
(() => {
  'use strict';
  const token = window.AUTOCINE_TOKEN;
  const variant = window.AUTOCINE_C3_VARIANT;
  const url = path => `${path}?token=${encodeURIComponent(token)}`;
  const $ = selector => document.querySelector(selector);
  let current = null;
  let tab = variant === 'p' ? 'camera' : 'easy';
  let drawer = null;
  let draft = null;
  let lastFrameTag = null;
  let toastTimer = null;
  const cameraStyles = [
    ['三人称斜め後ろ','third_cinema'],['三人称','third'],['Geo Aim','geo_aim'],
    ['シネマ','cinema'],['FPS','fps'],['Orbit','orbit'],
    ['Lolnamシネマ','lolnam_cinema'],['Follow','follow'],
    ['俯瞰シネマ','cinema_top'],['俯瞰','top']
  ];
  const modeNames = {manual:'従来の手動カメラ',fixed_auto:'固定視点＋自動構図補正',full_auto:'フルオートシネマ'};
  function esc(value) { return String(value ?? '').replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function toast(text) { const el=$('#toast'); el.textContent=text; el.hidden=false;
    clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,6000); }
  async function call(action, data={}) {
    const response=await fetch(url('/api/action'),{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action,data})});
    const result=await response.json();
    if(!response.ok)throw new Error(result.error || `${action} に失敗しました`);
    current=result;render();return result;
  }
  async function refresh() { const response=await fetch(url('/api/state'),{cache:'no-store'});
    if(!response.ok)throw new Error('状態を取得できません');current=await response.json();render(); }
  function run(action,data={}) { call(action,data).catch(e=>toast(e.message)); }
  function route(target) { location.assign(url(target)); }
  function time(seconds) { const n=Math.max(0,Number(seconds)||0);
    return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(Math.floor(n%60)).padStart(2,'0')}`; }
  function applyTheme(name) { const dark=matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme=name==='system'?(dark?'dark':'light'):name; }
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{
    if(current?.workspace.theme==='system')applyTheme('system'); });
  function render() {
    if(!current)return;
    applyTheme(current.workspace.theme);
    $('#connection').textContent=current.replay.connected ?
      `接続中・${current.replay.player_count}人 / TargetLock ${current.replay.target_slot ?? '未選択'}` : 'LoL未接続。リプレイを開くか準備状態を確認してください。';
    $('#connection-pill').textContent=current.replay.connected?'接続中':'未接続';
    $('#replay-file').textContent=current.replay.connected?'接続中の試合（ファイル名取得待ち）':'接続待ち';
    $('#scan-status').textContent=`${current.scan.status} / ${current.scenes.length}件 / 出力チェック ${current.checked_count}件`;
    $('#fps').textContent=current.preview.mirror_requested ?
      `実測 ${current.preview.measured_fps} fps / 目標 ${current.preview.target_hz}` : '実測 — fps';
    $('#footer-state').textContent=current.output.busy?'動画作成中':'実LoL総合QA NOT_RUN';
    const players=$('#players');players.replaceChildren();
    if(!current.replay.players.length)players.textContent='接続後に10人を表示します。';
    for(const p of current.replay.players){const b=document.createElement('button');
      b.className=`player${p.slot===current.replay.target_slot?' selected':''}`;
      b.textContent=`${p.side}　${p.champion}　${p.name}`;
      b.onclick=()=>run('target_lock',{slot:p.slot});players.append(b);}
    const scenes=$('#scenes');scenes.replaceChildren();
    if(!current.scenes.length)scenes.textContent='スキャン後にシーンを表示します。';
    for(const s of current.scenes){const row=document.createElement('div');
      row.className=`scene${s.selected?' selected':''}`;
      const check=document.createElement('input');check.type='checkbox';check.checked=s.checked;
      check.setAttribute('aria-label',`${time(s.time)} を出力対象にする`);
      check.onchange=()=>run('check_scene',{index:s.index,checked:check.checked});
      const focus=document.createElement('button');focus.style.cssText='border:0;background:transparent;text-align:left;flex:1;padding:0';
      focus.innerHTML=`<strong>${esc(time(s.time))}　${s.role==='assist'?'アシスト':'キル'}</strong><span class="meta">${esc(s.side||'サイド不明')}　${esc(s.killer)}</span>`;
      focus.onclick=()=>run('select_scene',{index:s.index});row.append(check,focus);scenes.append(row);}
    $('#selected-scene').textContent=(()=>{const s=current.scenes.find(x=>x.selected);
      return s?`選択：${time(s.time)} ${s.role} / ${s.side||'サイド不明'}`:'選択：なし';})();
    document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('selected',b.dataset.tab===tab));
    renderMiniTimeline();
    renderEditor();
  }
  function renderMiniTimeline(){
    const scenes=current.scenes;
    const duration=Math.max(1,Number(current.scan.duration)||0,...scenes.map(s=>Number(s.time)||0));
    const lane=$('#mini-events');lane.replaceChildren();
    if(!scenes.length){const empty=document.createElement('span');empty.className='mini-empty';
      empty.textContent='スキャン後にシーンを表示';lane.append(empty);}
    for(const scene of scenes){const point=document.createElement('button');
      point.className=`mini-point${scene.selected?' selected':''}`;
      point.style.left=`${Math.max(1,Math.min(99,100*Number(scene.time)/duration))}%`;
      point.dataset.scene=String(scene.index);
      point.title=`${time(scene.time)} ${scene.role==='assist'?'アシスト':'キル'} / ${scene.checked?'出力対象':'出力対象外'}`;
      point.setAttribute('aria-label',`${time(scene.time)} のシーンを選択`);lane.append(point);}
    for(const key of ['pre','post']){const input=$(`#trim-${key}`);
      if(document.activeElement!==input)input.value=String(current.trim?.[key]??(key==='pre'?4:3));}
  }
  function card(title,body){return `<section class="editcard"><h3>${title}</h3>${body}</section>`;}
  function modeButtons(){return Object.entries(modeNames).map(([id,label])=>
    `<button data-camera-mode="${id}" class="${current.camera.mode===label?'selected':''}">${label}</button>`).join('');}
  function renderEditor(){const d=current;const selected=d.scenes.find(x=>x.selected);
    document.body.classList.toggle('detail-view',tab==='detail');
    let html='';
    if(tab==='easy' && variant==='s'){
      const frameCards=d.frame.cards.slice(0,3);
      html=`<div class="shotcards">${Object.entries(modeNames).map(([id,label])=>
        `<button class="shot ${d.camera.mode===label?'selectedcard':''}" data-camera-mode="${id}"><span class="dot"></span>${label}</button>`).join('')}
        ${frameCards.map(x=>`<button class="shot ${d.frame.id===x.id?'selectedcard':''}" data-frame-direct="${esc(x.id)}">
          <img src="${url('/api/asset/'+encodeURIComponent(x.id))}" alt=""><span>${esc(x.label)}</span></button>`).join('')}
        <button class="shot fx ${d.frame.strength==='weak'?'selectedcard':''}" data-effect-strength="weak"><span class="dot"></span>控えめFX</button>
        <button class="shot fx ${d.frame.strength==='strong'?'selectedcard':''}" data-effect-strength="strong"><span class="dot"></span>強いFX</button>
        <button class="shot fx" data-zone="fx" data-action="native_editor_zone"><span class="dot"></span>FX詳細</button></div>
        <div class="editoractions"><button data-drawer="camera">カメラ設定</button><button data-drawer="asset">素材をもっと見る</button><button data-drawer="review">作成内容を確認</button></div>`;
    }else if(tab==='easy'){
      html=`<div class="editgrid">
      ${card('カメラ',`<p class="muted">選択したシーンの見せ方</p><div class="choicegrid">${modeButtons()}</div><button data-drawer="camera">カメラを詳しく設定</button>`)}
      ${card('キルフレーム・素材',`<p class="muted">現在：${esc(d.frame.id||'未選択')} / ${esc(d.frame.effect_id||'FX未選択')}</p><div class="editoractions"><button data-drawer="asset">画像で選ぶ</button><button data-action="work_gallery">Work素材図鑑</button></div>`)}
      ${card('色・FXと出力',`<p class="muted">確認用素材は正式合格と区別します。</p><div class="editoractions"><button data-zone="fx" data-action="native_editor_zone">FX詳細</button><button data-zone="color" data-action="native_editor_zone">色調整</button><button data-drawer="review">作成内容を確認</button></div>`)}
      </div>`;
    }else if(tab==='detail'){
      const keys=d.keyframes||[];
      const times=keys.map(k=>Number(k.time)||0);
      const lo=Math.min(0,...times),hi=Math.max(10,...times),range=Math.max(1,hi-lo);
      const dots=keys.map(k=>`<button class="keydot" style="left:${Math.max(1,Math.min(98,100*((Number(k.time)||0)-lo)/range))}%;top:${Math.max(7,Math.min(86,50-(Number(k.fov)||0)*1.5))}%" title="${esc(k.time)}秒 / 相対FOV ${esc(k.fov)}°" data-zone="scene" data-action="native_editor_zone" aria-label="${esc(k.time)}秒のキーを既存エディタで編集"></button>`).join('');
      html=`<div class="curve-layout"><div class="curve-main"><div class="editoractions"><strong>タイムライン・カーブ</strong>
        <span class="muted">選択中：${selected?time(selected.time):'シーンなし'} / 実キー ${keys.length}件</span>
        <button data-zone="scene" data-action="native_editor_zone">キーを追加・編集</button><button data-action="scene_save">シーンに保存</button></div>
        <div class="curve-grid" aria-label="実キーフレームの相対FOVカーブ">${dots}${keys.length?'':'<span class="curve-empty">シーンを選択し、既存エディタでキーを設定してください</span>'}</div></div>
        <aside class="curve-side"><h3>選択キー / 値</h3><p>時刻：${keys.length?esc(keys[0].time)+' 秒':'未設定'}</p>
        <p>相対FOV：${keys.length?esc(keys[0].fov)+'°':'未設定'}</p>
        <p class="muted">手動値とは別です。時刻・補間・Undoは実動作エディタで操作します。</p>
        <button data-zone="camera" data-action="native_editor_zone">精密編集を開く</button></aside></div>`;
    }else if(tab==='scene'){
      html=`<div class="editoractions"><button data-action="check_all">全件チェック</button><button data-action="uncheck_all">チェックを外す</button><button data-action="jump_selected">選択シーンへ移動</button><button data-action="scene_save">シーンを保存</button><button data-zone="scene" data-action="native_editor_zone">詳細タイムライン</button></div><div class="timeline">${d.scenes.length?d.scenes.map(s=>`<button data-scene="${s.index}" class="${s.selected?'selected':''}">${time(s.time)}<br>${esc(s.role)}</button>`).join(''):'スキャン後に実シーンを表示します。'}</div>`;
    }else if(tab==='camera'){
      const v=d.camera.values;
      html=`<div class="editgrid camera-grid">${card('カメラモード',`<div class="choicegrid">${modeButtons()}</div>`)}
        ${card('対象サイド・スタイル',`<div class="choicegrid">${['auto','BLUE','RED'].map(s=>
          `<button data-camera-side="${s}" class="${d.camera.side_key===s?'selected':''}">${s}</button>`).join('')}</div><button data-drawer="camera">10種・詳しい設定</button>`)}
        ${card('距離・高さ・角度',`<div class="settingrow"><label>距離</label><input type="range" data-camera-number="third_dist" min="500" max="1400" value="${v.third_dist??900}"><input type="number" data-camera-number="third_dist" min="500" max="1400" value="${v.third_dist??900}"></div>
        <div class="settingrow"><label>高さ</label><input type="range" data-camera-number="cam_height" min="0" max="900" value="${v.cam_height??350}"><input type="number" data-camera-number="cam_height" min="0" max="900" value="${v.cam_height??350}"></div>
        <div class="settingrow"><label>角度</label><input type="range" data-camera-number="third_yaw" min="-180" max="180" value="${v.third_yaw??0}"><input type="number" data-camera-number="third_yaw" min="-180" max="180" value="${v.third_yaw??0}"></div>
        <p class="muted small-only">狭い画面では数値をカメラ設定から開けます。</p>
        <button data-drawer="camera">カメラ数値を詳しく設定</button><button data-zone="camera" data-action="native_editor_zone">FOV・キーフレーム</button>`)}
        </div>`;
    }else if(tab==='fx'){
      html=card('色・FX',`<div class="editoractions"><button data-zone="fx" data-action="native_editor_zone">全映像FXを開く</button><button data-zone="color" data-action="native_editor_zone">LUT・色・DOF・Fog</button><button data-drawer="asset">Work素材・FX</button><button data-action="work_settings">素材とFXの設定</button></div><p class="muted">研究段階の機能を動作済みとは表示しません。</p>`);
    }else if(tab==='test'){
      const qa=d.qa?.selftest||{status:'NOT_RUN'};
      const saved=qa.status==='RECORDED'?
        `前回の安全な自動診断 ${esc(qa.timestamp)}：成功 ${qa.passed} / 注意 ${qa.warnings} / 失敗 ${qa.failed}`:
        '安全な自動診断：結果なし';
      html=card('テスト結果・診断',`<p>${d.qa?.auto_pending?'自動診断を実行中':'待機中'} / ${saved}</p>
        <p class="muted">この結果は実LoL映像・ゲーム音・録画の合格ではありません。総合試験はNOT_RUNです。</p>
        <p class="muted">未実装：エンゲージ独立検出、画像品質によるベストショット自動選択。</p>
        <div class="editoractions"><button data-action="diagnostics">診断ログを開く</button>
        <button data-action="automatic_qa" ${d.qa?.auto_pending?'disabled title="自動診断中です"':''}>安全な自動診断を実行</button>
        <button data-action="camera_qa" ${d.replay.connected?'':'disabled title="LoL接続後に実行できます"'}>カメラ＋Work素材一括QA</button></div>`);
    }else{
      html=card('動画作成・設定',`<p class="muted">出力対象 ${d.checked_count}件 / ${esc(d.output.fps)} / ${esc(d.output.encoder_policy)}</p><div class="editoractions"><button data-zone="output" data-action="native_editor_zone">GPU・音声・HUD</button><button data-action="output_folder">出力先</button><button data-drawer="review">作成内容を確認</button><button data-action="cancel_job">書き出しを停止</button></div>`);
    }
    $('#editor-content').innerHTML=html;
  }
  function openDrawer(kind){
    if(!current)return;
    drawer=kind;draft=null;
    if(kind==='review'){openReview();return;}
    const panel=$('#drawer');$('#drawer-title').textContent=kind==='camera'?'カメラ設定（適用前は変更されません）':'キルフレーム・素材（確認用を含む）';
    if(kind==='camera'){
      const values=current.camera.values;
      draft={mode:current.camera.mode,side:current.camera.side_key||'auto',
        style:current.camera.style_key||'third_cinema',values:{...values}};
      const rows=[['third_dist','距離',500,1400],['cam_height','高さ',0,900],['third_yaw','角度',-180,180],['motion_arc','回り込み',0,45],['motion_dolly','ドリー',0,15]];
      $('#drawer-body').innerHTML=`<h3>カメラモード</h3><div class="choicegrid">${modeButtons()}</div>
        <h3>対象サイド</h3><div class="choicegrid">${['auto','BLUE','RED'].map(x=>`<button data-camera-side="${x}">${x}</button>`).join('')}</div>
        <h3>既存カメラ10種</h3><select id="camera-style">${cameraStyles.map(([name,id])=>`<option value="${id}">${name}</option>`).join('')}</select>
        <h3>数値</h3>${rows.map(([key,label,min,max])=>`<div class="settingrow"><label for="num-${key}">${label}</label><input type="range" min="${min}" max="${max}" value="${values[key]??min}" data-number="${key}"><input id="num-${key}" type="number" min="${min}" max="${max}" step="0.1" value="${values[key]??min}" data-number="${key}"></div>`).join('')}
        <p class="muted">FOVとキー編集は既存の詳細エディタで操作します。手動値とキー値を混同しません。</p>
        <button data-zone="camera" data-action="native_editor_zone">FOV・キー編集を開く</button>`;
      $('#camera-style').value=draft.style;
    }else{
      draft={frameId:current.frame.id};
      const cards=[...current.frame.cards,...current.frame.library_cards];
      const seen=new Set();
      $('#drawer-body').innerHTML=`<p>既存の実素材を表示します。正式合格と確認用の区別は維持します。</p>
        <div class="assetcards">${cards.filter(x=>!seen.has(x.id)&&seen.add(x.id)).map(x=>
          `<button class="assetcard ${x.id===draft.frameId?'selected':''}" data-frame="${esc(x.id)}"><img src="${url('/api/asset/'+encodeURIComponent(x.id))}" alt=""><span>${esc(x.label)}</span><span>${esc(x.status)}</span></button>`).join('')}</div>
        <div class="editoractions"><button data-action="work_gallery">Work素材図鑑で全候補を見る</button><button data-action="legacy_frame_gallery">既存37バッジ</button></div>`;
    }
    panel.hidden=false;$('#drawer-close').focus();
  }
  function closeDrawer(){drawer=null;draft=null;$('#drawer').hidden=true;document.activeElement.blur();}
  async function applyDrawer(){
    if(!drawer||!draft)return;
    try{
      if(drawer==='camera'){
        // Validate all numeric values on the backend before applying any of them.
        const mode=Object.entries(modeNames).find(([,label])=>label===draft.mode)?.[0];
        if(!mode)throw new Error('カメラモードが不明です');
        await call('ui3_camera_batch',{mode,side:draft.side,style:draft.style,values:draft.values});
      }else if(drawer==='asset'){
        if(!draft.frameId)throw new Error('先に素材を選択してください');
        await call('frame',{id:draft.frameId});
      }
      closeDrawer();toast('既存AutoCineの設定へ適用しました');
    }catch(e){toast(e.message);}
  }
  function openReview(){const d=current;drawer='review';const box=$('#modalback');
    $('#modal-body').innerHTML=`<p>チェックしたシーン：${d.checked_count}件 / ${d.scenes.length}件</p>
      <p>カメラ：${esc(d.camera.mode)} / ${esc(d.camera.side)}</p>
      <p>キルフレーム：${esc(d.frame.id||'未選択')} / FX：${esc(d.frame.effect_id||'未選択')}</p>
      <p>出力：${esc(d.output.fps)} / ${esc(d.output.encoder_policy)}</p>
      <p>LoL接続：${d.replay.connected?'接続中':'未接続'} / 音声：${d.output.game_audio?'LoLゲーム音有効':'LoLゲーム音無効'}</p>
      <p class="muted">この確認画面を開くだけでは録画を開始しません。実接続・音声・GPU・出力は別途検証が必要です。</p>`;
    $('#modal-export').disabled=!d.replay.connected||!d.checked_count||d.output.busy;
    box.hidden=false;$('#modal-cancel').focus();
  }
  function closeReview(){drawer=null;$('#modalback').hidden=true;}
  document.addEventListener('click',event=>{
    const target=event.target.closest('button');if(!target)return;
    if(target.dataset.tab){tab=target.dataset.tab;renderEditor();document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('selected',b===target));return;}
    if(target.dataset.route){route(target.dataset.route);return;}
    if(target.dataset.drawer){openDrawer(target.dataset.drawer);return;}
    if(target.dataset.mode){run('event_mode',{value:target.dataset.mode});return;}
    if(target.dataset.scene){run('select_scene',{index:Number(target.dataset.scene)});return;}
    if(target.dataset.cameraMode){
      if(drawer==='camera'&&draft){draft.mode=modeNames[target.dataset.cameraMode];
        $('#drawer-body').querySelectorAll('[data-camera-mode]').forEach(b=>b.classList.toggle('selected',b===target));}
      else run('camera_mode',{value:target.dataset.cameraMode});return;}
    if(target.dataset.cameraSide&&draft){draft.side=target.dataset.cameraSide;
      $('#drawer-body').querySelectorAll('[data-camera-side]').forEach(b=>b.classList.toggle('selected',b===target));return;}
    if(target.dataset.cameraSide){run('camera_side',{value:target.dataset.cameraSide});return;}
    if(target.dataset.effectStrength){run('effect_strength',{value:target.dataset.effectStrength});return;}
    if(target.dataset.frameDirect){run('frame',{id:target.dataset.frameDirect});return;}
    if(target.dataset.frame&&draft){draft.frameId=target.dataset.frame;
      $('#drawer-body').querySelectorAll('[data-frame]').forEach(b=>b.classList.toggle('selected',b===target));return;}
    if(target.dataset.action){const data=target.dataset.zone?{zone:target.dataset.zone}:{};run(target.dataset.action,data);}
  });
  $('#drawer-close').onclick=closeDrawer;$('#drawer-cancel').onclick=closeDrawer;$('#drawer-apply').onclick=applyDrawer;
  $('#modal-cancel').onclick=closeReview;$('#modal-export').onclick=async()=>{
    closeReview();try{await call('export_checked');}catch(e){toast(e.message);}};
  document.addEventListener('input',event=>{
    const direct=event.target.dataset.cameraNumber;
    if(direct){document.querySelectorAll(`[data-camera-number="${direct}"]`).forEach(x=>{
      if(x!==event.target)x.value=event.target.value;
    });return;}
    const key=event.target.dataset.number;if(!key||!draft||drawer!=='camera')return;
    const value=Number(event.target.value);if(!Number.isFinite(value))return;
    draft.values[key]=value;
    $('#drawer-body').querySelectorAll(`[data-number="${key}"]`).forEach(x=>{if(x!==event.target)x.value=String(value);});
  });
  document.addEventListener('change',event=>{
    if(event.target.dataset.trim){
      run('trim',{key:event.target.dataset.trim,value:Number(event.target.value)});return;
    }
    if(event.target.dataset.cameraNumber){
      run('camera_number',{key:event.target.dataset.cameraNumber,value:Number(event.target.value)});return;
    }
    if(event.target.id==='camera-style'&&draft)draft.style=event.target.value;
  });
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    if(!$('#modalback').hidden)closeReview();else if(!$('#drawer').hidden)closeDrawer();
  });
  async function frame(){if(!current?.preview.mirror_requested)return;
    try{const response=await fetch(url('/api/frame.jpg'),{cache:'no-store',
      headers:lastFrameTag?{'If-None-Match':lastFrameTag}:{}});
      if(response.status===304)return;
      if(!response.ok)return;
      const blob=await response.blob();const image=$('#live-frame');const old=image.dataset.objectUrl;
      const objectUrl=URL.createObjectURL(blob);image.src=objectUrl;image.dataset.objectUrl=objectUrl;
      image.style.display='block';$('#video-empty').hidden=true;lastFrameTag=response.headers.get('ETag');
      if(old)URL.revokeObjectURL(old);
    }catch(_error){}
  }
  refresh().catch(e=>toast(e.message));
  setInterval(()=>refresh().catch(()=>{}),1300);
  setInterval(frame,100);
})();
