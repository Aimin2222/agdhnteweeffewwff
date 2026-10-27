"""Build an isolated source/BAT trial for the provisional UI3 integration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


APP = Path(__file__).resolve().parents[1]
REPO = APP.parent
ROOT_BATS = {"START_AUTOCINE_UI3.bat", "START.bat", "BUILD_AUDIO_HELPER.bat",
             "ENSURE_CPP_BUILD_TOOLS.bat", "COLLECT_DIAGNOSTICS.bat"}
SKIP_PARTS = {"qa", "qa_tmp", "ui3_data", "diagnostics", "projects", "output",
              "outputs", "tests", "__pycache__", ".venv", ".pytest_cache"}
SKIP_SUFFIXES = {".log", ".mp4", ".mkv", ".wav", ".pyc"}
SKIP_NAMES = {"settings.json", "issue53_launcher.py"}


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def archive_name(name: str) -> str:
    path = Path(name)
    if len(path.parts) == 2 and path.suffix.lower() == ".bat" and path.name not in ROOT_BATS:
        return f"LoL_AutoCine/Developer_Tools/{path.name}"
    return name.replace("\\", "/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    helper = APP / "tools" / "bin" / "lol_audio_helper.exe"
    if not helper.is_file():
        raise SystemExit("Native LoL audio helper is missing")
    names = subprocess.check_output(
        ["git", "-C", str(REPO), "ls-files", "-z", "--", "LoL_AutoCine"]
    ).decode("utf-8").split("\0")
    # Include only the reviewed C3/three-view acceptance evidence; all other QA/runtime
    # folders remain excluded because they may contain replay paths or logs.
    files = [name for name in names if name and (REPO / name).is_file()
             and (not SKIP_PARTS.intersection(Path(name).parts)
                  or name.startswith("LoL_AutoCine/qa/c3_acceptance_20261027/")
                  or name.startswith("LoL_AutoCine/qa/ui3_three_views_20261028/"))
             and Path(name).name not in SKIP_NAMES
             and Path(name).suffix.lower() not in SKIP_SUFFIXES
             and not name.startswith("LoL_AutoCine/design/ui/implementation_audit_29_")]
    launcher = "LoL_AutoCine/START_AUTOCINE_UI3.bat"
    if launcher not in files:
        raise SystemExit("Commit START_AUTOCINE_UI3.bat before packaging")
    bat = (REPO / launcher).read_bytes()
    if b"\r\n" not in bat or b"\n" in bat.replace(b"\r\n", b""):
        raise SystemExit("The UI3 BAT must use CRLF exclusively")
    info = {"source_commit": git("rev-parse", "HEAD"),
            "source_version": (APP / "VERSION.txt").read_text(encoding="utf-8").strip(),
            "entry_point": launcher, "distribution": "Windows source/BAT trial, no new EXE",
            "work_feature_audit": "70 rows; see docs/ui3/C3_ACCEPTANCE70_IMPLEMENTATION_20261027.csv",
            "work_acceptance": "284 cases; see qa/ui3_three_views_20261028/ACCEPTANCE_RESULTS_284.json",
            "ui_variants": "candidate3 T-A-M, League Director R1, Lolnam R2",
            "live_lol_result": "NOT_RUN"}
    archive = output / "LoL_AutoCine_UI3_Trial_BAT.zip"
    manifest = []
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=3,
                 allowZip64=True) as dest:
        for name in sorted(files):
            path = REPO / name
            data = path.read_bytes()
            target = archive_name(name)
            if target != name and path.suffix.lower() == ".bat":
                data = data.replace(b"%~dp0", b"%~dp0..\\")
            dest.writestr(target, data,
                          compress_type=ZIP_STORED if path.suffix.lower() in
                          {".png", ".jpg", ".jpeg"} else ZIP_DEFLATED)
            manifest.append({"path": target, "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()})
        helper_bytes = helper.read_bytes()
        helper_name = "LoL_AutoCine/tools/bin/lol_audio_helper.exe"
        dest.writestr(helper_name, helper_bytes, compress_type=ZIP_STORED)
        manifest.append({"path": helper_name, "bytes": len(helper_bytes),
                         "sha256": hashlib.sha256(helper_bytes).hexdigest()})
        dest.writestr("LoL_AutoCine/BUILD_INFO.json",
                      json.dumps(info, ensure_ascii=False, indent=2).encode("utf-8"))
        dest.writestr("README_TEST_JA.txt",
                      ("候補3の暫定機能統合版です。正式採用・実LoL合格ではありません。\n"
                       "ZIPを別フォルダに展開し、LoL_AutoCine/START_AUTOCINE_UI3.batをダブルクリック。\n"
                       "Python 3.12 x64とrequirements.txtの依存が必要です。\n"
                       "詳細: LoL_AutoCine/docs/ui3/README_UI3_TEST_JA.md\n"
                       "Work受入284件: LoL_AutoCine/qa/ui3_three_views_20261028/ACCEPTANCE_RESULTS_284.json\n"
                       "旧画面はSTART.batから起動できます。\n").encode("utf-8"))
    with ZipFile(archive) as reader:
        bad = reader.testzip()
        if bad:
            raise RuntimeError(f"UI3 ZIP CRC failed: {bad}")
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    sha = digest.hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{sha}  {archive.name}\n", encoding="utf-8")
    (output / "PACKAGE_MANIFEST.json").write_text(
        json.dumps({"build": info, "files": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"zip": str(archive), "sha256": sha,
                      "files": len(manifest), "commit": info["source_commit"]}))


if __name__ == "__main__":
    main()
