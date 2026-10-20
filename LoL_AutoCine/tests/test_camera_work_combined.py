"""Combined control/render contract, without pretending to capture real LoL."""
from types import SimpleNamespace
import pytest
from PIL import Image
from core import camera, jobs
from core.effects import Template
from core.players import Player
from core.work_kill_assets import make_event_work_badges, with_work_badges, layer_plan
from tests.test_smart_camera_director_v1 import API


@pytest.mark.parametrize('team', ['ORDER','CHAOS'])
@pytest.mark.parametrize('mode', ['fixed_auto','full_auto'])
def test_camera_preparation_preserves_work_event_and_export_contract(monkeypatch,tmp_path,team,mode):
    monkeypatch.setattr(camera.time,'sleep',lambda _:None)
    template=Template(style='third',camera_control_mode=mode,
        camera_auto_qa_approved={'BLUE':['third'],'RED':['third_cinema']},
        work_kill_frame_id='083/a_simple_main',work_kill_effect_id='A',work_kill_review=True,
        kill_icon_motion='slide_right',fps=60)
    before=template.to_dict()
    kills=[SimpleNamespace(time=23.,killer='A',victim='B')]
    player=Player(0,'Fixture','Fixture#JP','Fixture','Hero',team)
    plan,rig=jobs._setup_clip(API(),player,template,20.,kills,lambda _:None)
    assert template.to_dict()==before and plan.rotation_at(23)['z']==0
    assert rig.mode=='fps'
    icon=tmp_path/'portrait.png'
    Image.new('RGBA',(128,128),'blue').save(icon)
    entries=make_event_work_badges(tmp_path/'out.mp4',template,kills,[(3.,1.)],
        [dict(name='A',selection_name='Ashe'),dict(name='B',selection_name='Lux')],icon_lookup=lambda _:icon)
    graph=with_work_badges('[0:v]null[vout]',1,entries,duration=6,motion=template.kill_icon_motion)
    assert len(entries)==3 and graph.endswith('[vout]')
    layers=layer_plan(entries,6,template.kill_icon_duration)
    assert all(x['start']==3. and x['time']==3. for x in layers)
    assert all(x['end']<=3.+template.kill_icon_duration for x in layers)
    assert template.to_dict()==before
