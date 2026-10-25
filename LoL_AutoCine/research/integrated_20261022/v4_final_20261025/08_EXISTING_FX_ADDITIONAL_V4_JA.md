# 既存FX追加検証
10FX×3sizeの初期30条件に加え、10×3強度(.15/.5/.9)×3sizeの90条件を1.2秒/36frames実処理。初期の保存10動画は18frames全decode。追加は出力raw36frame全取得。処理成功と画質合格を分けます。ハーネスd=.6構文失敗はd=0.6へ直し、失敗ログも保存。アプリ不具合には数えません。

Zoom Blurは元tmix weights1,2,1 scale4で人工映像がほぼ桃一色。without_tmixは空間標準偏差約122、tmix_only/constant_scaleは0、元はほぼ0。時間拡縮ではなく混合倍率を原因候補に絞れます。auto-normalize/scale.25候補は9条件で画像詳細が戻ることを比較。両候補は未採用、既存保存ID/見た目に無条件適用しません。FFmpegのscaleは重み付き和へ乗算する指定です。[公式tmix仕様](https://ffmpeg.org/ffmpeg-filters.html#tmix)。

focus_blur/vr_blur/sphere_blur/zoom_blurには1920×1080固定の中間/出力があり、1366/1280入力で寸法保持を破る条件をJSONに記録。最終jobでの再scale有無は追試が必要。

UI説明：radial_blur=時間方向残像（現行）、zoom_blur=ズーム揺動＋残像（旧版）、glint=輪郭強調＋明度/コントラスト、panel_wipe/stretch_wipe=黒から全面フェードイン、focus/VR/sphere=全体ぼかし、chroma_leak=キル窓RGBずれ、flash=全面明度pulse。真の放射状畳込み/局所glow/空間ワイプは新ID案として分ける。6名称を製品実装済みに書き換えない。
