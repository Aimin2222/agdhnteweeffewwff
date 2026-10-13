"""Compare actual setup with prior BLUE6 tilt while retaining every other pose value."""
import math
from types import SimpleNamespace
import pytest
from core import camera, camera_tuning, jobs
from core.effects import Template
from core.players import Player


@pytest.mark.parametrize('team',['ORDER','BLUE'])
@pytest.mark.parametrize('side',['auto','blue','red'])
def test_live_blue6_retires_wrong_axis_bias_without_changing_position(monkeypatch,team,side):
    monkeypatch.setattr(jobs.time,'sleep',lambda _:None)
    monkeypatch.setattr(jobs,'attach_to_player',lambda *a,**kw:
        camera.RigInfo(mode='fps',third=True,h=(-.52,-.854166),
            v=(-7173.99,1860.48,4104.7),rot={'x':0.,'y':37.,'z':0.},
            pitch_axis='x',pitch_sign=1.))
    api=SimpleNamespace(set_playback=lambda **kw:None,seek=lambda t:t)
    player=Player(0,'Hero','Hero#JP','Hero','Hero',team)
    template=Template(style='third',camera_side=side,cam_height=170,
        smart_composition=True,auto_director_strength=.5,
        scene_keyframes=({'time':-1.,'yaw':6.,'zoom':5.,'fov':8.},))
    current,_=jobs._setup_clip(api,player,template,10,[SimpleNamespace(time=11)],lambda _:None)
    prior=dict(camera_tuning.SHOT_TUNING[('BLUE','third')],angles={'x':3.0})
    monkeypatch.setitem(camera_tuning.SHOT_TUNING,('BLUE','third'),prior)
    previous,_=jobs._setup_clip(api,player,template,10,[SimpleNamespace(time=11)],lambda _:None)
    # Latest Windows QA rejects the historical X-as-pitch compensation.
    # Preserve distance/FOV/controls but ignore both obsolete bias values.
    assert current._live_angle_bias==previous._live_angle_bias=={}
    assert current._live_dist_factor==previous._live_dist_factor==1.10
    assert not current._live_red_target_center
    for t in (10,11,12):
        assert current.offset_at(t)==previous.offset_at(t)
        assert current.fov_at(t)==previous.fov_at(t)
        rot,old=current.rotation_at(t),previous.rotation_at(t)
        assert all(math.isfinite(v) for v in rot.values())
        assert rot==old==pytest.approx(camera_tuning.target_center_rotation(current.offset_at(t)))
        assert rot['y']==old['y'] and rot['z']==old['z']==0
    assert template.video_effects==Template().video_effects
    assert template.grade==Template().grade
