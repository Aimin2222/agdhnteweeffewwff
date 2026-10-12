"""Reuse a recorded clip for 60fps badge QA, using the production GPU stage."""
from pathlib import Path
import math
import subprocess

from . import gpu_full
from .effects import Template, encoder_args
from .gpu_binary import ffmpeg_exe
from .gpu_pipeline import detect
from .kill_icons import with_badges
from .performance_diagnostics import run_render, _encoder_name


def render_badge_motion(source, destination, badge, theme, motion, duration, *,
                        encoder_policy='auto', log=lambda _m: None, size=(1920, 1080)):
    """Only add the test badge; copy existing audio and keep prior clip effects.

    CPU fallback uses the same motion, position, scale, duration and audio.
    A successful NVENC retry still reports the actual encoder separately.
    """
    source, destination, badge = map(Path, (source, destination, badge))
    duration = float(duration)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Invalid badge QA duration')
    destination.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = str(ffmpeg_exe())
    tpl = Template(fps=60, grade='standard', grade_strength=0, bloom=0,
                   vignette=0, grain=0, transition='cut', kill_icon_style=theme,
                   kill_icon_motion=motion, kill_icon_duration=2.1)
    caps = detect()
    stage = None
    reason = ('explicit_cpu_comparison' if gpu_full.mode() == 'cpu' else
              getattr(caps, 'full_probe_reason', 'full_gpu_runtime_unverified'))
    decoded = False
    try:
        if gpu_full.mode() != 'cpu' and caps.full_gpu_runtime_ok:
            try:
                stage = gpu_full.GPUFullStage(tpl, duration, [], ffmpeg=ffmpeg,
                    badges=[(badge, .45)], badge_index=1, lut_index=2, size=size)
                decoded, _ = gpu_full.decode_probe(ffmpeg, str(source), source.stat().st_mtime_ns)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
                reason = f'GPU badge preparation failed: {exc}'
                if stage is not None:
                    stage.close()
                    stage = None

        def render(on_gpu):
            cmd = [ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-filter_complex_threads', '1']
            if on_gpu:
                cmd += ['-init_hw_device', gpu_full.OPENCL_DEVICE, '-filter_hw_device', 'ocl']
                if decoded:
                    cmd += ['-hwaccel', 'cuda']
            cmd += ['-i', str(source)]
            if not on_gpu:
                cmd += ['-loop', '1', '-framerate', '60']
            cmd += ['-i', str(badge)]
            if on_gpu:
                cmd += ['-i', str(stage.lut)]
                graph = stage.graph
            else:
                graph = with_badges('[0:v]fps=fps=60:round=near,setpts=PTS-STARTPTS,format=rgba[vout]',
                                    1, [(badge, .45)], duration=duration,
                                    seconds=2.1, style=theme, motion=motion)
            encoding = encoder_args(60, policy=encoder_policy)
            if on_gpu and 'h264_nvenc' in encoding:
                encoding[encoding.index('-pix_fmt') + 1] = 'rgba'
            cmd += ['-filter_complex', graph, '-map', '[vout]', '-map', '0:a?',
                    '-c:a', 'copy', '-t', f'{duration:.3f}'] + encoding + ['-movflags', '+faststart', str(destination)]
            info = {'qa_kind': 'badge_motion', 'full_gpu_pipeline': on_gpu,
                    'pixel_processing': 'OpenCL GPU' if on_gpu else 'CPU',
                    'gpu_effects_unavailable_reason': None if on_gpu else reason,
                    'output_fps': 60, 'effects_fps': 60, 'kill_icon_motion': tpl.kill_icon_motion,
                    'encoder_policy': encoder_policy, 'filter_graph': graph,
                    'video_decoder': 'NVDEC' if on_gpu and decoded else 'CPU',
                    'main_frame_uploads': 1 if on_gpu else 0,
                    'main_frame_downloads': 1 if on_gpu else 0,
                    'cpu_video_effects': [] if on_gpu else ['kill_icons', 'kill_icon_motion']}
            result = run_render(cmd, output=destination, gpu_effects=stage.effects if on_gpu else [],
                                effect_values={'kill_icon_motion': tpl.kill_icon_motion},
                                fallback_reason=None if on_gpu else reason,
                                pipeline_info=info, timeout=180)
            return result, cmd

        used_gpu = stage is not None
        if used_gpu:
            try:
                result, cmd = render(True)
                if result.returncode:
                    reason = 'GPU badge render failed: ' + (result.stderr or '')[-700:]
                    used_gpu = False
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                reason = f'GPU badge render failed: {exc}'
                used_gpu = False
        if not used_gpu:
            log(f'キル表示QA: CPUフォールバック ({reason})')
            result, cmd = render(False)
        if result.returncode:
            raise RuntimeError('Badge QA failed: ' + (result.stderr or '')[-1200:])
        if not destination.is_file() or not destination.stat().st_size:
            raise RuntimeError('Badge QA did not produce a video')
        return {'gpu_effects_confirmed': used_gpu,
                'effects_backend': 'OpenCL GPU' if used_gpu else 'CPU',
                'encoder': _encoder_name(getattr(result, 'args', cmd)),
                'encoder_policy': encoder_policy,
                'encoder_retry_reason': getattr(result, 'encoder_retry_reason', None),
                'fallback_reason': None if used_gpu else reason,
                'output_fps': 60, 'duration_s': duration,
                'audio': 'copy_from_recorded_clip'}
    finally:
        if stage is not None:
            stage.close()
