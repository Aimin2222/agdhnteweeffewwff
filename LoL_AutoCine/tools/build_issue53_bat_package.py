"""Package the Issue #53 developer BAT workflow, without a frozen executable.

Tracked AutoCine source is copied from this dedicated worktree. The locally
built native audio helper is the only intentional untracked binary. Personal
settings, projects, recordings, and diagnostics are never included.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


APP = Path(__file__).resolve().parents[1]
REPO = APP.parent
ROOT_BATS = {
    "START.bat", "START_GPU.bat", "START_LOCAL_GPU.bat",
    "START_ISSUE53_DEV_QA.bat", "BUILD_AUDIO_HELPER.bat",
    "ENSURE_CPP_BUILD_TOOLS.bat", "COLLECT_DIAGNOSTICS.bat",
}
SKIP_PARTS = {"diagnostics", ".venv", "__pycache__", ".pytest_cache",
              "projects", "output", "outputs", "qa_tmp"}
SKIP_SUFFIXES = {".log", ".mp4", ".mkv", ".wav", ".pyc"}


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
        raise SystemExit("Native LoL audio helper is missing; build it before packaging")
    names = subprocess.check_output(
        ["git", "-C", str(REPO), "ls-files", "-z", "--", "LoL_AutoCine"]
    ).decode("utf-8").split("\0")
    files = [name for name in names if name and (REPO / name).is_file()
             and not SKIP_PARTS.intersection(Path(name).parts)
             and Path(name).name != "settings.json"
             and Path(name).suffix.lower() not in SKIP_SUFFIXES]
    launcher = "LoL_AutoCine/START_ISSUE53_DEV_QA.bat"
    if launcher not in files:
        raise SystemExit("Commit the Issue #53 BAT launcher before building")
    info = {
        "source_commit": git("rev-parse", "HEAD"),
        "source_version": (APP / "VERSION.txt").read_text(encoding="utf-8").strip(),
        "distribution": "developer source/BAT; no frozen EXE",
        "entry_point": "LoL_AutoCine/START_ISSUE53_DEV_QA.bat",
        "one_click_qa": "in-app developer camera + Work assets QA button",
        "live_lol_result": "NOT_RUN by package creation",
    }
    archive = output / "LoL_AutoCine_Issue53_Developer_BAT.zip"
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
                          compress_type=ZIP_STORED if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
                          else ZIP_DEFLATED)
            manifest.append({"path": target, "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()})
        helper_data = helper.read_bytes()
        helper_name = "LoL_AutoCine/tools/bin/lol_audio_helper.exe"
        dest.writestr(helper_name, helper_data, compress_type=ZIP_STORED)
        manifest.append({"path": helper_name, "bytes": len(helper_data),
                         "sha256": hashlib.sha256(helper_data).hexdigest()})
        dest.writestr("LoL_AutoCine/BUILD_INFO.json",
                      json.dumps(info, ensure_ascii=False, indent=2).encode("utf-8"))
        dest.writestr("README_TEST_JA.txt",
                      ("Issue #53 開発用BAT版。旧版・比較版とは別の短いパスへ展開してください。\n"
                       "LoL_AutoCine/START_ISSUE53_DEV_QA.bat を起動し、LoLリプレイ再生後、"
                       "画面内の『開発用：カメラ＋Work素材一括QA・30MB ZIP』を1回押します。\n"
                       "従来Flash/Zoomと比較する場合は、このBATを引数 legacy で実行します。\n"
                       "詳しい手順と未検証範囲は LoL_AutoCine/docs/ISSUE53_WINDOWS_TEST_JA.md。\n"
                       "Python 3.12 x64と依存パッケージは既存START.batの方法で準備します。\n"
                       "Native LoL音声helperは同梱しています。\n").encode("utf-8"))
    with ZipFile(archive) as reader:
        if reader.testzip() is not None:
            raise RuntimeError("Issue #53 BAT ZIP CRC failed")
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
