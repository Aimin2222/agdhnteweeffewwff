"""GPU-owned CPU circular focus and preset pipeline tests."""
import subprocess
import numpy as np
import pytest
from core.effects import Template, build_graph, one_click_templates, FFMPEG, GRADE_JP
from core.focus_fx import focus_settings, mask_expression
from core.preview import grade_rgb

def _neutral(**kw):
    return Template(grade='standard', grade_strength=0, contrast=1, bloom=0,
                    vignette=0, grain=0, transition='cut', **kw)


def test_circle_is_default_and_settings_roundtrip():
    tpl = _neutral(dof_enabled=True,dof_blur=7,dof_center_x=.42,
                   dof_center_y=.57,dof_radius=.27,dof_feather=.11,
                   video_effects={'center_mosaic':.25,'flash':.3})
    assert tpl.dof_shape == 'circle'
    restored = Template(**tpl.to_dict())
    assert restored.dof_radius == .27
    assert 'center_mosaic' not in restored.video_effects
    assert restored.video_effects['flash'] == .3


def test_mask_is_round_at_16_by_9_and_has_soft_edge():
    mask=mask_expression(.5,.54,.3,.15)
    assert 'W/H' in mask and 'sqrt' in mask and 'clip' in mask
    assert mask.startswith('255*')


def test_legacy_band_mode_still_exists():
    tpl=_neutral(dof_enabled=True,dof_blur=3,dof_shape='band')
    graph=build_graph(tpl,1,False)
    assert 'dofsrc' in graph
    assert 'cdofsrc' not in graph


def test_circle_filters_present_only_when_enabled():
    off=build_graph(_neutral(dof_enabled=False,dof_blur=4),1,False)
    on=build_graph(_neutral(dof_enabled=True,dof_blur=4),1,False)
    assert 'cdofalpha' not in off and 'cdofalpha' in on
    # Older v5.10.2 projects must not re-enable the retired mosaic effect.
    old=build_graph(_neutral(video_effects={'center_mosaic':.5}),1,False)
    assert 'cmosaalpha' not in old and 'pixelize' not in old


def test_circle_preview_favors_center_focus():
    # A high-frequency checkerboard: the center should retain more texture.
    y,x=np.mgrid[0:180,0:320]
    a=((x//2+y//2)%2*255).astype(np.uint8)
    source=np.repeat(a[:,:,None],3,axis=2)
    result=grade_rgb(source,_neutral(dof_enabled=True,dof_blur=12))
    center=result[90-8:90+8,160-8:160+8,0].astype(float).std()
    edge=result[10:26,10:26,0].astype(float).std()
    assert center>edge*3, (center,edge)


def test_retired_mosaic_setting_does_not_pixelate_preview():
    y,x=np.mgrid[0:180,0:320]
    source=np.stack([x.astype(np.uint8),y.astype(np.uint8),np.full_like(x,120,dtype=np.uint8)],axis=2)
    result=grade_rgb(source,_neutral(video_effects={'center_mosaic':.85}))
    baseline=grade_rgb(source,_neutral())
    assert np.array_equal(result,baseline)


@pytest.mark.parametrize('blur', [5, 10])
def test_ffmpeg_real_circle_mask_render(blur,tmp_path):
    tpl=_neutral(dof_enabled=True,dof_blur=blur)
    dst=tmp_path/f'dof_{blur}.png'
    cmd=[FFMPEG,'-hide_banner','-loglevel','error','-y',
         '-f','lavfi','-i','testsrc2=size=1920x1080:rate=1',
         '-filter_complex',build_graph(tpl,1,False),'-map','[vout]',
         '-frames:v','1','-update','1',str(dst)]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=70)
    assert r.returncode==0,r.stderr[-1500:]
    assert dst.stat().st_size>2000


def test_new_templates_have_safe_cameras():
    ts=one_click_templates()
    for n in ('クリア・アクション（視認性重視）','アイスブルー・シネマ',
              'ゴールド・フィニッシュ','エピック・チームファイト'):
        assert n in ts
        assert ts[n].style in ('third_cinema','lolnam_cinema','cinema_top')
        assert ts[n].dof_shape == 'circle'
    assert 'iceblue' in GRADE_JP and 'golden' in GRADE_JP
