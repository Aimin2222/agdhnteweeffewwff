# プレビューと書き出しの位置・RGBA比較
## 実行経路 / R10・R11
core/work_kill_assets.pyの既存with_work_badges（FFmpeg CPU出力）、render_preview_pair（Pillow CPUプレビュー）、layer_planを直接使用。原本・製品コードは変更せず、カタログと素材rootを研究コピーへメモリ上で向ける。frame083/a_simple_main、公式Yasuo/Jinxアイコン、D_project FXの有無、1/3段、6motion、3解像度=72条件。

30fpsでn3/6/9/12/18（.1/.2/.3/.4/.6秒）の5sample、計360の実RGBAを比較。全0.7秒の全フレーム比較ではない。全6motion=instant/slide_left/right/up/down/pop。既存popは横揺れであり拡大ではない。背景は同一の不透明黒へ合成しRGB support>8のbbox/IoU/MAEを測った。元PNG透過を保持してから合成するが、同一背景上RGB比較はalpha全画素同一の証明ではない。

比較シートはn9のCPU出力・CPUプレビュー・50%重畳・1920基準縮小候補・絶対差4倍。9枚のnative PNGを同梱（3解像度×3経路、FXあり3段instant）。数値全phaseはPOSITION_RESULTS.json、要約はPOSITION_SUMMARY.json。

## 結果
|出力|n9既存のbbox最大辺差（条件間範囲）|n9基準縮小候補|全5sampleの既存最大/候補最大|
|---|---|---|---|
|1920×1080|0–2px|0–2px|163 / 163px|
|1366×768|113–152px|0–1px|268 / 116px|
|1280×720|131–175px|0–1px|284 / 109px|

n9だけを見ると基準縮小でよく揃う。しかし登場途中では同じ1920でも差があり、単純縮小候補はFAIL。rowの割当・出現時刻・終了・motionの基準寸法を共通化する前に、最終画像だけ縮小しても解決しない。部分的に画面外の行がある場合のbboxは不安定なので全sampleの生データと画像を合わせて解釈する。

960×540@1、800×600@1.25、1024×576@1.5のletterbox/DPIは研究bitmapの写像。native Windowsの実DPI・GUI widgetの測定・ミラー取得ではない。実LoL画面、ネイティブDPI、GPU rendererはNOT_RUN。APIの更新中に他のCodex開発版を起動・変更していない。

## 安全な次の修正
TimeMap→共通イベント有効区間/row planner→基準座標の各レイヤー/motion→contain変換→最終pixel丸め、という共通プランを先に抽出する。再標本化filter/alpha型も一致させる。FFmpeg/Pillow双方の同じnとtに対する中間rectを保存する。bbox<=2pxだけで全画素や見た目を合格にせず、mask IoU・edge profile・RGB差と視認性を並べる。

注：n9は後発stackの登場途中を含む。全イベントが入場を終えたn18では、既存bbox差は1920=1px、1366=113–152px、1280=131–175px。候補は1920=1px、1366/1280=0px。この静止後の一致を登場全時間へ一般化しない。
