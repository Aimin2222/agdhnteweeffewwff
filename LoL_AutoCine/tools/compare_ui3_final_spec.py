"""Create honest reference overlays for the offline Windows WebView2 captures.

The Work images contain illustrative gameplay. Full-image pixel differences
therefore describe the evidence; they are never used as a UI pass score.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "design" / "ui" / "final_implementation_spec_20261028" / "references"
QA = ROOT / "qa" / "ui3_final_spec_20261028"


def main() -> int:
    target = QA / "comparisons"
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    for original in sorted(SPEC.glob("*.png")):
        if original.name == "C3_T-A-M_original.png":
            actual = QA / "c3_capture" / "T-A-M.png"
        else:
            family = "ld" if original.name.startswith("LD_") else "ln"
            actual = QA / f"{family}_capture" / original.name
        if not actual.is_file():
            rows.append({"screen": original.stem, "result": "NOT_RUN",
                         "reason": "Windows capture is missing"})
            continue
        with Image.open(original) as ref_image, Image.open(actual) as actual_image:
            ref = ref_image.convert("RGB")
            captured = actual_image.convert("RGB")
            original_size, captured_size = ref.size, captured.size
            resized = original_size != captured_size
            if resized:
                ref = ref.resize(captured_size, Image.Resampling.LANCZOS)
            overlay = Image.blend(ref, captured, 0.5)
            difference = ImageChops.difference(ref, captured)
            overlay_path = target / f"{original.stem}_overlay.png"
            difference_path = target / f"{original.stem}_difference.png"
            overlay.save(overlay_path, optimize=True)
            difference.save(difference_path, optimize=True)
            rows.append({"screen": original.stem, "result": "REVIEW",
                         "reference": str(original.relative_to(ROOT)),
                         "windows_capture": str(actual.relative_to(ROOT)),
                         "overlay": str(overlay_path.relative_to(ROOT)),
                         "difference": str(difference_path.relative_to(ROOT)),
                         "reference_size": original_size,
                         "capture_size": captured_size,
                         "reference_resized_for_comparison": resized,
                         "whole_image_mean_absolute_rgb_difference": round(
                             sum(ImageStat.Stat(difference).mean) / 3, 2),
                         "caveat": "Game imagery and sample match differ; UI fidelity is not passed by this metric."})
    (target / "index.json").write_text(json.dumps({"screens": rows}, ensure_ascii=False,
                                           indent=2), encoding="utf-8")
    print(f"Compared {sum(row['result'] == 'REVIEW' for row in rows)}/{len(rows)} source images")
    return 0 if all(row["result"] == "REVIEW" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
