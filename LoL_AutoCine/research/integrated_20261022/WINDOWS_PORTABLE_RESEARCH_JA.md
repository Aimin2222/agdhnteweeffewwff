# 他PC・Windows配布の調査

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 現状と方針

今回配布exeをビルド・起動していない。既存START.bat、音声helper構築経路、FFmpeg探索、設定保存を維持する。UI29のWebView2起動も別開発のため、研究側で置き換えない。

推奨は最初にone-folder portable版を別ビルド枝で検証し、成功後にinstallerを比較する。[PyInstaller公式](https://www.pyinstaller.org/en/stable/operating-mode.html)はPythonランタイムを含む配布と、OS/bit数に依存するビルド、動的import・追加データの手動指定を説明する。Python不要化は可能性の調査であり、本アプリの完成済み配布物ではない。

|要素|同梱/事前検査案|Windowsで必要な試験|
|---|---|---|
|Python/Tk/numpy/Pillow|固定版bundle、hidden imports|Python未導入・新規user・オフライン起動|
|FFmpeg/FFprobe|版/hash/ライセンス・filter構成一覧|NVENC実行とCPU代替、OpenCLは別probe|
|native audio helper|対象arch・必要runtime、ビルド入口維持|OS build/API対応、LoL PID限定・他アプリ音遮断|
|WGC/共有メモリ|bundle内のworkerを明示|最小化・再起動・複数monitor・権限差|
|WebView2|採用UIに必要ならruntime条件|未導入時の説明、既存起動経路の保持|
|素材|承認状態とhash manifest|652原寸一括ロードしない、欠落時にレビュー素材を代用しない|
|設定・project|ユーザー書込領域を分離|日本語/空白パス、read-only配置、長いパス|
|driver/GPU|機能probeを保存|NVIDIA旧/新、Intel/AMD、GPUなしCPU（対象範囲の提案）|
|画面|1366×768/1920×1080/125–200%DPI|数値欄・固定preview・ログ導線が隠れない|

## 起動診断案

ローカル起動→データ読取→書込権限/空容量→FFmpeg→encoder/FX→音声API/helper→LoL接続の順。LoL未起動はアプリ起動失敗にしない。依存downloadや管理者設定を無断実行する設計にはしない。

## 更新・削除・診断

アプリ版とプロジェクトschemaの移行を分離。更新前backupとrollbackを残し、アンインストールで映像・素材原本・projectを削除しない。診断は個人パス、ユーザー名、ローカル録画、アカウント識別子を公開Gitへ自動送信しない。収集対象と保持期間を表示し、共有用に匿名化した最小レポートを作る。ライセンス一覧とFFmpeg配布条件の確認もbuild工程に含める。
