# v5.10.18-test QA計画・比較表・直接ZIP 統合

受領ZIPのCRC/パス/リンクを確認。README・全差分・8追加テストを読んだ。指定GitHub基準0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへのapply --check/適用を別checkoutで確認。受領v17との差分13パスを現行Codex v17 9b7eeee604db4dd910a7111fe6c24e7e0e1c5326へ機能別に統合。古いUI/GPU/音声/カメラを上書きせず、前回GPU確認動画/音声copy/encoder_policy/動的VERSION/一意フォルダ/校正後の安定回転を維持。添付資料は参照でありユーザーの依頼・Codex実測と区別する。

- Templateの新規既定gradeをdefault（無補正）へ変更し、初回UIも無補正で開始。ユーザーがテンプレート/色を選ぶ操作と旧保存IDは維持。Bloom等の別エフェクトは変更していないため「全加工OFF」ではない。
- 図鑑をrootのactive galleryとして追跡し、開いている間はメインパネルのwheelを止める。transient設定、close/destroyで参照とworkerを解放。前回のLatestPreview/snapshot/Tkスレッドの分離を維持。
- QA計画はローカルJSONと、ユーザーが開発QAを押したときworkerで取得するGitHub JSON。既知camera/transition/motion/100〜500MBのみ許可し、64KB上限/3秒timeout/失敗時付属計画へ戻す。ソースコードや指示を実行しない。取得先は今回のCodexブランチqa/test_plan.json。通常起動時には通信しない。
- 付属計画は従来4カメラ＋geo_aim実験を両サイドで実施（10本）。APIにplanを渡さない呼出しは従来8本。QA対象は実キルを優先、なければアシスト。geo_aimは選択した時だけ相対offsetから視線を計算、既存4カメラの式/軸/手動0・180度/RED184度/TargetLockは保持。geometry_validationは数値上の疑義を記録し、映像の上下反転や主役が映っていることを断定しない。実験視点のLoL Euler軸はWindows要検証。
- 10切替/6モーションは録画済み素材を再利用し、前回GPU合成/60fps/元音声copy/選択encoder_policyを維持。色/DOFの二重適用なし。比較表は実MP4の小さな静止画から作り、短い動画でも終端外を読まない。輝度/コントラスト/切替との差分は参考値。主役/キル/水平線をAIで認識する機能ではない。
- QA結果を最大500MBのZIPへ直接保存、ZIPをZIPへ入れない。大きな動画は1MB単位のstreamで番号付きpartへ分割し、結合手順を入れる。原動画/元JSON/既存ZIP/個人ファイルを消さず、repeat時は別名。symlink/外部パスを含めない。出力名を先に計画してJSONを更新するため、ZIP内results.jsonが最終結果と一致する。CPU制御/静止画処理/I/Oは残る。
- 中止後は次ケースを開始せず、比較表/ZIPの追加処理も開始しない。現在のFFmpeg1本終了後に停止する仕様を維持。

GPU feature/gpu-releaseqa-v51018、UI feature/ui-releaseqa-v51018、統合 integration/v5.10.18、受領 archive/received-ui-v51018。旧95先端/旧配布物を保持し全99refsをbundle保存。core/camera.py・jobs.pyの共有blobを更新レビュー、他6共有blobは保持。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-releaseqa-v51018 --ui feature/ui-releaseqa-v51018 --integration integration/v5.10.18 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.18.json
```

ガードはコミット済み先端なのでstatusも確認。mainへマージしない。既存GPUエンジン全22FX/60fps時刻・LoL録音・WGC/Native Helper・ミラー・ScanFix/PortraitFix・37PNG/全旧aliasを保持。NVENCとGPUエフェクトは別。Windows/LoL画作り・NVIDIA速度は未確認。前回Linux native終了の原因は未確定で、今回成功だけで恒久解決と扱わない。今回検証はhandoff/VERIFICATION_v5.10.18.json。
