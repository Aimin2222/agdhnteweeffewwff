"""Verify the Director's elapsed-time path, not just the standalone clock."""
from types import SimpleNamespace

import pytest

import core.camera as camera
from core.camera_clock import SmoothReplayClock


def test_director_accounts_for_105ms_render_wait(monkeypatch):
    class WallClock:
        now = 1.0

        def sleep(self, elapsed):
            self.now += elapsed

    wall = WallClock()
    monkeypatch.setattr(camera, 'time', SimpleNamespace(
        perf_counter=lambda: wall.now, sleep=wall.sleep))
    bodies = []

    def send(**body):
        bodies.append(body)
        wall.now += .105
        if len(bodies) == 4:
            director._stop.set()

    api = SimpleNamespace(playback=lambda: {'time': director._clock.time},
                          set_render=send, set_playback=lambda **_: None)
    plan = camera.CameraPlan(style='cinema', kill_time=100, sel_name='Hero')
    plan.speed_at = lambda _: 1.0
    director = camera.CameraDirector(api, plan)
    director._clock = SmoothReplayClock(100)
    director._last_sync = wall.now
    director._run()
    # The last write has not yet had a following integration tick.
    assert director._clock.time == pytest.approx(100 + wall.now - 1 - .105)
    assert director.api_calls == director.api_slow_calls == 4
    assert director.max_api_latency_ms == pytest.approx(105)
    assert bodies[0]['selectionName'] == 'Hero'


def test_clock_stall_cap_and_pause_are_retained():
    clock = SmoothReplayClock(100)
    assert clock.advance(5) == pytest.approx(100.25)
    clock.observe(100.4)
    assert clock.advance(.18, 0) == pytest.approx(100.25)
