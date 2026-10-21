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
  const decorativeFrame = document.querySelector('.preview-stage img.frame-overlay');
  if (decorativeFrame) decorativeFrame.style.display = 'none';
  if (image) {
    image.removeAttribute('src');
    image.alt = '実LoLミラー映像は接続後に表示します';
    image.style.visibility = 'hidden';
  }
  function render() {
    const data = state.value;
    if (!data) return;
    applyTheme(data.workspace.theme);
    const themeChoice = document.querySelector('#theme');
    if (themeChoice && themeChoice.value !== data.workspace.theme) themeChoice.value = data.workspace.theme;
    picker.value = familyStart.get(data.workspace.candidate_id) || 'R-A-main';
    const tag = document.querySelector('.preview-tag');
    if (tag) tag.textContent = data.preview.mirror_requested ?
      `ミラー実測 ${data.preview.measured_fps} fps / 目標 ${data.preview.target_hz}` :
      'LoLミラー未接続・静止イラストは表示しません';
    const footnote = document.querySelector('footer.footnote span');
    if (footnote) footnote.textContent = 'UI比較版・実際の操作は既存AutoCineに反映 / LoL未接続時は映像を表示しません';
    const countLabel = document.querySelector('.scene-list .panel-head + button + p');
    if (countLabel) {
      countLabel.textContent = `検出 ${data.scenes.length}件 / 出力チェック ${data.checked_count}件` +
        (data.scan.percent > 0 && data.scan.percent < 100 ? ` / スキャン ${Math.round(data.scan.percent)}%` : '');
      countLabel.title = data.scan.status;
    }
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
      if (!scene) { card.style.display = 'none'; return; }
      card.style.display = '';
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
      const entry = data.frame.cards[index];
      if (!entry) { card.style.display = 'none'; return; }
      card.style.display = '';
      card.dataset.frameId = entry.id;
      card.classList.toggle('selected', data.frame.id === entry.id);
      const label = card.querySelector('h3');
      if (label) label.textContent = entry.label;
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
    document.querySelectorAll('.motion-grid .motion').forEach(card =>
      card.classList.toggle('selected',card.textContent.trim().includes(data.frame.motion)));
    document.querySelectorAll('[data-setting]').forEach(input => {
      if (document.activeElement === input) return;
      const key = input.dataset.setting;
      const value = key === 'pre' || key === 'post' ? null : data.camera.values[key];
      if (value !== null && value !== undefined) input.value = value;
    });
    if (image && !data.preview.mirror_requested) image.style.visibility = 'hidden';
  }
  async function refreshFrame() {
    if (image && state.value?.preview.mirror_requested) {
      try {
        const response = await fetch(endpoint('/api/frame.jpg') + `&n=${++state.frameNumber}`, {cache:'no-store'});
        if (response.ok) {
          const blob = await response.blob();
          const next = URL.createObjectURL(blob);
          const previous = image.dataset.blob;
          image.src = next;
          image.dataset.blob = next;
          image.style.visibility = 'visible';
          if (previous) URL.revokeObjectURL(previous);
        } else image.style.visibility = 'hidden';
      } catch (_) { image.style.visibility = 'hidden'; }
    }
    setTimeout(refreshFrame, 100);
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
  function operation(button) {
    const label = button.textContent.trim().replace(/\s+/g,' ');
    if (/リプレイを開く/.test(label)) return ['open_replay'];
    if (/準備/.test(label)) return ['prepare'];
    if (/試合全体.*スキャン|シーンを検出/.test(label)) return ['scan'];
    if (/ミラー開始/.test(label)) return ['mirror_start'];
    if (/ミラー停止/.test(label)) return ['mirror_stop'];
    if (/演出を確認|演出プレビュー.*再生/.test(label)) return ['preview_play'];
    if (/^■?\s*停止$/.test(label)) return ['preview_stop'];
    if (/動画を作成|書き出す/.test(label)) return ['export_menu'];
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
    const filter = event.target.closest('.scene-filter button');
    if (filter) {
      const label = filter.textContent.trim();
      const value = label.includes('両方') ? 'both' : label.includes('アシスト') ? 'assist' : 'kill';
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
    if (found?.[0] === 'export_menu') chooseExport();
    else if (found) invoke(found[0],found[1]);
    else message('この操作の実機接続は未完了です。動作済みとは扱いません。');
  });
  document.querySelectorAll('[data-setting]').forEach(input => input.addEventListener('change', () => {
    const key = input.dataset.setting, value = Number(input.value);
    if (!Number.isFinite(value)) return message('数値を入力してください');
    if (key === 'pre' || key === 'post') invoke('trim',{key,value});
    else invoke('camera_number',{key,value});
  }));
  const theme = document.querySelector('#theme');
  if (theme) theme.addEventListener('change', () => invoke('theme',{value:theme.value}));
  const familyStart = new Map([
    ['legacy02','L02-M'],['legacy03','L03-N'],['legacy05','L05-M'],
    ['legacy06','L06-L'],['testA','T-A-M'],['testB','T-B-M'],
    ['researchA','R-A-main'],['researchB','R-B-main'],['researchC','R-C-main'],
    ['researchD','R-D-main'],['researchE','R-E-main'],['researchF','R-F-main']
  ]);
  function openScreen(id) { location.assign(endpoint(`/ui/${encodeURIComponent(id)}`)); }
  const picker = document.createElement('select');
  picker.setAttribute('aria-label','12候補を切り替える');
  picker.style.cssText = 'position:fixed;top:6px;left:40%;z-index:2000;display:none;padding:10px';
  for (const [family,id] of familyStart) {
    const option=document.createElement('option');option.value=id;
    option.textContent=family + (family.startsWith('research')?'':'（再構成中）');
    option.disabled=!family.startsWith('research');
    picker.append(option);
  }
  picker.value='R-A-main';
  picker.addEventListener('change',()=> action('screen',{id:picker.value}).then(()=>openScreen(picker.value)).catch(e=>message(e.message)));
  document.body.append(picker);
  const viewPicker = document.createElement('select');
  viewPicker.setAttribute('aria-label','29画面IDを選択');
  viewPicker.style.cssText = 'position:fixed;top:54px;left:40%;z-index:2000;display:none;padding:10px';
  viewPicker.addEventListener('change',()=>action('screen',{id:viewPicker.value})
    .then(()=>openScreen(viewPicker.value)).catch(e=>message(e.message)));
  document.body.append(viewPicker);
  document.addEventListener('keydown',event=>{
    if (event.ctrlKey && event.shiftKey && event.key.toLowerCase()==='u') {
      event.preventDefault();
      const visible=picker.style.display==='none';
      picker.style.display=visible?'block':'none';
      viewPicker.style.display=visible?'block':'none';
    }
  });
  document.querySelectorAll('a[href$=".html"]').forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault();
    const filename=link.getAttribute('href').split('/').pop();
    const prefix=screenId.split('-')[1];
    const suffix=filename.replace('.html','').replace(/^A_|^E_/,'');
    const target=`R-${prefix}-${suffix.replaceAll('_','-')}`;
    if (state.value?.workspace.screens.some(row=>row.id===target)) {
      action('screen',{id:target}).then(()=>openScreen(target)).catch(e=>message(e.message));
    } else message('この候補内の補助画面は原画未提供です。別候補へ自動切替しません。');
  }));
  snapshot().then(()=>{
    for (const row of state.value.workspace.screens) {
      const option=document.createElement('option');
      option.value=row.id;
      option.textContent=`${row.id} — ${row.name}` + (row.id.startsWith('R-')?'':'（再構成中）');
      option.disabled=!row.id.startsWith('R-');
      viewPicker.append(option);
    }
    viewPicker.value=screenId;
  }).catch(error=>message(error.message));
  setInterval(()=>snapshot().catch(()=>{}), 1200);
  refreshFrame();
})();
