# v5.10.15 Scan / DOF / Checkbox / CameraFix GPUFull

完全版: handoff/LoL_AutoCine_v5.10.15_ScanUI_DOF_Checkbox_CameraFix_GPUFull_Windows_Full.zip をGitHubで開き **Download raw file**。または codex/lol-autocine-v51015-scan-dof-camera-handoff ブランチの **Code → Download ZIP**。旧版と別フォルダへ展開しLoL_AutoCine/START_GPU.bat。mainマージ/環境Publishは取得に不要。

右側①ボタンへ接続/プレイヤー取得/試合全体スキャンを統合。円形DOFと従来帯DOFは中央/右側とも排他表示し値を保持。チェックは高解像度から縮小し、選択済みのhover/disabledで表示を保つ。カメラ再選択/プレビューは校正キャッシュをリセット。表示名は簡潔にし旧名全件と保存IDを保持。画像Player互換も保持。

開発用一括録画はBLUE/RED代表キルの4カメラと、対象に2キル以上あれば全10切替モンタージュを_dev_replay_qaへ出力。既存GPU/LoL専用音声のrun_auto_editをworkerから使用。中止後は次のケースへ進まず入力を解放。生成に時間がかかる開発補助機能。GPU/60fps/音声/TargetLock/カメラ座標は前回と同じ。

最終Linux/Xvfb全585テスト成功（失敗/skip/除外なし）。最初の実行でネイティブ終了2回（原因未確定）。記録付き再実行は584成功・既存プレビューテスト1失敗、模擬プレイヤー情報を補完後に全件を再検証。再発しないという保証はしない。今回Windows/NVIDIA/LoL実機は未確認。

完全ZIP429ファイル、差分適用後431ソース一致。旧83refs/416既存ファイル/37PNG保持。MergeChangesは前回PortraitCrashFix基準、別版に単純上書きしない。確認手順はLoL_AutoCine/docs/WINDOWS_TEST_SCANFIX_v51015_JA.md。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51015-scan-dof-camera-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_ScanFix_Handoff
git clone --branch integration/v5.10.15-scanfix LoL_AutoCine_ScanFix_Handoff/handoff/LoL_AutoCine_v5.10.15_ScanUI_DOF_Checkbox_CameraFix_GPUFull_all_branches.bundle LoL_AutoCine_ScanFix_Dev
cd LoL_AutoCine_ScanFix_Dev
git branch feature/gpu-scanfix-v51015 origin/feature/gpu-scanfix-v51015
git branch feature/ui-scanfix-v51015 origin/feature/ui-scanfix-v51015
git status --short
```
全87ブランチをorigin/*として復元。originはローカルbundle。docs/CODEX_INTEGRATION_SCANFIX_v51015_JA.mdの担当ガードを実行。設定/録画/プロジェクトは保管。
