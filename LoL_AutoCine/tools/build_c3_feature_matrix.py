"""Join Work's 70-feature proposal with the actual UI3 access audit.

Do not turn a proposed handler or offline click into a live LoL pass.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "design" / "ui" / "c3_refinement_20261027" / "specs" / "FEATURE_BINDINGS_70.json"
BASE = ROOT / "docs" / "ui3" / "UI3_FEATURE70_CONNECTION_20261027.csv"
OUTPUT = ROOT / "docs" / "ui3" / "C3_FEATURE70_CONNECTION_20261027.csv"


def main() -> None:
    proposed = json.loads(WORK.read_text(encoding="utf-8"))["items"]
    with BASE.open(encoding="utf-8-sig", newline="") as source:
        implemented = {row["id"]: row for row in csv.DictReader(source)}
    if len(proposed) != 70 or len(implemented) != 70 or {x["id"] for x in proposed} != set(implemented):
        raise ValueError("Work/AutoCineの70機能台帳のIDが一致しません")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        fields = ("id", "name", "c3p_area", "c3s_area", "work_handler_candidate",
                  "current_ui3_access", "c3_connection", "offline_operation", "live_lol_test", "remaining")
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in proposed:
            feature_id = item["id"]
            access = implemented[feature_id]["ui3_access"]
            if access == "DIRECT_UI3":
                connection = "共通Appアダプターへ直接。画面内の専用操作または元候補3の全機能入口"
            elif access == "NATIVE_EDITOR":
                connection = "C3から既存Tk実動作エディタ。C3画面内の専用操作は一部未移植"
            elif access == "BACKEND_AUTOMATIC":
                connection = "既存バックエンド内部経路。独立UI操作なし"
            elif access == "UNIMPLEMENTED":
                connection = "未実装。成功表示・ダミー操作なし"
            else:
                connection = "接続未確認"
            offline = ("PASS: Windows C3素材適用・同名FX" if feature_id in {"WORKFRAME", "WORKFX"}
                       else "NOT_RUN: 個別のWindows実操作")
            writer.writerow({
                "id": feature_id, "name": item["name"], "c3p_area": item["C3P"],
                "c3s_area": item["C3S"],
                "work_handler_candidate": item["inherited_handler"],
                "current_ui3_access": access, "c3_connection": connection,
                "offline_operation": offline, "live_lol_test": "NOT_RUN",
                "remaining": item["remaining"],
            })
    print(f"{OUTPUT}: {len(proposed)} rows")


if __name__ == "__main__":
    main()
