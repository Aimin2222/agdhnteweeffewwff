# LoL AutoCine v5.7.4 - Auto Build Tools

## 変更内容

- Native LoL process-loopback audio helper のビルド前提を改善。
- MSVC `cl.exe` が無い場合、`BUILD_AUDIO_HELPER.bat` から Microsoft Visual Studio Build Tools の導入を自動試行。
- `winget` の Microsoft.VisualStudio.BuildTools パッケージを利用。
- `Desktop development with C++` に相当する `Microsoft.VisualStudio.Workload.VCTools` を要求。
- Visual Studio Build Tools のインストール後、`vswhere` でインストール先を検出し、`vcvars64.bat` を読み込んでその場でヘルパーをビルド。
- `START.bat` からもヘルパー未生成時に自動的にセットアップ処理を開始。

## 方針

最終的なアプリ化では、開発者向けのC++ビルド工程をユーザーに意識させない構成を目指す。
現段階ではネイティブProcess Loopbackヘルパーをソースから生成できるため、開発版ではBuild Tools自動セットアップ方式を採用する。

## 注意

Visual Studio Build Toolsの導入にはWindowsの管理者権限とUAC承認が必要になる場合がある。
また、インターネット接続と `winget` が利用可能であることが前提。
