"""Resident two-source QA dispatch, fallback, resource lifetime and timing."""
from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import pytest
from core import qa_true_transitions as qa
from core.gpu_qa_transitions import SpatialStage


@pytest.mark.parametrize('style', qa.TRANSITION_PREVIEWS)
def test_shader_keeps_two_gpu_inputs_and_fixed_clock(style):
    stage = SpatialStage(style, .92, .2576, width=320, height=180)
    folder = Path(stage.folder.name)
    try:
        assert stage.graph.count('hwupload') == 2 and stage.graph.count('hwdownload') == 1
        assert 'xfade=' not in stage.graph and 'scale=' not in stage.graph
        assert 'tpad=stop_mode=clone:stop=39' in stage.graph
        assert 'tpad=start_mode=clone:start=40' in stage.graph
        assert 'trim=end_frame=95' in stage.graph and 'setpts=N/(60*TB)' in stage.graph
        assert 'read_only image2d_t first,read_only image2d_t second' in stage.path.read_text()
    finally: stage.close()
    assert not folder.exists()


@pytest.mark.parametrize('failure', [None, 'driver', 'timeout', 'unverified'])
def test_spatial_qa_fallback_keeps_inputs_policy_muted_preview_and_reports(tmp_path, monkeypatch, failure):
    a=tmp_path/'first.mp4'; b=tmp_path/'second.mp4'; a.write_bytes(b'a'); b.write_bytes(b'b')
    dst=tmp_path/'out.mp4'; stages=[]; calls=[]
    monkeypatch.setattr(qa,'get_duration',lambda *a,**k:1)
    monkeypatch.setattr(qa,'detect',lambda:SimpleNamespace(full_gpu_runtime_ok=failure!='unverified',full_probe_reason='unverified'))
    monkeypatch.setattr(qa.gpu_full,'mode',lambda:'full')
    monkeypatch.setattr(qa,'encoder_args',lambda fps,policy:(['-c:v','h264_nvenc','-pix_fmt','yuv420p'] if policy=='gpu' else pytest.fail('policy lost')))
    real=qa.SpatialStage
    def stage(*args,**kw):
        result=real(*args,**kw);stages.append(result);return result
    monkeypatch.setattr(qa,'SpatialStage',stage)
    def render(cmd,**kw):
        calls.append((cmd,kw)); gpu=kw['pipeline_info']['full_gpu_pipeline']
        assert str(a) in cmd and str(b) in cmd and '-an' in cmd
        assert kw['pipeline_info']['output_fps']==60
        if gpu:
            assert '-init_hw_device' in cmd and 'rgba' in cmd
            assert stages[0].path.exists() and kw['gpu_effects']==['spatial_fade']
            if failure=='timeout':raise subprocess.TimeoutExpired(cmd,300)
            if failure=='driver':return SimpleNamespace(returncode=1,stderr='driver refused')
        else:
            assert '-init_hw_device' not in cmd and 'xfade=' in kw['pipeline_info']['filter_graph']
            assert not kw['gpu_effects']
        dst.write_bytes(b'video'*300)
        return SimpleNamespace(returncode=0,args=cmd,encoder_retry_reason=None)
    monkeypatch.setattr(qa,'run_render',render)
    qa.render_true_transition(a,b,dst,'fade',encoder_policy='gpu',width=320,height=180)
    report=json.loads(dst.with_suffix('.render.json').read_text())
    assert report['gpu_effects_confirmed'] is (failure is None)
    assert report['no_audio'] and report['qa_only'] and report['encoder']=='h264_nvenc'
    assert len(calls)==(2 if failure in ('driver','timeout') else 1)
    assert all(not p.path.exists() for p in stages)
    assert a.read_bytes()==b'a' and b.read_bytes()==b'b'
