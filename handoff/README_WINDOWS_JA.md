# v5.10.16-test Motion / CameraQA / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.16_Motion_CameraQA_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51016-motion-cameraqa-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。mainマージ/環境Publishは取得に不要。

登場モーション6種類をCPUとGPU両方へ追加。非pitchの急反転ガードを校正リセット後も保持し、リプレイ変更で消去。RED4/BLUE4の8本を60fps/LoL音声で録画し、2本の素材を全10切替で再利用するユーザー開始QAを追加。DOF radio/スクロール/表示名を統合し、前回ScanFix/PortraitFix/非同期ミラー/全旧名/37PNGを保持。

Linux/Xvfb全604成功（失敗/skip/除外なし）。6登場モーションは検証用CPU PoCLでOpenCLカーネルとCPU出力の60フレーム・位置一致を検証。物理NVIDIA/Windows/LoL性能は未確認。以前ScanFixのLinuxネイティブ終了は原因未確定だが今回全件で再発なし。CPU制御/音声/I/O/静止画準備/ミラープレビューは残る。

完全ZIP438ファイル、差分適用後440ソース一致。旧87refsを保持し全91refsをbundle保存。差分は前回Codex ScanFixだけが基準。Windows手順はLoL_AutoCine/docs/WINDOWS_TEST_v51016_JA.md。QA中止は次ケース停止、切替エンコード中は現在の1本を終えてから停止。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51016-motion-cameraqa-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51016_Handoff
git clone --branch integration/v5.10.16 LoL_AutoCine_v51016_Handoff/handoff/LoL_AutoCine_v5.10.16_Motion_CameraQA_GPUFull_all_branches.bundle LoL_AutoCine_v51016_Dev
cd LoL_AutoCine_v51016_Dev
git branch feature/gpu-motion-v51016 origin/feature/gpu-motion-v51016
git branch feature/ui-motion-v51016 origin/feature/ui-motion-v51016
git status --short
```

全91refsはorigin/*で復元。originはローカルbundle。既存設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51016_JA.md。

GitHub復元で全440ソース/91refs/配布物hash一致、再setupで3個人ファイル相当を保持。復元先代表テストは通常実行と記録のみ診断でIllegal instruction/132が2回発生、原因未確定。直前のメインスレッドGC回収を1回加える診断条件では95成功（12.45秒）。標準条件での復元先代表全件完走は未確認。全604成功と区別し、Windowsの修正効果やLinuxテスト安定化を主張しない。
