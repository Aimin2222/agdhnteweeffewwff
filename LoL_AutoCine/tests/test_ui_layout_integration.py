"""A/B layouts reuse one editor state and keep the mirror mounted."""
import json
import tkinter as tk

import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    import legacy_app

    monkeypatch.setattr(legacy_app, "SETTINGS", tmp_path / "settings.json")
    root = tk.Tk()
    instance = legacy_app.App(root)
    yield instance
    instance._live_preview.close()
    root.destroy()


def test_comparison_layout_preserves_camera_effect_and_preview(app):
    preview = app.canvas
    camera = app.var_style
    side = app.var_camera_side
    frame = app.var_work_frame
    app.var_style.set("三人称シネマ")
    app.var_ui_layout.set("テスト配置 B")
    app._apply_ui_layout()
    app.root.update_idletasks()
    assert app.right_scroll.winfo_manager() == "pack"
    assert app.right_scroll.pack_info()["side"] == "left"
    assert app._ui_test_inspector.winfo_manager() == "pack"
    assert app.canvas is preview
    assert app.var_style is camera and app.var_camera_side is side
    assert app.var_work_frame is frame
    assert app.var_style.get() == "三人称シネマ"
    app.var_ui_layout.set("現行配置 A")
    app._apply_ui_layout()
    assert app.right_scroll.pack_info()["side"] == "right"
    assert not app._ui_test_inspector.winfo_manager()
    assert app.canvas is preview


def test_layout_choice_is_presentation_only_and_saved(app):
    import legacy_app

    app.var_ui_layout.set("テスト配置 B")
    app._apply_ui_layout()
    data = json.loads(legacy_app.SETTINGS.read_text(encoding="utf-8"))
    assert data["ui_layout"] == "テスト配置 B"
    assert app.current_template().fps == 60


def test_small_window_keeps_preview_and_scrollable_panels(app):
    app.root.geometry("1024x680")
    app.var_ui_layout.set("テスト配置 B")
    app._apply_ui_layout(save=False)
    app.root.update_idletasks()
    assert app.canvas.winfo_manager() == "pack"
    assert app.left_scroll.canvas.winfo_manager() == "pack"
    assert app.right_scroll.canvas.winfo_manager() == "pack"
    assert app.root.minsize() == (1024, 680)


def test_event_timeline_selects_the_same_scene_and_respects_checkmarks(app):
    from core.scanner import Kill

    app.kills = [Kill(1, 60, "A", "X", [], role="kill"),
                 Kill(2, 120, "A", "Y", [], role="assist")]
    app.checked_kills = {1}
    app._fill_kills()
    timeline = app.kill_event_timeline
    assert len(timeline.markers) == 2
    assert timeline.checked == {1}
    timeline._select(type("Click", (), {"x": timeline.markers[1][0]})())
    assert app.lb_kills.curselection() == (1,)
