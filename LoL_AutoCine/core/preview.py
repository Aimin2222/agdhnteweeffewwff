# -*- coding: utf-8 -*-
"""テンプレート反映プレビュー。ミラー映像(またはサンプル画像)に色/エフェクト/タイトルをリアルタイムで適用する。

lolnam の「調整をその場で比較 (Before/After 分割)」を参考にした。
プレビューは numpy による近似 (軽量)。ffmpeg の最終出力とほぼ同じ傾向だが完全一致ではない。
厳密な見た目は render_exact_still() (ffmpeg と同じフィルタで1枚だけ描画) で確認できる。
"""
from __future__ import annotations
import subprocess
import math
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageFilter

from .effects import (FFMPEG, Template, auto_title, build_graph, find_jp_font, grade_values, make_title_png,
                      vignette_angle, FOG_RGB)


def sample_scene(w: int = 960, h: int = 540) -> np.ndarray:
    """LoLが映っていなくても色味を確認できる、ファンタジー風のサンプル画像 (RGB uint8)。"""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    sky = np.stack([90 + 60 * (1 - y / h), 130 + 50 * (1 - y / h), 200 + 40 * (1 - y / h)], -1)
    ground_mask = (y > h * 0.55)[..., None]
    grass = np.stack([60 + 30 * np.sin(x / 40), 130 + 40 * np.sin(y / 25), 55 + 20 * np.sin(x / 55)], -1)
    img = np.where(ground_mask, grass, sky)
    for cx, cy, r, col in ((w * .3, h * .62, 38, (230, 200, 90)), (w * .62, h * .7, 46, (220, 70, 70)),
                           (w * .8, h * .3, 60, (255, 240, 200))):
        m = ((x - cx) ** 2 + (y - cy) ** 2) < r * r
        img[m] = col
    return np.clip(img, 0, 255).astype(np.uint8)


_CACHE: dict = {}


def _vignette_r(w: int, h: int) -> np.ndarray:
    """中心からの距離 (角=1)。ffmpeg vignette は cos(angle * r)^4 で暗くする。"""
    k = ("v", w, h)
    if k not in _CACHE:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.hypot(xx - w / 2, yy - h / 2) / np.hypot(w / 2, h / 2)
        _CACHE[k] = r[..., None]
    return _CACHE[k]


def _title_overlay(title: str, w: int, h: int) -> Image.Image:
    k = ("t", title, w, h)
    if k not in _CACHE:
        with tempfile.TemporaryDirectory() as d:
            png = make_title_png(title, w, h, Path(d) / "t.png", find_jp_font())
            _CACHE[k] = Image.open(png).convert("RGBA").copy()
    return _CACHE[k]


def _luma(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def grade_rgb(frame_rgb: np.ndarray, t: Template, title: str = "") -> np.ndarray:
    """RGB uint8 -> 色/エフェクト適用後の RGB uint8 (近似)。"""
    a = frame_rgb.astype(np.float32) / 255.0
    h, w = a.shape[:2]
    g = grade_values(t.grade, t.grade_strength, t.contrast)
    # eq
    a = (a - 0.5) * g["contrast"] + 0.5 + g["brightness"]
    lum = _luma(a)[..., None]
    a = lum + (a - lum) * g["saturation"]
    a = np.clip(a, 0, 1) ** (1.0 / max(0.1, g["gamma"]))
    # colorbalance (影/中間/ハイライト) + 色温度
    tmp = max(-1.0, min(1.0, t.temperature))
    L = np.clip(_luma(a), 0, 1)
    ws, wm, wh = ((1 - L) ** 2)[..., None], (4 * L * (1 - L))[..., None], (L ** 2)[..., None]
    shift = np.zeros_like(a)
    for ch, (s_, m_, h_) in enumerate((
            (g["rs"], g["rm"] + 0.10 * tmp, g["rh"] + 0.06 * tmp),
            (g["gs"], g["gm"], g["gh"]),
            (g["bs"], g["bm"] - 0.10 * tmp, g["bh"] - 0.06 * tmp))):
        shift[..., ch] = (s_ * ws + m_ * wm + h_ * wh)[..., 0]
    a = np.clip(a + shift * 0.5, 0, 1)
    # bloom
    if t.bloom > 0:
        im = Image.fromarray((a * 255).astype(np.uint8))
        blur = np.asarray(im.filter(ImageFilter.GaussianBlur(max(2, w // 60)))).astype(np.float32) / 255.0 - 0.05
        op = min(0.6, 0.45 * t.bloom)
        a = np.clip(1 - (1 - a) * (1 - np.clip(blur, 0, 1) * op), 0, 1)
    # vignette
    if t.vignette > 0:
        a = a * np.cos(vignette_angle(t.vignette) * _vignette_r(w, h)) ** 4
    # grain
    if t.grain > 0:
        a = np.clip(a + np.random.normal(0, 0.012 + 0.05 * t.grain, a.shape[:2])[..., None], 0, 1)
    # カーブ補正 (UIのポイントを線形補間。最終出力のFFmpeg curvesと同じ方向)
    if getattr(t, "curve_enabled", False) and getattr(t, "curve_points", "").strip():
        try:
            pts = []
            for token in t.curve_points.replace(";", " ").split():
                x, y = token.split("/", 1)
                pts.append((float(x), float(y)))
            pts = sorted((max(0.0, min(1.0, x)), max(0.0, min(1.0, y))) for x, y in pts)
            if len(pts) >= 2:
                xs = np.array([p[0] for p in pts], dtype=np.float32)
                ys = np.array([p[1] for p in pts], dtype=np.float32)
                lut = np.interp(np.linspace(0.0, 1.0, 256), xs, ys).astype(np.float32)
                idx = np.clip((a * 255.0).astype(np.int16), 0, 255)
                a = lut[idx]
        except Exception:
            pass
    # Fog Preset: 最終出力と同じ方向の色霧をプレビューにも反映。
    if getattr(t, "fog_enabled", False) and getattr(t, "fog_strength", 0.0) > 0.001:
        fr, fg, fb = FOG_RGB.get(getattr(t, "fog_preset", "teal"), FOG_RGB["teal"])
        fog = np.array([fr, fg, fb], dtype=np.float32)[None, None, :]
        op = max(0.0, min(0.45, float(t.fog_strength) * 0.35))
        a = np.clip(a * (1.0 - op) + fog * op, 0, 1)
    # v5.10.3: match FFmpeg circular DOF in the lightweight preview.
    # This is screen-space centering around TargetLock's usual on-screen target.
    # Do not claim per-frame champion pixel tracking or actual 3D depth.
    from .focus_fx import focus_settings
    cx, cy, radius, feather = focus_settings(t)
    mask_circle = None
    def circle_distance():
        nonlocal mask_circle
        if mask_circle is None:
            yy, xx = np.ogrid[:h, :w]
            mask_circle = np.hypot((xx / w - cx) * w / h, (yy / h - cy)).astype(np.float32)
        return mask_circle
    if getattr(t, "dof_enabled", False) and getattr(t, "dof_blur", 0.0) > 0.01:
        base = a.copy()
        im = Image.fromarray((a * 255).astype(np.uint8))
        blurred = np.asarray(im.filter(ImageFilter.GaussianBlur(float(t.dof_blur) * .75))).astype(np.float32) / 255.0
        if getattr(t, "dof_shape", "circle") == "band":
            near=max(1.0, float(getattr(t, "dof_near_distance", 10000.0)))
            focus=max(near, float(getattr(t, "dof_focus_distance", 5510.0)))
            far=max(focus+1.0, float(getattr(t, "dof_far_distance", 10000.0)))
            fc=np.clip(focus/max(near+focus+far,1.0), .05,.95)
            span=max(.025,min((focus-near)/max(focus+far,1.0), (far-focus)/max(focus+far,1.0)))
            yy=np.linspace(0.,1.,h,dtype=np.float32)[:,None]
            weight=np.clip((np.abs(yy-fc)-span)/max(span,.02),0,1)
        else:
            weight=np.clip((circle_distance()-radius)/feather,0,1)
        a=base*(1.-weight[...,None])+blurred*weight[...,None]
    # cinema bars
    if t.bars > 0:
        bh = int(h * 0.12 * min(1.0, t.bars))
        if bh > 0:
            a[:bh] = 0
            a[h - bh:] = 0
    out = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    if title:
        base = Image.fromarray(out).convert("RGBA")
        base.alpha_composite(_title_overlay(title, w, h), (0, int(h * 0.14)))
        out = np.asarray(base.convert("RGB"))
    return out



def apply_video_effect_preview(frame_rgb: np.ndarray, t: Template, phase: float = 0.5) -> np.ndarray:
    """ミラー上で確認できる軽量プレビュー。最終FFmpegと完全一致ではないが、
    チェックした演出がONになっていることを直感的に確認できるようにする。"""
    a = np.asarray(frame_rgb).copy()
    fx = getattr(t, "video_effects", {}) or {}
    h, w = a.shape[:2]
    def strength(k):
        try: return max(0.0, min(1.0, float(fx.get(k, 0.0))))
        except Exception: return 0.0
    # Transformers
    if strength("mirror") > 0.001:
        a = a[:, ::-1].copy()
    # Motion camera / shake / wiggle: crop + resize with numpy
    motion = strength("motion_camera")
    shake = strength("camera_shake")
    wig = strength("wiggle")
    amp = 0.0
    freq = 1.0
    if motion: amp += 0.01 + 0.025*motion; freq=1.0
    if shake: amp += 0.008 + 0.025*shake; freq=7.0
    if wig: amp += 0.004 + 0.015*wig; freq=2.0
    if amp > 0:
        import math
        zx = int(w*amp); zy=int(h*amp)
        dx=int(math.sin(phase*2*math.pi*freq)*zx); dy=int(math.cos(phase*2*math.pi*freq*1.17)*zy)
        x0=max(0,min(w-2,(w-int(w*(1-2*amp)))//2+dx)); y0=max(0,min(h-2,(h-int(h*(1-2*amp)))//2+dy))
        cw=max(2,int(w*(1-2*amp))); ch=max(2,int(h*(1-2*amp)))
        crop=a[y0:y0+ch,x0:x0+cw]
        a=np.asarray(Image.fromarray(crop).resize((w,h),Image.Resampling.BILINEAR))
    # Spin motion
    spin=strength("spin_motion")
    if spin:
        deg=math.sin(phase*2*math.pi)*1.5*spin if 'math' in globals() else 0
        # Pillow rotateは軽量で、出力サイズを維持する。
        a=np.asarray(Image.fromarray(a).rotate(deg,resample=Image.Resampling.BILINEAR,expand=False,fillcolor=(0,0,0)))
    # Zoom/radial blur are approximated with a center crop + temporal-looking blend.
    zoom=strength("zoom_blur")
    if zoom:
        z=1.0+0.025*zoom
        cw,ch=int(w/z),int(h/z); x0=(w-cw)//2; y0=(h-ch)//2
        zf=np.asarray(Image.fromarray(a[y0:y0+ch,x0:x0+cw]).resize((w,h),Image.Resampling.BILINEAR)).astype(np.float32)
        a=np.clip(a.astype(np.float32)*0.65+zf*0.35,0,255).astype(np.uint8)
    # Glitch / VHS / chroma leak
    glitch=max(strength("glitch"),strength("vhs_damage"),strength("chroma_leak"))
    if glitch:
        px=max(1,int(2+12*glitch)); out=a.copy()
        out[:,:,0]=np.roll(a[:,:,0],px,axis=1)
        out[:,:,2]=np.roll(a[:,:,2],-px,axis=1)
        a=out
    if strength("vhs_damage"):
        noise=np.random.normal(0,5+16*strength("vhs_damage"),a.shape[:2])[:,:,None]
        a=np.clip(a.astype(np.float32)+noise,0,255).astype(np.uint8)
    # Block motion
    bm=strength("block_motion")
    if bm:
        bs=max(4,int(8+24*bm)); small=Image.fromarray(a).resize((max(1,w//bs),max(1,h//bs)),Image.Resampling.BOX)
        a=np.asarray(small.resize((w,h),Image.Resampling.NEAREST))
    # Kaleidoscope-like mirror blend
    kal=strength("kaleidoscope")
    if kal:
        m=a[:,::-1]
        a=np.clip(a.astype(np.float32)*(1-0.22*kal)+m.astype(np.float32)*(0.22*kal),0,255).astype(np.uint8)
    # Global blur / glint / sphere blur
    blur=max(strength("focus_blur"),strength("vr_blur"),strength("sphere_blur"))
    if blur:
        a=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.0+3.0*blur)))
    if strength("glint"):
        b=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(4)))
        a=np.clip(a.astype(np.float32)*0.78+b.astype(np.float32)*0.22*(0.5+strength("glint")),0,255).astype(np.uint8)
    # Flash / light leak preview: the playhead phase is used as a simple preview cue.
    flash=max(strength("flash"),strength("vr_light_leak"))
    if flash and phase > 0.72:
        a=np.clip(a.astype(np.float32)*(1.0+0.45*flash),0,255).astype(np.uint8)
    return a


def apply_camera_preview(frame_rgb: np.ndarray, t: Template, phase: float = 0.5) -> np.ndarray:
    """ミラー表示用の仮想カメラ。Replay APIは一切触らず、カメラ演出の見た目だけ近似する。

    実際の対象プレイヤー追従は録画時のReplay CameraDirectorが担当する。
    ミラーでは中心を仮想ターゲットとして、テンプレートのstyle/intensity/dist_scaleから
    ドリーイン/FOV変化を画面上で確認できるようにする。
    """
    a = np.asarray(frame_rgb)
    if a.ndim != 3 or a.shape[2] != 3:
        return frame_rgb
    style = getattr(t, "style", "cinema")
    if style not in ("cinema", "follow", "cinema_top", "top", "fps", "orbit"):
        return frame_rgb
    intensity = {"natural": 0.6, "standard": 1.0, "strong": 1.4}.get(getattr(t, "intensity", "standard"), 1.0)
    base = max(0.3, min(1.0, float(getattr(t, "dist_scale", 0.8))))
    if style in ("cinema", "cinema_top"):
        # キル付近の寄りを想定した静止プレビュー。中央をターゲットとして扱う。
        zoom = 1.0 + (1.0 - base) * 0.55 * intensity
    else:
        zoom = 1.0 + (1.0 - base) * 0.18
    if style in ("cinema_top", "top"):
        zoom *= 0.92  # 俯瞰は寄りすぎない
    zoom = max(1.0, min(1.55, zoom))
    h, w = a.shape[:2]
    if zoom <= 1.001:
        out = a.copy()
    else:
        cw, ch = max(2, int(w / zoom)), max(2, int(h / zoom))
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        crop = a[y0:y0 + ch, x0:x0 + cw]
        out = np.asarray(Image.fromarray(crop).resize((w, h), Image.Resampling.LANCZOS))
    if style == "orbit":
        # ミラーではターゲットを中央と仮定し、オービット感を左右シフトで近似。
        off=int(w*0.05*intensity*float(np.sin(phase*2*np.pi)))
        shifted=np.empty_like(out); shifted[:] = out[:, -1:]
        if off >= 0:
            shifted[:, off:] = out[:, :w-off]
            shifted[:, :off] = out[:, :1]
        else:
            q=-off; shifted[:, :w-q] = out[:, q:]; shifted[:, w-q:] = out[:, -1:]
        out=shifted
    # カメラ高さもミラーで確認できるよう、画角の上下位置を軽く近似する。
    # 実際のReplay座標は録画時にCameraDirectorが適用する。
    cam_h = float(getattr(t, "cam_height", 170.0))
    shift = int(max(-0.12, min(0.12, (cam_h - 170.0) / 900.0)) * h)
    if shift:
        shifted = np.empty_like(out)
        shifted[:] = out[-1] if shift > 0 else out[0]
        if shift > 0:
            shifted[shift:] = out[:-shift]
        else:
            shifted[:shift] = out[-shift:]
        out = shifted
    return out

def compose_compare(original_rgb: np.ndarray, t: Template, title: str = "", split: float = 0.0) -> np.ndarray:
    """split=0: 全面が適用後。0<split<=1: 左 split 割合が適用前 / 右が適用後 (境界線つき)。"""
    graded = grade_rgb(original_rgb, t, title)
    if split <= 0.0:
        return graded
    h, w = graded.shape[:2]
    x = int(w * min(1.0, split))
    out = graded.copy()
    out[:, :x] = original_rgb[:, :x]
    if 0 < x < w:
        out[:, max(0, x - 1):x + 1] = 255
    return out


def preview_title(t: Template, n_kills: int = 1) -> str:
    return t.title_text or (auto_title([None] * n_kills) if t.title_auto else "")


def render_exact_still(frame_rgb: np.ndarray, t: Template, dst: Path) -> Path:
    """ffmpeg の最終出力と同じフィルタ(タイトル/切替演出を除く)で1枚だけ描画する。"""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    h, w = frame_rgb.shape[:2]
    t2 = Template(**{**t.to_dict(), "transition": "cut", "bpm": 0.0})
    graph = build_graph(t2, 1.0, False)
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "in.png"
        Image.fromarray(frame_rgb).save(src)
        cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-filter_complex", graph,
               "-map", "[vout]", "-frames:v", "1", str(dst)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("正確プレビューに失敗: " + r.stderr[-400:])
    return dst
