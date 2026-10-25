/* Live controls for audited research layouts; the original CSS/markup stays intact. */
(() => {
  'use strict';
  const token = window.AUTOCINE_TOKEN;
  const screenId = window.AUTOCINE_SCREEN;
  const endpoint = (path) => `${path}?token=${encodeURIComponent(token)}`;
  const state = {value: null, frameNumber: 0};
  const systemDark = matchMedia('(prefers-color-scheme: dark)');
  function applyTheme(preference) {
    document.documentElement.dataset.theme = preference === 'system' ?
      (systemDark.matches ? 'dark' : 'light') : preference;
  }
  systemDark.addEventListener('change', () => {
    if (state.value?.workspace.theme === 'system') applyTheme('system');
  });
  const notice = document.createElement('div');
  notice.setAttribute('role', 'status');
  notice.style.cssText = 'position:fixed;bottom:34px;left:50%;transform:translateX(-50%);' +
    'z-index:1000;padding:8px 14px;border-radius:7px;background:#172b3e;color:white;' +
    'font:14px Yu Gothic UI,Meiryo,sans-serif;box-shadow:0 4px 16px #0005;display:none';
  document.body.append(notice);
  let noticeTimer;
  function message(text) {
    notice.textContent = text;
    notice.style.display = 'block';
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => notice.style.display = 'none', 5000);
  }
  async function snapshot() {
    const response = await fetch(endpoint('/api/state'), {cache: 'no-store'});
    if (!response.ok) throw new Error('状態の取得に失敗しました');
    state.value = await response.json();
    render();
  }
  async function action(name, data={}) {
    const response = await fetch(endpoint('/api/action'), {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action:name,data})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `${name} に失敗しました`);
    state.value = result;
    render();
    return result;
  }
  function invoke(name, data) { action(name,data).catch(error => message(error.message)); }
  const image = document.querySelector('.preview-stage img.game-image');
  let frameTag = null;
  let lastFrameRequest = 0;
  const displayedFrameTimes = [];
  let displayedFps = 0;
  let lastDisplayedFrame = 0;
  const decorativeFrame = document.querySelector('.preview-stage img.frame-overlay');
  if (decorativeFrame) decorativeFrame.style.display = 'none';
  if (image) {
    image.removeAttribute('src');
    image.alt = '実LoLミラー映像は接続後に表示します';
    image.style.visibility = 'hidden';
  }
  function sceneTime(seconds) {
    return `${String(Math.floor(seconds/60)).padStart(2,'0')}:` +
      String(Math.floor(seconds%60)).padStart(2,'0');
  }
  function renderTimeline(data) {
    const timeline=document.querySelector('[data-ui="timeline"]');
    if (!timeline) return;
    timeline.querySelectorAll('.film-placeholder').forEach(slot =>
      slot.style.display = data.scenes.length ? 'none' : '');
    const duration=Math.max(data.scan.duration || 0,
      ...data.scenes.map(scene=>scene.time + 10),0);
    const ruler=[...timeline.querySelectorAll('.ruler span')];
    ruler.forEach((tick,index)=>{
      tick.textContent=duration ? sceneTime(duration*index/Math.max(ruler.length-1,1)) : '—';
    });
    const lanes=[...timeline.querySelectorAll('.lane')];
    lanes.forEach((lane,index)=>{
      if (index>0) {
        // Keep the authored lane layout, but remove illustrative clips until real scene data exists.
        lane.style.display='';
        lane.querySelectorAll('.clip').forEach(clip=>clip.remove());
        const marker=lane.querySelector('.kill-line');
        if (marker) marker.style.display='none';
        lane.title='このトラックは実際のシーンを選択した後に編集します';
        return;
      }
      const bar=lane.querySelector('.lane-bar');
      if (!bar) return;
      bar.querySelectorAll('.clip').forEach(clip=>clip.remove());
      const marker=bar.querySelector('.kill-line');
      const selected=data.scenes.find(scene=>scene.selected);
      if (marker) {
        marker.style.display=selected && duration ? '' : 'none';
        if (selected && duration) marker.style.left=`${Math.min(100,100*selected.time/duration)}%`;
      }
      for (const scene of data.scenes) {
        const clip=document.createElement('span');
        clip.className=`clip${scene.selected?' active':''}`;
        clip.dataset.sceneIndex=String(scene.index);
        clip.textContent=sceneTime(scene.time);
        clip.title=`${sceneTime(scene.time)} ${scene.role==='assist'?'アシスト':'キル'} ` +
          `${scene.side || 'サイド不明'} / ${scene.checked?'出力対象':'出力対象外'}`;
        clip.style.left=`${Math.min(97,100*scene.time/duration)}%`;
        clip.style.width=`${Math.max(2.5,Math.min(12,800/duration))}%`;
        clip.style.cursor='pointer';
        bar.append(clip);
      }
      const label=lane.querySelector('.lane-label');
      if (label) label.textContent=data.scenes.length ? `検出シーン ${data.scenes.length}件` : 'スキャン後に表示';
    });
  }
  function filterLibrary() {
    const query = (document.querySelector('.legacy6-search')?.value || '').trim().toLowerCase();
    const filter = document.querySelector('[data-library-filter].selected')?.dataset.libraryFilter || 'all';
    document.querySelectorAll('[data-ui^="library-card-"]').forEach(card => {
      if (!card.dataset.frameId) return;
      const matchesText = !query || `${card.dataset.frameId} ${card.querySelector('.library-card-name')?.textContent || ''}`
        .toLowerCase().includes(query);
      card.style.display = matchesText && (filter === 'all' || card.dataset.status === filter) ? '' : 'none';
    });
  }
  function render() {
    const data = state.value;
    if (!data) return;
    applyTheme(data.workspace.theme);
    const themeChoice = document.querySelector('#theme');
    if (themeChoice && themeChoice.value !== data.workspace.theme) themeChoice.value = data.workspace.theme;
    picker.value = familyStart.get(data.workspace.candidate_id) || 'T-B-M';
    const tag = document.querySelector('.preview-tag');
    if (tag) tag.textContent = data.preview.mirror_requested ?
      `UI映像更新 ${displayedFps.toFixed(1)} fps / 合成表示 ${data.preview.measured_fps} fps / 目標 ${data.preview.target_hz}` :
      'LoLミラー未接続・静止イラストは表示しません';
    document.querySelectorAll('.connection-state').forEach(label=>{
      label.textContent=data.replay.connected?'接続中':'LoL未接続';
    });
    document.querySelectorAll('[data-ui="replay-header"]').forEach(label=>{
      label.textContent=data.replay.connected?'リプレイ接続中':'リプレイ未接続';
    });
    document.querySelectorAll('[data-ui="output-fps"]').forEach(label=>{
      label.textContent=/fps/i.test(String(data.output.fps)) ?
        String(data.output.fps) : `${data.output.fps} fps`;
    });
    const footnote = document.querySelector('footer.footnote span');
    if (footnote) footnote.textContent = 'UI比較版・実際の操作は既存AutoCineに反映 / LoL未接続時は映像を表示しません';
    const scanStatus=document.querySelector('[data-ui="scan-status"]');
    if (scanStatus) scanStatus.textContent=data.scan.status;
    const sceneCount=document.querySelector('[data-ui="scene-count"]');
    if (sceneCount) sceneCount.textContent=`全${data.scenes.length}件`;
    const replayStatus=document.querySelector('[data-ui="replay-status"]');
    if (replayStatus) replayStatus.textContent=data.replay.connected ?
      `Replay API 接続済み / プレイヤー${data.replay.player_count}人` :
      'Replay API 未接続。リプレイを開き、試合全体スキャンまたは更新を実行してください。';
    const replayPath=document.querySelector('[data-ui="replay-path"]');
    if (replayPath) replayPath.textContent=data.replay.connected ?
      '接続中の試合（ファイル名は未取得）' : '接続待ち';
    const targetName=document.querySelector('[data-ui="target-name"]');
    if (targetName) {
      const target=data.replay.players.find(player=>player.slot===data.replay.target_slot);
      targetName.textContent=target ? `TargetLock：${target.champion} / ${target.name}` : 'TargetLock：未選択';
    }
    const flowReady=document.querySelector('.layout-E[data-ui="workspace"] [data-ui="ready-panel"]');
    if (flowReady) {
      const lines=[...flowReady.querySelectorAll('.stat-line')];
      const target=data.replay.players.find(player=>player.slot===data.replay.target_slot);
      const encoder=String(data.output.encoder_policy || '未設定');
      const encoderShort=encoder.includes('NVENC') ? '自動 (NVENC優先)' : encoder;
      const summaries=[
        data.replay.connected ? (target ? `${target.champion} / ${target.name}` : '接続中・対象未選択') : 'LoL未接続',
        `${data.checked_count}件選択`,
        `1920×1080 / ${data.output.fps}`,
        encoderShort,
        `${data.output.busy ? '処理中' : '未実行'} / ${data.preview.mirror_requested ? 'ミラー要求中' : '停止中'}`
      ];
      lines.forEach((line,index)=>{const value=line.querySelector('b');if(value && summaries[index]){
        value.textContent=summaries[index];
        if(index===3)value.title=encoder;
      }});
      const choices=flowReady.parentElement.querySelectorAll('.choice-dock .choice');
      const camera=choices[0]?.querySelector('p');
      if(camera)camera.textContent={manual:'従来の手動カメラ',fixed_auto:'固定視点＋自動構図補正',
        full_auto:'フルオートシネマ'}[data.camera.mode] || '既存の設定';
      const frame=choices[1]?.querySelector('p');
      if(frame)frame.textContent=data.frame.id || 'キルフレーム未選択';
      const thumb=choices[1]?.querySelector('img.frame-thumb');
      if(thumb){
        thumb.style.visibility=data.frame.id ? 'visible' : 'hidden';
        if(data.frame.id && thumb.dataset.frameId!==data.frame.id){
          thumb.src=endpoint(`/api/asset/${encodeURIComponent(data.frame.id)}`);
          thumb.dataset.frameId=data.frame.id;
          thumb.alt='選択中の実キルフレーム';
        }
      }
      const effect=choices[2]?.querySelector('p');
      if(effect)effect.textContent=data.frame.effect_id || 'FX未選択';
    }
    const playerList=document.querySelector('[data-ui="player-list"]');
    if (playerList) {
      playerList.replaceChildren();
      if (!data.replay.players.length) {
        const placeholder=document.createElement('p');
        placeholder.textContent='試合接続後にプレイヤーを表示します。';
        playerList.append(placeholder);
      }
      for (const player of data.replay.players) {
        const row=document.createElement('div');
        row.className=`player-row${player.slot===data.replay.target_slot?' selected':''}`;
        row.dataset.playerSlot=String(player.slot);
        row.textContent=`${player.side}　${player.champion}　${player.name}`;
        playerList.append(row);
      }
    }
    const modeNames={manual:'従来の手動カメラ',fixed_auto:'固定視点＋自動構図補正',
      full_auto:'フルオートシネマ'};
    document.querySelectorAll('.camera-card[data-action-value]').forEach(card=>
      card.classList.toggle('selected',modeNames[card.dataset.actionValue]===data.camera.mode));
    const styleNames = {
      third:'三人称 追従のみ',
      third_cinema:'三人称シネマ (斜め後ろ・寄り＋ローアングル＋スロー)',
      geo_aim:'座標で主役を追う（実験用）',
      cinema:'FPS風シネマ (標準視点でドリーイン＋スロー)',
      fps:'FPS視点 (高さ補正)',orbit:'オービット (実験的)',
      lolnam_cinema:'Lolnam風シネマ (自動カメラ移動)',
      follow:'FPS風 追従のみ',cinema_top:'俯瞰シネマ (ズーム＋スロー・安全)',
      top:'俯瞰 追従のみ (安全)'
    };
    document.querySelectorAll('.testb-style-cards [data-action-value]').forEach(card =>
      card.classList.toggle('selected',styleNames[card.dataset.actionValue] === data.camera.style));
    document.querySelectorAll('.target-side button').forEach(button=>{
      const name=button.textContent.trim();
      const active=name==='BLUE' ? data.camera.side.includes('ブルー') :
        name==='RED' ? data.camera.side.includes('レッド') :
        name==='自動' && data.camera.side.includes('自動');
      button.classList.toggle('selected',active);
    });
    document.querySelectorAll('.edit-mode button').forEach(button=>{
      if (button.closest('.legacy3-edit-mode')) {
        button.classList.toggle('selected',button.dataset.actionValue===screenId);
        return;
      }
      const mode=button.textContent.includes('詳細')?'advanced':'easy';
      button.classList.toggle('selected',data.edit_mode===mode);
    });
    document.querySelectorAll('.legacy3-preset').forEach(button=>
      button.classList.toggle('selected',button.dataset.actionValue===data.easy_preset));
    const presetName=document.querySelector('[data-ui="easy-preset-name"]');
    if (presetName) presetName.textContent=data.easy_preset || '未選択';
    const countLabel = document.querySelector('[data-ui="scene-list"] .panel-head + button + p');
    if (countLabel) {
      countLabel.textContent = `検出 ${data.scenes.length}件 / 出力チェック ${data.checked_count}件` +
        (data.scan.percent > 0 && data.scan.percent < 100 ? ` / スキャン ${Math.round(data.scan.percent)}%` : '');
      countLabel.title = data.scan.status;
    }
    document.querySelectorAll('span, strong, button, p').forEach(label=>{
      const value=label.textContent.trim();
      if (value==='表示例：4 / 6件を選択' || label.dataset.liveCount==='selection') {
        label.textContent=`選択：${data.checked_count} / ${data.scenes.length}件`;
        label.dataset.liveCount='selection';
      } else if (value==='チェックした4件' || label.dataset.liveCount==='checked') {
        label.textContent=`チェックした${data.checked_count}件`;
        label.dataset.liveCount='checked';
      } else if (value==='4件から動画を作成' || label.dataset.liveCount==='export') {
        label.textContent=`${data.checked_count}件から動画を作成`;
        label.dataset.liveCount='export';
      }
    });
    const selectedScene=data.scenes.find(scene=>scene.selected);
    document.querySelectorAll('.preview-heading .row span:first-child').forEach(label=>{
      if (/^\d{1,2}:\d{2}/.test(label.textContent.trim()) || label.dataset.liveTime) {
        label.textContent=selectedScene ?
          `${sceneTime(selectedScene.time)}.${String(Math.floor(selectedScene.time%1*100)).padStart(2,'0')}` :
          '--:--';
        label.dataset.liveTime='1';
      }
    });
    renderTimeline(data);
    const sampleCards = [...document.querySelectorAll('[data-ui^="scene-card-"]')];
    if (sampleCards.length && data.scenes.length > sampleCards.length) {
      const parent = sampleCards[0].parentElement;
      for (let index = sampleCards.length; index < data.scenes.length; index++) {
        const clone = sampleCards[0].cloneNode(true);
        clone.dataset.ui = `scene-card-${index}`;
        parent.append(clone);
      }
    }
    document.querySelectorAll('[data-ui^="scene-card-"]').forEach((card, position) => {
      const scene = data.scenes[position];
      if (!scene) {
        // Empty slots preserve each candidate's layout without pretending a replay was scanned.
        card.style.display = '';
        card.style.opacity = '0.55';
        card.style.cursor = 'default';
        card.title = '未スキャン：リプレイ接続後にシーンが表示されます';
        card.classList.add('empty-scene');
        delete card.dataset.sceneIndex;
        card.classList.remove('selected');
        const time = card.querySelector('.time');
        if (time) time.textContent = '--:--';
        const side = card.querySelector('.side');
        if (side) { side.textContent = '—'; side.classList.remove('blue', 'red'); }
        const title = card.querySelector('strong');
        if (title) title.textContent = card.closest('.layout-A, .layout-detail') ? '未接続' : '未スキャン';
        const thumbnail = card.querySelector('img.scene-thumb');
        if (thumbnail) { thumbnail.style.visibility = 'hidden'; thumbnail.alt = ''; }
        const check = card.querySelector('.check');
        if (check) { check.textContent = ''; check.classList.remove('checked'); }
        return;
      }
      card.style.display = '';
      card.style.opacity = '';
      card.style.cursor = '';
      card.title = '';
      card.classList.remove('empty-scene');
      card.dataset.sceneIndex = scene.index;
      card.classList.toggle('selected',scene.selected);
      const time = card.querySelector('.time');
      if (time) time.textContent = `${Math.floor(scene.time/60)}:${String(Math.floor(scene.time%60)).padStart(2,'0')}`;
      const side = card.querySelector('.side');
      if (side) {
        side.textContent = scene.side || '—';
        side.classList.toggle('blue', scene.side === 'BLUE');
        side.classList.toggle('red', scene.side === 'RED');
      }
      const title = card.querySelector('strong');
      if (title) title.textContent = scene.role === 'assist' ? 'アシスト' :
        scene.multikill >= 3 ? 'トリプルキル' :
        scene.multikill === 2 ? 'ダブルキル' : 'キル';
      const thumbnail = card.querySelector('img.scene-thumb');
      if (thumbnail) {
        thumbnail.style.visibility = 'hidden';
        thumbnail.alt = 'このシーンのサムネイルは未取得';
      }
      const check = card.querySelector('.check');
      if (check) { check.textContent = scene.checked ? '✓' : ''; check.classList.toggle('checked', scene.checked); }
    });
    document.querySelectorAll('[data-ui^="material-card-"]').forEach((card, index) => {
      const entry = screenId === 'T-B-F' ? data.frame.testb_cards[index] : data.frame.cards[index];
      if (!entry) { card.style.display = 'none'; return; }
      card.style.display = '';
      card.dataset.frameId = entry.id;
      card.classList.toggle('selected', data.frame.id === entry.id);
      const label = card.querySelector('h3');
      if (label) {
        const referenceNames = {
          '083/a_simple_main': 'No.083 A',
          '004/demacia_frame': 'No.004 デマーシア',
          '004/noxus_frame': 'No.004 ノクサス',
          '004/bilgewater_frame': 'No.004 ビルジウォーター'
        };
        label.textContent = referenceNames[entry.id] || entry.label;
        label.title = entry.label;
      }
      const badge = card.querySelector('.badge');
      if (badge) {
        badge.textContent = entry.status === 'approved' ? '✓ 枠のみ正式合格' : '△ 確認用';
        badge.classList.toggle('ok',entry.status === 'approved');
        badge.classList.toggle('warn',entry.status !== 'approved');
      }
      const thumbnail = card.querySelector('img.frame-thumb');
      if (thumbnail && thumbnail.dataset.frameId !== entry.id) {
        thumbnail.src = endpoint(`/api/asset/${encodeURIComponent(entry.id)}`);
        thumbnail.alt = `${entry.label} の監査済み原本`;
        thumbnail.dataset.frameId = entry.id;
      }
    });
    const libraryCards = data.frame.library_cards || [];
    document.querySelectorAll('[data-ui^="library-card-"]').forEach((card, index) => {
      const entry = libraryCards[index];
      if (!entry) { card.style.display = 'none'; return; }
      card.style.display = '';
      card.dataset.frameId = entry.id;
      card.dataset.status = entry.status;
      card.classList.toggle('selected', data.frame.id === entry.id);
      const name = card.querySelector('.library-card-name');
      if (name) name.textContent = entry.label.replace(/^No\.\d+\s*/, '').replace(/_frame$/, '').replaceAll('_',' ');
      const badge = card.querySelector('.badge');
      if (badge) badge.textContent = entry.status === 'approved' ? '枠のみ正式合格' : '確認用';
      const thumb = card.querySelector('img.frame-thumb');
      if (thumb && thumb.dataset.frameId !== entry.id) {
        thumb.src = endpoint(`/api/asset/${encodeURIComponent(entry.id)}`);
        thumb.dataset.frameId = entry.id;
        thumb.alt = `${entry.label} の実素材`;
      }
    });
    const selectedLibraryFrame = libraryCards.find(entry => entry.id === data.frame.id);
    document.querySelectorAll('[data-ui="selected-frame-name"]').forEach(node => {
      node.textContent = selectedLibraryFrame?.label || data.frame.id || 'キルフレーム未選択';
    });
    document.querySelectorAll('.selected-frame-thumb').forEach(thumb => {
      const chosen = data.frame.id;
      thumb.style.display = chosen ? '' : 'none';
      if (chosen && thumb.dataset.frameId !== chosen) {
        thumb.src = endpoint(`/api/asset/${encodeURIComponent(chosen)}`);
        thumb.dataset.frameId = chosen;
      }
    });
    document.querySelectorAll('.selected-frame-empty').forEach(node =>
      node.style.display = data.frame.id ? 'none' : '');
    document.querySelectorAll('[data-ui="selected-frame-status"]').forEach(node => {
      node.textContent = selectedLibraryFrame?.status === 'approved' ?
        '枠のみ正式合格。FXの品質合格は別判定です。' :
        selectedLibraryFrame ? '確認用素材。品質合格は未判定です。' :
        data.frame.id ? '別ページの選択素材です。品質状態は図鑑で確認してください。' : '素材は未選択';
    });
    document.querySelectorAll('[data-ui="selected-effect-name"]').forEach(node => {
      node.textContent = data.frame.effect_id || 'エフェクト未選択';
    });
    document.querySelectorAll('[data-ui="selected-camera-mode"]').forEach(node => {
      node.textContent = data.camera.mode || '現在の設定';
    });
    filterLibrary();
    document.querySelectorAll('.motion-grid .motion').forEach(card =>
      card.classList.toggle('selected',card.textContent.trim().includes(data.frame.motion)));
    document.querySelectorAll('[data-setting]').forEach(input => {
      if (document.activeElement === input) return;
      const key = input.dataset.setting;
      const value = key === 'pre' || key === 'post' ? null : data.camera.values[key];
      if (value !== null && value !== undefined) input.value = value;
    });
    const hudToggle=document.querySelector('[data-hud-toggle]');
    if (hudToggle) hudToggle.checked = data.output.hud !== 'full';
    const hudVisible=document.querySelector('[data-hud-visible]');
    if (hudVisible) hudVisible.checked = data.output.hud === 'full';
    if (image && !data.preview.mirror_requested) image.style.visibility = 'hidden';
  }
  async function refreshFrame() {
    if (image && state.value?.preview.mirror_requested && !document.hidden) {
      const targetHz = Math.max(1, Math.min(144, Number.parseInt(state.value.preview.target_hz, 10) || 60));
      const remaining = 1000 / targetHz - (performance.now() - lastFrameRequest);
      if (remaining > 1) {
        setTimeout(() => requestAnimationFrame(refreshFrame), remaining);
        return;
      }
      lastFrameRequest = performance.now();
      try {
        const response = await fetch(endpoint('/api/frame.jpg') + `&n=${++state.frameNumber}`,
          {cache:'no-store', headers:frameTag ? {'If-None-Match':frameTag} : {}});
        if (response.status === 304) {
          // Native mirror has not presented a new frame; avoid a redundant decode.
          if (performance.now() - lastDisplayedFrame > 1000) displayedFps = 0;
        } else if (response.ok) {
          const blob = await response.blob();
          const next = URL.createObjectURL(blob);
          const previous = image.dataset.blob;
          image.src = next;
          image.dataset.blob = next;
          await image.decode();
          image.style.visibility = 'visible';
          if (previous) URL.revokeObjectURL(previous);
          frameTag = response.headers.get('ETag');
          const now = performance.now();
          lastDisplayedFrame = now;
          displayedFrameTimes.push(now);
          while (displayedFrameTimes.length && displayedFrameTimes[0] < now - 1000) displayedFrameTimes.shift();
          displayedFps = displayedFrameTimes.length > 1 ?
            1000 * (displayedFrameTimes.length - 1) / (now - displayedFrameTimes[0]) : 0;
        } else {
          image.style.visibility = 'hidden';
          frameTag = null;
          displayedFps = 0;
          displayedFrameTimes.length = 0;
        }
      } catch (_) {
        image.style.visibility = 'hidden';
        displayedFps = 0;
      }
      requestAnimationFrame(refreshFrame);
    } else {
      if (!state.value?.preview.mirror_requested) {
        frameTag = null;
        displayedFps = 0;
        displayedFrameTimes.length = 0;
      }
      setTimeout(refreshFrame, 200);
    }
  }
  const modeLabels = [
    ['従来の手動カメラ','manual'], ['固定視点＋自動構図補正','fixed_auto'],
    ['フルオートシネマ','full_auto']
  ];
  const motionLabels = new Map([
    ['一気に表示','instant'],['左から登場','slide_left'],['右から登場','slide_right'],
    ['下から登場','slide_up'],['上から登場','slide_down'],['パッと飛び出す','pop']
  ]);
  const cameraStyles = new Map([
    ['三人称シネマ','third_cinema'],['三人称','third'],['Geo Aim','geo_aim'],
    ['シネマ','cinema'],['FPS風','fps'],['Orbit','orbit'],
    ['Lolnamシネマ','lolnam_cinema'],['Follow','follow'],
    ['俯瞰シネマ','cinema_top'],['俯瞰','top']
  ]);
  function chooseExport() {
    const veil=document.createElement('div');
    veil.style.cssText='position:fixed;inset:0;background:#071321aa;z-index:3000;' +
      'display:grid;place-items:center';
    const panel=document.createElement('div');
    panel.style.cssText='background:var(--panel);color:var(--ink);padding:24px;' +
      'border:1px solid var(--line);border-radius:12px;min-width:330px;box-shadow:0 10px 30px #0006';
    const heading=document.createElement('h2');
    heading.textContent='動画にする範囲を選択';
    panel.append(heading);
    for (const [name,label] of [
      ['export_selected','現在のシーンだけ'], ['export_checked','チェックしたシーン'],
      ['export_all','全検出シーン'], ['export_smart','スマート自動編集']
    ]) {
      const item=document.createElement('button');
      item.textContent=label;
      item.style.cssText='display:block;width:100%;margin:8px 0;padding:10px';
      item.addEventListener('click',event=>{
        event.stopPropagation();veil.remove();invoke(name);
      });
      panel.append(item);
    }
    const cancel=document.createElement('button');
    cancel.textContent='キャンセル';
    cancel.style.cssText='display:block;width:100%;margin-top:12px;padding:10px';
    cancel.addEventListener('click',event=>{event.stopPropagation();veil.remove()});
    panel.append(cancel);veil.append(panel);document.body.append(veil);
  }
  function chooseProjectOperation() {
    const veil=document.createElement('div');
    veil.style.cssText='position:fixed;inset:0;background:#071321aa;z-index:3000;' +
      'display:grid;place-items:center';
    const panel=document.createElement('div');
    panel.style.cssText='background:var(--panel);color:var(--ink);padding:24px;' +
      'border:1px solid var(--line);border-radius:12px;min-width:330px;box-shadow:0 10px 30px #0006';
    const heading=document.createElement('h2');
    heading.textContent='シーン編集プロジェクト';
    panel.append(heading);
    for (const [name,label] of [
      ['project_export','JSONファイルに保存'], ['project_import','JSONファイルから読み込む']
    ]) {
      const item=document.createElement('button');
      item.textContent=label;
      item.style.cssText='display:block;width:100%;margin:8px 0;padding:10px';
      item.addEventListener('click',event=>{
        event.stopPropagation();veil.remove();invoke(name);
      });
      panel.append(item);
    }
    const cancel=document.createElement('button');
    cancel.textContent='キャンセル';
    cancel.style.cssText='display:block;width:100%;margin-top:12px;padding:10px';
    cancel.addEventListener('click',event=>{event.stopPropagation();veil.remove()});
    panel.append(cancel);veil.append(panel);document.body.append(veil);
  }
  function operation(button) {
    if (button.dataset.action) {
      const name=button.dataset.action;
      return [name,button.dataset.actionValue?{value:button.dataset.actionValue}:{}];
    }
    const label = button.textContent.trim().replace(/\s+/g,' ');
    if (button.closest('.bottom-panel .tabs')) {
      const zones={'シーン':'scene','カメラ':'camera','色・FX':'fx','出力':'output'};
      return zones[label] ? ['native_editor_zone',{zone:zones[label]}] :
        label==='テスト結果' ? ['diagnostics'] : null;
    }
    if (/リプレイを開く/.test(label)) return ['open_replay'];
    if (/リプレイを変更/.test(label)) return ['open_replay'];
    if (/準備/.test(label)) return ['prepare'];
    if (/試合全体.*スキャン|シーンを検出/.test(label)) return ['scan'];
    if (/ミラー開始/.test(label)) return ['mirror_start'];
    if (/ミラー停止/.test(label)) return ['mirror_stop'];
    if (/演出を確認|演出プレビュー.*再生/.test(label)) return ['preview_play'];
    if (/^■?\s*停止$/.test(label)) return ['preview_stop'];
    if (/^基本設定$/.test(label)) return ['native_settings'];
    if (/GPU・音声・HUD/.test(label)) return ['native_settings'];
    if (/^出力設定$/.test(label)) return ['native_editor_zone',{zone:'output'}];
    if (/^簡単編集$/.test(label)) return ['edit_mode',{value:'easy'}];
    if (/^詳細編集$/.test(label)) return ['edit_mode',{value:'advanced'}];
    if (/このシーンに保存/.test(label)) return ['scene_save'];
    if (/元に戻す/.test(label)) return ['scene_undo'];
    if (/やり直す/.test(label)) return ['scene_redo'];
    if (/キーフレーム・色・DOFを開く/.test(label)) return ['native_editor_zone',{zone:'scene'}];
    if (/プロジェクト保存・読み込み/.test(label)) return ['project_menu'];
    if (/動画を作成|書き出す/.test(label)) return ['export_menu'];
    if (/おすすめで自動作成/.test(label)) return ['export_smart'];
    if (/ログ|診断/.test(label)) return ['diagnostics'];
    if (/選択シーンへ移動/.test(label)) return ['jump_selected'];
    if (/図鑑の全候補を見る/.test(label)) return ['work_gallery'];
    if (/FX設定/.test(label)) return ['work_settings'];
    if (/カメラ＋Work素材一括QA/.test(label)) return ['camera_qa'];
    if (/全選択/.test(label)) return ['check_all'];
    if (/全解除/.test(label)) return ['uncheck_all'];
    if (/\bBLUE\b/.test(label)) return ['camera_side',{value:'BLUE'}];
    if (/\bRED\b/.test(label)) return ['camera_side',{value:'RED'}];
    if (/自動/.test(label) && label.length < 10) return ['camera_side',{value:'auto'}];
    return null;
  }
  document.addEventListener('click', event => {
    if (event.target.closest('.prepare .section-head button')) {
      invoke('connect');
      return;
    }
    const player=event.target.closest('[data-player-slot]');
    if (player) {
      invoke('target_lock',{slot:Number(player.dataset.playerSlot)});
      return;
    }
    const timelineClip=event.target.closest('[data-ui="timeline"] .clip[data-scene-index]');
    if (timelineClip) {
      invoke('select_scene',{index:Number(timelineClip.dataset.sceneIndex)});
      return;
    }
    const check = event.target.closest('.scene-card .check');
    if (check) {
      event.stopPropagation();
      const index = Number(check.closest('.scene-card').dataset.sceneIndex);
      if (Number.isInteger(index)) invoke('check_scene',{index,checked:!check.classList.contains('checked')});
      return;
    }
    const card = event.target.closest('[data-ui^="scene-card-"]');
    if (card) {
      const index = Number(card.dataset.sceneIndex);
      if (Number.isInteger(index)) invoke('select_scene',{index});
      return;
    }
    const filter = event.target.closest('.scene-filter button, .filters button');
    if (filter) {
      const label = filter.textContent.trim();
      const value = /両方|すべて|キル\＋アシスト/.test(label) ? 'both' :
        label.includes('アシスト') ? 'assist' : 'kill';
      invoke('event_mode',{value});
      return;
    }
    const camera = event.target.closest('.camera-card');
    if (camera) {
      const match = modeLabels.find(([label]) => camera.textContent.includes(label));
      if (match) invoke('camera_mode',{value:match[1]});
      return;
    }
    const motion = event.target.closest('.motion-grid .motion');
    if (motion) {
      const found = [...motionLabels].find(([label])=>motion.textContent.includes(label));
      if (found) invoke('motion',{value:found[1]});
      return;
    }
    const frameCard = event.target.closest('[data-ui^="material-card-"]');
    if (frameCard?.dataset.frameId) {
      invoke('frame',{id:frameCard.dataset.frameId});
      return;
    }
    const libraryCard = event.target.closest('[data-ui^="library-card-"]');
    if (libraryCard?.dataset.frameId) {
      invoke('frame',{id:libraryCard.dataset.frameId});
      return;
    }
    const libraryFilter = event.target.closest('[data-library-filter]');
    if (libraryFilter) {
      document.querySelectorAll('[data-library-filter]').forEach(button =>
        button.classList.toggle('selected',button===libraryFilter));
      filterLibrary();
      return;
    }
    const preset = event.target.closest('.style-tiles .preset');
    if (preset) {
      const found=[...cameraStyles].find(([label])=>preset.textContent.trim()===label);
      if (found) invoke('camera_style',{value:found[1]});
      else message('このカメラカードの接続は未完了です');
      return;
    }
    const button = event.target.closest('button');
    if (!button) return;
    const found = operation(button);
    if (found?.[0] === 'choose_screen') location.assign(endpoint('/choose'));
    else if (found?.[0] === 'focus_scene') {
      const panel=document.querySelector('[data-ui="scene-list"]');
      if (panel) {
        panel.setAttribute('tabindex','-1');
        panel.focus();
        panel.classList.add('attention');
        setTimeout(()=>panel.classList.remove('attention'),1200);
      }
    }
    else if (found?.[0] === 'screen') {
      const id=button.dataset.actionValue;
      const route=id===currentViews?.main?'main':id===currentViews?.detail?'detail':null;
      if(route) comparisonRoute(route);
      else action('screen',{id}).then(()=>openScreen(id)).catch(e=>message(e.message));
    }
    else if (found?.[0] === 'edit_mode' && currentViews)
      comparisonRoute(found[1].value==='easy'?'main':'detail');
    else if (found?.[0] === 'export_menu') chooseExport();
    else if (found?.[0] === 'project_menu') chooseProjectOperation();
    else if (found?.[0] === 'apply_selected_frame') {
      const id=state.value?.frame?.id;
      if (id) invoke('frame',{id});
      else message('先にキルフレームを選択してください');
    }
    else if (found) invoke(found[0],found[1]);
    else message('この操作の実機接続は未完了です。動作済みとは扱いません。');
  });
  document.querySelectorAll('[data-setting]').forEach(input => input.addEventListener('change', () => {
    const key = input.dataset.setting, value = Number(input.value);
    if (!Number.isFinite(value)) return message('数値を入力してください');
    if (key === 'pre' || key === 'post') invoke('trim',{key,value});
    else invoke('camera_number',{key,value});
  }));
  document.querySelector('.legacy6-search')?.addEventListener('input', filterLibrary);
  const hudToggle=document.querySelector('[data-hud-toggle]');
  if (hudToggle) hudToggle.addEventListener('change',()=>invoke('hud',
    {value:hudToggle.checked?'hidden':'full'}));
  const hudVisible=document.querySelector('[data-hud-visible]');
  if (hudVisible) hudVisible.addEventListener('change',()=>invoke('hud',
    {value:hudVisible.checked?'full':'hidden'}));
  const theme = document.querySelector('#theme');
  if (theme) theme.addEventListener('change', () => invoke('theme',{value:theme.value}));
  const familyStart = new Map([
    ['testB','T-B-M'],['legacy03','L03-N'],['testA','T-A-M'],
    ['legacy06','L06-L'],['researchE','R-E-main'],
    ['legacy02','L02-M'],['legacy05','L05-M']
  ]);
  function openScreen(id) { location.assign(endpoint(`/ui/${encodeURIComponent(id)}`)); }
  const candidateViews = new Map([
    ['legacy03',{main:'L03-N',detail:'L03-D',material:'derived-material'}],
    ['testB',{main:'T-B-M',detail:'T-B-C',material:'T-B-F'}],
    ['testA',{main:'T-A-M',detail:'derived',material:'derived-material'}],
    ['legacy06',{main:'L06-L',detail:'L06-E',material:'L06-L'}],
    ['researchE',{main:'R-E-main',detail:'R-E-studio',material:'R-E-frames'}],
    ['legacy02',{main:'L02-M',detail:'derived',material:'derived-material'}],
    ['legacy05',{main:'L05-M',detail:'derived',material:'derived-material'}]
  ]);
  const currentFamily=window.AUTOCINE_DERIVED_DETAIL ||
    (screenId.startsWith('R-E-') ? 'researchE' :
      [...candidateViews].find(([,views])=>Object.values(views).includes(screenId))?.[0]);
  const currentViews=candidateViews.get(currentFamily);
  function comparisonRoute(kind) {
    if (!currentViews) return;
    const target=currentViews[kind] || currentViews.detail;
    const mode=kind==='main'?'easy':'advanced';
    if (target==='derived' || target==='derived-material') {
      // A derivative has no audit image and is labelled as a complement.
      const mainId=currentViews.main;
      const route=target==='derived' ? 'detail' : 'material';
      action('comparison_edit_mode',{value:mode}).then(()=>action('screen',{id:mainId})).then(()=>location.assign(
        endpoint(`/compare/${route}/${encodeURIComponent(currentFamily)}`))).catch(e=>message(e.message));
    } else action('comparison_edit_mode',{value:mode}).then(()=>action('screen',{id:target}))
      .then(()=>openScreen(target)).catch(e=>message(e.message));
  }
  document.querySelectorAll('[data-compare]').forEach(button=>
    button.addEventListener('click',event=>{event.stopPropagation();comparisonRoute(button.dataset.compare)}));
  if (currentViews && !document.querySelector('[data-compare]')) {
    const currentKind=window.AUTOCINE_DERIVED_DETAIL ? 'detail' :
      screenId===currentViews.main ? 'main' : 'detail';
    const routeButton=document.createElement('button');
    routeButton.type='button';
    routeButton.textContent=currentKind==='main' ? '詳細編集へ →' : '← メインへ戻る';
    routeButton.title=`${currentFamily} の${currentKind==='main'?'詳細編集':'メイン'}へ移動。設定とシーンは保持`;
    routeButton.style.cssText='position:fixed;right:0;top:27%;z-index:2000;' +
      'padding:8px 10px;border:2px solid #075fe0;border-right:0;' +
      'border-radius:7px 0 0 7px;background:#fff;color:#0746a7;' +
      'font:600 13px Yu Gothic UI,Meiryo,sans-serif;box-shadow:0 3px 12px #0004;cursor:pointer';
    routeButton.addEventListener('click',event=>{
      event.stopPropagation();comparisonRoute(currentKind==='main'?'detail':'main');
    });
    document.body.append(routeButton);
  }
  if (currentFamily==='researchE' && screenId==='R-E-main' &&
      !window.AUTOCINE_DERIVED_DETAIL && !document.querySelector('[data-ui="scene-list"]')) {
    // The source mock has no scene list. Keep a compact real-operation drawer on
    // the main view without changing the audited composition or inventing data.
    const drawer=document.createElement('section');
    drawer.dataset.ui='scene-list';
    drawer.setAttribute('aria-label','実シーン・スキャン操作');
    drawer.style.cssText='display:none;position:fixed;left:8px;top:34%;z-index:2001;' +
      'width:min(330px,calc(100vw - 20px));max-height:60vh;overflow:auto;padding:12px;' +
      'border:1px solid #8da9ce;border-radius:9px;background:#fff;color:#172b3e;' +
      'font:14px Yu Gothic UI,Meiryo,sans-serif;box-shadow:0 6px 24px #0005';
    drawer.innerHTML='<h2 style="margin:0 0 8px">検出シーン</h2>' +
      '<button data-action="scan">試合全体スキャン</button><p data-ui="scan-status">未スキャン</p>' +
      '<div class="scene-card" data-ui="scene-card-0"><span class="check"></span>' +
      '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>' +
      '<button data-action="native_editor_zone" data-action-value="scene">シーン編集・タイムライン</button>';
    const toggleScenes=event=>{
      event.stopPropagation();drawer.style.display=drawer.style.display==='none'?'block':'none';
    };
    const findStep=[...document.querySelectorAll('.layout-E .step')]
      .find(step=>step.querySelector('strong')?.textContent.trim()==='02');
    if(findStep){
      findStep.setAttribute('role','button');findStep.setAttribute('tabindex','0');
      findStep.setAttribute('aria-label','見どころ：試合全体スキャンとシーン一覧');
      findStep.title='クリックして試合全体スキャンとシーン一覧を開く';
      findStep.style.cursor='pointer';
      findStep.addEventListener('click',toggleScenes);
      findStep.addEventListener('keydown',event=>{
        if(event.key==='Enter'||event.key===' '){event.preventDefault();toggleScenes(event)}
      });
    }
    document.body.append(drawer);
  }
  const switchButton = document.createElement('button');
  switchButton.type = 'button';
  switchButton.textContent = 'UI比較';
  switchButton.title = '7候補を切り替える';
  switchButton.setAttribute('aria-controls', 'ui29-switch-panel');
  switchButton.setAttribute('aria-expanded', 'false');
  switchButton.style.cssText = 'position:fixed;right:0;top:50%;z-index:2001;' +
    'transform:translateY(-50%);writing-mode:vertical-rl;padding:12px 7px;' +
    'border:2px solid #075fe0;border-right:0;border-radius:8px 0 0 8px;' +
    'background:#fff;color:#0746a7;font:600 14px Yu Gothic UI,Meiryo,sans-serif;' +
    'box-shadow:0 3px 12px #0004;cursor:pointer';
  document.body.append(switchButton);
  const switchPanel = document.createElement('div');
  switchPanel.id = 'ui29-switch-panel';
  switchPanel.setAttribute('role', 'group');
  switchPanel.setAttribute('aria-label', 'UI比較画面の切替');
  switchPanel.style.cssText = 'position:fixed;right:38px;top:10vh;z-index:2001;' +
    'width:min(370px,calc(100vw - 50px));max-height:80vh;' +
    'overflow:auto;display:none;box-sizing:border-box;padding:16px;border:1px solid #8da9ce;' +
    'border-radius:10px;background:#fff;color:#172b3e;' +
    'font:14px Yu Gothic UI,Meiryo,sans-serif;box-shadow:0 6px 24px #0005';
  const panelTitle = document.createElement('strong');
  panelTitle.textContent = '7案のUIを比較';
  panelTitle.style.cssText = 'display:block;margin-bottom:12px;font-size:16px';
  switchPanel.append(panelTitle);
  function showSwitchPanel(visible) {
    switchPanel.style.display = visible ? 'block' : 'none';
    switchButton.setAttribute('aria-expanded', String(visible));
    if (visible) picker.focus();
    else switchButton.focus();
  }
  switchButton.addEventListener('click', event => {
    event.stopPropagation();
    showSwitchPanel(switchPanel.style.display === 'none');
  });
  switchPanel.addEventListener('click', event => event.stopPropagation());
  const picker = document.createElement('select');
  picker.setAttribute('aria-label','7候補を切り替える');
  picker.style.cssText = 'display:block;width:100%;box-sizing:border-box;padding:8px;margin:4px 0 12px';
  for (const [family,id] of familyStart) {
    const option=document.createElement('option');option.value=id;
    option.textContent=family;
    picker.append(option);
  }
  picker.value='T-B-M';
  picker.addEventListener('change',()=> action('screen',{id:picker.value}).then(()=>openScreen(picker.value)).catch(e=>message(e.message)));
  const familyLabel = document.createElement('label');
  familyLabel.textContent = '候補グループ';
  familyLabel.append(picker);
  switchPanel.append(familyLabel);
  if (currentViews) {
    const routes=document.createElement('div');
    routes.style.cssText='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px';
    for (const [kind,label] of [['main','メイン'],['detail','詳細編集'],['material','素材']]) {
      if (kind==='material' && !currentViews.material) continue;
      const button=document.createElement('button');button.type='button';button.textContent=label;
      button.addEventListener('click',()=>comparisonRoute(kind));routes.append(button);
    }
    switchPanel.append(routes);
  }
  const themePicker = document.createElement('select');
  themePicker.setAttribute('aria-label','比較画面の配色');
  themePicker.style.cssText = 'display:block;width:100%;box-sizing:border-box;padding:8px;margin:4px 0 12px';
  for (const [value,label] of [['system','Windowsに合わせる'],['light','ライト'],['dark','ダーク']]) {
    const option=document.createElement('option');option.value=value;option.textContent=label;
    themePicker.append(option);
  }
  themePicker.addEventListener('change',()=>action('theme',{value:themePicker.value})
    .then(()=>snapshot()).catch(e=>message(e.message)));
  const themeLabel=document.createElement('label');
  themeLabel.textContent='配色';themeLabel.append(themePicker);switchPanel.append(themeLabel);
  const chooserButton = document.createElement('button');
  chooserButton.type = 'button';
  chooserButton.textContent = '7候補の一覧を開く';
  chooserButton.style.cssText = 'padding:8px 12px;border:1px solid #075fe0;' +
    'border-radius:6px;background:#eef5ff;color:#0746a7;cursor:pointer';
  chooserButton.addEventListener('click', () => location.assign(endpoint('/choose')));
  switchPanel.append(chooserButton);
  document.body.append(switchPanel);
  document.addEventListener('keydown',event=>{
    if (event.ctrlKey && event.shiftKey && event.key.toLowerCase()==='u') {
      event.preventDefault();
      showSwitchPanel(switchPanel.style.display === 'none');
    }
    if (event.key === 'Escape' && switchPanel.style.display !== 'none') showSwitchPanel(false);
  });
  document.querySelectorAll('a[href$=".html"]').forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault();
    const filename=link.getAttribute('href').split('/').pop();
    const prefix=screenId.split('-')[1];
    const suffix=filename.replace('.html','').replace(/^A_|^E_/,'');
    const target=`R-${prefix}-${suffix.replaceAll('_','-')}`;
    if (state.value?.workspace.screens.some(row=>row.id===target)) {
      const kind=target===currentViews?.main?'main':
        target===currentViews?.detail?'detail':target===currentViews?.material?'material':null;
      if (kind) comparisonRoute(kind);
      else action('screen',{id:target}).then(()=>openScreen(target)).catch(e=>message(e.message));
    } else message('この候補内の補助画面は原画未提供です。別候補へ自動切替しません。');
  }));
  snapshot().then(()=>{
    for (const row of state.value.workspace.screens) {
      const familyOption = [...picker.options].find(option => option.value === familyStart.get(row.family));
      if (familyOption) familyOption.textContent =
        row.name;
    }
    themePicker.value=state.value.workspace.theme;
  }).catch(error=>message(error.message));
  setInterval(()=>snapshot().catch(()=>{}), 1200);
  refreshFrame();
})();
