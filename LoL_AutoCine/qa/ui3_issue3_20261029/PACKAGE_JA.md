# Windows BAT試験用ZIP（2026-10-29）

- ソースコミット: `776045a3336529369318d6ef380d6a8e77d8c1a1`（PR #55、Draft）。
- ファイル: `builds/ui3-issue3-20261029-776045a/LoL_AutoCine_UI3_Trial_BAT.zip`（ローカル配布物。サイズのためGitHubへは含めない）。
- SHA-256: `7b380d41c6b49a274333b50923de634395034c6f13d1a5b26c9c308f5ee0e0e0`。
- 2223ファイル。`tools/build_ui3_bat_package.py` によるZIP生成・整合検査はPASS。
- 展開後 `START_AUTOCINE_UI3.bat` で起動する開発用試験版。既存のAutoCine本体・7案比較版・他PRは置き換えない。
- このZIPでの別PC起動、日本語/空白パス、実LoL、GPU/NVENC、音声、録画、MP4はNOT_RUN。完成配布版とは呼ばない。
