FPSカメラで古いTop座標から空撮りになる可能性に対応し、対象相対poseへ変更。REDの位置と向きへ同じ192度を適用し、手動0/180度と高さ入力も保持。受領のチーム/モード別小補正を有限値・距離0.87〜1.15・角度±8度で制限。校正/stable rotationのチーム・モード分離とTargetLock/旧CameraPlan APIを保持。実構図改善はWindows未確認。

自動ディレクター強さと色パネルをチェック直下に展開。0%で既定Orbitが再生成される問題を補正し、UI snapshotをTemplate末尾の任意auto_director_strength（既定None）から実カメラへ接続。0/50/100%の接近量とOrbitを検証、旧位置引数/JSON/scene replace保持、不正値は開始前エラー。スタイル固有FOV/スロー/ローアングルは残る。参照BATは単体動画/フォルダ・入力別出力先・TEMPログ/pause。空入力ZIPと元動画保持のCodex補正も残す。

受領指定v15基準へ独立apply --check/適用し、受領v20との差分12パスを現行Codex v20へ選択統合。旧GPU22FX/60fps/LoL専用音声/録画/NVENC/diagnostics/fallback/500MBstream ZIP/37PNG/107refs/過去配布物保持、全111refs bundleと共有8blobレビュー。GPU描画本体は変更せず任意のカメラ値だけTemplateへ追加。添付の実機/Release記述は受領側資料として区別。自動動画アップロードなし。

検証: Linux/Xvfb全696成功（失敗/skip/除外なし、58.339秒）。実カメラ計算とUIワーカーsnapshot、不正強さ/角度、FPS手動向き/高さ、単体実60fps動画の6時点シートと元動画不変、旧GPU/UI/音声/ZIP回帰を確認。ZIP CRC/ソース一致/差分apply/個人ファイル除外/旧refsと配布物保持を検証。Windows/NVIDIA/LoL画角とBAT実行は未確認、過去native終了原因は未確定。

前回v5.10.20を比較先とするDraft PR。mainへマージしません。完全ZIP→Download raw file、別フォルダでSTART_GPU.bat。実機手順docs/WINDOWS_TEST_v51021_JA.md。
