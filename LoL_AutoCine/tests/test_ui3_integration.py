"""Candidate 3 trial must retain the comparison app and reveal real Tk tools."""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import urlopen

from ui.audit29_runtime import Audit29Runtime
from ui.audit29_server import UI29Server
from ui.c3_compare import render as render_c3


ROOT = Path(__file__).resolve().parents[1]


def test_ui3_launch_is_provisional_and_keeps_all_comparison_screens():
    with TemporaryDirectory(dir=ROOT / "qa") as folder:
        app = Mock()
        with patch.dict(os.environ, {"AUTOCINE_UI3_LAUNCH": "1"}):
            runtime = Audit29Runtime(app, Path(folder) / "prefs.json")
            assert runtime.screen_id == "T-A-M"
            assert runtime.theme == "system"
        with patch.dict(os.environ, {}, clear=True):
            comparison = Audit29Runtime(app, Path(folder) / "other.json")
            assert comparison.screen_id is None


def test_native_editor_restores_alpha_before_showing_existing_controls():
    # perform() returns a snapshot; use the existing fake App from the UI29
    # regression suite so this verifies the same dispatcher contract.
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_ui29_runtime import App

    with TemporaryDirectory(dir=ROOT / "qa") as folder:
        app = App()
        app.root.attributes = Mock()
        app.root.deiconify = Mock()
        app.root.lift = Mock()
        app.root.withdraw = Mock()
        app._focus_editor_zone = Mock()
        runtime = Audit29Runtime(app, Path(folder) / "prefs.json")
        runtime.perform("native_editor_zone", {"zone": "fx"})
        app._focus_editor_zone.assert_called_once_with("fx")
        app.root.attributes.assert_called_once_with("-alpha", 1.0)
        app.root.deiconify.assert_called_once()
        app.root.lift.assert_called_once()
        runtime.perform("native_legacy_hide")
        app.root.withdraw.assert_called_once()


def test_ui3_bat_and_70_row_matrix_are_packaging_ready():
    bat = (ROOT / "START_AUTOCINE_UI3.bat").read_bytes()
    assert b"\r\n" in bat and b"\n" not in bat.replace(b"\r\n", b"")
    assert b"--ui3" in bat and b"AUTOCINE_UI3_LAUNCH=1" in bat
    with (ROOT / "docs" / "ui3" / "UI3_FEATURE70_CONNECTION_20261027.csv").open(
            encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 70
    assert len({row["id"] for row in rows}) == 70
    assert {row["id"] for row in rows if row["ui3_access"] == "UNIMPLEMENTED"} == {
        "ENGAGE", "BESTSHOT"}
    assert all(row["live_lol_test"] == "NOT_RUN" for row in rows)


def test_c3_views_reuse_app_and_are_gated_from_seven_candidate_exe():
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_ui29_runtime import App

    for variant in ("p", "s"):
        html = render_c3(variant, "test-token")
        assert 'data-ui="replay-target"' in html
        assert 'data-ui="preview"' in html
        assert 'data-ui="scene-list"' in html
        assert 'data-ui="editor"' in html
        assert 'data-ui="mini-timeline"' in html
        assert 'data-trim="pre"' in html and 'data-trim="post"' in html
        assert 'data-tab="test"' in html
        assert 'data-route="/ui/T-A-M"' in html
    with TemporaryDirectory(dir=ROOT / "qa") as folder:
        app = App()
        with patch.dict(os.environ, {"AUTOCINE_UI3_LAUNCH": "1"}):
            server = UI29Server(app, Path(folder) / "prefs.json")
            base = f"http://127.0.0.1:{server.http.server_port}"
            try:
                for variant in ("p", "s"):
                    with urlopen(f"{base}/ui3/{variant}?token={server.token}") as response:
                        assert response.status == 200
                        assert f'data-variant="{variant}"' in response.read().decode("utf-8")
                server.runtime.perform("camera_number", {"key": "third_dist", "value": 930})
                assert app.sl["third_dist"].get() == 930
                assert server.runtime.screen_id == "T-A-M"
            finally:
                server.close()
        with patch.dict(os.environ, {"AUTOCINE_UI3_LAUNCH": "0"}):
            server = UI29Server(app, Path(folder) / "other.json")
            try:
                with __import__("pytest").raises(HTTPError) as denied:
                    urlopen(f"http://127.0.0.1:{server.http.server_port}/ui3/p?token={server.token}")
                assert denied.value.code == 404
            finally:
                server.close()


def test_c3_camera_draft_validates_before_changing_existing_values():
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_ui29_runtime import App

    app = App()
    runtime = Audit29Runtime(app, ROOT / "qa" / "nonexistent-ui3-test-prefs.json")
    before = (app.var_camera_control_mode.get(), app.var_camera_side.get(),
              app.var_style.get(), app.sl["third_dist"].get())
    with __import__("pytest").raises(ValueError):
        runtime.perform("ui3_camera_batch", {"mode": "manual", "side": "BLUE",
                                              "style": "third", "values": {"third_dist": 9999}})
    assert before == (app.var_camera_control_mode.get(), app.var_camera_side.get(),
                      app.var_style.get(), app.sl["third_dist"].get())
    runtime.perform("ui3_camera_batch", {"mode": "manual", "side": "BLUE",
                                         "style": "third", "values": {"third_dist": 960}})
    assert app.sl["third_dist"].get() == 960


def test_c3_trim_uses_existing_app_values_and_rejects_invalid_seconds():
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_ui29_runtime import App, Variable

    app = App()
    app.var_pre, app.var_post = Variable(4.0), Variable(3.0)
    runtime = Audit29Runtime(app, ROOT / "qa" / "nonexistent-ui3-trim-prefs.json")
    runtime.perform("trim", {"key": "pre", "value": 5.5})
    runtime.perform("trim", {"key": "post", "value": 4.0})
    assert runtime.snapshot()["trim"] == {"pre": 5.5, "post": 4.0}
    with __import__("pytest").raises(ValueError):
        runtime.perform("trim", {"key": "pre", "value": 30})
    assert app.var_pre.get() == 5.5


def test_c3_acceptance_keeps_all_106_cases_and_no_unverified_feature_pass():
    result = json.loads((ROOT / "qa" / "c3_acceptance_20261027" /
                         "UI_ACCEPTANCE_RESULTS_106.json").read_text(encoding="utf-8"))
    rows = result["results"]
    assert len(rows) == result["total"] == 106
    assert len({row["id"] for row in rows}) == 106
    assert all(row["status"] in {"PASS", "FAIL", "REVIEW", "NOT_RUN"} for row in rows)
    assert all(row["status"] == "NOT_RUN" for row in rows if row["id"].startswith("FN-"))
    assert all(row["evidence"] for row in rows if row["status"] == "PASS")


def test_c3_suggested_changes_only_three_values_and_undo_respects_custom_edits():
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_ui29_runtime import App

    app = App()
    app._edit_keyframes = [{"time": 0, "yaw": 10, "zoom": 2, "fov": 0}]
    runtime = Audit29Runtime(app, ROOT / "qa" / "nonexistent-ui3-suggested-prefs.json")
    old = (app.var_camera_control_mode.get(), app.var_style.get(),
           app.var_work_strength.get())
    runtime.perform("ui3_suggested_apply")
    assert runtime.snapshot()["ui3_suggested"]["can_undo"] is True
    assert app._edit_keyframes == [{"time": 0, "yaw": 10, "zoom": 2, "fov": 0}]
    runtime.perform("ui3_suggested_apply")
    runtime.perform("ui3_suggested_undo")
    assert old == (app.var_camera_control_mode.get(), app.var_style.get(),
                   app.var_work_strength.get())
    runtime.perform("ui3_suggested_apply")
    app.sl["third_dist"].set(955)
    assert runtime.snapshot()["ui3_suggested"]["state"] == "custom"
    with __import__("pytest").raises(ValueError):
        runtime.perform("ui3_suggested_undo")
    assert app.sl["third_dist"].get() == 955
    app._edit_keyframes.append({"time": 1, "yaw": 0, "zoom": 0, "fov": 0})
    assert runtime.snapshot()["ui3_suggested"]["can_undo"] is False
