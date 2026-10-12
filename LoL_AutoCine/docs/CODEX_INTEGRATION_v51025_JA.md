# v5.10.25-test BLUE6角度のみ・参考演出資料

受領ZIP CRC/パス/リンク・README/全patch/単体3テストを確認。指定GitHub0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへ独立checkoutでapply --check/適用し、添付単体テストはpatch内とbyte一致。受領v24から9パスの差分を現行Codex v24 eebfebda8a385895df805825bc56d84c7db4f762へ機能別統合。旧累積GPU/音声/録画/UIを上書きしない。原本archive/received-ui-v51025、原コード/READMEはhistory、ZIPはGit外。添付の実機画像/JSON/xMediaレビュー/コンテナ不調/CI・Release記述は受領側資料でCodex実測ではない。

映像動作はBLUE third（#6）angle X +3→-2（差-5度）のみ。距離1.10、位置/Orbit/keyframe/FOV/速度・他9モードは維持。BLUEのこのliveモードでXは俯角として使う受領候補、被写体を下へ移す狙いはWindows未確認。RED1/3幾何look-at・他RED/BLUE・手動0/180・FPS高さ・校正/stable cache分離・TargetLock/seek/reset/safe top・director gain・ABIは維持。実_setup_clipでチームORDER/BLUE、side auto/blue/red、keyframe/strength付きの旧+3版と比較し、各3時点でoffset/FOV/Y/Z一致・Xだけ-5を検証。前回golden12ケースはBLUE6のX差だけ明記し、他値の厳密比較を継続。新テスト初回と2回目はfixtureのt/timeとfov不足で各60成功/6失敗、既存time/yaw/zoom/fov形式へfixtureだけ修正。アプリのカメラ本体は変更していない。

qa/xmedia_reference_notes_v51025.jsonは静止画と受領側説明による4参考案の資料。通常template/QA/UIへ自動適用しない（コードの読込やUI選択ボタンは追加していない）。noirは全体低彩度近似、部分カラーの動的maskは未実装。29本の生MP4をCodexで新たに解析した結果ではない。既定エフェクト・vignette/barsを変更しない。既存GPU22FXは保持。

QA付属plan説明/IDを更新し、remoteは実在する今回CodexブランチのデータJSONだけ、64KB/3秒/schema/offlinefallback保持。camera_qaはdynamicVERSIONを保持し受領の固定version更新で戻さない。GPU・音声・録画・UI・core/camera.py/jobs.py本体byte不変。

担当GPU feature/gpu-cameraqa-v51025、UI feature/ui-cameraqa-v51025、統合 integration/v5.10.25。旧123先端・37PNG・旧配布物保持、全127refs bundle・共有8blobをレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51025 --ui feature/ui-cameraqa-v51025 --integration integration/v5.10.25 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.25.json
python tools/check_text_encoding.py
```

statusも確認。GPU Full22FX/OpenCL/NVENC/60fps時刻・frame数/LoL Native Loopback・Helper/WGC/encoderpolicy・実FXとencoder別診断/CPUfallback/LatestPreview/Tk所有/ミラー/6空間・6キルQA/oneclickQA・cache/partial・二重押し・stop/指定7ログ各1MB原byte/1MBstream・500MB直接ZIP・最終JSON/参照ZIP120本・各1GB・合計4GB・safe name・CRC・temp cleanup・Unicode/cancel・Explorerを保持。静止画はCPUで通常GPU動画経路外。CPUゼロ・物理GPU性能/構図改善は主張しない。過去native139/132原因未確定。結果handoff/VERIFICATION_v5.10.25.json、mainマージなし。
