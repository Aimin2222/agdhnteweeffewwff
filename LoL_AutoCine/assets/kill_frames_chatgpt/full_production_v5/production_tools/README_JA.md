# 素材制作・再開用ツール

本体とは独立した素材管理・検査・確認出力用。本体コードは変更しない。2026-10-16 17:54 JSTに生成を再開した。最新の制作状態は production.json と PROGRESS_JA.md を読む。GENERATION_LIMIT_STATUS_JA.md は過去の上限記録を含む。

実行時の作業ディレクトリはリポジトリのルート。Python + Pillow + NumPy + OpenCV、動画出力にはFFmpegが必要。package_all.pyの構文確認はWindows標準位置のNode.jsを参照する。確認版の日本語フォントはWindowsのMeiryo。画像生成APIを呼ぶスクリプトではなく、画像自体は内蔵image_genで1素材ずつ制作し、生成PNGをframe_runner.pyで保存する。

## 原本の読み取り元

この制作ブランチには原本89枚が含まれていない場合がある。原本を管理するブランチ codex/killframes-all-89-candidates-20261014 と既存manifestを参照し、読み取り元のSHAを qa/source_integrity.json と照合する。既存原本を変更しない。通常は LoL_AutoCine/assets/kill_concepts/ を読み、必要なら環境変数 AUTOCINE_KILL_SOURCE_DIR で原本フォルダを指定する。ローカルの隔離worktreeでは兄弟の ../LoL_AutoCine/assets/kill_concepts/ も読み取り候補になる。

## 手順

1. frame_runner.py jobs 0 4 で未制作候補のプロンプトと参照パスを取得。No.016の修正待ちには reference_corrections/016/corrections.json を優先し、旧参照cropの欠けを再利用しない。再制作は別の出力名と履歴を使用し、既存PNGを上書きしない。
2. 原本全体と該当cropを見て、内蔵image_genに参照を渡し、高画質・透過RGBAで制作。save INDEX GENERATED_FILE で新規候補を保存。initは初期化用であり、既存台帳がある状態では実行しない。
3. qa_frames.py でSHA・alpha・寸法と未比較の白黒コンタクトシートを作る。作成だけで目視レビュー済みにしない。visual_reviews.jsonへの追記は実際に比較したkey/SHAだけ。修正が必要ならrepair_queue.jsonと旧版履歴を維持する。
4. 全652候補が揃ったら修正対象を確認する。frame_repair.py preview COUNT は修正候補の読み取り専用確認、jobs COUNT は全候補が揃った後の修正用プロンプト出力。原本crop・原本全体・旧候補の3画像を実際に見てから内蔵image_genで修正し、使用した単一ジョブJSONを保存して save INDEX EXPECTED_PREVIOUS_SHA GENERATED_PNG JOB_JSON を実行する。旧PNGと生成時の参照・SHAを履歴に残し、新しい候補は generated_v5_N.png に保存する。修正だけで合格にせず、再度目視比較する。原本自体が欠けている部分は推測復元しない。
5. 全652候補と必要な修正を確認後に render_motion.py を実行。未制作が残る場合は停止する。各候補に動く比較MP4・透過WebP・2048ピークPNG・仕様を生成する。途中再開は入力SHAと版、出力SHAが全て一致したものだけ再利用する。
6. 全件の目視比較と動きの確認後、finalize_all.pyで整合を確認する。レビュー記録が全件分揃わない場合は停止する。最終採用0と修正待ちの注記は保持し、自動合格にしない。
7. package_all.py で全件の一覧ZIPと高画質透過PNGの分割ZIPを作る。未制作・未出力が残る状態では実行しない。ネイティブPNGはバイトを保持し、確認動画のみ軽量化する。全ZIPのCRCとSHAを照合する。
8. 指定ブランチへ素材・資料だけ保存し、固定コミットのGitHub実体を再取得してSHAを照合。保存・生成・レビュー・最終採用・本体統合を区別して報告する。

原本の厳密一致、微小alpha残留、原本の欠損箇所、推定の肖像マスクは未承認。CPU確認版をGPUや実LoLの試験結果と混同しない。既存35種のv3確認ZIPを、v5全652登録の完成物だと案内しない。
