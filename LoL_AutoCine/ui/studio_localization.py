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
def convert_label(key, labels):
    return labels.get(key, key)
def reverse_label(value, labels):
    return next((key for key,label in labels.items() if label==value), value if value in labels else next(iter(labels)))
