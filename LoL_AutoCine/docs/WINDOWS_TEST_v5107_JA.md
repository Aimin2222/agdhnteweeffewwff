# Windowsで今回確認すること

旧版を残したままv5.10.7完全版を別フォルダへ展開してください。START_GPU.batで起動し、前回と同じ設定・素材で比較します。GPU加工は前回診断16回すべて成功しています。

1. **設定エリア**: ミラーON、ライブFX ONで「カラー・エフェクト／書き出し」の3タブを切替え、色/強さ/DOFスライダーとスクロールを30秒ほど操作。操作への反応、固まりの有無、操作を止めた約0.4秒後にミラーの通常画質/頻度へ戻るかを確認。操作中のミラーは軽くするため一時的に約6fpsです。ライブFX OFFでも比較してください。
2. **GPUテスト**: アプリを閉じ、TEST_GPU_RENDER.batをダブルクリック。raw MP4選択画面で同じ録画を選びます。6ケースの進行、終了コード、最後の「続行するには何かキーを押してください」が残るかを確認。02_standard_gpuと03_standard_cpuの色・DOF・Bloom、04の日本語タイトル、05の白飛び、06の演出を比較（加工テスト自体は無音）。NVENC使用だけではGPUエフェクト成功を示しません。「GPU confirmed」またはRESULTS.jsonのgpu_effects_confirmedを確認します。失敗/選択キャンセルでもdiagnostics/gpu_test_startup_日時.jsonと.log、gpu_test_launcher.logに記録します。
3. **通常書き出し**: 1080p・60fpsで1シーンと2〜3シーンを書き出し、GPU加工、LoL音声/同期、三人称、ミラー復帰を確認。RED/BLUE側、キル＋アシスト→全編スキャン→全シーン作成、撃破アイコンのガラス斬撃/中央なしも確認。カメラ/音声はGPUテストの6ケースでは確認できません。

最後にCOLLECT_DIAGNOSTICS.batを実行してZIPを送ってください。ミラーの設定操作が重かったか、GPUテストの選択画面が出たか、終了コードも教えてください。ウィンドウが閉じても起動ログは残ります。Python自体が起動できない場合はgpu_test_launcher.logだけになります。

完全版はGitHubの取得用ブランチでCode → Download ZIP、またはhandoffのWindows_Full.zipをDownload raw fileで取得できます。mainマージやクラウド環境Publishは不要です。MergeChanges ZIPは前回GPU Full v5.10.6に対するGitパッチであり、受領UI ZIPだけを上書きするものではありません。
