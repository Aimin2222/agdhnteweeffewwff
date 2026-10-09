"""GPU-owned v5.10.0 encoder, diagnostics and portrait design tests."""
from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from PIL import Image
from core.effects import Template, encoder_args
from core.kill_icons import MARK_STYLES, make_badge, normalize_design
from core.performance_diagnostics import cpu_encoder_retry_command, latest_render_summary

def _icons(folder):
    a,b=folder/'a.png',folder/'b.png'
    Image.new('RGB',(64,64),(255,32,32)).save(a)
    Image.new('RGB',(64,64),(20,160,240)).save(b)
    return a,b


def test_color_and_mark_validation():
    assert normalize_design('#aabbcc','#ccddff',True,.9,5,'swords') == ('#AABBCC','#CCDDFF',True,.9,5,'swords')
    assert normalize_design('red','ffccff',True,float('nan'),300,'bad') == ('','',True,.65,8,'auto')
    assert normalize_design('','','',-1,-4,'cross')[3:] == (0,1,'cross')


@pytest.mark.parametrize('mark',list(MARK_STYLES))
def test_all_marks_and_custom_frame(tmp_path,mark):
    a,b=_icons(tmp_path)
    target=make_badge(tmp_path/(mark+'.png'),'neon',killer_icon=a,victim_icon=b,
                      mark_style=mark,frame_color='#22AA44',glow_color='#5533DD',border_width=6,glow_strength=.8)
    with Image.open(target) as img:
        assert img.size==(385,116)
        assert img.getpixel((77,55))[:3] == (255,32,32)
        assert img.getpixel((306,55))[:3] == (20,160,240)
        assert img.getpixel((35,53))[3]>0
        assert img.getpixel((192,58))[3]>0


def test_glow_toggle_does_not_change_portrait(tmp_path):
    a,b=_icons(tmp_path)
    on=make_badge(tmp_path/'on.png','cinema',killer_icon=a,victim_icon=b,glow_enabled=True)
    off=make_badge(tmp_path/'off.png','cinema',killer_icon=a,victim_icon=b,glow_enabled=False)
    with Image.open(on) as i, Image.open(off) as j:
        assert i.getpixel((77,55))==j.getpixel((77,55))
        assert i.getpixel((120,50))!=j.getpixel((120,50))


def test_cpu_encoder_selection(monkeypatch):
    from core import effects
    monkeypatch.setattr(effects,'gpu_encoder_available',lambda:True)
    assert 'libx264' in encoder_args(60,policy='cpu')
    assert 'h264_nvenc' in encoder_args(60,policy='auto')
    assert 'h264_nvenc' in encoder_args(60,policy='gpu')
    monkeypatch.setattr(effects,'gpu_encoder_available',lambda:False)
    assert 'libx264' in encoder_args(60,policy='gpu')


def test_nvenc_command_fallback_preserves_audio_filters_and_fps():
    original=['ffmpeg','-i','a.mp4','-filter_complex','[0:v]null[vout]','-map','[vout]',
              '-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr',
              '-cq','18','-b:v','0','-r','60','-pix_fmt','yuv420p',
              '-c:a','copy','output.mp4']
    retry=cpu_encoder_retry_command(original)
    assert 'h264_nvenc' not in retry and 'libx264' in retry
    assert retry[1:8]==original[1:8]
    assert retry[retry.index('-r'):] == original[original.index('-r'):]
    assert cpu_encoder_retry_command(['-c:v','libx264','output.mp4']) is None


def test_latest_render_diagnostics_explicit_gpu_fx(tmp_path):
    d=tmp_path/'performance'
    d.mkdir()
    f=d/'render_00001.json'
    f.write_text(json.dumps({'encoder':'h264_nvenc','gpu_effects_confirmed':False,'returncode':0}),encoding='utf-8')
    assert 'エフェクト CPU' in latest_render_summary(tmp_path)
    assert 'h264_nvenc' in latest_render_summary(tmp_path)
    f.write_text(json.dumps({'encoder':'libx264','gpu_effects_confirmed':True,'returncode':0,
                             'encoder_retry_reason':'nvenc failed'}),encoding='utf-8')
    assert 'エフェクト GPU' in latest_render_summary(tmp_path)
    assert 'CPU切替' in latest_render_summary(tmp_path)


def test_nvenc_runtime_failure_is_retried_as_cpu_with_real_diagnostics(tmp_path, monkeypatch):
    from core import performance_diagnostics as perf
    # Isolate generated diagnostics instead of touching the user's application logs.
    fake_file=tmp_path/'core'/'performance_diagnostics.py'
    monkeypatch.setattr(perf,'__file__',str(fake_file))
    monkeypatch.setattr(perf,'_sample_gpu',lambda:{})
    seen=[]
    def fake_run(args, **kwargs):
        seen.append(list(args))
        if 'h264_nvenc' in args:
            return SimpleNamespace(returncode=1, stderr='driver rejected NVENC')
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(perf.subprocess,'run',fake_run)
    args=['ffmpeg','-y','-i','source.mp4','-map','0:v',
          '-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr','-cq','18','-b:v','0',
          '-r','60','-pix_fmt','yuv420p','clip.mp4']
    outcome=perf.run_render(args,output=tmp_path/'clip.mp4',gpu_effects=[],effect_values={})
    assert outcome.returncode == 0
    assert len(seen)==2
    assert 'libx264' in seen[1]
    details=list((tmp_path/'diagnostics'/'performance').glob('render_*.json'))
    assert details
    info=json.loads(details[0].read_text(encoding='utf-8'))
    assert info['encoder']=='libx264'
    assert 'driver rejected NVENC' in info['encoder_retry_reason']


def test_raw_recording_cpu_preference_never_selects_nvenc(tmp_path, monkeypatch):
    import numpy as np
    from core import recorder
    class FakeSource:
        frame_count=1
        def latest(self):
            return np.zeros((24,32,4),dtype=np.uint8)
    seen=[]
    class FakeProc:
        stdin=object()
        stderr=None
    class DummyThread:
        def __init__(self,*args,**kwargs): pass
        def start(self): pass
    monkeypatch.setattr(recorder,'gpu_encoder_available',lambda:True)
    monkeypatch.setattr(recorder.subprocess,'Popen',lambda cmd,**kw:(seen.append(cmd) or FakeProc()))
    monkeypatch.setattr(recorder.threading,'Thread',DummyThread)
    raw=recorder.ClipRecorder(FakeSource(),tmp_path/'raw.mp4',fps=60,encoder_policy='cpu')
    raw.start()
    assert 'libx264' in seen[0] and 'h264_nvenc' not in seen[0]


def test_montage_cpu_policy_is_passed_into_encoder_args(tmp_path,monkeypatch):
    from core import montage_fx, effects
    clips=[tmp_path/'a.mp4',tmp_path/'b.mp4']
    selected=[]
    monkeypatch.setattr(effects,'encoder_args',lambda fps,policy='auto':(selected.append(policy) or ['-c:v','libx264','-preset','veryfast','-crf','17']))
    monkeypatch.setattr(montage_fx,'get_duration',lambda *a,**kw:1.0)
    def mock_concat(files,dst):Path(dst).write_bytes(b'joint-audio')
    def mock_run(cmd,**kwargs):
        Path(cmd[-1]).write_bytes(b'audio-preserved'*100)
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(montage_fx.subprocess,'run',mock_run)
    assert montage_fx.render_montage(clips,tmp_path/'out.mp4','dark',concat=mock_concat,
                                     encoder_policy='cpu')=='dark'
    assert selected==['cpu']
