"""Exercise the reviewed camera timing change without Windows or a GPU."""
import time

import pytest

from core.camera import CameraDirector, CameraPlan, smoothstep
from core.camera_clock import SmoothReplayClock


def test_clock_pause_and_bounded_correction():
    clock = SmoothReplayClock(100)
    clock.observe(101)
    assert clock.advance(.05, 0) == 100
    assert clock.advance(.05, 1) == pytest.approx(100.054)
    clock.observe(99)
    before = clock.time
    assert clock.advance(.05, 1) == pytest.approx(before + .046)


def test_two_marker_camera_keeps_previous_smoothstep():
    frames = ({'time': -1, 'yaw': -15, 'zoom': -4, 'fov': 3},
              {'time': 1, 'yaw': 25, 'zoom': 12, 'fov': -5})
    plan = CameraPlan(style='third_cinema', kill_time=100, scene_keyframes=frames)
    for i in range(41):
        u = i / 40
        expected = tuple(frames[0][key] + (frames[1][key] - frames[0][key]) * smoothstep(u)
                         for key in ('yaw', 'zoom', 'fov'))
        assert plan.keyframe_values(99 + 2*u) == pytest.approx(expected)


def test_multimarker_turns_stay_within_each_segment():
    frames = tuple({'time': t, 'yaw': y, 'zoom': y/2, 'fov': -y/4}
                   for t, y in [(-2, 0), (-1.8, 10), (0, -20), (.3, 15), (3, 0)])
    plan = CameraPlan(style='lolnam_cinema', kill_time=100, scene_keyframes=frames)
    for left, right in zip(frames, frames[1:]):
        for i in range(101):
            t = left['time'] + (right['time'] - left['time']) * i/100
            for key, value in zip(('yaw', 'zoom', 'fov'), plan.keyframe_values(100+t)):
                assert min(left[key], right[key])-1e-8 <= value <= max(left[key], right[key])+1e-8


def test_live_director_counts_slow_render_calls_and_keeps_target():
    class API:
        def __init__(self):
            self.started = time.perf_counter()
            self.bodies = []
            self.speeds = []

        def playback(self):
            return {'time': 100 + time.perf_counter() - self.started}

        def set_render(self, **body):
            self.bodies.append(body)
            time.sleep(.03)
            if len(self.bodies) == 3:
                director._stop.set()

        def set_playback(self, **body):
            self.speeds.append(body['speed'])

    api = API()
    director = CameraDirector(api, CameraPlan(style='cinema', kill_time=100, sel_name='Hero'))
    director.start()
    director._th.join(timeout=2)
    director.stop()
    assert not director._th.is_alive()
    assert director.errors == 0
    assert director.api_calls == director.api_slow_calls == 3
    assert director.max_api_latency_ms >= 25
    assert api.bodies[0]['selectionName'] == 'Hero'
    assert api.bodies[0]['cameraAttached'] is True
    assert all('fieldOfView' in body for body in api.bodies)
    assert api.speeds
    assert director._clock.time > 100
