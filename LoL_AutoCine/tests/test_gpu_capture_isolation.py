"""Use real subprocesses/shared memory to exercise WGC's safe process boundary.

The synthetic worker replaces only the Windows driver; it is not GPU validation.
"""
from pathlib import Path
from multiprocessing import shared_memory
import subprocess
import sys
import threading
import time

import numpy as np
import pytest

from core.capture import WGCWindowSource, CaptureError, FrameSource
from core import capture_process as cp


@pytest.fixture
def worker(monkeypatch,tmp_path):
    real_popen=subprocess.Popen
    monkeypatch.setattr(cp,'ROOT',tmp_path)
    from core import capture
    monkeypatch.setattr(capture,'find_lol_hwnd',lambda:123)
    def configure(mode):
        def launch(command,**kwargs):
            name=command[command.index('--memory')+1]
            code=f"""
import sys,time,os
sys.path.insert(0,{str(Path(__file__).resolve().parents[1])!r})
from core.capture_process import SharedFrame
import numpy as np
bridge=SharedFrame({name!r})
mode={mode!r}
if mode=='native':
 import types
 import core.capture_worker as worker
 worker.find_lol_hwnd=lambda:123
 worker.importlib.metadata.version=lambda _: 'test-native'
 class WindowsCapture:
  def __init__(self, cursor_capture=False,draw_border=False,window_name=None,minimum_update_interval=None,window_hwnd=None):
   assert window_name==worker.LOL_WINDOW_TITLE and window_hwnd==123
   assert not cursor_capture and not draw_border and minimum_update_interval==16
   self.handlers={{}}
  def event(self,fn):self.handlers[fn.__name__]=fn;return fn
  def start_free_threaded(self):
   assert threading.current_thread() is threading.main_thread()
   def frames():
    while True:
     data=np.full((32,48,4),[10,20,30,255],dtype=np.uint8)
     self.handlers['on_frame_arrived'](types.SimpleNamespace(frame_buffer=data),None)
     data[:]=0
     time.sleep(.02)
   threading.Thread(target=frames,daemon=True).start()
   return object()
 import threading
 sys.modules['windows_capture']=types.SimpleNamespace(WindowsCapture=WindowsCapture)
 worker.run({name!r},worker.LOL_WINDOW_TITLE)
if mode=='blocked':
 time.sleep(120)
if mode=='crash':
 os._exit(17)
for i in range(3000):
 bridge.write(np.full((32,48,4),[10,20,30,255],dtype=np.uint8))
 if mode=='later-crash' and i==10:os._exit(18)
 time.sleep(.02)
"""
            return real_popen([sys.executable,'-u','-c',code],**kwargs)
        monkeypatch.setattr(cp.subprocess,'Popen',launch)
    yield configure
    cp._cleanup_sessions()


def wait_for(predicate,timeout=3):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if predicate():return
        time.sleep(.01)
    pytest.fail('condition did not become true')


def test_shared_frame_owns_pixels_and_rejects_incomplete_or_invalid_frames():
    bridge=cp.SharedFrame(capacity=64*64*4)
    try:
        image=np.full((12,16,4),[10,20,30,255],dtype=np.uint8)
        bridge.write(image)
        seq,copy=bridge.read(0)
        image[:]=0
        assert np.array_equal(copy[0,0],[10,20,30,255])
        assert bridge.read(seq) is None
        cp.HEADER.pack_into(bridge.memory.buf,0,seq+1,12,16,12*16*4)
        assert bridge.read(seq) is None
        cp.HEADER.pack_into(bridge.memory.buf,0,seq+2,12,16,1)
        with pytest.raises(ValueError,match='header'):bridge.read(seq)
        with pytest.raises(ValueError):bridge.write(np.zeros((100,100,4),np.uint8))
        with pytest.raises(ValueError):bridge.write(np.zeros((12,16,3),np.uint8))
    finally:bridge.close()


@pytest.mark.parametrize('mode',['frames','native'])
def test_actual_process_delivers_bgra_without_importing_native_capture(worker,mode):
    worker(mode);source=WGCWindowSource()
    try:
        source.start();session=source._session;name=session.frame.memory.name
        assert source.running and source.frame_count>=1
        assert source.latest().shape==(32,48,4)
        assert np.array_equal(source.latest()[0,0],[10,20,30,255])
        old=source.frame_count;wait_for(lambda:source.frame_count>old)
        source.start()  # Must reuse, never duplicate the active child.
        assert source._session is session
        assert 'windows_capture' not in sys.modules
    finally:source.stop()
    assert session.process.poll() is not None and source.latest() is None
    with pytest.raises(FileNotFoundError):shared_memory.SharedMemory(name=name)
    source.stop()


def test_native_start_hang_has_bounded_timeout_and_same_source_can_retry(worker):
    worker('blocked');source=WGCWindowSource();session=cp.CaptureSession(source,source.title)
    session.launch();process=session.process;name=session.frame.memory.name
    try:
        start=time.monotonic()
        with pytest.raises(CaptureError,match='開始できません'):
            session.await_frame(timeout=.15)
        assert time.monotonic()-start<.7
    finally:session.close()
    assert process.poll() is not None
    with pytest.raises(FileNotFoundError):shared_memory.SharedMemory(name=name)
    worker('frames')
    try:source.start();assert source.running
    finally:source.stop()


def test_child_failure_before_first_frame_is_reported_and_cleaned(worker):
    worker('crash');source=WGCWindowSource()
    with pytest.raises(CaptureError,match='code=17'):
        source.start()
    assert not source.running and source._session is None
    worker('frames')
    try:source.start();assert source.running
    finally:source.stop()


def test_child_exit_after_start_propagates_instead_of_recording_stale_frame(worker):
    worker('later-crash');source=WGCWindowSource()
    try:
        source.start();session=source._session
        wait_for(lambda:session.error is not None)
        assert not source.running
        with pytest.raises(CaptureError,match='code=18'):source.latest()
    finally:source.stop()


def test_stop_during_blocked_start_releases_waiter_and_process(worker):
    worker('blocked');source=WGCWindowSource();errors=[]
    def start():
        try:source.start()
        except CaptureError as e:errors.append(str(e))
    thread=threading.Thread(target=start,daemon=True);thread.start()
    wait_for(lambda:source._session is not None and source._session.process is not None)
    process=source._session.process
    source.stop();thread.join(2)
    assert not thread.is_alive() and errors and not source.running
    assert process.poll() is not None and source._session is None


def test_tk_events_continue_during_native_startup_wait(worker):
    import tkinter as tk
    worker('blocked');source=WGCWindowSource();errors=[]
    root=tk.Tk();root.withdraw();ticks=[]
    def tick():
        ticks.append(time.monotonic());root.after(10,tick)
    def start():
        try:source.start()
        except CaptureError as e:errors.append(str(e))
    thread=threading.Thread(target=start,daemon=True)
    try:
        thread.start();wait_for(lambda:source._session is not None and source._session.process is not None)
        root.after(0,tick)
        end=time.monotonic()+.25
        while time.monotonic()<end:
            root.update();time.sleep(.003)
        assert len(ticks)>=10 and thread.is_alive()
        source.stop();thread.join(2)
        assert not thread.is_alive() and errors
    finally:
        source.stop();root.destroy()


def test_missing_window_does_not_create_worker(monkeypatch):
    from core import capture
    monkeypatch.setattr(capture,'find_lol_hwnd',lambda:None)
    monkeypatch.setattr(cp.subprocess,'Popen',lambda *a,**k:pytest.fail('worker created'))
    with pytest.raises(CaptureError,match='見つかりません'):WGCWindowSource().start()


def test_worker_rejects_another_window_before_loading_native_capture():
    from core.capture_worker import run
    try:
        with pytest.raises(RuntimeError,match='Only the LoL'):run('unused','another window')
        assert 'windows_capture' not in sys.modules
    finally:
        import faulthandler
        faulthandler.cancel_dump_traceback_later()
