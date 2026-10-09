# -*- coding: utf-8 -*-
"""Collect useful AutoCine diagnostics without PowerShell escaping pitfalls."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "diagnostics"
DST = ROOT / "AutoCine_Diagnostics.zip"
KEEP_NAMES = {"latest_diagnostics.zip"}


def collect():
    SRC.mkdir(exist_ok=True)
    files = [p for p in SRC.rglob("*") if p.is_file() and p.stat().st_size > 0]
    # Include all valid performance, ffmpeg and runtime logs, not only the latest.
    if not files:
        print("No diagnostic files found under", SRC)
        return False
    with ZipFile(DST, "w", compression=ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT))
    print("Created:", DST)
    print("Collected files:", len(files))
    return True


if __name__ == "__main__":
    sys.exit(0 if collect() else 2)
