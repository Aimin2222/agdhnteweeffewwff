# Flash と Zoom Blur の実描画比較
## Flash：F01–F04 / R07・R11
既存core/effects.pyのASTから_enable_expr / _build_video_effect_filtersを取り出してCPU FFmpegで実行。本体へ研究候補を代入していない。合成入力320×180に動く矩形＋固定灰色RGB80の50×40領域。閾値0で「同じ色変換経路を通るeq brightness=0」の同時刻灰色領域とRGBを比較した。raw入力との差を先行発光と誤認しない。

fps=30/60/60000÷1001、rate=1/0.5。Replay時刻 .1004、連続 .1004/.3002/.5004、同時 .1004/.1004、短間隔 .1004/.1084 の4系列。計24group×3revision=72描画。output event=replay time/rate、有理数で比較し、最初の可視frame=ceil(event×fps)。金線はそのCFRフレーム。

legacyは既存graphそのまま。V4は各eventのmax合成・因果gateだが時刻を小数3桁へ丸める。V5は各eventのgateをn>=ceil(exact event×fps)とし、減衰の原点は12桁表示。強度は既存同様0.15、振幅0.278。V5のmaxは同時kill数に比例して白くする加算ではない。

既存/V4は通常速度の12条件で最初のeventより前にRGB差分。スローの12条件ではこの最初のeventの丸め問題は今回再現しなかった。V5は全24で先行差分0、正の差分が出るframeも全24で期待値一致。単に常時消灯したPASSではない。例30fps event .1004秒では旧/V4がn3=.10000で光り、V5はn4=.13333で開始。

連続kill中の残光は前eventに由来し得るため、全体が次kill直前に暗いことは要求しない。FLASH_RESULTSの数値は最初のevent前の全体差分。FLASH_ISOLATED_EVENTSでは4固有時刻×fps3×rate2=24で各V5項を独立レンダーし、すべてのevent項の先行差分0・開始frame一致を追加確認。短間隔は同一CFRframeへ量子化されることがある。別victim同時killのイベントID保持は、本検査の画像max合成とは別の上流要件。

VFR・seek/pause・途中速度変更・長尺PTS精度・GPU版は未実施。V5のn gateをそのままVFRへ適用しない。製品へ採用するなら処理revisionを分ける。

## Zoom：Z01–Z05 / R08・R09
旧の1920×1080 scale/crop/tmix graphを実CPU処理。strength=.15/.5/.9、明暗、静止/移動=12group。18frames@30fps。動画とRGB統計は640×360提示サイズで取得、native解像度histogramではない。移動は背景矩形の移動で、色パッチ自体の完全な動体追従試験ではない。

旧 tmix weights 1 2 1 / scale=4 に対し、候補は自動正規化scale=0のみを変更。旧のRGB全成分>250の画素率は約99.9–100%、候補は全12で0%。旧はRGBパッチもすべて255、候補は弱では160/32/32等を保持。ただし強ズームの固定blue ROIはパッチ境界へ移り、背景混入で平均値が変化する。この値を色変換だけの誤りとは断定しない。完全な色管理・色域保持の合格ではない。

別の孤立tmix試験でn6に赤[160,32,32]→青[32,32,160]へhard cut。履歴連続ではn6=[128,32,64]、n7にも混合。segmentごとにfilterを再生成した候補はn6から[32,32,160]で一致。正規化だけでは切替残像を消せない。

これは時間混合＋ズームの比較。単一フレームを中心から複数方向/半径で標本化する空間radial blurの実装・検証ではない。GPU候補には正規化weight、float精度、同じalpha/color/range、履歴continuity ID、seek/cut flush、同一PTSでのCPU対照が必要。GPU実行、速度、VRAM、NVENC成功はこの段階ではNOT_RUN。
