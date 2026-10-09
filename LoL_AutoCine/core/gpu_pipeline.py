# -*- coding: utf-8 -*-
"""LoL AutoCine GPU effects pipeline.

GPU effects are capability-probed instead of inferred from the mere presence of
scale_cuda/NVENC.  This prevents an unstable OpenCL path from being selected
on machines where the filter exists but the runtime/device does not.
"""
from __future__ import annotations
import subprocess
from dataclasses import dataclass
from functools import lru_cache

from .gpu_binary import ffmpeg_exe
from .gpu_bloom import OPENCL_DEVICE, shader_source
FFMPEG = ffmpeg_exe()


@dataclass(frozen=True)
class GPUCapabilities:
    nvenc: bool = False
    cuda: bool = False
    scale_cuda: bool = False
    opencl: bool = False
    gblur_opencl: bool = False
    unsharp_opencl: bool = False
    overlay_cuda: bool = False
    chromakey_cuda: bool = False
    opencl_runtime_ok: bool = False
    program_opencl: bool = False
    rgba_gpu_runtime_ok: bool = False
    rgba_probe_reason: str = ''


def _run(args: list[str], timeout: float = 10.0) -> tuple[int, str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except Exception as e:
        return -1, str(e)


@lru_cache(maxsize=1)
def _filters_text() -> str:
    _, txt = _run([FFMPEG, "-hide_banner", "-filters"])
    return txt.lower()


def _opencl_probe() -> bool:
    """実際にOpenCLフレームを1枚だけ通せるか確認する。

    フィルター名が存在するだけではWindows側のOpenCLランタイムが壊れている
    ケースがあるため、ここを通過した時だけGPU blurを使用する。
    """
    f = _filters_text()
    if "avgblur_opencl" not in f:
        return False
    # Upstream FFmpeg provides avgblur_opencl (not gblur_opencl). Test the
    # exact NV12 upload, filter and NV12 download path used by the renderer.
    candidates = [
        [FFMPEG, "-hide_banner", "-loglevel", "error",
         "-init_hw_device", OPENCL_DEVICE, "-filter_hw_device", "ocl",
         "-f", "lavfi", "-i", "color=c=0x4080c0:s=64x64:d=0.1",
         "-vf", "format=nv12,hwupload,avgblur_opencl=sizeX=3:sizeY=3:planes=1,hwdownload,format=nv12",
         "-frames:v", "1", "-f", "null", "-"],
    ]
    for cmd in candidates:
        rc, _ = _run(cmd, timeout=8.0)
        if rc == 0:
            return True
    return False


@lru_cache(maxsize=1)
def _rgba_probe():
    import tempfile
    from pathlib import Path
    from types import SimpleNamespace
    if 'program_opencl' not in _filters_text():
        return False, 'ffmpeg_missing_program_opencl'
    source = shader_source(SimpleNamespace(dof_blur=1,bloom=.25))
    with tempfile.TemporaryDirectory(prefix='autocine-opencl-probe-') as folder:
        path = Path(folder)/'probe.cl'
        path.write_text(source,encoding='utf-8')
        escaped = str(path).replace('\\','/').replace(':',r'\:').replace("'",r"\'")
        rc, text = _run([FFMPEG,'-hide_banner','-loglevel','error','-init_hw_device',OPENCL_DEVICE,
                        '-filter_hw_device','ocl','-f','lavfi','-i','color=c=0x4080c0:s=64x64:d=0.1',
                        '-vf',f"format=rgba,hwupload,program_opencl=source='{escaped}':kernel=copy_rgba,hwdownload,format=rgba",
                        '-frames:v','1','-f','null','-'],timeout=12)
    return rc == 0, '' if rc == 0 else text[-1000:]


@lru_cache(maxsize=1)
def detect() -> GPUCapabilities:
    _, enc = _run([FFMPEG, "-hide_banner", "-encoders"])
    enc = enc.lower()
    f = _filters_text()
    nvenc = "h264_nvenc" in enc
    scale_cuda = "scale_cuda" in f
    gblur_opencl = "avgblur_opencl" in f
    unsharp_opencl = "unsharp_opencl" in f
    opencl = "opencl" in f
    runtime_ok = _opencl_probe() if gblur_opencl else False
    rgba_ok, rgba_reason = _rgba_probe()
    return GPUCapabilities(
        nvenc=nvenc,
        cuda=nvenc or scale_cuda or "hwupload_cuda" in f,
        scale_cuda=scale_cuda,
        opencl=opencl,
        gblur_opencl=gblur_opencl,
        unsharp_opencl=unsharp_opencl,
        overlay_cuda="overlay_cuda" in f,
        chromakey_cuda="chromakey_cuda" in f,
        opencl_runtime_ok=runtime_ok,
        program_opencl='program_opencl' in f,
        rgba_gpu_runtime_ok=rgba_ok,
        rgba_probe_reason=rgba_reason,
    )


def backend_name(c: GPUCapabilities | None = None) -> str:
    c = c or detect()
    if c.nvenc and (c.opencl_runtime_ok or c.rgba_gpu_runtime_ok):
        return "OpenCL GPU Effects (verified) + NVIDIA NVENC"
    if c.nvenc:
        return "NVIDIA NVENC + CPU Effects fallback"
    if c.opencl_runtime_ok or c.rgba_gpu_runtime_ok:
        return "OpenCL GPU Effects + CPU Encode fallback"
    return "CPU Effects / CPU Encode"


GPU_OPENCL_BLUR = {"focus_blur", "vr_blur", "sphere_blur"}
GPU_OPENCL_SHARP = {"glint"}


def selected_gpu_effects(effect_values: dict, c: GPUCapabilities | None = None) -> set[str]:
    c = c or detect()
    if not c.opencl_runtime_ok:
        return set()
    out: set[str] = set()
    if c.gblur_opencl:
        out |= {k for k in GPU_OPENCL_BLUR if float(effect_values.get(k, 0.0)) > 0.001}
    if c.unsharp_opencl:
        out |= {k for k in GPU_OPENCL_SHARP if float(effect_values.get(k, 0.0)) > 0.001}
    return out


def gpu_prefix(effect_values: dict, c: GPUCapabilities | None = None) -> tuple[str, set[str]]:
    c = c or detect()
    selected = selected_gpu_effects(effect_values, c)
    if not selected:
        return "", set()
    parts: list[str] = ["format=nv12,hwupload"]
    consumed: set[str] = set()
    for key in ("focus_blur", "vr_blur", "sphere_blur"):
        if key in selected:
            v = float(effect_values.get(key, 0.0))
            sigma = 1.0 + 7.0 * v
            # Box blur approximates Gaussian on the GPU.
            # Luma-only avoids color shifts with NV12 hardware frames.
            radius = max(1, min(15, int(round(sigma))))
            parts.append(f"avgblur_opencl=sizeX={radius}:sizeY={radius}:planes=1")
            consumed.add(key)
    if "glint" in selected:
        v = float(effect_values.get("glint", 0.0))
        parts.append(f"unsharp_opencl=lx=5:ly=5:la={0.25 + 0.45*v:.3f}")
        consumed.add("glint")
    # hwdownload must use an actual OpenCL-supported software format.
    # Direct yuv420p downloads caused failures on NVIDIA/FFmpeg 7.x.
    parts += ["hwdownload", "format=nv12"]
    return ",".join(parts), consumed
