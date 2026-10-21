"""Write a human-readable 29-screen status from recorded QA evidence."""
from __future__ import annotations

import json
from pathlib import Path

from ui29_review import ROOT, load_inventory


QA = ROOT / "qa" / "ui29"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def main():
    screens = load_inventory()
    live = read_json(QA / "live_offline" / "review" / "index.json") or {}
    probe = read_json(QA / "local_bridge_probe.json") or {}
    results = {row["screen_id"]: row for row in live.get("screens", [])}
    lines = [
        "# 全29画面 UI進捗・テスト結果",
        "",
        "監査元：`design/ui/implementation_audit_29_20261021/`。全12候補を最終対象として維持。最終UIは未選定。",
        "",
        "## 今回確認したこと",
        "",
        f"- 原画像・個別仕様・SHA-256・寸法：{len(screens)}画面を照合。",
        "- 新18画面：既存AutoCine Appに接続したローカルUI経由で、LoL未接続のEdge画像・DOM矩形・50%重ね・差分を保存。",
        f"- Appブリッジ（候補切替、テーマ、カメラ側・距離、登場アニメ、監査済み素材）：{probe.get('result', 'NOT_RUN')}。",
        "- LoLリプレイ接続、WGCミラー、カメラ実映像、GPU/NVENC、ゲーム音、録画、MP4出力：**このブランチでは未実施**。",
        "- 旧11画面：編集可能な原HTMLがないため、コードとしての忠実な再構成は未実装。原画像を押せるだけの画面として扱わない。",
        "",
        "`MEASURED` は寸法比較を実行した意味。目視審査・機能合格ではない。`REVIEW` は矩形差が許容外。",
        "",
        "## 29画面一覧",
        "",
        "| ID | 候補 | 実装 | オフライン視覚 | 映像外RGB差/255 | 矩形 ±2px | LoL実機 |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for screen in screens:
        row = results.get(screen["id"], {})
        bounds = row.get("bounds") or []
        passed = sum(item["result"] == "PASS" for item in bounds)
        total = len(bounds)
        implemented = "部分実装" if screen["group"] == "research" else "未実装"
        visual = row.get("visual_result", "NOT_RUN")
        mae = row.get("unmasked_rgb_mae", "—")
        dimension = f"{passed}/{total}" if total else "—"
        lines.append(f"| {screen['id']} | {screen['family_name']} | {implemented} | {visual} | {mae} | {dimension} | NOT_RUN |")
    lines += [
        "",
        "## 残る合格条件",
        "",
        "1. 旧11画面を原画像の配置・操作順でコードから再構成し、12候補すべてを同じAppで切り替える。",
        "2. 新18画面を含む全操作部品を監査F01〜F25へ接続し、表示例を実データへ置換する。エンゲージは専用実装ができるまで未対応と表示する。",
        "3. 全29画面で実装画像・重ね合わせ・差分・寸法を審査し、表示倍率125%も確認する。",
        "4. 実際のLoLリプレイでスキャン、TargetLock、BLUE/RED、固定自動・フルオート、FX、WGC、GPU/NVENC、LoL音声、MP4出力を機能別に合否記録する。",
        "5. 合格したコミットからポータブルEXE/ZIPを作り、起動・操作・保存・書き出しを実機で確認する。mainへのマージはユーザー承認待ち。",
        "",
    ]
    target = QA / "STATUS_JA.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"{target}: {len(screens)} screens, {sum(x.get('capture_size') is not None for x in results.values())} offline captures")


if __name__ == "__main__":
    main()
