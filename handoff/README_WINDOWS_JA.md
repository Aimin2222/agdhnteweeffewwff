# v5.10.15 PortraitCrashFix GPUFull

完全版: handoff/LoL_AutoCine_v5.10.15_PortraitCrashFix_GPUFull_Windows_Full.zip をGitHubで開き **Download raw file**。または codex/lol-autocine-v51015-portrait-crashfix-handoff ブランチの **Code → Download ZIP**。旧版と別フォルダへ展開しLoL_AutoCine/START_GPU.batで起動。Windows取得にmainマージ/環境Publishは不要。

Player形式と辞書形式の両方をcore/kill_icons画像ID取得APIで安全に扱う小さい修正。既存UIは辞書snapshotを渡しているので、Linuxで同じWindows画面クラッシュを再現したという意味ではない。GPU/60fps/NVENC/音声/TargetLock/UIは前回版と同一。CPUゼロや物理GPU速度は主張しない。

全574テスト成功（失敗/skip/除外なし）。完全ZIP422ファイル、Gitパッチ適用後424ソース一致。旧80refs/415ファイル/37PNG保持。今回のWindows/NVIDIA/LoL実機は未確認。まとめテスト: LoL_AutoCine/docs/WINDOWS_TEST_PORTRAITFIX_v51015_JA.md（画像連続選択、未キャッシュ/オフライン、ミラーON、1080p60fps+GPU+LoL音声）。

MergeChangesは前回Codex統合v5.10.15基準。別バージョンへ単純上書きしない。Gitパッチは先に--check、単体Gitルートでは-p2を追加。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51015-portrait-crashfix-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_PortraitFix_Handoff
git clone --branch integration/v5.10.15-portraitfix LoL_AutoCine_PortraitFix_Handoff/handoff/LoL_AutoCine_v5.10.15_PortraitCrashFix_GPUFull_all_branches.bundle LoL_AutoCine_PortraitFix_Dev
cd LoL_AutoCine_PortraitFix_Dev
git branch feature/gpu-portraitfix-v51015 origin/feature/gpu-portraitfix-v51015
git branch feature/ui-scan-v51015 origin/feature/ui-scan-v51015
git status --short
```
全83ブランチがorigin/*で復元される。originはローカルbundle。担当ガードはdocs/CODEX_INTEGRATION_PORTRAITFIX_v51015_JA.md。旧設定/録画/プロジェクトを残して移行。

GitHubから固定payloadを取得して424ソース/83refs/ZIPとbundleのハッシュ一致を確認。復元先代表92テスト成功、セットアップ再実行で424ソース/83refs/設定相当3ファイル保持、status clean。install_script/start_skillを保存して読戻し一致を確認、他の環境設定は保持。Publish未実施。これは同じクラウド実行環境の別フォルダ検証で、Windows/NVIDIA実機の検証ではない。
