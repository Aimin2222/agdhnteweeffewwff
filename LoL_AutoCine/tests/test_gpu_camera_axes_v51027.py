"""Measured Euler contract, protected golden shots and ten independent modes."""
import copy
import json
import math
from pathlib import Path
from threading import Event
from types import SimpleNamespace
import time

import pytest
from core import camera, camera_tuning, jobs
from core.effects import Template
from core.players import Player
from core.replay_api import ReplayApiError

MODES = ('third', 'third_cinema', 'fps', 'lolnam_cinema', 'geo_aim')


def setup(monkeypatch, team, mode, *, h=(-.3, -.9539392014), axis='y', roll=0., tpl=None):
    monkeypatch.setattr(jobs.time, 'sleep', lambda _s: None)
    monkeypatch.setattr(jobs, 'attach_to_player', lambda *a, **kw:
        camera.RigInfo(mode='fps', third=mode!='fps', h=h, v=(h[0]*2300,1900,h[1]*2300),
                       P=(0,60,0), rot={'x':0.,'y':56.,'z':roll}, pitch_axis=axis, pitch_sign=1.))
    api=SimpleNamespace(set_playback=lambda **kw:None, seek=lambda t:t)
    return jobs._setup_clip(api, Player(0,'Fixture','Fixture#JP','Fixture','Hero',team),
                            tpl or Template(style=mode),20,[SimpleNamespace(time=23)],lambda _m:None)[0]


@pytest.mark.parametrize('team,mode', [('ORDER', m) for m in MODES] + [('CHAOS','third_cinema'),('CHAOS','lolnam_cinema')])
@pytest.mark.parametrize('axis,roll', [('x',-192.),('y',0.)])
def test_repaired_modes_aim_at_target_with_zero_roll_even_with_poisoned_axis(monkeypatch,team,mode,axis,roll):
    plan=setup(monkeypatch,team,mode,axis=axis,roll=roll)
    assert plan._live_engine_target_lock and plan._live_angle_bias == {}
    for t in (20,22,23,24,26):
        rotation=plan.rotation_at(t);expected=camera_tuning.target_center_rotation(plan.offset_at(t))
        assert rotation == pytest.approx(expected)
        assert rotation['z']==0 and 14<=rotation['y']<=72
        assert camera_tuning.yaw_alignment_error(plan.offset_at(t),rotation)<1e-7


@pytest.mark.parametrize('case',json.loads((Path(__file__).with_name('red35_v51026_golden.json')).read_text(encoding='utf-8'))['cases'])
def test_good_red3_red5_match_frozen_previous_live_setup(monkeypatch,case):
    h=(math.cos(math.radians(case['angle'])),math.sin(math.radians(case['angle'])))
    tpl=Template(style=case['style'],cam_height=case['height'],auto_director_strength=case['strength'],
                 smart_composition=case['smart_composition'],scene_keyframes=case['keyframes'])
    plan=setup(monkeypatch,'CHAOS',case['style'],h=h,tpl=tpl)
    assert not plan._live_engine_target_lock and not plan._prepare_pose_before_capture
    for sample in case['samples']:
        t=sample['time']
        assert plan.offset_at(t)==tuple(sample['offset'])
        assert plan.rotation_at(t)==sample['rotation']
        assert plan.fov_at(t)==sample['fov'] and plan.speed_at(t)==sample['speed']


@pytest.mark.parametrize('side,team',[('BLUE','ORDER'),('RED','CHAOS')])
@pytest.mark.parametrize('changed', MODES)
def test_changing_one_mode_cannot_change_other_nine_or_template(monkeypatch,side,team,changed):
    def snapshots():
        result={}
        for current_team in ('ORDER','CHAOS'):
            for mode in MODES:
                tpl=Template(style=mode);before=tpl.to_dict()
                p=setup(monkeypatch,current_team,mode,tpl=tpl)
                assert tpl.to_dict()==before
                result[(current_team,mode)]=[(p.offset_at(t),p.rotation_at(t),p.fov_at(t)) for t in (20,23,26)]
        return result
    before=snapshots()
    value=copy.deepcopy(camera_tuning.SHOT_TUNING[(side,changed)]);value['distance']+=.02
    monkeypatch.setitem(camera_tuning.SHOT_TUNING,(side,changed),value)
    after=snapshots()
    for key in before:
        assert (before[key]!=after[key]) == (key==(team,changed)),key


def test_profiles_and_return_values_are_not_shared(monkeypatch):
    baseline={m:camera.live_side_profile('ORDER',style=m) for m in MODES}
    monkeypatch.setitem(camera.LIVE_MODE_PROFILES,('ORDER','third'),(-7.,40.,1180.))
    assert camera.live_side_profile('ORDER',style='third')!=baseline['third']
    for m in MODES[1:]:assert camera.live_side_profile('ORDER',style=m)==baseline[m]
    a=camera.live_side_profile('ORDER',style='fps');a['distance']=99999
    assert camera.live_side_profile('ORDER',style='fps')==baseline['fps']


def test_later_ui_keyframe_edits_cannot_mutate_a_running_plan(monkeypatch):
    marks=[{'time':-1.,'yaw':6.,'zoom':4.,'fov':2.},{'time':1.,'yaw':14.,'zoom':-3.,'fov':8.}]
    tpl=Template(style='third_cinema',scene_keyframes=marks)
    plan=setup(monkeypatch,'ORDER','third_cinema',tpl=tpl)
    before=(plan.offset_at(23),plan.rotation_at(23),plan.fov_at(23))
    tpl.scene_keyframes[0]['yaw']=179
    tpl.scene_keyframes[1]['zoom']=100
    assert (plan.offset_at(23),plan.rotation_at(23),plan.fov_at(23))==before


class RenderAPI:
    def __init__(self, *, stale=False, forever=False):
        self.values={};self.top_reads=0;self.stale=stale;self.forever=forever;self.calls=[]
    def set_render(self,**kw):self.values.update(copy.deepcopy(kw));self.calls.append(copy.deepcopy(kw))
    def render(self):
        mode=self.values['cameraMode'];offset=self.values.get('selectionOffset',{})
        point=(1000.,60.,12000.)
        if mode=='top':
            self.top_reads+=1
            stale=self.forever or self.stale and self.top_reads==1
            pos=(14000.,1960.,2000.) if stale else (500.,1960.,10000.)
            name='PreviousActor' if stale else 'Fixture'
        else:
            pos=tuple(point[i]+float(offset.get(k,0)) for i,k in enumerate(('x','y','z')));name='Fixture'
        return {'cameraMode':mode,'cameraAttached':True,'selectionName':name,
                'selectionOffset':copy.deepcopy(offset),'cameraPosition':dict(zip(('x','y','z'),pos)),
                'cameraRotation':copy.deepcopy(self.values.get('cameraRotation',{'x':0.,'y':56.,'z':0.})),
                'fieldOfView':self.values.get('fieldOfView',60.)}


def test_stale_previous_actor_is_reacquired_instead_of_guessed_or_cached(monkeypatch):
    monkeypatch.setattr(camera.time,'sleep',lambda _s:None)
    monkeypatch.setattr(camera,'_TPS_CALIBRATION',{});monkeypatch.setattr(camera,'_TPS_STABLE_ROTATIONS',{})
    api=RenderAPI(stale=True);logs=[]
    rig=camera.attach_to_player(api,Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER'),
                                'third',settle=0,log=logs.append,third_elev=37)
    assert rig.third and rig.pitch_axis=='y' and rig.pitch_sign==1
    assert api.top_reads==2 and rig.h==pytest.approx((-.242535625,-.9701425))
    assert rig.rot['z']==0
    assert any('reacquired_top_baseline' in row for row in logs)


def test_unverifiable_baseline_falls_back_without_using_old_world_point(monkeypatch):
    monkeypatch.setattr(camera.time,'sleep',lambda _s:None)
    monkeypatch.setattr(camera,'_TPS_CALIBRATION',{('Hero','ORDER','third'):{'P':(1,2,3),'h':(1,0),'axis':'x','rot':{'z':180}}})
    api=RenderAPI(forever=True)
    rig=camera.attach_to_player(api,Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER'),'third',settle=0)
    assert rig.fell_back and rig.mode=='top' and api.top_reads==3
    assert api.values['cameraMode']=='top'


def test_detached_baseline_is_rejected_even_when_coordinates_look_plausible(monkeypatch):
    monkeypatch.setattr(camera.time,'sleep',lambda _s:None)
    api=RenderAPI();original=api.render
    def detached():
        state=original();state['cameraAttached']=False;return state
    api.render=detached
    rig=camera.attach_to_player(api,Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER'),'fps',settle=0)
    assert rig.fell_back and rig.mode=='top' and api.top_reads==3


def test_frame_arriving_during_initial_pose_confirmation_is_not_discarded(monkeypatch):
    # Paused LoL can emit only one frame for a camera POST. Taking the capture
    # baseline AFTER its acknowledgement would wait for a frame that never comes.
    from core.capture import WGCWindowSource
    import numpy as np
    plan=setup(monkeypatch,'ORDER','fps');source=WGCWindowSource()
    monkeypatch.setattr(jobs,'_prime_live_replay_once',lambda *a,**kw:None)
    monkeypatch.setattr(jobs,'_setup_clip',lambda *a:(plan,plan.rig))
    api=RenderAPI();post=api.set_render
    def set_pose(**kw):
        post(**kw);source._push(np.zeros((8,8,4),dtype=np.uint8))
    api.set_render=set_pose
    actual,rig=jobs._prepare_clip_capture(api,source,None,None,20,[],Event(),lambda _m:None)
    assert actual is plan and rig is plan.rig and source.frame_count==1


def test_initial_pose_ack_is_verified_before_capture_and_mismatch_aborts(monkeypatch):
    plan=setup(monkeypatch,'ORDER','fps');api=RenderAPI();logs=[]
    jobs._apply_initial_camera_pose(api,plan,20,Event(),logs.append)
    assert api.values['cameraRotation']==plan.rotation_at(20)
    assert json.loads(logs[-1].split(' ',1)[1])['verified']
    wrong=RenderAPI();wrong.render=lambda:{'cameraMode':'top'}
    with pytest.raises(ReplayApiError,match='反映されません'):
        jobs._apply_initial_camera_pose(wrong,plan,20,Event(),lambda _m:None)
    assert len(wrong.calls)==2  # bounded retries, no recorder is started


def test_good_modes_initial_path_is_not_touched(monkeypatch):
    for mode in ('fps','geo_aim'):
        p=setup(monkeypatch,'CHAOS',mode)
        api=SimpleNamespace(set_render=lambda **kw:pytest.fail('Protected mode must not gain a new POST'))
        jobs._apply_initial_camera_pose(api,p,20,Event(),lambda _m:None)


def test_unacknowledged_camera_never_starts_video_or_audio(monkeypatch,tmp_path):
    plan=setup(monkeypatch,'ORDER','fps')
    monkeypatch.setattr(jobs,'_setup_clip',lambda *a:(plan,plan.rig))
    monkeypatch.setattr(jobs,'ClipRecorder',lambda *a,**kw:pytest.fail('No video before camera verification'))
    api=RenderAPI();api.render=lambda:{'cameraMode':'top'}
    source=SimpleNamespace(frame_count=0)
    player=Player(0,'Fixture','Fixture#JP','Fixture','Hero','ORDER')
    with pytest.raises(ReplayApiError,match='反映されません'):
        jobs.record_one_clip(api,source,player,Template(style='fps'),20,26,[SimpleNamespace(time=23)],
                             tmp_path/'raw.mp4',audio_factory=lambda _p:pytest.fail('No audio before camera verification'))


def test_red1_pullback_is_small_and_only_auto(monkeypatch):
    p=setup(monkeypatch,'CHAOS','third')
    assert p._live_dist_factor==pytest.approx(1.13*1.08)
    manual=setup(monkeypatch,'CHAOS','third',tpl=Template(style='third',camera_side='blue'))
    assert manual._live_dist_factor==1.13
    assert p._live_angle_bias=={} and not manual._prepare_pose_before_capture


def test_director_target_lock_uses_final_smoothed_limited_sent_offset():
    # Real director thread with deliberately slow API; every POST must still
    # point at its own camera position, including manual yaw and wraparound.
    p=camera.CameraPlan(style='third_cinema',team='ORDER',kill_time=23,third_elev=37,
                       third_dist=1060,side_yaw=175,third_yaw=12,
                       rig=camera.RigInfo(mode='fps',third=True,h=(0,-1),v=(0,1900,-2200)))
    p._live_engine_target_lock=True
    class API:
        def __init__(self):self.calls=[]
        def playback(self):return {'time':23}
        def set_playback(self,**kw):pass
        def set_render(self,**kw):self.calls.append(copy.deepcopy(kw));time.sleep(.05)
    api=API();director=camera.CameraDirector(api,p)
    director.start()
    try:time.sleep(.35)
    finally:director.stop()
    assert len(api.calls)>=2 and director.api_slow_calls>=1
    for row in api.calls:
        pos=tuple(row['selectionOffset'][k] for k in ('x','y','z'))
        assert camera_tuning.yaw_alignment_error(pos,row['cameraRotation'])<1e-7
        assert row['cameraRotation']['y']==pytest.approx(camera_tuning.target_center_rotation(pos)['y'])
        assert row['cameraRotation']['z']==0
