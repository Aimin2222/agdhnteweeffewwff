# Windowsまとめてテスト v5.10.17-test

完全ZIPを旧版と別フォルダで展開しSTART_GPU.bat。旧設定/録画を保持。

1. 接続→試合全体スキャン→開発用「カメラ8本＋つなぎ演出10種類を自動テスト」を実行。8カメラ/10切替に加えbadge_motion_*.mp4が6本作成されるか確認。6本では新たなLoL録画が始まらないことも確認。
2. results.jsonのoutputs[].camera_diagnosticsへ8本のside/style/pitch_axis/pitch_sign/pitch_complement/baseline_rotation/side_heading_degrees/initial_camera_offset/initial_camera_rotationが入るか確認。画面の水平線反転/対象ロスト/地形にめり込む症状を区別し、RED/BLUEの通常三人称・シネマ・FPS・Lolnamを比較。ログは予定値であり映像判定ではない。
3. badge_motion_testsの6本を再生し、瞬時/左/右/下/上/popの方向・位置・時刻を比較。約3秒以下/60fps/元素材の音声を確認。render.gpu_effects_confirmedとrender.encoderを別々に確認。フォールバック時は理由が入り、CPU加工をGPU成功と表示しないか確認。
4. 通常の1シーン/全検出/チェック2シーンを書き出し、1080p60fps・色・元設定・LoL音声のみ・同期・録画後ミラー復帰を確認。TEST_GPU_RENDERの6ケース比較も行う。
5. ミラーONでスクロール/スライダー/ページ/DOF円・帯/素材連続選択/選択チェックが止まらないか確認。旧設定読み込み・6モーション・BLUE/RED再選択/seek/手動0・180度/TargetLockを確認。
6. QA途中で中止し次ケースを開始しないことを確認。エンコード中は現在の1本を終えてから残り停止する仕様。

この会話へAutoCine_Diagnostics.zipとQA results.jsonを添付。可能ならRED1本・BLUE1本の映像を共有し、水平線反転/対象ロスト/地形へのめり込みのどれかと操作・所要時間をメモ。個人ログや録画をGitHubへ無断追加しない。Windows/NVIDIA実機の性能はクラウドで保証しない。
