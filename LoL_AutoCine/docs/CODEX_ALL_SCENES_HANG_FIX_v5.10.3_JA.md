# v5.10.3 一括作成・応答停止対策

ユーザーはGPU優先で「全検出シーンで作成」を押した直後に応答なし・異常終了したと報告。Windowsの診断ログや終了コードは未提供なので、今回の実機異常終了原因を断定しない。

## コードで確認・再現したUI停止経路

- 接続表示の_refresh_status_safeは別スレッドからstatusをキューへ送るだけだった。実際のapi.is_upはUIの_pump→_refresh_statusで実行していた。ReplayAPI._reqは録画・カメラ制御と同じRLock内でHTTP応答を待つため、録画側が使用中だとUIがロック待ちし、さらに通信タイムアウトまで画面操作を止め得る。
- GPU表示の_refresh_gpu_statusもUIでFFmpegエンコーダ一覧、フィルター一覧、OpenCL実行プローブと履歴読み込みを実行していた。通信以外にも、これらの応答待ちがUIを止め得る。NVENCエンコード自体の実行失敗とは別の問題。
- Linux/Tkで録画側を模した通信ロック保持0.6秒とGPU確認遅延0.6秒を与え、修正前のUIコールバックがそれぞれ0.661秒/0.640秒ブロックすることを実測した。実Windowsの異常終了を再現した試験ではない。

## 修正

接続・GPU表示の確認処理を別のdaemonスレッドへ移し、結果の文字列だけをキューへ送る。Tkのラベル・変数・タイマーはUIで扱う。確認中の再クリックは新しい確認スレッドを増やさず、接続確認タイマーは一本だけ維持。確認失敗でも状態を戻して再確認できる。終了時は接続タイマーを解除し、表示確認スレッドのjoinや通信待ちをしない。確認スレッドはApp/Tk変数への参照を保持せず、終了後のTkオブジェクト破棄もワーカーへ移さない。

一括作成はbusyを設定読み取り前に確認し、二重クリック時に再スナップショット/二重録画しない。Template/モンタージュ/シーン設定はUIで読み取って既存の_makeへ渡す。開始準備中の表示とALL_STAGEのclick/template/enqueue/worker/capture/renderログ、例外記録、35秒周期のスレッドスタック採取を追加。ワーカー終了・起動失敗ではスタック採取を解除。既存チェック済み作成の診断も維持する。

core以下・GPU処理・NVENC選択/CPUフォールバック・録画・カメラ・LoL専用音声・Native Helper・START.batはv5.10.3から変更しない。レイアウトやコントロール変数は変更しない。UI所有の小さな修正としてfeature/ui-dispatch-hangfix-v5103に保存し、integration/v5.10.3-hangfixへ統合。元integration/v5.10.3と旧版を残す。

## 検証

関連20テスト成功。全体pytest259件成功・失敗/skipなし（初回13.22秒。確認スレッドがApp/Tk変数を保持しないよう追加調整後も全259件を再検証）。新しい6ケースでは実Tkのイベント処理とワーカーを使い、API/GPU確認が待機中でも全5シーン・GPU方針・ゲーム音・モンタージュが既存レンダラ境界へ渡り、画面更新/中止/二重起動防止が動くことを検査。実ReplayAPIロック保持中のUI応答、確認失敗からの再試行、一本の接続タイマー、不正数値の安全な記録、映像入力失敗時のスタック採取解除も確認。待機を模した試験でありWindows Native Captureは実行していない。

依存/構文/空白/担当ガード、ZIP内容と差分適用、全ソースと旧Git履歴、GitHubからの復元の証跡はhandoff/VERIFICATION_v5.10.3_HangFix.jsonへ保存する。個人の設定・ログ・録画・音声・プロジェクトをGitや配布ZIPに含めない。

## Windowsでの確認

応答停止対策版は新しいGitHubブランチcodex/lol-autocine-v5103-hangfix-handoffでCode→Download ZIPし、旧版と別フォルダへ展開してLoL_AutoCine/START.batで起動。環境Publishは不要。元のv5.10.3と区別するため完全版の名前はLoL_AutoCine_v5.10.3_HangFix_Windows_Full.zip。番号5.10.3は維持する。

GPU優先で、まずチェック1シーン、次に「全検出シーン」を試し、開始準備中・進捗・中止の応答を確認。色・LoLだけの音声・TargetLock・同期・fpsを旧版と比較する。まだ異常終了する場合は、再起動する前に同じフォルダのCOLLECT_DIAGNOSTICS.batでローカルへ診断ZIPを作る。runtime.logのALL_STAGE、crash.log、fatal_python.log、FFmpeg診断、終了コードからWindows Capture/Native Audio/ドライバ経路を切り分ける。外部へ自動送信しない。
