# -*- coding: utf-8 -*-
"""v5.9.2 tests: UI, serialization, actual CameraPlan and effect Template coupling."""
from dataclasses import asdict
from math import hypot, isclose
from types import SimpleNamespace
import tkinter as tk
import pytest
from core.camera import CameraPlan, RigInfo, MIN_CAM_HEIGHT
from core.effects import Template
from core.scanner import Kill
from core.players import Player
from ui.scene_project import SceneProject, Shot, scene_key, apply_shot
from ui.scene_batch import build_scene_templates
from legacy_app import App

FRAMES = [
    {'time': -2, 'yaw': -30, 'zoom': -20, 'fov': 10},
    {'time': 0, 'yaw': 30, 'zoom': 25, 'fov': -8},
    {'time': 2, 'yaw': 0, 'zoom': 0, 'fov': 0},
]


def test_keyframes_camera_interpolation_and_target_framing():
    shot=Shot.validated({'keyframes': FRAMES})
    rig=RigInfo(mode='fps',third=True,h=(0,-1),rot={'x':0.0,'y':0.0,'z':0.0},pitch_axis='x',pitch_sign=-1)
    base=CameraPlan(style='lolnam_cinema',kill_time=100,kill_times=(100,),rig=rig,
                    third_dist=950,motion_arc=12,motion_dolly=3)
    plan=CameraPlan(style='lolnam_cinema',kill_time=100,kill_times=(100,),rig=rig,
                    third_dist=950,motion_arc=12,motion_dolly=3,scene_keyframes=tuple(shot.keyframes))
    assert plan.keyframe_values(98)==(-30,-20,10)
    assert plan.keyframe_values(100)==(30,25,-8)
    assert plan.keyframe_values(99)==(0,2.5,1)  # smooth midpoint
    assert plan.keyframe_values(102)==(0,0,0)
    assert plan.fov_at(100)==pytest.approx(base.fov_at(100)-8)
    assert plan.fov_at(98)==pytest.approx(base.fov_at(98)+10)
    assert plan.keyframe_values(100)==plan.keyframe_values(100)
    for i in range(81):
        t=97+i*.1
        pos,_=plan.third_pose_at(t)
        assert pos[1] >= MIN_CAM_HEIGHT-0.0001
        assert all(abs(x)<10000 for x in pos)
        assert plan.rotation_at(t) is not None
    # Do not silently change camera without keyframes.
    empty=CameraPlan(style='lolnam_cinema',kill_time=100,kill_times=(100,),rig=rig,
                     third_dist=950,motion_arc=12,motion_dolly=3,scene_keyframes=())
    assert empty.third_pose_at(100)==base.third_pose_at(100)
    assert empty.fov_at(100)==base.fov_at(100)


def test_color_effects_optional_and_isolated():
    template=Template(game_audio=True,temperature=-.1,bloom=.1,dof_enabled=True,dof_blur=4)
    template.video_effects['focus_blur']=.05
    base=Shot.validated({'keyframes': FRAMES, 'fx_override': False, 'temperature': .8})
    unchanged=apply_shot(template,base)
    assert unchanged.temperature==-.1
    assert unchanged.dof_blur==4
    assert unchanged.video_effects['focus_blur']==.05
    modified=apply_shot(template,Shot.validated({'fx_override':True,'temperature':.5,
                   'bloom':.75,'focus_blur':.42,'dof_blur':12,'keyframes':FRAMES}))
    assert modified.temperature==.5
    assert modified.bloom==.75
    assert modified.video_effects['focus_blur']==.42
    assert modified.dof_enabled and modified.dof_blur==12
    assert modified.game_audio and template.game_audio
    assert template.temperature==-.1 and template.bloom==.1 and template.dof_blur==4
    assert len(modified.scene_keyframes)==3


def test_backward_compat_validation_history(tmp_path):
    shot=Shot.validated({'keyframes':list(reversed(FRAMES)), 'fx_override':True})
    assert [f['time'] for f in shot.keyframes]==[-2,0,2]
    project=SceneProject()
    project.put('K',shot)
    project.save(tmp_path/'scene.json')
    saved=SceneProject.load(tmp_path/'scene.json')
    assert saved.to_dict()['schema_version']==3
    assert saved.shots['K'].keyframes==shot.keyframes
    assert saved.undo() is False  # ephemeral undo history not persisted
    assert project.undo()
    assert 'K' not in project.shots
    assert project.redo()
    assert project.shots['K'].keyframes==shot.keyframes
    for version in (1,2):
        old=SceneProject.from_dict({'schema_version':version,'shots':{'K':{'arc':10}},'sequence':[]})
        assert old.shots['K'].keyframes==[] and not old.shots['K'].fx_override
    with pytest.raises(ValueError):
        Shot.validated({'keyframes':[{}]*41})
    with pytest.raises(ValueError):
        Shot.validated({'keyframes':'bad'})


def test_keyframes_in_per_scene_render_template():
    k=Kill(1,100,'Aimin','Enemy',[])
    base=Template(style='third_cinema')
    shots={scene_key(k):asdict(Shot.validated({'keyframes':FRAMES,'fx_override':True,'bloom':.6}))}
    output=list(build_scene_templates([k],base,shots,auto=False))
    assert len(output)==1
    assert output[0][1].style=='lolnam_cinema'
    assert output[0][1].scene_keyframes[1]['yaw']==30
    assert output[0][1].bloom==.6
    assert base.style=='third_cinema' and base.scene_keyframes==[]


def test_gui_create_keyframes_and_save(tmp_path):
    root=tk.Tk()
    try:
        app=App(root)
        app.scene_project_path=tmp_path/'scene.json'
        app.locked=Player(1,'Aimin','Aimin#1','Aimin','Lee Sin','ORDER')
        app.kills=[Kill(1,100,'Aimin','Enemy',[])]
        app.checked_kills={0}
        app._fill_kills()
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        app.kf_vars['time'].set(-1)
        app.kf_vars['yaw'].set(20)
        app.kf_vars['zoom'].set(10)
        app.kf_vars['fov'].set(-4)
        app.on_keyframe_upsert()
        app.var_scene_fx_enabled.set(True)
        app.scene_fx_vars['bloom'].set(.8)
        app.on_save_scene()
        key=scene_key(app.kills[0])
        assert app.scene_project.shots[key].keyframes[0]['yaw']==20
        assert app.scene_project.shots[key].fx_override
        assert app.scene_project.shots[key].bloom==.8
        app._autosave_project()
        reloaded=SceneProject.load(app.scene_project_path)
        assert reloaded.shots[key].keyframes[0]['yaw']==20
        assert app.scene_project.undo() and key not in app.scene_project.shots
        assert app.scene_project.redo() and key in app.scene_project.shots
    finally:
        root.destroy()


def test_scene_thumbnail_is_opt_in_and_written_from_mirror(tmp_path,monkeypatch):
    import numpy as np
    import legacy_app as module
    monkeypatch.setattr(module,'ROOT',tmp_path)
    root=tk.Tk()
    try:
        app=App(root)
        app.kills=[Kill(1,100,'Aimin','Enemy',[])]
        app._fill_kills()
        app.lb_kills.selection_set(0)
        app.on_scene_selection()
        key=scene_key(app.kills[0])
        assert not app._scene_thumbnail_path(key).exists()
        app._current_frame_rgb=lambda w,h:(np.full((90,160,3),[20,90,180],dtype=np.uint8),'mirror')
        app.on_capture_scene_thumbnail()
        assert app._scene_thumbnail_path(key).is_file()
        assert app._scene_thumbnail_photo is not None
    finally:
        root.destroy()
