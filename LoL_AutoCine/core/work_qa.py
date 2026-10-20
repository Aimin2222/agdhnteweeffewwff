"""Developer-only Work asset and mirror checks attached to the 30 MB CameraQA run.

The checks prove file integrity and that draft compositing runs. They never
promote a source image or a video shot to visual/production approval.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw

from .effects import FFMPEG, Template
from .kill_icons import MOTION_STYLES
from .work_kill_assets import catalog, file_signature, _verified, render_preview_pair, resolve_asset


def _sheet(items, output, *, columns=4, cell=(260, 138)):
    width, height = cell
    rows = (len(items)+columns-1)//columns
    sheet = Image.new('RGB', (columns*width, rows*height), '#e9edf3')
    draw = ImageDraw.Draw(sheet)
    for index, (label, image) in enumerate(items):
        x, y = (index % columns)*width, (index//columns)*height
        tile = Image.new('RGBA', (width-12, height-33), '#172331')
        source = image.copy()
        source.thumbnail((tile.width-8, tile.height-8), Image.Resampling.LANCZOS)
        tile.alpha_composite(source, ((tile.width-source.width)//2,
                                      (tile.height-source.height)//2))
        sheet.paste(tile.convert('RGB'), (x+6, y+4))
        draw.text((x+8, y+height-26), label[:37], fill='#202c40')
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=82, optimize=True)


def _mirror_probe(source_video):
    from .gpu_mirror import probe, render, last_status
    available, device = probe()
    report = {'device': device, 'opencl_gpu_available': bool(available),
              'scope': 'one decoded sample frame; excludes WGC capture and Tk upload'}
    if not source_video or not Path(source_video).is_file():
        report['sample'] = 'no recorded clip'
        return report
    with tempfile.TemporaryDirectory(prefix='autocine-work-qa-') as folder:
        still = Path(folder)/'sample.png'
        command = [FFMPEG, '-y', '-hide_banner', '-loglevel', 'error', '-ss', '1',
                   '-i', str(source_video), '-frames:v', '1', str(still)]
        result = subprocess.run(command, capture_output=True, timeout=30)
        if result.returncode or not still.is_file():
            report['sample'] = 'frame extraction failed'
            return report
        with Image.open(still) as image:
            rgba = np.asarray(image.convert('RGBA'))
        bgra = rgba[:, :, [2, 1, 0, 3]].copy()
        template = Template(bloom=.4, dof_enabled=True, dof_blur=3., vignette=.3)
        times = []
        for _ in range(11):
            started = time.perf_counter()
            rendered = render(bgra, 640, 360, template)
            times.append((time.perf_counter()-started)*1000)
            if rendered is None:
                break
        report['sample'] = 'decoded CameraQA clip'
        report['backend'], report['reason'] = last_status()
        report['warm_median_ms'] = round(statistics.median(times[1:]), 2) if len(times)>1 else None
        report['sample_passed'] = rendered is not None and rendered[0].shape[2] == 3
    return report


def run_work_qa(folder, *, source_video=None, stop=None, log=lambda _message: None):
    """Audit 998 source images, draft pair modes and all 35 effect animations."""
    from .work_kill_assets import ROOT
    destination = Path(folder)/'WorkQA'
    destination.mkdir(parents=True, exist_ok=True)
    data = catalog()
    report = {'created_at': datetime.now().isoformat(timespec='seconds'),
              'source_commit': data.get('source_commit'),
              'frames_total': len(data['frames']),
              'frames_approved': sum(x['status']=='approved' for x in data['frames']),
              'effects_total': len(data['effects']),
              'effects_approved': sum(x['status']=='approved' for x in data['effects']),
              'legacy_layers_total': len(data['legacy_layers']),
              'files_checked': 0, 'file_errors': [], 'effect_errors': [],
              'effect_composites_checked': 0, 'draft_composites_checked': 0,
              'motion_styles_checked': [], 'motion_errors': [],
              'contact_sheets': [],
              'visual_approval': 'not_performed; human source comparison required'}
    report_path = destination/'report.json'
    def flush():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    flush()
    log('Work素材QA: 原本のSHA・RGBA・寸法を998件検査中。画像原本は変更しません。')
    for row in data['frames']+data['effects']+data['legacy_layers']:
        if stop is not None and stop.is_set():
            report['canceled'] = True
            flush()
            return report_path
        path = ROOT/row['path']
        try:
            if not _verified(file_signature(path), row['sha256']):
                raise ValueError('SHA256 mismatch')
            with Image.open(path) as image:
                if image.format != 'PNG' or image.mode != 'RGBA':
                    raise ValueError('not RGBA PNG')
                if 'width' in row and image.size != (row['width'], row['height']):
                    raise ValueError('dimension mismatch')
            report['files_checked'] += 1
        except (OSError, ValueError) as exc:
            report['file_errors'].append({'id': row.get('id', row['path']),
                                          'error': f'{type(exc).__name__}: {exc}'})
    flush()
    log(f"Work素材QA: {report['files_checked']}件のファイル検査を完了。図鑑シートを作成中。")
    for start in range(0, len(data['frames']), 24):
        if stop is not None and stop.is_set():
            break
        cells = []
        for row in data['frames'][start:start+24]:
            try:
                _, path = resolve_asset(row['id'], review=True)
                with Image.open(path) as image:
                    cells.append((row['id']+' ['+row['status']+']', image.convert('RGBA').copy()))
            except (OSError, ValueError) as exc:
                report['file_errors'].append({'id': row['id'], 'error': str(exc)})
        if cells:
            target = destination/f'frames_{start//24+1:02d}.jpg'
            _sheet(cells, target)
            report['contact_sheets'].append(target.name)
        if (start//24+1) % 8 == 0:
            log(f"Work素材QA: フレーム図鑑 {min(start+24,len(data['frames']))}/{len(data['frames'])}件")
    with tempfile.TemporaryDirectory(prefix='autocine-work-icons-') as temp:
        a, b = Path(temp)/'a.png', Path(temp)/'b.png'
        for path, color in ((a, '#326fcb'), (b, '#b83e4d')):
            image = Image.new('RGBA', (128, 128), color)
            ImageDraw.Draw(image).text((30, 55), 'DEMO', fill='white')
            image.save(path)
        # Sample multiple draft geometries and the approved path; all 652
        # source files were checked above without inventing approved holes.
        sample = [data['frames'][i] for i in (0, 1, 2, len(data['frames'])//2, -3, -2, -1)]
        sample.append(next(x for x in data['frames'] if x['status']=='approved'))
        for row in sample:
            try:
                template = Template(work_kill_frame_id=row['id'], work_kill_review=True)
                render_preview_pair(template, a, b, .2, size=(640, 360))
                report['draft_composites_checked'] += 1
            except Exception as exc:
                report['file_errors'].append({'id': row['id'], 'error': f'composite: {exc}'})
        motions = []
        for motion in MOTION_STYLES:
            try:
                template = Template(work_kill_frame_id='083/a_simple_main',
                                    work_kill_review=True, kill_icon_motion=motion)
                for elapsed in (.08, .35, 1.0):
                    image = render_preview_pair(template, a, b, elapsed, size=(640, 360))
                    if elapsed == .35 and image.getbbox() is None:
                        raise ValueError('motion is invisible at 0.35s')
                    motions.append((f'{motion} {elapsed:.2f}s', image))
                report['motion_styles_checked'].append(motion)
            except Exception as exc:
                report['motion_errors'].append({'motion': motion, 'error': f'{type(exc).__name__}: {exc}'})
        if motions:
            target = destination/'work_six_entrances.jpg'
            _sheet(motions, target, columns=3)
            report['contact_sheets'].append(target.name)
        effects = []
        for row in data['effects']:
            if stop is not None and stop.is_set():
                break
            try:
                template = Template(work_kill_frame_id='083/a_simple_main',
                                    work_kill_effect_id=row['id'], work_kill_review=True)
                render_preview_pair(template, a, b, .08, size=(640, 360))
                _, path = resolve_asset(row['id'], 'effects', review=True)
                with Image.open(path) as image:
                    effects.append((row['id']+' [review]', image.convert('RGBA').copy()))
                report['effect_composites_checked'] += 1
            except Exception as exc:
                report['effect_errors'].append({'id': row['id'], 'error': f'{type(exc).__name__}: {exc}'})
        for start in range(0, len(effects), 24):
            target = destination/f'effects_{start//24+1:02d}.jpg'
            _sheet(effects[start:start+24], target)
            report['contact_sheets'].append(target.name)
    log(f"Work素材QA: {report['effect_composites_checked']}/{len(data['effects'])}演出を合成。GPUミラーを計測中。")
    try:
        report['mirror_gpu'] = _mirror_probe(source_video)
    except Exception as exc:
        report['mirror_gpu'] = {'error': f'{type(exc).__name__}: {exc}'}
    report['completed'] = not (stop is not None and stop.is_set())
    flush()
    log(f"Work素材QA: {report['files_checked']}ファイル、{report['effect_composites_checked']}演出、"
        f"仮枠{report['draft_composites_checked']}例を確認。正式合格数は変更なし。")
    return report_path
