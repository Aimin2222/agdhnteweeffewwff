"""Real-scene comparison must not block Tk or reuse scenes after a rescan."""
import threading
import time
from types import SimpleNamespace
import tkinter as tk

from PIL import Image
import pytest

from tests.test_v5107_mirror_controls import app


def pump(root, done, timeout=4):
    deadline = time.monotonic() + timeout
    while not done() and time.monotonic() < deadline:
        root.update()
        time.sleep(.005)
    assert done()


def test_native_quality_is_opt_in_and_does_not_change_export(app, monkeypatch):
    assert app.var_preview_quality.get() == '操作優先'
    app.var_live.set(False)
    app.var_preview_quality.set('表示サイズで確認')
    monkeypatch.setattr(app.canvas, 'winfo_width', lambda: 1600)
    monkeypatch.setattr(app.canvas, 'winfo_height', lambda: 900)
    app._preview_input()
    app._preview_tick()
    key = app._live_preview._key
    pump(app.root, lambda: app._live_preview.result(key) is not None)
    image, original = app._live_preview.result(key)[1]
    assert image.size == (1600, 900)
    assert original.shape[:2] == (900, 1600)
    assert app.current_template().fps == 60
    app._save_settings()
    app.var_preview_quality.set('操作優先')
    app._load_settings()
    assert app.var_preview_quality.get() == '表示サイズで確認'


@pytest.fixture
def gallery_app(tmp_path):
    from core.effects import Template
    root = tk.Tk()
    root.withdraw()
    kill = SimpleNamespace(event_id=1, time=31., killer='Alpha', victim='Beta', role='kill')
    instance = SimpleNamespace(root=root, kills=[kill], templates={'原色': Template(grade='default'), '金': Template(grade='golden')},
        _scene_thumbnail_path=lambda key: tmp_path/f'{key}.png', _preview_input=lambda event: None)
    yield instance
    root.destroy()


def test_gallery_comparison_worker_leaves_tk_responsive(gallery_app, monkeypatch):
    from ui import template_gallery as gallery
    from ui.scene_project import scene_key
    path = gallery_app._scene_thumbnail_path(scene_key(gallery_app.kills[0]))
    Image.new('RGB', (960, 540), (32, 85, 170)).save(path)
    entered, release = threading.Event(), threading.Event()
    main = threading.get_ident()
    comparison = gallery.render_scene_comparison
    def slow(*args, **kwargs):
        assert threading.get_ident() != main
        entered.set()
        assert release.wait(3)
        return comparison(*args, **kwargs)
    monkeypatch.setattr(gallery, 'render_scene_comparison', slow)
    win = gallery.open_gallery(gallery_app)
    try:
        pump(gallery_app.root, entered.is_set)
        heartbeat = []
        gallery_app.root.after(1, lambda: heartbeat.append(True))
        pump(gallery_app.root, lambda: bool(heartbeat), timeout=.5)
        assert not win._previews
        release.set()
        pump(gallery_app.root, lambda: len(win._previews) == 2)
        assert all(photo.width() == 303 for photo in win._previews)
    finally:
        release.set()
        win.destroy()
    assert win._comparison_worker._closed


def test_same_count_rescan_replaces_stale_scene_and_no_fake_image(gallery_app):
    from ui.template_gallery import open_gallery
    first = open_gallery(gallery_app)
    pump(gallery_app.root, lambda: first._comparison_worker.result(first._generation) is not None)
    assert not first._previews
    gallery_app.kills = [SimpleNamespace(event_id=2, time=64., killer='Gamma', victim='Delta', role='assist')]
    second = open_gallery(gallery_app)
    assert second is not first and not first.winfo_exists()
    assert 'アシスト' in second._scene_signature[0][0]
    assert '64.0s' in second._scene_signature[0][0]
    assert first._comparison_worker._closed
    second.destroy()
