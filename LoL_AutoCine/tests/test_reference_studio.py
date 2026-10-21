"""The comparison presentation must not fork project or camera state."""
from pathlib import Path
import tkinter as tk

import pytest

import legacy_app
from core.camera import CAMERA_SIDE_CHOICES
from ui.layout_variants import LAYOUT_NAMES
from ui.reference_studio import ReferenceStudio
from core.scanner import Kill


def test_nine_reference_layouts_share_controller_and_fit_small_window(tmp_path, monkeypatch):
    monkeypatch.setattr(legacy_app, "SETTINGS", Path(tmp_path) / "settings.json")
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("interactive Tk display unavailable")
    app = legacy_app.App(root)
    studio = ReferenceStudio(app)
    try:
        app.var_camera_side.set(CAMERA_SIDE_CHOICES["red"])
        app.var_pre.set(6.5)
        app.var_work_frame.set("test/shared-id")
        app.kills = [Kill(1, 60, "A", "X", [], role="kill")]
        app.checked_kills = {0}
        app._fill_kills()
        app.lb_kills.selection_set(0)
        for name in LAYOUT_NAMES:
            app.var_ui_layout.set(name)
            studio._change_layout()
            root.update()
            assert app.var_camera_side.get() == CAMERA_SIDE_CHOICES["red"]
            assert app.var_pre.get() == 6.5
            assert app.var_work_frame.get() == "test/shared-id"
            assert app.checked_kills == {0}
            assert app.lb_kills.curselection() == (0,)
            assert app.canvas.winfo_toplevel() is studio.window
        studio.window.geometry("1366x768+0+0")
        root.update()
        assert studio.timeline.winfo_height() >= 100
        assert app.canvas.winfo_height() >= 250
        studio._offline_reference()
        assert app.canvas.find_withtag("offline_reference")
        app.var_mirror.set(True)
        studio._offline_reference()
        assert not app.canvas.find_withtag("offline_reference")
    finally:
        app._live_preview.close()
        studio.window.destroy()
        root.destroy()
