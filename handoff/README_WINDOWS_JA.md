# v5.10.18-test ReleaseQA / DirectZIP / GPUFull

完全版 **handoff/LoL_AutoCine_v5.10.18_ReleaseQA_DirectZIP_GPUFull_Windows_Full.zip** をGitHubで開き **Download raw file**。または **codex/lol-autocine-v51018-releaseqa-directzip-handoff** の **Code → Download ZIP**。旧版と別フォルダへ展開してLoL_AutoCine/START_GPU.bat。Windows取得にmainマージ/環境Publishは不要。

新規カラー既定を無補正にし、図鑑open中は背後パネルwheelを抑制。QAボタンでデータ専用計画を取得（失敗時付属へ）、既知操作/64KB/3秒/100〜500MBだけ許可。付属計画はRED/BLUE各5カメラ（従来4＋geo_aim実験）と10切替/6登場モーション。plan未指定APIは従来8本。geoは選択時だけ相対座標で視線を計算し、従来カメラ式は保持。数値/実フレーム比較表は参考値で、主役や上下反転を自動合格判定しない。

QA結果は500MB以下の直接ZIPへ保存しZIPの入れ子なし。巨大MP4は1MBずつstreamしてpartへ分割、結合手順付き。原動画/JSON/既存ZIPを消さず、repeatは別名。出力名を先に計画しZIP内JSONを最終結果と一致。従来GPU Full/60fps/LoL専用音声/素材再利用/encoder policyを維持。静止画/音声/I/O/制御/ミラー近似はCPUも使う。

Linux/Xvfb全635成功82.14秒（失敗/skip/除外なし）。合成の実動画から2カメラ比較/2画像と直接ZIP/final JSON/CRCを検証。大きな動画の分割・再結合・元データ保持/再出力/symlink除外もテスト。Windows/LoL/NVIDIA速度とgeo実構図は未確認。前回native終了の原因は未確定で、今回成功を恒久修正とは扱わない。

完全ZIP461ファイル、差分適用後463ソース一致。旧95refsを保持し全99refs bundle。差分基準は前回Codex v5.10.17-test。実機手順はLoL_AutoCine/docs/WINDOWS_TEST_v51018_JA.md。QA中止は現在の1本を終えて残り停止、比較表/ZIPも追加開始しない。

## ローカルGit復元
```sh
git clone --single-branch --branch codex/lol-autocine-v51018-releaseqa-directzip-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51018_Handoff
git clone --branch integration/v5.10.18 LoL_AutoCine_v51018_Handoff/handoff/LoL_AutoCine_v5.10.18_ReleaseQA_DirectZIP_GPUFull_all_branches.bundle LoL_AutoCine_v51018_Dev
cd LoL_AutoCine_v51018_Dev
git branch feature/gpu-releaseqa-v51018 origin/feature/gpu-releaseqa-v51018
git branch feature/ui-releaseqa-v51018 origin/feature/ui-releaseqa-v51018
git status --short
```

全99refsはorigin/*で復元。originはローカルbundle。設定/録画/プロジェクトを保管。担当ガードはdocs/CODEX_INTEGRATION_v51018_JA.md。
