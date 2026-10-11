接続とスキャンの別ボタンを右側①へ統合し、未接続でも接続→プレイヤー取得→試合全体スキャンを単一workerで進めます。完全スキャンのキャッシュとリプレイ世代、既存非同期ミラー/UIを保持。

DOF中央/右側とも円形と従来帯の設定を排他表示し、値は保持。高解像度縮小チェックのselected+active/disabledを優先して表示を維持。カメラ再選択/プレビューの校正キャッシュをリセット。core/camera.pyは消去関数追加のみで座標/pitch/TargetLock不変。キルフレーム名は簡潔にし全旧名alias/保存IDとPortraitCrashFixを保持。

開発用一括録画はBLUE/RED4カメラと全10切替（2キル以上の対象がいる時）を既存GPU・LoL専用音声経路で実行。UIでsnapshotしてworkerへ渡し、中止で次ケースを開始せず、所有入力をfinally解放。

検証: 最終Linux/Xvfb全585成功（失敗/skip/除外なし）、pip/構文/担当ガード。完全ZIP429ファイルとGit差分適用後431ソース一致。GPU/60fps/音声/37PNG不変、旧83ref先端/416既存ファイルを保持、全87refsをbundle保存。受領パッチの生ログ/cache/pycは含めず、6ソースのGit差分を再生成。受領側89成功記録とは区別。

初回全テスト中にネイティブ終了2回（原因未確定）。記録付き再実行は584成功・プレビューテスト1失敗で、固定プレイヤーを模擬データに補完して全件を再検証。テストは除外していません。Windows/NVIDIA/LoL実機と反転防止効果は未確認。

前回PortraitCrashFixを比較先とするDraft PR。mainにはマージしません。完全ZIP→Download raw file、またはCode→Download ZIPで取得し別フォルダへ展開してSTART_GPU.bat。Windowsテストはdocs/WINDOWS_TEST_SCANFIX_v51015_JA.md。

