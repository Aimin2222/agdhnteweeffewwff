# LoL AutoCine v5.10.15 Scan/UI/Camera 修正版メモ

## 今回の主な修正

1. **スキャン導線を一本化**
   - 左側の「接続して10人を取得」を削除。
   - 右側の **「① スキャン（接続→10人取得→試合全体）」** で、接続・10人取得・試合全体スキャンをまとめて実行するよう変更。
   - 取得後のプレイヤー一覧は左側で確認・固定する用途に整理。

2. **チェックボックスの見た目改善**
   - `ui/check_indicator.py` を更新し、高解像度から縮小する方式に変更。
   - 白UI上で荒く見えにくい、角丸の青いチェック表示へ変更。

3. **DOF UIの整理**
   - 円形DOFと従来の上下ぼかしを **同時表示しない** よう修正。
   - 右側の DOF 詳細カードにもモード切替を追加。
   - 図形付きの説明（円形 / 横帯）を追加し、現在どちらの方式か見てわかるように改善。

4. **三人称/FPS/Lolnam シネマの上下反転対策**
   - カメラスタイル再選択時、およびカメラプレビュー開始時に、三人称リグのキャッシュを明示的にクリアする処理を追加。
   - `core/camera.py` に `clear_tps_calibration()` を追加。
   - 「同じカメラをもう一度押したあとに地面が上になる」系の再現を抑える狙い。

5. **キルフレーム名の簡素化**
   - 長すぎる名称・ダサく見えやすい名称を、シンプルで普通の名前へ変更。
   - 旧名称からの読み込み互換のため、逆引きマップには旧名エイリアスを残してあります。

6. **開発用ワンボタン実録画テストを追加**
   - 試合全体スキャン後に使える、**「開発用：カメラ/演出テストを一括作成」** ボタンを追加。
   - BLUE/RED の代表キルを使い、主要カメラスタイルをまとめて書き出します。
   - さらに、キル数が足りる場合はモンタージュ演出も一括でテスト出力します。
   - 一時的な開発補助機能であり、完成版では削除予定の前提です。

## 変更ファイル

- `legacy_app.py`
- `core/camera.py`
- `core/kill_icons.py`
- `ui/check_indicator.py`
- `tests/test_v51012_allscan_quality_camera.py`
- `tests/test_v51015_ui_restructure.py`

## 実施テスト

### 1回目
- `tests/test_v51015_ui_restructure.py`
- `tests/test_v51012_allscan_quality_camera.py`
- `tests/test_v5102_circle_focus_preset.py`
- `tests/test_v51015_portrait_player_compat.py`

結果: **25 passed**

### 2回目
- `tests/test_v51013_player_filter.py`
- `tests/test_v51011_gallery_camera_qa.py`
- `tests/test_v51010_real_scene_material.py`
- `tests/test_gpu_shared_v51013.py`

結果: **64 passed**

合計: **89 passed / 0 failed**

## Windowsで重点確認してほしい点

1. 右側のスキャンボタンだけで、接続→10人取得→全体スキャンまで完了するか。
2. チェックボックスの見た目が改善されているか。
3. DOFを円形 / 従来で切り替えたとき、片方だけ表示されるか。
4. 三人称通常 / 三人称シネマ / FPS風 / Lolnamシネマを連続で試しても、上下反転が再発しないか。
5. 開発用一括テストボタンで `_dev_replay_qa` 配下にまとめて出力されるか。
