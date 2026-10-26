"""Separate opt-in Windows test entry point for Issue #53.

The ordinary app.py / START.bat keep legacy rendering. The packaged executable
routes existing child-process commands back into their Python modules.
"""
from __future__ import annotations

import os
from pathlib import Path
import runpy
import sys


def main() -> None:
    argv = sys.argv
    if len(argv) >= 3 and argv[1] == "-u" and Path(argv[2]).name == "capture_worker.py":
        sys.argv = [argv[2], *argv[3:]]
        runpy.run_path(str(Path(__file__).resolve().parent / "core" / "capture_worker.py"), run_name="__main__")
        return
    if len(argv) >= 3 and argv[1:3] == ["-m", "yt_dlp"]:
        sys.argv = ["yt_dlp", *argv[3:]]
        from yt_dlp import main as yt_dlp_main
        raise SystemExit(yt_dlp_main())
    os.environ.setdefault("AUTOCINE_RESEARCH_FLASH", "causal_pts_v1")
    os.environ.setdefault("AUTOCINE_RESEARCH_ZOOM", "normalized_tmix_v1")
    from app import main as app_main
    app_main()


if __name__ == "__main__":
    main()
