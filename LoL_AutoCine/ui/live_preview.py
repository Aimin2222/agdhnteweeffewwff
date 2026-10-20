"""One bounded preview worker. Requests/results contain plain data, never Tk objects."""
from __future__ import annotations

import threading
import time
from collections import deque
import statistics


class LatestPreview:
    def __init__(self, render, *, fallback=None, on_error=None):
        self._render = render
        self._fallback = fallback
        self._on_error = on_error
        self._last_error = None
        self._last_error_at = 0.
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._pending = None
        self._result = None
        self._key = None
        self._closed = False
        self._thread = None
        self._durations_ms = deque(maxlen=120)
        self._replaced = 0
        self._completed = 0

    def submit(self, key, request):
        with self._lock:
            if self._closed:
                return
            self._key = key
            if self._pending is not None:
                self._replaced += 1
            self._pending = (key, request)  # Replace obsolete frames, never queue them.
            if self._thread is None:
                self._thread = threading.Thread(target=self._run, daemon=True,
                                                name="AutoCine-live-preview")
                self._thread.start()
            self._wake.set()

    def result(self, key):
        with self._lock:
            return self._result if self._result is not None and self._result[0] == key else None

    def close(self):
        with self._lock:
            self._closed = True
            self._pending = self._result = None
            self._wake.set()

    def stats(self):
        with self._lock:
            samples = list(self._durations_ms)
            return {'completed': self._completed, 'replaced': self._replaced,
                    'median_ms': round(statistics.median(samples), 2) if samples else None,
                    'p95_ms': round(sorted(samples)[int(.95*(len(samples)-1))], 2) if samples else None}

    def _run(self):
        while True:
            self._wake.wait()
            with self._lock:
                if self._closed:
                    return
                job, self._pending = self._pending, None
                self._wake.clear()
            if job is None:
                continue
            key, request = job
            started = time.perf_counter()
            try:
                value = self._render(request)
            except Exception as exc:
                value = None  # A stopped capture source must not kill the UI worker.
                message = f'{type(exc).__name__}: {exc}'
                now = time.monotonic()
                if message != self._last_error or now-self._last_error_at >= 5.:
                    self._last_error, self._last_error_at = message, now
                    if self._on_error:
                        try: self._on_error(message)
                        except Exception: pass
                if self._fallback:
                    try: value = self._fallback(request)
                    except Exception: pass
            with self._lock:
                self._durations_ms.append((time.perf_counter()-started)*1000)
                self._completed += 1
                if not self._closed and key == self._key and value is not None:
                    self._result = (key, value)
