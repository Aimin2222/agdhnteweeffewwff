# v5.10.25-test BLUE6 / Reference / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.25_BLUE6_Reference_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51025-blue6-reference-handoff** の **Code → Download ZIP**。旧版と別フォルダLoL_AutoCine/START_GPU.bat。Windows取得にmainマージ/環境Publishは不要。

映像動作はBLUE通常third X +3→-2（差-5度）のみ。距離1.10/offset/FOV/Orbit/keyframe・速度、RED全5と他BLUEは維持。実setupでORDER/BLUE・side auto/blue/red・keyframe/gain付きの旧+3版と3時点比較、位置/FOV/Y/Z不変でXだけ-5。中心/遮蔽・上端切れ改善はWindows未確認。RED1/3相対中心・手動0/180/FPS高さ・team/mode cacheとstable/TargetLock保持。

4参考映像の演出JSONは静止画と受領側説明の資料で通常template/QA/UIへ自動適用なし。29本をCodexで解析した結果ではない。noir全体低彩度と未実装の動的部分カラーmaskを区別。既定FX/vignette/barsは変更なし。

GPU22FX/OpenCL/NVENC/60fps・LoL専用音声/録画/診断fallback/ミラー/oneclickQA/cache・partial/二重押し・stop/7指定ログ各1MB/1MBstream・500MB直接ZIP/最終JSON/参照ZIP・CRC/上限120本・各1GB・合計4GB/flatten・原名対応・temp cleanup・Unicode/cancel/Explorer保持。GPU/音声/録画/UI/camera/jobs本体byte不変。全785自動テスト成功、失敗/skip/除外なし、70.371秒。関連66成功1.25秒。初回と2回目は追加fixture形式不備で各60成功/6失敗、既存time/yaw/zoom/fovへfixtureのみ修正。Windows/LoL/BAT/NVIDIAは未確認、過去native139/132原因は未確定。

完全ZIP535、差分apply後537ソース一致、全127refs bundle・旧229配布物保持。実機手順LoL_AutoCine/docs/WINDOWS_TEST_v51025_JA.md。添付実機/CI/Release評価は受領側。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51025-blue6-reference-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51025_Handoff
git clone --branch integration/v5.10.25 LoL_AutoCine_v51025_Handoff/handoff/LoL_AutoCine_v5.10.25_BLUE6_Reference_GPUFull_all_branches.bundle LoL_AutoCine_v51025_Dev
cd LoL_AutoCine_v51025_Dev
git branch feature/gpu-cameraqa-v51025 origin/feature/gpu-cameraqa-v51025
git branch feature/ui-cameraqa-v51025 origin/feature/ui-cameraqa-v51025
git status --short
```
全refsはorigin/*へ復元、originはローカルbundle。handoff/*.bundle binaryを保持。個人設定/録画は保管。
