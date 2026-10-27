"""Candidate 3 trial must retain the comparison app and reveal real Tk tools."""
from __future__ import annotations

import csv
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from ui.audit29_runtime import Audit29Runtime


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
