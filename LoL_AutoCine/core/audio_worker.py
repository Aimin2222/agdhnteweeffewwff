# -*- coding: utf-8 -*-
"""Isolated LoL process-loopback audio worker.

Native WASAPI/COM failures are intentionally isolated in this child process so
an access violation cannot terminate the AutoCine GUI process.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
from .procloop import ProcessLoopbackRecorder


def main() -> int:
    if len(sys.argv) < 2:
        print("ERROR output path is required", flush=True)
        return 2
    path = Path(sys.argv[1])
    rec = ProcessLoopbackRecorder(path)
    try:
        rec.start()
        print(f"START {rec.t0:.9f}", flush=True)
    except Exception as e:
        print(f"ERROR {e}", flush=True)
        return 3
    stop_code = 0
    try:
        for line in sys.stdin:
            if line.strip().upper() == "STOP":
                break
    finally:
        try:
            dur = rec.stop()
            print(f"DURATION {dur:.6f}", flush=True)
        except Exception as e:
            print(f"ERROR_STOP {e}", flush=True)
            stop_code = 4
    return stop_code


if __name__ == "__main__":
    raise SystemExit(main())
