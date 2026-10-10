"""GPU-owned shared recording warmup and stale frame protection."""
from types import SimpleNamespace
import threading
import numpy as np
import pytest
import core.jobs as jobs
from core.capture import WGCWindowSource, CaptureError, SyntheticSource
from core.jobs import _prime_live_replay_once, _await_capture_refresh


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    class Clock:
        now = 0.0
        on_sleep = None
        def sleep(self, seconds):
            self.now += seconds
            if self.on_sleep:
                self.on_sleep(seconds)
    value = Clock()
    monkeypatch.setattr(jobs, 'time', SimpleNamespace(
        monotonic=lambda: value.now, time=lambda: value.now,
        perf_counter=lambda: value.now, sleep=value.sleep))
    return value

class FakeReplay:
    def __init__(self, source):
        self.source=source
        self.t=0.0
        self.playing=False
        self.calls=[]
    def set_playback(self,**kwargs):
        self.calls.append(('playback',kwargs.copy()))
        if 'paused' in kwargs:
            self.playing=not kwargs['paused']
    def seek(self,t):
        self.calls.append(('seek',t))
        self.t=t
        return t
    def playback(self):
        if self.playing:
            self.t+=0.12
            self.source._push(np.zeros((8,8,4),dtype=np.uint8))
        return {'time':self.t, 'seeking':False}


def test_first_clip_automatically_plays_before_seeking_to_start():
    source = WGCWindowSource()
    api = FakeReplay(source)
    logs=[]
    _prime_live_replay_once(api,source,start=95.0,log=logs.append)
    assert api._autocine_record_primed is True
    assert ('seek',93.5) in api.calls
    assert any(p.get('paused') is False for name,p in api.calls if name=='playback')
    assert api.playing is False
    assert source.frame_count>0
    assert any('手動再生は不要' in line for line in logs)
    n=len(api.calls)
    _prime_live_replay_once(api,source,start=150.0,log=logs.append)
    assert len(api.calls)==n  # Do not replay each following clip


def test_fresh_capture_guard_fails_safe_on_stale_game_frame():
    source=WGCWindowSource()
    with pytest.raises(CaptureError,match='更新されません'):
        _await_capture_refresh(source,0,timeout=0.01)
    source._push(np.zeros((8,8,4),dtype=np.uint8))
    _await_capture_refresh(source,0,timeout=0.01)


@pytest.mark.parametrize('moving,fresh', [(False, True), (True, False)])
def test_warmup_requires_both_replay_progress_and_fresh_frames(moving, fresh):
    source = WGCWindowSource()
    class Replay(FakeReplay):
        def playback(self):
            if self.playing:
                if moving:
                    self.t += .12
                if fresh:
                    source._push(np.zeros((8, 8, 4), dtype=np.uint8))
            return {'time': self.t}
    api = Replay(source)
    with pytest.raises(CaptureError, match='準備が完了'):
        _prime_live_replay_once(api, source, 95)
    assert not getattr(api, '_autocine_record_primed', False)
    assert not api.playing
    # A failed attempt must be eligible for a later successful retry.
    api.playback = FakeReplay.playback.__get__(api)
    _prime_live_replay_once(api, source, 95)
    assert api._autocine_record_primed


def test_warmup_replay_failure_pauses_and_remains_retryable():
    source = WGCWindowSource()
    class Replay(FakeReplay):
        def playback(self):
            if self.playing:
                raise jobs.ReplayApiError('failed while preparing')
            return {'time': self.t}
    api = Replay(source)
    with pytest.raises(jobs.ReplayApiError):
        _prime_live_replay_once(api, source, 95)
    assert not api.playing
    assert not getattr(api, '_autocine_record_primed', False)


def test_stop_during_final_warmup_wait_prevents_success_flag(clock):
    stop = threading.Event()
    clock.on_sleep = lambda seconds: stop.set() if seconds == .35 else None
    source = WGCWindowSource()
    api = FakeReplay(source)
    with pytest.raises(jobs.StallError, match='停止'):
        _prime_live_replay_once(api, source, 95, stop=stop)
    assert not api.playing
    assert not getattr(api, '_autocine_record_primed', False)


def test_frame_wait_accepts_only_a_new_frame_after_baseline(clock):
    source = WGCWindowSource()
    source._push(np.zeros((8, 8, 4), dtype=np.uint8))
    baseline = source.frame_count
    with pytest.raises(CaptureError):
        _await_capture_refresh(source, baseline, timeout=.01)
    clock.on_sleep = lambda _: source._push(np.ones((8, 8, 4), dtype=np.uint8))
    _await_capture_refresh(source, baseline)
    assert source.frame_count > baseline


def test_stop_during_frame_wait_prevents_recording(clock):
    stop = threading.Event()
    clock.on_sleep = lambda _: stop.set()
    with pytest.raises(jobs.StallError, match='停止'):
        _await_capture_refresh(WGCWindowSource(), 0, stop=stop)


def test_frame_from_during_setup_cannot_start_audio_or_recorder(monkeypatch, tmp_path):
    source = WGCWindowSource()
    source.running = True
    source._push(np.zeros((8, 8, 4), dtype=np.uint8))
    def setup(*args):
        source._push(np.ones((8, 8, 4), dtype=np.uint8))
        return None, None
    monkeypatch.setattr(jobs, '_setup_clip', setup)
    monkeypatch.setattr(jobs, 'ClipRecorder', lambda *a, **kw: pytest.fail('stale capture started'))
    api = FakeReplay(source)
    api._autocine_record_primed = True
    # Replay can move, but never produces another capture frame in recovery.
    def playback_without_frames():
        api.t += .12 if api.playing else 0
        return {'time': api.t}
    api.playback = playback_without_frames
    with pytest.raises(CaptureError, match='準備が完了'):
        jobs.record_one_clip(api, source, None,
                             jobs.Template(game_audio=True), 95, 96, [], tmp_path/'raw.mp4',
                             audio_factory=lambda *a: pytest.fail('audio started before readiness'))
    assert not (tmp_path/'raw.mp4').exists()
    assert not api.playing and not api._autocine_record_primed


@pytest.mark.parametrize('dead', [False, True])
def test_later_paused_scene_recovers_once_and_returns_to_exact_start(monkeypatch, dead):
    source = WGCWindowSource()
    source.running = not dead
    api = FakeReplay(source)
    api._autocine_record_primed = True
    setups, restarts, logs = [], [], []
    def setup(api, player, tpl, start, kills, log):
        api.set_playback(paused=True, speed=1.0)
        api.seek(start)
        # A paused renderer emits one valid frame during setup, then stays idle.
        source._push(np.ones((8, 8, 4), dtype=np.uint8))
        setups.append(start)
        return 'plan', 'rig'
    def restart():
        restarts.append(True)
        source.running = True
    monkeypatch.setattr(jobs, '_setup_clip', setup)
    monkeypatch.setattr(source, 'start', restart)
    monkeypatch.setattr(source, 'stop', lambda: None)
    assert jobs._prepare_clip_capture(api, source, None, jobs.Template(), 95, [], None, logs.append) == ('plan', 'rig')
    assert setups == [95, 95] and api.t == 95 and not api.playing
    assert restarts == ([True] if dead else [])
    assert sum('1回だけ復旧' in line for line in logs) == 1
    assert '指定の開始時刻' in logs[-1]


def test_cancelled_scene_does_not_restart_capture(monkeypatch, clock):
    source = WGCWindowSource();source.running = True
    api = FakeReplay(source);api._autocine_record_primed = True
    stop = threading.Event()
    monkeypatch.setattr(jobs, '_setup_clip', lambda *a: (None, None))
    monkeypatch.setattr(source, 'start', lambda: pytest.fail('cancelled source restarted'))
    clock.on_sleep = lambda _: stop.set()
    with pytest.raises(jobs.StallError):
        jobs._prepare_clip_capture(api, source, None, jobs.Template(), 95, [], stop, lambda _: None)


def test_game_pauses_before_ffmpeg_finalization(monkeypatch, tmp_path):
    source = SyntheticSource();api = FakeReplay(source)
    plan = SimpleNamespace(base_fov=90)
    rig = SimpleNamespace(v=None, third=False)
    monkeypatch.setattr(jobs, '_setup_clip', lambda *a: (plan, rig))
    monkeypatch.setattr(jobs, 'apply_fx', lambda *a, **k: {})
    monkeypatch.setattr(jobs, 'restore_fx', lambda *a: None)
    monkeypatch.setattr(jobs, 'restore_hud', lambda *a: None)
    monkeypatch.setattr(api, 'set_render', lambda **k: None, raising=False)
    monkeypatch.setattr(jobs, '_play_until', lambda *a, **k: None)
    director = SimpleNamespace(start=lambda: None,stop=lambda: None,errors=0,
        api_calls=0,api_slow_calls=0,max_api_latency_ms=0,max_clock_drift=0)
    monkeypatch.setattr(jobs, 'CameraDirector', lambda *a: director)
    class Recorder:
        started_perf = 0
        def __init__(self, *a, **k): pass
        def start(self): pass
        def stop(self):
            assert not api.playing, 'replay kept running during timing correction'
            return 2
    monkeypatch.setattr(jobs, 'ClipRecorder', Recorder)
    take = jobs.record_one_clip(api,source,None,jobs.Template(game_audio=False,hide_hud=False),
                               95,97,[],tmp_path/'raw.mp4')
    assert take.duration == 2


def test_synthetic_capture_needs_no_windows_warmup():
    source = SyntheticSource()
    api = FakeReplay(source)
    _prime_live_replay_once(api, source, 95)
    _await_capture_refresh(source, 0)
    assert api.calls == []


@pytest.mark.parametrize('positions,success', [([80, 95], True), ([80, 81], False)])
def test_seek_mismatch_retries_once_before_camera_attachment(monkeypatch, positions, success):
    positions = iter(positions)
    calls = []
    api = SimpleNamespace(set_playback=lambda **kwargs: None,
                          seek=lambda target: (calls.append(target), next(positions))[1])
    attached = []
    monkeypatch.setattr(jobs, 'attach_to_player',
                        lambda *a, **kw: (attached.append(True), SimpleNamespace(mode='third'))[1])
    args = (api, SimpleNamespace(selection_name='Hero', champion='Hero'),
            jobs.Template(), 95, [SimpleNamespace(time=96)], lambda _: None)
    if success:
        jobs._setup_clip(*args)
        assert attached == [True]
    else:
        with pytest.raises(jobs.ReplayApiError, match='シーク位置'):
            jobs._setup_clip(*args)
        assert not attached
    assert calls == [95, 95]
