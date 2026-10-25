# 35FX実合成
35×4形状×weak/strong×light/dark/complex=840組を実描画。各組に最大3段を配置。さらにFlash0.28と彩度0.75の診断合成840組。全35比較シートを目視。縮小タイル256×144なので元FXの全画素審査とは別です。V3原寸35確認を継承します。

動背景は35本、各1280×720/30fps/90frames。4形状を4象限に示し、前半weak、後半strong。全90frame decode35/35。弱0.40秒/強1.90秒の2時点シート全35を目視。人工HP線・名前・HUD・minimapとぶつかる配置を意図して可視化。実LoL映像ではありません。Riot公式static champion PNG（Yasuo/Jinx/Ahri/Zed、出典とhashはOFFICIAL_ICON_PROVENANCE）を使用。

観測：各組の左右顔は識別可能。強い交差光/縦装飾は3段の隣接行に合流しやすい。round083以外の肖像配置は暫定円fallbackで穴との不一致がある。Flash診断で明部の白wash/彩度減少。対策案はフレーム本体修正ではなく、検証済みportrait mask、最大3段間隔/安全領域、peak強度と表示時間、最後のkillだけclimaxという設定差分。全部新規提案、未採用。

全35の全時間を人手再生審査したとは記載しません。動画と比較画像を同梱し、実LoL HUD背景/全時間視認審査を残件にします。approved/review変更0。

追加：固定commitのリポジトリcamera_comparison_20261020.jpgからRED/BLUE各320×180の背景cropを取得し、960×540へ拡大。35×4形状×2強度×2参照背景=560合成を35シートにして全件目視。左右顔は見える一方、強Arcade/Dawn/Infernal等は段を縦につなぎ、背景の白beamとも競合。cropの低解像度/圧縮とHUD非表示のため、現在のLoL captureやHUD合格にはしません。offline mock_preview_offline.jpgも確認しましたが実captureの出典を確定できず、実LoL背景とは扱いません。参照出典/hashはFX_REPOSITORY_BACKGROUND_V4.json。
