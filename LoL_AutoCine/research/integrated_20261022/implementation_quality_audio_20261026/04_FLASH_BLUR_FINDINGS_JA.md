# Flash / Zoom Blur追加検証
## CPU Flash（新たな失敗を明示）
前候補V4 causal gateを30/60fps、3強度、単発/短間隔/重複/同frame/不規則/密集/小数丸めの42ケースで検査。174 assertion中12失敗、失敗caseは6。残りの通常36ケースは全条件成立。元コードは変更していない。
新発見：時刻0.5004/0.6004を小数3桁へ丸めると0.500/0.600になり、30/60fps両方でイベント前のframeへ効果が漏れた。V4のno-pre-first/no-futureがともに失敗。元の「未来pulseにstart gateを置けば十分」という説明には時刻量子化条件が不足していた。
V5研究probeは正確なoutput timeとfpsからceil(time*fps)を計算し、eqのnを開始条件にした。6追加probeで先行漏れ/未来影響の12条件が成立した。CFR前提の限定結果で、旧単発の全互換/可変速/VFR/GPU/LoLは未検証。正式採用せず別revisionへ隔離する。
式候補：B(n)=max_i[A_i*exp(−18*max(0,t−t_i))*I(n>=ceil(t_i*fps))]。Aは旧0.18+0.65*strengthの丸めも含め互換検査。重複IDは除去するが、別ID同時killは残す。add合成は白飛び増幅、latest上書きは順序依存となるため、この候補ではmaxを検討する。
強度が高い場合の白飛びは因果性とは別の問題で、candidate_white_fractionを保存した。強度capを勝手に既定にせず、ユーザー設定/legacy再現/新revisionの3つを明示する。future guardに合格しても美術的合格とはしない。

## Zoom Blur時間混合段
tmixのみをRGB 64×36の固定値32/96/180と移動stepで分離し、scale=4/0/0.25の12ケースを実行した。旧scale4では固定入力3種が全て255へ飽和。scale0/.25では固定値を誤差0で保持、step前へのエネルギー漏れなし。時間的残像は残る。
これはfull Zoom Blur/GPU/LoLの検証ではない。1920固定scale/crop、動的ズーム、色変換の影響は別。tmixのscaleは重み合計に対する係数で、weights 1/2/1の正規化と空間ズームの拡大率を混同しない。[FFmpeg公式tmix](https://ffmpeg.org/ffmpeg-filters.html#tmix)を参照。
新仕様条件：①定数輝度を維持②scene/seekで履歴flush③一時停止/単frame previewにも同じ履歴契約④範囲/transferを固定⑤flatと動きの両方を計測⑥旧projectはlegacy revisionを維持。正規化で真の空間radial blurを再現したとは報告しない。

生データ：FLASH_BOUNDARY_RESULTS.json / TMIX_NORMALIZATION_RESULTS.json。失敗は削除せず保存。

追加の非空検査：V5が常に発光ゼロで合格している可能性を除外するため、6probeで実際の初回発光frameを確認。30fps=frame16、60fps=frame31で期待値と一致し、2回目のevent frameにも発光がある。追加12条件成立。FLASH_V5_POSITIVE_ONSET_RESULTS.jsonとv5_onset_probe.pyを参照。
