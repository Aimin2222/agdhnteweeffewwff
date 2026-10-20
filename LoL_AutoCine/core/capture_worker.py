"""Standalone WGC worker: no Tk, FFmpeg, audio, or desktop capture fallback."""
from pathlib import Path
import argparse
import faulthandler
import importlib.metadata
import inspect
import os
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.capture import LOL_WINDOW_TITLE, find_lol_hwnd
from core.capture_process import SharedFrame


def run(memory_name, title):
    faulthandler.enable(file=sys.stderr)
    faulthandler.dump_traceback_later(6, file=sys.stderr)
    print('WGC_STAGE worker_enter python=' + sys.version.split()[0], file=sys.stderr, flush=True)
    if title != LOL_WINDOW_TITLE:
        raise RuntimeError('Only the LoL replay window is supported')
    hwnd = find_lol_hwnd()
    if hwnd is None:
        raise RuntimeError('LoL replay window was not found')
    print('WGC_STAGE import_begin', file=sys.stderr, flush=True)
    from windows_capture import WindowsCapture
    print('WGC_STAGE import_ready version=' + importlib.metadata.version('windows-capture'), file=sys.stderr, flush=True)
    bridge = SharedFrame(memory_name)
    closed = threading.Event()
    failed = threading.Event()
    rate_started = time.perf_counter()
    rate_frames = 0
    parameters = inspect.signature(WindowsCapture).parameters
    kwargs = dict(cursor_capture=False, draw_border=False)
    # The native API accepts exactly ONE target. Passing both the name and
    # HWND raises before the capture can start (windows-capture 2.0.1).
    if 'window_hwnd' in parameters:
        kwargs['window_hwnd'] = hwnd
    else:
        kwargs['window_name'] = title
    if 'monitor_index' in parameters:
        kwargs['monitor_index'] = None
    if 'minimum_update_interval' in parameters:
        kwargs['minimum_update_interval'] = 16
    cap = WindowsCapture(**kwargs)
    @cap.event
    def on_frame_arrived(frame, control):
        nonlocal rate_started, rate_frames
        try:
            # WGC already has a 16 ms minimum update interval. A second
            # 1/60 s timer dropped legitimate ~16 ms callbacks and reduced
            # unique frames in 60 FPS exports to about 39 FPS on the QA host.
            # The shared slot is latest-only; recording still samples at 60.
            # Direct shared-memory copy while the native BGRA mapping is valid.
            first = bridge.sequence == 0
            bridge.write(frame.frame_buffer)
            rate_frames += 1
            now = time.perf_counter()
            elapsed = now-rate_started
            if elapsed >= 5.0:
                print(f'WGC_STAGE published_fps={rate_frames/elapsed:.1f} '
                      f'frames={rate_frames} seconds={elapsed:.1f}', file=sys.stderr, flush=True)
                rate_started, rate_frames = now, 0
            if first:
                faulthandler.cancel_dump_traceback_later()
                print('WGC_STAGE first_frame_written', file=sys.stderr, flush=True)
        except Exception as e:
            print('WGC_STAGE frame_error ' + str(e), file=sys.stderr, flush=True)
            failed.set()
    @cap.event
    def on_closed():
        print('WGC_STAGE window_closed', file=sys.stderr, flush=True)
        closed.set()
    print('WGC_STAGE native_start_begin', file=sys.stderr, flush=True)
    control = cap.start_free_threaded()
    print('WGC_STAGE native_start_ready', file=sys.stderr, flush=True)
    # Keep cap/control/bridge alive until process shutdown. A native stop may
    # block too: the parent owns the bounded termination of this worker.
    while not closed.wait(.05) and not failed.is_set():
        pass
    faulthandler.cancel_dump_traceback_later()
    print('WGC_STAGE worker_finished', file=sys.stderr, flush=True)
    sys.stderr.flush()
    os._exit(1 if failed.is_set() else 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--memory', required=True)
    parser.add_argument('--title', required=True)
    args = parser.parse_args()
    try:
        run(args.memory, args.title)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        os._exit(2)
