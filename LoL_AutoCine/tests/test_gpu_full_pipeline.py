"""Resource lifetime, ABI, graph coverage and fail-safe dispatch; no GPU assumed."""
from pathlib import Path
from types import SimpleNamespace
import subprocess
import pytest
from core import effects as fx, gpu_full as gpu, performance_diagnostics as perf
from core.gpu_pipeline import GPUCapabilities
from core.effects import Template


def neutral(**kw):
    return Template(**(dict(grade='standard',grade_strength=0,bloom=0,vignette=0,
                           grain=0,transition='cut',game_audio=False)|kw))


def test_color_definition_is_shared_and_calibration_has_all_rgb_values():
    from PIL import Image
    import numpy as np
    tpl=neutral(temperature=.3,vibrance=.4,exposure=.05,curve_enabled=True)
    stage=gpu.GPUFullStage(tpl,1,[],ffmpeg=fx.FFMPEG)
    folder=Path(stage.folder.name)
    try:
        pixels=np.asarray(Image.open(stage.lut))
        assert pixels.shape==(33,1089,4)
        assert pixels[0,0,:3].max()<35
        assert pixels[32,1088,:3].min()>200
        assert fx.color_filters(tpl)==fx.build_graph(tpl,1,False).split('[0:v]')[1].split(',format=yuv420p')[0].split(',')
    finally:stage.close()
    assert not folder.exists()


def test_all_effects_resident_gpu_keep_order_clock_and_no_cpu_pixel_filters():
    tpl=neutral(video_effects={k:.7 for k in fx.VIDEO_EFFECT_LABELS},dof_enabled=True,
                dof_blur=3,dof_shape='band',bloom=.3,vignette=.3,grain=.2,
                bars=.06,fog_enabled=True,fog_strength=.3,bpm=120,highlight_pulse=.5)
    stage=gpu.GPUFullStage(tpl,1,[(.4,.6)],ffmpeg=fx.FFMPEG)
    try:
        assert set(fx.VIDEO_EFFECT_LABELS)<=stage.effects
        assert {'color_grade','scale','dof','bloom','grain','fog','bars','bpm','highlight_pulse'}<=stage.effects
        graph=stage.graph
        assert graph.count('hwdownload')==1 and graph.count('hwupload')==2 # footage + static LUT
        assert 'trim=end_frame=60' in graph and 'setpts=N/(60*TB),fps=fps=60' in graph
        for cpu in ('eq=','colorbalance=','noise=','vignette=','scale=','tmix=','overlay=','drawbox=','maskedmerge','gblur=','lut3d='):
            assert cpu not in graph
        assert graph.index('fps=fps=60')<graph.index('kernel=color_scale')<graph.index('kernel=full_dof_x')<graph.index('kernel=full_bloom_x')
        assert 'loop=loop=4:size=1:start=0' in graph # temporal history, hardware frame clones
        assert 'device_type=gpu' in gpu.OPENCL_DEVICE
    finally:stage.close()


def test_future_unknown_effect_fails_explicitly_instead_of_dropping_it():
    with pytest.raises(ValueError,match='future_effect'):
        gpu.GPUFullStage(neutral(video_effects={'future_effect':.5}),1,[],ffmpeg=fx.FFMPEG)


def test_portraits_share_bounded_stack_and_gpu_scale_opacity(tmp_path):
    from core.kill_icons import badge_plan
    from PIL import Image
    badges=[]
    for n in range(4):
        p=tmp_path/f'{n}.png';Image.new('RGBA',(96,48),(255,0,0,127)).save(p)
        badges.append((p,.2+n*.1))
    plan=badge_plan(badges,2,1.55)
    assert plan[0]['end']==pytest.approx(.39) and [p['row'] for p in plan]==[0,1,2,0]
    tpl=neutral(kill_icon_style='impact',kill_icon_scale=.8,kill_icon_opacity=.4)
    stage=gpu.GPUFullStage(tpl,2,[],ffmpeg=fx.FFMPEG,title_index=1,badge_index=2,badges=badges,lut_index=6)
    try:
        assert '[6:v]' in stage.graph and '[5:v]' in stage.graph
        assert stage.graph.index('kernel=title')<stage.graph.index('kernel=badge_0')
        code=stage.path.read_text()
        assert '0.400000000f' in code and '0.800000000f' in code
        assert '0.390000000f' in code and '7*sin(35*' in code
    finally:stage.close()


@pytest.mark.parametrize('failure',['driver','color','timeout'])
def test_full_gpu_retries_same_cpu_effects_titles_events_audio_and_cleans(tmp_path,monkeypatch,failure):
    from PIL import Image
    src=tmp_path/'in.mp4';src.write_bytes(b'source')
    dst=tmp_path/'out.mp4';wav=tmp_path/'game.wav';wav.write_bytes(b'wave'*100)
    bgm=tmp_path/'bgm.wav';bgm.write_bytes(b'bgm'*100)
    badge=tmp_path/'portrait.png';Image.new('RGBA',(96,48)).save(badge)
    tpl=neutral(video_effects={'vignette_fx':.3,'radial_blur':.4},dof_enabled=True,dof_blur=4,bloom=.3)
    tpl.title_text='TITLE';tpl.game_audio=True;tpl.bgm_path=str(bgm);tpl.kill_icon_style='neon'
    original=tpl.to_dict();calls=[];paths=[]
    # Calibration behavior is separately exercised with real FFmpeg above.
    monkeypatch.setattr(gpu,'_bake_color',lambda *a:bytes(33**3*3))
    monkeypatch.setattr(gpu,'decode_probe',lambda *a:(True,''))
    monkeypatch.setattr(fx,'detect_gpu',lambda:GPUCapabilities(nvenc=True,cuda=True,full_gpu_runtime_ok=True))
    monkeypatch.setattr(fx,'encoder_args',lambda *a,**k:['-c:v','h264_nvenc','-pix_fmt','yuv420p'])
    monkeypatch.setattr(fx,'make_event_badges',lambda *a,**k:[(badge,.4)])
    checks=iter([30,0] if failure=='color' else [30,30])
    monkeypatch.setattr(fx,'_colorfulness',lambda _:next(checks))
    monkeypatch.setattr(fx.subprocess,'run',lambda *a,**k:SimpleNamespace(stderr='Audio:',returncode=0))
    def render(cmd,**kw):
        calls.append((cmd,kw))
        graph=cmd[cmd.index('-filter_complex')+1]
        assert wav.name in ' '.join(cmd) and bgm.name in ' '.join(cmd)
        if len(calls)==1:
            assert cmd[cmd.index('-pix_fmt')+1]=='rgba' and '-hwaccel' in cmd
            assert '-loop' not in cmd # images are uploaded once, then repeated on GPU
            assert kw['pipeline_info']['full_gpu_pipeline'] and not kw['pipeline_info']['cpu_video_effects']
            shader=Path(graph.split("source='")[1].split("'")[0]);paths.append(shader)
            assert shader.exists() and kw['gpu_effects']>=set(tpl.video_effects)
            if failure=='timeout': raise subprocess.TimeoutExpired(cmd,600)
            if failure=='driver': return SimpleNamespace(returncode=1,stderr='driver failure')
        else:
            assert '-hwaccel' not in cmd and '-init_hw_device' not in cmd
            assert cmd[cmd.index('-pix_fmt')+1]=='yuv420p'
            assert not kw['pipeline_info']['full_gpu_pipeline'] and kw['gpu_effects']==[]
            assert 'tmix=' in graph and "between(t,0.300,1.000)" in graph
            assert 'cdofalpha' in graph and 'gblur=' in graph
            assert paths[0].exists()
        dst.write_bytes(b'output'*400)
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(perf,'run_render',render)
    fx.apply_effects(src,dst,tpl,1,[],game_wav=wav,effect_events=[(.4,.6)])
    assert len(calls)==2 and tpl.to_dict()==original
    assert not paths[0].exists() and not badge.exists() and not dst.with_suffix('.title.png').exists()


def test_nvenc_rgba_to_x264_retry_keeps_audio_and_compatible_output():
    cmd=['ffmpeg','-i','video','-i','game.wav','-map','[vout]','-map','[aout]',
         '-c:v','h264_nvenc','-preset','p5','-pix_fmt','rgba','-c:a','aac','out.mp4']
    retry=perf.cpu_encoder_retry_command(cmd)
    assert 'libx264' in retry and retry[retry.index('-pix_fmt')+1]=='yuv420p'
    assert retry.count('-map')==2 and '-i' in retry and 'game.wav' in retry and 'aac' in retry


def test_forced_cpu_never_initializes_gpu_stage(tmp_path,monkeypatch):
    monkeypatch.setenv('AUTOCINE_GPU_EFFECTS','cpu')
    monkeypatch.setattr(fx,'detect_gpu',lambda:GPUCapabilities(opencl_runtime_ok=True,rgba_gpu_runtime_ok=True,full_gpu_runtime_ok=True))
    monkeypatch.setattr(fx,'_apply_effects',lambda *args:assert_cpu(args[-3]))
    def assert_cpu(caps):
        assert not caps.opencl_runtime_ok and not caps.rgba_gpu_runtime_ok and not caps.full_gpu_runtime_ok
    fx.apply_effects(tmp_path/'src',tmp_path/'dst',neutral(bloom=.3),1,[])


def test_nvdec_failure_is_cached_and_reported(monkeypatch):
    calls=[]
    monkeypatch.setattr(gpu.subprocess,'run',lambda cmd,**k:(calls.append(cmd) or SimpleNamespace(returncode=1,stderr='unsupported codec')))
    gpu.decode_probe.cache_clear()
    assert gpu.decode_probe('ffmpeg','clip',1)==(False,'unsupported codec')
    assert gpu.decode_probe('ffmpeg','clip',1)==(False,'unsupported codec')
    assert len(calls)==1 and '-hwaccel' in calls[0]
    gpu.decode_probe.cache_clear()
