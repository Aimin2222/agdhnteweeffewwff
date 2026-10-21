"""Build the real AutoCine UI comparison EXE and its isolated WGC worker.

Run with the project's Windows virtualenv. The native audio helper is an
explicit input because it is built separately with MSVC from tools/native_audio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
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
        "LoL_AutoCine_UI29.exe",
        "LoL_AutoCine_Capture.exe",
        "_internal/VERSION.txt",
        "_internal/assets/work_kill_assets/catalog.json",
        "_internal/tools/bin/lol_audio_helper.exe",
        "_internal/design/ui/implementation_audit_29_20261021/SCREENS_29.json",
        "_internal/design/ui/ui_rethink_20261021/ui.css",
        "_internal/design/ui/ui29_legacy/legacy.css",
        "_internal/design/ui/ui29_legacy/reconstructed.css",
        "_internal/ui/audit29_client.js",
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
    parser.add_argument("--webview2-fixed-folder", type=Path,
                        help="Optional extracted official WebView2 Fixed Version folder")
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
        run("--onedir", "--windowed", "--name", "LoL_AutoCine_UI29", *common,
            "--collect-all", "webview", str(APP / "ui29_entry.py"))
        run("--onefile", "--console", "--name", "LoL_AutoCine_Capture", *common,
            str(APP / "tools" / "portable_capture_worker.py"))
    bundle = dist / "LoL_AutoCine"
    internal = bundle / "_internal"
    ui29_bundle = dist / "LoL_AutoCine_UI29"
    shutil.copy2(ui29_bundle / "LoL_AutoCine_UI29.exe", bundle / "LoL_AutoCine_UI29.exe")
    copy_tree(ui29_bundle / "_internal", internal)
    shutil.copy2(dist / "LoL_AutoCine_Capture.exe", bundle / "LoL_AutoCine_Capture.exe")
    for name in ("assets", "qa", "templates"):
        copy_tree(APP / name, internal / name)
    shutil.copy2(APP / "VERSION.txt", internal / "VERSION.txt")
    # The Codex-bundled Python runtime adds a local CA exclusion file to
    # SSLContext.__new__. Standard Python has no such file. Preserve that
    # runtime policy in frozen builds made with the bundled interpreter.
    rejected_cas = Path(ssl.__file__).with_name("codex-rejected-cas.pem")
    if rejected_cas.is_file():
        shutil.copy2(rejected_cas, internal / rejected_cas.name)
    for name in ("ui_rethink_20261021", "ui29_legacy"):
        copy_tree(APP / "design" / "ui" / name, internal / "design" / "ui" / name)
    audit = internal / "design" / "ui" / "implementation_audit_29_20261021"
    audit.mkdir(parents=True, exist_ok=True)
    shutil.copy2(APP / "design" / "ui" / "implementation_audit_29_20261021" / "SCREENS_29.json",
                 audit / "SCREENS_29.json")
    (internal / "ui").mkdir(parents=True, exist_ok=True)
    shutil.copy2(APP / "ui" / "audit29_client.js", internal / "ui" / "audit29_client.js")
    (internal / "tools" / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(helper, internal / "tools" / "bin" / helper.name)
    if args.webview2_fixed_folder:
        fixed = args.webview2_fixed_folder.resolve()
        if not (fixed / "msedgewebview2.exe").is_file():
            parser.error("--webview2-fixed-folder must contain msedgewebview2.exe")
        copy_tree(fixed, bundle / "WebView2Fixed")
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
                "ui29_total_screens": 29, "ui29_groups": 12,
                "ui29_partially_interactive_screens": 29,
                "ui29_accepted_screens": 0,
                "webview2_fixed_included": bool(args.webview2_fixed_folder),
                "source_commit": commit,
                "audio_helper_sha256": helper_hash,
                "note": "LoL/WGC/NVENC/audio require Windows hardware validation."}
    (bundle / "BUILD_INFO.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (bundle / "README_TEST_JA.txt").write_text(
        "LoL AutoCine UI比較テスト版（実動作・検証用）\n"
        "LoL_AutoCine.exe は現行の配置1～9です。従来のBAT起動もこの経路です。\n"
        "LoL_AutoCine_UI29.exe はWebView2内蔵のUI29比較版です。ブラウザ操作は不要です。\n"
        "UI29は29画面を操作できる途中版ですが、外観と全操作の合格は未完了です。\n"
        "LoL実機検証は未完了です。\n"
        + ("WebView2 Fixed Runtimeを同梱しています。Windows 10のフォルダ権限要件も確認してください。\n"
           if args.webview2_fixed_folder else
           "WindowsのMicrosoft Edge WebView2 Runtimeが必要です（このZIPには未同梱）。\n")
        + "同梱のLoL_AutoCine_Capture.exeはミラー用です。削除しないでください。\n"
        "リプレイ接続・NVENC・ゲーム音声は各PCで実機確認が必要です。\n"
        "操作順はGitHubのdocs/ui_integration_20261020/TEST_GUIDE_JA.mdを参照してください。\n",
        encoding="utf-8")
    validate_bundle(bundle)
    # A windowed PyInstaller process can stay open on an exception dialog;
    # explicitly test import/resources with a terminating non-GUI entry path.
    subprocess.run([str(bundle / "LoL_AutoCine.exe"), "--smoke-test"],
                   cwd=bundle, timeout=30, check=True)
    subprocess.run([str(bundle / "LoL_AutoCine_UI29.exe"), "--ui29-smoke"],
                   cwd=bundle, timeout=60, check=True)
    subprocess.run([str(bundle / "LoL_AutoCine_Capture.exe"), "--help"],
                   cwd=bundle, timeout=30, check=True, stdout=subprocess.DEVNULL)
    target = output / "LoL_AutoCine_UI_Comparison_Portable.zip"
    make_zip(bundle, target)
    print(target)


if __name__ == "__main__":
    main()
