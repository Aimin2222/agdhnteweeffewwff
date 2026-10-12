# -*- coding: utf-8 -*-
"""CI guard against common Windows Japanese mojibake regression.

Inspect the tracked source text, not binary media. Do not blindly re-encode
files and risk corrupting user data. Windows cmd launchers must be 7-bit ASCII
so the active legacy OEM code page cannot misparse batch labels/commands.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

TEXT_SUFFIXES = {
    ".py", ".json", ".md", ".txt", ".yml", ".yaml", ".toml",
    ".ini", ".cfg", ".bat", ".cmd", ".ps1", ".html", ".css", ".js",
}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "build", "dist", "diagnostics"}


def audit(root: Path) -> list[str]:
    root = Path(root).resolve()
    try:
        git_root = Path(subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
        ).decode().strip()).resolve()
        raw = subprocess.check_output(["git", "-C", str(git_root), "ls-files", "-z", "--", str(root)])
        paths = [git_root / Path(b.decode("utf-8", "surrogateescape")) for b in raw.split(b"\0") if b]
    except (OSError, subprocess.CalledProcessError):
        paths = list(root.rglob("*"))
    problems = []
    for path in paths:
        if path.is_symlink():
            continue
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.stat().st_size > 5_000_000:
            continue
        payload = path.read_bytes()
        try:
            body = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            problems.append(f"{path}: source file is not UTF-8: {exc}")
            continue
        if "\ufffd" in body:
            problems.append(f"{path}: contains Unicode replacement character")
        if path.suffix.lower() in {".bat", ".cmd"} and any(byte > 0x7f for byte in payload):
            problems.append(f"{path}: Windows cmd script must be ASCII-only")
    return problems


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    issues = audit(base)
    for issue in issues:
        print("[ENCODING ERROR]", issue)
    if issues:
        print(f"[ENCODING] {len(issues)} problem(s)")
        return 1
    print("[ENCODING] All tracked AutoCine source files UTF-8; BAT/CMD ASCII")
    return 0


if __name__ == "__main__":
    sys.exit(main())
