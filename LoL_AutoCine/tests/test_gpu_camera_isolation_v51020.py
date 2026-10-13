"""Mode and team isolation must apply to both calibration and last-good rotation."""
import json
import math
import subprocess
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
from PIL import Image
from core import camera, jobs
from core.effects import Template, FFMPEG
from core.players import Player
from tools.reference_video_review import create_sheets


@pytest.mark.parametrize('other_key', [('Hero', 'ORDER', 'third'), ('Hero', 'CHAOS', 'third_cinema')])
def test_other_mode_or_team_cannot_restore_its_rotation(monkeypatch, other_key):
    monkeypatch.setattr(camera, '_TPS_CALIBRATION', {})
    monkeypatch.setattr(camera, '_TPS_STABLE_ROTATIONS', {})
    def save(key):
        camera._cache_success(key, (0,0,0), (0,1900,-2500),
            {'x':180., 'y':37., 'z':0.}, (0,-1), 'y', 1, lambda _:None, 'ok')
    class API:
        def __init__(self): self.values={}
        def set_render(self, **kw): self.values.update(kw)
        def render(self):
            off=self.values.get('selectionOffset', {})
            pos=({'x':0., 'y':1900., 'z':-2500.} if self.values['cameraMode']=='top'
                 else {'x':off.get('x',0), 'y':off.get('y',0), 'z':off.get('z',0)})
            return {'cameraPosition':pos, 'cameraRotation':{'x':0., 'y':37., 'z':0.},
                    'cameraMode':self.values['cameraMode'], 'cameraAttached':True,
                    'selectionName':self.values['selectionName'], 'selectionOffset':off}
    player=Player(0,'Hero','Hero#JP','Hero','Hero','ORDER')
    save(other_key)
    camera.clear_tps_calibration('Hero', preserve_rotation=True)
    rig=camera.attach_to_player(API(), player, 'third_cinema', settle=0, third_elev=37)
    assert rig.third and rig.rot['x']==0
    own=('Hero','ORDER','third_cinema')
    save(own)
    camera.clear_tps_calibration('Hero', preserve_rotation=True)
    rig=camera.attach_to_player(API(), player, 'third_cinema', settle=0, third_elev=37)
    # The corrected engine contract must not restore a stored backwards yaw.
    # This own-mode cache remains separate, but aim is derived from its position.
    assert rig.third and rig.rot['x']==0 and rig.rot['z']==0
    camera.clear_tps_calibration('Hero')
    assert not camera._TPS_CALIBRATION and not camera._TPS_STABLE_ROTATIONS


@pytest.mark.parametrize('team', ['ORDER','CHAOS'])
@pytest.mark.parametrize('style', ['third','third_cinema','fps','lolnam_cinema','geo_aim'])
def test_live_flags_are_limited_to_their_side_and_mode(monkeypatch, team, style):
    monkeypatch.setattr(jobs.time,'sleep',lambda _:None)
    rig=camera.RigInfo(mode='fps',third=style!='fps',h=(0,-1),v=(0,1900,-2500),
        rot={'x':0.,'y':37.,'z':0.},pitch_axis='y',pitch_sign=1.)
    monkeypatch.setattr(jobs,'attach_to_player',lambda *a,**kw:rig)
    api=SimpleNamespace(set_playback=lambda **kw:None,seek=lambda t:t)
    player=Player(0,'Hero','Hero#JP','Hero','Hero',team)
    plan,_=jobs._setup_clip(api,player,Template(style=style),10,[SimpleNamespace(time=11)],lambda _:None)
    assert plan._live_blue_geo_look == (team=='ORDER' and style in ('third','third_cinema','lolnam_cinema'))
    assert plan._live_blue_pulled_back == (team=='ORDER' and style=='third')
    assert plan._live_fps_recenter == (style=='fps')
    assert plan._live_red_normal_reframe == (team=='CHAOS' and style=='third')
    rotation=plan.rotation_at(10)
    assert all(math.isfinite(v) for v in rotation.values())
    assert rotation['z']==0.0  # v5.10.23 removes RED normal-third roll bias


def test_empty_reference_folder_produces_valid_report(tmp_path):
    src=tmp_path/'videos';src.mkdir()
    result=create_sheets(str(src),tmp_path/'sheets',logger=lambda _:None)
    with ZipFile(result) as z:
        assert z.testzip() is None and z.namelist()==['reference_review.json']
        assert json.loads(z.read('reference_review.json'))['video_count']==0


def test_reference_six_frames_are_generated_without_changing_video(tmp_path):
    src=tmp_path/'videos';src.mkdir();video=src/'reference.mp4'
    subprocess.run([FFMPEG,'-y','-loglevel','error','-f','lavfi','-i',
        'testsrc2=size=320x180:rate=60:duration=1','-c:v','libx264','-pix_fmt','yuv420p',str(video)],
        check=True,capture_output=True,timeout=30)
    original=video.read_bytes()
    output=tmp_path/'review'
    result=create_sheets(src,output,logger=lambda _:None)
    with ZipFile(result) as z:
        assert z.testzip() is None
        report=json.loads(z.read('reference_review.json'));item=report['items'][0]
        assert report['video_count']==1 and len(item['samples'])==6 and not item['errors']
        with Image.open(output/item['contact_sheet']) as sheet: assert sheet.size==(1440,588)
        assert len(z.namelist())==2
    assert video.read_bytes()==original
