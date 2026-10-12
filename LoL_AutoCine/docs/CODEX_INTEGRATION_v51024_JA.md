# v5.10.24-test RED相対中心補正・参照動画ZIP

受領ZIP CRC/パス/リンク/README/全patch/単体7テストとpatch内byte一致を確認。指定基準GitHub0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへ独立checkoutでapply --check/適用。受領v23から13パスだけ機能別レビューし、現行Codex v23 c048f3580bd2fe74954d7544b2737dc4f804511bへ統合。GPU・音声・録画/UIを旧累積patchで上書きしない。独立clone初回はhardlink制約で失敗、--no-hardlinksの別フォルダで確認した。原ZIPはGit外、原本archive/received-ui-v51024、code/READMEはhistory保存。新handoff/実機評価/CI/Release記述は受領側資料でCodex実測ではない。

RED auto通常thirdとFPSだけ、相対位置offsetへ向くatan2(-dx,-dz)と俯角atan2(dy,hypot(dx,dz))（14〜72制限）、Z=0を適用。RED thirdの旧X+4補正を自動時のみ除く。FPS距離1.60・独立高さ、offset位置式は保持。side/modeに限定した私有flag、CameraPlanとTemplate・_setup_clip ABI、TargetLock/cache/stable回転/seek/reset/safe top/ディレクターgainは維持。手動0/180は幾何flag無効、手動thirdは前回X+4を保持。旧direct planはopt-inなしで旧式。RED2/4/5と全BLUEの位置/回転を前版保存ソースから採った12ケース・各3時点のgoldenで比較。QA poseにflagと幾何回転を記録し、dynamicVERSIONは保持。実LoL Euler軸や主役中心・壁の遮蔽の改善を数式だけで断定しない。

動画ZIPを直接入力可能。元ZIPは不変、動画拡張子のみ120本・各1GB・合計4GBを展開前に検査、1MB chunk・実byte上限付きで一時フォルダへ保存。../・Windows drive/UNC・日本語・重複名も連番safe nameへ平坦化、archive member pathでextractしない。CRC/壊れたZIP/暗号化/非対応圧縮は理由を出し、上限/破損は比較出力開始前に失敗。一時展開はfinallyで掃除。参照名対応reference_archive_names.jsonと6時点JPEG/JSONだけを結果ZIPへ入れ、元動画/元ZIPを二重ZIPにしない。メディア不正は従来の動画別errorsへ記録。静止画抽出はCPUで通常GPU動画加工の外。

pickerのexplicit parent/root.destroy、日本語stemの別出力、cancelは比較出力なし、.venv/venv/PATH python/py -3の実import検査、ASCII/UTF8/unbuffered・Python直後status・TEMP/diagnosticsログ保持。BATは動画/ZIP/フォルダdrag時に結果pathとExplorer。pickerはPython --open-outputで選択した実結果を表示・WindowsかつCI外の成功時だけExplorer、cancel/失敗では開かない。受領のOUTPUTがpickerで未設定の問題を補正。CLIは明示option時のみ開く。Windows BATの実候補選択/日本語CMD/Explorerは実機未確認。

GPU feature/gpu-cameraqa-v51024、UI feature/ui-cameraqa-v51024、統合 integration/v5.10.24、受領archive/received-ui-v51024。旧119先端/旧配布物/37PNGを保持、全123refs bundle。共有8blobをレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51024 --ui feature/ui-cameraqa-v51024 --integration integration/v5.10.24 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.24.json
python tools/check_text_encoding.py
```

ガードはcommit済み先端なのでstatusも確認。全22GPUFX/OpenCL/NVENC/60fps時刻・フレーム数/LoL Native Loopback・Helper/WGC/encoder policy・FXとencoder別診断/安全CPUfallback/LatestPreview/Tk主スレッド/ミラー/6空間・6キルQA/64KB・3秒plan/oneclickQA・complete cache・partial/二重押し/stop/7既知ログ各1MB rawtail/1MBstream・500MB直接ZIP・最終JSONを保持。GPU映像/音声/録画の本体byte不変。CPUゼロ/GPU速度を主張しない。過去native139/132の原因は未確定。テスト結果はhandoff/VERIFICATION_v5.10.24.json、Windows/NVIDIA/LoL実機は未確認、mainマージなし。
