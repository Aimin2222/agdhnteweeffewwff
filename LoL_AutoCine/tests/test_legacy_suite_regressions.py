"""Real still-render and synthetic legacy camera/audio safety regressions."""
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
import pytest

from core.effects import Template, FFMPEG, apply_effects
from core.preview import render_exact_still, sample_scene
from tests import run_tests as legacy


def neutral(**changes):
    return Template(**(dict(grade='standard', grade_strength=0, contrast=1,
                           bloom=0, vignette=0, grain=0, bars=0, temperature=0,
                           title_auto=False, game_audio=False) | changes))


@pytest.mark.parametrize('size', [(480, 270), (960, 540), (1920, 1080), (511, 287)])
@pytest.mark.parametrize('effect', ['bloom', 'band_dof'])
def test_real_still_keeps_size_color_and_input_template(tmp_path, size, effect):
    width, height = size
    source = sample_scene(width, height)
    if effect == 'band_dof':
        # Fine colored texture makes a real blur measurable at every size.
        yy, xx = np.indices((height, width))
        source[(xx // 4 + yy // 4) % 2 == 0] = (240, 50, 80)
    original = source.copy()
    template = neutral(transition='flash', bpm=120,
                       **({'bloom': .3} if effect == 'bloom' else
                          {'dof_enabled': True, 'dof_blur': 5, 'dof_shape': 'band'}))
    before = template.to_dict()
    destination = render_exact_still(source, template, tmp_path/'preview.png')
    with Image.open(destination) as image:
        assert image.size == size and image.mode == 'RGB'
        pixels = np.asarray(image).astype(float)
    assert np.ptp(pixels.mean(axis=(0, 1))) > 10  # Keep a colored frame, not gray.
    assert pixels.std() > 20 and pixels.mean() < 230  # No first-frame white flash.
    assert template.to_dict() == before and np.array_equal(source, original)
    with Image.open(render_exact_still(source, neutral(), tmp_path/'neutral.png')) as image:
        unfiltered = np.asarray(image).astype(float)
    assert np.abs(pixels - unfiltered).mean() > .2  # Effect wasn't disabled to pass.


def test_game_audio_on_without_wav_is_still_rejected(tmp_path):
    source = tmp_path/'source.mp4'
    subprocess.run([FFMPEG, '-y', '-hide_banner', '-loglevel', 'error',
                    '-f', 'lavfi', '-i', 'color=c=blue:s=320x180:r=60:d=0.2',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(source)],
                   check=True, timeout=30)
    with pytest.raises(RuntimeError, match='LoLゲーム音WAV'):
        apply_effects(source, tmp_path/'output.mp4', neutral(game_audio=True), .2, [])


def test_missing_lol_never_allocates_capture_session():
    legacy.t07_no_desktop_fallback.__wrapped__()


def test_broken_fps_camera_remains_top_during_capture():
    legacy.t12_fps_camera_falls_back_to_top_instead_of_underground.__wrapped__()
