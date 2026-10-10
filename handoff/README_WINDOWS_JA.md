# v5.10.13 一括スキャン・表示プレイヤー・カメラ・素材 / GPU Full統合版

GitHubの `codex/lol-autocine-v51013-match-camera-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行。Windows取得にはmainマージやクラウドPublishは不要。

完全版だけなら `handoff/LoL_AutoCine_v5.10.13_PlayerFilter_GPUFull_Windows_Full.zip` を開いて **Download raw file**。MergeChangesは前回Codex統合v5.10.10基準のGit差分。PNGはbinary patchに収録され、テキストだけ上書きしても素材は追加されません。UI単独版へGPUファイルを上書きしないでください。

v5.10.11→12→13をレビューして統合。一括スキャンのキャッシュで表示プレイヤー/キル/アシストを切り替え、処理中の対象変更や中断・再接続後の古い結果を防ぐ。BLUE/REDのカメラ姿勢、図鑑の大きい比較画像と拡大表示、自動QA、素材37種類を追加。書き出し素材は770×232、CPU/GPUとも元の画面サイズへ縮小。受領PNGの絵は保持。

RED自動192°は受領変更の暫定構図で、Windows実映像は未確認。手動ブルー/レッドの0°/180°も選べます。基準角をスマート構図の制限で潰さず、カメラの位置と視線を同じ方向へ。API俯角の補数表現を判定し、判定不能時は安全なトップへ戻ります。

ミラー「操作優先」、設定変更時だけのsnapshot、図鑑/拡大の単一画像ワーカーを保持。ライブミラーはCPU/Pillow近似表示です。GPU Full/OpenCL、NVENC、60fpsタイムスタンプとフレーム数、LoL専用音声/同期、録画、GPU比較テストは従来の修正を保持。

全pytest499件成功（47秒、失敗/skipなし）、担当衝突ガードと完全ZIP/差分適用後の全ソース一致を確認。今回のWindows/NVIDIA/LoL実機の映像・音声・速度は未検証。

まとめテスト: **LoL_AutoCine/docs/WINDOWS_TEST_v51013_JA.md**。一括スキャン→表示対象/モード/チェック切替→BLUE/RED4カメラ→旧/追加素材と行間/発光→ミラーONの図鑑/拡大/色/スクロール→1080p60fpsの1/複数シーンとLoLだけの音声→自動QAとGPU比較6ケース→COLLECT_DIAGNOSTICS。

## ローカルGitへ復元

```sh
git clone --single-branch --branch codex/lol-autocine-v51013-match-camera-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v51013_Handoff
git clone --branch integration/v5.10.13 LoL_AutoCine_v51013_Handoff/handoff/LoL_AutoCine_v5.10.13_PlayerFilter_GPUFull_all_branches.bundle LoL_AutoCine_v51013_Dev
cd LoL_AutoCine_v51013_Dev
git branch feature/gpu-shared-v51013 origin/feature/gpu-shared-v51013
git branch feature/ui-player-filter-v51013 origin/feature/ui-player-filter-v51013
git status --short
```

全72ブランチがorigin/*として復元されます。originはローカルbundle。担当ガード/共有レビューはdocs/CODEX_INTEGRATION_v51013_JA.md。既存フォルダの設定/プロジェクト/録画を保持して移行してください。
