"""Candidate-3 refinement views. Presentation only; one existing App owns all state.

The Work SVG/PNG files are measurements and references, never rendered as a
clickable image. The original T-A-M HTML remains the unmodified baseline.
"""
from __future__ import annotations

import json


VARIANTS = {"p", "s"}


def render(variant: str, token: str) -> str:
    if variant not in VARIANTS:
        raise ValueError("unknown C3 variant")
    label = "C3-P 精密編集" if variant == "p" else "C3-S かんたん編集"
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LoL AutoCine — {label}</title>
<link rel="stylesheet" href="/runtime/c3.css?token={token}"></head>
<body data-variant="{variant}">
<header class="topbar"><strong class="brand">AutoCine</strong><span class="viewname">候補3 / {label} 比較</span>
 <nav aria-label="画面と機能"><button data-route="/ui/T-A-M">元の候補3</button><button data-route="/ui3/p">C3-P</button><button data-route="/ui3/s">C3-S</button>
 <button data-action="open_replay">リプレイ</button><button data-action="prepare">準備</button>
 <button data-action="native_settings">基本設定</button><button data-action="diagnostics">ログ</button>
 <button class="primary" data-drawer="review">作成内容を確認</button></nav></header>
<main class="shell">
 <aside class="panel left" data-ui="replay-target"><h2>1. リプレイ準備・対象</h2>
  <label class="muted">リプレイファイル</label><div class="filebox" id="replay-file">接続待ち</div>
  <button class="primary wide" data-action="prepare">準備状態を確認</button>
  <p class="status" id="connection">LoL未接続</p><h3>TargetLock / 注目プレイヤー</h3>
  <div id="players" class="playerlist"></div><button class="footbutton" data-action="native_editor_zone" data-zone="scene">テンプレート・参考</button>
 </aside>
 <section class="center"><section class="panel preview" data-ui="preview"><div class="previewhead"><h2>ミラープレビュー</h2><span id="connection-pill">未接続</span></div>
   <div class="video" data-ui="mirror-image"><img id="live-frame" alt="LoLミラー映像"><div id="video-empty">LoL未接続・映像はまだありません</div></div>
   <div class="transport"><button data-action="mirror_start">ミラー開始</button><button data-action="mirror_stop">停止</button>
    <button class="primary" data-action="preview_play">演出を再生</button><button data-action="preview_stop">プレビュー停止</button>
    <span id="fps">実測 — fps</span></div></section></section>
 <aside class="panel right" data-ui="scene-list"><h2>2. 試合全体から見せ場を選ぶ</h2>
  <button class="primary wide" data-action="scan">試合全体スキャン</button><p class="status" id="scan-status">未スキャン</p>
  <div class="filters"><button data-mode="both">すべて</button><button data-mode="kill">キル</button><button data-mode="assist">アシスト</button></div>
  <div id="scenes" class="scenelist"></div><button class="footbutton" data-action="jump_selected">選択シーンへ移動</button>
 </aside>
 <section class="editor panel" data-ui="editor"><div class="editbar"><button data-tab="easy">かんたん編集</button><button data-tab="detail">詳細編集</button>
  <button data-tab="scene">シーン</button><button data-tab="camera">カメラ</button><button data-tab="fx">色・FX</button><button data-tab="output">出力</button>
  <button data-tab="test">テスト結果</button><span class="editnote" id="selected-scene">選択：なし</span></div>
  <div class="mini-timeline" data-ui="mini-timeline" aria-label="常設シーンタイムラインとキル前後トリム">
   <span class="mini-label">シーン</span><div class="mini-events" id="mini-events"></div>
   <label>前 <input id="trim-pre" data-trim="pre" type="number" min="1" max="15" step="0.5" aria-label="キル前の秒数"></label>
   <label>後 <input id="trim-post" data-trim="post" type="number" min="1" max="15" step="0.5" aria-label="キル後の秒数"></label>
   <button data-tab="scene" aria-label="タイムラインを拡大">拡大</button></div>
  <div id="editor-content"></div></section>
 <footer><span>候補3の基本構造を保持。研究案は正式採用前の比較ビューです。</span><span id="footer-state">実LoL検証 NOT_RUN</span></footer>
</main>
<div class="drawer" id="drawer" hidden><div class="drawerhead"><h2 id="drawer-title">設定</h2><button id="drawer-close" aria-label="閉じる">×</button></div><div id="drawer-body"></div>
 <div class="drawerfoot"><button id="drawer-cancel">キャンセル</button><button id="drawer-apply" class="primary">適用</button></div></div>
<div class="modalback" id="modalback" hidden><div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
 <h2 id="modal-title">作成内容を確認</h2><div id="modal-body"></div><div class="modalactions"><button id="modal-cancel">戻る</button><button id="modal-export" class="primary">チェック済みシーンから作成</button></div></div></div>
<div class="toast" id="toast" role="status" hidden></div>
<script>window.AUTOCINE_TOKEN={json.dumps(token)};window.AUTOCINE_C3_VARIANT={json.dumps(variant)};</script>
<script src="/runtime/c3.js?token={token}"></script></body></html>'''
