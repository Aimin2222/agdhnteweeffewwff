"""RED-only adjustments must retain manual heading, calibration and other cameras."""
from types import SimpleNamespace
from dataclasses import fields
import pytest
from core import jobs
from core.camera import CameraPlan, RigInfo
from core.effects import Template
from core.players import Player


@pytest.mark.parametrize('team,choice,style,yaw',[
    ('CHAOS','auto','third',184.),('ORDER','auto','third',-12.),
    ('CHAOS','red','third',180.),('CHAOS','blue','third',0.),
    ('ORDER','red','third',180.),('CHAOS','auto','third_cinema',192.),
    ('CHAOS','auto','lolnam_cinema',192.),('ORDER','auto','third_cinema',-12.),
    ('CHAOS','auto','fps',0.),
])
def test_setup_adjusts_only_automatic_red_normal_camera(monkeypatch,team,choice,style,yaw):
    api=SimpleNamespace(set_playback=lambda **k:None,seek=lambda t:t)
    player=Player(5,'A','A#JP1','A','Ahri',team,selection_name='Ahri')
    rig=RigInfo(mode='fps',third=style!='fps',v=(240.,1200.,-400.))
    monkeypatch.setattr(jobs,'attach_to_player',lambda *a,**k:rig)
    monkeypatch.setattr(jobs.time,'sleep',lambda *a:None)
    plan,actual=jobs._setup_clip(api,player,Template(style=style,camera_side=choice),1.,
        [SimpleNamespace(time=4.)],lambda msg:None)
    assert actual is rig and plan.side_yaw==yaw and plan.team==team
    assert plan.sel_name=='Ahri' and plan.kill_times==(4.,)


@pytest.mark.parametrize('style',['fps','third_cinema','lolnam_cinema','cinema'])
def test_red_fps_scale_is_scoped_and_blue_math_unchanged(style):
    rig=RigInfo(mode='fps',third=False,v=(240.,1200.,-400.))
    blue=CameraPlan(style=style,rig=rig,dist_scale=.8,height=40,team='ORDER')
    red=CameraPlan(style=style,rig=rig,dist_scale=.8,height=40,team='CHAOS')
    a,b=blue.offset_at(0),red.offset_at(0)
    if style=='fps':
        assert a==(192.,1000.,-320.)
        assert b==pytest.approx((192*.76,960*.76+40,-320*.76))
    else:assert a==b


def test_camera_plan_keeps_positional_contract_with_team_appended():
    assert fields(CameraPlan)[-1].name=='team'
    assert CameraPlan().team=='ORDER'
