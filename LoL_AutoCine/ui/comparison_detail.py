"""Clearly labelled comparison detail views when the audit has no original image.

These are additional routes, not entries in the 29-screen visual audit.
They share the same runtime/client as the audited screens.
"""
from __future__ import annotations

from html import escape


DERIVED_DETAILS = {
    "researchB": ("Creator", "プリセットから細部へ", "R-B-main", "creator"),
    "researchC": ("Director", "ショットから細部へ", "R-C-main", "director"),
    "testA": ("現行整理", "従来の編集領域", "T-A-M", "classic"),
}


def render_detail(family: str, token: str) -> str:
    title, subtitle, main_id, layout = DERIVED_DETAILS[family]
    controls = '''
      <section class="box camera-box" data-ui="camera-modes"><h2>カメラ設定</h2>
        <div class="choice-row">
          <button class="camera-card" data-action="camera_mode" data-action-value="manual">従来の手動カメラ</button>
          <button class="camera-card" data-action="camera_mode" data-action-value="fixed_auto">固定視点＋自動構図補正</button>
          <button class="camera-card" data-action="camera_mode" data-action-value="full_auto">フルオートシネマ</button>
        </div><div class="target-side choice-row"><button data-action="camera_side" data-action-value="BLUE">BLUE</button>
          <button data-action="camera_side" data-action-value="RED">RED</button>
          <button data-action="camera_side" data-action-value="auto">自動</button></div>
        <div class="numbers"><label>距離 <input type="number" data-setting="third_dist" step="10"></label>
          <label>高さ <input type="number" data-setting="cam_height" step="10"></label>
          <label>角度 <input type="number" data-setting="third_yaw" step="1"></label>
          <label>回り込み <input type="number" data-setting="motion_arc" step="1"></label></div>
        <p>現在：<strong data-ui="selected-camera-mode">—</strong></p>
        <button data-action="native_editor_zone" data-action-value="camera">既存の詳細カメラ編集を開く</button>
      </section>
      <section class="box asset-box"><h2>キルフレーム・素材</h2>
        <p>選択中：<strong data-ui="selected-frame-name">未選択</strong></p>
        <p data-ui="selected-frame-status">品質状態を確認中</p>
        <div class="asset-grid">
          <button class="material-card" data-ui="material-card-0"><img class="frame-thumb" alt=""><h3>素材</h3><span class="badge">—</span></button>
          <button class="material-card" data-ui="material-card-1"><img class="frame-thumb" alt=""><h3>素材</h3><span class="badge">—</span></button>
          <button class="material-card" data-ui="material-card-2"><img class="frame-thumb" alt=""><h3>素材</h3><span class="badge">—</span></button>
        </div><button data-action="work_gallery">Work素材図鑑を開く</button>
      </section>
      <section class="box fx-box"><h2>FX・登場アニメ</h2>
        <p>同名FX：<strong data-ui="selected-effect-name">未選択</strong></p>
        <div class="choice-row"><button data-action="effect_strength" data-action-value="weak">弱</button>
          <button data-action="effect_strength" data-action-value="strong">強</button>
          <button data-action="work_settings">FX設定を開く</button></div>
        <div class="motion-grid">
          <button class="motion" data-action="motion" data-action-value="instant">一気に表示</button>
          <button class="motion" data-action="motion" data-action-value="slide_left">左から登場</button>
          <button class="motion" data-action="motion" data-action-value="slide_right">右から登場</button>
          <button class="motion" data-action="motion" data-action-value="slide_up">下から登場</button>
          <button class="motion" data-action="motion" data-action-value="slide_down">上から登場</button>
          <button class="motion" data-action="motion" data-action-value="pop">パッと飛び出す</button>
        </div><button data-action="native_editor_zone" data-action-value="fx">既存の詳細FX編集を開く</button>
      </section>
      <section class="box finishing-box"><h2>色・シーン編集</h2>
        <p>色・キーフレームの細部は既存編集画面で調整します。</p>
        <div class="choice-row"><button data-action="native_editor_zone" data-action-value="color">色調整を開く</button>
          <button data-action="native_editor_zone" data-action-value="scene">シーン編集を開く</button>
          <button data-action="scene_save">このシーンに保存</button>
          <button data-action="scene_undo">元に戻す</button></div>
      </section>'''
    scene = '''<section class="box scenes" data-ui="scene-list"><h2>検出シーン</h2>
      <button data-action="scan">試合全体スキャン</button><p data-ui="scan-status">未スキャン</p>
      <div class="scene-card" data-ui="scene-card-0"><span class="check"></span>
        <strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>
      <div class="scene-card" data-ui="scene-card-1"><span class="check"></span>
        <strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>
      <button data-action="native_editor_zone" data-action-value="scene">シーン一覧・タイムライン編集へ</button>
    </section>'''
    preview = '''<section class="box preview-panel" data-ui="preview-panel"><div class="preview-heading">
      <h2>ミラープレビュー</h2><span class="connection-state">LoL未接続</span></div>
      <div class="preview-stage" data-ui="preview-stage"><img class="game-image" alt="LoLミラー未接続">
        <span class="preview-tag">LoL未接続</span></div>
      <div class="playbar" data-ui="preview-controls"><button data-action="mirror_start">ミラー開始</button>
        <button data-action="mirror_stop">ミラー停止</button>
        <button data-action="preview_play">演出プレビュー再生</button>
        <button data-action="preview_stop">プレビュー停止</button></div>
    </section>'''
    if layout == "creator":
        body = f'<aside class="column">{scene}{controls.split("<section class=\"box asset-box\"")[0]}</aside><main class="column">{preview}<div class="controls">' + '<section class="box asset-box"' + controls.split('<section class="box asset-box"', 1)[1] + '</div></main>'
    elif layout == "director":
        body = f'<aside class="column">{scene}</aside><main class="column">{preview}<div class="controls">{controls}</div></main>'
    else:
        body = f'<aside class="column">{scene}{controls}</aside><main class="column">{preview}</main>'
    return f'''<!doctype html><html lang="ja" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>AutoCine {escape(title)} 詳細比較</title>
<link rel="stylesheet" href="/runtime/comparison-detail.css?token={escape(token)}"></head>
<body class="detail-{layout}"><header><strong>LoL AutoCine</strong><span>{escape(title)} / {escape(subtitle)}</span>
  <span class="draft">原画像未提供・比較用派生詳細</span><button data-action="open_replay">リプレイを開く</button>
  <button data-action="native_settings">基本設定</button><button data-action="export_menu">動画を作成</button></header>
<nav class="comparison-nav"><button data-compare="main">← メインに戻る</button>
  <strong>詳細編集</strong><button data-action="edit_mode" data-action-value="advanced">既存の詳細編集も開く</button></nav>
<div class="workspace">{body}</div>
<section class="box timeline" data-ui="timeline"><h2>タイムライン</h2><div class="ruler"><span>—</span><span>—</span><span>—</span></div>
  <div class="lane"><strong class="lane-label">スキャン後に表示</strong><div class="lane-bar"><span class="kill-line"></span></div></div>
  <div class="trim"><label>キル前 <input type="number" data-setting="pre" value="5" step="0.1">秒</label>
    <label>キル後 <input type="number" data-setting="post" value="3" step="0.1">秒</label></div></section>
<footer>この派生詳細には監査原画像がありません。29画面の画像一致判定には含めません。LoL接続・書き出しは実機未検証です。</footer>
<script>window.AUTOCINE_TOKEN={token!r};window.AUTOCINE_SCREEN={main_id!r};
window.AUTOCINE_DERIVED_DETAIL={family!r};</script>
<script src="/runtime/client.js?token={escape(token)}"></script></body></html>'''
