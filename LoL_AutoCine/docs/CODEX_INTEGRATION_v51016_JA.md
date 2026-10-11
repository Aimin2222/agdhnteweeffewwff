# v5.10.16-test 統合契約と変更

今回受領ZIP内README・パッチ・9テストを確認。受領が指定するGitHub基準0e8e8f65362fd10a3ab9509c3fcbb4580b72691dに対し別checkoutでapply --checkと適用を確認した。現在の基準は前回Codex ScanFix e62be60d41fefd41dfc01568211c75bb3fd86ff6であり、古い基準からGPUファイルを上書きせず機能ごとに統合した。原ZIPはGit外attachmentsに保持。添付文書は参照資料であり、ユーザーの依頼と区別する。

- キル表示6登場モーションと保存項目を追加。Template末尾の既定instantで旧設定・位置引数を維持。受領CPU式を共通化しOpenCL合成にも実装、映像をCPU overlayへ戻さない。GPU診断へkill_icon_motionを記録。
- 三人称の非pitch軸だけ110度以上の急変を抑える。前回の成功回転を校正リセット後も保持し、リプレイ切替では消去。俯角/座標/TargetLockの式と手動向きは保持。共有core/camera.pyのblobをレビュー済み。
- RED4/BLUE4の実シーン録画QAをユーザー操作で開始。既存run_auto_edit/LoL専用音声/60fpsで順次8本録画。うち2本を全10切替に再利用し、新たなLoL録画を行わない。選択encoder_policyと実VERSIONを記録し、要求切替からfallbackした場合をresults.jsonへ失敗として記録。処理はworker、TkはUIスレッド。
- 中止は録画経路の既存stopへ渡す。切替エンコードは現在の1本を終えてから残りを中止する（実行中FFmpegの即時停止は今回の実装範囲外）。
- UIのモーション選択、DOF円/帯radio、スクロール速度とカメラ表示名を統合。前回ScanFixの接続/全体スキャン、画像Player互換、6状態チェック表示、非同期ミラーを維持。指定された11素材名だけ更新し全旧名aliasと37PNGを保持。

GPU担当feature/gpu-motion-v51016、UI担当feature/ui-motion-v51016、統合integration/v5.10.16。旧87ブランチを保持。受領原本archive/received-ui-v51016。担当検証はコミット済み先端のみ: 未保存statusも確認する。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-motion-v51016 --ui feature/ui-motion-v51016 --integration integration/v5.10.16 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.16.json
```

共有レビューはstable/v5.8.5からの8ファイルを正確なblobへ固定。後続差分があれば再レビュー。mainマージ禁止。旧配布物/個人設定/録画/プロジェクトを保持。

映像加工は既存GPU Full経路を保持。CPU制御・音声・I/O・LUT/静止画準備・Pillowミラープレビューは残る。NVENCの使用とGPUエフェクト実行は別。物理GPUのないクラウドでのPoCL試験はカーネルと時刻検証だけでありNVIDIA性能の証明ではない。Windows/LoL実機はユーザーのまとめて確認を待つ。

以前のScanFix全件実行で原因未確定のLinuxネイティブ終了2回があった。除外/GC無効化で隠さず記録付きで検証する。今回結果はhandoff/VERIFICATION_v5.10.16.jsonを参照。
