"""Large mirror presentation must not resize pixels on Tk or resnapshot unchanged controls."""
from types import SimpleNamespace
import threading
import time
import tkinter as tk

import numpy as np
from PIL import Image
import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    import legacy_app
    monkeypatch.setattr(legacy_app, 'SETTINGS', tmp_path/'settings.json')
    root = tk.Tk()
    instance = legacy_app.App(root)
    instance.source = SimpleNamespace(running=True, latest=lambda: np.zeros((1080, 1920, 4), dtype=np.uint8))
    yield instance
    instance._live_preview.close()
    root.destroy()


def test_cached_snapshot_refreshes_all_changed_settings(app, monkeypatch):
    calls = []
    original = app.current_template
    def template():
        calls.append(True)
        return original()
    monkeypatch.setattr(app, 'current_template', template)
    first, key = app._preview_template_snapshot()
    assert app._preview_template_snapshot()[0] is first
    assert len(calls) == 1
    app.sl['temperature'].set(.7)
    app.effect_vars['mirror'].set(True)
    app.var_tr.set('カット')
    second, new_key = app._preview_template_snapshot()
    assert second.temperature == .7 and second.video_effects['mirror'] > 0
    assert first.temperature != second.temperature and key != new_key
    assert len(calls) == 2


def test_full_resize_is_done_before_tk_upload_and_items_are_reused(app, monkeypatch):
    import legacy_app
    app.var_live.set(False)
    cw, ch = 1600, 900
    monkeypatch.setattr(app.canvas, 'winfo_width', lambda: cw)
    monkeypatch.setattr(app.canvas, 'winfo_height', lambda: ch)
    app._preview_input()
    app._preview_tick()
    key = app._live_preview._key
    deadline = time.monotonic()+3
    while app._live_preview.result(key) is None and time.monotonic() < deadline:
        time.sleep(.01)
    assert app._live_preview.result(key) is not None
    image, original = app._live_preview.result(key)[1]
    assert image.size == (cw, ch)
    assert original.shape[:2] == (360, 640)
    main = threading.get_ident()
    resize = Image.Image.resize
    def checked_resize(*args, **kw):
        assert threading.get_ident() != main, 'UI thread performed a pixel resize'
        return resize(*args, **kw)
    monkeypatch.setattr(Image.Image, 'resize', checked_resize)
    app._preview_tick()
    items = app.canvas.find_all()
    assert len(items) == 2
    deadline = time.monotonic()+3
    old_result = app._preview_presented
    while app._live_preview.result(key) is old_result and time.monotonic() < deadline:
        time.sleep(.01)
    app._preview_tick()
    assert app.canvas.find_all() == items
    assert app._photo.width() == cw


def test_raw_decode_ignores_zero_alpha_and_keeps_bgr_colors():
    import legacy_app
    frame = np.zeros((108, 192, 4), dtype=np.uint8)
    frame[..., 0] = 19
    frame[..., 1] = 45
    frame[..., 2] = 201
    source = SimpleNamespace(latest=lambda: frame)
    image, original = legacy_app._render_live_preview((source, 96, 54, None, '', 0, 192, 108))
    assert image.getpixel((30, 30)) == (201, 45, 19)
    assert tuple(original[20, 20]) == (201, 45, 19)


def test_scan_passes_the_ui_selected_event_mode(app, monkeypatch):
    app.locked = object()
    app.players = [app.locked]
    app.var_event_mode.set('キル＋アシスト')
    requests = []
    monkeypatch.setattr(app, '_run_bg', lambda *args: requests.append(args))
    app.on_scan()
    assert requests[0][1] == 'キル＋アシスト'


def test_editor_events_slow_only_mirror_and_resume(app, monkeypatch):
    app.var_live.set(False)
    scheduled = []
    monkeypatch.setattr(app.root, 'after', lambda delay, fn: scheduled.append(delay))
    app._preview_input()
    app._preview_tick()
    assert scheduled[-1] == 167
    app._preview_input_at -= 1
    app._preview_tick()
    assert scheduled[-1] == 50
    assert app.current_template().fps == 60


def test_notebook_wheel_marks_input_before_native_binding_is_blocked(app):
    app.var_edit_mode.set('advanced')
    app._apply_edit_mode(log=False)
    app.var_editor_zone.set('color')
    app._apply_editor_zone()
    app.root.update()
    notebook = app._editor_advanced_tabs
    before = notebook.select()
    app._preview_input_at = 0
    notebook.event_generate('<MouseWheel>', delta=-120)
    assert app._preview_input_at > 0
    assert notebook.select() == before
