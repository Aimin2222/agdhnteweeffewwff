/* Standalone comparison behavior layered on the unchanged Work layout.
 * The source mock renders first; this file keeps demo state and neutral labels.
 */
(() => {
  'use strict';
  const labels = {hybrid: '候補8', flow: '候補9', library: '候補10'};
  const params = new URLSearchParams(location.search);
  const layout = labels[params.get('layout')] ? params.get('layout') : 'hybrid';
  const storeKey = 'autocine-work-ui-8-10-v1';
  let state = {};
  try { state = JSON.parse(sessionStorage.getItem(storeKey) || '{}'); } catch (_) { state = {}; }
  const variant = document.querySelector('#variant');
  variant.textContent = labels[layout];
  document.title = `LoL AutoCine — ${labels[layout]}`;
  document.body.dataset.candidate = labels[layout];
  const view = params.get('view') || 'main';
  if (layout !== 'hybrid' && (view === 'detail' || view === 'camera')) {
    // Work supplied only a main reference for these two layouts. Give their
    // detail navigation a usable comparison surface in the same visual style.
    document.querySelector('#right').innerHTML =
      `<h2>${view === 'camera' ? 'カメラ・FX' : '詳細編集'}</h2>` + cameras() + fx() +
      '<button class="wide" data-pop="scene">シーンと色の詳細</button>';
  }

  function settings() {
    const values = {};
    document.querySelectorAll('.setting').forEach(group => {
      const name = group.querySelector('label')?.textContent.trim();
      const number = group.querySelector('input[type="number"]');
      if (name && number) values[name] = number.value;
    });
    return values;
  }
  function save() {
    state.theme = document.documentElement.dataset.theme;
    state.settings = {...(state.settings || {}), ...settings()};
    state.checkedScenes = [...document.querySelectorAll('.scene input[type="checkbox"]')]
      .map(input => input.checked);
    state.selectedScene = [...document.querySelectorAll('.scene')]
      .findIndex(scene => scene.classList.contains('active'));
    try { sessionStorage.setItem(storeKey, JSON.stringify(state)); } catch (_) { /* ephemeral demo */ }
  }
  function restore() {
    if (!params.has('theme') && state.theme) {
      document.documentElement.dataset.theme = state.theme;
      document.querySelector('#theme').textContent = `テーマ：${state.theme === 'dark' ? 'ダーク' : 'ライト'}`;
    }
    document.querySelectorAll('.setting').forEach(group => {
      const name = group.querySelector('label')?.textContent.trim();
      const value = state.settings?.[name];
      if (value === undefined) return;
      group.querySelectorAll('input').forEach(input => { input.value = value; });
    });
    document.querySelectorAll('.scene input[type="checkbox"]').forEach((input, index) => {
      if (state.checkedScenes && index < state.checkedScenes.length)
        input.checked = state.checkedScenes[index];
    });
    if (Number.isInteger(state.selectedScene) && state.selectedScene >= 0) {
      const scenes = [...document.querySelectorAll('.scene')];
      scenes.forEach((scene, index) => scene.classList.toggle('active', index === state.selectedScene));
    }
    if (state.asset) {
      document.querySelectorAll('button.card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('img')?.getAttribute('src') === state.asset);
      });
    }
    if (layout === 'flow' && Number.isInteger(state.flowStep)) {
      [...document.querySelectorAll('#left > button')].forEach((button, index) =>
        button.classList.toggle('selected', index === state.flowStep));
    }
  }
  restore();
  window.addEventListener('pagehide', save);
  document.addEventListener('input', event => {
    if (event.target.closest('.setting')) save();
  });
  document.addEventListener('change', event => {
    if (event.target.matches('.scene input[type="checkbox"]')) save();
  });

  const toast = document.createElement('div');
  toast.className = 'experience-toast';
  toast.setAttribute('role', 'status');
  toast.hidden = true;
  document.body.append(toast);
  let toastTimer;
  function show(message) {
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.hidden = true; }, 3600);
  }
  function navigate(targetLayout, targetView) {
    save();
    const next = new URL(location.href);
    next.search = '';
    next.searchParams.set('layout', targetLayout);
    next.searchParams.set('view', targetView);
    next.searchParams.set('theme', document.documentElement.dataset.theme || 'light');
    location.assign(next.href);
  }

  // Capture navigation before the Work mock's bubble listener reloads the page.
  document.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    if (button.dataset.layout && labels[button.dataset.layout]) {
      event.preventDefault(); event.stopImmediatePropagation();
      navigate(button.dataset.layout, 'main');
      return;
    }
    if (button.dataset.view) {
      event.preventDefault(); event.stopImmediatePropagation();
      navigate(layout, button.dataset.view);
      return;
    }
    if (button.textContent.trim() === '詳細編集へ進む') {
      event.preventDefault(); event.stopImmediatePropagation();
      navigate(layout, 'detail');
      return;
    }
    if (button.id === 'theme') {
      event.preventDefault(); event.stopImmediatePropagation();
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      button.textContent = `テーマ：${next === 'dark' ? 'ダーク' : 'ライト'}`;
      save();
      return;
    }
    if (button.textContent.trim() === '出力フォルダーを選択' ||
        button.textContent.trim() === '出力先を選び直す') {
      event.preventDefault(); event.stopImmediatePropagation();
      openPop('warning'); // explicitly a sample warning, no system file picker
      return;
    }
    if (button.matches('.card')) {
      state.asset = button.querySelector('img')?.getAttribute('src') || '';
      document.querySelectorAll('button.card').forEach(card =>
        card.classList.toggle('selected', card === button));
      save();
    }
    const flowButtons = [...document.querySelectorAll('#left > button')];
    if (layout === 'flow' && flowButtons.includes(button)) {
      state.flowStep = flowButtons.indexOf(button);
      flowButtons.forEach((item, index) => item.classList.toggle('selected', index === state.flowStep));
      save();
    }
    const demoActions = new Map([
      ['試合全体スキャン', '見本のシーンを表示しています。LoLへの接続・スキャンは行いません。'],
      ['ミラー開始', '中央は構図見本です。LoLミラーには接続しません。'],
      ['ミラー停止', '見本表示を維持します。実ミラーの停止操作はありません。'],
      ['▶ 演出をプレビュー', '演出プレビューの操作見本です。動画は再生・録画しません。'],
      ['■ 停止', '操作見本を停止しました。録画ジョブはありません。'],
      ['このシーンへ適用', '選択した見本素材を現在のシーンに記録しました。実動画には適用しません。'],
      ['シーン設定を保存', 'この体験版内の設定を保持しました。AutoCine本体は変更しません。']
    ]);
    const message = demoActions.get(button.textContent.trim());
    if (message) { save(); show(message); }
  }, true);

  document.addEventListener('click', event => {
    const scene = event.target.closest('.scene');
    if (scene && !event.target.matches('input')) {
      document.querySelectorAll('.scene').forEach(item => item.classList.toggle('active', item === scene));
      save();
    }
  });

  // The original compare dialog is built on demand; relabel it without altering
  // its measured geometry or the Work research originals.
  function relabelDialog() {
    const dialog = document.querySelector('#dialog');
    if (!dialog?.open) return;
    dialog.querySelectorAll('[data-layout]').forEach(button => {
      const label = labels[button.dataset.layout];
      if (label && button.textContent !== label) button.textContent = label;
    });
    const paragraph = [...dialog.querySelectorAll('p')]
      .find(item => item.textContent.includes('P1/P2/P3'));
    if (paragraph) paragraph.textContent = paragraph.textContent.replace('P1/P2/P3', '候補8/9/10');
  }
  new MutationObserver(relabelDialog).observe(document.querySelector('#dialog'),
    {childList: true, subtree: true});
  relabelDialog();
})();
