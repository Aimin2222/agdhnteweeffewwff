"""GPU dispatch/order/rollback tests; hardware execution is checked separately."""
from pathlib import Path
from types import SimpleNamespace
import subprocess
import pytest
from core.effects import Template, build_graph
from core.gpu_bloom import GPUBlurStage, OPENCL_DEVICE


def neutral(**kw):
    return Template(grade='standard',grade_strength=0,vignette=0,grain=0,
                    bars=0,transition='cut',game_audio=False,**kw)


def test_no_gpu_blur_when_runtime_unverified():
    stage=GPUBlurStage(neutral(bloom=.25,dof_enabled=True,dof_blur=4),SimpleNamespace(rgba_gpu_runtime_ok=False))
    assert not stage.effects and stage.path is None
    graph=build_graph(neutral(bloom=.25),1,False,gpu_blur_stage=stage)
    assert 'gblur=sigma=11' in graph and 'program_opencl' not in graph


def test_both_gpu_blurs_keep_color_before_blur_and_single_transfer():
    tpl=neutral(bloom=.25,dof_enabled=True,dof_blur=4)
    stage=GPUBlurStage(tpl,SimpleNamespace(rgba_gpu_runtime_ok=True))
    try:
        assert stage.effects=={'bloom','dof'} and stage.path.exists()
        graph=build_graph(tpl,1,False,gpu_blur_stage=stage)
        assert graph.index('colorbalance=')<graph.index('kernel=dof_x')<graph.index('kernel=bloom_x')
        assert graph.count('hwupload')==graph.count('hwdownload')==1
        assert 'gblur=' not in graph and 'maskedmerge' not in graph
        assert 'format=rgba' in graph and 'format=yuv420p[vout]' in graph
        assert 'device_type=gpu' in OPENCL_DEVICE
    finally:
        path=stage.path;stage.close()
    assert not path.exists()


def test_band_dof_remains_before_gpu_bloom():
    tpl=neutral(bloom=.3,dof_enabled=True,dof_shape='band',dof_blur=3)
    stage=GPUBlurStage(tpl,SimpleNamespace(rgba_gpu_runtime_ok=True))
    try:
        graph=build_graph(tpl,1,False,gpu_blur_stage=stage)
        assert stage.effects=={'bloom'}
        assert graph.index('dofsrc')<graph.index('kernel=bloom_x')
    finally:stage.close()


def test_rgba_probe_rejects_gpu_failure_and_keeps_reason(monkeypatch):
    from core import gpu_pipeline as gpu
    calls=[]
    monkeypatch.setattr(gpu,'_filters_text',lambda:'program_opencl')
    monkeypatch.setattr(gpu,'_run',lambda args,**kw:(calls.append(args) or (1,'No matching GPU devices')))
    gpu._rgba_probe.cache_clear()
    try:
        ok,reason=gpu._rgba_probe()
        assert not ok and 'No matching GPU' in reason
        assert calls[0][calls[0].index('-init_hw_device')+1]==OPENCL_DEVICE
        assert not Path(calls[0][calls[0].index('-vf')+1].split("source='")[1].split("'")[0]).exists()
    finally:gpu._rgba_probe.cache_clear()


@pytest.mark.parametrize('failure',['driver','color'])
def test_gpu_failure_restores_bloom_dof_title_audio_and_event_timing(tmp_path,monkeypatch,failure):
    from core import effects as fx, performance_diagnostics as perf
    from core.gpu_pipeline import GPUCapabilities
    from core.scanner import Kill
    from PIL import Image
    src=tmp_path/'in.mp4';src.write_bytes(b'source')
    wav=tmp_path/'game.wav';wav.write_bytes(b'wave'*100)
    bgm=tmp_path/'bgm.wav';bgm.write_bytes(b'bgm'*100)
    dst=tmp_path/'out.mp4';badge=tmp_path/'badge.png'
    Image.new('RGBA',(32,16),(0,255,0,255)).save(badge)
    tpl=neutral(bloom=.25,dof_enabled=True,dof_blur=5)
    tpl.game_audio=True;tpl.bgm_path=str(bgm);tpl.title_text='TITLE';tpl.kill_icon_style='neon'
    original=tpl.to_dict();calls=[];shader_paths=[]
    monkeypatch.setattr(fx,'detect_gpu',lambda:GPUCapabilities(rgba_gpu_runtime_ok=True,program_opencl=True))
    monkeypatch.setattr(fx,'encoder_args',lambda *a,**kw:['-c:v','libx264'])
    monkeypatch.setattr(fx,'make_event_badges',lambda *a,**kw:[(badge,.4)])
    color_checks=iter([30,0] if failure=='color' else [30,30])
    monkeypatch.setattr(fx,'_colorfulness',lambda _:next(color_checks))
    monkeypatch.setattr(fx.subprocess,'run',lambda *a,**kw:SimpleNamespace(stderr='Audio:',returncode=0))
    def render(cmd,**kw):
        graph=cmd[cmd.index('-filter_complex')+1]
        assert '.title.png' in ' '.join(cmd) and wav.name in ' '.join(cmd) and bgm.name in ' '.join(cmd)
        # Existing badges begin 0.10s before the recorded event, including retries.
        assert "between(t,0.300,1.000)" in graph
        calls.append((cmd,kw,graph))
        if len(calls)==1:
            path=Path(graph.split("source='")[1].split("'")[0]);shader_paths.append(path)
            assert path.exists() and kw['gpu_effects']=={'bloom','dof'}
            if failure=='driver':
                return SimpleNamespace(returncode=1,stderr='GPU driver refused')
            dst.write_bytes(b'valid-output'*200)
            return SimpleNamespace(returncode=0,stderr='')
        assert shader_paths[0].exists()
        dst.write_bytes(b'valid-output'*200)
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(perf,'run_render',render)
    fx.apply_effects(src,dst,tpl,1,[Kill(1,10,'A','B',[])],game_wav=wav,effect_events=[(.4,.6)])
    assert len(calls)==2 and 'program_opencl' not in calls[1][2]
    assert 'gblur=' in calls[1][2] and 'cdofalpha' in calls[1][2]
    assert calls[1][1]['gpu_effects']==[]
    assert calls[1][1]['pipeline_info']['bloom_cpu_optimized']
    assert calls[1][1]['pipeline_info']['dof_mask_cpu_optimized']
    assert calls[1][1]['pipeline_info']['gpu_backend']=='CPU Effects fallback'
    assert calls[1][1]['pipeline_info']['gpu_opencl_device'] is None
    assert tpl.to_dict()==original
    assert not shader_paths[0].exists() and not badge.exists() and not dst.with_suffix('.title.png').exists()


def test_gpu_binary_checksum_and_override(tmp_path,monkeypatch):
    from core import gpu_binary as b
    import json
    target=tmp_path/b.GPU_ARCHIVE_SHA256/'ffmpeg.exe';target.parent.mkdir();target.write_bytes(b'MZtest')
    marker=tmp_path/'installed.json';marker.write_text(json.dumps({'archive_sha256':b.GPU_ARCHIVE_SHA256,'exe_sha256':b.sha256_file(target)}))
    assert b.verified_gpu_binary(tmp_path)==str(target)
    target.write_bytes(b'MZchanged')
    assert b.verified_gpu_binary(tmp_path) is None
    b.ffmpeg_exe.cache_clear()
    import imageio_ffmpeg
    monkeypatch.setenv('IMAGEIO_FFMPEG_EXE','chosen-ffmpeg')
    monkeypatch.setattr(imageio_ffmpeg,'get_ffmpeg_exe',lambda:'chosen-ffmpeg')
    try:assert b.ffmpeg_exe()=='chosen-ffmpeg'
    finally:b.ffmpeg_exe.cache_clear()


def test_installer_rejects_bad_archive_without_changes(tmp_path):
    from tools.setup_gpu_ffmpeg import install_archive
    archive=tmp_path/'download.zip';archive.write_bytes(b'bad')
    cache=tmp_path/'cache'
    with pytest.raises(RuntimeError,match='checksum'):
        install_archive(archive,cache)
    assert not cache.exists()


def test_installer_activates_only_validated_binary_and_preserves_existing(tmp_path,monkeypatch):
    from tools import setup_gpu_ffmpeg as setup
    from core import gpu_binary as binary
    import zipfile
    archive=tmp_path/'fixture.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('fixture/bin/ffmpeg.exe',b'MZ-test-executable')
        z.writestr('fixture/LICENSE.txt','fixture license')
        z.writestr('../../must-not-extract','unexpected')
    # A local fixture pin; production constants are not changed.
    checksum=binary.sha256_file(archive)
    monkeypatch.setattr(setup,'GPU_ARCHIVE_SHA256',checksum)
    monkeypatch.setattr(binary,'GPU_ARCHIVE_SHA256',checksum)
    def run(command,**kwargs):
        assert Path(command[0]).read_bytes()==b'MZ-test-executable'
        return SimpleNamespace(returncode=0,stdout='program_opencl avgblur_opencl h264_nvenc libx264')
    monkeypatch.setattr(setup.subprocess,'run',run)
    cache=tmp_path/'cache'
    executable=setup.install_archive(archive,cache)
    assert binary.verified_gpu_binary(cache)==str(executable)
    assert list(executable.parent.glob('LICENSE*.txt'))
    assert not (tmp_path/'must-not-extract').exists()
    monkeypatch.setattr(binary,'sys',SimpleNamespace(platform='win32'))
    monkeypatch.delenv('IMAGEIO_FFMPEG_EXE',raising=False)
    monkeypatch.setattr(binary,'verified_gpu_binary',lambda:str(executable))
    binary.ffmpeg_exe.cache_clear()
    try:
        assert binary.ffmpeg_exe()==str(executable)
    finally:binary.ffmpeg_exe.cache_clear()
    original=executable.read_bytes()
    with pytest.raises(RuntimeError,match='preserved'):
        setup.install_archive(archive,cache)
    assert executable.read_bytes()==original
