# -*- coding: utf-8 -*-
"""色合い・エフェクト・タイトルを ffmpeg フィルタとして組み立てる + ワンクリックテンプレート。

編集は録画後に ffmpeg で一括適用 (元の録画クリップは raw/ に残る)。
日本語タイトルは textfile=(UTF-8ファイル) 経由で渡し、文字化け/エスケープ事故を防ぐ。
"""
from __future__ import annotations
import os
import subprocess
import sys
import shutil
from dataclasses import dataclass, field, replace, asdict
from pathlib import Path
from typing import Optional

from .gpu_binary import ffmpeg_exe
FFMPEG = ffmpeg_exe()

from .kill_icons import make_event_badges, with_badges, normalize as kill_style_normalize
from .focus_fx import circular_dof_filter, focus_settings
from .gpu_bloom import GPUBlurStage, OPENCL_DEVICE
from .camera import INTENSITY
from .gpu_pipeline import detect as detect_gpu, gpu_prefix, backend_name as gpu_backend_name

# ---- 色グレード: eq(contrast/brightness/saturation/gamma) + colorbalance(影/中間/ハイライトのRGB)
NEUTRAL = dict(contrast=1.0, brightness=0.0, saturation=1.0, gamma=1.0,
               rs=0, gs=0, bs=0, rm=0, gm=0, bm=0, rh=0, gh=0, bh=0)

GRADES: dict = {
    "default":    dict(),  # No creative colour transformation
    "lolnam":     dict(contrast=1.20, saturation=1.20, rs=-0.09, bs=0.12,
                       rm=0.055, bm=-0.065, rh=0.085, bh=-0.04),
    "drama":      dict(contrast=1.22, brightness=-0.018, saturation=0.78,
                       rs=0.04, bs=-0.03, rh=0.07, gh=0.02),
    "fade":       dict(contrast=0.84, brightness=0.025, saturation=0.84, gamma=1.07),
    "highcontrast": dict(contrast=1.32, saturation=1.16, brightness=-0.012),
    "standard":   dict(),
    "film":       dict(contrast=1.10, saturation=0.82, rs=0.07, bs=-0.05, rh=0.03, gh=0.01, bh=-0.04),
    "noir":       dict(contrast=1.25, saturation=0.12, brightness=-0.03),
    "dark":       dict(contrast=1.15, brightness=-0.07, saturation=0.9, gamma=0.92),
    "sunset":     dict(contrast=1.06, saturation=1.2, rm=0.10, gm=0.02, bm=-0.10, rh=0.10, bh=-0.08),
    "midnight":   dict(contrast=1.1, saturation=0.95, brightness=-0.05, rs=-0.06, bs=0.12, bm=0.08, bh=0.05),
    "tealorange": dict(contrast=1.12, saturation=1.15, rs=-0.08, gs=0.03, bs=0.10, rm=0.04, bm=-0.04,
                       rh=0.12, gh=0.04, bh=-0.10),
    "neon":       dict(contrast=1.22, saturation=1.76, rs=0.07, bs=0.14, gm=-0.03, rh=0.08, bh=0.06),
    "purple":     dict(contrast=1.14, saturation=1.2, rm=0.13, bm=0.16, gm=-0.085, rs=0.05, bs=0.08),
    "iceblue":    dict(contrast=1.19, saturation=1.09, rs=-0.095, bs=0.14, rm=-0.06, gm=0.01,
                       bm=0.10, rh=0.02, gh=0.03, bh=0.08),
    "golden":     dict(contrast=1.17, saturation=1.14, rs=0.045, bs=-0.055, rm=0.11, gm=0.045,
                       bm=-0.045, rh=0.09, gh=0.04, bh=-0.07),
}
GRADE_JP = {
    "default": "デフォルト（色補正なし）", "lolnam": "Lolnam風シネマ",
    "drama": "ドラマ", "fade": "フェード", "highcontrast": "高コントラスト",
    "standard": "標準", "film": "フィルム", "noir": "ノワール", "dark": "ダーク", "sunset": "夕日",
    "midnight": "深夜青", "tealorange": "ティール&オレンジ", "neon": "ネオン", "purple": "紫霧", "iceblue": "アイスブルー", "golden": "シネマゴールド",
}

TRANSITIONS = {"cut": "カット", "fade": "フェード", "flash": "フラッシュ"}
FOG_PRESETS = {
    "teal": "Teal", "sand": "Sand", "white": "White", "emerald": "Emerald", "cream": "Cream"
}
FOG_RGB = {
    "teal": (0.04, 0.55, 0.52), "sand": (0.70, 0.52, 0.30), "white": (0.92, 0.92, 0.92),
    "emerald": (0.08, 0.55, 0.35), "cream": (0.96, 0.92, 0.65)
}

# Premiere / After Effects系の演出名を、AutoCineで安全に再現できる
# FFmpeg標準フィルタへマッピングする。GPU非対応フィルタはNVENCの前段で
# CPU処理になるが、デコード・スケール・エンコードはGPUを優先する。
VIDEO_EFFECT_CATEGORIES = {
    "映像切り替え": [
        ("motion_camera", "Motion Camera"), ("radial_blur", "Radial Blur"),
        ("zoom_blur", "Zoom Blur"), ("glitch", "Glitch"), ("kaleidoscope", "Kaleidoscope"),
        ("vhs_damage", "VHS Damage"), ("block_motion", "Block Motion"), ("spin_motion", "Spin Motion"),
    ],
    "キル瞬間": [("chroma_leak", "Chroma Leak"), ("flash", "Flash")],
    "映像全体": [
        ("focus_blur", "Focus Blur"), ("vignette_fx", "Vignette"), ("glint", "Glint"),
        ("camera_shake", "Camera Shake"), ("wiggle", "Wiggle"),
    ],
    "照明系": [
        ("vr_blur", "VR Blur"), ("vr_light_leak", "VR Light Leak（Film Burn）"),
        ("sphere_blur", "球体ブラー"),
    ],
    "ワイプ系": [("panel_wipe", "Panel Wipe"), ("stretch_wipe", "Stretch Wipe")],
    "Transformers": [("mirror", "Mirror"), ("slice", "Slice")],
}
VIDEO_EFFECT_LABELS = {k: label for items in VIDEO_EFFECT_CATEGORIES.values() for k, label in items}
VIDEO_EFFECT_DEFAULTS = {
    "motion_camera": 0.35, "radial_blur": 0.25, "zoom_blur": 0.25, "glitch": 0.30,
    "kaleidoscope": 0.20, "vhs_damage": 0.25, "block_motion": 0.25, "spin_motion": 0.20,
    "chroma_leak": 0.35, "flash": 0.55, "focus_blur": 0.20, "vignette_fx": 0.20,
    "glint": 0.25, "camera_shake": 0.20, "wiggle": 0.15, "vr_blur": 0.20,
    "vr_light_leak": 0.25, "sphere_blur": 0.18, "panel_wipe": 0.20, "stretch_wipe": 0.20,
    "mirror": 0.0, "slice": 0.20,
}


@dataclass
class Template:
    name: str = "カスタム"
    style: str = "cinema"            # camera.STYLES
    intensity: str = "standard"      # natural / standard / strong
    grade: str = "tealorange"
    grade_strength: float = 0.8      # 0-1.4
    temperature: float = 0.0         # -1..1 (暖色+)
    contrast: float = 1.0            # 0.6..1.6 (追加)
    vignette: float = 0.4            # 0-1
    grain: float = 0.2               # 0-1
    bloom: float = 0.25              # 0-1
    bars: float = 0.0                # 0-1 (シネマ枠 最大 約 12%)
    transition: str = "flash"        # cut/fade/flash
    title_auto: bool = False          # キル数/対戦相手を自動タイトル化
    title_text: str = ""             # 手入力タイトル (空なら文字なし)
    bpm: float = 0.0                 # >0 ならビートに合わせた明滅
    bgm_path: str = ""
    pre: float = 4.0                 # キル前秒数
    post: float = 3.0                # キル後秒数
    merge_multikill: bool = True
    lut_path: str = ""               # .cube
    fps: int = 60                 # 最終出力FPS
    capture_fps: int = 144        # 内部キャプチャFPS（LoLミラー/カメラ制御は144Hz優先）
    exposure: float = 0.0            # -0.3..0.3 (露出)
    vibrance: float = 0.0            # -1..1.5 (自然な彩度)
    game_audio: bool = True          # ゲーム音を録音して入れる
    game_volume: float = 1.0
    bgm_volume: float = 0.4            # BGMを足す時の音量 (ゲーム音が鳴る間は自動で下がる)
    hide_hud: bool = True            # 録画時にHUDを全部隠す（v2.2安全ミラー経路）
    keep_champion_bars: bool = False # HUD非表示でもチャンピオンのHPバーだけ残す
    cam_height: float = 170.0        # カメラの高さ補正 (地面に埋まる時は上げる)
    dist_scale: float = 0.8
    third_elev: float = 28.0
    third_dist: float = 950.0          # FPS風カメラの距離 (小さいほど寄る)
    third_yaw: float = 0.0             # 三人称の水平回転角（度）
    motion_arc: float = 0.0            # 自動カメラ回り込み角（度）
    motion_dolly: float = 0.0           # 自動ドリー量（%）
    motion_profile: str = "cinematic"   # smooth / cinematic / dynamic / auto
    fog_enabled: bool = False
    fog_preset: str = "teal"
    fog_strength: float = 0.0
    curve_enabled: bool = False
    curve_points: str = "0/0 0.25/0.20 0.50/0.50 0.75/0.80 1/1"
    dof_enabled: bool = False
    dof_preview: bool = False
    dof_blur: float = 0.0
    dof_focus_distance: float = 5510.0
    dof_near_distance: float = 10000.0
    dof_far_distance: float = 10000.0
    # Premiere/After Effects系の映像演出。キーはVIDEO_EFFECT_LABELSのID、値は0=OFF/0.0〜1.0=強度。
    video_effects: dict = field(default_factory=lambda: {k: 0.0 for k in VIDEO_EFFECT_DEFAULTS})
    effect_preset: str = "なし"
    # 参考動画テンプレート用メタデータ。カメラ設定は変更せず、映像演出だけを保存する。
    reference_dna: dict = field(default_factory=dict)
    reference_sources: list = field(default_factory=list)
    template_origin: str = "builtin"
    scene_keyframes: list = field(default_factory=list)  # append to preserve legacy positional fields
    montage_fx: str = "cut"  # append; optional final montage effect, legacy defaults unchanged
    smart_highlight_enabled: bool = False  # explicit automatic planning only
    smart_highlight_style: str = "auto"
    highlight_pulse: float = 0.0  # kill-timed accent, legacy graph unchanged when zero
    kill_icon_style: str = "off"  # off/simple/cinema/neon/impact
    kill_icon_position: str = "right-top"
    kill_icon_scale: float = 1.0
    kill_icon_duration: float = 1.55
    kill_icon_opacity: float = 1.0
    smart_composition: bool = False  # safer distance/elevation around the locked player
    smart_montage: bool = False  # only smart auto-edit reorders unpinned scenes
    kill_icon_players: list = field(default_factory=list)  # transient replay roster for real champion portraits
    # v5.10.0: appended to preserve historical positional Template arguments.
    encoder_policy: str = 'auto'  # auto/gpu/cpu; GPU refers to *encoding*, not the FX graph
    kill_frame_color: str = ''
    kill_glow_color: str = ''
    kill_glow_enabled: bool = True
    kill_glow_strength: float = .65
    kill_frame_width: int = 3
    kill_mark_style: str = 'auto'
    # v5.10.2: image-space focus; values appended for project compatibility.
    dof_shape: str = 'circle'  # circle (default) or band (old height approximation)
    dof_center_x: float = .50  # 0..1, approx TargetLock subject's screen position
    dof_center_y: float = .54
    dof_radius: float = .29   # normalized by screen height, not screen width
    dof_feather: float = .12  # soft circular edge
    camera_side: str = "auto"  # v5.10.5: auto / blue / red (append: old positional templates safe)
    kill_sparkle_intensity: float = 1.0  # v5.10.8: corner rays/star flares
    kill_stack_gap: int = 4  # v5.10.8: additional pixels between simultaneous kills

    def __post_init__(self) -> None:
        # v5.10.3: preserve older project JSON but retire the accidentally-added
        # circular pixelation effect. Never expose or export it again.
        if isinstance(self.video_effects, dict):
            self.video_effects = {k: v for k, v in self.video_effects.items() if k != 'center_mosaic'}

    def amp(self) -> float:
        return INTENSITY.get(self.intensity, 1.0)

    def to_dict(self) -> dict:
        data = asdict(self)
        # Saved templates may have been edited in memory after __post_init__.
        if isinstance(data.get('video_effects'), dict):
            data['video_effects'].pop('center_mosaic', None)
        return data


def one_click_templates() -> dict:
    """ワンクリック用テンプレ。lolnam の調整項目(露出/色温度/コントラスト/彩度/LUT/ブルーム…)に合わせて構成。
    ※「ジャネット風」は動画を直接視聴できていないため、定番のキルモンタージュ表現からの近似。"""
    T = Template
    return {
        "三人称シネマ": T(name="三人称シネマ", style="third_cinema", intensity="standard", grade="tealorange",
                      grade_strength=0.8, vignette=0.4, grain=0.15, bloom=0.25, bars=0.06, transition="flash"),
        "Lolnam風シネマ": T(name="Lolnam風シネマ", style="lolnam_cinema", intensity="standard", grade="tealorange",
                          grade_strength=0.8, vignette=0.35, grain=0.15, bloom=0.25, bars=0.06, transition="flash",
                          motion_arc=14.0, motion_dolly=5.0, motion_profile="auto"),
        "Lolnam風スムーズ": T(name="Lolnam風スムーズ", style="lolnam_cinema", intensity="natural", grade="film",
                          grade_strength=0.55, vignette=0.2, grain=0.1, bloom=0.12, bars=0.03, transition="fade",
                          motion_arc=8.0, motion_dolly=2.0, motion_profile="smooth"),
        "Lolnam風ダイナミック": T(name="Lolnam風ダイナミック", style="lolnam_cinema", intensity="strong", grade="tealorange",
                          grade_strength=0.85, vignette=0.45, grain=0.18, bloom=0.32, bars=0.08, transition="flash",
                          motion_arc=22.0, motion_dolly=8.0, motion_profile="dynamic"),
        "三人称 自然め": T(name="三人称 自然め", style="third", intensity="natural", grade="film",
                       grade_strength=0.5, vignette=0.2, grain=0.1, bloom=0.1, transition="fade"),
        "俯瞰シネマ (安全)": T(name="俯瞰シネマ (安全)", style="cinema_top", intensity="standard", grade="film",
                          grade_strength=0.7, vignette=0.35, grain=0.15, bloom=0.2, transition="fade"),
        "ジャネット風シネマ": T(name="ジャネット風シネマ", style="cinema", intensity="standard", grade="tealorange",
                          grade_strength=0.85, vignette=0.5, grain=0.25, bloom=0.3, bars=0.08,
                          transition="flash", bpm=0.0, vibrance=0.3),
        "自然め追従 (三人称)": T(name="自然め追従 (三人称)", style="third", intensity="natural", grade="film",
                          grade_strength=0.5, vignette=0.2, grain=0.1, bloom=0.1, transition="fade"),
        "クリーン (色補正なし)": T(name="クリーン (色補正なし)", style="follow", intensity="natural", grade="standard",
                           grade_strength=0.0, vignette=0.0, grain=0.0, bloom=0.0, bars=0.0, transition="cut",
                           title_auto=False),
        "ノワール強め": T(name="ノワール強め", style="cinema", intensity="strong", grade="noir",
                       grade_strength=1.0, vignette=0.7, grain=0.4, bloom=0.2, bars=0.1, transition="fade"),
        "ダークグレー": T(name="ダークグレー", style="cinema", intensity="standard", grade="dark",
                      grade_strength=1.0, vignette=0.55, grain=0.2, bloom=0.15, bars=0.06, transition="fade",
                      exposure=-0.05),
        "ティール・ドリーム": T(name="ティール・ドリーム", style="cinema", intensity="standard", grade="midnight",
                         grade_strength=0.9, temperature=-0.2, vignette=0.35, grain=0.12, bloom=0.45, transition="flash",
                         vibrance=0.5),
        "ネオン・モンタージュ": T(name="ネオン・モンタージュ", style="cinema", intensity="strong", grade="neon",
                          grade_strength=0.9, vignette=0.3, grain=0.1, bloom=0.5, transition="flash", bpm=128.0),
        "夕焼けシネマ": T(name="夕焼けシネマ", style="orbit", intensity="standard", grade="sunset",
                       grade_strength=0.9, temperature=0.3, vignette=0.4, grain=0.2, bloom=0.35, bars=0.06,
                       transition="fade"),
        "ヴィンテージ・フィルム": T(name="ヴィンテージ・フィルム", style="follow", intensity="natural", grade="film",
                            grade_strength=1.0, temperature=0.25, contrast=1.05, vignette=0.6, grain=0.55, bloom=0.2,
                            bars=0.07, transition="fade", exposure=0.03),
        # v5.10.8: an ungraded reference baseline and a one-click kill-glow look.
        "デフォルト（無加工カラー）": T(name="デフォルト（無加工カラー）",
                           style="third_cinema", intensity="natural",
                           grade="default", grade_strength=0,
                           vignette=0, grain=0, bloom=0, bars=0, transition="cut"),
        "ロイヤルゴールド・キルログ": T(name="ロイヤルゴールド・キルログ",
                           style="third_cinema", intensity="standard",
                           grade="golden", grade_strength=.65,
                           vignette=.16, grain=.05, bloom=.25, bars=.02, transition="flash",
                           kill_icon_style="cinema", kill_glow_enabled=True,
                           kill_glow_strength=1.4, kill_frame_color="#F6CB75",
                           kill_glow_color="#FFDB80", kill_mark_style="royal"),
        # v5.10.2: tasteful preset additions, no new camera coordinates or FPS assumptions.
        "クリア・アクション（視認性重視）": T(name="クリア・アクション（視認性重視）",
                          style="third_cinema", intensity="natural", grade="standard",
                          grade_strength=.0, vignette=.08, grain=.0, bloom=.10,
                          bars=.0, transition="cut", motion_profile="smooth",
                          motion_arc=7.0, motion_dolly=2.0),
        "アイスブルー・シネマ": T(name="アイスブルー・シネマ",
                          style="lolnam_cinema", intensity="standard", grade="iceblue",
                          grade_strength=.65, vignette=.22, grain=.08, bloom=.22,
                          bars=.02, transition="fade", motion_profile="smooth",
                          motion_arc=10.0, motion_dolly=3.0),
        "ゴールド・フィニッシュ": T(name="ゴールド・フィニッシュ",
                          style="third_cinema", intensity="standard", grade="golden",
                          grade_strength=.70, vignette=.27, grain=.09, bloom=.23,
                          bars=.04, transition="flash", motion_profile="cinematic",
                          motion_arc=13.0, motion_dolly=4.0),
        "エピック・チームファイト": T(name="エピック・チームファイト",
                          style="cinema_top", intensity="standard", grade="tealorange",
                          grade_strength=.55, vignette=.20, grain=.05, bloom=.20,
                          bars=.02, transition="cut", motion_profile="smooth",
                          motion_arc=5.0, motion_dolly=2.0, smart_composition=True),
    }


def vignette_angle(v: float) -> float:
    """ビネット強度(0-1) -> ffmpeg vignette angle。"""
    return 0.2 + 0.4 * max(0.0, min(1.0, v))


def _lerp(a: float, b: float, k: float) -> float:
    return a + (b - a) * k


def grade_values(name: str, strength: float, contrast_extra: float) -> dict:
    tgt = {**NEUTRAL, **GRADES.get(name, {})}
    v = {k: _lerp(NEUTRAL[k], tgt[k], strength) for k in NEUTRAL}
    v["contrast"] = max(0.5, min(2.0, v["contrast"] * contrast_extra))
    v["saturation"] = max(0.0, min(3.0, v["saturation"]))
    return v


def _esc_path(p: str) -> str:
    """ffmpeg フィルタ内パス用エスケープ (Windows の C: を C\\: に)。"""
    return p.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def find_jp_font() -> Optional[str]:
    cands = [
        r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\YuGothB.ttc", r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\msgothic.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def auto_title(kills: list) -> str:
    n = len(kills)
    roles = {getattr(k, "role", "kill") for k in kills}
    if roles == {"assist"}:
        return "ASSIST" if n == 1 else f"{n} ASSISTS"
    names = {1: "KILL", 2: "DOUBLE KILL", 3: "TRIPLE KILL", 4: "QUADRA KILL"}
    return names.get(n, "PENTA KILL" if n >= 5 else "KILL")


def make_title_png(text: str, w: int, h: int, dst: Path, font: Optional[str]) -> Path:
    """タイトルを透過PNGに描画 (Pillow)。drawtext 非依存・日本語OK。"""
    from PIL import Image, ImageDraw, ImageFont
    size = max(24, h // 12)
    try:
        fnt = ImageFont.truetype(font, size, index=0) if font else ImageFont.load_default()
    except Exception:
        fnt = ImageFont.load_default()
    img = Image.new("RGBA", (w, int(size * 1.9)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (w - tw) // 2 - bbox[0], (img.height - th) // 2 - bbox[1]
    d.text((x, y), text, font=fnt, fill=(255, 255, 255, 255), stroke_width=max(2, size // 18),
           stroke_fill=(0, 0, 0, 170))
    img.save(dst)
    return dst


def _fog_filter(t: Template) -> Optional[str]:
    if not t.fog_enabled or t.fog_strength <= 0.001:
        return None
    r,g,b = FOG_RGB.get(t.fog_preset, FOG_RGB["teal"])
    strength=max(0.0,min(1.0,t.fog_strength))
    # 画面全体に柔らかな色霧を重ねる。元映像のディテールを残すため低不透明度。
    return (f"color=c=0x{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}:s=16x16,format=rgba,colorchannelmixer=aa={strength:.3f}[fog];"
            "[0:v][fog]scale2ref[base][fog2];[base][fog2]blend=all_mode=softlight:all_opacity=0.35")

def _curve_filter(t: Template) -> Optional[str]:
    if not t.curve_enabled or not t.curve_points.strip():
        return None
    # FFmpeg curvesのpoint syntax。UIで入力したポイントをそのまま保存。
    pts=t.curve_points.replace(";", " ").strip().replace("'", "")
    return f"curves=all='{pts}'"


def _effect_events(kills: Optional[list], t: Template, duration: float) -> list[tuple[float, float]]:
    """キル時演出の相対時間を作る。録画クリップの先頭は kill_time-pre なので、
    ksの絶対時刻から安全にクリップ内時刻へ変換する。"""
    if not kills:
        return [(max(0.0, min(duration, float(getattr(t, "pre", 0.0)))) ,
                 max(0.0, min(duration, float(getattr(t, "pre", 0.0))) + 0.45))]
    base = float(getattr(kills[0], "time", 0.0)) - float(getattr(t, "pre", 0.0))
    out = []
    for k in kills:
        kt = float(getattr(k, "time", 0.0)) - base
        if -0.2 <= kt <= duration + 0.2:
            out.append((max(0.0, min(duration, kt)), max(0.0, min(duration, kt + 0.42))))
    return out or [(max(0.0, min(duration, float(getattr(t, "pre", 0.0)))),
                    max(0.0, min(duration, float(getattr(t, "pre", 0.0))) + 0.42))]


def _enable_expr(events: list[tuple[float, float]], before: float = 0.0, after: float = 0.0) -> str:
    parts = []
    for a, b in events:
        parts.append(f"between(t,{max(0.0,a-before):.3f},{min(99999.0,b+after):.3f})")
    return "'" + "+".join(parts or ["0"]) + "'"


def _build_video_effect_filters(t: Template, duration: float, events: list[tuple[float,float]], still: bool) -> list[str]:
    """標準FFmpegだけで動く軽量版の映像演出。
    キル瞬間系はevents、全体系はduration全体へ適用する。"""
    if still or not getattr(t, "video_effects", None):
        return []
    e = {k: max(0.0, min(1.0, float(v))) for k, v in (t.video_effects or {}).items() if float(v) > 0.001}
    f=[]
    # 全体/カメラ系。crop→scaleで出力解像度を維持する。
    if e.get("motion_camera"):
        k=e["motion_camera"]; amp=3 + 18*k
        f.append(f"crop=w=iw*0.94:h=ih*0.94:x='(iw-ow)/2+sin(2*PI*t/2.7)*{amp:.2f}':y='(ih-oh)/2+cos(2*PI*t/3.1)*{amp*0.55:.2f}',scale=1920:1080:flags=lanczos")
    if e.get("camera_shake"):
        k=e["camera_shake"]; amp=2 + 22*k
        f.append(f"crop=w=iw*0.96:h=ih*0.96:x='(iw-ow)/2+sin(2*PI*t/0.12)*{amp:.2f}':y='(ih-oh)/2+cos(2*PI*t/0.095)*{amp*0.7:.2f}',scale=1920:1080:flags=lanczos")
    if e.get("wiggle"):
        k=e["wiggle"]; amp=1 + 10*k
        f.append(f"crop=w=iw*0.98:h=ih*0.98:x='(iw-ow)/2+sin(2*PI*t/0.55)*{amp:.2f}':y='(ih-oh)/2+sin(2*PI*t/0.43)*{amp*0.7:.2f}',scale=1920:1080:flags=lanczos")
    if e.get("spin_motion"):
        k=e["spin_motion"]; ang=0.015+0.09*k
        f.append(f"rotate='sin(2*PI*t/0.8)*{ang:.5f}':ow=iw:oh=ih:fillcolor=black")
    if e.get("zoom_blur"):
        k=e["zoom_blur"]; z=0.025+0.10*k
        f.append(f"scale=w='1920*(1+{z:.4f}*abs(sin(2*PI*t/1.6)))':h='1080*(1+{z:.4f}*abs(sin(2*PI*t/1.6)))':eval=frame,crop=1920:1080:x='(iw-ow)/2':y='(ih-oh)/2',tmix=frames=3:weights='1 2 1':scale=4")
    if e.get("radial_blur"):
        k=e["radial_blur"]
        f.append(f"tmix=frames={3 if k<0.6 else 5}:weights='1 2 1'")
    if e.get("glitch"):
        k=e["glitch"]; px=int(2+18*k)
        f.append(f"rgbashift=rh={px}:bh=-{px}:enable='between(t,0,{duration:.3f})'")
        f.append(f"noise=alls={int(6+20*k)}:allf=t+u:enable='between(t,0,{duration:.3f})'")
    if e.get("kaleidoscope"):
        op=0.12+0.35*e["kaleidoscope"]
        f.append(f"split=2[k0][k1];[k1]hflip[k1f];[k0][k1f]blend=all_mode=screen:all_opacity={op:.3f}")
    if e.get("vhs_damage"):
        k=e["vhs_damage"]; px=int(1+7*k)
        f.append(f"rgbashift=rh={px}:bh=-{px},noise=alls={int(10+25*k)}:allf=t+u")
    if e.get("block_motion"):
        k=e["block_motion"]; bs=int(12+44*k)
        f.append(f"pixelize=width={bs}:height={bs}:enable='between(t,0,{duration:.3f})'")
    # キル瞬間系
    expr=_enable_expr(events, before=0.02, after=0.08)
    if e.get("chroma_leak"):
        px=int(4+32*e["chroma_leak"])
        f.append(f"rgbashift=rh={px}:bh=-{px}:enable={expr}")
    if e.get("flash"):
        amp=0.18+0.65*e["flash"]
        f.append(f"eq=brightness='{amp:.3f}*exp(-18*abs(t-{events[0][0]:.3f}))':eval=frame:enable={_enable_expr(events, after=0.15)}")
    # 全体系
    if e.get("focus_blur"):
        sigma=1.0+8.0*e["focus_blur"]
        f.append(f"scale=960:540:flags=bilinear,gblur=sigma={sigma:.2f}:steps=1,scale=1920:1080:flags=bilinear")
    if e.get("vignette_fx"):
        f.append(f"vignette=angle={1.05-0.45*e['vignette_fx']:.3f}")
    if e.get("glint"):
        f.append("unsharp=lx=5:ly=5:la=0.45")
        f.append(f"eq=contrast={1.0+0.25*e['glint']:.3f}:brightness={0.02+0.08*e['glint']:.3f}")
    if e.get("vr_blur"):
        f.append(f"scale=960:540:flags=bilinear,gblur=sigma={1.0+7.0*e['vr_blur']:.2f}:steps=1,scale=1920:1080:flags=bilinear")
    if e.get("vr_light_leak"):
        f.append(f"colorize=hue=28:saturation=0.85:lightness=0.62:mix={0.10+0.28*e['vr_light_leak']:.3f}:enable={_enable_expr(events, before=0.10, after=0.28)}")
    if e.get("sphere_blur"):
        f.append(f"scale=960:540:flags=bilinear,gblur=sigma={0.8+5.0*e['sphere_blur']:.2f}:steps=1,scale=1920:1080:flags=bilinear")
    # ワイプ：最初の0.55秒を黒から開く。1クリップ単位なので安全な単入力版。
    if e.get("panel_wipe"):
        p=0.45+0.25*e["panel_wipe"]
        f.append(f"fade=t=in:st=0:d={p:.3f}:alpha=0")
    if e.get("stretch_wipe"):
        p=0.35+0.25*e["stretch_wipe"]
        f.append(f"fade=t=in:st=0:d={p:.3f}")
    if e.get("mirror"):
        f.append("hflip")
    if e.get("slice"):
        k=e["slice"]
        f.append(f"scroll=horizontal={0.02+0.18*k:.3f}:vertical=0")
    return f


def color_filters(t: Template) -> list[str]:
    """Shared grade definition for software rendering and one-time GPU LUT bake."""
    f: list = []
    g = grade_values(t.grade, t.grade_strength, t.contrast)
    tmp = max(-1.0, min(1.0, t.temperature))      # 色温度は colorbalance に加算
    rm, bm = g["rm"] + 0.10 * tmp, g["bm"] - 0.10 * tmp
    rh, bh = g["rh"] + 0.06 * tmp, g["bh"] - 0.06 * tmp
    cl = lambda x: max(-1.0, min(1.0, x))
    bright = max(-1.0, min(1.0, g["brightness"] + 0.5 * t.exposure))
    f.append(f"eq=contrast={g['contrast']:.3f}:brightness={bright:.3f}:saturation={g['saturation']:.3f}:gamma={g['gamma']:.3f}")
    f.append("colorbalance=" + ":".join(
        f"{k}={cl(v):.3f}" for k, v in dict(rs=g["rs"], gs=g["gs"], bs=g["bs"], rm=rm, gm=g["gm"], bm=bm,
                                           rh=rh, gh=g["gh"], bh=bh).items()))
    if abs(t.vibrance) > 0.01:
        f.append(f"vibrance=intensity={max(-2.0, min(2.0, t.vibrance)):.2f}")
    if t.lut_path and os.path.exists(t.lut_path):
        f.append(f"lut3d=file='{_esc_path(t.lut_path)}'")
    cf = _curve_filter(t)
    if cf:
        f.append(cf)
    return f


def build_graph(t: Template, duration: float, has_title: bool, still: bool = False,
                pre_filters: str = "", effect_events: Optional[list[tuple[float,float]]] = None,
                gpu_blur_stage=None) -> str:
    """Legacy CPU/hybrid graph. Retained unchanged as the recovery renderer."""
    f = color_filters(t)
    f.extend(_build_video_effect_filters(t, duration, effect_events or [], still))
    # Optional CPU accent uses existing kill timestamps, independently of NVENC.
    pulse = max(0.0, min(1.0, float(getattr(t, "highlight_pulse", 0.0))))
    if pulse > 0.001 and not still and effect_events:
        from .highlight_pulse import pulse_filters
        f.extend(pulse_filters(effect_events, pulse))
    gpu_blurs = gpu_blur_stage.effects if gpu_blur_stage else set()
    if gpu_blurs:
        # Keep grade/custom CPU effects before DOF/Bloom as in the legacy graph.
        # A band DOF stays on CPU and must precede the GPU Bloom stage below.
        if 'dof' in gpu_blurs or not (t.dof_enabled and t.dof_blur > .01):
            f.append(gpu_blur_stage.graph)
    if t.dof_enabled and t.dof_blur > 0.01 and 'dof' not in gpu_blurs:
        if getattr(t, 'dof_shape', 'circle') != 'band':
            # Circular 2D focus, independent of nonexistent per-pixel replay depth.
            # The camera locks its target close to screen center; manual x/y offset
            # remains available when unusual angles move the target.
            f.append(circular_dof_filter(t))
        else:
            # Replay APIから画素ごとの深度バッファは取得できないため、
            # 2D映像の上下位置を「奥行きの代理値」として使うDOF近似。
            # 画面全体へ一律blurする旧実装とは違い、フォーカス帯だけを元画像で保持する。
            blur = max(0.0, min(20.0, float(t.dof_blur)))
            near = max(1.0, float(t.dof_near_distance))
            focus = max(near, float(t.dof_focus_distance))
            far = max(focus + 1.0, float(t.dof_far_distance))
            # 近/遠の範囲を 0..1 に正規化し、focus をその中心に置く。
            fnear = max(0.02, min(0.48, (focus - near) / max(focus + far, 1.0)))
            ffar = max(0.02, min(0.48, (far - focus) / max(focus + far, 1.0)))
            fc = max(0.05, min(0.95, focus / max(near + focus + far, 1.0)))
            # y/H からfocusまでの距離を作り、focus帯の外側だけblur画像をmaskedmergeする。
            sigma = max(1.0, min(18.0, blur * 1.15))
            depth = f"clip((Y/H)*1.0,0,1)"
            mask_expr = (f"255*clip(abs({depth}-{fc:.5f})/{max(min(fnear, ffar),0.02):.5f}-1,0,1)")
            f.append(
                f"split=3[dofsrc][dofblur][dofmask];[dofblur]scale=960:540:flags=bilinear,gblur=sigma={sigma:.2f}:steps=1,scale=1920:1080:flags=bilinear[dofb];"
                f"[dofsrc]format=rgba[dofa];[dofb]format=rgba[dofc];"
                # The depth mask is a smooth image-space gradient. Compute it at
                # 1/4 resolution then upscale; far fewer geq evaluations.
                f"[dofmask]scale=480:270:flags=bilinear,format=gray,geq=lum='clip({mask_expr},0,255)',"
                f"scale=1920:1080:flags=bilinear[dofm];"
                f"[dofc][dofa][dofm]maskedmerge"
            )
    if gpu_blurs and 'dof' not in gpu_blurs and t.dof_enabled and t.dof_blur > .01:
        f.append(gpu_blur_stage.graph)
    if t.bloom > 0 and 'bloom' not in gpu_blurs:
        # Expensive 1080p sigma=22 gblur used to dominate CPU render time.
        # A 540p sigma=11 convolution has approximately the same screen-space
        # radius; composite remains full-resolution and keeps the RGB pipeline.
        f.append(f"split=2[o][g];[g]scale=960:540:flags=bilinear,"
                 f"gblur=sigma=11:steps=1,eq=brightness=-0.05,"
                 f"scale=1920:1080:flags=bilinear[gb];"
                 f"[o][gb]blend=all_mode=screen:all_opacity={min(0.6, 0.45 * t.bloom):.3f}")
    if t.vignette > 0:
        f.append(f"vignette=angle={1.1 - 0.5 * min(1.0, t.vignette):.3f}")
    if t.grain > 0:
        f.append(f"noise=alls={int(18 * t.grain)}:allf=t")
    if t.bpm > 0 and not still:
        f.append(f"eq=brightness='0.10*exp(-9*mod(t,{60.0 / t.bpm:.4f}))':eval=frame")
    if t.bars > 0:
        h = 0.12 * min(1.0, t.bars)
        f.append(f"drawbox=x=0:y=0:w=iw:h=ih*{h:.3f}:color=black:t=fill")
        f.append(f"drawbox=x=0:y=ih-ih*{h:.3f}:w=iw:h=ih*{h:.3f}:color=black:t=fill")
    if t.fog_enabled and t.fog_strength > 0.001:
        r,g,b=FOG_RGB.get(t.fog_preset,FOG_RGB["teal"])
        op=max(0.0,min(0.45,t.fog_strength*0.35))
        color=f"0x{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        f.append(f"drawbox=x=0:y=0:w=iw:h=ih:color={color}@{op:.3f}:t=fill")
    post: list = []
    if not still:
        if t.transition == "flash":
            post += ["fade=t=in:st=0:d=0.18:color=white", f"fade=t=out:st={max(0.1, duration - 0.22):.2f}:d=0.22:color=white"]
        elif t.transition == "fade":
            post += ["fade=t=in:st=0:d=0.3", f"fade=t=out:st={max(0.1, duration - 0.35):.2f}:d=0.35"]
    post.append("format=rgb24" if still else "format=yuv420p")
    pre = (pre_filters + ",") if pre_filters else ""
    head = "[0:v]" + pre + ",".join(f)
    if has_title:
        if still:
            ti = "[1:v]format=rgba[ti]"
        else:
            t_in, t_out = 0.3, max(1.0, duration - 0.6)
            ti = f"[1:v]format=rgba,fade=t=in:st={t_in}:d=0.5:alpha=1,fade=t=out:st={t_out - 0.5:.2f}:d=0.5:alpha=1[ti]"
        return (f"{head}[v0];{ti};"
                f"[v0][ti]overlay=x=(W-w)/2:y=H*0.14:format=auto[v1];"
                f"[v1]{','.join(post)}[vout]")
    return f"{head},{','.join(post)}[vout]"


def audio_graph(t: Template, duration: float, game_idx: Optional[int], bgm_idx: Optional[int],
                trim: float = 0.0) -> Optional[str]:
    """ゲーム音(+BGM)のミックス。BGMはゲーム音が鳴っている間だけ自動で下がる (sidechain ダッキング)。"""
    D = max(0.1, duration)
    fade = f"afade=t=in:d=0.05,afade=t=out:st={max(0.0, D - 0.4):.2f}:d=0.4"
    norm = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    ga = bg = None
    if game_idx is not None:
        ga = (f"[{game_idx}:a]atrim=start={max(0.0, trim):.3f},asetpts=PTS-STARTPTS,{norm},"
              f"volume={t.game_volume:.2f},apad,atrim=duration={D:.3f}")
    if bgm_idx is not None:
        bg = (f"[{bgm_idx}:a]{norm},volume={t.bgm_volume:.2f},apad,atrim=duration={D:.3f},"
              f"afade=t=in:d=0.3,afade=t=out:st={max(0.0, D - 0.5):.2f}:d=0.5")
    if ga and bg:
        return (f"{ga}[ga];{bg}[ba];[ga]asplit=2[ga1][ga2];"
                f"[ba][ga2]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=500[bd];"
                f"[ga1][bd]amix=inputs=2:duration=longest:normalize=0,{fade},alimiter=limit=0.95[aout]")
    if ga:
        return f"{ga},{fade},alimiter=limit=0.95[aout]"
    if bg:
        return f"{bg},alimiter=limit=0.95[aout]"
    return None


def _has_encoder(name: str) -> bool:
    try:
        r = subprocess.run([FFMPEG, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=8)
        return name in r.stdout
    except Exception:
        return False

def gpu_encoder_available() -> bool:
    return _has_encoder("h264_nvenc")

_GPU_DECODE_ARGS = None

def gpu_filter_args() -> list:
    """安定性を優先したGPU対応入力設定。

    CUDA/CUVIDデコードは環境依存で落ちるため強制しない。GPUを使う場所は
    capability check 後の scale_cuda/NVENC などに限定し、失敗時はCPUへ戻せる構成にする。
    """
    return []

_GPU_CAPS = None
def gpu_capabilities() -> dict:
    c = detect_gpu()
    return {
        "nvenc": c.nvenc, "cuda": c.cuda, "scale_cuda": c.scale_cuda,
        "opencl": c.opencl, "gblur_opencl": c.gblur_opencl,
        "unsharp_opencl": c.unsharp_opencl, "opencl_runtime_ok": c.opencl_runtime_ok,
        "program_opencl": c.program_opencl, "rgba_gpu_runtime_ok": c.rgba_gpu_runtime_ok,
        "rgba_probe_reason": c.rgba_probe_reason,
        'full_gpu_runtime_ok': c.full_gpu_runtime_ok,
        'full_probe_reason': c.full_probe_reason,
    }

def gpu_pipeline_status() -> str:
    return gpu_backend_name(detect_gpu())

def encoder_args(fps: int, crf: int = 17, policy: str = 'auto') -> list:
    # NVENC on an FFmpeg encoder list does not prove the actual Windows driver
    # will accept a render. performance_diagnostics retries libx264 on failure.
    if policy != 'cpu' and gpu_encoder_available():
        # CQ 18 is roughly comparable to CRF 17 for typical game footage while being
        # much faster when NVENC is available.
        return ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr",
                "-cq", "18", "-b:v", "0", "-r", str(fps), "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-r", str(fps), "-pix_fmt", "yuv420p"]


def _mux_game_audio(video_path: Path, wav_path: Path, dst: Path, duration: float,
                     trim: float, volume: float = 1.0) -> None:
    """完成済み映像へLoLのWAVを後段muxする。

    映像のfilter_complexとゲーム音声を同じコマンドに詰め込むより、音声だけを後段で
    muxした方が入力indexやfilter graphの影響を受けにくく、NVENC映像を再エンコードせず
    音声だけAAC化できる。これを標準のゲーム音経路にする。
    """
    tmp = dst.with_name(dst.stem + "__audio_mux.mp4")
    af = (f"aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
          f"volume={max(0.0, float(volume)):.3f},apad,atrim=duration={max(0.1, duration):.3f}")
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(video_path),
           "-ss", f"{max(0.0, float(trim)):.3f}", "-i", str(wav_path),
           "-filter_complex", f"[1:a]{af}[aout]",
           "-map", "0:v:0", "-map", "[aout]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-t", f"{max(0.1, duration):.3f}", "-shortest", "-movflags", "+faststart", str(tmp)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size < 1024:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise RuntimeError("LoLゲーム音声のmuxに失敗しました: " + (r.stderr[-1200:] if r.stderr else "unknown"))
    tmp.replace(dst)


def apply_effects(src: Path, dst: Path, t: Template, duration: float, kills: list,
                   size: Optional[tuple] = None, game_wav: Optional[Path] = None,
                   audio_trim: float = 0.0, game_audio: Optional[Path] = None,
                   audio_offset: Optional[float] = None,
                   effect_events: Optional[list] = None) -> None:
    """Keep the original API and release GPU shader files on every exit/retry."""
    caps = detect_gpu()
    stage = None
    resources = []
    from .gpu_full import mode
    if mode() == 'cpu':
        caps = replace(caps, opencl_runtime_ok=False, rgba_gpu_runtime_ok=False,
                       full_gpu_runtime_ok=False, full_probe_reason='explicit_cpu_comparison')
    try:
        stage = GPUBlurStage(t, caps)
    except (OSError, ValueError) as e:
        import logging
        logging.getLogger(__name__).warning('GPU blur setup failed; using CPU: %s', e)
    try:
        _apply_effects(src,dst,t,duration,kills,size,game_wav,audio_trim,game_audio,
                       audio_offset,effect_events,caps,stage,resources)
    finally:
        for cleanup in reversed(resources):
            cleanup()
        if stage is not None:
            stage.close()


def _apply_effects(src, dst, t, duration, kills, size=None, game_wav=None,
                   audio_trim=0.0, game_audio=None, audio_offset=None,
                   effect_events=None, caps=None, gpu_blur_stage=None, resources=None):
    """録画クリップへ映像エフェクトを適用し、必要ならLoL音声を後段muxする。

    GPU優先: 実機OpenCLプローブに成功した効果のみGPUへ回し、それ以外はCPUで処理。
    LoLゲーム音は映像レンダー後に別muxするため、エフェクトfilter graphで音声が消える問題を避ける。
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    if game_wav is None and game_audio is not None:
        game_wav = Path(game_audio)
    if audio_offset is not None:
        audio_trim = max(0.0, float(audio_offset))
    title = t.title_text or (auto_title(kills) if t.title_auto else "")
    png = None
    OUTPUT_W, OUTPUT_H = 1920, 1080
    if title:
        png = make_title_png(title, OUTPUT_W, OUTPUT_H, dst.with_suffix(".title.png"), find_jp_font())
        if resources is not None:
            resources.append(lambda: png.unlink(missing_ok=True))

    # GPU Effects Engine: GPU-native effects run in a dedicated GPU stage.
    # Unsupported effects remain on the CPU. The frame is downloaded at most
    # once before the legacy CPU filter graph, then NVENC encodes the result.
    caps = caps or detect_gpu()
    gpu_prefix_graph, consumed_gpu = gpu_prefix(t.video_effects, caps)
    consumed_gpu = set(consumed_gpu) | (gpu_blur_stage.effects if gpu_blur_stage else set())
    # Select the final video clock BEFORE expensive filters. A 144fps capture
    # exported at 60fps must not run CPU/OpenCL effects on discarded frames.
    frame_rate = f"fps=fps={int(t.fps)}:round=near"
    scale = f"{frame_rate},scale={OUTPUT_W}:{OUTPUT_H}:flags=lanczos"
    pre = ",".join([x for x in (frame_rate, gpu_prefix_graph,
                              f"scale={OUTPUT_W}:{OUTPUT_H}:flags=lanczos") if x])
    events = _effect_events(kills, t, duration) if effect_events is None else list(effect_events)
    # Build a distinct *actual champion* portrait pair for each event. If Riot
    # icons are unavailable, omit the badge rather than showing a fake champion.
    badge_style = kill_style_normalize(getattr(t, "kill_icon_style", "off"))
    import logging
    badge_entries = (make_event_badges(dst, badge_style, kills, events,
                     getattr(t,"kill_icon_players",[]), log=logging.getLogger(__name__).warning,
                     frame_color=t.kill_frame_color, glow_color=t.kill_glow_color,
                     glow_enabled=t.kill_glow_enabled, glow_strength=t.kill_glow_strength,
                     border_width=t.kill_frame_width, mark_style=t.kill_mark_style,
                     sparkle_strength=getattr(t, "kill_sparkle_intensity", 1.0))
                     if badge_style != "off" else [])
    badge_idx = 1 + int(png is not None)
    def add_pair_graph(g):
        if not badge_entries: return g
        return with_badges(g, badge_idx, badge_entries, duration=duration,
                           position=t.kill_icon_position, scale=t.kill_icon_scale,
                           seconds=t.kill_icon_duration, opacity=t.kill_icon_opacity,
                           style=badge_style, stack_gap=getattr(t, "kill_stack_gap", 4))
    def add_pair_inputs(command, loop=True):
        for badge_path, _ in badge_entries:
            if loop:
                command += ["-loop", "1", "-framerate", str(t.fps), "-t", f"{duration:.2f}"]
            command += ["-i", str(badge_path)]
    def clean_pair_files():
        for path, _ in badge_entries:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                pass
    if resources is not None:
        resources.append(clean_pair_files)
    original_effects = t.video_effects
    if consumed_gpu:
        remaining = dict(original_effects)
        for key in consumed_gpu & set(original_effects):
            remaining[key] = 0.0
        t.video_effects = remaining
    try:
        graph = build_graph(t, duration, png is not None, pre_filters=pre, effect_events=events,
                            gpu_blur_stage=gpu_blur_stage)
        graph = add_pair_graph(graph)
    finally:
        t.video_effects = original_effects
    full_stage = None
    full_reason = getattr(caps, 'full_probe_reason', '')
    decode_ok, decode_reason = False, 'not_selected'
    from .gpu_full import GPUFullStage, mode, decode_probe
    if mode() == 'full' and getattr(caps, 'full_gpu_runtime_ok', False):
        try:
            full_stage = GPUFullStage(t,duration,events,ffmpeg=FFMPEG,
                                     title_index=1 if png is not None else None,
                                     badge_index=badge_idx,badges=badge_entries,
                                     lut_index=badge_idx+len(badge_entries))
            if resources is not None: resources.append(full_stage.close)
            graph = full_stage.graph
            consumed_gpu = full_stage.effects
            if caps.cuda:
                decode_ok,decode_reason = decode_probe(FFMPEG,str(src),Path(src).stat().st_mtime_ns)
        except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
            full_reason = str(exc)[-1200:]
            logging.getLogger(__name__).warning('Full GPU setup failed; using legacy path: %s',full_reason)
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error"]
    if consumed_gpu:
        # hwupload without a filter device is not usable on Windows.
        cmd += ["-init_hw_device", OPENCL_DEVICE, "-filter_hw_device", "ocl"]
    if decode_ok:
        cmd += ['-hwaccel','cuda']
    cmd += ["-i", str(src)]
    idx = 1
    if png is not None:
        if full_stage is None:
            cmd += ["-loop", "1", "-framerate", str(t.fps), "-t", f"{duration:.2f}"]
        cmd += ["-i", str(png)]
        idx += 1
    add_pair_inputs(cmd, loop=full_stage is None)
    idx += len(badge_entries)
    if full_stage is not None:
        # A static image is uploaded once. OpenCL framesync repeats that GPU
        # frame at EOF; do not decode/upload a new PNG for every video frame.
        cmd += ['-i',str(full_stage.lut)]
        idx += 1

    # ゲーム音だけの標準経路は後段mux。BGMを使う場合のみ従来の同時ミックスを使う。
    game_idx = bgm_idx = None
    has_wav = bool(game_wav and Path(game_wav).exists() and Path(game_wav).stat().st_size > 100)
    mix_audio_in_graph = bool(t.bgm_path and os.path.exists(t.bgm_path))
    if mix_audio_in_graph and t.game_audio and has_wav:
        cmd += ["-i", str(game_wav)]
        game_idx, idx = idx, idx + 1
    if mix_audio_in_graph:
        cmd += ["-stream_loop", "-1", "-i", t.bgm_path]
        bgm_idx, idx = idx, idx + 1

    ag = audio_graph(t, duration, game_idx, bgm_idx, audio_trim) if mix_audio_in_graph else None
    cmd += ["-filter_complex", graph + (";" + ag if ag else ""), "-map", "[vout]"]
    if ag:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    encoding = encoder_args(t.fps, policy=t.encoder_policy)
    if full_stage is not None and 'h264_nvenc' in encoding:
        encoding[encoding.index('-pix_fmt')+1] = 'rgba'
    cmd += ["-t", f"{duration:.3f}"] + encoding + ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(dst)]
    from .performance_diagnostics import run_render
    pipeline_info = {
        'full_gpu_pipeline': full_stage is not None,
        'full_gpu_unavailable_reason': full_reason if full_stage is None else None,
        'gpu_effects_mode': mode(),
        'video_decoder': 'NVDEC' if decode_ok else 'CPU',
        'gpu_decode_unavailable_reason': None if decode_ok else decode_reason,
        'main_frame_uploads': 1 if full_stage is not None else None,
        'main_frame_downloads': 1 if full_stage is not None else None,
        'pixel_processing': 'OpenCL GPU' if full_stage is not None else 'CPU/OpenCL hybrid',
        'encoder_color_conversion': 'NVENC hardware RGB input' if full_stage is not None and 'rgba' in encoding else 'software YUV420P',
        'cpu_once_per_template': ['color_LUT_calibration','PNG_resources'] if full_stage is not None else [],
        'cpu_control_and_audio': True,
        'cpu_frame_boundary_conversion': 'decoded YUV to upload RGBA',
        'cpu_per_frame_stages': ['YUV_to_RGBA_upload_boundary'] if full_stage is not None else ['legacy_software_filters'],
        "gpu_backend": gpu_backend_name(caps),
        "gpu_effects_unavailable_reason": (
            None if consumed_gpu else
            caps.rgba_probe_reason if t.bloom > 0 or t.dof_enabled else
            "bundled_ffmpeg_missing_avgblur_opencl" if not caps.gblur_opencl else
            "opencl_device_or_filter_probe_failed" if not caps.opencl_runtime_ok else
            "no_supported_gpu_effect_enabled" if not consumed_gpu else None),
        "gpu_capabilities": gpu_capabilities(),
        "ffmpeg_executable": FFMPEG,
        "gpu_opencl_device": OPENCL_DEVICE if consumed_gpu else None,
        "gpu_blur_effects": sorted(gpu_blur_stage.effects) if gpu_blur_stage else [],
        "gpu_effects_selected": sorted(consumed_gpu),
        "cpu_video_effects": sorted(k for k, value in original_effects.items()
                                    if float(value or 0) > 0.001 and k not in consumed_gpu),
        "bloom_cpu_optimized": bool(t.bloom > 0 and 'bloom' not in consumed_gpu),
        "dof_mask_cpu_optimized": bool(t.dof_enabled and t.dof_blur > 0.01 and 'dof' not in consumed_gpu),
        "bloom_level": t.bloom,
        "dof_blur_level": t.dof_blur if t.dof_enabled else 0,
        "dof_shape": getattr(t, "dof_shape", "circle"),
        "dof_center": focus_settings(t)[:2],
        "dof_radius": focus_settings(t)[2],
        "filter_graph": graph,
        "kill_icon_style": badge_style,
        "kill_icon_pairs_resolved": len(badge_entries),
        "kill_icon_position": getattr(t, "kill_icon_position", "right-top"),
        "kill_icon_scale": getattr(t, "kill_icon_scale", 1.0),
        "kill_icon_duration": getattr(t, "kill_icon_duration", 1.55),
        "kill_icon_opacity": getattr(t, "kill_icon_opacity", 1.0),
        "encoder_policy": t.encoder_policy,
        "kill_frame_color": t.kill_frame_color,
        "kill_mark_style": t.kill_mark_style,
        "video_resolution": "1920x1080",
        "output_fps": t.fps,
        "effects_fps": t.fps,
        "frame_rate_selection": "before_effects",
        "duration_s": duration,
    }
    try:
        r = run_render(cmd, output=dst, gpu_effects=consumed_gpu, effect_values=original_effects,
                       pipeline_info=pipeline_info)
    except subprocess.TimeoutExpired as exc:
        if not consumed_gpu: raise
        r = subprocess.CompletedProcess(cmd,1,stderr='GPU render timed out: '+str(exc))
    # GPU effect runtimeが不安定な環境では、同じ設定をCPUエフェクト経路で自動再試行。
    if r.returncode != 0 and consumed_gpu:
        fallback = dict(t.video_effects)
        for key in consumed_gpu & set(original_effects):
            fallback[key] = float(original_effects.get(key, 0.0))
        t.video_effects = fallback
        try:
            graph_cpu = build_graph(t, duration, png is not None, pre_filters=scale, effect_events=events)
            graph_cpu = add_pair_graph(graph_cpu)
            cpu_cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
            idx2 = 1
            if png is not None:
                cpu_cmd += ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(png)]
                idx2 += 1
            add_pair_inputs(cpu_cmd)
            idx2 += len(badge_entries)
            if mix_audio_in_graph:
                if t.game_audio and has_wav:
                    cpu_cmd += ["-i", str(game_wav)]
                    gi2, idx2 = idx2, idx2 + 1
                else:
                    gi2 = None
                cpu_cmd += ["-stream_loop", "-1", "-i", t.bgm_path]
                bi2, idx2 = idx2, idx2 + 1
                ag2 = audio_graph(t, duration, gi2, bi2, audio_trim)
            else:
                ag2 = None
            cpu_cmd += ["-filter_complex", graph_cpu + (";" + ag2 if ag2 else ""), "-map", "[vout]"]
            if ag2:
                cpu_cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
            cpu_cmd += ["-t", f"{duration:.3f}"] + encoder_args(t.fps, policy=t.encoder_policy) + ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(dst)]
            r = run_render(cpu_cmd, output=dst, gpu_effects=[], effect_values=original_effects, fallback_reason="GPU render failed",
                           pipeline_info={**pipeline_info, "gpu_effects_selected": [],
                                          'full_gpu_pipeline':False,'pixel_processing':'CPU',
                                          'video_decoder':'CPU','main_frame_uploads':0,'main_frame_downloads':0,
                                          'encoder_color_conversion':'software YUV420P',
                                          "gpu_backend": "CPU Effects fallback",
                                          "gpu_effects_unavailable_reason": "gpu_render_failed",
                                          "gpu_opencl_device": None,
                                          "gpu_blur_effects": [],
                                          "bloom_cpu_optimized": bool(t.bloom > 0),
                                          "dof_mask_cpu_optimized": bool(t.dof_enabled and t.dof_blur > .01),
                                          "cpu_video_effects": sorted(k for k,v in original_effects.items() if float(v or 0)>0.001),
                                          "filter_graph": graph_cpu})
        finally:
            t.video_effects = original_effects
    if r.returncode != 0:
        raise RuntimeError("ffmpeg エフェクト適用に失敗: " + r.stderr[-1200:])
    if not dst.exists() or dst.stat().st_size < 1024:
        raise RuntimeError("出力MP4が正常に生成されませんでした")

    # GPU/OpenCL経路やNVENCドライバの色変換相性で彩度が消えた場合に備え、
    # 元映像がカラーなのに出力だけほぼモノクロならCPUフィルター経路で再描画する。
    # ノワール/意図的な低彩度テンプレートではこの検査を行わない。
    intentional_mono = (str(getattr(t, "grade", "")) == "noir" or
                        float(getattr(t, "vibrance", 0.0)) < -0.75)
    if not intentional_mono and r.returncode == 0:
        src_color = _colorfulness(Path(src))
        dst_color = _colorfulness(dst)
        if src_color > 10.0 and 0.0 <= dst_color < max(3.0, src_color * 0.12):
            if consumed_gpu:
                remaining = dict(original_effects)
                t.video_effects = remaining
                try:
                    graph_cpu = build_graph(t, duration, png is not None, pre_filters=scale, effect_events=events)
                    graph_cpu = add_pair_graph(graph_cpu)
                    cpu_cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
                    idxc = 1
                    if png is not None:
                        cpu_cmd += ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(png)]
                        idxc += 1
                    add_pair_inputs(cpu_cmd)
                    idxc += len(badge_entries)
                    if mix_audio_in_graph:
                        gi = None
                        if t.game_audio and has_wav:
                            cpu_cmd += ["-i", str(game_wav)]
                            gi, idxc = idxc, idxc + 1
                        cpu_cmd += ["-stream_loop", "-1", "-i", t.bgm_path]
                        bi, idxc = idxc, idxc + 1
                        agc = audio_graph(t, duration, gi, bi, audio_trim)
                    else:
                        agc = None
                    cpu_cmd += ["-filter_complex", graph_cpu + (";" + agc if agc else ""), "-map", "[vout]"]
                    if agc:
                        cpu_cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
                    cpu_cmd += ["-t", f"{duration:.3f}"] + encoder_args(t.fps, policy=t.encoder_policy) + ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(dst)]
                    rr = run_render(cpu_cmd, output=dst, gpu_effects=[], effect_values=original_effects, fallback_reason="color preservation retry",
                                    pipeline_info={**pipeline_info, "gpu_effects_selected": [],
                                                   'full_gpu_pipeline':False,'pixel_processing':'CPU',
                                                   'video_decoder':'CPU','main_frame_uploads':0,'main_frame_downloads':0,
                                                   'encoder_color_conversion':'software YUV420P',
                                                   "gpu_backend": "CPU Effects fallback",
                                                   "gpu_effects_unavailable_reason": "color_preservation_retry",
                                                   "gpu_opencl_device": None,
                                                   "gpu_blur_effects": [],
                                                   "bloom_cpu_optimized": bool(t.bloom > 0),
                                                   "dof_mask_cpu_optimized": bool(t.dof_enabled and t.dof_blur > .01),
                                                   "cpu_video_effects": sorted(k for k,v in original_effects.items() if float(v or 0)>0.001),
                                                   "filter_graph": graph_cpu})
                    if rr.returncode != 0:
                        raise RuntimeError("色保持用CPU再描画に失敗: " + rr.stderr[-1000:])
                finally:
                    t.video_effects = original_effects

    clean_pair_files()
    for temporary in (png,):
        if temporary is not None:
            try:
                Path(temporary).unlink(missing_ok=True)
            except OSError:
                pass

    if t.game_audio and not mix_audio_in_graph:
        if not has_wav:
            raise RuntimeError("LoLゲーム音WAVが見つからないため、音声付きMP4を作成できません")
        _mux_game_audio(dst, Path(game_wav), dst, duration, audio_trim, t.game_volume)

    # 最終MP4に音声ストリームがあることを確認。
    if t.game_audio:
        try:
            probe = subprocess.run([FFMPEG, "-hide_banner", "-i", str(dst)], capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=10)
            if "Audio:" not in probe.stderr:
                raise RuntimeError("ゲーム音声ストリームがMP4に入りませんでした")
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("完成MP4の音声ストリーム検証がタイムアウトしました") from e


def _colorfulness(path: Path) -> float:
    """中央フレームのRGBチャンネル差を軽量に測る。0に近いほどモノクロ。"""
    try:
        import numpy as np
        r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", "0.5",
                            "-i", str(path), "-frames:v", "1", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=12)
        if r.returncode != 0 or len(r.stdout) < 3:
            return -1.0
        a = np.frombuffer(r.stdout, dtype=np.uint8)
        if a.size < 3:
            return -1.0
        a = a[:(a.size // 3) * 3].reshape(-1, 3).astype(np.float32)
        return float(np.mean(np.max(a, axis=1) - np.min(a, axis=1)))
    except Exception:
        return -1.0


def _probe_size(path: Path) -> tuple:
    import re
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    m = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", r.stderr)
    return (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)


def concat_clips(clips: list, dst: Path) -> None:
    """同一エンコードのMP4を無劣化連結 (モンタージュ)。"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    lst = dst.with_suffix(".concat.txt")
    lst.write_text("".join(f"file '{Path(c).as_posix()}'\n" for c in clips), encoding="utf-8")
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
           "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        os.remove(lst)
    except OSError:
        pass
    if r.returncode != 0:
        raise RuntimeError("ffmpeg 連結に失敗: " + r.stderr[-600:])
