"""Join Work's C3 placement and 106-case checklist with conservative QA evidence.

This script never turns a static source reference or UI click into a LoL pass.
All untested cases retain NOT_RUN; REVIEW records partial visual evidence.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "design" / "ui" / "c3_acceptance_20261027" / "specs"
OUTPUT = ROOT / "docs" / "ui3"
QA = ROOT / "qa" / "c3_acceptance_20261027"


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_matrix() -> dict:
    placement = json.loads((WORK / "FUNCTION_PLACEMENT_70.json").read_text(encoding="utf-8"))
    with (OUTPUT / "C3_FEATURE70_CONNECTION_20261027.csv").open(
            encoding="utf-8-sig", newline="") as source:
        connections = {row["id"]: row for row in csv.DictReader(source)}
    items = placement["items"]
    ids = {item["id"] for item in items}
    if len(items) != 70 or len(ids) != 70 or ids != set(connections):
        raise ValueError("Work placement and current 70-function ledger disagree")
    rows = []
    for item in items:
        connection = connections[item["id"]]
        source_url = item.get("source", "")
        path = ""
        if "](" in source_url:
            url = source_url.split("](", 1)[1].split(")", 1)[0]
            remote = urlparse(url).path
            if "/LoL_AutoCine/" in remote:
                path = remote.split("/LoL_AutoCine/", 1)[1].split("#", 1)[0]
        rows.append({
            "id": item["id"], "name": item["name"],
            "primary_category": item["primary_category_ja"],
            "easy_entry": item["easy_entry"], "detail_entry": item["detail_entry"],
            "work_inherited_status": item["inherited_status"],
            "current_ui3_access": connection["current_ui3_access"],
            "current_connection": connection["c3_connection"],
            "handler_candidate": connection["work_handler_candidate"],
            "source_file": path,
            "source_file_present": "YES" if path and (ROOT / path).is_file() else "NOT_CONFIRMED",
            "offline_operation": connection["offline_operation"],
            "live_lol_test": "NOT_RUN", "remaining": connection["remaining"],
        })
    target = OUTPUT / "C3_ACCEPTANCE70_IMPLEMENTATION_20261027.csv"
    with target.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"file": repo_path(target), "counts": dict(Counter(r["current_ui3_access"] for r in rows)),
            "source_files_present": sum(r["source_file_present"] == "YES" for r in rows)}


def build_checklist() -> dict:
    work = json.loads((WORK / "UI_ACCEPTANCE_CHECKLIST.json").read_text(encoding="utf-8"))
    qa = json.loads((QA / "index.json").read_text(encoding="utf-8"))
    checks = qa["state_checks"]
    required = {"trim_from_ui", "test_results_tab", "shared_camera_state",
                "shared_checked_scenes", "same_app_screen_id"}
    required |= {name for name in checks if name.endswith("_revision_geometry")}
    if len(work["results"]) != 106 or any(checks.get(name) != "PASS" for name in required):
        raise ValueError("C3 offline QA evidence is incomplete")
    evidence = repo_path(QA / "index.json")
    decisions = {
        "ID01": ("REVIEW", "testA/T-A-MをPR51と照合。DPI実測記録が未取得。",
                 ["docs/ui3/CANDIDATE3_IDENTITY_AUDIT_20261027_JA.md", evidence]),
        "VIS01": ("REVIEW", "元候補3のWindows画面は撮影済み。原画への視覚総合合格は未判定。",
                  ["qa/c3_20261027/index.json"]),
        "VIS02": ("REVIEW", "C3-Pの原画像・重ね合わせ・差分を保存。タイムラインは改訂IDで別判定。",
                  ["qa/c3_acceptance_20261027/C3P_main_light_overlay.png", evidence]),
        "VIS03": ("REVIEW", "C3-Sの原画像・重ね合わせ・差分を保存。タイムラインは改訂IDで別判定。",
                  ["qa/c3_acceptance_20261027/C3S_main_light_overlay.png", evidence]),
        "VIS04": ("PASS", "C3-R01/R02/R03を記録。常設タイムライン矩形は両サイズのP/Sで指定値±2px以内。",
                  [evidence, "design/ui/c3_acceptance_20261027/specs/REVISION_PROPOSAL.json"]),
        "PRE03": ("REVIEW", "ライト/ダークと詳細切替を撮影し、カメラ値保持を確認。プレビュー時刻保持は未検証。",
                  [evidence]),
        "SIZE01": ("REVIEW", "1366×768のP/Sメインを撮影。詳細と図鑑の同条件検査は未実施。",
                   ["qa/c3_acceptance_20261027/C3P_main_1366x768_windows.png",
                    "qa/c3_acceptance_20261027/C3S_main_1366x768_windows.png"]),
        "SIZE03": ("PASS", "中央ミラー領域の実DOM矩形を1920×1080と1366×768で記録。",
                   [evidence]),
        "THEME01": ("REVIEW", "ライト/ダークの画面を撮影。Windowsテーマ追従の切替は未実施。",
                    [evidence]),
        "NUM01": ("REVIEW", "カメラ数値960をWindows UIから適用。スライダーからの逆方向操作は未検証。",
                  [evidence]),
        "ASSET02": ("REVIEW", "実素材と同名FXの適用を確認。一時選択後のキャンセルは未検証。",
                    [evidence]),
        "MODE01": ("PASS", "C3-Sでかんたん→詳細→かんたんを切り替え、Windows画面を撮影。",
                   [evidence]),
        "MODE02": ("REVIEW", "控えめおすすめの適用確認・UndoをWindowsで操作。後から数値/キーを変更した際のUndo禁止は単体試験で確認。全プリセットと選択キー適用範囲は未検証。",
                   [evidence, "tests/test_ui3_integration.py"]),
        "REG01": ("REVIEW", "元T-A-Mと他候補を変更せず独立ルートを追加。正式素材の承認状態の全数照合は未実施。",
                  ["docs/ui3/CANDIDATE3_IDENTITY_AUDIT_20261027_JA.md", evidence]),
    }
    for case in work["results"]:
        status, actual, files = decisions.get(case["id"], (
            "NOT_RUN", "このビルドで当該受入操作を完走していません。", []))
        case.update(status=status, actual=actual, evidence=files,
                    environment={"build_commit": qa["source_commit"],
                                 "candidate": "testA/T-A-M", "variant": "C3-P/C3-S",
                                 "dpi": "NOT_MEASURED", "live_lol": "NOT_RUN"},
                    reviewer="Codex offline QA" if status != "NOT_RUN" else None)
    work["all_status"] = "MIXED"
    work["source_work_commit"] = "3fdda5405f5acac1188ea7be70a07239df06e08b"
    work["implementation_commit"] = qa["source_commit"]
    work["counts"] = dict(Counter(case["status"] for case in work["results"]))
    target = QA / "UI_ACCEPTANCE_RESULTS_106.json"
    target.write_text(json.dumps(work, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"file": repo_path(target), "counts": work["counts"]}


def main() -> None:
    print(json.dumps({"matrix": build_matrix(), "acceptance": build_checklist()},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
