# 5.10.27-test 同一シーンで確認する手順

1. GitHubの新しいWindows_Full.zipをDownload raw fileで取得し、旧版とは別フォルダーへ展開。LoL_AutoCine/START_GPU.batで起動。旧設定/録画は削除しない。VERSION.txtは5.10.27-test。配布MANIFESTのfingerprintとresultsが一致すること。
2. 前回と同じリプレイを開き、同じ対象とキルイベントで「開発用：全カメラテスト・30MB ZIP」を1回押す。開発ボタンは1つ。スキャン済みなら再利用、終了後のBATは不要。全10カメラ完了か、中止/俯瞰理由を確認。
3. RED3 FPS、RED5 geo_aimを最初に比較。良かった構図・追従が変わっていないか。RED1は距離8%増加だけ。RED2は上下反転なし、RED4は地形裏でなく戦闘が映るか。
4. BLUE6〜10をPRE/KILL/POSTと全動画で確認。被写体と敵が見えるか、空/遠景だけにならないか、冒頭0〜0.5秒に構図が飛ばないか。こちらでは実機の修正後映像はまだ確認していない。
5. 同じイベントでRED→BLUE→REDと切り替え、再度撮影。1モードだけ設定を変更し、他の9モードの設定と構図に影響しないか。停止してミラー/カメラ状態が戻るかも確認。
6. 通常の短い書き出しを1080p/60fpsで1本、LoL音声ありで確認。長さ/速度/キル時刻と音声同期、GPU FX/NVENC状態を見る。GPUメーターのVideo Encodeと3D/Computeを区別する。開発送信ZIPの動画だけ960x540/60fps。
7. 最新results.json、全part ZIP(各30MB以下)、診断ZIPを送る。resultsのinitial_pose_checks、camera_pose、baseline_reads、camera_code_fingerprintをこちらで照合する。問題がある番号と「近い/見切れ/反転/空/停止」を添えてください。

前後比較は同じリプレイ・対象・イベントが必要。自動テスト成功だけでは構図の合格にしない。今回の修正後で良くなったことはこの実機テストで確定する。開発用QA機能は完成版で除去する。
