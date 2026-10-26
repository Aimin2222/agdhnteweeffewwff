"""Catch missing runtime files before publishing a Windows UI ZIP."""
from pathlib import Path

import pytest

from tools.build_portable_ui import validate_bundle


def test_portable_bundle_requires_version_and_runtime_tools(tmp_path):
    paths = [
        "LoL_AutoCine.exe",
        "LoL_AutoCine_UI29.exe",
        "LoL_AutoCine_Capture.exe",
        "_internal/VERSION.txt",
        "_internal/assets/work_kill_assets/catalog.json",
        "_internal/tools/bin/lol_audio_helper.exe",
        "_internal/imageio_ffmpeg/binaries/ffmpeg-test.exe",
        "_internal/ui/comparison7_screens.json",
        "_internal/design/ui/ui_rethink_20261021/ui7.css",
        "_internal/design/ui/ui29_legacy/legacy.css",
        "_internal/design/ui/ui29_legacy/reconstructed.css",
        "_internal/ui/audit29_client.js",
        "_internal/ui/comparison_detail.css",
    ]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()
    validate_bundle(tmp_path)
    (tmp_path / "_internal/VERSION.txt").unlink()
    with pytest.raises(RuntimeError, match="VERSION.txt"):
        validate_bundle(tmp_path)


def test_portable_bundle_rejects_excluded_candidate_source(tmp_path):
    from tools.build_portable_ui import validate_bundle
    paths = ["LoL_AutoCine.exe", "LoL_AutoCine_UI29.exe", "LoL_AutoCine_Capture.exe",
             "_internal/VERSION.txt", "_internal/assets/work_kill_assets/catalog.json",
             "_internal/tools/bin/lol_audio_helper.exe",
             "_internal/imageio_ffmpeg/binaries/ffmpeg-test.exe",
             "_internal/ui/comparison7_screens.json",
             "_internal/design/ui/ui_rethink_20261021/ui7.css",
             "_internal/design/ui/ui29_legacy/legacy.css",
             "_internal/design/ui/ui29_legacy/reconstructed.css",
             "_internal/ui/audit29_client.js", "_internal/ui/comparison_detail.css"]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()
    design = tmp_path / "_internal/design/ui/ui_rethink_20261021"
    (design / "A_main.html").touch()
    with pytest.raises(RuntimeError, match="Excluded candidate"):
        validate_bundle(tmp_path)
