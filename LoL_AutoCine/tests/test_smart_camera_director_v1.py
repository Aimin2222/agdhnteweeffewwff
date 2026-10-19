"""Numerical camera safety, not a claim of visually approved LoL footage."""
import copy
import json
import math
from types import SimpleNamespace

import pytest
from core import camera, jobs
from core.camera_tuning import target_center_rotation, yaw_alignment_error
from core.effects import Template
from core.players import Player
from core.smart_camera_director import decide_camera, SUPPORTED_STYLES

class API:
    def __init__(self, stale=False):
        self.values = {}
        self.calls = []
        self.stale = stale
        self.top_reads = 0
    def set_playback(self, **kwargs): pass
    def seek(self, t): return t
    def set_render(self, **kwargs):
        self.values.update(copy.deepcopy(kwargs))
        self.calls.append(copy.deepcopy(kwargs))
    def render(self):
        mode = self.values['cameraMode']
        offset = self.values.get('selectionOffset', {})
        point = (1000., 60., 12000.)
        if mode == 'top':
            self.top_reads += 1
            pos = (500., 1960., 10000.)
        else:
            pos = tuple(point[i] + offset.get(k, 0) for i, k in enumerate(('x','y','z')))
        if self.stale:
            pos = (18000., 2000., 0.) if mode == 'top' else point
        return {'cameraMode': mode, 'cameraAttached': True,
                'selectionName': 'PreviousActor' if self.stale else 'Fixture',
                'cameraPosition': dict(zip(('x','y','z'),pos)),
                'selectionOffset': copy.deepcopy(offset), 'fieldOfView': self.values.get('fieldOfView',60),
                # Deliberately poison repeated top reads with the old axis/roll.
                'cameraRotation': copy.deepcopy(self.values.get('cameraRotation', {'x': 0., 'y':56., 'z':0.}))
                if self.top_reads < 2 or mode != 'top' else {'x': 0., 'y':-56., 'z':180.}}


def setup(monkeypatch, team, style, mode, angle=0, api=None, **extra):
    monkeypatch.setattr(camera.time, 'sleep', lambda _s: None)
    tpl = Template(style=style, third_yaw=angle, **extra)
    tpl.camera_control_mode = mode
    player = Player(0,'Fixture','Fixture#JP','Fixture','Hero',team)
    logs=[]
    before = copy.deepcopy(tpl.to_dict())
    plan, rig = jobs._setup_clip(api or API(), player, tpl, 20, [SimpleNamespace(time=23)], logs.append)
    assert tpl.to_dict() == before
    return plan, rig, logs

@pytest.mark.parametrize('team', ['ORDER','CHAOS'])
@pytest.mark.parametrize('style', SUPPORTED_STYLES)
@pytest.mark.parametrize('mode', ['fixed_auto','full_auto'])
@pytest.mark.parametrize('angle', [0,90,180])
def test_all_modes_reselected_twice_face_actual_target_without_roll(monkeypatch,team,style,mode,angle):
    api=API()
    poses=[]
    for repeat in range(2):
        plan,rig,logs=setup(monkeypatch,team,style,mode,angle,api)
        assert plan.style == style
        assert plan._camera_decision['fallback'] is (mode=='full_auto')
        samples=[]
        for t in [20,22.5,23,24,26]:
            offset=plan.offset_at(t)
            assert all(math.isfinite(v) for v in offset)
            assert 32 <= plan.fov_at(t) <= 100
            if rig.mode=='fps':
                rotation=plan.rotation_at(t)
                assert rotation == pytest.approx(target_center_rotation(offset))
                assert rotation['z']==0
                assert yaw_alignment_error(offset, rotation) < 1e-7
                assert rotation['y']==pytest.approx(math.degrees(math.atan2(offset[1],math.hypot(offset[0],offset[2]))))
                samples.append((offset,rotation))
        poses.append(samples)
    assert poses[0]==poses[1]  # poisoned return roll/sign cannot accumulate


def test_fixed_explicit_90_180_orbit_is_not_clipped_as_auto_motion(monkeypatch):
    plans=[setup(monkeypatch,'ORDER','third','fixed_auto',a)[0] for a in [0,90,180]]
    offsets=[p.offset_at(20) for p in plans]
    a,b,c=offsets
    assert a[0]==pytest.approx(b[2]) and a[2]==pytest.approx(-b[0])
    assert a[0]==pytest.approx(-c[0]) and a[2]==pytest.approx(-c[2])


def test_decisions_are_side_specific_reproducible_and_wide_for_multi():
    ledger={'BLUE':['third_cinema','cinema_top'], 'RED':['third']}
    for _ in range(3):
        assert decide_camera('full_auto','ORDER','fps',[23],approved=ledger).style=='third_cinema'
        assert decide_camera('full_auto','ORDER','fps',[24,23],approved=ledger).style=='cinema_top'
        assert decide_camera('full_auto','CHAOS','fps',[23],approved=ledger).style=='third'
    assert decide_camera('full_auto','ORDER','fps',[23],approved=ledger,excluded=['BLUE:third_cinema']).style=='cinema_top'
    assert decide_camera('full_auto','CHAOS','fps',[23],approved=ledger,excluded=['BLUE:third']).style=='third'
    fallback=decide_camera('full_auto','RED','third',[23],approved={'BLUE':['third']},excluded=['RED:third'])
    assert fallback.style=='top' and fallback.fallback
    assert 'no_verified_candidate_for_side' in fallback.reasons
    assert decide_camera('full_auto','RED','third',[23],approved={}).fallback


def test_runtime_selection_does_not_mutate_template_or_switch_within_clip(monkeypatch):
    monkeypatch.setattr(camera.time,'sleep',lambda _s:None)
    tpl=Template(style='fps')
    tpl.camera_control_mode='full_auto'
    tpl.camera_auto_qa_approved={'BLUE':['third_cinema','cinema_top']}
    tpl.camera_auto_excluded=[]
    before=copy.deepcopy(tpl.__dict__)
    logs=[]
    plan,_=jobs._setup_clip(API(),Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER'),tpl,20,
                            [SimpleNamespace(time=23),SimpleNamespace(time=24)],logs.append)
    assert plan.style=='cinema_top' and tpl.__dict__==before
    for t in [20,23,24,27]:
        plan.offset_at(t); assert plan.style=='cinema_top'
        assert plan.fov_at(t)>=60
    decision=json.loads(next(s for s in logs if s.startswith('SMART_CAMERA_DECISION ')).split(' ',1)[1])
    assert decision['reasons'][1]=='multi_kill_wide_priority'


def test_stale_baseline_falls_back_top_and_records_reason(monkeypatch):
    plan,rig,logs=setup(monkeypatch,'CHAOS','fps','fixed_auto',api=API(stale=True))
    assert rig.mode=='top' and rig.fell_back and not plan._live_engine_target_lock
    assert any(s.startswith('SMART_CAMERA_FALLBACK ') for s in logs)


def test_invalid_offset_uses_finite_relative_fallback_once(monkeypatch):
    plan,_,logs=setup(monkeypatch,'ORDER','third','fixed_auto')
    plan.rig.h=(float('nan'),0)
    for _ in range(2):
        offset=plan.offset_at(23)
        assert offset==(0,650,-1050)
        assert plan.rotation_at(23)['z']==0
    assert len([s for s in logs if 'invalid_pose_safe_relative_offset' in s])==1


def test_explicit_manual_disables_new_automation_without_erasing_settings(monkeypatch):
    plan,_,_=setup(monkeypatch,'CHAOS','third','manual',smart_composition=True,auto_director_strength=1.4)
    assert not plan.smart_composition and plan._director_gain()==0
    legacy,_,_=setup(monkeypatch,'CHAOS','third',None,smart_composition=True,auto_director_strength=1.4)
    assert legacy.smart_composition and legacy._director_gain()==1.4


def test_template_round_trip_preserves_modes_and_side_qa_without_legacy_conversion(tmp_path):
    # Added optional fields must survive the actual project serialization.
    tpl=Template(**{'style':'third','camera_control_mode':'fixed_auto',
                            'camera_auto_excluded':['RED:orbit'],
                            'camera_auto_qa_approved':{'BLUE':['third']}})
    from core.reference_safe import load_template
    saved=tmp_path/"template.json"
    saved.write_text(json.dumps(tpl.to_dict()),encoding="utf-8")
    restored=load_template(saved)
    assert restored.camera_control_mode=='fixed_auto'
    assert restored.camera_auto_excluded==['RED:orbit']
    assert restored.camera_auto_qa_approved=={'BLUE':['third']}
    assert Template(**{'style':'third','smart_composition':True}).camera_control_mode is None


@pytest.mark.parametrize('team', ['ORDER', 'CHAOS'])
@pytest.mark.parametrize('style', ['third', 'third_cinema', 'fps', 'lolnam_cinema', 'geo_aim', 'orbit'])
def test_director_slow_api_aims_from_sent_pose_for_new_modes(monkeypatch,team,style):
    import time
    # Do not patch sleep: exercise the actual clock, smoothing and limiter.
    rig=camera.RigInfo(mode='fps',third=style in camera.THIRD_STYLES,
                       h=(0,-1), v=(0,1900,-2200), rot={'x':0,'y':45,'z':180}, pitch_axis='x')
    plan=camera.CameraPlan(style=style, team=team, third_yaw=180, kill_time=23, kill_times=(23,24),
                           rig=rig, third_dist=1060, third_elev=37)
    plan.camera_control_mode='full_auto'
    class SlowAPI:
        def __init__(self): self.calls=[]
        def playback(self): return {'time':23}
        def set_playback(self,**kw): pass
        def set_render(self,**kw):
            self.calls.append(copy.deepcopy(kw)); time.sleep(.05)
    api=SlowAPI();director=camera.CameraDirector(api,plan)
    director.start()
    try: time.sleep(.24)
    finally: director.stop()
    assert len(api.calls)>=2 and director.api_slow_calls>=1
    for body in api.calls:
        offset=tuple(body['selectionOffset'][k] for k in ('x','y','z'))
        assert yaw_alignment_error(offset,body['cameraRotation'])<1e-7
        assert body['cameraRotation']['z']==0


def test_nonfinite_api_position_never_passes_attachment(monkeypatch):
    monkeypatch.setattr(camera.time,'sleep',lambda _s:None)
    api=API();render=api.render
    def invalid_validation():
        state=render()
        if any(state.get('selectionOffset',{}).values()):
            state['cameraPosition']['x']=float('nan')
        return state
    api.render=invalid_validation
    player=Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER')
    rig=camera.attach_to_player(api,player,'third',safe_axes=True)
    assert rig.mode=='top' and rig.fell_back


def test_malformed_metadata_does_not_create_qa_pass_or_enable_auto():
    assert decide_camera({},'RED','third').mode=='manual'
    d=decide_camera('full_auto','RED','third',[float('nan'),'bad',23],
                    approved={'RED':['unknown',{}]},excluded=[{}])
    assert d.fallback and d.kill_times==(23,)



def test_new_preview_ack_failure_restores_mirror_before_playback(monkeypatch):
    from core.replay_api import ReplayApiError
    plan,rig,_=setup(monkeypatch,'ORDER','third','fixed_auto')
    restored=[]
    api=API();api.render=lambda: {'cameraMode':'top'}
    monkeypatch.setattr(jobs,'_setup_clip',lambda *a:(plan,rig))
    monkeypatch.setattr(jobs,'restore_mirror_camera',lambda *a:restored.append(True))
    monkeypatch.setattr(jobs,'CameraDirector',lambda *a:pytest.fail('No playback before final pose acknowledgement'))
    with pytest.raises(ReplayApiError):
        jobs.preview_clip(api,object(),Template(),20,26,[SimpleNamespace(time=23)])
    assert restored==[True]
