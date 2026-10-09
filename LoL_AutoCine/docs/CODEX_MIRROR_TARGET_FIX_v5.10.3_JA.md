# v5.10.3 GPUFX MirrorFix

## 診断で確認した原因

前回CaptureFixのユーザー診断はPython 3.14.7 / windows-capture 2.0.1を明記している。14回の子プロセスがすべてWindowsCaptureのコンストラクターで `You can only specify one of: monitor_index, window_name, or window_hwnd` により終了(code=2)。前回追加したworkerがwindow_nameとwindow_hwndを両方指定していた実装上の不具合。ミラーもチェック/全検出/選択シーンも映像入力取得前に失敗し、GPU処理/FFmpegの開始はない。原診断/個人のパス/プレイヤー情報は配布しない。

「開始準備中」が続くのは、入力失敗をログにだけ記録し進捗ラベルを更新していなかったため。native開始が今回も35秒固まっていたとは判断しない。以前の診断のnative待機とは別の、明確な引数エラーである。

## 小さい変更と維持する接続仕様

- windows-captureがHWNDを受け付ければHWNDのみ、それ以外は既存LoLタイトルのみ。monitor_indexは明示None。minimum_update_intervalは受け付ける版だけ16msを指定。モニター/デスクトップ録画へのフォールバックは追加しない。
- 子が失敗したとき、最終例外をCaptureErrorへ含める。プロセス/共有メモリの境界・8秒の初フレーム制限・回収・BGRA/カラー・start/stop/latest/frame_count/runningは維持。
- ミラー開始/停止をdaemon workerへ移し、Tkアクセス/変数更新/キャンバス描画/ログ表示はUI pumpのみ。workerはApp/Tkを保持しない。開始中の再クリックは中止、古い結果は世代番号で除外、失敗はOFFへ戻し再試行できる。
- ミラーを録画が利用中の切替はログで案内して拒否。準備中に書き出した場合も明示エラーへ戻す。新旧キャプチャの同時開始を避ける。
- 映像入力準備の状態と、入力/作成エラーを進捗ラベルに反映し、失敗後「開始準備中」を残さない。

UIレイアウト/既存コントロール変数/タイムライン/カメラ操作は変更しない。GPU Bloom/DOF/OpenCL/FFmpeg/NVENC/CPUフォールバック・録画・時刻・TargetLock・LoL専用音声・Native Helper・START類・依存宣言は前回CaptureFixとバイト一致。core/capture.pyの公開APIは変更しない。共有2内部モジュールの変更blobを新しいレビューJSONへ記録し、旧承認も保持。コード差分はcore/capture_worker.py、core/capture_process.py、ui/mirror_capture.py、legacy_app.pyと2テスト。

## 開発ブランチと検査

GPU/キャプチャ側: feature/capture-targetfix-v5103。
UI操作側: feature/ui-mirror-targetfix-v5103。
統合: integration/v5.10.3-mirrorfix。
元feature/gpu-engine/feature/ui-dispatch-hangfix-v5103と全旧ブランチを残す。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/capture-targetfix-v5103 --ui feature/ui-mirror-targetfix-v5103 --shared-review docs/CODEX_SHARED_API_REVIEW_MIRROR_v5.10.3.json --integration integration/v5.10.3-mirrorfix
.venv/bin/python -m compileall -q app.py legacy_app.py ui_phase1_prototype.py core ui tests tools
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
```

全pytest283件成功（失敗/skipなし）。従来278に、旧window_name版・子の例外表示・実Tkミラー待機/中止/旧結果の無効化/再試行・checked入力失敗の表示の5件を追加。既存all入力失敗のテストもラベル検査を追加。実サブプロセスと共有メモリ、実Tkは利用するがnative Windowsキャプチャは合成である。

公式PyPIのSHA256照合済み1.4.4/1.5.0/2.0.0/2.0.1のPythonラッパーを使い、nativeコンストラクターの「対象は1個」の検証を代替して、新workerの引数適合を確認。旧workerでは2.0.1の同じ拒否を再現。ただし実Windows/WGC/GPU成功の証拠ではない。Linux上の環境で実GPU/LoL/Windowsは未検証、性能向上を断言しない。

## Windowsで確認

取得用の新Draft PRブランチcodex/lol-autocine-v5103-mirrorfix-handoffでCode → Download ZIP。旧フォルダと分けて展開し、LoL_AutoCine/START_GPU.batを実行。GitHubのhandoffの完全版ZIPのDownload raw fileも使用できる。mainへのマージ・クラウド環境Publishは不要。

1. LoLリプレイを表示し、最小化を解除。ミラーONで実映像表示、OFFで停止、再ONで再表示を確認。
2. 開始準備中でも他のUI操作ができ、再クリックでOFFにできることを確認。
3. チェック1シーン→2シーンを作成。入力取得後録画へ進むかを確認。
4. 失敗すれば準備中のままにならず具体的エラーになるかを確認。COLLECT_DIAGNOSTICS.batで新しい診断ZIPを採取。
5. 書き出し開始後に色/LoLだけ音声/同期/対象追従/fps/Bloom/DOFを再確認。effects JSONのgpu_effects_confirmed、pipeline.gpu_blur_effectsとencoder=h264_nvencを別々に確認し、GPU使用率だけで判断しない。

配布名GPUFX_MirrorFix、VERSION番号5.10.3を維持。完全版/前回CaptureFixからの差分/全ブランチbundle/ハッシュを保存し、全旧版も残す。差分はtools/package_v5103_mirrorfix.pyで生成する。後続UI ZIP統合でも担当検査と正確な共有blob検査を行う。
