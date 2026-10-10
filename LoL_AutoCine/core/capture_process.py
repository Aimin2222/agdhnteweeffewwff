"""Bound native WGC startup/exit without loading it in the GUI interpreter."""
from __future__ import annotations
import atexit
import logging
from multiprocessing import shared_memory
from pathlib import Path
import struct
import subprocess
import sys
import threading
import time
import weakref

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
HEADER = struct.Struct('<QIII')  # sequence, height, width, payload bytes
HEADER_BYTES = 64
MAX_BYTES = 3840 * 2160 * 4
START_TIMEOUT = 8.0
_sessions = weakref.WeakSet()
_registry_lock = threading.Lock()


def _log(message):
    logging.getLogger(__name__).info(message)
    try:
        folder = ROOT / 'diagnostics'
        folder.mkdir(exist_ok=True)
        with (folder / 'capture.log').open('a', encoding='utf-8') as f:
            f.write(time.strftime('[%Y-%m-%d %H:%M:%S] ') + message + '\n')
    except OSError:
        pass


class SharedFrame:
    """One latest BGRA frame; odd sequence means the writer is copying.

    A reader owns its copied array and accepts it only when both sequence
    reads match. No queue can accumulate full-resolution frames.
    """
    def __init__(self, name=None, capacity=MAX_BYTES):
        if name is None:
            self.memory = shared_memory.SharedMemory(create=True, size=HEADER_BYTES + capacity)
            self.memory.buf[:HEADER_BYTES] = bytes(HEADER_BYTES)
            self.owner = True
        else:
            kwargs = {'name': name, 'create': False}
            if sys.version_info >= (3, 13):
                kwargs['track'] = False
            self.memory = shared_memory.SharedMemory(**kwargs)
            self.owner = False
            if sys.platform != 'win32' and sys.version_info < (3, 13):
                # The standalone subprocess has a separate resource tracker;
                # only the creator may unlink this allocation (Python 3.12).
                from multiprocessing import resource_tracker
                resource_tracker.unregister(self.memory._name, 'shared_memory')
        self.capacity = self.memory.size - HEADER_BYTES
        self.sequence = 0

    def write(self, frame):
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 4:
            raise ValueError('Capture must supply uint8 BGRA')
        h, w, _ = frame.shape
        size = h * w * 4
        if h <= 0 or w <= 0 or size > self.capacity:
            raise ValueError('Capture frame exceeds shared buffer capacity')
        sequence = self.sequence + 2
        HEADER.pack_into(self.memory.buf, 0, sequence - 1, h, w, size)
        target = np.ndarray(frame.shape, dtype=np.uint8, buffer=self.memory.buf, offset=HEADER_BYTES)
        try:
            np.copyto(target, frame)  # Copy while the native callback owns its buffer.
        finally:
            del target
        HEADER.pack_into(self.memory.buf, 0, sequence, h, w, size)
        self.sequence = sequence

    def read(self, previous):
        sequence, h, w, size = HEADER.unpack_from(self.memory.buf)
        if sequence == 0 or sequence == previous or sequence & 1:
            return None
        if h <= 0 or w <= 0 or size != h * w * 4 or size > self.capacity:
            raise ValueError('Invalid shared capture frame header')
        view = np.ndarray((h, w, 4), dtype=np.uint8, buffer=self.memory.buf, offset=HEADER_BYTES)
        try:
            result = view.copy()
        finally:
            del view
        # Reject incomplete/overwritten frames instead of publishing mixed pixels.
        if struct.unpack_from('<Q', self.memory.buf)[0] != sequence:
            return None
        return sequence, result

    def close(self):
        self.memory.close()
        if self.owner:
            try:
                self.memory.unlink()
            except FileNotFoundError:
                pass


class CaptureSession:
    def __init__(self, source, title):
        self.source = source
        self.title = title
        self.ready = threading.Event()
        self.cancelled = threading.Event()
        self.frame = None
        self.process = None
        self.reader = None
        self.error = None
        self._cleanup_lock = threading.Lock()
        self.stderr = None
        self.error_path = None
        self.job_handle = None

    def launch(self):
        from .capture import CaptureError
        try:
            self.frame = SharedFrame()
            folder = ROOT / 'diagnostics'
            folder.mkdir(exist_ok=True)
            # Each attempt keeps its own native startup diagnostics.
            self.error_path = folder / f'capture_worker_{time.time_ns()}.log'
            self.stderr = self.error_path.open('wb')
            cmd = [sys.executable, '-u', str(Path(__file__).with_name('capture_worker.py')),
                   '--memory', self.frame.memory.name, '--title', self.title]
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if sys.platform == 'win32' else 0
            self.process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.DEVNULL, stderr=self.stderr,
                                            creationflags=flags)
            self.job_handle = _windows_kill_on_close(self.process)
            _log(f'WGC_STAGE process_started pid={self.process.pid}')
            with _registry_lock:
                _sessions.add(self)
            self.reader = threading.Thread(target=self._receive, name='AutoCine-WGC-reader', daemon=True)
            self.reader.start()
        except Exception as e:
            self.close()
            raise CaptureError(f'LoLキャプチャの準備に失敗しました: {e}') from e

    def _receive(self):
        sequence = 0
        try:
            while not self.cancelled.is_set():
                code = self.process.poll()
                if code is not None:
                    self.error = f'画面キャプチャの別プロセスが終了しました (code={code})'
                    # Show the native exception, not only the child exit code.
                    try:
                        with self.error_path.open('rb') as log:
                            log.seek(0, 2)
                            log.seek(max(0, log.tell() - 4096))
                            lines = log.read().decode('utf-8', 'replace').splitlines()
                        for line in reversed(lines):
                            if line.startswith('Exception:') or 'Error: ' in line and not line.startswith(' '):
                                self.error += ': ' + line[:500]
                                break
                    except OSError:
                        pass
                    self.source.running = False
                    with self.source._lock:
                        self.source._frame = None
                    self.ready.set()
                    _log(f'WGC_STAGE worker_exit code={code}')
                    self.close(_from_reader=True)
                    return
                sample = self.frame.read(sequence)
                if sample is not None:
                    sequence, copied = sample
                    self.source._push(copied)
                    self.ready.set()
                self.cancelled.wait(.004)
        except Exception as e:
            self.error = f'画面キャプチャの受信に失敗しました: {e}'
            self.source.running = False
            self.ready.set()
            try:
                self.close(_from_reader=True)
            except Exception:
                _log('WGC_STAGE receiver_cleanup_failed')

    def await_frame(self, timeout=START_TIMEOUT):
        from .capture import CaptureError
        if not self.ready.wait(timeout):
            _log('WGC_STAGE startup_timeout')
            raise CaptureError('LoL画面キャプチャが8秒以内に開始できませんでした。'
                               'リプレイ画面を表示し、最小化を解除してから再試行してください。'
                               '詳細は diagnostics/capture_worker_*.log に保存しました。')
        if self.error:
            raise CaptureError(self.error)
        if self.cancelled.is_set():
            raise CaptureError('LoL画面キャプチャの開始を中止しました。')
        if self.process.poll() is not None:
            raise CaptureError('LoL画面キャプチャが開始前に終了しました。')
        if self.source.latest() is None:
            raise CaptureError('LoL画面キャプチャからフレームを取得できませんでした。')
        _log('WGC_STAGE first_frame_ready')

    def close(self, _from_reader=False):
        if not self.cancelled.is_set():
            _log(f'WGC_STAGE stop_requested caller={threading.current_thread().name}')
        self.cancelled.set()
        self.ready.set()
        if _from_reader:
            if not self._cleanup_lock.acquire(blocking=False):
                return  # Another caller is already cleaning up and joining us.
        else:
            self._cleanup_lock.acquire()
        try:
            self.source.running = False
            process = self.process
            if process is not None:
                if process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=.75)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=.75)
                    except ProcessLookupError:
                        pass
                if process.poll() is None:
                    # Keep resources referenced until a later cleanup succeeds.
                    raise RuntimeError('Capture worker could not be stopped')
                _log(f'WGC_STAGE process_stopped pid={process.pid} code={process.returncode}')
            if self.reader is not None and self.reader is not threading.current_thread():
                self.reader.join(timeout=.5)
                if self.reader.is_alive():
                    raise RuntimeError('Capture receiver could not be stopped')
                self.reader = None
            if self.frame is not None:
                self.frame.close()
                self.frame = None
            if self.stderr is not None:
                self.stderr.close()
                self.stderr = None
            if self.job_handle is not None:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(self.job_handle)
                self.job_handle = None
            with _registry_lock:
                _sessions.discard(self)
        finally:
            self._cleanup_lock.release()


def _windows_kill_on_close(process):
    """Stop only this child if Windows kills its parent without running atexit."""
    if sys.platform != 'win32':
        return None
    import ctypes
    from ctypes import wintypes
    class Basic(ctypes.Structure):
        _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64),
                    ('flags', wintypes.DWORD), ('min_ws', ctypes.c_size_t),
                    ('max_ws', ctypes.c_size_t), ('active', wintypes.DWORD),
                    ('affinity', ctypes.c_size_t), ('priority', wintypes.DWORD),
                    ('scheduling', wintypes.DWORD)]
    class IO(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
    class Limits(ctypes.Structure):
        _fields_ = [('basic', Basic), ('io', IO), ('process_memory', ctypes.c_size_t),
                    ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t), ('peak_job', ctypes.c_size_t)]
    api = ctypes.windll.kernel32
    api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    api.CreateJobObjectW.restype = wintypes.HANDLE
    api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    job = api.CreateJobObjectW(None, None)
    if not job:
        _log('WGC_STAGE job_guard_unavailable')
        return None
    info = Limits()
    info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not api.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)) or not api.AssignProcessToJobObject(job, process._handle):
        api.CloseHandle(job)
        _log('WGC_STAGE job_guard_unavailable')
        return None
    return job


def _cleanup_sessions():
    with _registry_lock:
        sessions = list(_sessions)
    for session in sessions:
        try:
            session.close()
        except Exception:
            pass


atexit.register(_cleanup_sessions)
