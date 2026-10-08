"""Best-effort per-render telemetry; never prevents rendering."""
import csv
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import zipfile


def _sample_gpu():
    exe = shutil.which('nvidia-smi')
    if not exe:
        return {}
    try:
        p = subprocess.run([exe, '--query-gpu=utilization.gpu,utilization.encoder,memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        values = [float(x.strip()) for x in p.stdout.strip().splitlines()[0].split(',')]
        return dict(zip(('gpu_pct', 'encoder_pct', 'vram_used_mb', 'vram_total_mb', 'gpu_temp_c'), values))
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return {}


def run_render(cmd, *, output, gpu_effects, effect_values, fallback_reason=None,
               pipeline_info=None, timeout=600):
    """subprocess.run-compatible CompletedProcess with diagnostics in diagnostics/performance."""
    base = Path(__file__).resolve().parent.parent / 'diagnostics'
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    folder = base / 'performance'
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    stop = threading.Event()
    try:
        import psutil
    except ImportError:
        psutil = None
    def sample():
        while not stop.is_set():
            row = {'elapsed_s': round(time.monotonic() - start, 2)}
            if psutil:
                row['cpu_pct'] = psutil.cpu_percent(interval=None)
                row['ram_used_mb'] = round(psutil.virtual_memory().used / 1048576)
            try:
                row.update(_sample_gpu())
                rows.append(row)
            except Exception:
                pass
            stop.wait(3)
    start = time.monotonic()
    worker = threading.Thread(target=sample, daemon=True, name='AutoCineTelemetry')
    try:
        worker.start()
    except Exception:
        worker = None
    error = None
    result = None
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        return result
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        stop.set()
        if worker is not None:
            worker.join(timeout=0.3)
        fields = ['elapsed_s', 'cpu_pct', 'ram_used_mb', 'gpu_pct', 'encoder_pct', 'vram_used_mb', 'vram_total_mb', 'gpu_temp_c']
        try:
            csv_path = folder / ('render_' + stamp + '.csv')
            with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            stderr = (result.stderr if result else '') or ''
            log_path = base / 'ffmpeg' / ('render_' + stamp + '.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text('Command: ' + subprocess.list2cmdline([str(x) for x in cmd]) + '\n\n' + stderr + '\n' + (error or ''), encoding='utf-8')
            data = {'started_at': stamp, 'output': str(output), 'elapsed_s': round(time.monotonic()-start, 3), 'returncode': result.returncode if result else None, 'error': error, 'gpu_effects_requested': list(gpu_effects), 'effect_values': effect_values, 'fallback_reason': fallback_reason, 'encoder': 'h264_nvenc' if 'h264_nvenc' in cmd else 'CPU/other', 'gpu_effects_attempted': bool(gpu_effects), 'gpu_effects_confirmed': bool(gpu_effects) and result is not None and result.returncode == 0, 'pipeline': pipeline_info or {}, 'effective_processing_fps': round(float((pipeline_info or {}).get('output_fps', 0) or 0) * float((pipeline_info or {}).get('duration_s', 0) or 0) / max(time.monotonic()-start,0.001), 2) if (pipeline_info or {}).get('duration_s') else None, 'samples': len(rows), 'metrics': {key: {'avg': round(sum(r[key] for r in rows if key in r) / len([r for r in rows if key in r]), 2), 'max': max(r[key] for r in rows if key in r)} for key in fields[1:] if any(key in r for r in rows)}}
            json_path = folder / ('render_' + stamp + '.json')
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            with zipfile.ZipFile(base / 'latest_diagnostics.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for path in (csv_path, json_path, log_path):
                    z.write(path, path.relative_to(base))
        except Exception:
            # Telemetry must never mask an FFmpeg result or crash the render worker.
            pass
