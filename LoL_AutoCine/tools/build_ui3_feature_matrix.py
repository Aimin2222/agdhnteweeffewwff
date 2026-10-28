"""Pin Work's 70-row audit and record UI3 reachability without claiming live QA."""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ui3"
SOURCE = DOC / "WORK_70_FEATURE_BASELINE_V4.csv"
OUTPUT = DOC / "UI3_FEATURE70_CONNECTION_20261027.csv"

DIRECT = {
    "REPLAY", "LAUNCH", "PLAYER", "SCAN", "ASSIST", "SCENE", "TIMELINE",
    "HUD", "MIRROR", "JOB", "WORKFRAME", "WORKFX", "MOTION", "PREVIEW",
    "SMARTMONTAGE", "SELFQA", "DIAG", "FIXED", "FULL",
}
NATIVE = {
    "KEYFRAME", "HIGHLIGHT", "AUDIO", "BGM", "NVENC", "GPUFX",
    "GRADE", "FOG", "DOF", "PULSE", "BADGE", "REFERENCE", "MONTAGEFX",
}
AUTOMATIC = {"MULTI", "CAPTURE", "RECORD", "AUDIOGUARD"}
UNIMPLEMENTED = {"ENGAGE", "BESTSHOT"}


def classify(feature_id: str) -> tuple[str, str]:
    if feature_id in UNIMPLEMENTED:
        return "UNIMPLEMENTED", "監査時点で本体処理なし。ダミー操作は設置しない"
    if feature_id in DIRECT or feature_id.startswith("CAM_"):
        return "DIRECT_UI3", "候補3の画面または全機能パネルから既存Appへ操作を送る"
    if feature_id in NATIVE or feature_id.startswith("FX_"):
        return "NATIVE_EDITOR", "候補3の全機能パネルから従来の実動作エディタを開く。候補3内への移植は残作業"
    if feature_id in AUTOMATIC:
        return "BACKEND_AUTOMATIC", "接続済み処理の内部経路。独立した画面操作はない"
    return "NEEDS_MAPPING", "対応する操作経路の確認が必要"


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 70 or len({row["id"] for row in rows}) != 70:
        raise ValueError("Workの70機能台帳が欠損しています")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("id", "name", "work_status", "ui3_access", "basis", "live_lol_test"))
        for row in rows:
            access, basis = classify(row["id"])
            writer.writerow((row["id"], row["name"], row["status_label"],
                             access, basis, "NOT_RUN"))
    counts = {label: sum(classify(row["id"])[0] == label for row in rows)
              for label in ("DIRECT_UI3", "NATIVE_EDITOR", "BACKEND_AUTOMATIC",
                            "UNIMPLEMENTED", "NEEDS_MAPPING")}
    print(f"70 rows: {counts}")


if __name__ == "__main__":
    main()
