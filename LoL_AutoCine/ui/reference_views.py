"""Opt-in native WebView presentation for the two Work reference layouts.

This implementation is new code based on the approved PNG/specification
measurements.  It does not embed the retired research demo or its mock store.
All operations use the same UI29Server/Audit29Runtime as candidate 3.
"""
from __future__ import annotations

import html
import json


VIEWS = ("main", "easy", "detail", "camera", "curve", "color", "material", "export")


def render(variant: str, token: str) -> str:
    if variant not in ("ld", "ln"):
        raise ValueError("unknown reference UI")
    title = "Track Desk" if variant == "ld" else "Shot Canvas"
    subtitle = "League Director参考・パラメーターを俯瞰する" if variant == "ld" else "Lolnam参考・映像からショットを仕上げる"
    nav = "".join(f'<button type="button" data-view="{view}">{label}</button>' for view, label in (
        ("main", "メイン"), ("easy", "かんたん"), ("detail", "詳細編集"), ("camera", "カメラ"),
        ("curve", "カーブ"), ("color", "色調整"), ("material", "素材"), ("export", "出力")))
    rail_nav = "".join(f'<button type="button" data-view="{view}"><span aria-hidden="true">{icon}</span>{label}</button>'
                       for view, icon, label in (("easy", "✦", "かんたん"),
                                                 ("detail", "▤", "詳細編集"),
                                                 ("camera", "◉", "カメラ"),
                                                 ("curve", "⌁", "カーブ"),
                                                 ("color", "◐", "色調整"),
                                                 ("material", "◇", "素材"),
                                                 ("export", "▣", "出力")))
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LoL AutoCine — {html.escape(title)}</title>
<link rel="stylesheet" href="/runtime/reference.css?token={token}"></head>
<body data-variant="{variant}">
<header class="topbar"><strong class="logo">AC</strong><strong>AutoCine</strong><span class="research">REFERENCE</span>
<div class="variants"><button data-route="candidate3">候補3</button><button data-route="ld" class="{'active' if variant == 'ld' else ''}">League Director</button><button data-route="ln" class="{'active' if variant == 'ln' else ''}">Lolnam</button></div>
<span class="project">LoL AutoCine ・ UI比較試験</span><span class="spacer"></span>
<button data-action="scene_undo" title="選択シーンの編集を元に戻す">↶</button><button data-action="scene_redo" title="選択シーンの編集をやり直す">↷</button>
<select id="theme" aria-label="画面テーマ"><option value="light">ライト</option><option value="dark">ダーク</option><option value="system">Windows追従</option></select>
<button data-action="project_export">保存</button><button data-action="project_import">開く</button>
<button id="help-open">操作ガイド</button><button data-action="native_settings">設定</button></header>
<div class="navrow"><div class="view-title"><strong>{html.escape(title)}</strong><small>{html.escape(subtitle)}</small></div>
<nav class="topnav" aria-label="編集画面">{nav}</nav><span id="connection" class="connection">状態を確認中</span></div>
<main class="workspace">
<aside class="scene-pane"><div class="pane-head"><strong>見せ場を選ぶ</strong><span id="scene-count">0</span></div>
<small id="scan-note">LoL接続後に実データを表示</small><button data-action="scan" class="scan-button">試合全体スキャン</button>
<div id="scene-list" class="scene-list"></div></aside>
<aside class="tool-rail" aria-label="操作レール">{rail_nav}</aside>
<section class="center"><div class="preview-head"><strong id="scene-title">シーン未選択</strong><span>16:9</span><button id="compare-view" disabled title="実ミラーの調整前後比較は未接続です。演出再生は下の操作群から行えます">調整前と比較</button></div>
<div class="preview-stage"><img id="mirror-image" alt="実ミラープレビュー" hidden><div id="preview-offline">LoL未接続・実ミラー待機中<br><small>見本映像ではありません</small></div></div>
<div class="transport"><button data-action="mirror_start">▶ ミラー開始</button><button data-action="mirror_stop">■ ミラー停止</button><button data-action="preview_play">▶ 演出確認</button><button data-action="preview_stop">■ 停止</button><span id="preview-fps">実測 — fps</span></div>
{'' if variant == 'ln' else '<div class="shot-strip" id="shot-strip"></div>'}</section>
<aside class="inspector"><div class="pane-head"><strong id="inspector-title">メイン</strong><small id="inspector-status">実状態を表示</small></div>
<div id="inspector-body" class="inspector-body"></div></aside>
</main>
<section class="timeline">{'<div class="shot-strip" id="shot-strip"></div>' if variant == 'ln' else ''}<div class="timeline-head"><strong>ショットの時間を整える</strong><small>実シーンと編集設定</small><span class="spacer"></span><button data-view="detail">キーフレーム</button><button data-view="curve">カーブ</button><button data-action="native_editor_zone" data-data='{{"zone":"camera"}}'>詳細編集を開く</button></div>
<div class="tracks"><div class="track-labels"><span>画角 FOV</span><span>回転・カメラ</span><span>キル演出</span></div><div id="timeline-tracks" class="track-canvas"></div></div>
<div class="timeline-foot"><span id="timeline-summary">試合スキャン前</span><input id="trim-pre" type="number" min="1" max="15" step="0.5" aria-label="キル前 秒">秒前
<input id="trim-post" type="number" min="1" max="15" step="0.5" aria-label="キル後 秒">秒後
<button data-view="export">出力へ</button></div></section>
<footer><span id="message" role="status">実LoL・録画・音声の検証状況は結果画面で確認してください</span><span>AutoCine共通バックエンド ・ 比較用表示層</span></footer>
<dialog id="shot-check-dialog" aria-label="出力対象シーン"><h2>出力対象シーン</h2><p>表示中のショットと動画へ入れるショットは別々に選べます。</p><div id="shot-check-list"></div><button type="button" id="shot-check-close">閉じる</button></dialog>
<dialog id="help-dialog" aria-label="操作ガイド"><h2>操作ガイド</h2><ol><li>実LoLリプレイを開き、試合全体をスキャンします。</li><li>シーンを選択し、出力対象はチェックで別に指定します。</li><li>カメラ・素材・色・出力を設定し、実プレビューで確認します。</li><li>出力前にLoL接続と録画状態を確認してください。</li></ol><p>絶対FOV、自由Bezier、調整前後比較などは現在未接続です。</p><button type="button" id="help-close">閉じる</button></dialog>
<script>window.AUTOCINE_TOKEN={json.dumps(token)};window.AUTOCINE_VARIANT={json.dumps(variant)};</script>
<script src="/runtime/reference.js?token={token}"></script></body></html>'''
