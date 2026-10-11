# 受領側のテスト記録（Codex統合後の実行結果ではありません）

# v5.10.15 自動テスト記録

- 実行環境: Linux + Xvfb（Windows版LoLの実機ではない）
- 一括回帰テスト: `python -m pytest -q tests --ignore=tests/test_v5105_preview_responsiveness.py`
- 結果: **507 passed in 57.54s**
- 除外理由: `tests/test_v5105_preview_responsiveness.py` は以前から実行が長時間止まる問題があるため、今回の一括実行では除外。
- GUIの機能確認: カラー/FX/出力独立ページ、DOF ON/OFFで詳細欄展開、Tk標準ComboboxのPopdown展開中に背後パネルがスクロールしないことをGUIテストで確認。
- RED FPS: ゲーム画像から被写体が左下に外れていることを確認し、REDのみFPSカメラの既存オフセットを縮小。
- RED通常3人称: REDのみYawを小さく補正し、上下Pitchの余分な反転を撤廃。BLUEおよびLolnamシネマの計算は維持。
- ZIP: Windowsフル版とCodex用パッチのCRC検査成功、`git apply --check -p1`成功。
- 未確認: Windows実機のリプレイでのカメラ構図、ミラー実動作、実GPU/NVENC、LoL専用音声、トランジション10種類の実書き出し。

※ 507件成功はWindows実機の動作保証ではありません。実機テストは `TESTLIST_v5.10.15_JA.md` をご利用ください。
