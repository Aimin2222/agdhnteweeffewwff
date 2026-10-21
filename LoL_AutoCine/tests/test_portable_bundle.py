"""Catch missing runtime files before publishing a Windows UI ZIP."""
from pathlib import Path

import pytest

from tools.build_portable_ui import validate_bundle


def test_portable_bundle_requires_version_and_runtime_tools(tmp_path):
    paths = [
        "LoL_AutoCine.exe",
        "LoL_AutoCine_Capture.exe",
        "_internal/VERSION.txt",
        "_internal/assets/work_kill_assets/catalog.json",
        "_internal/tools/bin/lol_audio_helper.exe",
        "_internal/imageio_ffmpeg/binaries/ffmpeg-test.exe",
    ]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()
    validate_bundle(tmp_path)
    (tmp_path / "_internal/VERSION.txt").unlink()
    with pytest.raises(RuntimeError, match="VERSION.txt"):
        validate_bundle(tmp_path)
