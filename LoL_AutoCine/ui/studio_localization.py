# -*- coding: utf-8 -*-
"""Japanese display only, IDs in project JSON/FFmpeg unchanged."""
SHOT_PROFILE_JA = {"auto":"自動", "smooth":"なめらか", "cinematic":"シネマ", "dynamic":"ダイナミック"}
SHOT_INTENSITY_JA = {"natural":"自然", "standard":"標準", "strong":"強め"}
FOG_LABEL_JA = {"teal":"青緑の霧", "sand":"砂色の霧", "white":"白い霧", "emerald":"エメラルドの霧", "cream":"クリーム色の霧"}
EFFECT_LABEL_JA = {
 "motion_camera":"カメラ移動", "radial_blur":"放射状ぼかし", "zoom_blur":"ズームぼかし",
 "glitch":"映像ノイズ", "kaleidoscope":"万華鏡", "vhs_damage":"VHS風ノイズ",
 "block_motion":"ブロック移動", "spin_motion":"回転演出", "chroma_leak":"色ずれ",
 "flash":"閃光", "focus_blur":"全体ぼかし", "vignette_fx":"周辺減光",
 "glint":"輝き", "camera_shake":"カメラの揺れ", "wiggle":"小刻みな揺れ",
 "vr_blur":"VR風ぼかし", "vr_light_leak":"光漏れ（フィルム焼け）",
 "sphere_blur":"球状ぼかし", "panel_wipe":"パネル切替", "stretch_wipe":"伸縮切替",
 "mirror":"左右反転", "slice":"画面スライス",
}
# Short, plain-language effect descriptions shown directly in the UI.
EFFECT_HELP_JA = {
    "motion_camera": "録画後の画面を少し動かす演出。実際のReplay APIカメラとは別です。",
    "radial_blur": "連続フレームを重ねて動きを強調します。強くすると残像が増えます。",
    "zoom_blur": "拡大と残像で勢いを出します。キル時の強調に向きます。",
    "glitch": "色ずれと細かなノイズで、一瞬の乱れを作ります。",
    "kaleidoscope": "左右の反転映像を薄く重ねて、万華鏡風に見せます。",
    "vhs_damage": "古いビデオ風の色ずれ・ノイズです。画質が荒くなります。",
    "block_motion": "画面全体がブロック状になります。強くすると粗いモザイクに近づきます。",
    "spin_motion": "画面全体をわずかに左右へ回転させます。",
    "chroma_leak": "キル瞬間に赤・青の輪郭をずらします。",
    "flash": "キルの瞬間に短い白い閃光を入れます。",
    "focus_blur": "映像全体を柔らかくします。キャラだけを残すなら下の『円形DOF』を使います。",
    "vignette_fx": "画面の周囲を暗くして中心へ視線を集めます。",
    "glint": "輪郭と明るい部分を少し強調します。",
    "camera_shake": "撃破時などに画面を細かく揺らします。強すぎると見づらくなります。",
    "wiggle": "画面を小刻みにゆらして動きを足します。",
    "vr_blur": "画面全体を柔らかくぼかします。",
    "vr_light_leak": "光がレンズに漏れたような暖色の演出を入れます。",
    "sphere_blur": "球状の光をイメージした全体ぼかし。円形にピントを残す機能ではありません。",
    "panel_wipe": "クリップ冒頭を短くフェードさせます。",
    "stretch_wipe": "映像冒頭の切替を柔らかくします。",
    "mirror": "左右を反転します。ゲーム画面の左右が入れ替わります。",
    "slice": "画面を水平移動させる演出。端に違和感が出る場合があります。",
}

TEMPLATE_HELP_JA = {
    "クリア・アクション（視認性重視）": "色をほぼ変えず、キャラの動きを見やすく。初めての自動編集におすすめ。",
    "アイスブルー・シネマ": "青いハイライトと穏やかな移動。落ち着いたLoLモンタージュ向け。",
    "ゴールド・フィニッシュ": "暖かい金色と短い光。キルの締めをきれいに見せたい時に。",
    "エピック・チームファイト": "安全な俯瞰ベースで集団戦全体を見せる。派手な回転は控えめ。",
    "ネオン・モンタージュ": "発色が強めのハイライト。明るい演出が好きな人向け。",
    "Lolnam風スムーズ": "急なカメラ移動を避け、自然につなぐ落ち着いた演出。",
}

def convert_label(key, labels):
    return labels.get(key, key)
def reverse_label(value, labels):
    return next((key for key,label in labels.items() if label==value), value if value in labels else next(iter(labels)))
