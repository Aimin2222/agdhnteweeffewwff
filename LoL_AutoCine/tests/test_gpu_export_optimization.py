"""Export cadence, buffer ownership and Gaussian math without physical GPU claims."""
from pathlib import Path
from types import SimpleNamespace
import math
import re
import subprocess
import numpy as np
import pytest
from core import effects as fx, recorder
from core.gpu_pipeline import GPUCapabilities
from core.gpu_bloom import _gaussian_table


def neutral(**kwargs):
    return fx.Template(grade='standard',grade_strength=0,vignette=0,grain=0,
                       bars=0,bloom=0,transition='cut',game_audio=False,**kwargs)


@pytest.mark.parametrize('fps', [30,60,144])
def test_real_ffmpeg_selects_exact_output_clock_before_effects(fps):
    graph=fx.build_graph(neutral(fps=fps),1,False,
                         pre_filters=f'fps=fps={fps}:round=near')
    result=subprocess.run([fx.FFMPEG,'-v','error','-f','lavfi','-i',
        'testsrc2=size=64x48:rate=144:duration=1','-filter_complex',graph,
        '-map','[vout]','-t','1','-an','-f','framemd5','-'],
        capture_output=True,text=True,check=True,timeout=20)
    frames=[line for line in result.stdout.splitlines() if line and not line.startswith('#')]
    assert len(frames)==fps
    assert f'#tb 0: 1/{fps}' in result.stdout
    times=[int(line.split(',')[2].strip()) for line in frames]
    assert times==list(range(fps))


def test_export_dispatch_places_fps_before_gpu_upload_and_retains_raw_setting(tmp_path,monkeypatch):
    from core import performance_diagnostics as perf
    src=tmp_path/'in.mp4';src.write_bytes(b'input')
    dst=tmp_path/'out.mp4';seen=[]
    tpl=neutral(fps=60,capture_fps=144,video_effects={'focus_blur':.2})
    caps=GPUCapabilities(gblur_opencl=True,opencl_runtime_ok=True)
    monkeypatch.setattr(fx,'detect_gpu',lambda:caps)
    monkeypatch.setattr(fx,'_colorfulness',lambda _:30)
    monkeypatch.setattr(fx,'encoder_args',lambda *a,**k:['-c:v','libx264','-r','60'])
    def render(cmd,**kwargs):
        seen.append((cmd,kwargs));dst.write_bytes(b'video'*400)
        return SimpleNamespace(returncode=0,stderr='')
    monkeypatch.setattr(perf,'run_render',render)
    fx.apply_effects(src,dst,tpl,1,[])
    cmd,details=seen[0];graph=cmd[cmd.index('-filter_complex')+1]
    assert graph.startswith('[0:v]fps=fps=60:round=near,')
    assert graph.index('fps=') < graph.index('hwupload') < graph.index('colorbalance=')
    assert details['pipeline_info']['effects_fps']==60
    assert details['pipeline_info']['frame_rate_selection']=='before_effects'
    assert tpl.capture_fps==144 and tpl.fps==60


@pytest.mark.parametrize('strided',[False,True])
def test_recording_writes_owned_bgra_buffer_without_an_extra_bytes_copy(tmp_path,strided):
    frame=np.arange(12*16*4,dtype=np.uint8).reshape(12,16,4)
    if strided:frame=frame[:,::-1,:]
    src=SimpleNamespace(frame_count=1,latest=lambda:frame)
    rec=recorder.ClipRecorder(src,tmp_path/'raw.mp4');rec.w=16;rec.h=12
    class Sink:
        def write(self,buffer):
            assert isinstance(buffer,memoryview) and buffer.contiguous
            assert bytes(buffer)==frame.tobytes()
            if not strided:assert buffer.obj is frame
            rec._stop.set()
    rec._proc=SimpleNamespace(stdin=Sink())
    rec._run()
    assert rec.frames==1 and rec.error is None


@pytest.mark.parametrize('sigma',[.115,4.6,11,23])
def test_precomputed_kernel_coefficients_preserve_original_gaussian(sigma):
    source=_gaussian_table('test',sigma)
    weights=[float(v[:-1]) for v in source.split('{',1)[1].split('}',1)[0].split(',')]
    radius=math.ceil(sigma*3)
    original=np.exp(-.5*np.arange(-radius,radius+1,dtype=float)**2/sigma**2)
    original/=original.sum()
    optimized=np.array(list(reversed(weights[1:]))+weights)
    np.testing.assert_allclose(optimized,original,rtol=1e-8,atol=1e-12)
    assert math.isclose(optimized.sum(),1,abs_tol=1e-10)
