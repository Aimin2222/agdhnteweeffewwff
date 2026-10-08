# v5.9.6 共有APIレビュー

受領パッチ全体の適用検査は成功。UIはfeature/ui-hud-batch-v596、共有jobsの
変更はfeature/gpu-engineへ分けて保存する。前回UI表示修正を維持し、全ZIP上書きは行わない。
VERSION/jobsの受領基準SHA256は一致。legacy_appの不一致は前回の3行表示修正によるもの。

## 共有変更

core/jobs.pyのrun_auto_editでHUDモードの説明文字列と開始ログを追加し、
実装と一致しない古いHUDコメントを修正する。関数署名、録画、HUDフラグ送信・復元、
音声、mux、エフェクトとエンコードの実行経路を変更しない。
名前表示に関する未対応のReplay APIプロパティを送らない。

UIのhud_presetsは既存Template.hide_hud/keep_champion_barsへ3択を変換する。
hidden=(True,False)、health=(True,True)、full=(False,False)。通常HUDはゲームの状態を維持。
名前非表示そのものはLoL内の設定が必要と案内する。
一括適用はUIスレッドの未保存Shotを検証して既存SceneProject.put_manyへ渡す。
確認ダイアログでキャンセルでき、1回のUndoで対象全体を戻す。Tk値をworkerへ渡さない。

CameraPlan/Templateの末尾フィールドとキーなしFOV、TargetLock、250ms時計を維持。
camera.py/camera_clock.pyは前回共有レビューから同一なので、その承認オブジェクトを引き継ぐ。
新レビューJSONはこの3ファイルのmode/blobに限って承認し、後続の共有変更は再レビューする。

検証結果はCODEX_INTEGRATION_RESULTS_v5.9.6_JA.mdへ記録する。
Windows・実LoL・Native専用録音・GPUの実機成功は主張しない。
