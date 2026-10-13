# 5.10.27-test カメラ軸・モード独立性の修正候補

基準はCodex 5.10.26-testの単一QAボタン版 fa13295637e7c1e97c60c74f332430de707a96ae、fingerprint f9c229d7546fca11。UI担当の基準bec275dとは別の積み上げ。main/PR29/42/43へマージしない。

## 実機証拠と原因

20261013_153947と164710の全10カメラおよび各27 MP4をFFprobeで計測、FFmpeg -xerrorで全体をデコード。960x540、60fps nominal、H.264。最新4 ZIPは各30,000,000 bytes以下、CRC正常、別添resultsとアーカイブ内resultsが一致。実機評価はRED3/5良好、RED1近い、RED2反転、RED4地形裏、BLUE全般不適切。

回転計算が混在。良好RED FPSではX=水平回転、Y=俯角、Z=0。BLUE FPSは水平回転354度付近をYへ送り、RED2は水平回転をZへ送り約-192度ロール。RED4は対象への実際の視線と水平回転が約180度ずれていた。BLUEの他モードもX/Yが逆。前の対象のカメラ座標をシーク後の基準に混ぜると俯角の推定にも影響した。動画冒頭と約0.2秒後で構図が変わり、仮姿勢の検証後、録画開始後の最初のdirector POSTで最終姿勢に変わる経路も確認。

## 変更範囲

- BLUE全5種とRED2/4だけ、実際のselectionOffsetからX=atan2(-dx,-dz)、Y=atan2(dy,horizontal)、Z=0を計算。良好RED3/5の計算、位置、FOVは変更しない。共通target_center_rotationの数学は旧版と同じ。
- 10モードの方位/距離/俯角プロファイル、追加距離と視線方針を別キー・独立値に分離。戻り値と実行中キーフレームをコピー。キャッシュは対象/チーム/モード別。1モードの設定を変えて他の9モードが変わらない回帰を追加。
- 問題モードの基準は同じ対象・top/fps・ゼロoffset・有限座標・合理的な距離を確認。不一致は上限2回再取得。古い世界座標の再利用で成功扱いにしない。再取得できなければ理由を記録して安全俯瞰。
- RED1は自動サイドの距離倍率だけ8%増加。角度と手動サイドは維持。BLUE旧X=-2度の誤軸補正は修正対象のlive経路では適用せず、試験X=-4度を採用しない。旧SHOT_TUNING/直接CameraPlan呼び出しは互換性のため保持。
- 録画・音声開始前に問題モードとRED1の最終offset/rotation/FOV/対象/attachmentをAPIで確認。最大3回確認、反映が確認できない場合中止。CameraQA resultsにinitial_pose_checksを保存。
- directorの平滑化/遅いAPI向け制限後、実際に送信するoffsetから同時に視線を再計算。yawの360度境界も連続化。

legacy_app.py、GPU Full/22FX、録画器、60fps入力、LoL専用音声、カメラクロック、ミラー、通常出力、設定形式を旧版で上書きしない。開発用QAボタンは1つのまま、送信用のみ540p/60fps/各30MB以下、通常1080p録画は変更しない。完成版では開発QA入口/圧縮アダプターを削除する指示を保持。

## 設計上の限界と確認

対象中心にレンズを向ける幾何とモード独立性は検証可能だが、地形の遮蔽、敵の見切れ、ゲームAPIの挙動はWindows同一シーンで再撮影が必要。安全俯瞰は撮影成功/希望構図の合格ではない。自動QAの単色警告は人間レビュー用で、被写体認識や空の証明ではない。CPU/GPU全経路の改善を今回のカメラ修正で宣言しない。受領診断にはprogram_opencl不足が残り、NVENC成功とGPU FX成功を区別する。

tests/red35_v51026_golden.jsonは匿名の入力を旧fa13295の_setup_clipで計算した固定数値。RED3/5の6条件・5時刻でoffset/rotation/FOV/speedを完全一致検証。全10モード、stale座標、Zロール、低速API、初回姿勢未反映時の録画/音声非開始を追加検証。

共有core/camera.pyとcore/jobs.pyは今回のGPU/カメラ担当ブランチのみで変更し、CODEX_SHARED_API_REVIEW_v5.10.27.jsonで実際のblobを固定。UI側は版検証の期待値更新のみ。既存の共有API signaturesと通常書き出し経路を保持。チェックはcheck_parallel_integration.pyを用いる。

ローカル全体テストはUIモジュール別プロセスで全収集件数の実行を確認する。既存の共有Tkプロセス終了時のnative crash原因は未解決、GC無効化/テスト除外は行わない。詳細件数/実コミット/配布SHAはhandoff/VERIFICATIONとSOURCE_GIT_REPORTに保存する。
