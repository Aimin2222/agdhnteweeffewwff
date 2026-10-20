"""Native callbacks at 16 ms must not be discarded by another 16.67 ms gate."""
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from core import capture_worker


def test_wgc_16ms_callbacks_all_reach_latest_frame_slot(monkeypatch):
    bridges = []
    class Bridge:
        def __init__(self, _name):
            self.sequence = 0
            self.writes = 0
            bridges.append(self)
        def write(self, _buffer):
            self.writes += 1
            self.sequence += 2

    instances = []
    class FakeCapture:
        def __init__(self, cursor_capture=False, draw_border=False, window_hwnd=None,
                     monitor_index=None, minimum_update_interval=None):
            self.callbacks = {}
            self.minimum_update_interval = minimum_update_interval
            instances.append(self)
        def event(self, callback):
            self.callbacks[callback.__name__] = callback
            return callback
        def start_free_threaded(self):
            frame = SimpleNamespace(frame_buffer=np.zeros((2, 2, 4), np.uint8))
            for _ in range(20):
                self.callbacks['on_frame_arrived'](frame, None)
            self.callbacks['on_closed']()
            return object()

    clock = iter(i*.016 for i in range(22))
    monkeypatch.setattr(capture_worker, 'SharedFrame', Bridge)
    monkeypatch.setattr(capture_worker, 'find_lol_hwnd', lambda: 123)
    monkeypatch.setattr(capture_worker, 'time', SimpleNamespace(perf_counter=lambda: next(clock)))
    monkeypatch.setattr(capture_worker.faulthandler, 'enable', lambda **_kw: None)
    monkeypatch.setattr(capture_worker.faulthandler, 'dump_traceback_later', lambda *_a, **_kw: None)
    monkeypatch.setattr(capture_worker.faulthandler, 'cancel_dump_traceback_later', lambda: None)
    monkeypatch.setattr(capture_worker.os, '_exit', lambda code: (_ for _ in ()).throw(SystemExit(code)))
    monkeypatch.setitem(sys.modules, 'windows_capture', SimpleNamespace(WindowsCapture=FakeCapture))
    with pytest.raises(SystemExit) as stopped:
        capture_worker.run('test-slot', capture_worker.LOL_WINDOW_TITLE)
    assert stopped.value.code == 0
    assert instances[0].minimum_update_interval == 16
    assert bridges[0].writes == 20
