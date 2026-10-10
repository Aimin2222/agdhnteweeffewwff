"""UI responsiveness during blocked Replay API / FFmpeg status checks."""
import queue
import threading
import time
from types import SimpleNamespace
import tkinter as tk
import pytest


def _until(root, condition, timeout=3):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        root.update()
        if condition():
            return
        time.sleep(.005)
    assert condition(), 'UI result was not delivered'


@pytest.fixture
def gui(tmp_path, monkeypatch):
    import legacy_app as ui
    from core.replay_api import ReplayAPI
    monkeypatch.setattr(ReplayAPI, 'is_up', lambda _: False)
    monkeypatch.setattr(ui, 'gpu_encoder_available', lambda: False)
    monkeypatch.setattr(ui, 'gpu_pipeline_status', lambda: 'CPU Effects / CPU Encode')
    monkeypatch.setattr(ui, 'SETTINGS', tmp_path/'settings.json')
    monkeypatch.setattr(ui, 'RUN_LOG', tmp_path/'runtime.log')
    monkeypatch.setattr(ui, 'CRASH_LOG', tmp_path/'crash.log')
    monkeypatch.setattr(ui, '_fatal_fp', None)
    root = tk.Tk()
    app = ui.App(root)
    _until(root, lambda: not app._status_refresh_pending and not app._gpu_refresh_pending)
    app.scene_project_path = tmp_path/'project.json'
    yield app, root
    app._closing = True
    root.destroy()


@pytest.mark.parametrize('probe_kind', ['connection', 'gpu'])
def test_all_scene_dispatch_and_stop_work_while_status_is_blocked(gui, monkeypatch, probe_kind):
    import legacy_app as ui
    from core.players import Player
    from core.scanner import Kill
    app, root = gui
    owner = threading.get_ident()
    entered, release, rendering, finish = (threading.Event() for _ in range(4))
    calls, captured, stopped = [], [], []

    def slow_probe(*_):
        calls.append(threading.get_ident())
        entered.set()
        assert release.wait(3)
        return True

    if probe_kind == 'connection':
        monkeypatch.setattr(app.api, 'is_up', slow_probe)
        refresh = app._refresh_status
    else:
        monkeypatch.setattr(ui, 'gpu_encoder_available', slow_probe)
        refresh = app._refresh_gpu_status
    # Tk variable reads must stay on the owner thread, even with all-scene jobs.
    original_get = tk.Variable.get
    def checked_get(var):
        assert threading.get_ident() == owner, 'worker read Tk state'
        return original_get(var)
    monkeypatch.setattr(tk.Variable, 'get', checked_get)
    app.locked = Player(1, 'A', 'A#1', 'A', 'Lee Sin', 'ORDER')
    app.kills = [Kill(i+1, 10+i, 'A', 'B', []) for i in range(5)]
    app.var_encoder_policy.set('GPU優先（NVENC）')
    app.var_gaudio.set(True)
    app.var_montage.set(True)
    source = SimpleNamespace(stop=lambda: stopped.append(True))
    monkeypatch.setattr(app, '_ensure_source', lambda: (source, True))
    def render(src, player, kills, template, montage, audio_factory, *scene):
        captured.append((threading.get_ident(), src, player, kills, template, montage, audio_factory))
        rendering.set()
        assert finish.wait(3)
        return SimpleNamespace(outputs=['clip.mp4'], failed=[])
    monkeypatch.setattr(app, '_render_with_optional_scene_mode', render)
    heartbeats = []
    try:
        begin = time.monotonic()
        refresh()
        assert time.monotonic()-begin < .2
        assert entered.wait(1)
        for _ in range(20):
            refresh()
        assert len(calls) == 1, 'duplicate status threads'
        root.after(0, lambda: heartbeats.append(True))
        app.on_make_clips()
        assert app.busy and rendering.wait(1)
        _until(root, lambda: bool(heartbeats))
        # A second click does not resnapshot settings or start another capture.
        monkeypatch.setattr(ui.messagebox, 'showinfo', lambda *_: None)
        monkeypatch.setattr(app, 'current_template', lambda: pytest.fail('busy click reread settings'))
        app.on_make_clips()
        assert len(captured) == 1
        app.on_stop()
        assert app.stop_ev.is_set()
        tid, src, player, kills, template, montage, factory = captured[0]
        assert tid != owner and src is source and player is app.locked
        assert kills == app.kills and len(kills) == 5
        assert template.encoder_policy == 'gpu' and template.game_audio
        assert montage and factory is not None
    finally:
        release.set()
        finish.set()
        _until(root, lambda: not app.busy and not app._status_refresh_pending and not app._gpu_refresh_pending)
    assert stopped == [True]
    text = ui.RUN_LOG.read_text()
    for stage in ('click_enter', 'template_begin', 'template_ready', 'enqueue_worker',
                  'queued', 'worker_enter', 'capture_start', 'capture_ready', 'render_begin', 'render_complete'):
        assert 'ALL_STAGE '+stage in text


def test_connection_refresh_does_not_wait_for_real_api_lock(gui, monkeypatch):
    from core.replay_api import ReplayAPI
    app, root = gui
    api = ReplayAPI()
    # is_up retains the real ReplayAPI method rather than the fixture's stub.
    def get(_):
        with api._lock:
            return {}
    api.get = get
    api.is_up = lambda: bool(api.get('/replay/playback') is not None)
    app.api = api
    entered, release = threading.Event(), threading.Event()
    def recording_request():
        with api._lock:
            entered.set()
            assert release.wait(3)
    holder = threading.Thread(target=recording_request)
    holder.start()
    assert entered.wait(1)
    heartbeat = []
    try:
        begin = time.monotonic()
        app._refresh_status()
        assert time.monotonic()-begin < .2
        root.after(0, lambda: heartbeat.append(True))
        _until(root, lambda: bool(heartbeat))
        assert app._status_refresh_pending
    finally:
        release.set()
        holder.join(1)
        _until(root, lambda: not app._status_refresh_pending)
    assert '接続: OK' in app.lbl_status.cget('text')


def test_status_errors_are_delivered_and_can_be_refreshed_again(gui, monkeypatch):
    import legacy_app as ui
    app, root = gui
    def fail():
        raise RuntimeError('probe failure')
    monkeypatch.setattr(app.api, 'is_up', fail)
    monkeypatch.setattr(ui, 'gpu_encoder_available', fail)
    app._refresh_status()
    app._refresh_gpu_status()
    _until(root, lambda: not app._status_refresh_pending and not app._gpu_refresh_pending)
    assert '確認できません' in app.lbl_status.cget('text')
    assert '判定できません' in app.lbl_gpu.cget('text')
    monkeypatch.setattr(app.api, 'is_up', lambda: True)
    monkeypatch.setattr(ui, 'gpu_encoder_available', lambda: True)
    app._refresh_status()
    app._refresh_gpu_status()
    _until(root, lambda: not app._status_refresh_pending and not app._gpu_refresh_pending)
    assert '接続: OK' in app.lbl_status.cget('text')
    assert 'NVENC登録あり' in app.lbl_gpu.cget('text')
    # Manual refreshes replace the periodic timer instead of multiplying it.
    token = app._status_poll_token
    app._schedule_status_poll()
    assert app._status_poll_token != token
    assert token not in root.tk.call('after', 'info')


def test_invalid_all_scene_settings_are_reported_without_launch(gui, monkeypatch):
    import legacy_app as ui
    app, root = gui
    app.locked = SimpleNamespace(name='A')
    app.kills = [SimpleNamespace(time=10)]
    def invalid():
        raise tk.TclError('invalid number')
    monkeypatch.setattr(app, 'current_template', invalid)
    monkeypatch.setattr(app, '_ensure_source', lambda: pytest.fail('capture started'))
    app.on_make_clips()
    assert not app.busy
    assert 'ALL_CALLBACK_ERROR' in ui.CRASH_LOG.read_text()


def test_all_scene_watchdog_cancelled_on_capture_failure(gui, monkeypatch, tmp_path):
    import legacy_app as ui
    app, root = gui
    app.locked = SimpleNamespace(name='A')
    app.kills = [SimpleNamespace(time=10)]
    armed, cancelled = [], []
    monkeypatch.setattr(ui, '_fatal_fp', object())
    monkeypatch.setattr(ui.faulthandler, 'dump_traceback_later', lambda *a, **k: armed.append(True))
    monkeypatch.setattr(ui.faulthandler, 'cancel_dump_traceback_later', lambda: cancelled.append(True))
    def fail():
        raise ui.CaptureError('No frames')
    monkeypatch.setattr(app, '_ensure_source', fail)
    app.on_make_clips()
    _until(root, lambda: not app.busy)
    assert armed == cancelled == [True]
    assert not app._checked_watchdog_active
    assert '書き出し失敗: No frames' in app.lbl_job.cget('text')


def test_mirror_wait_and_stop_do_not_block_tk_and_cancelled_result_stays_off(gui, monkeypatch):
    import legacy_app as ui
    app, root = gui
    owner = threading.get_ident()
    entered, release, stopped = (threading.Event() for _ in range(3))
    sources = []

    class Source:
        running = False
        def __init__(self):
            sources.append(self)
        def start(self):
            assert threading.get_ident() != owner
            if len(sources) == 1:
                entered.set()
                assert release.wait(3)
            self.running = True
        def latest(self):
            return None
        def stop(self):
            assert threading.get_ident() != owner
            self.running = False
            stopped.set()

    monkeypatch.setattr(ui, 'FAKE_CAPTURE', False)
    monkeypatch.setattr(ui, 'WGCWindowSource', Source)
    original_get, original_set = tk.Variable.get, tk.Variable.set
    def checked_get(var):
        assert threading.get_ident() == owner
        return original_get(var)
    def checked_set(var, value):
        assert threading.get_ident() == owner
        return original_set(var, value)
    monkeypatch.setattr(tk.Variable, 'get', checked_get)
    monkeypatch.setattr(tk.Variable, 'set', checked_set)
    try:
        begin = time.monotonic()
        app.on_mirror_toggle()
        assert time.monotonic() - begin < .2 and entered.wait(1)
        assert app._mirror.pending and app.var_mirror.get()
        ticks = []
        root.after(0, lambda: ticks.append(True))
        _until(root, lambda: bool(ticks))
        app.on_mirror_toggle()
        assert not app.var_mirror.get() and app.source is None
        assert stopped.wait(1)
        # A new attempt succeeds before the old worker delivers its result.
        app.on_mirror_toggle()
        _until(root, lambda: app.source is sources[1])
        release.set()
        _until(root, lambda: not sources[0].running)
        root.update()
        assert app.source is sources[1] and app.var_mirror.get()
        app.on_mirror_toggle()
        assert app.source is None and not app.var_mirror.get()
    finally:
        release.set()
        app._mirror.stop()


def test_mirror_failure_returns_off_and_allows_retry(gui, monkeypatch):
    import legacy_app as ui
    app, root = gui
    class Source:
        running = False
        def start(self):
            raise ui.CaptureError('You can only specify one of')
        def stop(self):
            pass
    monkeypatch.setattr(ui, 'FAKE_CAPTURE', False)
    monkeypatch.setattr(ui, 'WGCWindowSource', Source)
    for _ in range(2):
        app.on_mirror_toggle()
        _until(root, lambda: not app._mirror.pending)
        assert app.source is None and not app.var_mirror.get()
    assert 'ミラー開始失敗: You can only specify one of' in ui.RUN_LOG.read_text()


def test_checked_capture_failure_replaces_preparing_label(gui, monkeypatch):
    import legacy_app as ui
    app, root = gui
    app.locked = SimpleNamespace(name='A')
    app.kills = [SimpleNamespace(time=10)]
    app.checked_kills = {0}
    app.lbl_job.configure(text='開始準備中…')
    def fail():
        raise ui.CaptureError('native target rejected')
    monkeypatch.setattr(app, '_ensure_source', fail)
    app.on_make_checked()
    _until(root, lambda: not app.busy)
    assert '書き出し失敗: native target rejected' in app.lbl_job.cget('text')
