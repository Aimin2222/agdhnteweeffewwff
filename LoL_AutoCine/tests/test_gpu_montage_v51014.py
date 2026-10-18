"""All new accents must retain video clocks/audio and reach the GPU path."""
from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from core import gpu_full, gpu_pipeline, montage_fx, effects
from core.camera import CameraPlan,RigInfo

@pytest.mark.parametrize('style',list(montage_fx.MONTAGE_PROFILES))
def test_every_accent_builds_gpu_graph_and_preserves_original_frame_count(tmp_path,monkeypatch,style):
    monkeypatch.setattr(gpu_full,'mode',lambda:'full')
    monkeypatch.setattr(gpu_pipeline,'detect',lambda:SimpleNamespace(full_gpu_runtime_ok=True))
    monkeypatch.setattr(gpu_full.subprocess,'run',lambda *a,**k:SimpleNamespace(stderr='Video: h264, 1920x1080, 60 fps',returncode=1))
    monkeypatch.setattr(gpu_full,'_montage_frame_count',lambda *a:61)
    monkeypatch.setattr(gpu_full,'_bake_color',lambda *a:bytes(1089*33*3))
    from core import performance_diagnostics as diag
    calls=[]
    def render(cmd,**kw):
        graph=cmd[cmd.index('-filter_complex')+1]
        kernel_path=graph.split("source='")[1].split("'")[0]
        shader=Path(kernel_path.replace(r'\:', ':')).read_text()
        assert 'eq_rgb' in shader and gpu_full.number(montage_fx.MONTAGE_PROFILES[style][0]) in shader
        assert cmd[cmd.index('-frames:v')+1]=='61'
        assert 'trim=end_frame=61' in graph and 'setpts=N/(60*TB)' in graph
        assert cmd[cmd.index('-c:a')+1]=='copy' and '0:a?' in cmd
        post=montage_fx.MONTAGE_PROFILES[style][2]
        assert ('apply_lut(aux,c.xyz)' in shader)==bool(post)
        assert kw['pipeline_info']['cpu_video_effects']==[]
        assert kw['pipeline_info']['input_frames']==61
        Path(cmd[-1]).write_bytes(b'encoded'*400)
        calls.append(cmd)
        return SimpleNamespace(returncode=0,stderr='',args=cmd)
    monkeypatch.setattr(diag,'run_render',render)
    assert gpu_full.render_gpu_montage('ffmpeg',tmp_path/'source.mp4',tmp_path/'out.mp4',style,[.5],['-c:v','libx264'])
    assert len(calls)==1

@pytest.mark.parametrize('style',list(montage_fx.MONTAGE_PROFILES))
def test_new_accent_dispatches_gpu_before_cpu_and_copies_audio(tmp_path,monkeypatch,style):
    monkeypatch.setattr(effects,'encoder_args',lambda *a,**k:['-c:v','libx264'])
    monkeypatch.setattr(montage_fx,'get_duration',lambda *a,**k:1.)
    attempts=[]
    def gpu(ff,source,dest,key,cuts,args,logger):
        attempts.append(key);Path(dest).write_bytes(b'gpu result'*300);return True
    monkeypatch.setattr(gpu_full,'render_gpu_montage',gpu)
    def concat(clips,dst):Path(dst).write_bytes(b'original audio'*300)
    assert montage_fx.render_montage(['a','b'],tmp_path/'out.mp4',style,concat=concat)==style
    assert attempts==[style]


def test_frame_count_uses_video_not_padded_audio_duration(tmp_path,monkeypatch):
    monkeypatch.setattr(gpu_full.subprocess,'run',lambda *a,**k:SimpleNamespace(
        returncode=0,stdout=json.dumps({'streams':[{'nb_frames':'61'}]})))
    monkeypatch.setattr('shutil.which',lambda name:'ffprobe')
    assert gpu_full._montage_frame_count('ffmpeg',tmp_path/'source.mp4')==61


def test_bundled_ffmpeg_without_probe_counts_packets_without_decode(tmp_path,monkeypatch):
    monkeypatch.setattr('shutil.which',lambda name:None)
    commands=[]
    def run(cmd,**kw):commands.append(cmd);return SimpleNamespace(returncode=0,stdout='frame=1\nframe=61\n')
    monkeypatch.setattr(gpu_full.subprocess,'run',run)
    assert gpu_full._montage_frame_count(str(tmp_path/'ffmpeg.exe'),tmp_path/'source.mp4')==61
    assert commands[0][commands[0].index('-c:v')+1]=='copy' and '-an' in commands[0]

@pytest.mark.parametrize('axis',['x','y','z'])
@pytest.mark.parametrize('sign',[1.,-1.])
@pytest.mark.parametrize('complement',[True,False])
def test_red_normal_pitch_scope_and_kill_cue_bounds(axis,sign,complement):
    rig=RigInfo(mode='fps',third=True,h=(0.,-1.),pitch_axis=axis,pitch_sign=sign,
                pitch_complement=complement,rot={'x':0.,'y':0.,'z':0.})
    blue=CameraPlan(style='third',rig=rig,side_yaw=0,third_elev=31)
    red=CameraPlan(style='third',rig=rig,side_yaw=192,third_elev=31,kill_time=10)
    assert red.rotation_at(0)[axis]==pytest.approx(blue.rotation_at(0)[axis])
    assert red._third_heading(5)==192 and red._third_heading(15)==192
    assert red._third_heading(10)==199
    cine=CameraPlan(style='third_cinema',rig=rig,side_yaw=192,third_elev=31,kill_time=10)
    assert cine.rotation_at(0)[axis]*sign>0
    red.smart_composition=True;red.third_yaw=54
    assert red._third_heading(10)==247  # final motion stays within +55
