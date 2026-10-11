"""Gallery/comparison pixel work must leave Tk responsive and discard stale work."""
import threading
from types import SimpleNamespace
import numpy as np
from PIL import Image
from tkinter import ttk
from tests.test_v5107_mirror_controls import app
from tests.test_v51010_gallery_responsiveness import pump
from core.effects import Template


def test_gallery_slow_render_leaves_ui_responsive_and_latest_choice_wins(app, monkeypatch):
    from ui import kill_frame_gallery as gallery
    entered, release = threading.Event(), threading.Event()
    main = threading.get_ident()
    requests = []
    def slow(request):
        assert threading.get_ident() != main
        requests.append(request)
        entered.set()
        assert release.wait(3)
        return Image.new('RGBA', (40, 20)), Image.new('RGBA', (770, 232)), ''
    monkeypatch.setattr(gallery, 'render_preview', slow)
    monkeypatch.setattr(gallery, 'render_thumbnails', lambda *args: None)
    original = app.current_template().to_dict()
    win = gallery.open_gallery(app)
    panel = win._kill_gallery
    try:
        pump(app.root, entered.is_set)
        beats = []
        app.root.after(1, lambda: beats.append(True))
        pump(app.root, lambda: bool(beats), timeout=.5)
        assert not hasattr(panel, '_main_photo')
        panel.select('off')
        panel.strength.set(.4)
        panel.glow_enabled.set(False)
        panel.zoom_preview()
        panel._refresh_preview()
        release.set()
        pump(app.root, lambda: hasattr(panel._zoom_window, '_photo'))
        assert requests[-1] == ('off', .4, False)
        assert panel._preview_presented[0] == panel._preview_generation
        assert panel._zoom_window._photo.width() == 770
        assert app.current_template().to_dict() == original
        panel.select('off', apply=True)
        assert app.var_kill_glow_strength.get() == .4
        assert app.var_kill_glow_enabled.get() is False
    finally:
        release.set()
        win.destroy()
    assert panel._preview_worker._closed and panel._stop_event.is_set()
    assert panel._poll_after is None and panel._preview_after is None


def test_gallery_errors_are_visible_and_close_pending_work(app, monkeypatch):
    from ui import kill_frame_gallery as gallery
    monkeypatch.setattr(gallery, 'render_badge', lambda *args: (_ for _ in ()).throw(ValueError('broken badge')))
    monkeypatch.setattr(gallery, 'render_thumbnails', lambda *args: None)
    win = gallery.open_gallery(app)
    panel = win._kill_gallery
    pump(app.root, lambda: 'broken badge' in panel.preview.cget('text'))
    panel._queue_preview()
    win.destroy()
    assert panel._preview_worker._closed and panel._preview_after is None


def test_comparison_frame_and_grade_are_off_tk_and_close_during_render(app, monkeypatch):
    from ui import frame_comparison as comparison
    entered, release = threading.Event(), threading.Event()
    main = threading.get_ident()
    def latest():
        assert threading.get_ident() != main
        entered.set()
        assert release.wait(3)
        return np.zeros((30, 40, 4), dtype=np.uint8)
    source = SimpleNamespace(running=True, latest=latest)
    original = app.current_template().to_dict()
    win = comparison.open_comparison(app.root, source, app.current_template(), with_effects=True)
    try:
        pump(app.root, entered.is_set)
        beats = []
        app.root.after(1, lambda: beats.append(True))
        pump(app.root, lambda: bool(beats), timeout=.5)
        win.destroy()
        assert win._comparison_worker._closed
        assert app.current_template().to_dict() == original
    finally:
        release.set()
        if win.winfo_exists(): win.destroy()


def test_comparison_preserves_bgr_colors_and_reports_missing_or_broken_source():
    from ui.frame_comparison import render_comparison
    raw = np.zeros((30, 40, 4), dtype=np.uint8)
    raw[..., :3] = (19, 45, 201)  # zero alpha from Windows capture must be ignored
    source = SimpleNamespace(running=True, latest=lambda: raw)
    image, error = render_comparison((source, Template().to_dict(), 40, 30, False))
    assert error == '' and image.getpixel((10, 10)) == (201, 45, 19)
    assert image.size == (80, 30)
    assert render_comparison((None, {}, 40, 30, False))[0] is None
    source.latest = lambda: (_ for _ in ()).throw(ValueError('capture stopped'))
    image, error = render_comparison((source, {}, 40, 30, False))
    assert image is None and 'capture stopped' in error


def test_preset_hover_is_500ms_and_cancels_without_mutating_settings(app, monkeypatch):
    from ui import frame_comparison
    button = ttk.Button(app.root)
    button.pack()
    app.root.update()
    scheduled, cancelled, shown = [], [], []
    monkeypatch.setattr(button, 'after', lambda delay, callback: scheduled.append((delay, callback)) or 'hover')
    monkeypatch.setattr(button, 'after_cancel', cancelled.append)
    key = next(iter(app.templates))
    app._bind_preset_hover(button, key)
    before = app.current_template().to_dict()
    button.event_generate('<Enter>')
    assert scheduled[-1][0] == 500
    button.event_generate('<Leave>')
    assert 'hover' in cancelled
    monkeypatch.setattr(frame_comparison, 'open_comparison', lambda *a, **k: shown.append(k) or __import__('tkinter').Toplevel(button))
    button.event_generate('<Enter>')
    scheduled[-1][1]()
    assert shown[-1]['hover']
    button.event_generate('<Leave>')
    assert app.current_template().to_dict() == before
    button.destroy()
