"""v5.10.5 kill-feed, side-aware camera and accessible effect help regressions."""
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from core.camera import CameraPlan, RigInfo, side_yaw_for, CAMERA_SIDE_CHOICES
from core.effects import Template
from core.kill_icons import make_badge, with_badges


def _img(path, fill):
    Image.new('RGB', (72,72),fill).save(path)
    return path


@pytest.mark.parametrize('team,choice,expected', [
    ('ORDER','auto',0), ('BLUE','auto',0), ('CHAOS','auto',180),
    ('RED','auto',180), ('ORDER','red',180), ('CHAOS','blue',0),
    ('CHAOS','bad',180),
])
def test_side_choices(team,choice,expected):
    assert side_yaw_for(team,choice)==expected


def test_red_camera_orbits_opposite_blue_without_losing_target_lock():
    rig=RigInfo(mode='fps', third=True, h=(0.,-1.),rot={'x':-28.,'y':15.,'z':0.},pitch_axis='x',pitch_sign=-1.)
    blue=CameraPlan(style='third',rig=rig,third_elev=28,third_dist=950,side_yaw=0)
    red=CameraPlan(style='third',rig=rig,third_elev=28,third_dist=950,side_yaw=180)
    o_blue,_=blue.third_pose_at(0)
    o_red,_=red.third_pose_at(0)
    assert o_blue[0]==pytest.approx(-o_red[0],abs=1e-8)
    assert o_blue[2]==pytest.approx(-o_red[2],abs=1e-8)
    assert o_blue[1]==pytest.approx(o_red[1])  # same clearance
    assert red.rotation_at(0) is not None
    assert 'selectionName' not in red.__dict__ # TargetLock rig unchanged
    assert rig.h==(0.,-1.)


def test_template_camera_side_append_compatibility():
    t=Template(camera_side='red',kill_icon_style='cinema')
    data=t.to_dict()
    assert data['camera_side']=='red'
    old=Template()
    assert old.camera_side=='auto'
    assert [f.name for f in fields(Template)][-3:] == ['camera_side', 'kill_sparkle_intensity', 'kill_stack_gap']


def test_actual_glow_works_and_portraits_are_unchanged(tmp_path):
    a=_img(tmp_path/'a.png', (201,30,35))
    b=_img(tmp_path/'b.png', (8,130,210))
    off=make_badge(tmp_path/'off.png','cinema',killer_icon=a,victim_icon=b,glow_enabled=False)
    neon=make_badge(tmp_path/'on.png','cinema',killer_icon=a,victim_icon=b,
                    glow_enabled=True,glow_strength=1.0,glow_color='#FDE078')
    with Image.open(off) as im0, Image.open(neon) as im1:
        assert im0.getpixel((77,55))==im1.getpixel((77,55))
        a0=sum(im0.getchannel('A').get_flattened_data())
        a1=sum(im1.getchannel('A').get_flattened_data())
        assert a1>a0+150000
        assert im1.getpixel((120,50))[3]>im0.getpixel((120,50))[3]


def test_neon_and_gold_output_different_colors(tmp_path):
    a=_img(tmp_path/'a.png',(200,0,0))
    b=_img(tmp_path/'b.png',(0,0,200))
    images=[]
    for style in ('neon','cinema'):
        file=make_badge(tmp_path/f'{style}.png',style,killer_icon=a,victim_icon=b,glow_strength=1.0)
        with Image.open(file) as im: images.append(im.convert('RGBA').copy())
    assert images[0].getpixel((36,18))!=images[1].getpixel((36,18))


def test_kill_feed_stacks_simultaneous_kills_on_different_rows():
    g=with_badges('null[vout]',1,[(Path('a.png'),1.0),(Path('b.png'),1.25)],duration=3.,seconds=1.6,scale=1.)
    assert "y='62+0'" in g and "y='62+120'" in g
    assert "between(t,0.900,2.600)" in g
    assert "between(t,1.150,2.850)" in g
    assert "[2:v]" in g


def test_more_than_three_kills_does_not_stack_offscreen():
    g=with_badges('null[vout]',1,[(Path(f'{k}.png'),1+.1*k) for k in range(5)],duration=3.,seconds=1.5)
    assert "62+360" not in g
    assert "62+240" in g


def test_help_button_opens_visible_dialog(monkeypatch):
    import legacy_app
    class V:
        def set(self, t): self.text=t
    app=SimpleNamespace(root=None,effect_help_text=V())
    messages=[]
    monkeypatch.setattr(legacy_app.messagebox,'showinfo',lambda *a,**k:messages.append((a,k)))
    legacy_app.App._show_effect_help(app,'glitch')
    assert len(messages)==1 and '映像ノイズ' in messages[0][0][0]
    assert '色ずれ' in messages[0][0][1]


def test_two_gold_kill_pairs_really_stack_in_ffmpeg(tmp_path):
    import shutil, subprocess
    ff=shutil.which('ffmpeg')
    if not ff:
        pytest.skip('FFmpeg missing')
    a=_img(tmp_path/'a.png',(235,35,50));b=_img(tmp_path/'b.png',(40,90,240))
    c=_img(tmp_path/'c.png',(15,200,100))
    one=make_badge(tmp_path/'one.png','cinema',killer_icon=a,victim_icon=b)
    two=make_badge(tmp_path/'two.png','cinema',killer_icon=a,victim_icon=c)
    graph=with_badges('[0:v]format=yuv420p[vout]',1,[(one,.4),(two,.8)],
                      duration=2.0,seconds=1.3,style='cinema')
    dst=tmp_path/'stack.mp4'
    args=[ff,'-y','-hide_banner','-loglevel','error','-f','lavfi','-i',
          'color=c=black:s=640x360:r=30:d=2',
          '-loop','1','-t','2','-i',str(one),'-loop','1','-t','2','-i',str(two),
          '-filter_complex',graph,'-map','[vout]','-c:v','libx264','-r','30',
          '-pix_fmt','yuv420p',str(dst)]
    result=subprocess.run(args,capture_output=True,text=True,timeout=40)
    assert result.returncode==0,result.stderr[-1500:]
    assert dst.stat().st_size>1000
    # Lower row must not be black after second kill appears.
    frame=subprocess.run([ff,'-loglevel','error','-ss','1','-i',str(dst),
                          '-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],
                         capture_output=True,timeout=15)
    assert frame.returncode==0
    raw=frame.stdout
    # center of portraits at x=640-385-32+78=301, y=62+120+58=240
    pixel=(240*640+301)*3
    assert max(raw[pixel:pixel+3])>75
