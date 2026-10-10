# v5.10.10 実シーン図鑑・キルログ素材 / GPU Full統合版

GitHubの `codex/lol-autocine-v51010-real-scene-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行。取得・起動にはmainマージやクラウドPublishは不要。

完全版だけなら `handoff/LoL_AutoCine_v5.10.10_RealScene_GPUFull_Windows_Full.zip` を開いて **Download raw file**。MergeChangesは前回Codex v5.10.7基準のGit差分で、UI単独版v5.10.9へそのまま上書きしない。

v5.10.8→9→10を順にレビューして統合。実シーンの選択・移動・撮影による補正前/後の図鑑、キルログ素材6種、追加カラー、発光プリセット/強度/角の光/行間を追加。新しい行間と角の光を既存GPU書き出しへ接続。画像未保存なら案内を表示し、仮のゲーム画像で代用しない。静止画比較は色/2D FXの近似で、カメラの動きや時間演出は動画で確認する。

図鑑の読込・色/FX処理は単一ワーカーへ移し、最新要求だけ保持。Tkは画像表示だけ行う。同件数の再スキャンで古い選択肢が残る問題も修正。ミラーは「操作優先」を初期値にし、従来の操作中負荷対策を保持。「表示サイズで確認」で高解像度のミラーも選択でき、選択を保存。ライブミラーはCPU/Pillowの近似表示、書き出しはGPU Fullと60fpsを維持する。

GPU/録画/TargetLock/LoL専用音声の既存処理、TEST_GPU_RENDERの起動ログ・pause・6ケース、Windowsの起動バッチとNative Audio Helper構築を保持。全pytest407件成功（43秒、失敗/skipなし）。素材の実アイコン、発光、CPU/GPU行間、実Tkの応答・品質選択を確認。**今回の新Windows版は実機未確認**。

まとめテスト: **LoL_AutoCine/docs/WINDOWS_TEST_v51010_JA.md**。
1. ミラーONで発光/色/スライダー/タブ/スクロール。「操作優先」と「表示サイズで確認」を比較。
2. キル＋アシストをスキャンし図鑑→①移動→場面確認→②保存。検索/適用/同件数再スキャンを確認。
3. 素材6種、発光OFF/弱/強・角の光・行間を同シーンで比較。1080p/60fpsの1/複数シーン、色、実アイコン、LoLのみの音声/同期、三人称/BLUE/REDを確認。
4. アプリを閉じTEST_GPU_RENDERで同じrawを6ケース比較→COLLECT_DIAGNOSTICSのZIPを送る。

## ローカルGitに戻す

```sh
git clone --single-branch --branch codex/lol-autocine-v51010-real-scene-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51010_Handoff
git clone --branch integration/v5.10.10 LoL_AutoCine_v51010_Handoff/handoff/LoL_AutoCine_v5.10.10_RealScene_GPUFull_all_branches.bundle LoL_AutoCine_v51010_Dev
cd LoL_AutoCine_v51010_Dev
git branch feature/gpu-material-v51010 origin/feature/gpu-material-v51010
git branch feature/ui-real-scenes-v51010 origin/feature/ui-real-scenes-v51010
git status --short
```

全63ブランチはorigin/*に復元され、originはローカルbundle。担当ガード/共有レビューはdocs/CODEX_INTEGRATION_v51010_JA.md。個人設定・プロジェクト・録画は既存フォルダに保持したまま移行する。
