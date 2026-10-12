# v5.10.23-test 相対RED FPSピッチ・BLUE引き構図・参照動画選択

受領ZIPのCRC/パス/リンクと全README/差分/10新規テスト（param展開）を確認。指定GitHub0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへ独立checkoutでapply --check/適用、単体テストはpatch内とbyte一致。受領v22から12パス差分だけ現行Codex v22 a9e72ff4acc6081c0f80d16f4d306ffba1c7525aへ機能別統合。旧GPU/音声/録画/UIを丸ごと上書きしない。前回の有限値・手動向き・高さ・ディレクター・空フォルダ・診断ZIP修正を保持。原ZIPはGit外、原コードはarchive/received-ui-v51023とhistory。添付のWindows/画像評価/CI/MP4解析できない/Release記述は受領側の説明でCodex実測・Release作成ではない。

カメラ: RED通常thirdのZ+3を撤去してX+4の試験値、距離1.13保持。RED FPSは固定Y42とX-4/Y+4追加biasを除き、実相対offsetのatan2からpitch+3（18〜52に制限）を計算。fps_back1.60保持。offsetには自動pullbackと独立高さが含まれる。旧手動0/180と直接planのside_yaw fallbackは保持。RED2シネマ/4 Lolnam/5 geoの数値不変。BLUE第三者各モードの距離1.10/1.08/1.08/1.08、FPS back1.38に引き、追加角度は保持。これは受領の小幅補正候補、構図改善や実軸の正しさはWindows未確認。

校正/安定回転のチーム・モード分離、TargetLock/forced pitch metadata/safe top/seek/reset、ディレクターgain・旧None、TemplateとCameraPlan ABI、RED FPS高さ/手動headingは維持。数値によるpitch一致は主役/キルのAI自動認識ではない。BLUE7/9の距離も意図して変更、前回構図と比較して悪化時はモード単位で判断する。

参考BATは.venv→venv→PATH python→py -3を実import（PIL/imageio_ffmpeg）で検査。引数なしはMP4選択→キャンセル時フォルダ選択、全部キャンセルはPython側で出力しない。ZIPは展開を案内。Python statusを直後に保存してGOTO後の状態へ依存しない。PYTHONUNBUFFERED/UTF8、ASCII本体、TEMPとdiagnostics/reference_review_latest.logを保持。Python不足/入力不存在/ZIP指定も今回試行のログを残す。Windows cmdの候補選択・ログ・日本語パス実機は未確認。

Python helperの前回Path正規化/空フォルダJSON・ZIP/元動画不変/個別エラー記録を保持。pickerには明示parent、finallyでroot.destroy。引数なしCLIの自動出力先は実stem（日本語保持）を使い、ASCII化で別の日本語動画が同じreferenceフォルダになって上書きする候補を修正。BATドラッグ時と同じ命名。実日本語名60fps MP4から6時点JPEG/JSON/ZIP、pickerファイル/フォルダ/キャンセル、元動画不変・異なる出力先を確認。静止比較はCPU処理で通常GPUエンコード経路外、外部送信なし。

新しいreference_review_latest.logをQA_Supportの既知名へ追加。指定7ファイル末尾各1MBを元byteでコピー、ログの再エンコード/原本変更/symlink追加なし。中止時はsupport/ZIPを開始せず、失敗は録画保持。既知名1MB以下だけZIPへ、1MBstream/500MB上限/元動画・JSON・旧ZIP/別名再出力/最終JSON一致を維持。3時点は時間割合参考サンプル。前回未接続から1ワーカーのQA・complete cache再利用・partial/二重押し/stop/Tk snapshotも保持。

GPU feature/gpu-cameraqa-v51023、UI feature/ui-cameraqa-v51023、統合 integration/v5.10.23、受領 archive/received-ui-v51023。旧115先端/211旧配布物/37PNG保持、全119refs bundleと共有8blobレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51023 --ui feature/ui-cameraqa-v51023 --integration integration/v5.10.23 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.23.json
python tools/check_text_encoding.py
```

statusも確認。GPU Full22FX/OpenCL/NVENC/60fps時刻・フレーム数/LoL Native Loopback/Helper/WGC/encoder policy・FXとencoder別診断/安全CPUfallback/LatestPreview/Tk所有/ミラー応答/6空間・6キルQA/付属3比較と通常10演出/データJSON64KB・3秒は保持。effects・録画・音声本体はbyte不変、今回GPU性能改善やCPUゼロを主張しない。過去native139/132は原因未確定、成功を恒久修正と扱わない。Windows/LoL構図・BAT/NVIDIA速度は未確認。結果handoff/VERIFICATION_v5.10.23.json。mainへマージしない。
