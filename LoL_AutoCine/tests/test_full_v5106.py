# -*- coding: utf-8 -*-
"""Regression checks for the v5.10.6 user-reported issues."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from core.mirror_restore import restore_mirror_camera
from core.camera import CameraPlan, RigInfo, side_yaw_for
from core.kill_icons import MARK_STYLES, make_badge
from core.players import Player
from core.scanner import scan_kills


class FakeMirrorAPI:
    def __init__(self, fail=False):
        self.commands = []
        self.fail = fail

    def set_playback(self, **kwargs):
        self.commands.append(("playback", kwargs))

    def set_render(self, **kwargs):
        self.commands.append(("render", kwargs))
        if self.fail:
            from core.replay_api import ReplayApiError
            raise ReplayApiError("unavailable")


@pytest.fixture
def blue_player():
    return Player(0, "Tester", "Tester#AA", "Tester", "Lee Sin", "ORDER", selection_name="LeeSin")


def test_safe_mirror_reset_uses_attached_top_camera(blue_player):
    api = FakeMirrorAPI()
    assert restore_mirror_camera(api, blue_player, 70)
    render = api.commands[-1][1]
    assert render["cameraMode"] == "top"
    assert render["cameraAttached"] is True
    assert render["selectionName"] == "LeeSin"
    assert render["selectionOffset"] == {"x": 0, "y": 0, "z": 0}
    assert render["fieldOfView"] == 70
    assert api.commands[0][1]["paused"] is True


def test_mirror_reset_failure_is_not_a_capture_error(blue_player):
    assert restore_mirror_camera(FakeMirrorAPI(fail=True), blue_player) is False


def test_red_third_person_look_and_position_both_reverse():
    rig = RigInfo(mode="fps", third=True, h=(1.0, 0.0), pitch_axis="x",
                  pitch_sign=-1.0, rot={"x": 0.0, "y": 0.0, "z": 17.0})
    blue = CameraPlan(style="third", rig=rig, third_dist=1000, third_elev=34,
                      side_yaw=side_yaw_for("ORDER"))
    red = CameraPlan(style="third", rig=rig, third_dist=1000, third_elev=34,
                     side_yaw=side_yaw_for("CHAOS"))
    a, b = blue.offset_at(0.0), red.offset_at(0.0)
    assert a[0] == pytest.approx(-b[0])
    assert a[2] == pytest.approx(-b[2])
    assert a[1] == pytest.approx(b[1])
    rot_a, rot_b = blue.rotation_at(0.0), red.rotation_at(0.0)
    assert abs(rot_a["z"] - rot_b["z"]) == pytest.approx(180.0)


def test_center_mark_can_be_hidden(tmp_path):
    from PIL import Image
    assert "none" in MARK_STYLES
    out = tmp_path / "no_center.png"
    make_badge(out, "cinema", killer_icon=None, victim_icon=None,
               mark_style="none", glow_enabled=False)
    with Image.open(out) as im:
        # Center transparent, portraits may still have decorative borders.
        assert im.convert("RGBA").getpixel((192, 56))[3] == 0


class FakeReplay:
    def __init__(self):
        self.events_value = [
            dict(EventID=1, EventName="ChampionKill", EventTime=1.5,
                 KillerName="Tester", VictimName="Opponent", Assisters=[]),
            dict(EventID=2, EventName="ChampionKill", EventTime=2.5,
                 KillerName="Friend", VictimName="Opponent", Assisters=["Tester"]),
        ]
        self.seek_calls = []
        self.posts = []

    def playback(self):
        return {"length": 4.0, "time": 4.0}

    def set_playback(self, **kwargs):
        self.posts.append(kwargs)

    def seek(self, t):
        self.seek_calls.append(t)

    def events(self):
        return list(self.events_value)


@pytest.mark.parametrize("mode,roles", [
    ("kill", ["kill"]),
    ("assist", ["assist"]),
    ("both", ["kill", "assist"]),
])
def test_scan_can_return_assists(monkeypatch, blue_player, mode, roles):
    import core.scanner as scanner
    monkeypatch.setattr(scanner.time, "sleep", lambda _: None)
    found = scan_kills(FakeReplay(), blue_player, event_mode=mode)
    assert [k.role for k in found.kills] == roles


def test_ui_forwards_scanned_mode_and_installs_hover():
    source = (Path(__file__).resolve().parents[1] / "legacy_app.py").read_text(encoding="utf-8")
    assert "self._run_bg(self._scan, self.var_event_mode.get())" in source
    assert "need_rescan = getattr(self, \"_last_scan_mode\", event_mode) != event_mode" in source
    assert "HoverHelp(help_button," in source
