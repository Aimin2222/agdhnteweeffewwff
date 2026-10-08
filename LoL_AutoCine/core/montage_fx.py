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

MONTAGE_FX = {"cut", "flash", "dark"}


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
    if style == "flash":
        # 2 frame wide flicker at 60fps; avoid full-white screen or seizure-like strobing
        terms = [f"0.22*max(0,1-abs(t-{x:.4f})/0.09)" for x in cuts]
    else:
        terms = [f"-0.24*max(0,1-abs(t-{x:.4f})/0.18)" for x in cuts]
    # Note: FFmpeg filter argument escaping is handled by passing the entire
    # filter as one subprocess argument (not through a shell).
    return "eq=brightness='" + "+".join(terms) + "':eval=frame"


def render_montage(clips, dst, style="cut", *, concat=None, ffmpeg=None,
                   ffprobe="ffprobe", encoder=None, logger=None) -> str:
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
                args = encoder_args(60)
                # The original clip FPS must be preserved: remove any forced -r.
                if "-r" in args:
                    n = args.index("-r")
                    del args[n:n+2]
            cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                   "-vf", filt, "-map", "0:v:0", "-map", "0:a?", *args,
                   "-c:a", "copy", "-movflags", "+faststart", str(dst)]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
            used_encoder = args[args.index("-c:v") + 1] if "-c:v" in args else "custom"
            if result.returncode and encoder is None and used_encoder == "h264_nvenc":
                if logger:
                    logger("モンタージュGPUエンコード失敗 → CPUで再試行: " + result.stderr[-250:])
                alt = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p"]
                cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
                       "-vf", filt, "-map", "0:v:0", "-map", "0:a?", *alt,
                       "-c:a", "copy", "-movflags", "+faststart", str(dst)]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
                used_encoder = "libx264"
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
