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


def cpu_encoder_retry_command(command):
    """Safe NVENC-to-CPU retry without changing effects, inputs or audio mapping."""
    args=list(command)
    positions=[i+1 for i in range(len(args)-1)
               if args[i]=='-c:v' and args[i+1]=='h264_nvenc']
    if len(positions)!=1: return None
    idx=positions[0]
    tail=[]
    cursor=idx+1
    while cursor<len(args):
        if args[cursor] in {'-preset','-tune','-rc','-cq','-b:v'}:
            if cursor+1>=len(args): return None
            cursor+=2
        else:
            tail.append(args[cursor]);cursor+=1
    # RGBA input lets NVENC perform its color conversion on hardware. libx264
    # must explicitly return to the compatible 4:2:0 software output format.
    for n in range(len(tail)-1):
        if tail[n]=='-pix_fmt': tail[n+1]='yuv420p'
    return args[:idx]+['libx264','-preset','medium','-crf','17']+tail


def _encoder_name(command):
    for i in range(len(command)-1):
        if command[i]=='-c:v': return command[i+1]
    return 'other'


def record_encoding_result(command, *, output, returncode, error=None,
                           fallback_reason=None, pipeline_info=None):
    """Best-effort telemetry for the streaming recorder, which owns its stdin."""
    try:
        root=Path(__file__).resolve().parent.parent/'diagnostics'
        folder=root/'performance';folder.mkdir(parents=True,exist_ok=True)
        stamp=dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        data={'started_at':stamp,'output':str(output),'returncode':returncode,'error':error,
              'command':list(command),'encoder':_encoder_name(command),
              'encoder_retry_reason':fallback_reason,'fallback_reason':fallback_reason,
              'gpu_effects_attempted':False,'gpu_effects_confirmed':False,
              'pipeline':pipeline_info or {}}
        (folder/('render_'+stamp+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception:
        pass


def latest_render_summary(base=None):
    """Read actual last render telemetry. Do not confuse NVENC with GPU video effects."""
    root=Path(base) if base is not None else Path(__file__).resolve().parent.parent/'diagnostics'
    logs=sorted((root/'performance').glob('render_*.json'))
    if not logs: return '実績なし（書き出し後に更新）'
    try:
        data=json.loads(logs[-1].read_text(encoding='utf-8'))
        encoder=data.get('encoder','不明')
        gpu_fx=bool(data.get('gpu_effects_confirmed',False))
        reason=data.get('encoder_retry_reason') or data.get('fallback_reason')
        ok=data.get('returncode')==0 and not data.get('error')
        state='成功' if ok else '失敗'
        fx=('GPU' if gpu_fx else 'CPU') if ok else '未完了'
        return f'直近: {state} / 映像エンコード {encoder} / エフェクト {fx}' + (f' / CPU切替: {str(reason)[:75]}' if reason else '')
    except (ValueError, OSError, TypeError):
        return '直近の診断を読み取れません'


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
               pipeline_info=None, timeout=600, allow_encoder_retry=True):
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
    process = psutil.Process() if psutil else None
    ffmpeg_processes = {}
    def sample():
        while not stop.is_set():
            row = {'elapsed_s': round(time.monotonic() - start, 2)}
            if psutil:
                row['cpu_pct'] = psutil.cpu_percent(interval=None)
                row['ram_used_mb'] = round(psutil.virtual_memory().used / 1048576)
                try:
                    row['python_cpu_pct'] = process.cpu_percent(interval=None)
                    total = 0.0
                    alive = set()
                    for child in process.children(recursive=True):
                        if 'ffmpeg' not in child.name().lower(): continue
                        alive.add(child.pid)
                        cached = ffmpeg_processes.setdefault(child.pid,child)
                        total += cached.cpu_percent(interval=None)
                    for pid in set(ffmpeg_processes)-alive: del ffmpeg_processes[pid]
                    # psutil process percentages sum logical cores and may
                    # exceed 100%; normalized value is share of this PC.
                    row['ffmpeg_cpu_pct'] = round(total,2)
                    row['ffmpeg_cpu_pc_pct'] = round(total/max(1,psutil.cpu_count() or 1),2)
                except (psutil.Error,OSError):
                    pass
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
    actual_command = list(cmd)
    encoder_retry_reason = None
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        if result.returncode != 0 and allow_encoder_retry:
            retry=cpu_encoder_retry_command(cmd)
            if retry is not None:
                encoder_retry_reason='NVENC選択時の書き出し失敗 → libx264で再試行: '+(result.stderr or '')[-450:]
                actual_command=retry
                result=None
                result=subprocess.run(retry,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        result.args=actual_command
        result.encoder_retry_reason=encoder_retry_reason
        return result
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        stop.set()
        if worker is not None:
            worker.join(timeout=0.3)
        fields = ['elapsed_s', 'cpu_pct', 'ram_used_mb', 'gpu_pct', 'encoder_pct', 'vram_used_mb', 'vram_total_mb', 'gpu_temp_c',
                  'python_cpu_pct','ffmpeg_cpu_pct','ffmpeg_cpu_pc_pct']
        try:
            csv_path = folder / ('render_' + stamp + '.csv')
            with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            stderr = (result.stderr if result else '') or ''
            log_path = base / 'ffmpeg' / ('render_' + stamp + '.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text('Command: ' + subprocess.list2cmdline([str(x) for x in cmd]) + '\n\n' + ('CPU retry command: '+subprocess.list2cmdline([str(x) for x in actual_command])+'\n' if encoder_retry_reason else '') + stderr + '\n' + (error or '') + '\n' + (encoder_retry_reason or ''), encoding='utf-8')
            pipeline_info = dict(pipeline_info or {})
            if encoder_retry_reason and _encoder_name(actual_command)=='libx264':
                pipeline_info['encoder_color_conversion']='software YUV420P (NVENC retry)'
            data = {'started_at': stamp, 'output': str(output), 'elapsed_s': round(time.monotonic()-start, 3), 'returncode': result.returncode if result else None, 'error': error, 'command': actual_command, 'gpu_effects_requested': list(gpu_effects), 'effect_values': effect_values, 'fallback_reason': fallback_reason or encoder_retry_reason, 'encoder_retry_reason': encoder_retry_reason, 'encoder': _encoder_name(actual_command), 'gpu_effects_attempted': bool(gpu_effects), 'gpu_effects_confirmed': bool(gpu_effects) and error is None and result is not None and result.returncode == 0, 'pipeline': pipeline_info or {}, 'effective_processing_fps': round(float((pipeline_info or {}).get('output_fps', 0) or 0) * float((pipeline_info or {}).get('duration_s', 0) or 0) / max(time.monotonic()-start,0.001), 2) if (pipeline_info or {}).get('duration_s') else None, 'samples': len(rows), 'metrics': {key: {'avg': round(sum(r[key] for r in rows if key in r) / len([r for r in rows if key in r]), 2), 'max': max(r[key] for r in rows if key in r)} for key in fields[1:] if any(key in r for r in rows)}}
            json_path = folder / ('render_' + stamp + '.json')
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            with zipfile.ZipFile(base / 'latest_diagnostics.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for path in (csv_path, json_path, log_path):
                    z.write(path, path.relative_to(base))
        except Exception:
            # Telemetry must never mask an FFmpeg result or crash the render worker.
            pass
