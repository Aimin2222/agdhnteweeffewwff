# Python起動修正（2026-10-19）

## 今回の原因と修正

Native Audio Helperの確認後、`.venv`が存在しないとSTART.batは`py -3 app.py`を実行していた。クリーンインストール後はpyランチャーが存在せず、コード9009で停止した。SETUP_DEV_ENV.batもpyに依存していた。

START/SETUPは共通のtools/bootstrap_python.ps1を使う。既存のアプリ用.venv、指定Python、Codex付属Python、pyランチャー、PATH上の実体、通常インストール先を調べる。既定はPython 3.12 x64。WindowsAppsのストア用エイリアスを実体と誤認しない。PowerShell自体もPATHに依存せずWindows標準パスから起動する。

初回はアプリ内に.venvを作成し、検証済みrequirements-recovery-20261018.txtから依存をセットアップする。OS全体のPython設定や実行ポリシーは変更しない。Native Audio Helperの確認・構築フローは従来通り維持する。不完全な既存.venvを勝手に削除・上書きしない。

## 差し替え方法

1. 起動修正ZIPを展開する。
2. 展開したSTART.bat、SETUP_DEV_ENV.bat、requirements-recovery-20261018.txtとtoolsフォルダを、現在のSTART.batがある場所へコピーする。同名ファイルは上書きし、toolsは既存フォルダへ結合する。
3. START.batをダブルクリックする。初回はネット接続が必要な場合がある。`Setup is complete`またはアプリ画面が出るまで待つ。

Codex付属ランタイムがない別PCでは、Python 3.12 x64のインストールが必要になる場合がある。`AUTOCINE_PYTHON`で実体のpython.exeを明示指定することもできる。

## 検証

- 追加したWindows起動検査4件成功：pyなし、Python実体なしの案内、不完全.venv保持、空白入りパスでSTARTからテスト用子アプリの起動・終了コード維持・音声ヘルパーファイル不変。
- 新規.venvを実際に作成して固定依存を導入し、pip check成功。
- その新規環境から隔離コピーのAutoCine本体GUI起動・イベントループ・終了が成功。
- カメラ・画像素材・エンコード・音声キャプチャの実装は今回変更していない。実LoLの画角・録音の未確認状態も変わらない。
