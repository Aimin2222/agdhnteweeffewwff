# Codex統合手順：v5.9.5 UIワークスペース

基準: ChatGPT側 v5.9.4。GPU/音声の作業ブランチは上書きしないこと。

## 対象
- `legacy_app.py`（UIの配置、ゾーン切り替え、設定コピー・貼り付け）
- `tests/test_v593_mode_camera.py`（旧「詳細カード全部表示」テストをゾーン表示へ更新）
- `tests/test_v595_workspace.py`（新規）
- `VERSION.txt`, `README_v5.9.5_JA.md`, docs（新規説明）

`core/` と `ui/` のPythonコード、GPUエンコード、LoL Process Loopback録音は変更していない。

## 統合方法
1. Codex側の変更を必ずコミットし、ブランチをバックアップする。
2. 同梱の `patches/v594_to_v595.patch` をまず `git apply --check` で確認する。v5.9.4と異なる `legacy_app.py` がある場合は自動上書きしない。
3. UI関係の変更を安全に統合し、`python -m py_compile legacy_app.py` と `pytest` を実行する。
4. Windows実機でリプレイ固定、チェック済みシーンの書き出し、LoL専用音声、カラー映像、カメラプレビューを確認する。

注意: GitHubの別ブランチ内の旧GPUコードをフル版で上書きしないこと。
