# -*- coding: utf-8 -*-
from pathlib import Path
from types import SimpleNamespace
from core.effects import Template
from ui.scene_project import Shot, SceneProject, scene_key, recommend, apply_shot
from ui.scene_batch import render_scenes, build_scene_templates

def kill(event, at, multi=1, role='kill'):
    return SimpleNamespace(event_id=event, time=at, killer='Aimin', victim=f'E{event}', multikill=multi, role=role)

def test_recommendation():
    assert recommend(kill(1,100,1)).arc == 10
    assert recommend(kill(2,101,2)).arc == 14
    assert recommend(kill(3,102,3)).arc == 22
    assert recommend(kill(4,103,1,'assist')).intensity == 'natural'

def test_save_history_roundtrip(tmp_path):
    p=SceneProject(); k=scene_key(kill(1,200))
    p.put(k,Shot(profile='dynamic',arc=22))
    p.put(k,Shot(profile='smooth',arc=7))
    assert p.undo() and p.shots[k].arc == 22
    assert p.redo() and p.shots[k].arc == 7
    f=tmp_path/'project.json';p.save(f)
    loaded=SceneProject.load(f)
    assert loaded.shots[k].arc == 7
    assert loaded.to_dict()['schema_version'] == 1
    assert len(loaded.to_dict()['shots'])==1
    assert SceneProject.from_dict(loaded.to_dict()).shots[k].profile=='smooth'

def test_numeric_validation():
    checked=Shot.validated({'arc':500,'dolly':-5,'yaw':999,'pre':float('nan'),'post':0})
    assert checked.arc==75 and checked.dolly==0 and checked.yaw==180
    assert checked.pre==4 and checked.post==1

def test_template_per_scene_preserves_original():
    base=Template(style='third_cinema',motion_arc=3,motion_dolly=2,pre=4,post=3)
    k1,k2=kill(1,100),kill(2,150,3)
    override={scene_key(k1): {'profile':'dynamic','arc':37,'dolly':8,'yaw':90,'pre':5,'post':6,'intensity':'strong'}}
    result=list(build_scene_templates([k1,k2],base,override,auto=True))
    assert result[0][1].motion_arc==37 and result[0][1].third_yaw==90
    assert result[0][1].style=='lolnam_cinema'
    assert result[1][1].motion_arc==22
    assert base.style=='third_cinema' and base.motion_arc==3
    disabled=list(build_scene_templates([k1],base,{},auto=False))
    assert disabled[0][1].style=='third_cinema' and disabled[0][1].motion_arc==3

def test_render_delegates_to_existing_audio_gpu_path(tmp_path):
    base=Template(style='third_cinema',game_audio=True)
    events=[kill(1,100),kill(2,180,3)]
    calls=[];montage=[];progress=[]
    def fake_run(api,source,player,ks,tpl,out_root,make_montage,**kw):
        assert tpl.game_audio is True
        assert kw['audio_factory'] is not None
        calls.append((ks[0].event_id,tpl.motion_arc,tpl.style,make_montage))
        return SimpleNamespace(outputs=[tmp_path/f'{len(calls)}.mp4'],failed=[])
    def fake_concat(outputs,target):
        montage.append((list(outputs),target))
    player=SimpleNamespace(name='Aimin',champion='Lee Sin')
    result=render_scenes(None,None,player,events,base,tmp_path,True,{},auto=True,
                          run_edit=fake_run,concat=fake_concat,unique_path=lambda p:p,
                          audio_factory=lambda _:None,progress=lambda *a:progress.append(a))
    assert len(calls)==2 and calls[0][1]==10 and calls[1][1]==22
    assert calls[0][2]=='lolnam_cinema'
    assert all(x[3] is False for x in calls)
    assert len(result.outputs)==2 and len(montage)==1 and result.montage is not None
    assert progress[-1][2]==100

def test_no_implicit_camera_change_for_other_modes():
    t=Template(style='fps')
    k=kill(1,100)
    selected=list(build_scene_templates([k],t,{},auto=True))
    assert selected[0][1].style=='fps'
