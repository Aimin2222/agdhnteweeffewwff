# -*- coding: utf-8 -*-
"""Single-layer, size-bounded ZIP exports for opt-in AutoCine camera QA."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import zipfile

DEFAULT_MAX_BYTES = 500_000_000
# 475MB payload target leaves ample room for headers and manifest; compressed
# already-encoded MP4s are stored, not deflated again.
SAFETY_BYTES = 25_000_000
CHUNK_BYTES = 420_000_000


def split_test_results(folder: Path, *, max_bytes: int = DEFAULT_MAX_BYTES,
                       log=lambda _m: None) -> list[Path]:
    """Pack MP4s and reports as independent ZIPs of strictly <= max_bytes.

    QA ZIPs never contain ZIPs. A >max-size original is chunked into .part
    files with a restoration note; original MP4 on disk is never modified.
    """
    folder = Path(folder)
    max_bytes = int(max_bytes)
    if max_bytes <= 1_000_000:
        raise ValueError("max_bytes must be greater than 1MB")
    limit = max_bytes - min(SAFETY_BYTES, max_bytes // 12)
    chunk_bytes = min(CHUNK_BYTES, max(512_000, limit - 5_000_000))
    sources = sorted(p for p in folder.rglob("*") if p.is_file()
                     and p.suffix.lower() in {".mp4", ".json", ".txt", ".md", ".csv", ".jpg", ".png"})
    if not sources:
        return []
    outputs = []
    current = []
    used = 0
    temporary_parts = []
    restoration = []

    def add_file(item: Path, name: str):
        nonlocal used, current
        cost = item.stat().st_size + 4096 + len(name.encode("utf-8"))
        if cost > limit:
            raise RuntimeError(f"archive item exceeds maximum: {name}")
        if current and used + cost > limit:
            finish()
        current.append((item, name))
        used += cost

    def finish():
        nonlocal used, current
        if not current:
            return
        target = folder / f"{folder.name}_part{len(outputs)+1:03d}.zip"
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for path, name in current:
                archive.write(path, name)
        if target.stat().st_size > max_bytes:
            target.unlink(missing_ok=True)
            raise RuntimeError("Produced archive exceeded the maximum size")
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise RuntimeError(f"CRC failed: {target}")
        outputs.append(target)
        log(f"QA ZIP完成: {target.name} / {target.stat().st_size/1_000_000:.1f}MB")
        current, used = [], 0

    try:
        for path in sources:
            rel = path.relative_to(folder).as_posix()
            if path.stat().st_size + 4096 <= limit:
                add_file(path, rel)
                continue
            # Oversized MP4 is chunked without corrupting or deleting the source.
            n = 0
            with path.open("rb") as inp:
                while True:
                    piece = inp.read(chunk_bytes)
                    if not piece:
                        break
                    n += 1
                    part = folder / f".qa_split_{len(temporary_parts):05d}.part"
                    part.write_bytes(piece)
                    temporary_parts.append(part)
                    add_file(part, f"{rel}.part{n:03d}")
            restoration.append({"original": rel, "parts": n,
                                "instruction": "Restore by binary concatenation in numeric part order."})
        if restoration:
            note = folder / ".qa_restoration_notes.txt"
            note.write_text(json.dumps(restoration, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary_parts.append(note)
            add_file(note, "RESTORE_OVERSIZED_FILES.txt")
        finish()
        return outputs
    finally:
        for p in temporary_parts:
            p.unlink(missing_ok=True)
