# -*- coding: utf-8 -*-
"""Reproducible v5.10.13 RealScene GPUFull full & Codex-diff ZIPs. Run from a Git checkout.

Usage: python LoL_AutoCine/tools/package_v51013.py
Prerequisite: git fetch origin codex/lol-autocine-v51010-real-scene-handoff
Only packages Git-tracked files; excludes personal settings, recordings and projects.
Supports both the local AutoCine repository and the GitHub handoff checkout.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

APP = Path(__file__).resolve().parents[1]
REPO = Path(subprocess.check_output(["git", "-C", str(APP), "rev-parse", "--show-toplevel"], text=True).strip())
DIST = REPO / "dist"
BASE_REFS = (("integration/v5.10.10", "origin/integration/v5.10.10") if REPO == APP else
             ("origin/codex/lol-autocine-v51010-real-scene-handoff",))
STABLE = next((ref for ref in BASE_REFS if subprocess.run(
    ["git", "-C", str(REPO), "rev-parse", "--verify", ref + "^{commit}"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0), None)
if STABLE is None:
    raise RuntimeError("Codex v5.10.10基準がありません。元のbundleから復元するか基準ブランチをfetchしてください。")
EXCLUDED_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules", "output", "outputs", "projects", "thumbnails"}
EXCLUDED_SUFFIXES = {".mp4", ".mkv", ".wav", ".avi", ".mov", ".webm", ".pyc", ".log", ".tmp"}
PACKAGE_NAME = "LoL_AutoCine_v5.10.13_PlayerFilter_GPUFull"
FULL_ZIP = DIST / (PACKAGE_NAME + "_Windows_Full.zip")
DIFF_ZIP = DIST / (PACKAGE_NAME + "_Codex_MergeChanges.zip")


def run_git(*args: str) -> str:
    proc = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=True)
    return proc.stdout


def in_package(path: Path) -> bool:
    rel = path.relative_to(APP)
    return (path.is_file() and
            not any(name in EXCLUDED_DIRS for name in rel.parts) and
            path.suffix.lower() not in EXCLUDED_SUFFIXES and
            rel.name != "settings.json" and
            path.resolve().is_relative_to(APP.resolve()) and
            not (len(rel.parts) > 1 and rel.parts[0] == "diagnostics"))


def write_manifest(z: ZipFile, files: list[Path]) -> None:
    for f in files:
        z.write(f, arcname="LoL_AutoCine/" + f.relative_to(APP).as_posix())


def build() -> tuple[Path, Path]:
    version = (APP / "VERSION.txt").read_text(encoding="utf-8").strip()
    if version != "5.10.13":
        raise RuntimeError(f"VERSION.txt is not 5.10.13: {version}")
    DIST.mkdir(exist_ok=True)
    tracked = run_git("ls-files", "-z", "--", str(APP)).rstrip("\0").split("\0")
    allfiles = sorted(REPO / name for name in tracked if name and in_package(REPO / name))
    assert len(allfiles) >= 90, f"Suspiciously incomplete source: {len(allfiles)} files"
    with ZipFile(FULL_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        write_manifest(z, allfiles)

    diff_names = run_git("diff", "--no-renames", "--name-only", "-z", f"{STABLE}...HEAD", "--", str(APP)).rstrip("\0").split("\0")
    changed = [REPO / name for name in diff_names if name and in_package(REPO / name)]
    if not changed or not any(p.as_posix().endswith("legacy_app.py") for p in changed):
        raise RuntimeError("Expected v5.10.13 source changes are missing in the diff")
    prefix = "LoL_AutoCine/" if REPO == APP else ""
    # Keep CRLF bytes in Windows batch-file hunks; text=True normalizes them.
    patch = subprocess.check_output(["git", "-C", str(REPO), "diff", "--no-renames", "--binary",
                                     "--src-prefix=a/" + prefix, "--dst-prefix=b/" + prefix,
                                     f"{STABLE}...HEAD", "--", str(APP)])
    instructions = """# v5.10.13 GPU映像処理とホットフィックスの統合の差分

- 基準: `codex/lol-autocine-v51010-real-scene-handoff`（v5.10.10 RealScene GPUFull）
- テキスト変更ファイルは `LoL_AutoCine/` 以下。PNG素材は重複容量を避け、Git binary patchにのみ収録。パッチ適用でPNGも復元される。単なるファイル上書きでは統合が完了しない。
- Git推奨: 既存変更をコミットしてから差分を検査して適用する。GitHub取得用リポジトリのルートでは `git apply --check CHANGES_v5.10.13_PlayerFilter_GPUFull.patch` → `git apply CHANGES_v5.10.13_PlayerFilter_GPUFull.patch`。
- AutoCine単体のGitルート（直下にcore/やSTART.batがある構成）では `git apply --check -p2 CHANGES_v5.10.13_PlayerFilter_GPUFull.patch` → `git apply -p2 CHANGES_v5.10.13_PlayerFilter_GPUFull.patch`。
- 今回はv5.10.11〜v5.10.13の一括スキャン、対象切替、図鑑、カメラ、素材37種類と既存GPUへの設定接続を統合。変更検査後にGitパッチで適用するか、新しい完全版を別フォルダへ展開する。
- Codexが別途編集した `core/effects.py`、`core/gpu_pipeline.py`、`core/jobs.py`、`core/camera.py` 等はコンフリクト確認必須
- 音声のProcess Loopback、NVENC、TargetLock、UI設定の回帰テストを実施
- Windows/LoL/NVIDIA実機テストは配布前のLinux CIとは別に行う
"""
    with ZipFile(DIFF_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        # Binary assets are already contained in the applicable Git binary patch.
        # Avoid duplicate 50+MB PNG payloads exceeding GitHub file limits.
        write_manifest(z, sorted(p for p in changed if p.suffix.lower() != '.png'))
        z.writestr("CHANGES_v5.10.13_PlayerFilter_GPUFull.patch", patch)
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
