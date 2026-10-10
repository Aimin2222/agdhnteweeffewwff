# v5.10.5をWindowsで取得する

GitHubの `codex/lol-autocine-v5105-responsive-ui-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行してください。mainマージやクラウド環境PublishはWindowsの取得/起動に不要です。

GitHubの `handoff/LoL_AutoCine_v5.10.5_ResponsiveUI_Windows_Full.zip` を開き **Download raw file** でも取得できます。完全版は単体起動用、MergeChangesは前回v5.10.4基準のGitパッチです。説明書の移動/旧パス削除があるので差分ファイルのコピーだけで更新しないでください。

ミラーONで設定変更・タブ/スクロールが詰まる原因だった画像変換/FX合成を別スレッドに移し、待ち行列を最新1件に制限しました。簡易FX最大15Hz/540p、通常録画・最終出力60 FPSです。グラフ更新をまとめ、キルフレームの公式画像取得もUIを止めません。v5.10.5の3段キルログ・発光・説明・サイド基準カメラも統合しています。

旧説明書27件を保存して整理し、ルートREADMEとSTART_HEREを現在の案内へ更新しました。起動/音声ヘルパーバッチ、core/ui/assets/toolsの位置と機能は維持します。単体exeは今回未作成です。

受領Windows診断では5本とも60 FPS、GPU Bloom+DOFとNVENCで成功、加工45.1～57.5秒。CPUの色補正/粒子/合成/変換・ミラー簡易合成は残ります。CPU81～88%はPC全体でありアプリ単独ではありません。新しい統合版のWindows改善率は未確認です。

全回帰332件成功（33.58秒、失敗/skipなし）。重い合成を止めた状態でも実Tkのスライダー・タブ・コールバックが動くこと、古い設定の破棄・ワーカー終了・ダウンロード中の応答性を確認。完全版285/差分54、旧パス削除を含むパッチ適用後287ソース一致、旧配布物84件の保存を確認します。

詳しい確認手順: LoL_AutoCine/docs/WINDOWS_TEST_v5105_JA.md。ミラーON+FX反映ONで色/DOFの連続操作とタブ/ホイール、60 FPS・Bloom+DOFの1シーン→複数シーン、色/焦点/TargetLock/LoL音声/同期を試してください。最後にCOLLECT_DIAGNOSTICSで診断ZIPを作成してください。

## ローカルGitで開発する場合

新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5105-responsive-ui-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v5105_Handoff
git clone --branch integration/v5.10.5 LoL_AutoCine_v5105_Handoff/handoff/LoL_AutoCine_v5.10.5_ResponsiveUI_all_branches.bundle LoL_AutoCine_v5105_Dev
cd LoL_AutoCine_v5105_Dev
git branch feature/gpu-shared-v5105 origin/feature/gpu-shared-v5105
git branch feature/ui-responsive-v5105 origin/feature/ui-responsive-v5105
git branch integration/v5.10.4 origin/integration/v5.10.4
git status --short
git branch --all
```

全51ブランチはorigin/*へ復元されます。このcloneのoriginはPC上のbundleです。共有APIの担当ガードはdocs/CODEX_INTEGRATION_v5105_JA.mdを参照してください。
