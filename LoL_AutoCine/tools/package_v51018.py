# -*- coding: utf-8 -*-
"""Reproducible v5.10.17 CameraEvidence_BadgeQA GPUFull full & Codex-diff ZIPs. Run from a Git checkout.

Usage: python LoL_AutoCine/tools/package_v51018.py
Prerequisite: git fetch origin codex/lol-autocine-v51017-camera-evidence-badgeqa-handoff
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
BASE_REFS = (("integration/v5.10.17", "origin/integration/v5.10.17") if REPO == APP else
             ("origin/codex/lol-autocine-v51017-camera-evidence-badgeqa-handoff",))
STABLE = next((ref for ref in BASE_REFS if subprocess.run(
    ["git", "-C", str(REPO), "rev-parse", "--verify", ref + "^{commit}"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0), None)
if STABLE is None:
    raise RuntimeError("Codex v5.10.16基準がありません。元のbundleから復元するか基準ブランチをfetchしてください。")
EXCLUDED_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules", "output", "outputs", "projects", "thumbnails"}
EXCLUDED_SUFFIXES = {".mp4", ".mkv", ".wav", ".avi", ".mov", ".webm", ".pyc", ".log", ".tmp"}
PACKAGE_NAME = "LoL_AutoCine_v5.10.18_ReleaseQA_DirectZIP_GPUFull"
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
    if version != "5.10.18-test":
        raise RuntimeError(f"VERSION.txt is not 5.10.18-test: {version}")
    DIST.mkdir(exist_ok=True)
    tracked = run_git("ls-files", "-z", "--", str(APP)).rstrip("\0").split("\0")
    allfiles = sorted(REPO / name for name in tracked if name and in_package(REPO / name))
    assert len(allfiles) >= 90, f"Suspiciously incomplete source: {len(allfiles)} files"
    with ZipFile(FULL_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        write_manifest(z, allfiles)

    diff_names = run_git("diff", "--no-renames", "--name-only", "-z", f"{STABLE}...HEAD", "--", str(APP)).rstrip("\0").split("\0")
    changed = [REPO / name for name in diff_names if name and in_package(REPO / name)]
    if not changed or not any(p.as_posix().endswith("core/camera_qa.py") for p in changed):
        raise RuntimeError("Expected v5.10.16 source changes are missing in the diff")
    prefix = "LoL_AutoCine/" if REPO == APP else ""
    # Keep CRLF bytes in Windows batch-file hunks; text=True normalizes them.
    patch = subprocess.check_output(["git", "-C", str(REPO), "diff", "--no-renames", "--binary",
                                     "--src-prefix=a/" + prefix, "--dst-prefix=b/" + prefix,
                                     f"{STABLE}...HEAD", "--", str(APP)])
    instructions = """# v5.10.18-test ReleaseQA / DirectZIP / GPUFull 差分

- 基準は前回Codex v5.10.17-test（codex/lol-autocine-v51017-camera-evidence-badgeqa-handoff）。
- 別版へ丸ごと上書きせず、変更を保存してgit apply --check CHANGES_v5.10.18_ReleaseQA_DirectZIP_GPUFull.patch、その後git apply。単体AutoCine Gitでは-p2を追加。
- 完全版は旧版と別フォルダへ展開。設定/録画は削除しない。
- 内容・実機確認: docs/CODEX_INTEGRATION_v51018_JA.md、docs/WINDOWS_TEST_v51018_JA.md。
"""
    with ZipFile(DIFF_ZIP, "w", ZIP_DEFLATED, compresslevel=6) as z:
        # Binary assets are already contained in the applicable Git binary patch.
        # Avoid duplicate 50+MB PNG payloads exceeding GitHub file limits.
        write_manifest(z, sorted(p for p in changed if p.suffix.lower() != '.png'))
        z.writestr("CHANGES_v5.10.18_ReleaseQA_DirectZIP_GPUFull.patch", patch)
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
