# 自動動画品質検査の設計

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 既存の自己診断と追加する内容検査

[core/auto_qa.py:19](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/auto_qa.py#L19)は依存・FFmpeg列挙・合成・API等の検査。映像中の対象・時間・音声内容をすべて保証するものではない。以下は追加設計。検出と修復を分離し、unknownをpassに変換しない。

|検査|入力／方法案|誤検出・限界|修復案（自動適用前に記録）|負荷|
|---|---|---|---|---|
|黒画面|輝度率・継続時間、blackdetect|暗い場面/意図的fade|該当秒再録画候補。fade区間は別扱い|低|
|フリーズ・drop|capture frame_id時刻＋freezedetect|静止場面では画素一致が正常|fresh低下を診断、再取得・再録画|低〜中|
|対象画面外|対象追跡boxとconfidence|エフェクトや透明化で検出不能|信頼度低はunknown。topへ候補変更|高|
|左右逆転・ロック外れ|API side/style/pose＋対象画面位置|hflip演出、追従中の向き|一律軸反転を禁止し審査へ|中〜高|
|過回転・過zoom|yaw/FOV/距離の速度・加速度、被写体サイズ|急なダッシュは正常の可能性|キー値を制約し再プレビュー|低〜中|
|遮蔽・地中|対象可視率＋画像サンプル|depthがないので厳密3D遮蔽判定不可|広角候補を提示、低confidenceは人審査|高|
|AV同期|同一時計の開始差、既知cueの音・画相関|音のないkill、BGMで曖昧|開始offset修正案、全体のstretchは勝手にしない|中|
|無音・音割れ|astats/silencedetect、stream有無|静かな区間は正常、無音バイト検査とは別|ゲーム音必須なら失敗、BGMだけを代替しない|低|
|過露出・連続flash|高輝度画素率と変動・event窓|ゲーム本来のスキル発光|FX強度減衰案。健康安全の適合認証とは扱わない|低〜中|
|合成ずれ・切れ|素材box/alpha bounds、icon ID対応|透明な余白は正常|承認portrait boxへ戻し、原本は変更しない|低|
|不自然なcut|シーン境界とevent余白、画面差分|意図したhardcut|区間を延長、重複イベントを統合|中|
|色崩れ・モノクロ|入力出力の色統計・参照chart|意図的grade、暗い場面|FXoff基準と比較、原因経路を隔離|低〜中|

参考：[FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html)には黒・静止・無音・音量統計の基礎検出がある。人物の正しい同定やゲーム音の意味を保証する機能ではない。

## 結果schema案

`clip_id, input_hash, template_hash, patch, actual_encoder, actual_fx_path, metric, unit, interval_video_s, replay_s, threshold_version, status(pass/warn/fail/unknown), confidence, evidence, suggested_action`。再検査しても旧結果を上書きせずrun_idを付ける。閾値はscene typeごとに版管理。

## 導入と合格条件

最初は黒/stream/音声長/fresh比など説明可能な検査から。正常・意図的暗転・静止・バグ入りを各20例以上収集し、clip単位と時間窓単位のprecision/recallを別算出する（必要標本数の設計案）。テストと閾値調整用映像は分離。誤検知で正常クリップを無限再試行しない。再録画は最大1回等の上限と理由を明示し、人が元映像へ戻せる。機械合格を芸術品質合格と同一視しない。
