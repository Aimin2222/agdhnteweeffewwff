# B5 配布・異常系・復元
研究用状態機械へnone/disk_full/lol_disconnect/cancel/clip_failure/write_failureの6条件を注入。日本語・空白path内のjournalへ一時ファイル→os.replace→再読込。完了clipを再生成せず欠落分のみretry、fixture camera/HUD/TargetLockを復元するassertionは6/6PASS。ディスクを実際に満杯にしたりLoL通信/サービスを切断した試験ではない。実製品のerror handler成功と混同しない。

日本語BATはUTF-8/CRLFの文字列検査だけPASS。実行していない。Python無し別PC、EXE起動、FFmpeg/helper/WebView2同梱、管理者権限なし、実録画、CPU fallback、強制終了復旧はNOT_RUN。

Codex受入: クリーンなWindows標準ユーザー/日本語空白path/書込不可path/FFmpeg不在/音声helper不在/WebView2不在/空き容量不足/NVENC失敗/clip単位失敗/キャンセル/クラッシュ再開を個別にテスト。OSサービス/防御/ネットワーク設定を変更して通さない。中止はcancelledとして成功件数へ加算せず、部分出力とログの場所を返す。job journalにはschema/version/source hash/clip id/encoder実値/source-PTS範囲/一時出力hashを記録し、rename済みclipだけ完了扱い。

frozen実行時に外部python.exeの存在を仮定しない。[PyInstaller runtime information](https://pyinstaller.org/en/stable/runtime-information.html) の__file__/sys.executable規則に基づき同梱resourceを解決する。[WebView2 distribution](https://learn.microsoft.com/microsoft-edge/webview2/concepts/distribution) のEvergreen/Fixedを配布方針として選び、単にWebView2不在を「ネットワーク設定を変えれば直る」と扱わない。今回は導入/変更なし。
再実行b_fixtures.py。異常系E2Eはユーザー許可された隔離テスト環境が別途必要。
