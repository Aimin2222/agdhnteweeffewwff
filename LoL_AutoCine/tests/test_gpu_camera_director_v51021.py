"""New live tuning must preserve old templates and control actual camera geometry."""
from dataclasses import fields, replace
from types import SimpleNamespace
import json
import math
import subprocess
from zipfile import ZipFile
import pytest
from core import camera, jobs, camera_tuning
from core.effects import Template, FFMPEG
from core.players import Player
from tools.reference_video_review import create_sheets


def rig(third=True):
    return camera.RigInfo(mode='fps',third=third,h=(-.5,-math.sqrt(.75)),v=(7500,1900,-9000),
        rot={'x':0.,'y':42.,'z':0.},pitch_axis='y',pitch_sign=1.)


@pytest.mark.parametrize('style',['third_cinema','lolnam_cinema'])
def test_director_zero_half_full_controls_real_orbit_and_approach(style):
    poses=[];orbits=[]
    for gain in (0,.5,1):
        p=camera.CameraPlan(style=style,rig=rig(),third_dist=1060,third_elev=37,
            team='ORDER',kill_time=10,motion_arc=10*gain,motion_profile='cinematic')
        p._auto_director_strength=gain
        poses.append(math.dist((0,0,0),p.third_pose_at(10)[0]))
        orbits.append(p._lolnam_orbit(10))
    assert poses[0]==pytest.approx(1060)
    assert poses[0]>poses[1]>poses[2]
    if style=='lolnam_cinema':assert orbits[0]==0 and 0<orbits[1]<orbits[2]
    old=camera.CameraPlan(style=style,rig=rig(),team='ORDER',kill_time=10,motion_arc=0)
    if style=='lolnam_cinema':assert old._lolnam_orbit(10)>0  # old 0 still means automatic


@pytest.mark.parametrize('side,heading',[('blue',0),('red',180)])
def test_red_fps_manual_heading_applies_to_position_and_rotation(monkeypatch,side,heading):
    monkeypatch.setattr(jobs.time,'sleep',lambda _:None)
    monkeypatch.setattr(jobs,'attach_to_player',lambda *a,**kw:rig(False))
    api=SimpleNamespace(set_playback=lambda **kw:None,seek=lambda t:t)
    player=Player(0,'Hero','Hero#JP','Hero','Hero','CHAOS')
    p,_=jobs._setup_clip(api,player,Template(style='fps',camera_side=side),10,[SimpleNamespace(time=11)],lambda _:None)
    assert p._live_fps_side_heading==heading
    assert p.rotation_at(10)['x']==-heading
    original=p.third_pose_at(10)[0];offset=p.offset_at(10)
    assert offset[0]==pytest.approx(original[0]*(1 if heading==0 else -1))
    assert offset[2]==pytest.approx(original[2]*(1 if heading==0 else -1))
    assert math.dist((0,0,0),offset)<2500


def test_strength_snapshot_survives_scene_replace_and_keeps_camera_abi(monkeypatch):
    assert fields(camera.CameraPlan)[-1].name=='team'
    assert Template().auto_director_strength is None
    tpl=replace(Template(auto_director_strength=0),style='lolnam_cinema')
    monkeypatch.setattr(jobs.time,'sleep',lambda _:None)
    monkeypatch.setattr(jobs,'attach_to_player',lambda *a,**kw:rig())
    api=SimpleNamespace(set_playback=lambda **kw:None,seek=lambda t:t)
    p,_=jobs._setup_clip(api,Player(0,'Hero','Hero#JP','Hero','Hero','ORDER'),tpl,10,[SimpleNamespace(time=11)],lambda _:None)
    assert p._auto_director_strength==0 and p._lolnam_orbit(11)==0


@pytest.mark.parametrize('value',[float('nan'),float('inf'),9])
def test_tuning_rejects_nonfinite_or_large_angle(monkeypatch,value):
    monkeypatch.setitem(camera_tuning.SHOT_TUNING,('BLUE','third'),{'distance':1.,'angles':{'x':value}})
    with pytest.raises(ValueError):camera_tuning.shot_tuning('ORDER','third')


def test_one_video_generates_six_samples_and_keeps_original(tmp_path):
    video=tmp_path/'reference video (Jhin).mp4'
    subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i','testsrc2=size=320x180:rate=60:duration=1',
        '-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True,capture_output=True,timeout=30)
    data=video.read_bytes()
    output=create_sheets(video,tmp_path/'sheets',logger=lambda _:None)
    with ZipFile(output) as z:
        assert z.testzip() is None
        item=json.loads(z.read('reference_review.json'))['items'][0]
        assert item['relative_path']==video.name and len(item['samples'])==6 and not item['errors']
        assert item['contact_sheet'] in z.namelist()
    assert video.read_bytes()==data



def test_target_relative_fps_keeps_the_height_control():
    p=camera.CameraPlan(style='fps',rig=rig(False),height=0)
    p._live_fps_recenter=True
    before=p.offset_at(2)
    p.height=170
    after=p.offset_at(2)
    assert after[0]==before[0] and after[2]==before[2]
    assert after[1]-before[1]==pytest.approx(170)
