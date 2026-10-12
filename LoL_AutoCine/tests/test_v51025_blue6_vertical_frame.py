# -*- coding: utf-8 -*-
"""v5.10.25 BLUE normal-third isolated trial and approved-mode regression."""
from __future__ import annotations

import math
from pathlib import Path

from core.camera import CameraPlan, RigInfo
from core.camera_tuning import shot_tuning


def _camera_plan(style, team="ORDER"):
    rig = RigInfo(
        mode="fps", third=True, h=(-0.52, -0.854166260162505),
        rot={"x": 0.0, "y": 37.0, "z": 0.0},
        v=(-7173.99, 1860.48, 4104.70),
        pitch_axis="x", pitch_sign=1.0,
    )
    plan = CameraPlan(
        style=style, team=team, rig=rig, kill_time=750.2475586,
        third_elev=37.0, third_dist=950.0, side_yaw=-12.0,
    )
    config = shot_tuning(team, style)
    plan._live_dist_factor = config["distance"]
    plan._live_angle_bias = config["angles"]
    plan._live_fps_back = config["fps_back"]
    plan._live_blue_geo_look = (team == "ORDER" and style in
                                ("third", "third_cinema", "lolnam_cinema"))
    plan._live_blue_pulled_back = (team == "ORDER" and style == "third")
    plan._camera_axis_safety = True
    return plan


def test_blue6_has_only_isolated_minus_four_pitch_bias():
    target = shot_tuning("BLUE", "third")
    assert target["angles"] == {"x": -4.0}
    assert target["distance"] == 1.10
    plan = _camera_plan("third")
    for t in (747.2475586, 750.2475586, 753.2475586):
        relative = plan.offset_at(t)
        horizontal = math.hypot(relative[0], relative[2])
        geometric_pitch = math.degrees(math.atan2(relative[1], horizontal))
        adjusted = plan.rotation_at(t)
        assert math.isclose(adjusted["x"], geometric_pitch - 4.0, abs_tol=1e-7)
        assert adjusted["z"] == 0.0
        # An angle-only adjustment preserves the position, FOV and side heading.
        previous_position, previous_fov = plan.offset_at(t), plan.fov_at(t)
        plan._live_angle_bias = {}
        unbiased = plan.rotation_at(t)
        assert math.isclose(adjusted["x"] - unbiased["x"], -4.0, abs_tol=1e-7)
        assert adjusted["y"] == unbiased["y"]
        assert plan.offset_at(t) == previous_position
        assert plan.fov_at(t) == previous_fov
        plan._live_angle_bias = target["angles"]


def test_all_other_side_and_mode_tuning_is_identical_to_v51024():
    expected = {
        ("RED", "third"): (1.13, {}),
        ("RED", "third_cinema"): (0.96, {}),
        ("RED", "fps"): (1.0, {}),
        ("RED", "lolnam_cinema"): (1.0, {"x": -3.0, "y": -3.0}),
        ("RED", "geo_aim"): (1.12, {"x": -4.0}),
        ("BLUE", "third_cinema"): (1.08, {}),
        ("BLUE", "fps"): (1.0, {}),
        ("BLUE", "lolnam_cinema"): (1.08, {"x": 2.5}),
        ("BLUE", "geo_aim"): (1.08, {"x": 2.5}),
    }
    for (side, mode), (distance, angles) in expected.items():
        shot = shot_tuning(side, mode)
        assert shot["distance"] == distance
        assert shot["angles"] == angles
    assert shot_tuning("RED", "fps")["fps_back"] == 1.60
    assert shot_tuning("BLUE", "fps")["fps_back"] == 1.38


def test_unchanged_cinematic_blue_modes_keep_their_rotations():
    for mode in ("third_cinema", "lolnam_cinema"):
        plan = _camera_plan(mode)
        for t in (747.2475586, 750.2475586, 753.2475586):
            point = plan.offset_at(t)
            rot = plan.rotation_at(t)
            expected = math.degrees(math.atan2(point[1], math.hypot(point[0], point[2])))
            assert math.isclose(rot["x"] - shot_tuning("BLUE", mode)["angles"].get("x", 0.0),
                                expected, abs_tol=1e-7)
            assert rot["z"] == 0.0


def test_report_and_version_are_updated_but_test_plan_retains_ten_modes():
    root = Path(__file__).resolve().parents[1]
    version = (root / "VERSION.txt").read_text(encoding="utf-8").strip()
    qa_source = (root / "core" / "camera_qa.py").read_text(encoding="utf-8")
    assert version == "5.10.25-test"
    assert '"version": "5.10.25-test"' in qa_source
    import json
    plan = json.loads((root / "qa" / "test_plan.json").read_text(encoding="utf-8"))
    assert plan["camera_modes"] == ["third", "third_cinema", "fps",
                                     "lolnam_cinema", "geo_aim"]
    assert plan["max_zip_mb"] == 500
