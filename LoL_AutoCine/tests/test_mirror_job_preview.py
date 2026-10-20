"""Mirror display must share recording capture without owning/stopping it."""
from types import SimpleNamespace
import queue
import time
from unittest.mock import Mock
import numpy as np
from PIL import Image
import legacy_app as app_module
from ui.live_preview import LatestPreview, PresentationRate, preview_delay_ms


def await_result(worker,key):
    end=time.monotonic()+3
    while time.monotonic()<end:
        result=worker.result(key)
        if result is not None:return result[1]
        time.sleep(.01)
    raise AssertionError('preview worker did not deliver a frame')


def test_worker_reports_failure_uses_raw_fallback_and_recovers():
    errors=[]
    def render(value):
        if value=='bad':raise RuntimeError('effect render failed')
        return value
    worker=LatestPreview(render,fallback=lambda _: 'raw frame',on_error=errors.append)
    try:
        worker.submit('a','bad')
        assert await_result(worker,'a')=='raw frame'
        assert errors==['RuntimeError: effect render failed']
        worker.submit('b','good')
        assert await_result(worker,'b')=='good'
    finally:worker.close()


def test_job_owned_source_is_announced_to_ui_without_second_capture(monkeypatch):
    source=SimpleNamespace(running=False,start=Mock())
    monkeypatch.setattr(app_module,'WGCWindowSource',lambda:source)
    monkeypatch.setattr(app_module,'FAKE_CAPTURE',False)
    app=SimpleNamespace(_mirror=SimpleNamespace(pending=False),source=None,q=queue.Queue())
    actual,owned=app_module.App._ensure_source(app)
    assert actual is source and owned
    source.start.assert_called_once()
    messages=list(app.q.queue)
    assert ('capture_preview_ready',source) in messages


def test_mirror_start_during_job_explains_wait_and_does_not_start_wgc():
    logs=[]
    app=SimpleNamespace(_closing=False,busy=True,log=logs.append,var_mirror=Mock())
    app_module.App.on_mirror_start(app)
    assert app._capture_preview_enabled and logs
    app.var_mirror.set.assert_called_once_with(True)


def test_mirror_stop_during_job_hides_display_without_stopping_capture():
    source=SimpleNamespace(running=True)
    mirror=Mock()
    app=SimpleNamespace(busy=True,log=Mock(),_mirror=mirror,source=source,
                        canvas=Mock(),var_mirror=Mock(),_mirror_present_rate=PresentationRate())
    app_module.App.on_mirror_stop(app)
    assert app.source is source and source.running
    assert not app._capture_preview_enabled
    mirror.stop.assert_not_called()


def test_effect_failure_fallback_keeps_captured_colors(monkeypatch):
    from core.effects import Template
    frame=np.zeros((90,160,4),np.uint8);frame[:,:,2]=220
    source=SimpleNamespace(latest=lambda:frame)
    request=(source,160,90,Template(),'',0.,160,90)
    monkeypatch.setattr(app_module,'apply_video_effect_preview',Mock(side_effect=RuntimeError('bad effect')))
    worker=LatestPreview(app_module._render_live_preview,
        fallback=lambda r:app_module._render_live_preview((*r[:3],None,'',0.,*r[6:8])))
    try:
        worker.submit('colors',request)
        image,_=await_result(worker,'colors')
        assert image.getpixel((80,45))==(220,0,0)
    finally:worker.close()


def test_work_frame_can_preview_without_expensive_video_fx(monkeypatch):
    from core.effects import Template
    from ui import director_work_controls
    frame=np.zeros((90,160,4),np.uint8);frame[:,:,2]=220
    source=SimpleNamespace(latest=lambda:frame)
    template=Template(work_kill_frame_id='083/a_simple_main')
    monkeypatch.setattr(app_module,'apply_video_effect_preview',
                        Mock(side_effect=AssertionError('video FX must remain off')))
    called=[]
    def work_overlay(image, current, context):
        called.append((current.work_kill_frame_id, context))
        image.putpixel((80,45),(0,220,0))
        return image
    monkeypatch.setattr(director_work_controls,'composite_mirror',work_overlay)
    result,_=app_module._render_live_preview(
        (source,160,90,template,'',0.,160,90,('replay',[],[]),False))
    assert result.getpixel((80,45))==(0,220,0)
    assert called==[('083/a_simple_main',('replay',[],[]))]


def test_unexpected_ui_preview_error_is_logged_and_rescheduled(monkeypatch):
    writes=[]
    monkeypatch.setattr(app_module,'_diag_write',lambda *args:writes.append(args))
    root=SimpleNamespace(after=Mock())
    canvas=SimpleNamespace(winfo_width=Mock(side_effect=RuntimeError('temporary canvas issue')))
    app=SimpleNamespace(_closing=False,var_live=SimpleNamespace(get=lambda:False),busy=False,
                        _preview_input_at=0.,canvas=canvas,root=root,log=Mock(),_preview_tick=Mock())
    app_module.App._preview_tick(app)
    app.log.assert_called_once()
    assert 'MIRROR_PREVIEW_ERROR' in writes[0][1]
    assert root.after.call_args.args[1] is app._preview_tick
    assert 1 <= root.after.call_args.args[0] <= 33


def test_mirror_pacer_targets_selected_rate_without_adding_tk_transfer_time():
    assert preview_delay_ms('60 Hz', editing=False, gpu_active=True,
                            preview_fx=True, elapsed_ms=8) == 9
    assert preview_delay_ms('144 Hz', editing=False, gpu_active=True,
                            preview_fx=True, elapsed_ms=3) == 4
    assert preview_delay_ms('60 Hz', editing=True, gpu_active=True,
                            preview_fx=True, elapsed_ms=8) == 92
    assert preview_delay_ms('60 Hz', editing=False, gpu_active=False,
                            preview_fx=True, elapsed_ms=8) == 59


def test_presented_fps_counts_distinct_tk_uploads_and_resets():
    rate = PresentationRate(window_seconds=3)
    for index in range(61):
        rate.record(index / 30)
    assert round(rate.fps(), 1) == 30.0
    assert rate.stalled(3.1)
    assert rate.fps(3.1) == 0
    rate.reset()
    assert rate.fps() == 0
