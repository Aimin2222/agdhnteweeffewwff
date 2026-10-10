# -*- coding: utf-8 -*-
"""Riot 公式 Replay API / Live Client Data API の薄いクライアント (127.0.0.1:2999)。"""
from __future__ import annotations
import json
import ssl
import time
import urllib.request
import urllib.error
import http.client
from urllib.parse import urlsplit
import threading
from typing import Any, Optional


class ReplayApiError(Exception):
    pass


class ReplayAPI:
    def __init__(self, base: str = "https://127.0.0.1:2999", timeout: float = 3.0):
        self.base = base.rstrip("/")
        self.timeout = timeout
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # Riot の自己署名証明書 (ローカルのみ)
        self._lock = threading.RLock()
        # urllib.request sets Connection: close on each request. On the real
        # HTTPS Replay API that can mean a complete TCP/TLS handshake for every
        # 60Hz camera update, producing observed 100-240ms stalls. Reuse one
        # keep-alive connection instead. HTTP/1.0 servers may close responses;
        # those are transparently reopened on the next request.
        self._tls_context = ctx
        self._parsed_base = urlsplit(self.base)
        self._conn = None

    def _open_connection(self):
        url = self._parsed_base
        if url.scheme == 'https':
            return http.client.HTTPSConnection(url.hostname, url.port or 443,
                                               context=self._tls_context, timeout=self.timeout)
        if url.scheme == 'http':
            return http.client.HTTPConnection(url.hostname, url.port or 80,
                                              timeout=self.timeout)
        raise ReplayApiError('Unsupported Replay API scheme: ' + str(url.scheme))

    def _req(self, method: str, path: str, body: Optional[dict] = None) -> Any:
        data = json.dumps(body).encode('utf-8') if body is not None else None
        headers = {'Accept': 'application/json'}
        if data is not None:
            headers['Content-Type'] = 'application/json'
        try:
            with self._lock:
                if self._conn is None:
                    self._conn = self._open_connection()
                try:
                    prefix = self._parsed_base.path.rstrip('/')
                    self._conn.request(method, prefix + path, body=data, headers=headers)
                    response = self._conn.getresponse()
                    raw = response.read()   # consume body before next request
                    status = response.status
                    # HTTP/1.0 and explicitly closed responses cannot be reused.
                    if response.will_close:
                        self._conn.close()
                        self._conn = None
                except (OSError, http.client.HTTPException) as exc:
                    # A failed POST must not be automatically retried: it may
                    # have succeeded on the server before the socket broke.
                    try: self._conn.close()
                    except Exception: pass
                    self._conn = None
                    raise ReplayApiError(f'{method} {path} -> {exc}') from exc
        except ReplayApiError:
            raise
        except Exception as exc:
            raise ReplayApiError(f'{method} {path} -> {exc}') from exc
        if status >= 400:
            raise ReplayApiError(f'{method} {path} -> HTTP {status}')
        if not raw:
            return None
        try:
            return json.loads(raw.decode('utf-8'))
        except Exception:
            return None

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def get(self, path: str) -> Any:
        return self._req("GET", path)

    def post(self, path: str, body: dict) -> Any:
        return self._req("POST", path, body)

    # ---- high level
    def is_up(self) -> bool:
        try:
            self.get("/replay/playback")
            return True
        except ReplayApiError:
            return False

    def wait_ready(self, timeout: float = 120.0, interval: float = 1.5, stop=None) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout:
            if stop is not None and stop.is_set():
                return False
            if self.is_up():
                return True
            time.sleep(interval)
        return False

    def playback(self) -> dict:
        return self.get("/replay/playback") or {}

    def set_playback(self, **kw) -> None:
        self.post("/replay/playback", kw)

    def render(self) -> dict:
        return self.get("/replay/render") or {}

    def set_render(self, **kw) -> None:
        self.post("/replay/render", kw)

    def playerlist(self) -> list:
        r = self.get("/liveclientdata/playerlist")
        return r if isinstance(r, list) else []

    def events(self) -> list:
        r = self.get("/liveclientdata/eventdata") or {}
        return r.get("Events", []) if isinstance(r, dict) else []

    def seek(self, t: float, wait: float = 6.0) -> float:
        """t 秒へシークし、seeking が終わるまで待って実際の時刻を返す。"""
        self.set_playback(time=float(max(0.0, t)))
        t0 = time.time()
        pb: dict = {}
        while time.time() - t0 < wait:
            pb = self.playback()
            if not pb.get("seeking", False):
                break
            time.sleep(0.05)
        return float(pb.get("time", t))
