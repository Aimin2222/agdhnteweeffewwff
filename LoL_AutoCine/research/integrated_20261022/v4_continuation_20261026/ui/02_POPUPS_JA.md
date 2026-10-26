# ポップアップ・ダイアログ提案
Microsoftはモーダルを必要な中断に限定し、補助的情報は軽い表示にする設計を示す。本案では反復選択を右側ドロワー（レイアウトを再配置しpreviewに重ねない）とし、出力確認などにモーダルを使う。ドロワーはAutoCine向け独自案であり、MicrosoftのFlyoutそのものの実装ではない。
参考：[Dialogs and flyouts](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/dialogs-and-flyouts/)。

|画像ID|種類|内容と確定範囲|
|---|---|---|
|POP-details|右ドロワー|GPU・音声・HUD・テーマ。基本設定をプロジェクト値と分離|
|POP-camera|右ドロワー|制御方式、BLUE/RED、全10スタイルへの入口、slider/数値、TargetLock|
|POP-fx|右ドロワー|35FXの確認用状態、弱強/数値、6登場。使用選択は正式承認ではない|
|POP-frames|右ドロワー|652を承認状態・テーマで絞る図鑑。原本89/37バッジと混ぜない|
|POP-preview|右ドロワー|素材の拡大・明暗/チェッカー比較。元素材は不変|
|POP-scene|右ドロワー|選択sceneの時刻と前後秒、出力チェックと独立|
|POP-template|右ドロワー|6レシピを比較、変更項目表示、適用前はdraft|
|POP-output|確認モーダル|出力対象/本数/解像度/fps/音声/保存先。録画開始と明確に分離|
|POP-warning|警告モーダル|処理不能の原因と選び直す操作、設定保持、詳細ログID|
|POP-progress|非モーダル|進捗、計測済みETA、完了/警告/失敗、保存先。閉じると中止を分離|
|POP-help|右ドロワー|ミラー/演出確認/動画作成の意味と次の操作|
|POP-compare|比較モーダル|P1/P2/P3、元案7系統と正式選定の区別|

## 実装契約
- ×閉じる、Esc、キャンセルを明示。右側選択はdraftを編集し「適用」でcommit、閉じるで未確定だけ破棄。外側clickだけで変更確定しない。元の選択は保持。
- ドロワーは非モーダル：背景操作を禁止せず、フォーカスを閉じ込めない。ヘッダーとfooterを固定し中身のみscrollする製品実装を推奨。現在の試作ではドロワー全体scrollで、固定footerは未実装。
- モーダルは背景操作/scrollを抑止、初期focusを見出し/安全な選択へ。Tab/Shift+Tabを内部で循環し、Esc/閉じる後は起点へ戻す。危険操作にEnterが即時発火しない。
- 中止は確認後にjobへ送る。進捗窓を閉じる/テーマ変更/UI切替でjobやpreviewを停止しない。完了通知は非モーダルで再表示できる履歴を残す（履歴は新規提案）。
- 通知だけならトースト/InfoBar候補。長文エラーを自動消去しない。色に加えて成功✓/注意△/失敗×と文言、live regionを適切に使う。
- キーボード・フォーカスは[W3C Modal Dialog Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)を参考。HTML dialogの動作をWinUI/Tk/WebView製品で再検証する。

モック中のボタン/背景切替/保存先/適用は配置例が中心。全て動作する製品ではない。HTMLで確認したのは画面遷移、表示、slider/数値連動、theme値保持、fresh-openモーダルのEscとfocus復帰。ファイルpicker、素材全件検索、実ジョブ、正式承認操作は実装していない。
