# -*- coding: utf-8 -*-
"""映像入力はLoLのウィンドウ(HWND)のみ。デスクトップ/モニター全体へはフォールバックしない。

Windows Graphics Capture を `windows-capture` パッケージ経由でウィンドウ名指定して使う。
取得したフレームは numpy(BGRA) として最新1枚を保持し、プレビュー(ミラーリング)と録画の両方が参照する。
"""
from __future__ import annotations
import sys
import threading
import time
from typing import Optional

import numpy as np

LOL_WINDOW_TITLE = "League of Legends (TM) Client"


class CaptureError(Exception):
    pass


def find_lol_hwnd() -> Optional[int]:
    """LoL ウィンドウの HWND を返す。見つからなければ None (=録画を開始しない)。"""
    if sys.platform != "win32":
        return None
    import ctypes
    hwnd = ctypes.windll.user32.FindWindowW(None, LOL_WINDOW_TITLE)
    return int(hwnd) if hwnd else None


class FrameSource:
    """最新フレームを保持する基底クラス。frame は (h, w, 4) uint8 BGRA。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._count = 0
        self.running = False

    def _push(self, frame: np.ndarray) -> None:
        with self._lock:
            self._frame = frame
            self._count += 1

    def latest(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._frame

    @property
    def frame_count(self) -> int:
        return self._count

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class WGCWindowSource(FrameSource):
    """Windows Graphics Capture (ウィンドウ単位)。"""

    def __init__(self, window_title: str = LOL_WINDOW_TITLE):
        super().__init__()
        self.title = window_title
        self._control = None
        # Keep the Python WindowsCapture object alive for the entire native
        # capture session.  The native callback owns zero-copy frame memory.
        # Letting this object be garbage-collected while the native thread is
        # still running can cause 0xc0000005 access violations.
        self._capture = None
        self._closed = threading.Event()
        # WGC may deliver frames much faster than AutoCine needs. Keep the
        # native callback alive, but only copy one frame every 1/60 second.
        # This sharply reduces native->Python memory traffic.
        self._last_copy_at = 0.0
        self._copy_interval = 1.0 / 60.0

    def start(self) -> None:
        if find_lol_hwnd() is None:
            raise CaptureError("LoLのウィンドウが見つかりません。リプレイを再生してから実行してください "
                               "(画面全体へのフォールバックは行いません)。")
        try:
            from windows_capture import WindowsCapture  # type: ignore
        except ImportError as e:
            raise CaptureError("windows-capture が未インストールです。START.bat で依存関係を入れてください。") from e
        cap = WindowsCapture(
            cursor_capture=False,
            draw_border=False,
            window_name=self.title,
            minimum_update_interval=16,
        )
        self._capture = cap
        self._closed.clear()
        self._last_copy_at = 0.0

        @cap.event
        def on_frame_arrived(frame, control):  # noqa: ANN001
            try:
                # Throttle before touching/copying the native frame buffer.
                # WGC can deliver 120/144/240Hz even when the recorder is 60Hz.
                now = time.perf_counter()
                if now - self._last_copy_at < self._copy_interval:
                    return
                self._last_copy_at = now
                # frame_buffer is a zero-copy view into native mapped memory.
                # Copy it immediately while the callback owns the frame.
                buf = frame.frame_buffer
                copied = np.array(buf, dtype=np.uint8, copy=True, order="C")
                if copied.ndim != 3 or copied.shape[2] != 4:
                    return
                self._push(copied)
            except Exception:
                # Do not let Python exceptions propagate into the native
                # callback. The capture thread will be stopped by stop().
                return

        @cap.event
        def on_closed():
            self.running = False
            self._closed.set()

        try:
            self._control = cap.start_free_threaded()
        except Exception:
            self._capture = None
            raise
        self.running = True
        t0 = time.time()
        while self.latest() is None and time.time() - t0 < 5.0:
            time.sleep(0.05)
        if self.latest() is None:
            self.stop()
            raise CaptureError("LoLウィンドウからフレームを取得できません (最小化されていないか確認してください)。")

    def stop(self) -> None:
        # windows-capture has a native shutdown path. Never drop the
        # WindowsCapture object before that path has had a chance to close.
        self.running = False
        control = self._control
        try:
            if control is not None:
                control.stop()
                self._closed.wait(timeout=2.0)
        except Exception:
            pass
        self._control = None
        self._capture = None


class SyntheticSource(FrameSource):
    """テスト用: 再生時刻に応じて動くグラデーション映像を生成 (LoLなしでパイプライン検証)。"""

    def __init__(self, w: int = 640, h: int = 360, fps: float = 60.0, time_fn=None):
        super().__init__()
        self.w, self.h, self.fps, self.time_fn = w, h, fps, time_fn
        self._th: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start(self) -> None:
        self._stop.clear()
        self.running = True
        self._th = threading.Thread(target=self._run, daemon=True)
        self._th.start()
        t0 = time.time()
        while self.latest() is None and time.time() - t0 < 2:
            time.sleep(0.01)

    def _run(self) -> None:
        x = np.linspace(0, 255, self.w, dtype=np.uint8)
        base = np.tile(x, (self.h, 1))
        n = 0
        while not self._stop.is_set():
            t = self.time_fn() if self.time_fn else n / self.fps
            shift = int(t * 120) % self.w
            g = np.roll(base, shift, axis=1)
            fr = np.empty((self.h, self.w, 4), np.uint8)
            fr[..., 0] = g
            fr[..., 1] = 255 - g
            fr[..., 2] = (g // 2) + 40
            fr[..., 3] = 255
            self._push(fr)
            n += 1
            time.sleep(1.0 / self.fps)

    def stop(self) -> None:
        self._stop.set()
        self.running = False
        if self._th:
            self._th.join(timeout=1.0)
