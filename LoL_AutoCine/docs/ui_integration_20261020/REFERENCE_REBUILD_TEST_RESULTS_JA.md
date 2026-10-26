# 画像参照UI再制作：検証記録（2026-10-21）

この記録は、添付の14画面を参照して再制作した9案の**現段階**を対象とする。完成・正式合格の宣言ではない。

| 項目 | 結果 | 根拠・範囲 |
|---|---|---|
| 9案の起動・切替、共通状態 | 合格 | `test_reference_studio.py`。カメラ側、キル前秒数、Work枠ID、ミラーCanvasを確認。 |
| 既存UIの9案状態保持、Work素材カタログ | 合格 | `test_ui_layout_integration.py::test_all_nine_layouts_share_real_scene_and_camera_state` と `test_work_asset_catalog.py`、計5件。 |
| 1660×940・通常倍率、1660×940・125%、1366×768・125% | 表示確認 | 各9枚、計27枚の実Tk画面を`screenshots/reference_rebuild*`に保存。未接続プレビューは「UI参考静止画」と明記。 |
| WindowsポータブルEXE | 起動確認 | PyInstaller版の`--smoke-test`、WGCワーカーの`--help`、必要ファイル、ZIP CRCをビルド中に検査。通常起動後7秒間プロセスが継続した。 |
| LoL実リプレイ、BLUE/REDカメラ、TargetLock、GPU/NVENC、ゲーム音、60fps書き出し | 未検証 | 検証PCでLoLリプレイが起動していなかった。ユーザー用の順番は`TEST_GUIDE_JA.md`。 |
| 添付14画面との忠実度 | 未合格 | 画面構造と操作導線を近づけたが、文字サイズ、画像カード、ドック操作、独立した編集トラック等はモックと一致しない。実機テスト版を最終デザインと扱わない。 |

UI層は既存の`legacy_app.App`を1つ使い、カメラ計算、録画、GPU、音声の内部処理を変更していない。既存UIは`--legacy-ui`で開ける。GitHub ActionsのポータブルZIPはUI専用ブランチへのPushごとに生成する。ローカルZIPの`BUILD_INFO.json`にソースコミットを記録する。
