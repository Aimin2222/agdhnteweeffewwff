"""Compare the Windows BAT candidate-3 capture against the actual T-A-M source.

The source mock contains illustrative gameplay; an offline real mirror is blank.
Image differences are evidence for human review, not a functional pass score.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png"
TARGETS = {
    "header": (0, 0, 1672, 49),
    "prepare": (7, 54, 338, 608),
    "preview-panel": (352, 54, 902, 608),
    "preview-stage": (355, 94, 895, 492),
    "preview-controls": (355, 611, 895, 46),
    "scene-list": (1263, 54, 400, 608),
    "timeline": (7, 735, 1278, 53),
    "camera-detail": (7, 793, 588, 136),
    "target-side": (603, 793, 260, 136),
    "camera-numeric": (871, 793, 414, 136),
    "materials": (1294, 735, 369, 194),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()
    capture = args.capture.resolve()
    folder = capture.parent
    with Image.open(REFERENCE) as original, Image.open(capture) as actual:
        original = original.convert("RGB")
        actual = actual.convert("RGB")
        if original.size != actual.size:
            raise SystemExit(f"capture size {actual.size} differs from reference {original.size}")
        Image.blend(original, actual, 0.5).save(folder / "T-A-M_50percent_overlay.png")
        ImageChops.difference(original, actual).save(folder / "T-A-M_difference.png")
    bounds = json.loads((folder / "bounds/T-A-M.json").read_text(encoding="utf-8"))
    geometry = {}
    for key, target in TARGETS.items():
        actual = bounds.get(key)
        if actual is None:
            geometry[key] = {"result": "NOT_FOUND", "reference": target}
            continue
        # Judge the visible edges, not independent x/y/w/h deltas.  A small
        # origin and width error can add up at the far edge.
        target_edges = (target[0], target[1], target[0] + target[2], target[1] + target[3])
        actual_edges = (actual[0], actual[1], actual[0] + actual[2], actual[1] + actual[3])
        delta = [round(actual_edges[i] - target_edges[i], 2) for i in range(4)]
        size_delta = [round(actual[i] - target[i], 2) for i in (2, 3)]
        largest = max(abs(value) for value in delta)
        geometry[key] = {"result": "PASS" if largest <= 2 else "REVIEW" if largest <= 8 else "FAIL",
                         "reference": target, "actual": actual, "edge_delta_ltrb": delta,
                         "size_delta_wh": size_delta}
    report = {
        "candidate": "testA / T-A-M",
        "source": str(REFERENCE.relative_to(ROOT)).replace("\\", "/"),
        "capture": capture.name,
        "geometry_pass_tolerance_native_px": 2,
        "geometry_review_tolerance_native_px": 8,
        "geometry": geometry,
        "geometry_result": "FAIL" if any(row["result"] == "FAIL" for row in geometry.values()) else
                           "REVIEW" if any(row["result"] == "REVIEW" for row in geometry.values()) else "PASS",
        "visual_result": "REVIEW",
        "visual_note": "原画像のゲーム映像・実試合データは模式例。未接続の実ミラーと未取得行を同一画素として合格扱いしない。文字とカードは目視再審査。",
        "functional_result": "NOT_RUN: 実LoL・録画・音声・GPU・MP4",
    }
    (folder / "T-A-M_comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"geometry": report["geometry_result"],
                      "visual": report["visual_result"],
                      "regions": len(geometry)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
