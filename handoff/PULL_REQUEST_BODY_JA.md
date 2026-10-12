受領v5.10.19の通常third/RED geoのaxis safety、stale top基準の除外、REDシネマ/Lolnamの接近制限を補正候補として統合。BLUE geoの従来式は保持し、強制Y pitchとrig metadataを一致させ旧stable cacheで補正が取り消されないようにする。Windows構図・主役・水平線の改善は未確認。

初期状態は無加工/vignette・grain・bloom0/cut。既存プリセット/効果選択は保持。かんたん/詳細でテンプレート選択を共有しA/B図鑑を維持、色微調整4項目はON時だけ表示して値を保持。

QAはRED/BLUE別確認MP4と3時点画像、従来10演出/6キル登場に加えて2素材の6空間切替を追加。CPU固定をOpenCL GPU＋選択encoder_policy＋診断＋CPU xfade fallbackへ接続。延長をhardware frame cloneと明示フレーム数で制御し60fpsを固定。空間確認だけ無音、通常のLoL音声と通常モンタージュは維持。再録画しない。前回500MB直接ZIP/1MBstream/最終JSON一致/元動画・既存ZIP保持/データ専用plan制限も保持。

受領指定v15GitHub基準へapply --check/適用を独立検証。受領v18との差分16パスを現行Codex v18へ選択統合し、GPUエンジン/音声/録画/37PNG/旧99ref/過去配布物を保持、全103refs bundle保存。共有8blobを固定レビュー。添付の実機/Release記述は受領側資料として区別。

検証: Linux/Xvfb全653成功52.61秒（失敗/skip/除外なし）。6空間OpenCL kernelをCPU PoCLで実行し各95フレーム/60fps/両端素材一致と模様付き中間画像の差を検証。2side reels/3時点4カメラ/5比較画像/直接ZIP/CRCも実動画で確認。物理NVIDIA/Windows/LoL速度・カメラ構図は未確認。過去Linux native終了は原因未確定、今回は全件で再発なし。完全ZIPと差分適用のソース一致・個人ファイル除外を確認。

前回v5.10.18を比較先とするDraft PR、mainへマージしません。完全ZIP→Download raw file、またはCode→Download ZIP。別フォルダでSTART_GPU.bat、実機手順はdocs/WINDOWS_TEST_v51019_JA.md。
