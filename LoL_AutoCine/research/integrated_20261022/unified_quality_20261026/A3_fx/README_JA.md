# A3 Flash・Zoom・その他FXの追加実証
前回のCFR Flash V5 48限定試験、Zoom12比較、切替履歴試験を継承。今回同じ結果を新規本数に加算しない。SOURCE_COMPARISON_7によりqueried PR49のeffects等7ファイルは旧snapshotとAST一致を確認した。別の最新開発ブランチ全体の不具合を断定しない。

## Flash
新規はVFR風PTS/seek戻り/pause/速度変更の4列をFFmpeg filterへ与えたCPU実行。各event項をgte(t,exactTime)で因果gateしmax合成。最初のeventより前のRGB差分0、event後は実際に明るくなる。FLASH_NEW_CLOCK_RESULTS.jsonにgraph/PTS/平均値を保存。VFRコンテナのmux往復や実Replayシーク成功ではない。合成列が戻るseekはアプリの履歴管理の代替ではない。

明背景RGB210/175/120で強度.15/.5/.9の既存加算系はclipし得る。独立RGB倍率上限候補は254/maxRGBにgainを制限し3patchで255飽和0。ただし3強度が同じ上限に張り付くため強弱差が消える。flash_headroom_patch.pngも同じ色に見える。これを最適解/採用済みにしない。因果gateと露出/色管理は別の修正。暗いpixelへの効果、輝度perceptual差、HDR/range、連続時の上限はREVIEW。

## Zoom
正規化した時間tmixと、独立Pillow空間radial候補（5scale平均）を分離。移動する橙点に既知の座標中心を与える比較18frameとPNGを保存。空間固定中心では対象も二重にずれ、対象中心候補では対象中心を保ち周囲が伸びる。時間tmixは過去位置の二重像。これは追跡器実装やゲーム対象認識ではない。シーンcut/seekで履歴を破棄する条件は前回結果を継承。GPU kernel、正規化weights、linear/encoded色、alpha/range、frame continuity ID、中心座標のview変換を独立受入項目にする。

## その他と組合せ
8FX×.15/.5=16 CPUサンプル動画（18 native1920処理frame、提示640幅）を生成し全frame decode。motion_camera/glitch/focus_blur/camera_shake/vignette_fx/glint/chroma_leak/radial_blur。現在のradial_blur名のgraphはtmix時間混合で、本来の空間放射blurではない。

4組合せを実CPU描画: motion_camera+camera_shake、glitch+chroma_leak、focus_blur+glint、zoom_blur+flash。.15は研究開始値。最後はtmix正規化のみでFlashは旧gateのまま。全render PASS、品質REVIEW。起動込み単回elapsedを保存したが、GPU/実時間FPS/性能順位の証明にしない。移動系重ね過ぎ、時間blur+flash、色ずれ同士は自動presetの既定で重ねず、プレビューと上限を確認する提案。

対象保持/背景のみモノクロは今回照会したeffects/jobs内で該当mask処理を確認できず、実証NOT_RUN。全projectに絶対存在しないとは断定しない。必要条件は対象mask、境界保護、遅延/欠損時fallback、CPU/GPU同一色空間。素材35FXの画像審査と映像filterの実行可能性は別の集合。
再実行: fx_extended.py→fx_followup.py。本体へ統合しない。
