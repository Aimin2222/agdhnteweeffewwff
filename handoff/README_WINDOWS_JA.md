# LoL AutoCine v5.9.3をWindowsへ取得する

このブランチはユーザーの引き渡し依頼による保存用ブランチです。
最新の前回取得用ブランチを基準にし、AutoCineを `LoL_AutoCine/` に更新しています。
前回ブランチに他の変更が追加されていたことを確認し、その変更も保持しています。
mainへマージする必要はありません。

## Gitを使わず取得する

GitHubでこのリポジトリの `codex/lol-autocine-v593-handoff` ブランチを開き、
**Code → Download ZIP** を選んでWindows PCへ展開してください。
その中の **LoL_AutoCineフォルダ** が完全なプロジェクトです。
従来のWindows起動バッチ・Native Audio Helper構築フローを含んでいます。
元の動作版は別フォルダに保管し、既存の `START.bat` で起動してください。
UIOnly ZIPだけを単体で起動する必要はありません。

## Git履歴と並行開発ブランチを復元する

WindowsにGitがある場合、PowerShellまたはGit Bashで実行できます。
以下の保存先フォルダが既にある場合は、別の名前を使ってください。

```sh
git clone --single-branch --branch codex/lol-autocine-v593-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.3 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.3_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

`LoL_AutoCine_Dev` が元のAutoCineのGit履歴を持つ開発用プロジェクトです。
13ブランチはclone後の `origin/*` にも復元され、必要な担当ブランチへ切り替えられます。
このcloneのoriginはPC上のbundleへのパスです。GitHubへの同期先が必要な場合は、
AutoCine用のリポジトリを別途指定してください。

ZIPを先に取得した場合も、展開フォルダ内の同じbundleからcloneできます。
GitHub保存用リポジトリをそのまま開発する場合は、作業ディレクトリが `LoL_AutoCine/` になる点に注意してください。

## 保存内容と確認結果

- ソース: `integration/v5.9.3` の追跡済み153ファイル。元ファイルとバイト単位で一致を確認。
- Git履歴: `LoL_AutoCine_v5.9.3_all_branches.bundle`。全13ブランチを復元してコミット一致を確認。
- `MANIFEST.json`: 元コミット、全ブランチのコミット、bundleのSHA256。
- `SOURCE_GIT_REPORT_JA.md`: 元プロジェクトのGit状態と元v5.8.5からの差分一覧。
- 個人設定、ログ、録画、音声、Python仮想環境は含めていません。
- 79テスト成功。合成映像・音声を使った60fpsの新旧経路の機能検証も成功。
- Windows・実LoL・GPU・Native Audio Helperの実機動作は未検証。
- GPUエフェクト処理本体は維持し、共有APIにはレビュー済みのキーフレーム接続・連続時刻補間・診断を追加しています。GPU高速化の実装はまだ行っていません。

詳細な結果と既知の未解決事項は `LoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.3_JA.md` を参照してください。

前回の取得用ブランチとPR #1/#2を保持し、新しいブランチにv5.9.3を保存します。
比較先は `codex/lol-autocine-v592-handoff` です。mainへはマージしません。
PR本文は `PULL_REQUEST_BODY_JA.md` に保存しています。

ウィンドウタイトルとブランド表示もv5.9.3です。
旧v5.9.0/v5.9.2のbundleとmanifestを保持しています。
チャットの生成ZIPリンクは使用しません。
