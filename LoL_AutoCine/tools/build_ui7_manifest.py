"""Freeze only the seven selected candidate families for the comparison app.

The original 29-screen audit stays in Git as reference material. It is not a
runtime inventory or a packaged asset in this seven-candidate edition.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design/ui/implementation_audit_29_20261021/SCREENS_29.json"
TARGET = ROOT / "ui/comparison7_screens.json"

FAMILIES = ("testB", "legacy03", "testA", "legacy06", "researchE", "legacy02", "legacy05")
EXPECTED = {"T-B-M", "T-B-C", "T-B-F", "T-B-S", "L03-N", "L03-D", "T-A-M",
            "L06-L", "L06-E", "R-E-main", "R-E-studio", "R-E-frames",
            "R-E-main-dark", "R-E-main-1366x768", "L02-M", "L05-M"}


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = [row for row in rows if row["family"] in FAMILIES]
    if {row["id"] for row in selected} != EXPECTED or {row["family"] for row in selected} != set(FAMILIES):
        raise RuntimeError("seven-candidate inventory no longer matches the audit")
    TARGET.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
