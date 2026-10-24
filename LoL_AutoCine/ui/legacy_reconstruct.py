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


def _legacy02_library() -> str:
    slots = ''.join(
        f'<div class="scene-card" data-ui="scene-card-{i}">'
        '<span class="check"></span><span class="scene-thumb-placeholder">映像未取得</span>'
        '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>'
        for i in range(6))
    return ('<div class="row tabs">' + _button('▣ シーン', 'scan', cls='selected')
            + _button('♜ キルフレーム', 'work_gallery')
            + _button('✧ エフェクト', 'work_settings') + '</div>'
            '<div class="legacy2-scan">' + _button('⌕ 試合全体スキャン', 'scan', cls='full') + '</div>'
            '<h2>検出シーン <span data-ui="scene-count">全0件</span></h2>'
            '<p class="subtle" data-ui="scan-status">未スキャン</p>'
            '<div class="legacy2-scene-grid">' + slots + '</div>'
            '<div class="legacy2-selected-scene"><strong>選択中のシーン：</strong>'
            '<span data-ui="selected-scene-label">シーン未選択</span>'
            '<div class="row">' + _button('全選択', 'check_all')
            + _button('全解除', 'uncheck_all') + '</div></div>')


def _legacy03_scene_list(count: int = 3) -> str:
    slots = ''.join(
        f'<div class="scene-card" data-ui="scene-card-{i}">'
        '<span class="check"></span><span class="scene-thumb-placeholder">映像未取得</span>'
        '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>'
        for i in range(count))
    return ('<h2>検出シーン</h2><div class="legacy3-scan">'
            + _button('⌕ 試合全体スキャン', 'scan', cls='full') + '</div>'
            '<p class="legacy3-count">検出されたシーン <span data-ui="scene-count">全0件</span></p>'
            '<p class="subtle" data-ui="scan-status">未スキャン</p>'
            '<div class="legacy3-scene-list">' + slots + '</div>')


def _legacy03_inspector(detailed: bool) -> str:
    header = ('<h2>かんたん設定</h2><div class="legacy3-edit-mode edit-mode">'
              + _button('簡単編集', 'screen', 'L03-N', 'selected' if not detailed else '')
              + _button('詳細編集', 'screen', 'L03-D', 'selected' if detailed else '')
              + '</div>')
    if detailed:
        return (header + '<div class="legacy3-property-tabs">'
                + _button('カメラ', 'native_editor_zone', 'camera', 'selected')
                + _button('フレーム', 'work_gallery')
                + _button('エフェクト', 'work_settings') + '</div>'
                + '<h2>カメラショット</h2>' + _camera_modes() + _camera_numbers()
                + '<div class="legacy3-detail-actions">'
                + _button('TargetLockを設定', 'native_settings')
                + _button('カメラをリセット', 'native_settings') + '</div>')
    presets = (('おすすめ', 'Lolnam風スムーズ'),
               ('迫力重視', 'Lolnam風ダイナミック'),
               ('シンプル', '三人称 自然め'))
    return (header + '<h2>プリセット</h2><div class="legacy3-presets">'
            + ''.join(_button(label, 'easy_preset', preset, 'legacy3-preset')
                      for label, preset in presets) + '</div>'
            + '<p class="subtle">現在：<span data-ui="easy-preset-name">—</span></p>'
            + '<div class="legacy3-control">カメラ移動量 <small>速度の独立設定は未対応</small>'
            '<input data-setting="motion_dolly" type="range" min="0" max="15" step="0.5" value="3">'
            '<input data-setting="motion_dolly" type="number" min="0" max="15" step="0.5" value="3"></div>'
            + '<div class="legacy3-control">エフェクトの強さ'
            + _button('弱', 'effect_strength', 'weak')
            + _button('強', 'effect_strength', 'strong') + '</div>'
            + '<div class="legacy3-checks"><label><input type="checkbox" data-hud-visible>HUDを表示する</label>'
            + _button('TargetLockを設定', 'native_settings')
            + _button('37キルバッジの設定', 'work_gallery') + '</div>')


def _legacy05_inspector() -> str:
    presets = (('✦ おすすめ', 'Lolnam風スムーズ', 'バランスの取れた定番の演出'),
               ('◆ 落ち着いた演出', '三人称 自然め', 'シンプルで見やすい仕上がり'),
               ('♨ 迫力ある演出', 'Lolnam風ダイナミック', 'ダイナミックで印象的な仕上がり'))
    return ('<div class="legacy5-inspector-head"><h2>見た目を整える</h2>'
            + _button('簡単編集', 'edit_mode', 'easy', 'selected')
            + _button('詳細編集', 'edit_mode', 'advanced') + '</div>'
            '<h2>おすすめ設定から始めましょう</h2>'
            '<p class="subtle">シーンに合わせた演出で、魅力的なハイライトに仕上げます。</p>'
            '<div class="legacy5-presets">'
            + ''.join(f'<button class="legacy3-preset" data-action="easy_preset" '
                      f'data-action-value="{escape(value)}"><strong>{escape(label)}</strong>'
                      f'<small>{escape(note)}</small></button>'
                      for label, value, note in presets) + '</div>'
            '<p class="subtle">現在：<span data-ui="easy-preset-name">—</span></p>'
            '<div class="legacy5-control">カメラ移動量 <small>速度の独立設定は未対応</small>'
            '<input data-setting="motion_dolly" type="range" min="0" max="15" step="0.5" value="3">'
            '<input data-setting="motion_dolly" type="number" min="0" max="15" step="0.5" value="3"></div>'
            '<div class="legacy5-control">エフェクトの強さ'
            + _button('弱', 'effect_strength', 'weak')
            + _button('強', 'effect_strength', 'strong') + '</div>'
            + _button('詳細設定を開く', 'native_settings', cls='legacy5-details'))


def _legacy05_steps() -> str:
    steps = (('1', '試合を選ぶ', 'open_replay'), ('2', 'シーンを探す', 'focus_scene'),
             ('3', '見た目を整える', ''), ('4', '書き出す', 'export_menu'))
    return '<div class="legacy5-steps">' + ''.join(
        f'<button class="{"selected" if number == "3" else ""}"'
        + (f' data-action="{action}"' if action else ' disabled')
        + f'><b>{number}</b><span>{escape(label)}</span></button>'
        for number, label, action in steps) + '</div>'


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


def _legacy03_timeline(include_trim: bool = True) -> str:
    lanes = ('検出シーン', 'カメラ', 'キルフレーム', 'エフェクト')
    return ('<h2>タイムライン <span data-ui="selected-scene-label">シーン未選択</span></h2>'
            '<div class="ruler"><span>—</span><span>—</span><span>—</span><span>—</span>'
            '<span>—</span><span>—</span><span>—</span></div>'
            + ''.join('<div class="lane"><span class="lane-label">' + label +
                      '</span><div class="lane-bar"><span class="kill-line"></span></div></div>'
                      for label in lanes)
            + ('<div class="trim">キル前 <input type="number" data-setting="pre" value="5" min="1" max="15" step="0.5"> 秒　'
               'キル後 <input type="number" data-setting="post" value="3" min="1" max="15" step="0.5"> 秒</div>'
               if include_trim else ''))


def _material_library() -> str:
    return ('<h2>ライブラリ</h2><div class="region-pad">'
            + _button('試合全体スキャン', 'scan', cls='primary full')
            + '<div class="row tabs">' + _button('検出シーン', 'scan')
            + _button('キルフレーム', 'work_gallery') + _button('エフェクト', 'work_settings')
            + '</div><p class="subtle">素材の正式合格と確認用を区別します。</p>'
            + _frame_cards() + _button('図鑑の全候補を見る', 'work_gallery', cls='full') + '</div>')


def _legacy06_library() -> str:
    cards = ''.join(
        f'<button class="legacy6-library-card" data-ui="library-card-{i}">'
        '<img class="frame-thumb" alt="実素材"><span class="library-card-name">読み込み中</span>'
        '<span class="badge"></span></button>' for i in range(6))
    scenes = ''.join(
        f'<button class="legacy6-scene scene-card" data-ui="scene-card-{i}">'
        '<span class="check"></span><span class="scene-thumb-placeholder">映像未取得</span>'
        '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></button>'
        for i in range(3))
    return ('<h2>ライブラリ</h2><div class="legacy6-library-body">'
            + _button('⌕ 試合全体スキャン', 'scan', cls='full legacy6-scan')
            + '<div class="legacy6-library-tabs">' + _button('検出シーン', 'screen', 'L06-E')
            + '<button class="selected" disabled aria-current="page">キルフレーム</button>'
            + _button('エフェクト', 'work_settings') + '</div>'
            '<input class="legacy6-search" type="search" placeholder="フレームを検索" aria-label="フレームを検索">'
            '<div class="legacy6-library-filters">'
            '<button data-library-filter="all" class="selected">すべて</button>'
            '<button data-library-filter="approved">正式合格</button>'
            '<button data-library-filter="review">確認用</button></div>'
            '<div class="legacy6-library-grid">' + cards + '</div>'
            + _button('図鑑の全候補を見る', 'work_gallery', cls='full legacy6-full-gallery')
            + '<div class="legacy6-scene-strip"><h2>検出されたシーン <span data-ui="scene-count">全0件</span></h2>'
            '<p data-ui="scan-status" class="subtle">未スキャン</p>'
            '<div class="legacy6-scenes">' + scenes + '</div></div></div>')


def _legacy06_scene_list() -> str:
    scenes = ''.join(
        f'<div class="scene-card" data-ui="scene-card-{i}">'
        '<span class="check"></span><span class="scene-thumb-placeholder">映像未取得</span>'
        '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>'
        for i in range(6))
    return ('<h2>使用するシーン</h2><div class="legacy6-edit-scan">'
            + _button('⌕ 試合全体スキャン', 'scan', cls='full') + '</div>'
            '<p class="legacy6-scene-count">選択中のシーン：<span data-ui="scene-count">全0件</span></p>'
            '<p class="subtle" data-ui="scan-status">未スキャン</p>'
            '<div class="legacy6-edit-scenes">' + scenes + '</div>'
            + _button('‹ ライブラリで選び直す', 'screen', 'L06-L', 'full legacy6-back'))


def _legacy06_inspector(library: bool) -> str:
    if library:
        return ('<h2>選択中：<span data-ui="selected-frame-name">キルフレーム未選択</span></h2>'
                '<div class="legacy6-selected-preview"><img class="selected-frame-thumb" alt="選択中の実素材">'
                '<span class="selected-frame-empty">素材を選択してください</span></div>'
                + _button('演出プレビューで確認', 'preview_play', cls='primary full')
                + '<p class="subtle" data-ui="selected-frame-status">素材は未選択</p>'
                '<h2>カメラ <small>プレビュー用</small></h2><div class="legacy6-choice-row">'
                + _button('自動シネマ', 'camera_mode', 'full_auto')
                + _button('固定自動', 'camera_mode', 'fixed_auto')
                + _button('手動', 'camera_mode', 'manual') + '</div>'
                '<h2>エフェクト <small>同名FXがあれば同期</small></h2>'
                '<div class="legacy6-choice-row">'
                + _button('弱', 'effect_strength', 'weak')
                + _button('強', 'effect_strength', 'strong')
                + _button('詳細', 'work_settings') + '</div>')
    return ('<h2>編集設定</h2><div class="legacy6-edit-tabs">'
            + _button('簡単編集', 'edit_mode', 'easy')
            + _button('詳細編集', 'edit_mode', 'advanced', 'selected') + '</div>'
            '<div class="legacy6-property-tabs">'
            + _button('カメラ', 'native_editor_zone', 'camera', 'selected')
            + _button('キルフレーム', 'work_gallery')
            + _button('エフェクト', 'work_settings') + '</div>'
            '<h2>カメラの動き</h2><div class="legacy6-choice-row">'
            + _button('自動シネマ', 'camera_mode', 'full_auto')
            + _button('固定自動', 'camera_mode', 'fixed_auto')
            + _button('手動', 'camera_mode', 'manual') + '</div>'
            + _camera_numbers()
            + '<label class="legacy6-hud"><input type="checkbox" data-hud-visible>HUDを表示する</label>'
            + _button('TargetLockを設定', 'native_settings', cls='full'))


def _legacy06_applied() -> str:
    return ('<h2>適用中のアセット</h2><div class="legacy6-applied-row">'
            '<button data-action="native_settings"><strong>カメラ</strong><span data-ui="selected-camera-mode">現在の設定</span></button>'
            '<button data-action="work_gallery"><strong>キルフレーム</strong>'
            '<img class="selected-frame-thumb" alt="選択中の実素材">'
            '<span data-ui="selected-frame-name">未選択</span></button>'
            '<button data-action="work_settings"><strong>エフェクト</strong>'
            '<span data-ui="selected-effect-name">未選択</span></button>'
            + _button('ライブラリを開く', 'screen', 'L06-L') + '</div>')


def _testb_scene_list() -> str:
    scenes = ''.join(
        f'<div class="scene-card" data-ui="scene-card-{i}">'
        '<span class="check"></span><span class="scene-thumb-placeholder">映像未取得</span>'
        '<strong>未スキャン</strong><span class="time">--:--</span><span class="side">—</span></div>'
        for i in range(6))
    return ('<h2>シーンリスト</h2><div class="testb-scan">'
            + _button('試合全体スキャン', 'scan', cls='primary full') + '</div>'
            '<h3>キル・アシストフィルター</h3><div class="filters">'
            + _button('キル', 'event_mode', 'kill')
            + _button('アシスト', 'event_mode', 'assist')
            + _button('キル＋アシスト', 'event_mode', 'both') + '</div>'
            '<h3>検出シーン <span data-ui="scene-count">全0件</span></h3>'
            '<p class="subtle" data-ui="scan-status">未スキャン</p>'
            '<div class="testb-scenes">' + scenes + '</div>'
            '<div class="testb-scene-actions">' + _button('全選択', 'check_all')
            + _button('全解除', 'uncheck_all') + '</div>')


def _testb_camera_modes() -> str:
    modes = (
        ('従来の手動カメラ', 'manual', 'プレイヤー操作に近いカメラワーク', 'testb-qa-1'),
        ('固定視点＋自動構図補正', 'fixed_auto', '状況に応じて見やすい構図へ自動補正', 'testb-qa-3'),
        ('フルオートシネマ', 'full_auto', 'キルシーンを自動で撮影', 'testb-qa-6'),
    )
    return '<h2>カメラモード</h2><div class="testb-mode-list">' + ''.join(
        f'<button class="camera-card" data-action="camera_mode" data-action-value="{value}">'
        f'<span class="testb-qa-shot {shot}" title="過去QA画像・現在のプレビューではありません"></span>'
        f'<strong>{escape(label)}</strong><small>{escape(note)}</small></button>'
        for label, value, note, shot in modes) + '</div>'


def _testb_camera_cards() -> str:
    cards = (
        ('三人称', 'third', 'testb-qa-6'),
        ('三人称シネマ', 'third_cinema', 'testb-qa-7'),
        ('FPS風', 'fps', 'testb-qa-8'),
        ('Lolnamシネマ', 'lolnam_cinema', 'testb-qa-9'),
    )
    return ('<h2>画像選択 <small>過去QA画像</small></h2><div class="testb-style-cards">'
            + ''.join(f'<button data-action="camera_style" data-action-value="{value}">'
                      f'<span class="testb-qa-shot {shot}"></span><small>{escape(label)}</small></button>'
                      for label, value, shot in cards) + '</div>')


def _testb_camera_settings_cards() -> str:
    """The camera test reference shows ten choices in two rows of five."""
    cards = (
        ('三人称シネマ', 'third_cinema', 'testb-qa-7'),
        ('三人称', 'third', 'testb-qa-6'),
        ('Geo Aim', 'geo_aim', 'testb-qa-9'),
        ('シネマ', 'cinema', 'testb-qa-3'),
        ('FPS風', 'fps', 'testb-qa-8'),
        ('Orbit', 'orbit', 'testb-qa-1'),
        ('Lolnamシネマ', 'lolnam_cinema', 'testb-qa-9'),
        ('Follow', 'follow', 'testb-qa-6'),
        ('俯瞰シネマ', 'cinema_top', 'testb-qa-3'),
        ('俯瞰', 'top', 'testb-qa-1'),
    )
    return ('<h2>カメラスタイル <small>10種・過去QA画像</small></h2>'
            '<div class="testb-style-cards testb-style-grid">'
            + ''.join(f'<button data-action="camera_style" data-action-value="{value}">'
                      f'<span class="testb-qa-shot {shot}" '
                      'title="過去QA画像・現在のプレビューではありません"></span>'
                      f'<small>{escape(label)}</small></button>'
                      for label, value, shot in cards) + '</div>')


def _testb_camera_numbers() -> str:
    fields = (
        ('third_dist', '距離', '900', '500', '1400', '1'),
        ('cam_height', '高さ', '420', '0', '900', '1'),
        ('third_yaw', '回転角', '0', '-180', '180', '1'),
        ('motion_arc', '回り込み', '14', '0', '45', '0.5'),
        ('motion_dolly', '接近量', '5', '0', '15', '0.5'),
    )
    return '<h2>カメラパラメータ</h2><div class="testb-number-grid">' + ''.join(
        f'<label class="number-row"><span>{label}</span>'
        f'<input data-setting="{key}" type="range" min="{minimum}" max="{maximum}" '
        f'step="{step}" value="{value}">'
        f'<input data-setting="{key}" type="number" min="{minimum}" max="{maximum}" '
        f'step="{step}" value="{value}" aria-label="{label}"></label>'
        for key, label, value, minimum, maximum, step in fields) + '</div>'


def _testb_camera_qa() -> str:
    return ('<h2>BLUE / RED の確認済み候補</h2>'
            '<div class="testb-qa-side">'
            + _button('BLUE', 'camera_side', 'BLUE', 'blue')
            + '<span>確認済み：<b data-ui="blue-qa-count">未取得</b></span>'
            + _button('RED', 'camera_side', 'RED', 'red')
            + '<span>確認済み：<b data-ui="red-qa-count">未取得</b></span></div>'
            '<p class="subtle">候補の詳細は一括QA実行後に確認できます。</p>'
            + _button('カメラ＋Work素材一括QA', 'camera_qa', cls='full'))


def _testb_results() -> str:
    return ('<div class="testb-results-head"><h2>テスト結果 <small>画面への結果同期は未対応</small></h2>'
            + _button('診断ログ', 'diagnostics') + '</div>'
            '<div class="testb-results-table"><div>サイド</div><div>実行結果</div>'
            '<div>確認済み候補</div><div>BLUE</div><div>ログで確認</div><div>未取得</div>'
            '<div>RED</div><div>ログで確認</div><div>未取得</div></div>'
            '<p class="subtle">一括QA実行後の詳細は診断ログで確認してください。</p>')


def _testb_material_summary() -> str:
    return ('<h2>フレーム・エフェクト・モーション</h2><div class="testb-material-links">'
            + _button('キルフレーム図鑑', 'work_gallery')
            + _button('同名FX設定', 'work_settings')
            + _button('登場アニメ6種', 'screen', 'T-B-F') + '</div>'
            '<p>枠：<span data-ui="selected-frame-name">未選択</span></p>'
            '<p>FX：<span data-ui="selected-effect-name">未選択</span></p>')


def _testb_timeline() -> str:
    film = ''.join('<span class="film-placeholder">映像未取得</span>' for _ in range(13))
    return ('<h2>キル選択タイムライン <small>検出後に実シーンを表示</small></h2>'
            '<div class="ruler"><span>—</span><span>—</span><span>—</span><span>—</span>'
            '<span>—</span><span>—</span><span>—</span></div>'
            '<div class="lane"><span class="lane-label">試合全体</span>'
            '<div class="lane-bar"><div class="testb-film-strip">' + film + '</div>'
            '<span class="kill-line"></span></div></div>'
            '<div class="trim"><span data-ui="selected-scene-label">シーン未選択</span>'
            ' キル前 <input type="number" data-setting="pre" value="5" min="1" max="15" step="0.5"> 秒'
            ' キル後 <input type="number" data-setting="post" value="3" min="1" max="15" step="0.5"> 秒'
            + _button('この範囲をプレビュー', 'preview_play') + '</div>')


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
        if screen_id == 'L02-M':
            return ('<div class="legacy2-brand"><strong>LoL AutoCine</strong>'
                    '<span data-ui="replay-header">リプレイ未接続</span></div>'
                    '<div class="legacy2-topnav">'
                    + _button('▣ 素材', 'work_gallery')
                    + _button('▣ 編集', 'edit_mode', 'advanced', 'active')
                    + _button('▤ 書き出し', 'export_menu') + '</div>'
                    '<nav class="legacy2-settings">'
                    + _button('⚙ 基本設定', 'native_settings')
                    + _button('GPU', 'native_settings')
                    + _button('音声', 'native_settings')
                    + _button('HUD', 'native_settings')
                    + _button('TargetLock', 'native_settings')
                    + _button('37キルバッジ', 'work_gallery')
                    + _button('書き出し', 'export_menu', cls='primary') + '</nav>')
        if screen_id in {'L03-N', 'L03-D'}:
            return ('<div class="legacy3-brand"><strong>LoL AutoCine</strong>'
                    '<span data-ui="replay-header">リプレイ未接続</span></div>'
                    '<div class="legacy3-topnav">'
                    + _button('試合', 'open_replay')
                    + _button('編集', 'edit_mode', 'advanced' if screen_id == 'L03-D' else 'easy', 'active')
                    + _button('書き出し', 'export_menu') + '</div>'
                    '<nav class="legacy3-settings">'
                    + _button('⚙ 基本設定', 'native_settings')
                    + _button('GPU', 'native_settings')
                    + _button('音声', 'native_settings')
                    + _button('HUD', 'native_settings')
                    + _button('TargetLock', 'native_settings')
                    + _button('37キルバッジ', 'work_gallery')
                    + _button('書き出し', 'export_menu', cls='primary') + '</nav>')
        if screen_id in {'L06-L', 'L06-E'}:
            return ('<div class="legacy6-brand"><strong>LoL AutoCine</strong>'
                    '<span data-ui="replay-header">リプレイ未接続</span></div>'
                    '<div class="legacy6-topnav">' + _view_switcher(screen_id) + '</div>'
                    '<nav class="legacy6-settings">'
                    + _button('⚙ 基本設定', 'native_settings')
                    + _button('GPU', 'native_settings')
                    + _button('音声', 'native_settings')
                    + _button('HUD', 'native_settings')
                    + _button('TargetLock', 'native_settings')
                    + _button('37キルバッジ', 'work_gallery')
                    + _button('書き出し', 'export_menu', cls='primary') + '</nav>')
        if screen_id.startswith('T-B-'):
            return ('<div class="testb-brand"><b class="app-icon">L</b><strong>LoL AutoCine</strong>'
                    '<span>UI改善案・実動作比較</span><em>B案｜カメラ・エフェクトテスト</em></div>'
                    '<div class="testb-topnav">' + _view_switcher(screen_id) + '</div>'
                    '<nav class="testb-settings">'
                    + _button('リプレイを開く', 'open_replay')
                    + _button('準備', 'prepare')
                    + _button('GPU・音声・HUD設定', 'native_settings')
                    + _button('ログ', 'diagnostics')
                    + _button('動画を作成', 'export_menu', cls='primary') + '</nav>')
        if screen_id == 'L05-M':
            return ('<div class="legacy3-brand"><strong>LoL AutoCine</strong>'
                    '<span data-ui="replay-header">リプレイ未接続</span></div>'
                    '<nav class="legacy3-settings">'
                    + _button('⚙ 基本設定', 'native_settings')
                    + _button('GPU', 'native_settings')
                    + _button('音声', 'native_settings')
                    + _button('HUD', 'native_settings')
                    + _button('TargetLock', 'native_settings')
                    + _button('37キルバッジ', 'work_gallery')
                    + _button('書き出し', 'export_menu', cls='primary') + '</nav>')
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
    if region == 'scene-list':
        if screen_id in {'T-B-M', 'T-B-C'}:
            return _testb_scene_list()
        if screen_id in {'L03-N', 'L03-D', 'L05-M'}:
            return _legacy03_scene_list(5 if screen_id == 'L05-M' else 3)
        if screen_id == 'L06-E':
            return _legacy06_scene_list()
        return _scene_list()
    if region == 'library':
        if screen_id == 'L02-M':
            return _legacy02_library()
        return ('<div class="row tabs">' + _button('シーン', 'scan')
                + _button('キルフレーム', 'work_gallery')
                + _button('エフェクト', 'work_settings') + '</div>' + _scene_list())
    if region == 'material-library':
        return _legacy06_library() if screen_id == 'L06-L' else _material_library()
    if region == 'preview-panel':
        return '<h2>ミラープレビュー <span class="connection-state">LoL未接続</span></h2>'
    if region == 'preview-stage':
        return '<img class="game-image" alt="実LoLミラー映像"><span class="preview-tag">LoLミラー未接続</span>'
    if region == 'preview-controls':
        return (_button('ミラー開始', 'mirror_start', cls='primary')
                + _button('ミラー停止', 'mirror_stop')
                + _button('演出プレビュー再生', 'preview_play')
                + _button('プレビュー停止', 'preview_stop'))
    if screen_id in {'T-B-M', 'T-B-C'} and region == 'camera-modes': return _testb_camera_modes()
    if screen_id == 'T-B-M' and region == 'camera-cards': return _testb_camera_cards()
    if screen_id == 'T-B-C' and region == 'camera-cards': return _testb_camera_settings_cards()
    if region in {'camera-cards','camera-modes'}: return _camera_modes()
    if screen_id == 'T-B-M' and region == 'material-summary': return _testb_material_summary()
    if region == 'applied-assets' and screen_id == 'L06-E': return _legacy06_applied()
    if region in {'frame-cards','materials','material-summary','applied-assets'}: return _frame_cards()
    if region == 'effect-cards':
        return '<h2>エフェクト</h2><p class="subtle">選択した枠と同名FXを適用</p>' + _button('FX設定', 'work_settings')
    if screen_id == 'T-B-C' and region == 'side-buttons': return _side_buttons()
    if screen_id == 'T-B-M' and region == 'side-buttons':
        return ('<div class="target-side testb-side-buttons">'
                + _button('BLUE サイド', 'camera_side', 'BLUE', 'blue')
                + _button('RED サイド', 'camera_side', 'RED', 'red') + '</div>')
    if region in {'side-buttons','target-side'}: return _side_buttons()
    if region in {'camera-numeric'}:
        return _testb_camera_numbers() if screen_id == 'T-B-C' else _camera_numbers()
    if region == 'inspector':
        if screen_id == 'T-B-M':
            return ('<div class="testb-inspector-tabs">'
                    + _button('カメラ', 'screen', 'T-B-C', 'selected')
                    + _button('キル演出', 'screen', 'T-B-F') + '</div>')
        if screen_id == 'T-B-C':
            return ('<div class="testb-inspector-tabs">'
                    + _button('カメラ', 'screen', 'T-B-C', 'selected')
                    + _button('キル演出', 'screen', 'T-B-F') + '</div>')
        if is_test and screen_id != 'T-B-S':
            return '<h2>設定 <small>独立スクロール</small></h2>'
        if screen_id in {'L03-N', 'L03-D'}:
            return _legacy03_inspector(screen_id == 'L03-D')
        if screen_id == 'L05-M':
            return _legacy05_inspector()
        if screen_id in {'L06-L', 'L06-E'}:
            return _legacy06_inspector(screen_id == 'L06-L')
        if screen_id == 'L02-M':
            return ('<h2>プロパティ</h2><div class="legacy2-property-tabs">'
                    + _button('カメラ', 'native_settings', cls='selected')
                    + _button('キルフレーム', 'work_gallery')
                    + _button('エフェクト', 'work_settings') + '</div>'
                    + _camera_numbers()
                    + '<div class="legacy2-hud"><label><input type="checkbox" data-hud-toggle>'
                      'HUDを隠す</label></div>')
        return ('<h2>かんたん設定</h2><div class="region-pad">'
                + _camera_numbers() + '<h2>プレビュー用</h2>'
                + _button('基本設定', 'native_settings') + _button('詳細編集', 'edit_mode', 'advanced')
                + '</div>')
    if region == 'output':
        return ('<h2>出力設定</h2><div class="output-summary">'
                '<span>1920 × 1080</span><span data-ui="output-fps">60 fps</span><span>MP4</span></div>'
                + _button('出力先を選択', 'output_folder') + _button('動画を作成', 'export_menu', cls='primary'))
    if region == 'timeline':
        if screen_id in {'T-B-M', 'T-B-C'}: return _testb_timeline()
        return (_legacy03_timeline(include_trim=screen_id in {'L03-N', 'L03-D'})
                if screen_id in {'L03-N', 'L03-D', 'L05-M', 'L06-L', 'L06-E'}
                else _timeline())
    if region in {'edit-tabs','bottom-tabs'}:
        return ('<div class="edit-mode row">' + _button('簡単編集', 'edit_mode', 'easy')
                + _button('詳細編集', 'edit_mode', 'advanced') + '</div>')
    if region == 'step-tabs':
        return _legacy05_steps()
    if region == 'step-actions':
        return _button('戻る', 'focus_scene') + _button('次へ：書き出す', 'export_menu', cls='primary')
    if region == 'edit-links':
        if screen_id == 'L06-L':
            return ('<div class="legacy6-edit-links">'
                    + _button('簡単編集', 'edit_mode', 'easy', 'selected')
                    + _button('詳細編集', 'edit_mode', 'advanced')
                    + _button('編集画面で調整 →', 'screen', 'L06-E') + '</div>')
        return _button('簡単編集', 'edit_mode', 'easy') + _button('詳細編集', 'edit_mode', 'advanced')
    if region == 'proceed': return _button('編集へ進む', 'screen', 'L06-E', 'primary')
    if region == 'motion-grid':
        labels=['一気に表示','左から登場','右から登場','下から登場','上から登場','パッと飛び出す']
        return '<h2>登場アニメ</h2><div class="motion-grid">' + ''.join(
            f'<button class="motion">{label}</button>' for label in labels) + '</div>'
    if region in {'side-qa','test-results'}:
        if screen_id == 'T-B-C':
            return _testb_camera_qa() if region == 'side-qa' else _testb_results()
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
