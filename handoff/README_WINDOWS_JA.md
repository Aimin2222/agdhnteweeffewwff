# v5.10.21-test CameraDirector / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.21_CameraDirector_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51021-camera-director-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windowsへの取得にmainマージ/環境Publishは不要。

受領のチーム/モード別小補正、FPS対象相対位置、RED192度を統合。手動0/180度とFPS高さをCodexで保持、NaN角度を拒否。校正とstable rotationのモード分離も保持。RED2/BLUE7の追加角度はゼロ、BLUE7距離は不変、RED2距離0.96。実構図改善はWindows未確認。

色微調整/ディレクターを変数traceで直下展開。強さ0〜1.5をUIで検証し、Template末尾の任意値へsnapshotしてCameraPlanの接近量と明示Orbitゼロへ接続。旧位置引数/JSON/None/scene replaceを保持。0%でもスタイル固有FOV/スロー/ローアングル/keyframeは残る。MAKE_REFERENCE_SHEETS.batは単体動画/フォルダ、入力別出力先、TEMPログ/pause。6時点JPEG/JSON/ZIPはローカルだけ、元動画不変・外部送信なし。空フォルダも有効ZIP。

GPU全22FX/60fps時刻/LoL専用音声/NVENC/選択policy/CPU fallback診断/500MB直接ZIP/1MBstream/ミラー応答/capture終了テスト同期を保持。Linux/Xvfb全696成功、失敗/skip/除外なし、58.339秒。実GPU/Windows/LoL画角・BAT実行・性能は未確認。過去Linux native139/132は原因未確定、成功を恒久修正とは扱わない。

完全ZIP494ファイル、差分適用後496ソース一致、全111refs bundle（binary属性でWindows改行変換を防止）。差分基準は前回Codex v5.10.20-test。実機手順はLoL_AutoCine/docs/WINDOWS_TEST_v51021_JA.md。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51021-camera-director-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51021_Handoff
git clone --branch integration/v5.10.21 LoL_AutoCine_v51021_Handoff/handoff/LoL_AutoCine_v5.10.21_CameraDirector_GPUFull_all_branches.bundle LoL_AutoCine_v51021_Dev
cd LoL_AutoCine_v51021_Dev
git branch feature/gpu-cameraqa-v51021 origin/feature/gpu-cameraqa-v51021
git branch feature/ui-cameraqa-v51021 origin/feature/ui-cameraqa-v51021
git status --short
```

全refsはorigin/*へ復元。originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51021_JA.md。
