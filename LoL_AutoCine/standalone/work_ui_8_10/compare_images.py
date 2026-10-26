"""Pixel comparison between Work reference images and Windows app captures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageChops, ImageStat


HERE = Path(__file__).resolve().parent
REFERENCE = (HERE.parents[1] / "research" / "integrated_20261022" /
             "v4_continuation_20261026" / "ui" / "screens")
SAVE_IMAGES = {"P1-main", "P1-easy", "P1-detail", "P1-camera", "P1-material",
               "P1-timeline", "P1-small", "P1-dark", "P2-flow", "P2-small",
               "P2-dark", "P3-library", "POP-camera", "POP-frames", "POP-output",
               "POP-compare"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for capture in sorted(args.captures.glob("*.png")):
        source = REFERENCE / capture.name
        if not source.is_file():
            raise FileNotFoundError(source)
        with Image.open(source) as ref_file, Image.open(capture) as app_file:
            reference = ref_file.convert("RGB")
            actual = app_file.convert("RGB")
            if reference.size != actual.size:
                raise AssertionError(f"{capture.name}: {reference.size} != {actual.size}")
            diff = ImageChops.difference(reference, actual)
            mean = ImageStat.Stat(diff).mean
            gray = diff.convert("L")
            changed = sum(v for i, v in enumerate(gray.histogram()) if i > 20)
            total = reference.width * reference.height
            row = {"id": capture.stem, "size": list(reference.size),
                   "mean_absolute_rgb": round(sum(mean) / 3, 3),
                   "pixels_difference_gt20_pct": round(100 * changed / total, 3),
                   "reference": str(source), "capture": str(capture)}
            rows.append(row)
            if capture.stem in SAVE_IMAGES:
                folder = args.output / capture.stem
                folder.mkdir(exist_ok=True)
                copy2(source, folder / "reference.png")
                copy2(capture, folder / "windows_app.png")
                Image.blend(reference, actual, 0.5).save(folder / "overlay_50.png")
                diff.save(folder / "absolute_difference.png")
    report = {"kind": "WORK_REFERENCE_VS_WINDOWS_APP", "source_commit":
              "6ab57afee2e236e50833c6e15022484fb84b79e7",
              "comparison_note": "Candidate names intentionally changed to 8–10; pixel differences include text rendering and WebView2/Chromium differences.",
              "screens": rows}
    (args.output / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    print(f"compared={len(rows)} overlays={len(SAVE_IMAGES & {row['id'] for row in rows})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
