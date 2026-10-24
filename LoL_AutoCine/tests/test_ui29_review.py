"""The audit must not silently lose a screen or declare hardware success."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ui29_review


class UI29ReviewTests(unittest.TestCase):
    def test_inventory_has_all_29_screens_and_12_families(self):
        rows = ui29_review.load_inventory()
        self.assertEqual(len(rows), 29)
        self.assertEqual(len({row["family"] for row in rows}), 12)
        self.assertEqual(len({row["id"] for row in rows}), 29)

    def test_visual_measurement_never_claims_functional_success(self):
        row = next(x for x in ui29_review.load_inventory() if x["id"] == "R-A-main")
        with TemporaryDirectory(dir=ROOT / "qa") as folder:
            tmp_path = Path(folder)
            reference = ui29_review.AUDIT / row["reference"]
            capture = tmp_path / "R-A-main.png"
            with Image.open(reference) as image:
                image.save(capture)
            report = ui29_review.review(row, capture, tmp_path / "review")
            self.assertEqual(report["unmasked_rgb_mae"], 0)
            self.assertEqual(report["visual_result"], "REVIEW")  # no bounds
            self.assertEqual(report["functional_result"], "NOT_RUN")
            mask = ui29_review._mask_for(row, tuple(row["resolution"]))
            self.assertTrue(mask[300, 330])   # matte inside preview stage
            self.assertFalse(mask[300, 600])  # live 16:9 image only
            self.assertTrue((tmp_path / "review" / "overlay_50.png").is_file())
            self.assertTrue((tmp_path / "review" / "absolute_difference.png").is_file())

    def test_panel_bounds_must_be_measured(self):
        row = next(x for x in ui29_review.load_inventory() if x["id"] == "R-A-main")
        with TemporaryDirectory(dir=ROOT / "qa") as folder:
            tmp_path = Path(folder)
            capture = tmp_path / "R-A-main.png"
            with Image.open(ui29_review.AUDIT / row["reference"]) as image:
                image.save(capture)
            bounds = tmp_path / "bounds.json"
            bounds.write_text(json.dumps({"regions": {"header": [0, 0, 1920, 76]}}), encoding="utf-8")
            report = ui29_review.review(row, capture, tmp_path / "review", bounds)
            self.assertEqual(report["visual_result"], "REVIEW")
            self.assertTrue(any(x["result"] == "NOT_MEASURED" for x in report["bounds"]))


if __name__ == "__main__":
    unittest.main()
