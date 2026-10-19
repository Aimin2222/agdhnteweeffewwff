# -*- coding: utf-8 -*-
"""Collect useful AutoCine diagnostics without PowerShell escaping pitfalls."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys
import json
import hashlib
from importlib import metadata

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "diagnostics"
DST = ROOT / "AutoCine_Diagnostics.zip"
KEEP_NAMES = {"latest_diagnostics.zip"}


def collect():
    SRC.mkdir(exist_ok=True)
    versions = {}
    for name in ('windows-capture', 'pillow', 'numpy', 'imageio-ffmpeg'):
        try: versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError: versions[name] = None
    fingerprints = {}
    for name in ('legacy_app.py', 'ui/live_preview.py', 'ui/mirror_capture.py', 'core/capture.py'):
        path = ROOT / name
        if path.is_file(): fingerprints[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot = dict(python=sys.version, packages=versions, code_sha256=fingerprints)
    version_file = ROOT / 'VERSION.txt'
    if version_file.is_file(): snapshot['version'] = version_file.read_text(encoding='utf-8').strip()
    (SRC/'collector_environment.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    files = [p for p in SRC.rglob("*") if p.is_file() and not p.is_symlink()
             and p.resolve().is_relative_to(SRC.resolve()) and p.stat().st_size > 0]
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
