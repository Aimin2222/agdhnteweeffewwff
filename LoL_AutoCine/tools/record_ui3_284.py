"""Record only evidenced outcomes against Work's 284-case acceptance ledger."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa/ui3_three_views_20261028"
SOURCE = QA / "WORK_ACCEPTANCE_284_ORIGINAL.json"


def main() -> None:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    if original.get("total") != 284 or len(original.get("cases", [])) != 284:
        raise ValueError("Work acceptance source is not the expected 284-case ledger")
    results = json.loads(json.dumps(original, ensure_ascii=False))
    # Each case covers more than a mere screenshot or one successful click.
    # Keep incomplete gates at REVIEW and live-device tests at NOT_RUN.
    evidence = {
        "C3-REF": ["qa/ui3_baseline_20261027/T-A-M_comparison.json",
                   "qa/ui3_baseline_20261027/T-A-M_50percent_overlay.png"],
        "R1-REF": ["qa/ui3_reference_20261027/comparison.json",
                   "qa/ui3_reference_20261027/ld_50percent_overlay.png"],
        "R2-REF": ["qa/ui3_reference_20261027/comparison.json",
                   "qa/ui3_reference_20261027/ln_50percent_overlay.png"],
        "C3-STATE": ["qa/ui3_baseline_flow_20261027/index.json"],
        "R1-STATE": ["qa/ui3_reference_20261027/ld_flow.json"],
        "R2-STATE": ["qa/ui3_reference_20261027/ln_flow.json"],
        "C3-ASSET": ["qa/ui3_baseline_flow_20261027/index.json"],
        "R1-ASSET": ["qa/ui3_reference_20261027/ld_flow.json"],
        "R2-ASSET": ["qa/ui3_reference_20261027/ln_flow.json"],
    }
    for case in results["cases"]:
        if case["id"] in evidence:
            case["status"] = "REVIEW"
            case["evidence"] = evidence[case["id"]]
            case["actual"] = ("Windows source-host offline checks partially exercised this case; "
                              "full visual or live-backend acceptance remains unverified")
            case["visual_status"] = "REVIEW" if case["id"].endswith("-REF") else "NOT_RUN"
            case["functional_status"] = "REVIEW" if not case["id"].endswith("-REF") else "NOT_RUN"
    results["status"] = "9 REVIEW; 275 NOT_RUN; 0 PASS; 0 FAIL"
    results["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    results["scope"] = "Windows WebView2 source-host offline; no real LoL/GPU/audio/record/MP4 acceptance"
    (QA / "ACCEPTANCE_RESULTS_284.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(results["status"])


if __name__ == "__main__":
    main()
