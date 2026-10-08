# -*- coding: utf-8 -*-
"""Riot 公式 Replay API / Live Client Data API の薄いクライアント (127.0.0.1:2999)。"""
from __future__ import annotations
import json
import ssl
import time
import urllib.request
import urllib.error
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
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx)
        )

    def _req(self, method: str, path: str, body: Optional[dict] = None) -> Any:
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with self._lock:
                with self._opener.open(req, timeout=self.timeout) as r:
                    raw = r.read()
        except urllib.error.HTTPError as e:
            raise ReplayApiError(f"{method} {path} -> HTTP {e.code}") from e
        except Exception as e:
            raise ReplayApiError(f"{method} {path} -> {e}") from e
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

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
