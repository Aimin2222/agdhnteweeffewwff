"""Isolated startup and synthetic 1080p60 audio/render checks (no LoL capture)."""
from pathlib import Path
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def gui_check():
    import tkinter as tk
    import app
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *exc: errors.append(str(exc))
    instance = app.App(root)
    root.after(2500, instance.on_close)
    root.mainloop()
    if errors:
        raise RuntimeError(errors)
    print('App startup/event loop/close: PASS (isolated default settings)')


def media_check():
    import numpy as np
    from core import effects, gpu_pipeline
    from core.effects import Template
    ffmpeg = effects.FFMPEG
    print('FFmpeg:', ffmpeg, flush=True)
    print('Capabilities:', gpu_pipeline.detect(), flush=True)
    source = ROOT / 'synthetic_source.mp4'
    game_wav = ROOT / 'synthetic_game.wav'
    subprocess.run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error',
                    '-f', 'lavfi', '-i', 'color=c=red:s=1920x1080:r=60:d=1',
                    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-t', '1', str(source)], check=True, timeout=60)
    subprocess.run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error',
                    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
                    str(game_wav)], check=True, timeout=30)
    results = []
    for policy, mode in [('gpu', 'full'), ('cpu', 'cpu')]:
        os.environ['AUTOCINE_GPU_EFFECTS'] = mode
        destination = ROOT / f'synthetic_{policy}.mp4'
        template = Template(fps=60, encoder_policy=policy, grade='standard',
                            grade_strength=0, bloom=.15, vignette=0, grain=0,
                            bars=0, transition='cut', title_auto=False,
                            game_audio=True, kill_icon_style='off')
        effects.apply_effects(source, destination, template, 1, [],
                             size=(1920, 1080), game_wav=game_wav)
        probe = subprocess.run([ffmpeg, '-hide_banner', '-i', str(destination),
                                '-f', 'null', '-'], capture_output=True, text=True,
                               encoding='utf-8', errors='replace', timeout=60)
        assert probe.returncode == 0, probe.stderr
        assert '1920x1080' in probe.stderr and '60 fps' in probe.stderr
        assert 'Audio:' in probe.stderr
        duration = re.search(r'Duration: (\d+):(\d+):([\d.]+)', probe.stderr)
        seconds = int(duration[1])*3600 + int(duration[2])*60 + float(duration[3])
        assert abs(seconds - 1) < .1, seconds
        raw = subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error',
                              '-i', str(destination), '-frames:v', '1',
                              '-vf', 'scale=64:36', '-f', 'rawvideo',
                              '-pix_fmt', 'rgb24', '-'], capture_output=True, timeout=30)
        assert raw.returncode == 0 and len(raw.stdout) == 64*36*3
        rgb = np.frombuffer(raw.stdout, dtype=np.uint8).reshape(-1, 3).mean(axis=0)
        assert rgb[0] > rgb[1] + 80 and rgb[0] > rgb[2] + 80, rgb
        volume = subprocess.run([ffmpeg, '-hide_banner', '-i', str(destination),
                                 '-af', 'volumedetect', '-vn', '-f', 'null', '-'],
                                capture_output=True, text=True, timeout=30)
        mean = re.search(r'mean_volume: (-?[\d.]+) dB', volume.stderr)
        assert mean and float(mean[1]) > -60
        telemetry = sorted((ROOT/'diagnostics'/'performance').glob('render_*.json'))
        data = json.loads(telemetry[-1].read_text(encoding='utf-8'))
        results.append({'policy': policy, 'duration': seconds,
                        'rgb_mean': rgb.tolist(), 'audio_mean_db': float(mean[1]),
                        'encoder': data['encoder'],
                        'gpu_effects_confirmed': data['gpu_effects_confirmed']})
    print(json.dumps(results, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=['gui', 'media'])
    args = parser.parse_args()
    if args.worker:
        sys.path.insert(0, str(ROOT))
        (gui_check if args.worker == 'gui' else media_check)()
        return 0
    from run_local_tests import copy_source
    sys.path.insert(0, str(ROOT))
    from core.gpu_binary import ffmpeg_exe
    folder = ROOT/'diagnostics'/'local_dev'/dt.datetime.now().strftime('smoke_%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
               PYTHONDONTWRITEBYTECODE='1')
    default = ffmpeg_exe()
    checks = [('gui_default', 'gui', default), ('media_default', 'media', default)]
    local = shutil.which('ffmpeg')
    if local and local != default:
        checks.append(('media_local_ffmpeg', 'media', local))
    results = []
    with tempfile.TemporaryDirectory(prefix='autocine-local-smoke-') as temporary:
        workspace = Path(temporary)/'LoL_AutoCine'
        copy_source(workspace)
        for label, worker, ffmpeg in checks:
            env['IMAGEIO_FFMPEG_EXE'] = ffmpeg
            result = subprocess.run([sys.executable, '-B', 'tools/run_local_smoke.py',
                                     '--worker', worker], cwd=workspace, env=env,
                                    capture_output=True, text=True, encoding='utf-8',
                                    errors='replace', timeout=180)
            output = result.stdout + result.stderr
            (folder/f'{label}.log').write_text(output, encoding='utf-8')
            print(label, result.returncode, output, flush=True)
            results.append({'check': label, 'returncode': result.returncode})
        shutil.copytree(workspace/'diagnostics', folder/'test_diagnostics')
    (folder/'summary.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('Local reports:', folder)
    return 0 if all(row['returncode'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
