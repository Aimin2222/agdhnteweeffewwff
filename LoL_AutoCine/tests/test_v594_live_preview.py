"""Regression tests for unsaved keyframe replay and slow Replay API clocks."""
from types import SimpleNamespace

from core.camera_clock import SmoothReplayClock
from core.effects import Template
from legacy_app import App
from ui.scene_project import Shot


def test_unsaved_keyframes_go_to_actual_replay_preview():
    frames = [{'time': -2.0, 'yaw': -8.0, 'zoom': 0.0, 'fov': 0.0},
              {'time': 0.0, 'yaw': 18.0, 'zoom': 10.0, 'fov': -3.0},
              {'time': 2.0, 'yaw': 0.0, 'zoom': 0.0, 'fov': 0.0}]
    saved_tpl = Template(style='third_cinema')
    events = []
    preview_calls = []
    self = SimpleNamespace(
        shot_motion_graph=SimpleNamespace(redraw=lambda: events.append('redraw')),
        _current_scene=lambda: SimpleNamespace(time=173.5),
        _need_lock=lambda: True,
        busy=False,
        _scene_shot_from_ui=lambda: Shot(keyframes=frames),
        current_template=lambda: saved_tpl,
        _run_bg=lambda fn,*args: preview_calls.append((fn,args)),
        _preview_play=lambda *args: None,
        log=events.append,
    )
    App.on_keyframe_preview(self)
    assert len(preview_calls) == 1
    fn,(tpl,kill)=preview_calls[0]
    assert fn is self._preview_play
    assert kill.time == 173.5
    assert tpl.style == 'third_cinema'
    assert len(tpl.scene_keyframes) == 3
    assert tpl.scene_keyframes[1]['yaw']==18.0
    assert getattr(saved_tpl,'scene_keyframes',None) != tpl.scene_keyframes
    assert any('未保存' in msg for msg in events)


def test_slow_api_call_does_not_discard_replay_time():
    c=SmoothReplayClock(12.0)
    assert abs(c.advance(0.105)-12.105)<1e-8
    assert abs(c.advance(0.18)-12.285)<1e-8


def test_no_scene_does_not_start_preview():
    calls=[]
    self = SimpleNamespace(
        shot_motion_graph=SimpleNamespace(redraw=lambda: None),
        _current_scene=lambda: None,
        log=lambda msg:calls.append(msg),
        _need_lock=lambda: (_ for _ in ()).throw(AssertionError('should not request lock')),
    )
    App.on_keyframe_preview(self)
    assert calls and '選択' in calls[0]
