"""Material portraits and GPU/CPU row spacing must reflect the same editor settings."""
from pathlib import Path
import pytest
from PIL import Image

from core.effects import Template, FFMPEG
from core.gpu_full import GPUFullStage
from core.kill_icons import ASSET_STYLES, make_badge, normalize_stack_gap, with_badges


@pytest.mark.parametrize('style', list(ASSET_STYLES))
def test_material_contains_each_real_portrait_and_is_bounded(tmp_path, style):
    a, b = tmp_path/'killer.png', tmp_path/'victim.png'
    Image.new('RGB', (100, 100), (221, 13, 27)).save(a)
    Image.new('RGB', (100, 100), (17, 36, 225)).save(b)
    out = make_badge(tmp_path/'pair.png', style, killer_icon=a, victim_icon=b, glow_enabled=False)
    with Image.open(out) as im:
        assert im.size == (385, 116) and im.mode == 'RGBA'
        # Centers of the two actual portrait windows, mapped from source art.
        for point, expected in [((104, 61), (221, 13, 27)), ((280, 61), (17, 36, 225))]:
            assert max(abs(x-y) for x,y in zip(im.getpixel(point)[:3], expected)) <= 4


@pytest.mark.parametrize('scale,gap', [(1,0),(.8,12),(1.5,36)])
def test_gpu_row_spacing_matches_cpu_expression(tmp_path, scale, gap):
    path=tmp_path/'badge.png';Image.new('RGBA',(385,116),'red').save(path)
    badges=[(path,.2),(path,.3)]
    tpl=Template(kill_icon_style='premium_gold',kill_icon_scale=scale,kill_stack_gap=gap,
                 vignette=0,bloom=0,grain=0,transition='cut')
    cpu=with_badges('[0:v]null[vout]',1,badges,duration=1,scale=scale,stack_gap=gap)
    step=round(116*scale+gap)
    assert f"y='62+{step}'" in cpu
    stage=GPUFullStage(tpl,1,[],ffmpeg=FFMPEG,badge_index=1,badges=badges,lut_index=3)
    try:
        assert f'62.0f+{step}' in stage.path.read_text()
    finally:stage.close()


@pytest.mark.parametrize('value,expected', [('bad',4), (float('nan'),4), (float('inf'),4),(-10,0),(99,36)])
def test_invalid_project_gaps_are_bounded(value, expected):
    assert normalize_stack_gap(value) == expected


def test_material_glow_uses_same_validation_as_vector_style(tmp_path):
    out=make_badge(tmp_path/'safe.png','premium_gold',glow_strength='bad',glow_color='bad')
    assert out.is_file()
