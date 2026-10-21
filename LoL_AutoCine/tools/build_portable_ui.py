"""Build the real AutoCine UI comparison EXE and its isolated WGC worker.

Run with the project's Windows virtualenv. The native audio helper is an
explicit input because it is built separately with MSVC from tools/native_audio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

APP = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", *args], cwd=APP, check=True)


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def make_zip(folder: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent))
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failed: {bad}")


def validate_bundle(bundle: Path) -> None:
    required = (
        "LoL_AutoCine.exe",
        "LoL_AutoCine_Capture.exe",
        "_internal/VERSION.txt",
        "_internal/assets/work_kill_assets/catalog.json",
        "_internal/tools/bin/lol_audio_helper.exe",
    )
    missing = [name for name in required if not (bundle / name).is_file()]
    ffmpeg = list((bundle / "_internal" / "imageio_ffmpeg" / "binaries").glob("ffmpeg-*.exe"))
    if not ffmpeg:
        missing.append("_internal/imageio_ffmpeg/binaries/ffmpeg-*.exe")
    if missing:
        raise RuntimeError("Portable bundle missing required files: " + ", ".join(missing))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-helper", type=Path, required=True, help="MSVC-built lol_audio_helper.exe")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--package-only", action="store_true", help="Reuse already built EXEs")
    args = parser.parse_args()
    helper = args.audio_helper.resolve()
    if not helper.is_file() or helper.name.lower() != "lol_audio_helper.exe":
        parser.error("--audio-helper must point to an existing lol_audio_helper.exe")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    dist = output / "dist"
    work = output / "pyinstaller_work"
    spec = output / "pyinstaller_spec"
    common = ("--distpath", str(dist), "--workpath", str(work), "--specpath", str(spec),
              "--paths", str(APP), "--collect-all", "windows_capture",
              "--collect-all", "imageio_ffmpeg", "--collect-all", "pycaw",
              "--collect-all", "pyaudiowpatch", "--hidden-import", "yt_dlp")
    if not args.package_only:
        run("--onedir", "--windowed", "--name", "LoL_AutoCine", *common, str(APP / "app.py"))
        run("--onefile", "--console", "--name", "LoL_AutoCine_Capture", *common,
            str(APP / "tools" / "portable_capture_worker.py"))
    bundle = dist / "LoL_AutoCine"
    internal = bundle / "_internal"
    shutil.copy2(dist / "LoL_AutoCine_Capture.exe", bundle / "LoL_AutoCine_Capture.exe")
    for name in ("assets", "qa", "templates"):
        copy_tree(APP / name, internal / name)
    shutil.copy2(APP / "VERSION.txt", internal / "VERSION.txt")
    (internal / "tools" / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(helper, internal / "tools" / "bin" / helper.name)
    guide = APP / "docs" / "ui_integration_20261020" / "TEST_GUIDE_JA.md"
    shutil.copy2(guide, bundle / "TEST_GUIDE_JA.md")
    for name in ("settings.json", "diagnostics"):
        path = internal / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    helper_hash = hashlib.sha256(helper.read_bytes()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=APP, text=True).strip()
    manifest = {"kind": "working AutoCine UI comparison", "layouts": list(range(1, 10)),
                "source_commit": commit,
                "audio_helper_sha256": helper_hash,
                "note": "LoL/WGC/NVENC/audio require Windows hardware validation."}
    (bundle / "BUILD_INFO.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (bundle / "README_TEST_JA.txt").write_text(
        "LoL AutoCine UI比較テスト版（実動作・検証用）\n"
        "LoL_AutoCine.exe を起動してください。配置1～9は上部で切替できます。\n"
        "同梱のLoL_AutoCine_Capture.exeはミラー用です。削除しないでください。\n"
        "リプレイ接続・NVENC・ゲーム音声は各PCで実機確認が必要です。\n"
        "操作順はGitHubのdocs/ui_integration_20261020/TEST_GUIDE_JA.mdを参照してください。\n",
        encoding="utf-8")
    validate_bundle(bundle)
    # A windowed PyInstaller process can stay open on an exception dialog;
    # explicitly test import/resources with a terminating non-GUI entry path.
    subprocess.run([str(bundle / "LoL_AutoCine.exe"), "--smoke-test"],
                   cwd=bundle, timeout=30, check=True)
    subprocess.run([str(bundle / "LoL_AutoCine_Capture.exe"), "--help"],
                   cwd=bundle, timeout=30, check=True, stdout=subprocess.DEVNULL)
    target = output / "LoL_AutoCine_UI_Comparison_Portable.zip"
    make_zip(bundle, target)
    print(target)


if __name__ == "__main__":
    main()
