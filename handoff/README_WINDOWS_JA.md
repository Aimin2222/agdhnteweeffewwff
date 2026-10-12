# v5.10.19-test CameraUI / SpatialQA / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.19_CameraUI_SpatialQA_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51019-camera-ui-qa-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windows取得にmainマージ/環境Publish不要。

通常third/RED geoのyaw=X・pitch=Y・roll0、古いtop基準の除外、REDシネマ/Lolnam接近制限を受領の補正候補として統合。BLUE geo従来式は保持。強制軸とrig metadataを一致させ、旧stable cacheで補正を取り消さない。カメラの画角・主役・上下反転改善はWindows未確認。

初期状態を無加工/vignette/grain/bloom0/cutへ、明示プリセットは選べる。かんたん/詳細の共有テンプレートとA/B図鑑、ON時だけ色微調整4項目、値保持。既存ミラー/DOF/スキャン/出力/図鑑scrollを保持。

QAはRED/BLUE別の確認MP4、前/中/後3時点比較、従来10演出と6キル登場に加え6空間切替を追加。再録画せず2素材を既存OpenCL deviceで合成しencoder_policy/実FX経路/実encoder/fallbackを記録。空間確認動画だけ無音、通常録画・side reelsは元音声を保持。GPU不可/失敗/timeoutはCPU xfade。通常モンタージュを置換しない。500MB直接ZIP/1MBstream/元動画・JSON・既存ZIP保持/最終JSON一致を維持。

Linux/Xvfb全653成功52.61秒（失敗/skip/除外なし）。6空間GPU kernelは検証用CPU PoCLで各95フレーム/60fps/先頭と末尾の素材一致、模様付き中間映像の差を検証。2side reels/3時点4カメラ/5比較画像と直接ZIP/CRCを実動画で検証。物理NVIDIA/Windows/LoL速度・構図は未確認。過去native終了は原因未確定で、今回成功を恒久修正とは扱わない。

完全ZIP473ファイル、差分適用後475ソース一致。旧99refsを保持し全103refs bundle。差分基準は前回Codex v5.10.18-test。実機手順はLoL_AutoCine/docs/WINDOWS_TEST_v51019_JA.md。中止は現在の1本を終えて残り停止、比較/ZIPを追加開始しない。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51019-camera-ui-qa-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51019_Handoff
git clone --branch integration/v5.10.19 LoL_AutoCine_v51019_Handoff/handoff/LoL_AutoCine_v5.10.19_CameraUI_SpatialQA_GPUFull_all_branches.bundle LoL_AutoCine_v51019_Dev
cd LoL_AutoCine_v51019_Dev
git branch feature/gpu-cameraqa-v51019 origin/feature/gpu-cameraqa-v51019
git branch feature/ui-cameraqa-v51019 origin/feature/ui-cameraqa-v51019
git status --short
```

全103refsはorigin/*で復元。originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51019_JA.md。
