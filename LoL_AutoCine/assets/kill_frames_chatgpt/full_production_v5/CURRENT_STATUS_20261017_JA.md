# 全原本フレーム制作 v5 — 生成上限による途中状態

## 2026-10-17の現在状態（全件完成ではない）

原本89枚に対応する652登録の初回候補は全て作成済み。新規634件と継承18件。修正版1件を追加保存し、旧版も保持。原本crop・白背景・黒背景で、現在のSHAに対応する652件を比較した。最終合格は0。

長辺2048px以上は651件。残る086/faerie_court_strongは1983×793で、単純拡大せず再生成が必要。085/targon_variant_1は修正版generated_v5_1.pngを2172×724で保存し再比較済み。

目視の要修正220件、外周のalpha非ゼロ590件、重複除外609件。内訳の和を未完成件数として加算しない。外周の薄い残りも完全透過の合格とは扱わない。全てreviewであり、不合格素材をfinalに入れていない。詳細はqa/visual_reviews.json、qa/strict_transparency_queue.json、qa/production_state_20261017.jsonを参照。

Faerie Courtの再生成時、内蔵画像生成がHTTP 429 / usage_limit_reachedを返した。ツールの解除予定は2026-10-17 17:55:47 JST（UTC 08:55:47、Unix 1792227347）。解除時刻の保証や自動再開の予約ではない。有料APIへ切り替えていない。

v5全件分の動くエフェクト、全件確認ZIP、高画質画像ZIPは未制作。既存35種の動作確認版を652件分の完成と混同しない。制作ツールと仕様書の保存は出力実績ではない。

原本89枚のSHAを再検証し変更なし。既存37バッジと本体プログラムには変更を加えていない。原本見切れ8件と小型配色参照11件の制約は継続する。

次回は086/faerie_court_strongのネイティブ2K再生成から。production_tools/frame_repair.pyが原本crop・全原本・現候補を区別したジョブを返す。外周alphaの数値検査も修正対象に含める。旧版を上書きせず新規版を保存し、新しいSHAで原本比較をやり直す。比較記録が古いSHAのままでは合格を引き継がない。修正後に全件のエフェクト、動き、ZIPを作成・検査し、実ファイルとSHAをGitHubで確認する。

指定ブランチ: chatgpt/killframes-source-numbering-20261014。現時点の途中台帳はcheckpoints/checkpoint_0634_repair0001_quota.json。GitHubの保存確認は親フォルダのFULL_PRODUCTION_V5_COMMIT_*_REMOTE_VERIFICATION.jsonを参照。
