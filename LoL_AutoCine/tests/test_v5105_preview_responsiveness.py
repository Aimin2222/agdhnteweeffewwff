"""Slow preview work must not stall Tk; superseded settings must not accumulate."""
import threading
import time
from types import SimpleNamespace

import numpy as np
import tkinter as tk

from ui.live_preview import LatestPreview


def wait_for(predicate, root=None):
    deadline = time.monotonic() + 3
    while not predicate() and time.monotonic() < deadline:
        if root is not None:
            root.update()
        time.sleep(.005)
    assert predicate()


def test_pending_frames_are_bounded_and_old_settings_never_return():
    entered, release = threading.Event(), threading.Event()
    seen = []
    def render(value):
        seen.append(value)
        if value == 0:
            entered.set()
            assert release.wait(3)
        return value
    worker = LatestPreview(render)
    try:
        worker.submit('old', 0)
        assert entered.wait(1)
        for i in range(1, 500):
            worker.submit('new', i)
        assert worker.result('new') is None
        release.set()
        wait_for(lambda: worker.result('new') is not None)
        assert seen == [0, 499]
        assert worker.result('new')[1] == 499
        assert worker.result('old') is None
    finally:
        release.set()
        worker.close()


def test_close_discards_pending_work_without_waiting_for_slow_render():
    entered, release = threading.Event(), threading.Event()
    seen = []
    def render(value):
        seen.append(value)
        entered.set()
        release.wait(3)
        return value
    worker = LatestPreview(render)
    try:
        worker.submit('first', 1)
        assert entered.wait(1)
        worker.submit('second', 2)
        worker.close()
        worker.submit('third', 3)
        release.set()
        worker._thread.join(1)
        assert not worker._thread.is_alive()
        assert seen == [1]
        assert worker.result('first') is None
    finally:
        release.set()
        worker.close()


def test_mirror_fx_does_not_block_sliders_tab_switch_or_tk_callbacks(tmp_path, monkeypatch):
    import legacy_app
    monkeypatch.setattr(legacy_app, 'SETTINGS', tmp_path / 'settings.json')
    root = tk.Tk()
    app = legacy_app.App(root)
    entered, release = threading.Event(), threading.Event()
    main_thread = threading.get_ident()
    def effects(rgb, template, phase=.5):
        assert threading.get_ident() != main_thread
        entered.set()
        assert release.wait(3)
        return rgb
    monkeypatch.setattr(legacy_app, 'apply_video_effect_preview', effects)
    app.source = SimpleNamespace(running=True, latest=lambda: np.zeros((180, 320, 4), dtype=np.uint8))
    app.var_live.set(True)
    try:
        app._preview_tick()
        assert entered.wait(1)
        heartbeat = []
        root.after(0, lambda: heartbeat.append(True))
        for value in (.1, .3, .8):
            app.sl['grade_strength'].set(value)
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        app._editor_advanced_tabs.select(1)
        root.update()
        assert heartbeat and not release.is_set()
        assert app.sl['grade_strength'].get() == .8
        assert app._editor_advanced_tabs.index('current') == 1
        app._preview_tick()  # Submit the latest settings while old work is still blocked.
        key = app._live_preview._key
        release.set()
        wait_for(lambda: app._live_preview.result(key) is not None)
        app._preview_tick()
        assert app._preview_presented[0] == key
        assert app._photo is not None
    finally:
        release.set()
        app._live_preview.close()
        root.destroy()


def test_burst_of_focus_updates_draws_only_final_state(monkeypatch):
    from legacy_app import FocusCircleViz
    root = tk.Tk()
    variables = [tk.DoubleVar(master=root, value=value) for value in (.5, .5, .3, .1)]
    widget = FocusCircleViz(root, *variables)
    draws = []
    monkeypatch.setattr(widget, 'draw', lambda: draws.append(tuple(v.get() for v in variables)))
    try:
        for i in range(25):
            variables[0].set(i / 100)
            variables[1].set(.6)
        assert not draws
        wait_for(lambda: bool(draws), root)
        assert draws == [(.24, .6, .3, .1)]
    finally:
        root.destroy()


def test_portrait_download_and_glow_preview_do_not_block_tk(tmp_path, monkeypatch):
    import legacy_app
    import core.kill_icons
    from PIL import Image
    monkeypatch.setattr(legacy_app, 'SETTINGS', tmp_path / 'settings.json')
    root = tk.Tk()
    app = legacy_app.App(root)
    entered, release = threading.Event(), threading.Event()
    main_thread = threading.get_ident()
    icon = tmp_path / 'portrait.png'
    Image.new('RGB', (72, 72), 'blue').save(icon)
    def lookup(player):
        assert threading.get_ident() != main_thread
        entered.set()
        assert release.wait(3)
        return icon
    monkeypatch.setattr(core.kill_icons, 'champion_icon', lookup)
    app.locked = SimpleNamespace(team='ORDER', to_dict=lambda: {'champion':'A'})
    app.players = [SimpleNamespace(team='CHAOS', to_dict=lambda: {'champion':'B'})]
    app.var_kill_icon_style.set(legacy_app.KILL_ICON_STYLES['cinema'])
    displayed = []
    monkeypatch.setattr(app, '_show_badge_preview', lambda im: displayed.append((im.size, threading.get_ident())))
    try:
        app._preview_kill_frame()
        assert entered.wait(1)
        heartbeat = []
        root.after(0, lambda: heartbeat.append(True))
        root.update()
        assert heartbeat and app._badge_preview_pending
        app._preview_kill_frame()  # Repeated clicks cannot create more download workers.
        release.set()
        wait_for(lambda: bool(displayed), root)
        assert len(displayed) == 1 and displayed[0][1] == main_thread
        assert not app._badge_preview_pending
    finally:
        release.set()
        app._live_preview.close()
        root.destroy()
