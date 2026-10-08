# LoL AutoCine v5.8.6 — Codex + ChatGPT 並行開発の統合契約

## 基準

- 共通の出発点は v5.8.5。v5.8.4 の安定実績も保持。
- このZIPは **UI側の変更のみ** をベース v5.8.5 に上乗せしたバージョン。
- CodexがGPU側に加えた変更は、まだこのZIPに含めていない。統合までは別々のブランチ。
- それぞれのPCで試す前に v5.8.5 をバックアップすること。

## ファイル所有者（衝突防止）

| 担当 | 主な編集対象 | 禁止事項 |
| --- | --- | --- |
| ChatGPT/UI | `legacy_app.py`, `ui/`, UIテスト、UI仕様 | レンダラと音声の内部仕様を勝手に変更しない |
| Codex/GPU | `core/effects.py`, `core/gpu_pipeline.py`, GPUフィルターとそのテスト | `legacy_app.py` のレイアウトやコントロール変数を直接変更しない |
| 共同レビューが必要 | `core/jobs.py`, `core/camera.py`, `core/audio.py`, `core/scanner.py`, `app.py` | 片方だけでAPIを破壊しない |

## 接続境界 / Public Contract

UIがレンダラへ渡すのは `core.effects.Template` のデータ（既存の `current_template()`）と、キルのリスト。
レンダラに渡した時点で、UIの `tk.Variable` やTkウィジェットをワーカースレッドから読んではいけない。

- `Template.pre`, `Template.post`: クリップの前後秒数。編集タイムラインと既存のスピンボックスで同じ変数を操作する。
- `Template.motion_arc`, `Template.motion_dolly`, `Template.motion_profile`: 既存カメラの演出パラメータ。カメラのTargetLock座標系を変えない。
- `Template.video_effects`, `Template.dof_enabled`, `Template.bloom`: GPUバックエンドは読み取ってよい。UI用の変数型をGPUコードへ持ち込まない。
- `run_auto_edit(api, source, player, kills, template, output, montage, ..., audio_factory=...)` の呼び出し方式を維持する。
- LoL専用 Process Loopback 録音と NVENC → CPUフォールバックは維持。音声をデスクトップ録音に戻さない。
- `core.effects.Template` の既存フィールドを削除/リネームしない。必要なら新規フィールドはデフォルト付きで増やす。
- FFmpegの実行失敗をUIまでネイティブクラッシュで持ち込まず、エラーとフォールバック理由を診断ログへ記録する。

## このUIブランチで実装済み (v5.8.6)

- クリップ前後秒数をドラッグで変更できる実タイムライン。 `Template.pre/post` と同期。
- カメラ「自然/シネマ/ダイナミック」クイックボタン。実際の `motion_*` に同期。
- 任意ONの自動ディレクター。既存のスキャン済みキルのマルチキル数から簡易プリセットを選ぶ。未スキャン時は既存の auto motion に任せる。
- 従来のエフェクト、動画保存、音声、チェックシーン作成、ミラー等に変更なし。

## 重要: 実装済みでないもの

- このタイムラインは **動画の前後区間を編集** するもの。カメラの自由なキーフレームエディタにはまだなっていない。
- 現在の自動ディレクターはジョブ開始前の共通テンプレートを選択する。全キルを個別に分析した演出切替は未実装。
- プレビューと出力の色/DOFの完全一致は検証が必要。
- GPUエフェクト自体はこのブランチでは変更せず、Codex側担当。

## Gitでの統合例

1. `stable/v5.8.5` をタグ/ブランチとして保存。
2. UI側を `feature/ui-editor-v586`、Codex側を `feature/gpu-engine` としてコミット。
3. 統合ブランチで `feature/gpu-engine` を先にマージし、`feature/ui-editor-v586` を後にマージ（順序は逆でもよいがレビュー必須）。
4. コンフリクトが起きたら、UIファイルはUI側、GPUファイルはCodex側を起点に**内容を確認して**解決する。機械的な片側採用は避ける。
5. `python -m py_compile legacy_app.py ui/scene_timeline.py`、`python -m pytest tests/test_editor_ui_contract.py -q`、既存テストを実行。
6. Windows + LoL + GTX 1070 Ti 実機で「1クリップ、選択2シーン、カラー、LoL音声、NVENC、GPU診断」を再確認。

## Codexへの指示

このファイルを必ず参照し、現行UIを維持したままGPUコアを独立して開発してください。GPU側API変更が必要なら実装前にUIとの接続点・変更する関数署名・テスト方法を提案してください。
