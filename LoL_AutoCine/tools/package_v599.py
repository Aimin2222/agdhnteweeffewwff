# -*- coding: utf-8 -*-
"""Reproducible v5.9.9.1 full & Codex-diff ZIPs. Run from a Git checkout.

Usage: python LoL_AutoCine/tools/package_v599.py
Prerequisite: git fetch origin codex/lol-autocine-v598-handoff
Does not modify the Git index, edit a user file, or upload anything.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

APP = Path(__file__).resolve().parents[1]
REPO = APP.parent
DIST = REPO / "dist"
STABLE = "origin/codex/lol-autocine-v598-handoff"
EXCLUDED_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules", "output", "outputs"}
EXCLUDED_SUFFIXES = {".mp4", ".mkv", ".wav", ".avi", ".mov", ".webm", ".pyc", ".log", ".tmp"}
FULL_ZIP = DIST / "LoL_AutoCine_v5.9.9.1_Windows_Full.zip"
DIFF_ZIP = DIST / "LoL_AutoCine_v5.9.9.1_Codex_MergeChanges.zip"


def run_git(*args: str) -> str:
    proc = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=True)
    return proc.stdout


def in_package(path: Path) -> bool:
    rel = path.relative_to(APP)
    return (path.is_file() and
            not any(name in EXCLUDED_DIRS for name in rel.parts) and
            path.suffix.lower() not in EXCLUDED_SUFFIXES and
            not (len(rel.parts) > 1 and rel.parts[0] == "diagnostics"))


def write_manifest(z: ZipFile, files: list[Path]) -> None:
    for f in files:
        z.write(f, arcname=f.relative_to(REPO).as_posix())


def build() -> tuple[Path, Path]:
    version = (APP / "VERSION.txt").read_text(encoding="utf-8").strip()
    if version != "5.9.9.1":
        raise RuntimeError(f"VERSION.txt is not 5.9.9.1: {version}")
    DIST.mkdir(exist_ok=True)
    allfiles = sorted(f for f in APP.rglob("*") if in_package(f))
    assert len(allfiles) >= 90, f"Suspiciously incomplete source: {len(allfiles)} files"
    with ZipFile(FULL_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        write_manifest(z, allfiles)

    diff_names = run_git("diff", "--name-only", f"{STABLE}...HEAD", "--", "LoL_AutoCine").splitlines()
    changed = [REPO / name for name in diff_names if (REPO / name).is_file()]
    if not changed or not any(p.name == "kill_icons.py" for p in changed):
        raise RuntimeError("Expected v5.9.9.1 source changes are missing in the diff")
    patch = run_git("diff", "--binary", f"{STABLE}...HEAD", "--", "LoL_AutoCine")
    instructions = """# v5.9.9.1 Codex統合用差分

- 基準: `codex/lol-autocine-v598-handoff`（v5.9.8）
- 変更ファイル: このZIPに含まれる `LoL_AutoCine/` 以下
- Git推奨: 既存変更をコミットしてから `git apply --check CHANGES_v5.9.9.1.patch` → `git apply CHANGES_v5.9.9.1.patch`
- Gitを使わない場合: 一覧を比較してから各ファイルをマージ（自動上書きは推奨しない）
- Codexが別途編集した `core/effects.py`、`core/gpu_pipeline.py`、`core/jobs.py`、`core/camera.py` 等はコンフリクト確認必須
- 音声のProcess Loopback、NVENC、TargetLock、UI設定の回帰テストを実施
- Windows/LoL/NVIDIA実機テストは配布前のLinux CIとは別に行う
"""
    with ZipFile(DIFF_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        write_manifest(z, sorted(changed))
        z.writestr("CHANGES_v5.9.9.1.patch", patch)
        z.writestr("MERGE_INSTRUCTIONS_JA.md", instructions)
    for f in (FULL_ZIP, DIFF_ZIP):
        with ZipFile(f) as z:
            bad = z.testzip()
            if bad:
                raise RuntimeError(f"ZIP integrity test failed: {bad}")
            assert z.namelist(), f"{f.name} is empty"
    sums = "\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}"
                     for p in (FULL_ZIP, DIFF_ZIP)) + "\n"
    (DIST / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    print(f"Full: {len(allfiles)} files, {FULL_ZIP.stat().st_size} bytes")
    print(f"Diff: {len(changed)} files, {DIFF_ZIP.stat().st_size} bytes")
    print(sums, end="")
    return FULL_ZIP, DIFF_ZIP


if __name__ == "__main__":
    build()
