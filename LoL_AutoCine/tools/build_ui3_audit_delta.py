"""Cross-reference current triage with Work's 284-case audit proposal.

This is a progress map, not a formal acceptance result. It never upgrades a
visual or functional case to PASS based on source inspection alone.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from collections import Counter


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "design/ui/independent_ui_audit_20261028/data"
QA = ROOT / "qa/ui3_audit_20261028"


def main() -> None:
    proposal = json.loads((AUDIT / "ACCEPTANCE_284_PROPOSED.json").read_text(encoding="utf-8"))
    crosswalk = json.loads((AUDIT / "FINDING_CASE_CROSSWALK.json").read_text(encoding="utf-8"))
    report = (QA / "RECONCILIATION_JA.md").read_text(encoding="utf-8")
    statuses = {case["id"]: case["status"] for case in proposal["cases"]}
    pattern = r"^\| ((?:C3|R2?|QA)-\d+) \| (P\d) \| (修正済み|対応中|追加修正|要調査) \| (.*?) \|$"
    triage = {key: {"priority": priority, "progress": progress, "note": note}
              for key, priority, progress, note in re.findall(pattern, report, re.MULTILINE)}
    if len(statuses) != 284 or len(triage) != 26 or len(crosswalk["rows"]) != 26:
        raise ValueError("expected exactly 284 acceptance cases and 26 findings")
    rows = []
    for row in crosswalk["rows"]:
        finding = row["finding"]
        cases = row["related_cases"]
        if finding not in triage or any(case not in statuses for case in cases):
            raise ValueError(f"unmapped finding or acceptance case: {finding}")
        rows.append({"finding": finding, **triage[finding],
                     "related_cases": [{"id": case, "work_fixed_commit_proposal": statuses[case]}
                                       for case in cases]})
    result = {
        "scope": "Current remediation progress crosswalk; not formal acceptance",
        "work_audit_commit": "8fa9050d64aaa77ee74cb604f8c1793fc9718c7c",
        "proposed_284_counts": dict(Counter(statuses.values())),
        "formal_284_status": "UNCHANGED",
        "finding_progress_counts": dict(Counter(row["progress"] for row in rows)),
        "findings": rows,
        "evidence": ["RECONCILIATION_JA.md", "../ui3_fidelity_v2_20261028/RESULT_JA.md",
                     "c3_flow/index.json", "r2_stage_refined/index.json",
                     "c3_image_entry_refined/index.json"],
    }
    (QA / "ACCEPTANCE_DELTA_284.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"findings": len(rows), "linked_cases": sum(len(row["related_cases"]) for row in rows),
                      "progress": result["finding_progress_counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
