# -*- coding: utf-8 -*-
"""True two-source spatial transition comparisons (development QA only).

Do not change production concat/NVENC/audio routing based on these previews.
A tester approves an effect before it enters normal rendering.
"""
from pathlib import Path
import subprocess
import json
from .effects import encoder_args
from .gpu_pipeline import detect
from . import gpu_full
from .gpu_qa_transitions import SpatialStage
from .performance_diagnostics import run_render, _encoder_name

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
                           log=lambda _m:None, subprocess_run=None, width=1920, height=1080, fps=60, encoder_policy="auto"):
    """Produce one visually distinct, muted comparison using *existing* MP4s.

    No Replay API re-record, no change to game-audio output in production.
    """
    first, second, dest = Path(first), Path(second), Path(dest)
    if not first.exists() or not second.exists():
        raise FileNotFoundError("QA reference clips are missing")
    dest.parent.mkdir(parents=True,exist_ok=True)
    src_seconds = min(get_duration(first,ffmpeg=str(ffmpeg_exe())),
                      get_duration(second,ffmpeg=str(ffmpeg_exe())))
    if src_seconds < .7:
        raise ValueError("QA reference video is too short for a transition")
    length = min(2.6,src_seconds-.08)
    transition_seconds = min(0.45, max(.18,length*.28))
    graph_cpu = build_xfade_filter(style,length=length,duration=transition_seconds,
                                   width=width,height=height,fps=fps)
    caps=detect();stage=None;reason="explicit_cpu_comparison" if gpu_full.mode()=="cpu" else (getattr(caps,"full_probe_reason",None) or "full_gpu_runtime_unverified")
    try:
        if gpu_full.mode()!="cpu" and caps.full_gpu_runtime_ok:
            try:
                stage=SpatialStage(style,length,transition_seconds,width=width,height=height,fps=fps)
            except (OSError,ValueError,RuntimeError) as exc:
                reason="GPU spatial preparation failed: "+str(exc)
        def render(on_gpu):
            graph=stage.graph if on_gpu else graph_cpu
            cmd=[str(ffmpeg_exe()),"-nostdin","-hide_banner","-loglevel","error","-y","-filter_complex_threads","1"]
            if on_gpu:cmd += ["-init_hw_device",gpu_full.OPENCL_DEVICE,"-filter_hw_device","ocl"]
            cmd += ["-i",str(first),"-i",str(second),"-filter_complex",graph,"-map","[v]","-an"]
            enc=encoder_args(fps,policy=encoder_policy)
            if on_gpu and "h264_nvenc" in enc:enc[enc.index("-pix_fmt")+1]="rgba"
            cmd += enc+["-t",f"{2*length-transition_seconds:.9f}",str(dest)]
            info={"qa_kind":"spatial_transition","full_gpu_pipeline":on_gpu,
                  "pixel_processing":"OpenCL GPU" if on_gpu else "CPU xfade",
                  "output_fps":fps,"effects_fps":fps,"encoder_policy":encoder_policy,
                  "filter_graph":graph,"gpu_effects_unavailable_reason":None if on_gpu else reason}
            if subprocess_run:
                result=subprocess_run(cmd,capture_output=True,timeout=300)
            else:
                result=run_render(cmd,output=dest,gpu_effects=["spatial_"+style] if on_gpu else [],
                                  effect_values={"spatial_style":style},pipeline_info=info,
                                  fallback_reason=None if on_gpu else reason,timeout=300)
            return result,cmd
        used_gpu=stage is not None
        if used_gpu:
            try:
                result,cmd=render(True)
                if result.returncode:
                    reason="GPU spatial render failed: "+str(getattr(result,"stderr",""))[-700:];used_gpu=False
            except (OSError,RuntimeError,subprocess.TimeoutExpired) as exc:
                reason="GPU spatial render failed: "+str(exc);used_gpu=False
        if not used_gpu:
            log("空間切替QA: CPUフォールバック ("+reason+")")
            result,cmd=render(False)
        if result.returncode:
            raise RuntimeError("Spatial transition failed: "+str(getattr(result,"stderr",""))[-700:])
        if not dest.is_file() or dest.stat().st_size<=1024:
            raise RuntimeError("No preview MP4 written")
        report={"gpu_effects_confirmed":used_gpu,"effects_backend":"OpenCL GPU" if used_gpu else "CPU xfade",
                "encoder":_encoder_name(getattr(result,"args",cmd)),"encoder_policy":encoder_policy,
                "encoder_retry_reason":getattr(result,"encoder_retry_reason",None),
                "fallback_reason":None if used_gpu else reason,"output_fps":fps,
                "join_seconds":length-transition_seconds/2,"qa_only":True,"no_audio":True}
        dest.with_suffix(".render.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        log(f"空間切替の試作品: {style} → {dest.name}")
        return dest
    finally:
        if stage is not None:stage.close()
