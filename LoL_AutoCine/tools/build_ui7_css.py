"""Create the seven-candidate Flow stylesheet from the archived research CSS.

The source remains as a design record. The comparison EXE ships only the
common and Flow (E) selectors; removed candidates have no active CSS.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "design/ui/ui_rethink_20261021"
EXCLUDED = re.compile(r"\.layout-[ABCDF](?=[\s.#:\[,]|$)")


def blocks(source: str):
    position = 0
    while position < len(source):
        opening = source.find("{", position)
        if opening < 0:
            break
        header = source[position:opening].strip()
        depth = 1
        end = opening + 1
        while end < len(source) and depth:
            if source[end] == "{":
                depth += 1
            elif source[end] == "}":
                depth -= 1
            end += 1
        if depth:
            raise ValueError("unbalanced CSS")
        yield header, source[opening + 1:end - 1]
        position = end


def select(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    output = []
    for header, body in blocks(source):
        if header.startswith("@"):
            nested = select(body)
            if nested:
                output.append(f"{header}{{{nested}}}")
        else:
            selectors = [item.strip() for item in header.split(",")
                         if item.strip() and not EXCLUDED.search(item)]
            if selectors:
                output.append(f"{','.join(selectors)}{{{body}}}")
    return "\n".join(output)


def main():
    result = select((ROOT / "ui.css").read_text(encoding="utf-8"))
    if ".layout-E" not in result or ".layout-materials" not in result or EXCLUDED.search(result):
        raise RuntimeError("seven-candidate CSS validation failed")
    (ROOT / "ui7.css").write_text(result + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
