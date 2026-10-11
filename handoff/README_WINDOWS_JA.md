# v5.10.15 UI・スキャン・カメラ / GPU Full統合版

GitHubの `codex/lol-autocine-v51015-ui-scan-camera-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行。Windows取得にはmainマージやクラウドPublishは不要。

完全版だけなら `handoff/LoL_AutoCine_v5.10.15_UI_Scan_Camera_GPUFull_Windows_Full.zip` を開いて **Download raw file**。MergeChangesは前回Codex統合v5.10.14基準のGit差分。別バージョンへ上書きする場合は衝突を検査してください。

スキャン/表示プレイヤー/キル/アシストを右側へ集約。独立5ページ、出力内基本設定の折りたたみ、青チェック、DOF直下表示、わかりやすい素材/カラー名を統合。大きな仕上がり比較と本物のキラー画像の照会/取得/読込/加工はUI外の単一ワーカー、最新要求とリプレイ世代で古い結果を拒否。画像取得失敗は名前表示。旧設定・素材IDを保持。

RED通常三人称のpitchは校正済み符号を保持。自動REDだけyaw192→184°、手動blue/red0/180°は8°補正を適用しない。RED FPSだけoffset0.76倍。BLUE/シネマ/LolnamとTargetLockは保持。今回の構図の良否は実機未確認。

GPUエンジン・9切替演出・cut高速コピー・60fps時刻/フレーム数、NVENC/CPUfallback、LoL専用音声/録画/同期、37素材は保持。CPU制御/静止画生成/ライブミラー近似表示は残り、CPUゼロとは説明しません。

全pytest569件成功（失敗/skip/除外なし）。受領側の507件・1ファイル除外の結果とは別です。今回もミラー応答性テストを含め実行。担当衝突ガード、完全ZIP415ファイルと差分適用後417ソース一致、個人ファイル除外。Windows/NVIDIA/LoLの今回の画質・速度は未検証。

まとめテスト: **LoL_AutoCine/docs/WINDOWS_TEST_v51015_JA.md**。右側スキャン/対象切替→ミラーONの5ページ/DOF/スクロール/スライダー→青チェック→図鑑/日本語名/旧設定→大きな比較/本物のキラー画像の連続選択/再接続→BLUE/RED4カメラ→全10切替演出/1080p60fps/LoL音声/同期→中止再実行→GPU比較/診断収集。

## ローカルGitへ復元

```sh
git clone --single-branch --branch codex/lol-autocine-v51015-ui-scan-camera-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51015_Handoff
git clone --branch integration/v5.10.15 LoL_AutoCine_v51015_Handoff/handoff/LoL_AutoCine_v5.10.15_UI_Scan_Camera_GPUFull_all_branches.bundle LoL_AutoCine_v51015_Dev
cd LoL_AutoCine_v51015_Dev
git branch feature/gpu-camera-v51015 origin/feature/gpu-camera-v51015
git branch feature/ui-scan-v51015 origin/feature/ui-scan-v51015
git status --short
```

全80ブランチがorigin/*として復元されます。originはローカルbundle。担当ガード/共有レビューはdocs/CODEX_INTEGRATION_v51015_JA.md。旧設定/録画/プロジェクトを残して移行してください。
