"""Editable Windows UI for the ten raster-only legacy audit screens.

The audit's measured rectangles are the placement source of truth. These
screens use real controls and the same App adapter as the research screens;
the raster references are never used as an interactive background.
"""
from __future__ import annotations

from html import escape


SCREEN_IDS = frozenset({"L02-M", "L03-N", "L03-D", "L05-M", "L06-L", "L06-E",
                        "T-B-M", "T-B-S", "T-B-C", "T-B-F"})


def _button(label: str, action: str = "", value: str = "", cls: str = "") -> str:
    attrs = f' data-action="{escape(action)}"' if action else ""
    attrs += f' data-action-value="{escape(value)}"' if value else ""
    return f'<button class="{cls}"{attrs}>{escape(label)}</button>'


def _scene_list() -> str:
    return ('<h2>検出シーン <span data-ui="scene-count">全0件</span></h2><div class="region-pad">'
            + _button('試合全体スキャン', 'scan', cls='primary full')
            + '<p class="subtle" data-ui="scan-status">未スキャン</p>'
            + '<div class="filters">' + _button('すべて', 'event_mode', 'both')
            + _button('キル', 'event_mode', 'kill') + _button('アシスト', 'event_mode', 'assist') + '</div>'
            + '<div class="scene-rows"><div class="scene-card" data-ui="scene-card-0">'
            + '<span class="check"></span><span class="time">--:--</span>'
            + '<span class="side">—</span><strong>キル</strong></div></div>'
            + '<div class="row">' + _button('全選択', 'check_all') + _button('全解除', 'uncheck_all') + '</div>'
            + '</div>')


def _frame_cards() -> str:
    cards = ''.join(f'<div class="material-card" data-ui="material-card-{i}">'
                    '<img class="frame-thumb" alt="監査済み素材"><h3>読み込み中</h3><span class="badge"></span>'
                    '</div>' for i in range(4))
    return '<h2>キルフレーム <small>正式合格／確認用を表示</small></h2><div class="material-list">' + cards + '</div>'


def _camera_modes() -> str:
    return ('<h2>カメラモード</h2><div class="camera-choices">'
            '<div class="camera-card"><b>従来の手動カメラ</b><small>従来の視点</small></div>'
            '<div class="camera-card"><b>固定視点＋自動構図補正</b><small>視点を保ち構図を補正</small></div>'
            '<div class="camera-card"><b>フルオートシネマ</b><small>キルシーンを自動撮影</small></div>'
            '</div>')


def _camera_numbers() -> str:
    fields = [('third_dist', '距離', '900', '500', '1400'),
              ('cam_height', '高さ', '420', '0', '900'),
              ('third_yaw', '角度', '0', '-180', '180')]
    return '<h2>カメラパラメータ</h2>' + ''.join(
        f'<label class="number-row">{label}<input data-setting="{key}" type="range" min="{minimum}" max="{maximum}" value="{value}">'
        f'<input data-setting="{key}" type="number" min="{minimum}" max="{maximum}" value="{value}" aria-label="{label}"></label>'
        for key, label, value, minimum, maximum in fields)


def _side_buttons() -> str:
    return ('<h2>対象サイド</h2><div class="target-side row">'
            + _button('BLUE', 'camera_side', 'BLUE', 'blue')
            + _button('RED', 'camera_side', 'RED', 'red')
            + _button('自動', 'camera_side', 'auto') + '</div>'
            + '<p data-ui="target-name">TargetLock：未選択</p>')


def _timeline() -> str:
    return ('<h2>タイムライン <span data-ui="selected-scene-label">シーン未選択</span></h2>'
            '<div class="ruler"><span>—</span><span>—</span><span>—</span><span>—</span>'
            '<span>—</span><span>—</span><span>—</span></div>'
            '<div class="lane"><span class="lane-label">検出シーン</span><div class="lane-bar">'
            '<span class="kill-line"></span></div></div>'
            '<div class="trim">キル前 <input type="number" data-setting="pre" value="5" min="1" max="15" step="0.5"> 秒　'
            'キル後 <input type="number" data-setting="post" value="3" min="1" max="15" step="0.5"> 秒</div>')


def _material_library() -> str:
    return ('<h2>ライブラリ</h2><div class="region-pad">'
            + _button('試合全体スキャン', 'scan', cls='primary full')
            + '<div class="row tabs">' + _button('検出シーン', 'scan')
            + _button('キルフレーム', 'work_gallery') + _button('エフェクト', 'work_settings')
            + '</div><p class="subtle">素材の正式合格と確認用を区別します。</p>'
            + _frame_cards() + _button('図鑑の全候補を見る', 'work_gallery', cls='full') + '</div>')


def _view_switcher(screen_id: str) -> str:
    groups = {
        'L03-N': [('通常', 'L03-N'), ('詳細', 'L03-D')],
        'L03-D': [('通常', 'L03-N'), ('詳細', 'L03-D')],
        'L06-L': [('ライブラリ', 'L06-L'), ('編集', 'L06-E')],
        'L06-E': [('ライブラリ', 'L06-L'), ('編集', 'L06-E')],
    }
    test_group = [('全体', 'T-B-M'), ('画面設定', 'T-B-S'),
                  ('カメラ', 'T-B-C'), ('キル演出', 'T-B-F')]
    views = test_group if screen_id.startswith('T-B-') else groups.get(screen_id, [])
    if not views:
        return ''
    return '<div class="view-switcher" aria-label="同じ候補の画面切替">' + ''.join(
        _button(label, 'screen', target, 'active' if target == screen_id else '')
        for label, target in views) + '</div>'


def _component(screen_id: str, region: str) -> str:
    is_test = screen_id.startswith('T-')
    if region == 'header':
        title = {'L02-M':'動画編集ソフト標準型','L03-N':'ハイブリッド固定プレビュー型',
                 'L03-D':'ハイブリッド固定プレビュー型・詳細','L05-M':'ステップウィザード型',
                 'L06-L':'ライブラリ＋編集分離型','L06-E':'ライブラリ＋編集分離型・編集',
                 'T-B-M':'カメラ・エフェクトテスト','T-B-S':'カメラテスト設定',
                 'T-B-C':'カメラテスト設定','T-B-F':'キル演出設定'}[screen_id]
        return ('<div class="brand"><b class="app-icon">L</b><strong>LoL AutoCine</strong>'
                f'<span>{escape(title)}</span></div>' + _view_switcher(screen_id) + '<nav>'
                + _button('UI候補', 'choose_screen') + _button('リプレイを開く', 'open_replay')
                + _button('基本設定', 'native_settings') + _button('ログ', 'diagnostics')
                + '<select id="theme" aria-label="表示テーマ"><option value="system">Windows追従</option>'
                  '<option value="light">ライト</option><option value="dark">ダーク</option></select>'
                + _button('動画を作成', 'export_menu', cls='primary') + '</nav>')
    if region == 'scene-list': return _scene_list()
    if region == 'library':
        return ('<div class="row tabs">' + _button('シーン', 'scan')
                + _button('キルフレーム', 'work_gallery')
                + _button('エフェクト', 'work_settings') + '</div>' + _scene_list())
    if region == 'material-library': return _material_library()
    if region == 'preview-panel':
        return '<h2>ミラープレビュー <span class="connection-state">LoL未接続</span></h2>'
    if region == 'preview-stage':
        return '<img class="game-image" alt="実LoLミラー映像"><span class="preview-tag">LoLミラー未接続</span>'
    if region == 'preview-controls':
        return (_button('ミラー開始', 'mirror_start', cls='primary')
                + _button('ミラー停止', 'mirror_stop')
                + _button('演出プレビュー再生', 'preview_play')
                + _button('プレビュー停止', 'preview_stop'))
    if region in {'camera-cards','camera-modes'}: return _camera_modes()
    if region in {'frame-cards','materials','material-summary','applied-assets'}: return _frame_cards()
    if region == 'effect-cards':
        return '<h2>エフェクト</h2><p class="subtle">選択した枠と同名FXを適用</p>' + _button('FX設定', 'work_settings')
    if region in {'side-buttons','target-side'}: return _side_buttons()
    if region in {'camera-numeric'}: return _camera_numbers()
    if region == 'inspector':
        if is_test and screen_id != 'T-B-S':
            return '<h2>設定 <small>独立スクロール</small></h2>'
        return ('<h2>かんたん設定</h2><div class="region-pad">'
                + _camera_numbers() + '<h2>プレビュー用</h2>'
                + _button('基本設定', 'native_settings') + _button('詳細編集', 'edit_mode', 'advanced')
                + '</div>')
    if region == 'output':
        return ('<h2>出力設定</h2><div class="output-summary">'
                '<span>1920 × 1080</span><span data-ui="output-fps">60 fps</span><span>MP4</span></div>'
                + _button('出力先を選択', 'output_folder') + _button('動画を作成', 'export_menu', cls='primary'))
    if region == 'timeline': return _timeline()
    if region in {'edit-tabs','bottom-tabs'}:
        return ('<div class="edit-mode row">' + _button('簡単編集', 'edit_mode', 'easy')
                + _button('詳細編集', 'edit_mode', 'advanced') + '</div>')
    if region == 'step-tabs':
        return '<h2>① 試合を選ぶ　　② シーンを探す　　③ 見た目を整える　　④ 書き出す</h2>'
    if region == 'step-actions':
        return _button('戻る', 'choose_screen') + _button('次へ：書き出す', 'export_menu', cls='primary')
    if region == 'edit-links':
        return _button('簡単編集', 'edit_mode', 'easy') + _button('詳細編集', 'edit_mode', 'advanced')
    if region == 'proceed': return _button('編集へ進む', 'screen', 'L06-E', 'primary')
    if region == 'motion-grid':
        labels=['一気に表示','左から登場','右から登場','下から登場','上から登場','パッと飛び出す']
        return '<h2>登場アニメ</h2><div class="motion-grid">' + ''.join(
            f'<button class="motion">{label}</button>' for label in labels) + '</div>'
    if region in {'side-qa','test-results'}:
        return ('<h2>' + ('BLUE / RED カメラQA' if region=='side-qa' else 'テスト結果') + '</h2>'
                '<p class="subtle">実行後に結果とログを表示します。</p>'
                + _button('カメラ＋Work素材一括QA', 'camera_qa') + _button('ログ', 'diagnostics'))
    if region == 'scene-detail':
        return '<h2>選択シーン</h2><p data-ui="selected-scene-label">シーン未選択</p>' + _button('選択シーンへ移動', 'jump_selected')
    return '<h2>' + escape(region) + '</h2>'


def render_legacy(screen: dict) -> str:
    screen_id = screen['id']
    if screen_id not in SCREEN_IDS:
        raise ValueError(f'not a reconstructed legacy screen: {screen_id}')
    width, height = screen['resolution']
    parts = []
    for region in screen['regions']:
        x,y,w,h = region['rect']
        name = region['id']
        preview_class = ' preview-stage' if name == 'preview-stage' else ''
        parts.append(f'<section class="region region-{escape(name)}{preview_class}" data-ui="{escape(name)}" '
                     f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
                     + _component(screen_id,name) + '</section>')
    return (f'<!doctype html><html lang="ja" data-theme="light"><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>LoL AutoCine — {escape(screen["family_name"])} {screen_id}</title>'
            '<link rel="stylesheet" href="reconstructed.css">'
            f'<body data-screen="{screen_id}" data-plan="{escape(screen["family"])}">'
            f'<main id="legacy-canvas" style="width:{width}px;height:{height}px">'
            + ''.join(parts) + '</main>'
            f'<script>function fitLegacy(){{let c=document.getElementById("legacy-canvas");'
            f'let s=Math.min(innerWidth/{width},innerHeight/{height});'
            'c.style.transform=`scale(${s})`;c.style.left=`${(innerWidth-c.offsetWidth*s)/2}px`;'
            'c.style.top=`${(innerHeight-c.offsetHeight*s)/2}px`}'
            'addEventListener("resize",fitLegacy);fitLegacy();</script>'
            '<script src="ui.js"></script></body></html>')
