# CPU Flash再現と互換候補
元_build_video_effect_filtersをASTで独立実行し、gray320×180/60fps/3秒で実測。8集合（single、two_short、two_long、three、dense、edges、empty、retimed）×3強度×旧/v2=48。旧empty helperのIndexError3件は直接呼出し再現で、通常jobの到達性とは別。残45decode成功。

旧式はenableに全eventを含める一方、指数減衰中心はevents[0][0]のみ。three強度.45ではgray255/127/127、v2は255/255/255。v2は振幅.25+.55kで旧.18+.65kと異なり、互換候補として却下。

v3は旧振幅を小数3桁で維持、旧窓を保持、各event中心のpulseの最大値を使用。emptyはno-op。8×3=24実測、single3強度で180frames各bit一致3/3。three強度.15は各event gray207（同梱v3比較画像）、強度.45では各event gray255です。v3の.15画像と旧/v2の.45画像は同一強度の比較ではなく、JSONの同強度行で照合してください。重複は加算して白飛びを増やさない。イベント時刻変換後はoutput時刻を一度だけ与え、seek切れ目を跨いで補間しない。

processing_revision欠落→legacy、明示新revisionだけv3。未知revisionは勝手にrewriteしない。旧project/goldenを保護し、new revisionの採用と製品修正は別PR・ユーザー判断。実LoL製品障害確定とは記載しません。実機は同一入力・旧単発・短間隔/長間隔連戦・速度変更・クリップ境界でT09を再実行。

強度注記の混同を防ぐため、FLASH_SAME_STRENGTH_0p15/0p45.jpgに旧/v2/v3を同じ入力・強度・8時点で並べました。全180frameのgray曲線はFLASH_SAME_STRENGTH_V4.json。0.15の旧/v3左右比較動画も保存。両シートを目視し、旧は後続pulse欠落、v2は.15の振幅が旧/v3と異なる、v3は単発の値と後続pulseを維持することを確認しました。

最終追加検証：v3のglobal union gateだけでは、前event窓が開いている間に未来eventの対称exp pulseが先に上昇します。.5/.6秒eventの34/60秒で、強度.15は旧150/v3 171、.45は旧169/v3 201、.9は旧196/v3 249。研究候補max_v4_causal_start_gateは各event前の項を0にして150/169/196へ戻しました。追加8×3=24条件、single旧bit一致3/3。FLASH_OVERLAP_CAUSAL_GATE.jpgとFLASH_GATED_REVISION_V4.jsonが証拠です。したがってv3を無条件の安全な修正として推奨せず、採用検討は因果gateも含む回帰後に行います。研究候補番号と製品processing revisionは同じ意味ではなく、製品側の自動変更は一切ありません。
