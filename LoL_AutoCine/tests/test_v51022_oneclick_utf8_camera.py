# -*- coding: utf-8 -*-
"""Windows/LoL QA entry and per-camera isolation regression tests."""
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.camera_tuning import shot_tuning
from tools.check_text_encoding import audit


def test_red2_red4_blue7_blue9_approved_camera_profiles_untouched():
    assert shot_tuning("RED", "third_cinema")["angles"] == {}
    assert shot_tuning("RED", "third_cinema")["distance"] == .96
    assert shot_tuning("RED", "lolnam_cinema")["distance"] == 1.0
    assert shot_tuning("RED", "lolnam_cinema")["angles"] == {"x": -3.0, "y": -3.0}
    assert shot_tuning("ORDER", "third_cinema")["angles"] == {}
    assert shot_tuning("ORDER", "lolnam_cinema")["distance"] == 1.0


def test_red1_and_fps_and_blue8_are_independent_tuning():
    assert shot_tuning("CHAOS", "third")["distance"] > 1.0
    assert shot_tuning("CHAOS", "fps")["fps_back"] > 1.4
    assert shot_tuning("ORDER", "fps")["fps_back"] > 1.1
    assert shot_tuning("CHAOS", "geo_aim")["distance"] > 1.0
    assert shot_tuning("ORDER", "fps")["angles"] == {}
    assert shot_tuning("ORDER", "geo_aim")["fps_back"] == 1.0


def test_bat_sources_only_have_ascii():
    root = Path(__file__).resolve().parents[1]
    for p in root.glob("*.bat"):
        assert p.read_bytes().isascii(), f"cmd.exe encoding risk: {p.name}"


def test_encoding_audit_detects_invalid_utf8_and_legacy_batch(tmp_path):
    script = tmp_path / "notes.txt"
    script.write_bytes(b"valid ascii")
    assert audit(tmp_path) == []
    script.write_bytes(b"\x82\xa0")
    assert any("UTF-8" in message for message in audit(tmp_path))
    script.unlink()
    bat = tmp_path / "RUN.bat"
    bat.write_text("echo 日本語", encoding="utf-8")
    assert any("ASCII-only" in message for message in audit(tmp_path))


def test_one_click_qa_scans_from_unconnected_state(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        sequence = []
        app.players = []
        app._match_scan_cache = None
        app.stop_ev.clear()
        def fake_connect():
            sequence.append("connect")
            app.players = [SimpleNamespace(team="ORDER")]
        def fake_scan(mode):
            sequence.append("scan:" + mode)
            app._match_scan_cache = SimpleNamespace(
                complete=True, events=[SimpleNamespace(time=22.0)])
        app._connect = fake_connect
        app._scan = fake_scan
        app._record_camera_qa = lambda *args: sequence.append("record")
        app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
        assert sequence == ["connect", "scan:キル", "record"]
    finally:
        root.destroy()


def test_one_click_qa_reuses_existing_full_scan(monkeypatch):
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        app.players = [SimpleNamespace(team="ORDER")]
        app._match_scan_cache = SimpleNamespace(
            complete=True, events=[SimpleNamespace(time=22.0)])
        app._scan = lambda *a: pytest.fail("Do not rescan completed match")
        calls = []
        app._record_camera_qa = lambda *args: calls.append(args)
        app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
        assert len(calls) == 1
    finally:
        root.destroy()


def test_one_click_no_players_fails_without_capture():
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app=App(root)
        app.players = []
        app._match_scan_cache = None
        app.stop_ev.clear()
        app._connect = lambda: None
        app._record_camera_qa = lambda *args: pytest.fail("Do not record")
        with pytest.raises(RuntimeError, match="接続できません"):
            app._run_one_click_camera_qa(object(), Path("/tmp/qa"))
    finally:
        root.destroy()
