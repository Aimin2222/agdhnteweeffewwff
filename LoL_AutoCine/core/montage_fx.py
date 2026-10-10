# -*- coding: utf-8 -*-
"""Optional post-concat montage transitions. Existing cut mode is bit-exact copy.

Deliberately independent of replay, camera, game-audio capture and GPU filters.
The postprocessing only touches video; original LoL audio is stream-copied.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import re
import subprocess

MONTAGE_LABELS = {
    "cut": "なし（高速連結）",
    "flash": "白いフラッシュ",
    "dark": "シネマ暗転",
    "white": "ホワイトアウト",
    "soft": "ソフトディゾルブ風",
    "gold": "ゴールドライト",
    "cool": "クールブルー",
    "pulse": "インパクトパルス",
    "cinema": "フィルムフラッシュ",
    "shadow": "ディープシャドウ",
}
MONTAGE_REVERSE = {label: key for key,label in MONTAGE_LABELS.items()}
MONTAGE_FX = set(MONTAGE_LABELS)


def get_duration(path: Path, *, ffprobe: str = "ffprobe", ffmpeg: str = "ffmpeg") -> float:
    """Use stream duration; don't guess transition times from nominal clip duration."""
    args = [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)]
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
        if p.returncode:
            raise RuntimeError(p.stderr[-240:])
        result = float(json.loads(p.stdout)["format"]["duration"])
    except (FileNotFoundError, RuntimeError, ValueError, KeyError, json.JSONDecodeError):
        # Windows distributions that bundle only imageio's ffmpeg (no ffprobe)
        # still can read the container's exact Duration header.
        p = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=20)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", p.stderr)
        if m is None:
            raise RuntimeError(f"再生時間が取得できません: {path.name}: {p.stderr[-240:]}")
        result = float(m[1])*3600+float(m[2])*60+float(m[3])
    if not math.isfinite(result) or result <= 0:
        raise ValueError("クリップ時間が不正です")
    return result


def cut_points(clips, *, probe=get_duration):
    if len(clips) < 2:
        return []
    durations = [probe(Path(p)) for p in clips]
    elapsed = 0.0
    points = []
    for d in durations[:-1]:
        elapsed += d
        points.append(round(elapsed, 4))
    return points


def montage_filter(style: str, cuts: list[float]) -> str:
    """FFmpeg eq expression using wall-clock t (seconds), not frame count.

    Light flashes and black dips are brief and only near the join. No frames
    are added or removed; this keeps original gameplay audio in sync.
    """
    if style not in MONTAGE_FX:
        raise ValueError("未知のモンタージュ演出: " + style)
    if style == "cut" or not cuts:
        return "null"
    profiles = {
        "flash": (.22, .09), "dark": (-.24, .18),
        "white": (.34, .24), "soft": (.11, .30),
        "gold": (.19, .22), "cool": (.10, .20),
        "pulse": (.28, .11), "cinema": (.16, .16),
        "shadow": (-.34, .23),
    }
    amount, width = profiles[style]
    terms=[f"{amount:.3f}*max(0,1-abs(t-{x:.4f})/{width:.3f})" for x in cuts]
    # Safe continuous pulses preserve 1080p/60fps and original game audio.
    graph="eq=brightness='"+"+".join(terms)+"':eval=frame"
    if style in ("gold","cinema"):
        graph+=",colorbalance=rs=0.02:gs=0.008:bs=-0.018"
    elif style=="cool":
        graph+=",colorbalance=rs=-0.022:bs=0.035"
    elif style=="pulse":
        graph+=",eq=saturation=1.11"
    return graph

def render_montage(clips, dst, style="cut", *, concat=None, ffmpeg=None,
                   ffprobe="ffprobe", encoder=None, logger=None, encoder_policy='auto') -> str:
    """Create montage and report which path was *actually* applied.

    Fail-safe: if optional transition rendering fails, preserve previously
    concatenated, audio-bearing video as normal cut-mode output and log why.
    """
    if not clips:
        raise ValueError("モンタージュ対象がありません")
    if style not in MONTAGE_FX:
        raise ValueError("未知のモンタージュ演出")
    dst = Path(dst)
    from .effects import concat_clips, encoder_args, FFMPEG
    concatenate = concat or concat_clips
    ffmpeg = ffmpeg or FFMPEG
    if style == "cut" or len(clips) < 2:
        concatenate(list(clips), dst)
        return "cut"
    raw = dst.with_name(dst.stem + "__joined_raw.mp4")
    try:
        concatenate(list(clips), raw)
        try:
            boundaries = cut_points(clips, probe=lambda p: get_duration(p, ffprobe=ffprobe, ffmpeg=ffmpeg))
            filt = montage_filter(style, boundaries)
            args = list(encoder or ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p"])
            # Default app path prioritizes NVENC when installed; if it fails,
            # automatically retry software encoder without changing audio.
            if encoder is None:
                args = encoder_args(60) if encoder_policy == 'auto' else encoder_args(60, policy=encoder_policy)
                # The original clip FPS must be preserved: remove any forced -r.
                if "-r" in args:
                    n = args.index("-r")
                    del args[n:n+2]
                from .gpu_full import render_gpu_montage
                if style in ("flash", "dark") and render_gpu_montage(ffmpeg,raw,dst,style,boundaries,args,logger):
                    return style
            cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                   "-vf", filt, "-map", "0:v:0", "-map", "0:a?", *args,
                   "-c:a", "copy", "-movflags", "+faststart", str(dst)]
            from .performance_diagnostics import run_render, _encoder_name
            result = run_render(cmd, output=dst, gpu_effects=[], effect_values={}, timeout=900,
                                allow_encoder_retry=encoder is None,
                                pipeline_info={'stage':'montage','encoder_policy':encoder_policy,
                                               'cpu_video_effects':['eq'],'montage_style':style})
            used_encoder = _encoder_name(result.args)
            if result.encoder_retry_reason:
                if logger:
                    logger("モンタージュ: " + result.encoder_retry_reason)
            if result.returncode or not dst.is_file() or dst.stat().st_size < 1024:
                raise RuntimeError(result.stderr[-800:] or "モンタージュ演出の生成に失敗")
            if logger:
                logger("モンタージュ演出を適用: " + style + f" / 切り替え {len(boundaries)}回"
                       + f" / 映像フィルター=CPU eq / エンコーダー={used_encoder} / 音声=copy")
            return style
        except Exception as ex:
            if logger:
                logger("モンタージュ演出は適用できなかったため通常連結で保存: " + str(ex)[-400:])
            dst.unlink(missing_ok=True)
            raw.replace(dst)
            return "cut (fallback)"
    finally:
        raw.unlink(missing_ok=True)
