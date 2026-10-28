"""Save source/Windows overlays for the two optional Work reference layouts.

The source uses generated illustration and scene fixture data. The Windows
trial shows a real mirror only when connected; differences are REVIEW evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "ui3_reference_20261027"


def main() -> None:
    results = []
    for code, label in (("ld", "League Director / R1 Track Desk"),
                        ("ln", "Lolnam / R2 Shot Canvas")):
        source = QA / "reference" / f"{code.upper()}_main_light_1920x1080.png"
        actual = QA / f"reference-{code}.png"
        with Image.open(source) as ref_image, Image.open(actual) as actual_image:
            reference = ref_image.convert("RGB")
            implementation = actual_image.convert("RGB")
            if reference.size != (1920, 1080) or implementation.size != reference.size:
                raise ValueError(f"{label}: image dimensions do not match 1920x1080")
            Image.blend(reference, implementation, 0.5).save(QA / f"{code}_50percent_overlay.png")
            ImageChops.difference(reference, implementation).save(QA / f"{code}_difference.png")
        results.append({"ui": label, "reference": str(source.relative_to(ROOT)).replace("\\", "/"),
                        "capture": str(actual.relative_to(ROOT)).replace("\\", "/"),
                        "overlay": f"{code}_50percent_overlay.png", "difference": f"{code}_difference.png",
                        "visual": "REVIEW", "reason": "原画は合成イラストとシーンfixture。Windows版は未接続時に実ミラー映像と実シーンを偽装しない。画面骨格は目視再審査。",
                        "live_lol_gpu_audio_record_mp4": "NOT_RUN"})
    (QA / "comparison.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"screens": len(results), "visual": "REVIEW"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
