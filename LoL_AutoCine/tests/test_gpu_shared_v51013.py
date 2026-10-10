"""Regression at shared camera/scanner and hi-res compositor boundaries."""
import math
from types import SimpleNamespace
import pytest
from PIL import Image
from core.camera import CameraPlan, RigInfo, live_side_profile
from core.scanner import filter_scanned_events
from core.kill_icons import make_event_badges, with_badges
from core.effects import Template, FFMPEG
from core.gpu_full import GPUFullStage
from core.players import Player

@pytest.mark.parametrize('style', ['third', 'third_cinema', 'lolnam_cinema'])
@pytest.mark.parametrize('side', [180.0, 192.0])
def test_smart_pose_and_look_keep_red_heading(style, side):
    rig=RigInfo(mode='fps',third=True,h=(0.,-1.),pitch_axis='x',pitch_sign=1,
                rot={'x':32.,'y':0.,'z':0.})
    plan=CameraPlan(style=style,rig=rig,side_yaw=side,third_yaw=80,
                    smart_composition=True,motion_arc=150)
    offset, elevation=plan.third_pose_at(0)
    rotation=plan.rotation_at(0)
    angle=math.degrees(math.atan2(offset[0],-offset[2]))
    assert abs((angle+rotation['z']+180)%360-180)<1e-7
    assert abs(rotation['z']+side)<=55
    assert offset[1]>=300 and rotation['x']==pytest.approx(elevation)


def test_red_profile_is_explicit_and_manual_choice_still_available():
    assert live_side_profile('CHAOS')['yaw']==192
    assert live_side_profile('CHAOS','red')['yaw']==180
    assert live_side_profile('CHAOS','blue')['yaw']==0
    assert live_side_profile('ORDER')['yaw']==-12


def test_assists_and_other_killers_do_not_form_false_multikills():
    player=Player(0,'A','A#JP1','A','Lee Sin','ORDER')
    events=[dict(event_id=1,time=10.,killer='B',victim='X',assisters=['A']),
            dict(event_id=2,time=11.,killer='C',victim='Y',assisters=['A']),
            dict(event_id=3,time=12.,killer='A',victim='Z',assisters=[]),
            dict(event_id=4,time=13.,killer='A',victim='W',assisters=[])]
    filtered=filter_scanned_events(events,player,'both')
    assert [k.multikill for k in filtered[:2]]==[1,1]
    assert filtered[-1].multikill==2
    assert [k.multikill for k in filter_scanned_events(events,None,'both')][-1]==2


def test_export_material_resolution_and_compositors_match(tmp_path):
    a=Player(0,'A','A#JP1','A','Lee Sin','ORDER',selection_name='LeeSin')
    b=Player(5,'B','B#JP1','B','Ahri','CHAOS',selection_name='Ahri')
    icon=tmp_path/'icon.png';Image.new('RGB',(100,100),'red').save(icon)
    badges=make_event_badges(tmp_path/'out.mp4','user_frame_01',
        [SimpleNamespace(killer='A',victim='B')],[(.2,)], [a,b],icon_lookup=lambda p:icon)
    assert len(badges)==1
    with Image.open(badges[0][0]) as im:assert im.size==(770,232)
    graph=with_badges('[0:v]null[vout]',1,badges,duration=1,style='user_frame_01')
    assert "iw*0.500" in graph and "ih*0.500" in graph
    stage=GPUFullStage(Template(kill_icon_style='user_frame_01',vignette=0,bloom=0,grain=0),1,[],
                      ffmpeg=FFMPEG,badge_index=1,badges=badges,lut_index=2)
    try:
        assert 'get_image_width(aux)*0.500000000f' in stage.path.read_text()
        assert 'get_image_height(aux)*0.500000000f' in stage.path.read_text()
    finally:stage.close()
