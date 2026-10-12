# v5.10.20-test モード別カメラ・色微調整・参照動画シート

受領ZIPのCRC/パス/リンクと全差分・READMEを確認。指定GitHub基準0e8e8f65362fd10a3ab9509c3fcbb4580b72691dに独立checkoutでgit apply --check/適用。添付の単体8テストはpatch内とバイト一致。受領v19との差分10パスを現行Codex v19 26c90ed8236c3341d05327c55000eb1b85666213へ機能別統合。受領資料のスクリーンショット・ユーザー目視・良好モード・Release記述は受領側の説明で、Codexの実機確認やRelease作成ではない。原ZIPはGit外、原コードをarchive/received-ui-v51020とhistoryへ保存。

CameraPlanとattach_to_player/_setup_clipの署名・位置引数・フィールドを維持。校正キーを(selection, team, style)に分割。受領の分割だけではCodexのstable rotationが(selection, axis)共有のままなので、こちらも(selection, team, style, axis)へ分割。自モードの安定回転は再校正をまたいで保持、別チーム・別モードからの復元を防止。match変更/個人リセットで全関連キーを消す従来動作は保持。校正成功判定・安全俯瞰fallback・TargetLock・先週のforced Y/+1/通常pitch metadataは変更しない。

ライブsetupでだけ受領補正を有効化。BLUE通常thirdは距離1.26、BLUE third/third_cinema/Lolnamはgeo look方向を使用、FPSはBLUE0.54・RED0.89距離補正と向き補正、auto RED通常thirdのみheading+8。REDシネマとBLUE geoの計算式を維持。旧direct CameraPlanはフラグなしの従来式。手動0/180度・scene keyframe・FOV・Orbit演出と共通録画は保持。補正は受領候補で、構図改善/遮蔽物除去/対象の実機成功は未確認。

かんたん色微調整をチェックの直下にpack、表示後idleで既存scrollへ移動。OFFでも共有色設定値は保持。詳細/かんたんテンプレート、A/B、図鑑、ミラー応答改善とDOFを保持。

付属QA planの従来切替比較をcut/flash/darkの3種に絞る。全10種の通常編集機能や引数planなしの旧QA APIは削除しない。6 GPU空間切替と6 GPUキル登場、RED/BLUE別確認MP4、3時点画像は維持。remote JSON参照を今回の実在するCodex配布ブランチへ変更、データ専用/64KB/3秒/既知操作制限/offline fallbackを保持。

参照動画フォルダをMAKE_REFERENCE_SHEETS.batへドラッグすると各動画6時点のJPEGとJSONをローカルZIPへ。元動画は変更せず外部送信なし。空フォルダも空の有効JSON/ZIPを生成するCodex補正を追加。これは任意の静止比較ツール（CPU FFmpeg抽出/Pillow）で通常GPUエンコード経路に入れない。GPUエフェクト/NVENCとは別の参考処理、AI主役判定ではない。

GPU feature/gpu-cameraqa-v51020、UI feature/ui-cameraqa-v51020、統合 integration/v5.10.20、受領 archive/received-ui-v51020。旧103先端を保持し全107refs bundle。共有8blobを固定レビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51020 --ui feature/ui-cameraqa-v51020 --integration integration/v5.10.20 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.20.json
```

statusも別途確認。mainへマージしない。GPU Full全22FX/60fps時刻・LoL専用音声/WGC/Native Helper・37PNG・GPU spatialQA/encoder_policy/診断/CPU fallback・500MB直接ZIP/1MBstream/最終JSON一致を保持。前回capture終了テスト同期修正も保持。今回変更していないGPU kernelの性能改善は主張しない。CPU制御・音声・I/O・近似ミラーは残る。検証用CPU PoCLは物理GPUではない。過去Linux native139/132は原因未確定、成功したテストだけで恒久修正と扱わない。検証結果はhandoff/VERIFICATION_v5.10.20.json。
