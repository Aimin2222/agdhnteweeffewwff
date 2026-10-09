# LoL AutoCine v5.10.3をWindowsへ取得

GitHubの `codex/lol-autocine-v5103-handoff` ブランチで **Code → Download ZIP**。旧版は別フォルダへ保管し、新フォルダに展開して **LoL_AutoCine/START.bat** を起動してください。mainへのマージや環境PublishはWindows取得に不要です。

`handoff/LoL_AutoCine_v5.10.3_Windows_Full.zip` は起動用完全版。GitHubでファイルを開いて **Download raw file** でも取得できます。`Codex_MergeChanges.zip` はCodex保存版v5.10.1基準の差分で単体起動用ではありません。受領ZIPのv5.10.2基準パッチとは異なります。

円形DOF、中心X/Y・半径・境界の調整、日本語FX説明、2カラーと4プリセットを統合。円形モザイクは導入せず、旧JSONに残るcenter_mosaicだけを除去します。円形DOFは画面固定の2D CPU処理で、実深度/人物追跡やGPU高速化ではありません。旧上下DOFはbandとして残ります。形状指定のない旧JSONはcircleが既定値になります。

キル時刻補正、NVENC拒否時のCPU再試行、WGC初回準備、ホイール・一覧位置、三人称カメラとLoL専用音声を保持。受領の古いeffectsフルファイルで上書きしていません。Windows起動バッチとNative Helperを残しています。

pytest253件成功。実FFmpegで円形マスクの縦横比/内外の模様、4プリセット、1080p/60fps・合成音声とNVENC拒否→CPU再試行を確認。通常CPU出力と再試行のAACは完全一致、AV末尾差0秒。Windows/実LoL/Native録音/実GPU成功は未検証です。

240ソースファイル/Python86ファイル・全33ブランチをbundleに保存。完全版238/差分21ファイル、ハッシュ付き。個人設定・プロジェクト・録画・診断・画像キャッシュは含めません。旧ZIP/bundle/manifest/ハッシュを保持しています。

## Windowsでの確認

円形DOFをONにして内側の鮮明さと外側のぼかし、位置/半径変更を確認します。4プリセットを1クリップずつ試し、TargetLock/HUD/カラー/LoLだけの音声/60fps/同期を旧版と比較してください。手動再生なしの初回クリップ、ホイール、一覧チェック位置、複数クリップの順序・音ズレも確認します。

## ローカルGit開発

保存先がまだ存在しないことを確認して実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.10.3 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.10.3_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
git branch stable/v5.8.5 origin/stable/v5.8.5
git branch feature/gpu-engine origin/feature/gpu-engine
git branch feature/ui-circle-v5103 origin/feature/ui-circle-v5103
git branch integration/v5.10.1 origin/integration/v5.10.1
```

全33ブランチはorigin/*へ復元されます。UIはfeature/ui-circle-v5103、GPUはfeature/gpu-engine。上のgit branchコマンドは共有ガードとパッケージ作成の基準・担当ブランチをローカルへ作ります。以後UI開発では `git switch feature/ui-circle-v5103`、GPU開発では `git switch feature/gpu-engine` を使います。このcloneのoriginはPC上のbundleでGitHubではありません。

実変更一覧・Git状態はSOURCE_GIT_REPORT_JA.md、詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.10.3_JA.md、検証証跡はVERIFICATION_v5.10.3.jsonを参照してください。クラウド再セットアップ設定のPublishは将来のクラウド利用にのみ関係します。

GitHubから別フォルダへ240ファイル/全33ローカルref/HEADの一致を確認し、依存・構文・Tk・共有ガードと代表111テストが成功。installer再実行も追跡変更なし。新クラウドタスク起動の保証ではありません。再セットアップ設定は保存・読み戻し一致、他の設定を保持。将来反映時のみ環境設定で確認・保存後Publishしてください。
