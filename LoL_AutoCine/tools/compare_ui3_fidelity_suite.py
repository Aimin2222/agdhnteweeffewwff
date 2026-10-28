"""Compare all 20 approved LD/LN PNGs with native Windows WebView captures.

The preview and real scene content are dynamic. Their pixels are excluded only
from the separate UI-only metric; full overlays/differences remain untouched.
No numeric threshold here can declare visual fidelity PASS by itself.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design" / "ui" / "ld_lolnam_reference_20261027" / "screenshots"
QA = ROOT / "qa" / "ui3_fidelity_v2_20261028"


def excluded_regions(variant: str, size: tuple[int, int]) -> list[tuple[int, int, int, int]]:
    scale_x = size[0] / 1920
    scale_y = size[1] / 1080
    if variant == "ld":
        regions = [(277, 176, 1552, 713), (13, 262, 264, 770)]
    else:
        regions = [(98, 176, 1552, 713), (98, 771, 1552, 819)]
    return [tuple(round(value * (scale_x if i % 2 == 0 else scale_y))
                  for i, value in enumerate(rect)) for rect in regions]


def main() -> None:
    report = []
    for variant in ("ld", "ln"):
        folder = QA / variant
        for source in sorted(SOURCE.glob(f"{variant.upper()}_*.png")):
            capture = folder / source.name
            if not capture.exists():
                raise FileNotFoundError(f"Windows capture missing: {capture}")
            with Image.open(source) as ref, Image.open(capture) as app:
                reference, actual = ref.convert("RGB"), app.convert("RGB")
                if reference.size != actual.size:
                    raise ValueError(f"size mismatch: {source.name}")
                overlay = folder / f"{source.stem}_50percent_overlay.png"
                difference = folder / f"{source.stem}_difference.png"
                Image.blend(reference, actual, .5).save(overlay)
                diff = ImageChops.difference(reference, actual)
                diff.save(difference)
                mask = Image.new("L", reference.size, 255)
                for rect in excluded_regions(variant, reference.size):
                    ImageDraw.Draw(mask).rectangle(rect, fill=0)
                ui_pixels = mask.getbbox()
                if ui_pixels is None:
                    raise ValueError("UI mask covers entire image")
                samples = ImageStat.Stat(diff, mask)
                mean_ui_difference = round(sum(samples.mean) / 3, 2)
                report.append({
                    "screen": source.name,
                    "source": str(source.relative_to(ROOT)).replace("\\", "/"),
                    "windows_capture": str(capture.relative_to(ROOT)).replace("\\", "/"),
                    "overlay": str(overlay.relative_to(ROOT)).replace("\\", "/"),
                    "difference": str(difference.relative_to(ROOT)).replace("\\", "/"),
                    "excluded_dynamic_regions": excluded_regions(variant, reference.size),
                    "ui_only_mean_channel_difference_0_to_255": mean_ui_difference,
                    "visual_result": "REVIEW",
                    "reason": "映像・シーン以外の文字、アイコン、カード、内部レイアウトを目視審査中。数値のみでPASSとしない",
                })
    if len(report) != 20:
        raise ValueError(f"expected 20 screens, got {len(report)}")
    (QA / "comparison_20.json").write_text(
        json.dumps({"reference_commit": "d0523f43d911eea781451b91c01098393bd69e6f",
                    "screens": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"screens": len(report), "all_visual_results": "REVIEW",
                      "ui_only_mean_range": [min(row["ui_only_mean_channel_difference_0_to_255"] for row in report),
                                             max(row["ui_only_mean_channel_difference_0_to_255"] for row in report)]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
