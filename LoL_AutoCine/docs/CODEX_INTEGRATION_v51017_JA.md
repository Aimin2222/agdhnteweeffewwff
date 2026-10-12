# v5.10.17-test カメラ証拠 / GPU登場QA 統合

受領外ZIP内ZIPのCRC/パス/リンクを確認。README・全差分・3追加テストを読んだ。受領指定GitHub基準0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへのapply --check/適用を別checkoutで確認。受領v16と比べ追加はQA/数値ログ/3テスト/資料/バージョンだけ。現行Codex v16 beb18e06463bdc02bf43993a3bd60f95c4173121へ機能単位で統合し、古いGPU/カメラ/UIを上書きしていない。原ZIPはGit外attachmentsに保存。添付資料の実機/CIの主張は受領側記録であり、Codex実行結果と区別する。

変更: CameraQA名のジョブだけ、既存rig/planの数値をCAMERA_QA_POSE JSONとして記録しoutputs[].camera_diagnosticsへ格納。追加Replay API書き込みなし。通常カメラの式/俯角/RED184度/手動0・180度/TargetLockは保持。追加ログはcore/jobs.pyの共有blobをレビュー。証拠は予定値/開始リグであり、実動画の水平線や地形衝突を自動判定しない。

8カメラ/10切替は既存素材再利用・60fps・LoL専用音声/encoder_policyを保持。追加6モーションMP4は録画済み先頭クリップから作り、再録画しない。長さはmin(3秒,実素材長)、音声は元クリップからcopy。人物未指定の確認用装飾を一度だけ生成し、色/DOF等を二重適用しない。受領のCPU overlay/libx264固定を新helper core/gpu_badge_qa.pyで既存GPUFullStage/能力確認/エンコーダ選択/診断/CPUfallbackへ接続。CPU/OpenCL共通モーション式は前回版のまま。結果に実際のFX経路・encoder・fallback理由・60fpsを記録。NVENC→libx264 retryとGPU合成継続を別に記録。

GPU担当feature/gpu-camera-evidence-v51017、UI担当feature/ui-camera-evidence-v51017（前回UI内容を保持）、統合integration/v5.10.17、受領archive/received-ui-v51017。旧91先端を保持し全95refsを保存。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-camera-evidence-v51017 --ui feature/ui-camera-evidence-v51017 --integration integration/v5.10.17 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.17.json
```

共有8blobを固定。以後の変更は再レビュー。担当ガードはコミット済み先端なので未保存statusも確認。mainにはマージしない。旧配布物/設定/録画/診断/プロジェクトを保持。

UI/ミラー/DOF radio/ScanFix/PortraitFix/37PNG/旧alias、GPU Full全22FX/60fps時刻、LoL音声/録画/カメラコアは前回から保持。CPU制御/静止画・LUT準備/入力変換/音声/I/O/ミラー近似は残る。NVENCとGPUエフェクトは別。物理GPUのないクラウドPoCLはCPU OpenCLカーネル検証でありNVIDIA性能ではない。

中止は録画経路のstopへ渡し、つなぎと登場QAは現在の1本終了後に残りを止める。即時FFmpeg停止は未実装。Windows/LoLの画作り・速度・音声同期は手動確認。Linuxでは前回の全件604成功に加え代表実行で原因未確定のnative終了があり、安定性解決と断定しない。今回結果はhandoff/VERIFICATION_v5.10.17.json。
