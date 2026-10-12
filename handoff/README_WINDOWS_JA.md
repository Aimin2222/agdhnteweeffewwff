# v5.10.17-test CameraEvidence / BadgeQA / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.17_CameraEvidence_BadgeQA_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51017-camera-evidence-badgeqa-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windows取得にはmainマージ/環境Publish不要。

RED4/BLUE4録画のresults.jsonにカメラの数値証拠を追加。ログ用のAPI書込は増やさず、前回のカメラ式/TargetLock/旧UIを保持。8本/10切替に追加して録画済み映像から6登場モーションMP4を生成。再録画/音声再収録なし。受領CPU/libx264固定を既存GPUFullStage/選択encoder_policy/診断/安全CPUfallbackへ接続。60fpsと元音声copy、色/DOF等は二重適用しない。

Linux/Xvfb全614成功（66.45秒、失敗/skip/除外なし）。6登場QAをCPU PoCL OpenCLで実レンダリングし各60フレーム/音声packet一致を確認。物理NVIDIA/Windows/LoL性能は未確認。前回のLinuxネイティブ終了は原因未確定で、今回全件で再発なし。過去の異常を解決したとは主張しない。CPU制御/音声/I/O/静止画準備/ミラーは残る。

完全ZIP448ファイル、差分適用後450ソース一致。旧91refsを保持し全95refsをbundle保存。差分基準は前回Codex v5.10.16-test。実機手順はLoL_AutoCine/docs/WINDOWS_TEST_v51017_JA.md。QA中止は次ケース停止で、現在の切替/モーションエンコードを終えてから残り停止。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51017-camera-evidence-badgeqa-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51017_Handoff
git clone --branch integration/v5.10.17 LoL_AutoCine_v51017_Handoff/handoff/LoL_AutoCine_v5.10.17_CameraEvidence_BadgeQA_GPUFull_all_branches.bundle LoL_AutoCine_v51017_Dev
cd LoL_AutoCine_v51017_Dev
git branch feature/gpu-camera-evidence-v51017 origin/feature/gpu-camera-evidence-v51017
git branch feature/ui-camera-evidence-v51017 origin/feature/ui-camera-evidence-v51017
git status --short
```

全95refsはorigin/*として復元。originはローカルbundle。既存設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51017_JA.md。
