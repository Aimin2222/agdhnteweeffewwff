# v5.10.24-test TargetCenter / VideoZIP / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.24_TargetCenter_VideoZIP_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51024-target-center-zip-handoff** の **Code → Download ZIP**。旧版と別フォルダでLoL_AutoCine/START_GPU.bat。Windows取得はmainマージ/環境Publish不要。

RED auto通常third/FPSだけ相対offsetから同じRED軸yaw/pitchへ。thirdの自動X+4を除き、手動third前版X+4/手動FPS0・180/高さ/位置式を維持。RED2/4/5・BLUE全5・手動4ケースの計12ケース各3時点でv23位置/回転一致。構図/実軸/遮蔽改善はWindows未確認。

参照動画ZIPを120本・各1GB・合計4GB上限で一時展開、動画拡張子だけsafe連番名/../も平坦化、原名対応JSON。展開前上限・CRCエラー・1MB chunk実byte制限・一時掃除・元ZIP不変。結果は6時点JPEG/JSONだけで元動画やZIPを含めない。ダブルクリックpicker/動画ZIP/フォルダ/drag/日本語stem/明示root cleanup/cancel・最新ログ・Python候補実import/ASCII・UTF8・直後status保持。ドラッグとpicker両方で実結果フルパス、Windows CI外の成功時のみExplorer。失敗/cancelでは開かない。静止参照CPU処理は通常GPU動画経路外。

前回GPU全22FX/60fps時刻・フレーム数/LoL専用音声/NVENC/診断・fallback/ミラー応答/oneclick QA・complete cache/partial・二重押し・stop/指定7ログ各1MB末尾原byte/1MBstream・500MB直接ZIP/最終JSONを保持。全776自動テスト成功、失敗/skip/除外なし、71.310秒。関連89成功3.28秒。Windows/LoL/BAT日本語パス・Explorer/NVIDIA速度は未確認、過去native139/132原因は未確定。

完全ZIP525ファイル、差分適用後527ソース一致、全123refs bundle。旧220配布物保持。実機手順LoL_AutoCine/docs/WINDOWS_TEST_v51024_JA.md。元ZIPの実機/CI/Release記述は受領側資料、Codex実測とは別。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51024-target-center-zip-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51024_Handoff
git clone --branch integration/v5.10.24 LoL_AutoCine_v51024_Handoff/handoff/LoL_AutoCine_v5.10.24_TargetCenter_VideoZIP_GPUFull_all_branches.bundle LoL_AutoCine_v51024_Dev
cd LoL_AutoCine_v51024_Dev
git branch feature/gpu-cameraqa-v51024 origin/feature/gpu-cameraqa-v51024
git branch feature/ui-cameraqa-v51024 origin/feature/ui-cameraqa-v51024
git status --short
```
全refsはorigin/*へ復元、originはローカルbundle。handoff/*.bundle binary属性を保持。設定/録画/プロジェクトは保管。共有ガードはdocs/CODEX_INTEGRATION_v51024_JA.md。

GitHubから別checkout/bundle復元で全527ソース/123refs/ZIP・bundle hashes一致。復元先代表267成功22.65秒、失敗/skip/除外なし、GC有効・強制GCなし。再setupで527ソース/123refs/3個人設定相当のバイト保持/status clean。これは同一クラウド内の別フォルダ検証で新しいcloud task/Windows/Publish検証とは別。環境install_script/start_skillをrevision42へ保存してreadback確認、他の既知設定保持、Publishは未実行。次回環境へ反映する場合だけ環境設定で確認・保存後Publish。
