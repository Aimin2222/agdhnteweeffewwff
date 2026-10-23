# キルフレーム・FX 全件品質審査 第2版

## 機械検査
ソース基準 fb03e0390805125fc063f4599af6c2541a653abf のカタログを固定。catalog SHA256: 80caca563edcb782d1faec95653f39bb503c851e706667cabcae8fe245a0c879。

|項目|対象/結果|解釈|
|---|---|---|
|元ファイル取得・SHA256・decode・寸法/モード照合|652 frame+35 FX、687/687一致|美術合格ではない|
|取得bytes|1,032,714,605|ローカル作業cache、GitHubへ重複保存しない|
|全く同じSHA256のgroup|0|類似テーマや見た目の重複は別の目視課題|
|透過/可視部分|全687件に存在|顔の穴や意匠の妥当性を保証しない|
|alpha≥128で端に接触|11 frame、FX0|solid-edge確認待ち|
|上記を除くalpha>8で端に接触|63 frame、FX0|soft-edge確認待ち|
|正式状態|frame approved1/review651、FX review35|変更なし|

全行の計測値・bbox・透明pixel下のRGB・flagsは [JSON](ASSET_FULL_QA_V2.json) と [CSV](ASSET_FULL_QA_V2.csv)。透明pixelのRGBは情報項目で、見た目の色漏れを自動確定しない。

## 実際に目視した範囲
89番号から各1候補と35FXの124点を7枚の白/暗背景contact sheetで確認。さらにsolid-edge11の全体縮小図と端の64×64 patch拡大を確認。重複を除いてframe93/652、未559。FX35/35サムネイル確認、未0。原寸全体の検査済み0、実LoL顔/背景合成0、6motion動画0。サムネイル確認を原寸品質承認と同一視しない。

淡いweak FXは白背景で輪郭が弱い。暗背景では発光/粒が見える。A/star_guardian/faerie_court/dawnbringer/winter_festival系を実ゲームの明暗双方で優先。丸型と角型の顔開口を保ち、一律円maskで削らない。装飾密度が高い38/46/66/73/74系は最終表示サイズで顔とHUDへの被りを確認。039の単色は意図の可能性があるため自動却下しない。083/a_simple_mainの既存静止承認は他候補・motionへ拡張しない。

## solid-edge11の拡大確認
004/dragon_world_frame、011/strong_03、016/strong_02、029/weak_02、032/main、065/strong_02、065/strong_03、068/main、071/strong_01、081/main、084/shurima_variant_1。

端のsolid pixelは1〜24個だが、alpha>8・4近傍の連結成分は全て10,000pixelを超えた（打ち切り計数10001/10002は総面積ではない）。孤立した1pixelゴミとは言えない。装飾先端/花/房/発光が端に届く形を観察したが、原本比較なしで「欠落した平面」を確定できない。縮小や切り直しは行わない。[拡大資料](ASSET_EDGE_DETAILS_V2.jpg)・[個別所見](ASSET_EDGE_DETAILS_V2.json)。

## 残件と順序
1. P1：approved静止1件の回帰基準を保持し、solid-edge11件を原本とmargin比較。承認済みでも動作は未承認。
2. P2：soft-edge63件の余白、35FXの実LoL明暗背景・顔・文字との合成、淡色/高密度themeを確認。
3. P3：まだ未目視の559 frameを番号/theme/intensity別に埋める。93件も原寸/最終縮小で再審査。
4. 全687件のうち適用される素材について6motionと動画時間軸の審査。静止PNGのalpha検査だけでpop/slideの見切れを判断しない。

全687件の優先順位・thumb確認有無・正式状態を [残件queue](ASSET_REMAINING_QUEUE_V2.json) に収録。合否を変更するqueueではない。
