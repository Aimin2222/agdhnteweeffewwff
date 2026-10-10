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
    from ctypes import wintypes
    find = ctypes.windll.user32.FindWindowW
    find.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    find.restype = wintypes.HWND
    hwnd = find(None, LOL_WINDOW_TITLE)
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
    """LoL-only WGC in an isolated process, with bounded startup/shutdown."""

    def __init__(self, window_title: str = LOL_WINDOW_TITLE):
        super().__init__()
        self.title = window_title
        self._session = None
        self._state_lock = threading.RLock()
        self._stopping = False

    def start(self) -> None:
        from .capture_process import CaptureSession
        if find_lol_hwnd() is None:
            raise CaptureError("LoLのウィンドウが見つかりません。リプレイを再生してから実行してください。")
        with self._state_lock:
            old = self._session
            if self._stopping:
                raise CaptureError("LoL画面キャプチャを停止中です。")
            if old is not None and not old.cancelled.is_set():
                if self.running:
                    return
                raise CaptureError("LoL画面キャプチャを開始中です。")
        if old is not None:
            self.stop()
        with self._state_lock:
            if self._session is not None or self._stopping:
                raise CaptureError("LoL画面キャプチャを開始中です。")
            with self._lock:
                self._frame = None
            session = CaptureSession(self, self.title)
            self._session = session
            try:
                session.launch()
            except Exception:
                self.stop()
                raise
        try:
            session.await_frame()
            with self._state_lock:
                if self._session is not session or session.cancelled.is_set():
                    raise CaptureError("LoL画面キャプチャの開始を中止しました。")
                self.running = True
        except Exception:
            self.stop()
            raise

    def latest(self) -> Optional[np.ndarray]:
        session = self._session
        if session is not None and session.error:
            raise CaptureError(session.error)
        return super().latest()

    def stop(self) -> None:
        with self._state_lock:
            if self._stopping:
                return
            session = self._session
            self._stopping = True
            self.running = False
        try:
            if session is not None:
                session.close()
            with self._state_lock:
                if self._session is session:
                    self._session = None
            with self._lock:
                self._frame = None
        finally:
            with self._state_lock:
                self._stopping = False


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
