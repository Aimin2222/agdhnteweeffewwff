"""Build a separate portable Windows app for Work candidates 8–10."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
APP_NAME = "AutoCine_Work_UI_8_10"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--webview2-fixed-folder", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    fixed = args.webview2_fixed_folder.resolve()
    if not (fixed / "msedgewebview2.exe").is_file():
        parser.error("--webview2-fixed-folder must be a Microsoft Fixed Version runtime folder")
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onedir", "--windowed", "--name", APP_NAME,
               "--distpath", str(output / "dist"),
               "--workpath", str(output / "pyinstaller_work"),
               "--specpath", str(output / "pyinstaller_spec"),
               "--paths", str(HERE), "--collect-all", "webview",
               "--add-data", f"{HERE / 'web'};work_ui_web",
               str(HERE / "launcher.py")]
    subprocess.run(command, cwd=HERE, check=True)
    bundle = output / "dist" / APP_NAME
    shutil.copytree(fixed, bundle / "WebView2Fixed")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE,
                                     text=True).strip()
    info = {"app": APP_NAME, "kind": "standalone UI experience mock",
            "work_reference_commit": "6ab57afee2e236e50833c6e15022484fb84b79e7",
            "source_commit": commit, "candidates": ["候補8", "候補9", "候補10"],
            "real_lol_connection": False, "recording_export_gpu_audio": False,
            "webview2_fixed_version_bundled": True}
    (bundle / "BUILD_INFO.json").write_text(json.dumps(info, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    (bundle / "README_TEST_JA.txt").write_text(
        "LoL AutoCine — 候補8〜10 UI体験版\n\n"
        f"{APP_NAME}.exe を起動してください。Chrome・Edge・localhostの操作は不要です。\n"
        "『候補を比較』で候補8・9・10を切り替えます。上部から簡単編集・詳細編集・カメラ・素材・タイムラインを開けます。\n"
        "ライト/ダーク、ポップアップ、数値入力とスライダーを試せます。\n\n"
        "これは独立したUI研究用モックです。AutoCine本体や候補1〜7の設定を変更しません。\n"
        "LoL接続、スキャン、録画、GPU/NVENC、音声、動画出力は実行しません。画面中の映像とシーンは見本です。\n"
        "Microsoft WebView2 Fixed Runtime x64を同梱しています。Fixed Runtimeは自動更新されません。\n"
        "WebView2配布条件: https://developer.microsoft.com/en-us/microsoft-edge/webview2/\n",
        encoding="utf-8")
    required = [bundle / f"{APP_NAME}.exe", bundle / "_internal" / "work_ui_web" /
                "index.html", bundle / "WebView2Fixed" / "msedgewebview2.exe"]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    target = output / f"{APP_NAME}_Portable.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for path in bundle.rglob("*"):
            if path.is_file():
                archive.write(path, Path(APP_NAME) / path.relative_to(bundle))
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failed: {bad}")
    print(json.dumps({"zip": str(target), "bytes": target.stat().st_size,
                      "sha256": sha256(target)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
