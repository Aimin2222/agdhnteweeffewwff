# -*- coding: utf-8 -*-
"""True two-source spatial transition comparisons (development QA only).

Do not change production concat/NVENC/audio routing based on these previews.
A tester approves an effect before it enters normal rendering.
"""
from pathlib import Path
import subprocess

from .gpu_binary import ffmpeg_exe
from .montage_fx import get_duration

TRANSITION_PREVIEWS = {
    "fade": "実際のクロスフェード",
    "wipeleft": "左へワイプ",
    "slideright": "右からスライド",
    "circleopen": "中心から円形展開",
    "pixelize": "ピクセルで切替",
    "smoothup": "上へなめらか切替",
}


def build_xfade_filter(style, *, length, duration, width=1920, height=1080, fps=60):
    """Shared dimensions/timebase so native FFmpeg xfade never drifts frames."""
    if style not in TRANSITION_PREVIEWS:
        raise ValueError("Unknown QA transition")
    length = float(length)
    duration = float(duration)
    if not (0.18 <= duration < length):
        raise ValueError("Transition exceeds a clip")
    if width <= 0 or height <= 0 or fps <= 0:
        raise ValueError("Invalid output geometry")
    source = (f"trim=duration={length:.3f},setpts=PTS-STARTPTS,"
              f"fps={fps},scale={width}:{height}:flags=bicubic,"
              "setsar=1,format=yuv420p,settb=AVTB")
    return (f"[0:v]{source}[a];[1:v]{source}[b];"
            f"[a][b]xfade=transition={style}:duration={duration:.3f}:"
            f"offset={length-duration:.3f},format=yuv420p[v]")


def render_true_transition(first, second, dest, style, *,
                           log=lambda _m:None, subprocess_run=None, width=1920, height=1080, fps=60):
    """Produce one visually distinct, muted comparison using *existing* MP4s.

    No Replay API re-record, no change to game-audio output in production.
    """
    first, second, dest = Path(first), Path(second), Path(dest)
    if not first.exists() or not second.exists():
        raise FileNotFoundError("QA reference clips are missing")
    dest.parent.mkdir(parents=True,exist_ok=True)
    src_seconds = min(get_duration(first,ffmpeg=str(ffmpeg_exe())),
                      get_duration(second,ffmpeg=str(ffmpeg_exe())))
    length = max(0.6,min(2.6,src_seconds-.08))
    transition_seconds = min(0.45, length*.28)
    graph = build_xfade_filter(style,length=length,duration=transition_seconds,
                               width=width,height=height,fps=fps)
    cmd = [str(ffmpeg_exe()),"-nostdin","-hide_banner","-loglevel","error","-y",
           "-i",str(first),"-i",str(second),"-filter_complex",graph,
           "-map","[v]","-an","-c:v","libx264","-preset","ultrafast",
           "-crf","25","-pix_fmt","yuv420p","-r",str(fps),
           "-t",f"{2*length-transition_seconds:.3f}",str(dest)]
    result=(subprocess_run or subprocess.run)(cmd,capture_output=True,timeout=300)
    if result.returncode!=0:
        raise RuntimeError("FFmpeg xfade error: "+str(result.stderr)[-700:])
    if not dest.exists() or dest.stat().st_size<=1024:
        raise RuntimeError("No preview MP4 written")
    log(f"空間切替の試作品: {style} → {dest.name}")
    return dest
