"""Portable packaging keeps the WGC worker separate from the GUI."""
from pathlib import Path

import pytest

from core.capture_process import capture_worker_command


def test_source_launch_keeps_original_python_worker():
    command = capture_worker_command("frame123", "LoL", executable="python.exe", frozen=False)
    assert command[:2] == ["python.exe", "-u"]
    assert Path(command[2]).name == "capture_worker.py"
    assert command[-4:] == ["--memory", "frame123", "--title", "LoL"]


def test_frozen_launch_uses_sibling_executable(tmp_path):
    gui = tmp_path / "LoL_AutoCine.exe"
    worker = tmp_path / "LoL_AutoCine_Capture.exe"
    worker.touch()
    assert capture_worker_command("frame123", "LoL", executable=str(gui), frozen=True) == [
        str(worker), "--memory", "frame123", "--title", "LoL"]
    worker.unlink()
    with pytest.raises(FileNotFoundError, match="worker missing"):
        capture_worker_command("frame123", "LoL", executable=str(gui), frozen=True)
