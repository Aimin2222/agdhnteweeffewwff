# -*- coding: utf-8 -*-
"""AutoCine 音声診断ログ。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import threading

_ROOT = Path(__file__).resolve().parents[1]
_LOG = _ROOT / "diagnostics" / "audio.log"
_LOCK = threading.Lock()


def log(message: str, level: str = "INFO") -> None:
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().astimezone().isoformat(timespec="milliseconds")
        line = f"[{ts}] [{level.upper()}] {message}\n"
        with _LOCK:
            with _LOG.open("a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        # 診断ログの失敗で本体を止めない
        pass


def reset() -> None:
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        with _LOCK:
            _LOG.write_text("", encoding="utf-8")
    except Exception:
        pass
