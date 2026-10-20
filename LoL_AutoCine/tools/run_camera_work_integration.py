"""Offline 1080p60 Work/export tests; synthetic portraits/audio, no LoL visual approval."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    folder = args.output.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    import numpy as np
    from core import effects
    from core.effects import Template
    from core.scanner import Kill
    from core.kill_icons import MOTION_STYLES
    from core.work_kill_assets import render_preview_pair
    from ui.director_work_controls import mirror_event_rows
    ffmpeg = effects.FFMPEG
    source, wav = folder/'synthetic.mp4', folder/'synthetic.wav'
    def run(command, **kw):
        result = subprocess.run(command, capture_output=True, timeout=180, **kw)
        if result.returncode: raise RuntimeError(result.stderr.decode('utf-8', 'replace')[-5000:])
        return result
    run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
         'color=c=0x20242a:s=1920x1080:r=60:d=3', '-c:v', 'libx264', '-preset', 'ultrafast', str(source)])
    run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
         'sine=frequency=440:duration=3', str(wav)])
    icons = []
    for index, color in enumerate(('#2475db', '#d93946')):
        path = folder/f'synthetic_portrait_{index}.png'
        Image.new('RGBA', (128, 128), color).save(path)
        icons.append(path)
    roster = [dict(name='SyntheticA', selection_name='Ashe'), dict(name='SyntheticB', selection_name='Lux')]
    kills = [Kill(1, .4, 'SyntheticA', 'SyntheticB', []), Kill(2, 1., 'SyntheticB', 'SyntheticA', [])]
    records = []
    for index, motion in enumerate(MOTION_STYLES):
        output = folder/f'{motion}.mp4'
        template = Template(fps=60, encoder_policy='gpu', grade='standard', grade_strength=0,
            bloom=0, vignette=0, grain=0, bars=0, transition='cut', title_auto=False,
            game_audio=True, kill_icon_style='off', kill_icon_players=roster,
            work_kill_frame_id='083/a_simple_main', work_kill_effect_id='A',
            work_kill_review=True, work_kill_strength='weak' if index % 2 else 'strong',
            kill_icon_motion=motion, camera_control_mode='fixed_auto' if index % 2 else 'full_auto')
        os.environ['AUTOCINE_GPU_EFFECTS'] = 'full'
        with patch('core.kill_icons.champion_icon', side_effect=lambda p: icons[0 if p['name']=='SyntheticA' else 1]):
            effects.apply_effects(source, output, template, 3., kills,
                                 effect_events=[(.4, 1.), (1., 1.)], size=(1920, 1080), game_wav=wav)
        decoded = run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(output),
                       '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        frames = np.frombuffer(decoded.stdout, dtype=np.uint8).reshape(-1, 1080, 1920, 3)
        assert len(frames) == 180, len(frames)
        # Compare the real export against the same event-relative preview at six clocks.
        differences = []
        for at in (.2, .45, .7, 1.1, 1.5, 2.7):
            base = Image.new('RGBA', (1920, 1080), '#20242a')
            active = mirror_event_rows([k.to_dict() for k in kills], at, template.kill_icon_duration)
            for kill, row in active:
                pair = icons if kill['killer']=='SyntheticA' else icons[::-1]
                base.alpha_composite(render_preview_pair(template, *pair, at-kill['time'], row=row))
            expected = np.asarray(base.convert('RGB')).astype(float)
            actual = frames[round(at*60)].astype(float)
            # Compression/chroma and resize kernels differ; compare badge region with tolerance.
            difference = float(np.abs(actual[:500, 1450:]-expected[:500, 1450:]).mean())
            differences.append(dict(time=at, mean_absolute_rgb_error=difference))
            if difference > 12: raise AssertionError((motion, at, difference))
            if at == 1.1: Image.fromarray(frames[round(at*60)]).save(folder/f'{motion}_multikill.png')
        probe = subprocess.run([ffmpeg, '-hide_banner', '-i', str(output), '-af', 'volumedetect',
                                '-vn', '-f', 'null', '-'], capture_output=True, timeout=60)
        description = probe.stderr.decode('utf-8', 'replace')
        volume = re.search(r'mean_volume: (-?[\d.]+) dB', description)
        assert probe.returncode == 0 and volume and float(volume[1]) > -60
        assert '1920x1080' in description and '60 fps' in description
        telemetry = sorted((ROOT/'diagnostics/performance').glob('render_*.json'))
        data = json.loads(telemetry[-1].read_text('utf-8'))
        records.append(dict(motion=motion, frames=len(frames), fps=60, size=[1920,1080],
            audio_mean_db=float(volume[1]), encoder=data['encoder'],
            gpu_effects_confirmed=data['gpu_effects_confirmed'], comparisons=differences))
        (folder/'results.json').write_text(json.dumps(dict(scope='synthetic offline integration; real LoL capture not tested',
            records=records), ensure_ascii=False, indent=2), 'utf-8')
        print(motion, records[-1], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
