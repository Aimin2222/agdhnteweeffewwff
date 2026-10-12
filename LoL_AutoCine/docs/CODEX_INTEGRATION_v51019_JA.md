# v5.10.19-test カメラ補正候補・共有テンプレート・GPU空間切替QA

受領ZIPのCRC/パス/リンクを確認、README・全差分・8追加テストを読んだ。指定GitHub基準0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへのapply --check/適用を別checkoutで確認。受領v18との差分16パスだけを現行Codex v18 f8ee3c1d7c099a99fa2383b42af74255f47b5726へ機能別統合。原ZIPはGit外、コード/READMEをhistoryへ保存。添付のWindows症状・映像評価・Releases配布記述は受領側資料で、Codexの実機確認やRelease作成ではない。

カメラ: 通常thirdとRED geo_aimのaxis safetyを受領仕様で追加し、yaw=X/pitch=Y/Z=0。初期回転を強制する場合はrigのpitch_axis/sign/complementもY/+1/通常へ一致させ、旧stable rotationで補正が取り消されないよう調整。他モードの校正後stable cache/resetは保持。通常thirdの古いtop基準（水平距離>4500）を除外してcached hまたは受領の後方方向へ戻す。RED third_cinema/Lolnamの寄りすぎとOrbitを制限、BLUE geoの従来式を保持。これは受領の補正候補で、画角/軸/主役追従の改善はWindows未確認。カメラ全体の作り直しはしない。

初期Templateと先頭プリセットは無加工カラー、vignette/grain/bloom=0・cut。ユーザーが既存プリセット/効果を選ぶ操作は保持。ネオン/アイス/金プリセットを受領値へ調整。テンプレート選択とA/B図鑑をかんたん編集へ移し、詳細カラーにも同じvar_tplを使用。かんたん色微調整はチェックON時だけ4項目を表示、OFFでも値保持。既存ミラー・DOF・スキャン・図鑑スクロール・出力操作を保持。

QA: RED/BLUE別フォルダと片側ごとの確認MP4を既存素材から作る。切替は両チームのthird_cinema素材を優先。従来10演出/6キル登場に加え、実2素材の空間切替6種（fade/wipeleft/slideright/circleopen/pixelize/smoothup）をQAだけへ追加。通常モンタージュを置換せず、空間確認動画だけ無音。受領CPU/libx264固定を新OpenCL helperへ接続し、選択encoder_policy/実FX経路/実encoder/fallbackを記録。GPU不可/失敗/timeoutは同2素材でCPU xfade。RGB入出力の境界以外にCPU pixel処理を足さず、延長はGPU frame clone＋明示フレーム数、60fps/長さを固定。

比較表は実MP4の前/中/後3時点をRED/BLUEと切替ごとに表示。短い素材でも終端外を読まない。輝度/画素差分は参考値で、主役/キル/水平線のAI自動合格判定ではない。1MBずつstreamする500MB直接ZIP、元MP4/JSON/既存ZIP保持、最終JSON一致、symlink除外、データ専用JSON/64KB/3秒fallback、前回GPU確認動画の60fps/元音声copy/encoder_policyを維持。中止で次ケース/追加比較/ZIPを開始しない。

GPU feature/gpu-cameraqa-v51019、UI feature/ui-cameraqa-v51019、統合 integration/v5.10.19、受領 archive/received-ui-v51019。旧99先端を保持し全103refs bundle。共有8blob固定レビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51019 --ui feature/ui-cameraqa-v51019 --integration integration/v5.10.19 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.19.json
```

ガードはコミット済み先端のみ、statusも確認。mainへマージしない。GPU Full全22FX/60fps時刻・LoL専用音声/WGC/Native Helper・37PNG/全旧aliasを保持。CPU静止画/音声/I/O/制御/近似ミラーは残る。NVENCとGPUエフェクトは別。検証用PoCLはCPU OpenCLであり物理GPU性能ではない。過去Linux native終了の原因は未確定、今回の成功だけで恒久修正と扱わない。結果はhandoff/VERIFICATION_v5.10.19.json。

比較表の3時点はクリップの時間割合で採取する参考サンプルで、実キル瞬間の自動特定ではありません。

復元先の既存capture終了テストで、error通知→native log取得→running=Falseの中間状態を観測する競合が1件発生。テストだけをrunning=Falseまで待つ条件へ修正し、error存在とlatest()が例外を伝播する検証を維持。録画/capture実装は変更せず、テスト除外/GC無効化もしない。
