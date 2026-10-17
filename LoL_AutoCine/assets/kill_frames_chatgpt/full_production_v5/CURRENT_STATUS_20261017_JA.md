## Alpha cleanup GitHub verification update

Commit a690e954f6ec1d98d67f7a592da75e414e024ae1: 652 alpha-one-only derivative PNGs plus their manifest were saved and all 653 files were downloaded from GitHub and matched the committed bytes and SHA-256. The earlier local-only description below is historical. These derivatives correspond to checkpoint 0634_repair0010; ongoing geometry repairs have not been adopted into this derivative set. Final approved: 0.

## 2026-10-17 透過の微小残りの処理許可と検査

利用者が選び直した結果、alpha=1のみを0にする別版の数値処理を明示許可した。原本と生成原本を保持し、RGB・寸法・alpha=0および2～255は変更しない。チェックポイント0634_repair0010の652件で処理前後を検査し、この条件と生成原本のSHA不変を全件確認した。端にalphaが2以上の画素が残る196件は未解決であり、切り捨てず修正対象として扱う。最終合格0。

別版は現在ローカルのalpha_cleanup_v1に保存。再生成中の管理表へはまだ採用していない。GitHub保存済みという扱いにはせず、最新の再生成が確定してから採用・保存・実ファイルSHA検証を行う。許可記録はqa/alpha_cleanup_authorization_20261017.json。

# 全原本フレーム制作 v5 — 生成上限による途中状態

## 2026-10-17 夜の制作再開

利用者の再開指示後、内蔵画像生成が実際に成功したため修正制作を再開した。前回の利用上限停止は履歴であり、この再開時点では生成可能。086/faerie_court_strongを2172×724のRGBA PNGとしてgenerated_v5_1.pngへ別保存し、原本cropと白・黒背景で再比較済み。これで現在の652候補すべてが長辺2048px以上になった。

外周alphaの残りは再生成後も検出され、完全透過の合格にはしていない。次に原本との形状・配色・中央モチーフ等の相違が明確な候補を優先して修正し、その後も透過・見切れ・文字と顔の焼き込みを検査する。最終合格0件は継続。旧PNGと旧確認ZIPは保持し、有料APIへの切替はしていない。

この再開の証拠はqa/generation_resume_20261017.json。最新の保存数・比較結果はPROGRESS_JA.mdと新しいチェックポイントを参照。以下に記載された上限停止時の件数・解除予定・2K未満1件という記録は、その時点の履歴である。

## 前回の状態・設計・履歴

## 2026-10-17の現在状態（全件完成ではない）

原本89枚に対応する652登録の初回候補は全て作成済み。新規634件と継承18件。修正版1件を追加保存し、旧版も保持。原本crop・白背景・黒背景で、現在のSHAに対応する652件を比較した。最終合格は0。

長辺2048px以上は651件。残る086/faerie_court_strongは1983×793で、単純拡大せず再生成が必要。085/targon_variant_1は修正版generated_v5_1.pngを2172×724で保存し再比較済み。

目視の要修正220件、外周のalpha非ゼロ590件、重複除外609件。内訳の和を未完成件数として加算しない。外周の薄い残りも完全透過の合格とは扱わない。全てreviewであり、不合格素材をfinalに入れていない。詳細はqa/visual_reviews.json、qa/strict_transparency_queue.json、qa/production_state_20261017.jsonを参照。

Faerie Courtの再生成時、内蔵画像生成がHTTP 429 / usage_limit_reachedを返した。ツールの解除予定は2026-10-17 17:55:47 JST（UTC 08:55:47、Unix 1792227347）。解除時刻の保証や自動再開の予約ではない。有料APIへ切り替えていない。

v5全件分の動くエフェクト、動きを含む全件確認ZIP、高画質原寸画像ZIPは未制作。既存35種の動作確認版を652件分の完成と混同しない。制作ツールと仕様書の保存は出力実績ではない。

原本89枚のSHAを再検証し変更なし。既存37バッジと本体プログラムには変更を加えていない。原本見切れ8件と小型配色参照11件の制約は継続する。

次回は086/faerie_court_strongのネイティブ2K再生成から。production_tools/frame_repair.pyが原本crop・全原本・現候補を区別したジョブを返す。外周alphaの数値検査も修正対象に含める。旧版を上書きせず新規版を保存し、新しいSHAで原本比較をやり直す。比較記録が古いSHAのままでは合格を引き継がない。修正後に全件のエフェクト、動き、ZIPを作成・検査し、実ファイルとSHAをGitHubで確認する。

指定ブランチ: chatgpt/killframes-source-numbering-20261014。現時点の途中台帳はcheckpoints/checkpoint_0634_repair0001_quota.json。GitHubの保存確認は親フォルダのFULL_PRODUCTION_V5_COMMIT_*_REMOTE_VERIFICATION.jsonを参照。

## GitHub保存・実ファイル照合

## 追加した暫定の静止画確認ZIP

ユーザーの依頼により、未完成の現時点でも652候補を確認できる `downloads/review_snapshot_20261017/AutoCine_652候補_すぐ確認_20261017.zip` を追加した。ZIPをすべて展開し「ここから確認.html」を開く。検索・原本比較・背景切替・仮の採否記録とJSON出力に対応。縮小した確認用画像を収録し、原寸PNGは固定コミットへのリンクを付けている。候補PNG本体は変更していない。動画や完成素材ZIPの代替ではない。ChatGPT向けの現状まとめもZIP内と同じダウンロードフォルダに保存。

## 制作物の照合記録

制作物コミット: [120ed3bad77914ea29b66dbc760c008250d89afb](https://github.com/Aimin2222/agdhnteweeffewwff/commit/120ed3bad77914ea29b66dbc760c008250d89afb)。今回の追加45ファイルはGitHubから読み戻し、コミット内の実バイトと全件一致。

現在の652候補についても全件のSHAとGitオブジェクトを照合済み。605件は既に読み戻し済みのファイルと同一のGitオブジェクト、残る47件は今回の固定コミットから実画像を読み戻してSHA-256とGitオブジェクトを直接照合した。qa/github_current_candidate_coverage.jsonに1候補ごとの証拠を記録。保存の検証は視覚品質の合格を意味しない。
