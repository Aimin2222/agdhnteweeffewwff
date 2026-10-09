# AGENTS.md — LoL AutoCine

- 日本語で応答する。詳細設計は `CODEX_HANDOFF_JA.md` を最初に読む。
- このリポジトリは現時点の動作版 v5.8.5。v5.8.4を実機動作確認済みの比較基準とする。
- 現存する機能、UI、第三者視点/OrbitTargetLock、LoLプロセス専用録音を削除・改変しないことを最優先する。
- まず現状を監査し、修正前に小さな計画を示す。変更は機能単位、検証可能な小さい差分にする。
- Tkinter はUIスレッドからのみ操作。FFmpegと録画処理をUIスレッドでブロックしない。
- NVENC使用とGPUエフェクト実行を混同しない。選択したフィルター・実行/フォールバック理由は診断ログに正しく記録する。
- 非対応GPU/ドライバ/FFmpegでは安全なCPUフォールバック。過去の不適合経路 `hwdownload,format=yuv420p` を安易に再導入しない。
- 色、LoLのみの音声、実時間同期、カメラTargetLock、チェックシーン出力が最重要回帰項目。
- 自動テストや `python -m py_compile` を可能な範囲で実施し、Windows/LoLの実機未検証を明確に報告。
- パス・ユーザー名等が含まれる診断ログや録画はGitに無断でコミットしない。`.gitignore` を尊重する。
- 配布用ZIPや.exeを作る場合も既存の起動バッチとNative Audio Helper構築フローを残す。
- 初回は `CODEX_FIRST_TASK_JA.md` の範囲だけを実行し、大規模なGPUエンジン全面書き換えは行わない。
