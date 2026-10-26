"""Re-render the 18 *source HTML* screens; this is not live UI acceptance.

The result detects missing assets, viewport/theme drift, and non-reproducible
references before connecting real AutoCine state. Runtime screenshots are
reviewed separately with ui29_review.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import time

import numpy as np
from PIL import Image

from ui29_review import AUDIT, ROOT, load_inventory


DESIGN = ROOT / "design" / "ui" / "ui_rethink_20261021"
EDGE_PATHS = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


def capture_source(screen: dict, edge: Path, output: Path) -> dict:
    width, height = screen["resolution"]
    source = DESIGN / screen["html"]
    if not source.is_file():
        return {"id": screen["id"], "result": "MISSING_SOURCE"}
    uri = source.resolve().as_uri() + f'?capture=1&theme={screen["theme"]}'
    with tempfile.TemporaryDirectory(dir=output.parent) as profile:
        command = [str(edge), "--headless", "--disable-gpu", "--no-first-run",
                   "--no-default-browser-check", "--hide-scrollbars",
                   f"--user-data-dir={profile}", f"--window-size={width},{height}",
                   f"--screenshot={output}", uri]
        try:
            run = subprocess.run(command, timeout=45, capture_output=True, text=True)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"id": screen["id"], "result": "CAPTURE_FAILED", "error": str(exc)}
        for _ in range(50):
            if output.is_file() and output.stat().st_size:
                break
            time.sleep(.1)
        if not output.is_file():
            return {"id": screen["id"], "result": "CAPTURE_FAILED",
                    "exit_code": run.returncode, "stderr": run.stderr[-500:]}
    with Image.open(AUDIT / screen["reference"]) as expected, Image.open(output) as actual:
        a, b = expected.convert("RGB"), actual.convert("RGB")
        if a.size != b.size:
            return {"id": screen["id"], "result": "SIZE_MISMATCH",
                    "expected": list(a.size), "actual": list(b.size)}
        delta = np.abs(np.asarray(a, dtype=np.int16) - np.asarray(b, dtype=np.int16))
        return {"id": screen["id"], "result": "MEASURED", "size": list(a.size),
                "full_rgb_mae": round(float(delta.mean()), 4),
                "exact_pixel_percent": round(float(np.mean(np.all(delta == 0, axis=2))) * 100, 3),
                "note": "設計元HTMLの再現性。ライブUIの見た目・実機動作の合格ではない"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, default=next((p for p in EDGE_PATHS if p.is_file()), None))
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "ui29" / "source_baseline")
    parser.add_argument("--keep-captures", action="store_true")
    args = parser.parse_args(argv)
    if not args.edge or not args.edge.is_file():
        parser.error("Microsoft Edge executable was not found")
    rows = [x for x in load_inventory() if x["group"] == "research"]
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for row in rows:
        capture = args.output / f"{row['id']}.png"
        result = capture_source(row, args.edge, capture)
        print(row["id"], result["result"], result.get("full_rgb_mae"))
        results.append(result)
        if not args.keep_captures:
            capture.unlink(missing_ok=True)
    report = {"kind": "SOURCE_HTML_REPRODUCTION_ONLY", "screens": results,
              "screen_count": len(rows), "live_visual_acceptance": "NOT_RUN",
              "lol_functional_acceptance": "NOT_RUN"}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if len(rows) == 18 and all(x["result"] == "MEASURED" for x in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
