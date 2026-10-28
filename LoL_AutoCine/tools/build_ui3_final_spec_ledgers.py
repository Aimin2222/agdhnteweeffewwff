"""Record conservative implementation and test progress against Work's final spec."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "design" / "ui" / "final_implementation_spec_20261028"
QA = ROOT / "qa" / "ui3_final_spec_20261028"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    (QA / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    screens = read(SPEC / "specs" / "SCREEN_SPECIFICATIONS.json")["screens"]
    screen_rows = []
    reference_views = {"main", "easy", "detail", "camera", "curve", "color",
                       "material", "export"}
    c3_views = {"main", "easy", "detail", "camera", "color", "material", "export"}
    for item in screens:
        family, view = item["id"].split(".", 1)
        visible = view in (c3_views if family == "C3" else reference_views)
        screen_rows.append({"id": item["id"], "title": item["title"],
                            "current_access": "PARTIAL_INTERACTIVE_VIEW" if visible
                            else "ENTRY_OR_PARENT_VIEW_ONLY",
                            "visual_acceptance": "REVIEW" if family != "C3" and visible
                            or item["id"] == "C3.main" else "NOT_RUN",
                            "functional_acceptance": "NOT_RUN",
                            "reason": "Full controls, fidelity and live LoL end-to-end remain unverified"})
    save("SCREEN_STATUS_36.json", {"count": len(screen_rows), "screens": screen_rows})

    matrix = read(SPEC / "FUNCTION_IMPLEMENTATION_MATRIX.json")
    feature_rows = []
    for item in matrix["existing"]:
        grade = item["id"] == "GRADE"
        feature_rows.append({"id": item["id"], "name": item["name"], "kind": "existing",
                             "work_baseline_access": item["baseline_access"],
                             "current_access": "PARTIAL_DIRECT_GLOBAL_COLOR" if grade
                             else item["baseline_access"],
                             "verification": "PARTIAL_WINDOWS_OFFLINE" if grade else "NOT_RUN",
                             "remaining": "LUT, curve, scene scope and output parity" if grade
                             else "Work matrix requirements and real operation need verification"})
    for item in matrix["additional"]:
        n06 = item["id"] == "N06"
        feature_rows.append({"id": item["id"], "name": item["name"], "kind": "additional",
                             "work_baseline_access": item["baseline_status"],
                             "current_access": "PARTIAL_GLOBAL_COLOR_ADAPTER" if n06
                             else "NOT_COMPLETE", "verification": "PARTIAL_WINDOWS_OFFLINE" if n06
                             else "NOT_RUN", "decision_gate": item.get("decision"),
                             "remaining": item["required_work"]})
    save("FEATURE_STATUS_86.json", {"existing_count": 70, "additional_count": 16,
                                    "features": feature_rows,
                                    "note": "Baseline access is not an end-to-end PASS."})

    tests = read(SPEC / "specs" / "TEST_CASES.json")["cases"]
    partial = {
        "YAW-32": "R1/R2 yaw=32 and cross-variant state checked; C3/theme/scene/full mode not run",
        "COMPACT-NO-OVERLAP": "R2 1366x768 and 1920x1080 checked; DPI125/150 not run",
        "COLOR-ROUNDTRIP": "Existing global exposure=0.12 reached App; save/reload, LUT, CPU/GPU not run",
        "STATE-SWITCH": "Selected camera/frame/color values survived R1/R2 switch; draft/project/replay not run",
    }
    test_rows = [{"id": case["id"], "status": "NOT_RUN",
                  "related": case.get("related", []),
                  **({"partial_evidence": partial[case["id"]]}
                     if case["id"] in partial else {})} for case in tests]
    save("TEST_EXECUTION_239.json", {"total": len(test_rows),
                                     "counts": {"PASS": 0, "FAIL": 0, "REVIEW": 0,
                                                "NOT_RUN": len(test_rows)},
                                     "separate_284_ledger": "qa/ui3_three_views_20261028/ACCEPTANCE_RESULTS_284.json",
                                     "cases": test_rows})
    assert len(screen_rows) == 36 and len(feature_rows) == 86 and len(test_rows) == 239
    print("36 screens, 86 features, 239 uncompleted test cases recorded")


if __name__ == "__main__":
    main()
