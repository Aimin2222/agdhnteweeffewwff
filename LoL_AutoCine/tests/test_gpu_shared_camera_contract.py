"""Regression checks for the reviewed UI-to-camera bridge, with no GPU requirement."""
from dataclasses import fields

import pytest

from core.camera import CameraPlan
from core.effects import Template
from core.jobs import _setup_clip
from core.players import parse_players
from core.replay_api import ReplayAPI
from core.scanner import Kill
from tests.mock_replay_server import start_mock


@pytest.mark.parametrize("style", ["follow", "cinema", "third", "third_cinema", "lolnam_cinema"])
@pytest.mark.parametrize("fov", [20.0, 120.0])
def test_empty_keyframes_preserve_legacy_fov(style, fov):
    plan = CameraPlan(style=style, base_fov=fov, kill_time=0)
    assert plan.fov_at(30) == fov


def test_keyframes_do_not_change_non_third_camera():
    plan = CameraPlan(style="follow", base_fov=20,
                      scene_keyframes=({'time': 0, 'yaw': 30, 'zoom': 20, 'fov': 15},))
    assert plan.keyframe_values(0) == (0, 0, 0)
    assert plan.fov_at(0) == 20


def test_legacy_camera_positional_arguments_are_preserved():
    plan = CameraPlan("third", .6, 100, (100,), 58, .8, None, 28, 950,
                      15, 12, 3, "smooth", 180, "Hero")
    assert plan.height == 180 and plan.sel_name == "Hero"
    assert plan.scene_keyframes == ()


def test_legacy_template_positional_arguments_and_new_default_isolation():
    legacy = Template(fog_enabled=True, dof_enabled=True, template_origin="custom")
    old_values = [getattr(legacy, field.name) for field in fields(Template)
                  if field.name not in {"scene_keyframes", "montage_fx", "smart_highlight_enabled",
                                        "smart_highlight_style", "highlight_pulse"} | {'kill_icon_style', 'kill_icon_position', 'kill_icon_scale', 'kill_icon_duration', 'kill_icon_opacity', 'smart_composition', 'smart_montage', 'kill_icon_players'} | {'encoder_policy', 'kill_frame_color', 'kill_glow_color', 'kill_glow_enabled', 'kill_glow_strength', 'kill_frame_width', 'kill_mark_style'}]
    restored = Template(*old_values)
    assert restored.fog_enabled and restored.dof_enabled
    assert restored.template_origin == "custom" and restored.scene_keyframes == []
    restored.scene_keyframes.append({'time': 0})
    assert Template().scene_keyframes == []


def test_jobs_forward_keyframes_without_mutating_template():
    state, base, down = start_mock(length=60)
    try:
        api = ReplayAPI(base)
        player = parse_players(api.playerlist())[0]
        frames = [{'time': 0.0, 'yaw': 20.0, 'zoom': 10.0, 'fov': -4.0}]
        template = Template(style="lolnam_cinema", scene_keyframes=frames)
        plan, rig = _setup_clip(api, player, template, 9,
                                [Kill(1, 10, player.name, "Target", [])], lambda _: None)
        assert plan.scene_keyframes == tuple(frames)
        assert plan.keyframe_values(10) == (20, 10, -4)
        assert template.scene_keyframes == frames
        assert rig.third
    finally:
        down()
