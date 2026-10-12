ユーザー開始CameraQAのRED4/BLUE4出力へ数値証拠を追加。既存rig/planからpitch軸/符号/補角・基準回転/位置/offset・開始時想定offset/rotationを記録しresults.jsonへ格納。QA専用ログでReplay API書込みを増やさず、カメラ式・TargetLock・UIを保持する。画角や水平線の良否を自動判定したとは扱わない。

8本/10切替に加え、録画済み映像から6登場モーションMP4を生成。再録画せずmin(3秒,素材長)/60fps/元音声copy。受領のCPU overlay/libx264固定を既存GPUFullStage・選択encoder_policy・診断・安全CPUfallbackへ接続。色/DOFを二重適用せず、実FX経路と実encoder/fallbackを別に記録する。中止は現在の1本終了後に残り停止。

受領指定v15GitHub基準へのapply --check/適用を別checkoutで確認。受領v16との差分だけ現行Codex v16へ統合し、古いGPU/カメラ/UIファイルを上書きしない。添付の実機/Actions記録は受領側資料として区別して保存。

検証: Linux/Xvfb全614成功66.45秒（失敗/skip/除外なし）、GPU障害/timeout/CPU比較・音声/60fps/encoder retry診断、QAログのAPI書込不変。6モーションのCPU PoCL OpenCL実出力は各60フレーム/元音声packet一致。物理GPU/Windows/LoL速度と画角は未検証。前回のLinux native終了は原因未確定、今回は全件で再発なし。旧UI/GPUエンジン/録画/音声/37PNG/旧91refを保持し全95refs bundle保存。完全ZIPと差分適用の全ソース一致、個人ファイル除外を確認。

前回v5.10.16を比較先とするDraft PR。mainへマージしません。完全ZIP→Download raw file、またはCode→Download ZIPで取得して別フォルダでSTART_GPU.bat。実機手順はdocs/WINDOWS_TEST_v51017_JA.md。
