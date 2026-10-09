"""Preserve legacy camera behavior and map slow-motion events onto real video time."""
from dataclasses import fields
from types import SimpleNamespace
import pytest
from core.effects import Template
from core.camera import CameraPlan
from core.jobs import _recording_event_observer
from core.kill_icons import with_badge


def test_png_frame_rate_cannot_shorten_gameplay_or_audio():
    graph = with_badge('null[vout]', 1, [(1,1.4)], duration=3)
    assert 'shortest=0:eof_action=repeat' in graph


def test_v598_template_positions_are_preserved():
    previous = Template(smart_highlight_enabled=True, highlight_pulse=.7, montage_fx='dark')
    new = {'kill_icon_style', 'kill_icon_position', 'kill_icon_scale', 'kill_icon_duration',
           'kill_icon_opacity', 'smart_composition', 'smart_montage'}
    values = [getattr(previous, f.name) for f in fields(Template) if f.name not in new]
    restored = Template(*values)
    assert restored.smart_highlight_enabled and restored.highlight_pulse == .7
    assert restored.montage_fx == 'dark' and restored.kill_icon_style == 'off'
    assert not restored.smart_composition and not restored.smart_montage


def test_legacy_slow_motion_is_not_clamped_by_new_smart_floor():
    legacy = CameraPlan(style='lolnam_cinema', intensity=2, kill_time=10)
    assert legacy.speed_at(10) == pytest.approx(.4)
    legacy.intensity = 3
    assert legacy.speed_at(10) == pytest.approx(.35)
    legacy.smart_impact = .7
    assert legacy.speed_at(10) == pytest.approx(.4)


def test_camera_previous_positions_are_preserved():
    old = CameraPlan(height=185, sel_name='Hero', scene_keyframes=({'time': 0},))
    values = [getattr(old, f.name) for f in fields(CameraPlan)
              if f.name not in {'smart_composition', 'smart_impact'}]
    restored = CameraPlan(*values)
    assert restored.height == 185 and restored.sel_name == 'Hero'
    assert restored.scene_keyframes == old.scene_keyframes and not restored.smart_composition


def test_recording_time_interpolation_tracks_slow_and_variable_playback():
    events=[]
    observe=_recording_event_observer([SimpleNamespace(time=12),SimpleNamespace(time=11)],10,100,events)
    observe(10.5,101)
    observe(11.5,103)
    observe(12.5,104)
    assert [a for a,b in events] == pytest.approx([2,3.5])
    assert all(b-a == pytest.approx(.42) for a,b in events)
    observe(12.5,105)
    observe(11,106)
    assert len(events) == 2
