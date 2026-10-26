"""Build the isolated Issue #53 functional Windows executable and ZIP.

Run using the development Python with PyInstaller installed. Outputs are kept
outside the Git checkout. This never modifies the legacy EXE or BAT launchers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import sys
import zipfile


APP = Path(__file__).resolve().parents[1]
NAME = "LoL_AutoCine_Issue53_Test"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    helper = APP / "tools" / "bin" / "lol_audio_helper.exe"
    if not helper.is_file():
        raise SystemExit("Native LoL audio helper is missing; build it before packaging")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm",
               "--onedir", "--windowed", "--name", NAME,
               "--distpath", str(output / "dist"),
               "--workpath", str(output / "pyinstaller-work"),
               "--specpath", str(output),
               "--add-data", f"{APP / 'VERSION.txt'};.",
               "--add-data", f"{APP / 'assets'};assets",
               "--add-data", f"{APP / 'templates'};templates",
               "--add-data", f"{APP / 'core' / 'capture_worker.py'};core",
               "--add-binary", f"{helper};tools/bin",
               "--collect-all", "windows_capture",
               "--collect-all", "pycaw",
               "--collect-all", "yt_dlp",
               str(APP / "issue53_launcher.py")]
    # Some managed Python runtimes patch ssl.SSLContext to read this file next
    # to ssl.py. Include it only when that runtime actually supplies it.
    managed_ca = Path(ssl.__file__).with_name("codex-rejected-cas.pem")
    if managed_ca.is_file():
        command[3:3] = ["--add-data", f"{managed_ca};."]
    subprocess.run(command, cwd=APP, check=True)
    bundle = output / "dist" / NAME
    exe = bundle / f"{NAME}.exe"
    if not exe.is_file():
        raise RuntimeError(f"PyInstaller did not create {exe}")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=APP, text=True).strip()
    status = {
        "source_commit": revision,
        "entry_point": f"{NAME}.exe",
        "research_flash": "causal_pts_v1 opt-in",
        "research_zoom": "normalized_tmix_v1 opt-in",
        "real_lol_test": "NOT_RUN until a replay is supplied and executed",
    }
    (bundle / "BUILD_INFO.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    guide = APP / "docs" / "ISSUE53_WINDOWS_TEST_JA.md"
    if guide.is_file():
        (bundle / "TEST_GUIDE_JA.md").write_bytes(guide.read_bytes())
    archive = output / f"{NAME}_Portable.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as dest:
        for path in sorted(bundle.rglob("*")):
            if path.is_file():
                dest.write(path, path.relative_to(output / "dist"))
    with zipfile.ZipFile(archive) as reader:
        if reader.testzip() is not None:
            raise RuntimeError("Portable ZIP CRC check failed")
    digest_state = hashlib.sha256()
    with archive.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest_state.update(block)
    digest = digest_state.hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(json.dumps({"exe": str(exe), "zip": str(archive), "sha256": digest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
