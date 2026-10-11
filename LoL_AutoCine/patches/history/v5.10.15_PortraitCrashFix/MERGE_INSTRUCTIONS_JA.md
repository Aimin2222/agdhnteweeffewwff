# LoL AutoCine v5.10.15 — チャンピオン画像取得のクラッシュ修正

## 元コードと適用範囲
- Windowsフル版: ユーザー添付 `LoL_AutoCine_v5.10.15_UI_Scan_Camera_Windows_Full(2).zip` の全既存ファイルを保持し、`core/kill_icons.py` だけを小修正＋回帰テスト新規追加。
- **このフル版はGitHubのCodex GPU統合版ではありません。** Codex統合版へこのフルZIPを上書きしないでください。
- Codex差分ZIP: `core/kill_icons.py` の `_icon_id()` を `Player` と辞書の両方に対応させる1箇所のGitパッチ、および回帰テストのみ。GPU/OpenCL/録画/音声/UIレイアウト/カメラは一切変更しません。
- このパッチは同一コードを含むCodex統合ブランチにも適用できるように作られていますが、Codexに組み込んだ後に必ず再テストしてください。

## Codexへの統合例（Gitリポジトリのルートで）
1. 作業ブランチを作り、未コミット作業を保全。
2. `git apply --check CHANGES_v5.10.15_PortraitCrashFix.patch` で競合確認。
3. `git apply CHANGES_v5.10.15_PortraitCrashFix.patch` で適用。
4. `python -m pytest -q LoL_AutoCine/tests/test_v51015_portrait_player_compat.py` を実行（作業ディレクトリ・PYTHONPATH設定は既存のプロジェクト構成に合わせる）。
5. `python -m pytest -q LoL_AutoCine/tests` など全体回帰後、Codex側のGPU保護ガードで確認。

## Windows確認
- 旧ZIPは残し、新しいフルZIPを別フォルダへ展開。起動方法は従来の `START.bat` / `START_GPU.bat` 設定を守る。
- Replay接続→一括スキャン→BLUE/REDプレイヤー切替→シーン選択を連続10回程度繰り返す。
- チャンピオン画像が表示されるか、未取得時は名前表示で続行するか、`UI_PUMP_ERROR` が増えないか。
- LoL専用音声・NVENC・1080p/60fpsを1シーンで確認。今回の修正はこれらを変更していない。

## 限界
- 今回は1件の確定UIクラッシュのみを先行修正。8本の実録画QA・接続＋スキャンの1ボタン化などの未統合機能は含まれていない。
- Windows実機の最終動作とCodex統合後の実GPU動作は別途確認が必要。
