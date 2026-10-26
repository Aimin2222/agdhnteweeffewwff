# A4 全登場時間のプレビュー/出力比較
前回72条件×5sample=360frameから、今回はFXoff/on×1/2/3段×6motion×3解像度=108条件、各30fpsのn0..29、全1秒3240frameへ拡張。1920×1080/1366×768/1280×720、event.10/.15/.20秒、duration.55、scale.85、opacity.7。No083/a_simple_main＋D_project＋公式アイコンを研究コピーで使用。

既存CPU FFmpeg書出しとPillow previewでbbox差>2pxを持つ条件84FAIL、残24はREVIEW。欠落bbox比較48sampleがあり、0px合格へ置換しない。画面外登場/時刻境界/終端/段割りなどが混ざるのでFULL_ANIMATION_RESULTSの各frameで判断する。黒背景の旧経路と青灰背景の候補の背景差自体を改善根拠にしない。6比較PNGの登場中には端での見切れが残る。演出として許すかは別判断。

共通RGBA候補は同じ準備済みoverlay列を独立FFmpeg/Pillow合成器へ渡し108/108条件RGB最大差0。共有rasterを消費する合成器の一致であり、独立した2つの配置計算が正しい証明、全素材対応、製品修正、圧縮MP4のpixel完全一致ではない。

floatの開始/終了境界とmicrosecond量子化の差108行も記録。今回表のn21は.15+.55の終了境界が主因。すべてを「開始時刻の不具合」とまとめない。時刻を共通有理数/整数tickで定義しintervalは[start,end)、start/end丸め規則を一度決め、FFmpeg文字列とpreviewで同じ値を使う。

Codexへ: layer_plan、row割当、activation、elapsed、motion transform、anchor、scale、mask、opacity、FX layer、clipを共通OverlayPlanにする。1080を単純縮小する修正だけでは登場中の不一致が残る（前回FAIL）。実viewport letterboxとDPIは最後の画面変換とし動画座標へ混ぜない。6motionの既存意味（popは横方向減衰）を無断変更しない。native Windows DPI/スクロール/実アプリ/実ゲームはNOT_RUN。
受入: 全frameで前後境界の出現ID集合一致、同じraw RGBAでRGB差<=2px値（候補fixtureは0）、bbox差<=2px、重畳differenceを保存。欠落bboxは時刻/画面外の理由を記録し別審査。動画H264は色変換/圧縮許容を別定義。再実行parity_full.py。
