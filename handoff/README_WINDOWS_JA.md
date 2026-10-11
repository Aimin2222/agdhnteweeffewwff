# v5.10.14 Studio / GPU Full統合版

GitHubの `codex/lol-autocine-v51014-studio-gpu-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行。Windows取得にはmainマージやクラウドPublishは不要。

完全版だけなら `handoff/LoL_AutoCine_v5.10.14_Studio_GPUFull_Windows_Full.zip` を開いて **Download raw file**。MergeChangesは前回Codex統合v5.10.13基準のGit差分。別バージョンへ上書きする場合は衝突を検査してください。

5作業領域（シーン/カメラ/カラー/FX/出力）、折りたたみ、キルフレーム図鑑の検索/分類/拡大/適用、500ms仕上がりホバー、DOF実フレーム比較を統合。画素加工はUI外ワーカーで実行し、最新要求だけ表示、閉じる時は停止。画像取得エラーも表示。旧設定の切替演出名と手動カメラの基準角を保持。

切替演出はcutの高速コピーと9種類のGPU Full/OpenCL。映像フレーム数と60fps時刻を明示し、音声はcopy。GPU非対応/失敗は理由を記録してCPUへ戻る。静止画の生成とライブミラーの近似表示はCPUです。NVENCとGPUエフェクトを混同せず、CPUゼロとは説明しません。

RED通常三人称のpitch補正は当該モードだけ。BLUE/シネマ/FPS/Lolnam、TargetLock、LoL専用音声/録画/同期、旧GPU比較テストと37素材を保持。RED自動192°と今回の上下補正の実映像は未確認。

全pytest542件成功（65.56秒、失敗/skipなし）、担当衝突ガード、完全ZIPと差分適用後402ソース一致。全9演出のOpenCLカーネルをCPU PoCL検証環境で実行し60fps/60フレーム/音声同一性を確認。製品側はCPU OpenCL拒否を維持。Windows/NVIDIA/LoLの今回の画質・速度は未検証。

まとめテスト: **LoL_AutoCine/docs/WINDOWS_TEST_v51014_JA.md**。ミラーONの5領域/折りたたみ/スクロール/スライダー→図鑑の検索/発光/拡大/適用→500msホバーとDOF比較→BLUE/RED4カメラ→全10切替演出/1080p60fps→LoL音声/同期→中止再実行→GPU比較と診断収集。

## ローカルGitへ復元

```sh
git clone --single-branch --branch codex/lol-autocine-v51014-studio-gpu-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51014_Handoff
git clone --branch integration/v5.10.14 LoL_AutoCine_v51014_Handoff/handoff/LoL_AutoCine_v5.10.14_Studio_GPUFull_all_branches.bundle LoL_AutoCine_v51014_Dev
cd LoL_AutoCine_v51014_Dev
git branch feature/gpu-montage-v51014 origin/feature/gpu-montage-v51014
git branch feature/ui-studio-v51014 origin/feature/ui-studio-v51014
git status --short
```

全76ブランチがorigin/*として復元されます。originはローカルbundle。担当ガード/共有レビューはdocs/CODEX_INTEGRATION_v51014_JA.md。旧設定/録画/プロジェクトを残して移行してください。

GitHubから新規取得し、402ソース/76refs/ZIPとbundleのハッシュ一致、復元後代表126テスト（8.30秒）を確認。セットアップ再実行で個人ファイル相当3件を保持しました。次回クラウド用の設定は下書きだけ保存してあり、Windows取得にはPublish不要です。
