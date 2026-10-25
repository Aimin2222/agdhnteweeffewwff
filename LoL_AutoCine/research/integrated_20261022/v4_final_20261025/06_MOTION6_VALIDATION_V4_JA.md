# 6motion検証
instant / slide_left / slide_right / slide_up / slide_down / popを保持。popは16*exp(-18t)*cos(28t)の横減衰振動で、拡大に変更しません。

全652×6×3size×30/60=23,472シナリオ、active layer 5,903,208サンプルを数式評価。5event、最大同時3。静止後端見切れ0条件、人工minimap bbox重なり10442条件。これはCPU export用固定幅384・step164の座標幾何です。mirrorの縮小スケーリングを再現した数値ではありません。

別に4形状×6motion×1920/1366/1280×30/60=144実際のmirror描画動画をencode/decode。全144で予定81/162frames一致。1080p60の24本を保存し、4時点シート24枚を目視。前/後は非表示、frameと左右portraitは同一overlayで動く。slideの画面外からの登場中の見切れは仕様で、静止中欠損とは別です。3非円形は仮portrait配置。

追加で同じ083をoriginal CPU export graphとmirrorで実描画。1080p可視bbox[1527,84,1866,200]が一致。1366ではexport[973,84,1312,200]対mirror[1086,60,1328,142]。1280ではexport[887,84,1226,200]対mirror[1018,56,1245,133]。変更前に出力の基準座標を決め、旧処理revisionを保持する必要があります。

全652×6を全pixel動画としてrenderした件数とは混同しません。GPU/CPU pixel差、実LoL/HUD、実際のvictim解決はNOT_RUN。144全decode成功は美術・LoL合格ではありません。
