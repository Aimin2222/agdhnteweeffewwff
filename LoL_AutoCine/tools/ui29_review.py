"""Reproducible, per-screen review of the 29 UI audit references.

This tool deliberately does not turn a reference PNG into a UI. It verifies
source provenance and compares captures produced by a running implementation.
Visual and functional results are separate: a pixel match never proves LoL
connection, GPU processing, recording, audio, or export.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "design" / "ui" / "implementation_audit_29_20261021"
MANIFEST = AUDIT / "SCREENS_29.json"
REQUIRED_FAMILIES = {
    "legacy02", "legacy03", "legacy05", "legacy06", "testA", "testB",
    "researchA", "researchB", "researchC", "researchD", "researchE", "researchF",
}
REGION_TOLERANCE = {"legacy_full": 8, "legacy_test": 8, "research": 2}


def load_inventory() -> list[dict]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(entries) != 29 or len({e["id"] for e in entries}) != 29:
        raise ValueError("監査原本は重複のない29画面である必要があります")
    if {e["family"] for e in entries} != REQUIRED_FAMILIES:
        raise ValueError("12候補グループが揃っていません")
    for entry in entries:
        original = AUDIT / entry["reference"]
        spec = AUDIT / "screens" / f"{entry['id']}.md"
        if not original.is_file() or not spec.is_file():
            raise FileNotFoundError(f"{entry['id']}: 原画像または個別仕様がありません")
        digest = hashlib.sha256(original.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"{entry['id']}: 原画像のSHA-256が監査資料と不一致")
        with Image.open(original) as image:
            if list(image.size) != entry["resolution"]:
                raise ValueError(f"{entry['id']}: 原画像の寸法が監査資料と不一致")
    return entries


def _clip(rect, size):
    x, y, w, h = (round(v) for v in rect)
    return (max(0, x), max(0, y), min(size[0], x + w), min(size[1], y + h))


def _mask_for(entry: dict, size: tuple[int, int]) -> np.ndarray:
    mask = np.ones((size[1], size[0]), dtype=bool)
    # The source's broad comparison mask is the *stage*. Only its 16:9 image
    # contain rect is dynamic; the matte, status, and controls remain reviewable.
    rect = entry.get("preview_contain_rect")
    if rect:
        x0, y0, x1, y1 = _clip(rect, size)
        mask[y0:y1, x0:x1] = False
    return mask


def _region_review(entry: dict, measured: dict) -> list[dict]:
    actual = measured.get("regions", measured)
    limit = REGION_TOLERANCE[entry["group"]]
    rows = []
    for region in entry["regions"]:
        rid = region["id"]
        expected = region["rect"]
        found = actual.get(rid)
        if isinstance(found, dict):
            found = found.get("rect")
        if not isinstance(found, list) or len(found) != 4:
            rows.append({"region": rid, "result": "NOT_MEASURED", "expected": expected})
            continue
        delta = [round(float(a) - float(b), 3) for a, b in zip(found, expected)]
        rows.append({"region": rid, "result": "PASS" if max(map(abs, delta)) <= limit else "FAIL",
                     "expected": expected, "actual": found, "delta": delta, "tolerance_px": limit})
    return rows


def review(entry: dict, capture: Path, output: Path, bounds: Path | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    original_path = AUDIT / entry["reference"]
    with Image.open(original_path) as source, Image.open(capture) as actual:
        source_rgb = source.convert("RGB")
        actual_rgb = actual.convert("RGB")
        size_ok = source_rgb.size == actual_rgb.size
        result = {
            "screen_id": entry["id"], "family": entry["family"],
            "reference_sha256": entry["sha256"],
            "reference_size": list(source_rgb.size), "capture_size": list(actual_rgb.size),
            "size_result": "PASS" if size_ok else "FAIL",
            "visual_result": "NOT_RUN", "functional_result": "NOT_RUN",
        }
        shutil.copyfile(original_path, output / "original.png")
        shutil.copyfile(capture, output / "implementation.png")
        if not size_ok:
            (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        Image.blend(source_rgb, actual_rgb, .5).save(output / "overlay_50.png")
        ref = np.asarray(source_rgb, dtype=np.int16)
        got = np.asarray(actual_rgb, dtype=np.int16)
        difference = np.abs(ref - got).astype(np.uint8)
        Image.fromarray(difference, "RGB").save(output / "absolute_difference.png")
        mask = _mask_for(entry, source_rgb.size)
        result["dynamic_image_mask"] = entry.get("preview_contain_rect")
        result["unmasked_rgb_mae"] = round(float(difference[mask].mean()), 4) if mask.any() else None
        result["regions"] = []
        for region in entry["regions"]:
            x0, y0, x1, y1 = _clip(region["rect"], source_rgb.size)
            area = mask[y0:y1, x0:x1]
            part = difference[y0:y1, x0:x1]
            mae = round(float(part[area].mean()), 4) if area.any() else None
            result["regions"].append({"region": region["id"], "rgb_mae": mae})
        if bounds and bounds.exists():
            measurements = json.loads(bounds.read_text(encoding="utf-8"))
            result["bounds"] = _region_review(entry, measurements)
            failures = [x for x in result["bounds"] if x["result"] != "PASS"]
            result["visual_result"] = "REVIEW" if failures else "MEASURED"
        else:
            result["visual_result"] = "REVIEW"
            result["bounds_note"] = "部品の実測値がないため寸法合格とは判定しません"
        (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", type=Path, help="<画面ID>.pngを29枚置いた実装キャプチャフォルダ")
    parser.add_argument("--bounds-dir", type=Path, help="<画面ID>.jsonのDOM/Tk矩形実測フォルダ")
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "ui29" / "review")
    args = parser.parse_args(argv)
    screens = load_inventory()
    rows = []
    for entry in screens:
        capture = args.capture_dir / f"{entry['id']}.png" if args.capture_dir else None
        if capture and capture.is_file():
            bounds = args.bounds_dir / f"{entry['id']}.json" if args.bounds_dir else None
            rows.append(review(entry, capture, args.output / entry["id"], bounds))
        else:
            rows.append({"screen_id": entry["id"], "family": entry["family"],
                         "reference_sha256": entry["sha256"], "visual_result": "NOT_RUN",
                         "functional_result": "NOT_RUN", "reason": "実装画面のキャプチャ未提出"})
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"expected_screens": 29, "candidate_groups": 12, "screens": rows,
              "note": "視覚判定とLoL/GPU/録画/音声/書き出しの機能判定は別管理"}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"29画面 / 12候補グループ。実装キャプチャ: {sum('capture_size' in row for row in rows)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
