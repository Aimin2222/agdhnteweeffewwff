# v5.10.4 GPUFX Capture60をWindowsで試す

GitHubの `codex/lol-autocine-v5104-handoff` ブランチで **Code → Download ZIP**。前回版とは別フォルダへ展開して **LoL_AutoCine/START_GPU.bat** を起動してください。mainマージ/クラウド環境Publishは不要です。

GitHubの `handoff/LoL_AutoCine_v5.10.4_GPUFX_Capture60_Windows_Full.zip` の **Download raw file**でも取得できます。差分ZIPは前回v5.10.3 Capture60基準で、単体起動用ではありません。

v5.10.4 UI側のタブ誤切替防止、カメラ再生中のミラー簡易FX、カメラ通信Keep-Aliveと遅いAPI向け制限を統合しました。既存の非同期ミラー/書き出し保護、GPU Bloom・円形DOF・Focus Blur、60fps録画/時間補正/加工、LoL専用音声を保持。受領cameraの全モード0.40倍下限は従来スローを変えるため修正し、0.35倍を維持しています。

最新診断は統合前のCapture60版。4本すべて録画/時間補正/加工60fps、GPU Bloom + NVENC成功、加工46.9～51.6秒、モンタージュも成功。CPU色補正・粒子・合成/変換は残っています。PC全体CPU平均83～88%はアプリ単独の値ではありません。今回DOFは選択されていないため、この診断でDOF稼働とは言いません。

全pytest311件成功（30.71秒、失敗/skipなし）。実Tk/実HTTP/実FFmpeg/子プロセスの回帰、接続再利用/切断/HTTP500/同時接続/POST重複送信防止、共有APIとGPUファイル保持を確認。新しいv5.10.4統合版のWindows実機UI/カメラ/音声同期は未検証です。

詳細編集のタブ上ホイールでタブが変わらずクリックで切り替わること、ミラーON + FX反映ONでカメラ再生中の円形DOF表示、書き出し中は簡易FX停止を確認。同じ1シーンと4シーン連続で色/焦点/対象追従/LoLだけ音声/同期/速度を確認してください。COLLECT_DIAGNOSTICSで60fps/GPU実行/カメラAPI待ちを照合。ミラーFXはCPU/PILの簡易表示で、LoL本体の画面にはかかりません。

完全版272/差分12、差分適用後274ソース一致、個人ファイル除外。Git報告はSOURCE_GIT_REPORT_JA.md、検証はVERIFICATION_v5.10.4.json、詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_v5104_JA.md。

## ローカルGit開発

既存フォルダを上書きしない新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5104-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v5104_Handoff
git clone --branch integration/v5.10.4 LoL_AutoCine_v5104_Handoff/handoff/LoL_AutoCine_v5.10.4_GPUFX_Capture60_all_branches.bundle LoL_AutoCine_v5104_Dev
cd LoL_AutoCine_v5104_Dev
git branch feature/gpu-shared-v5104 origin/feature/gpu-shared-v5104
git branch feature/ui-notebook-livefx-v5104 origin/feature/ui-notebook-livefx-v5104
git branch integration/v5.10.3-capture60 origin/integration/v5.10.3-capture60
git status --short
git branch --all
```

全48ブランチをorigin/*へ復元。このcloneのoriginはPC上のbundleです。担当/共有レビュー/統合ガードは上記開発文書のコマンドを使用。全旧版/旧ZIP/bundleを保存しています。
