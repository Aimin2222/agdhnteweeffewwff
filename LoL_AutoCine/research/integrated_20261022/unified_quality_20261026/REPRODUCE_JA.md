# 再実行と依存入力
研究用Python+NumPy+Pillowと既存FFmpeg CPUを使用。pip install/RTK hook/Windows設定変更なし。scriptsはこのworkspaceのwork/autocine_unified_quality_20261026/に置いた構成でR=parents[2]を想定する。ZIP展開だけで687原本を同梱したものではない。別PCではcommon.pyのR/OLD/S/A/FFと関連読取rootを研究用コピーへ明示してから実行する。本体にパスを書き戻さない。

必要入力はINPUT_PROVENANCE/SOURCE_REFERENCES/PROTECTIONとREFERENCE_ASSET_REVIEW_QUEUEにhashを記録。原本687/37/89、公式アイコン、旧source snapshotが必要。SOURCE_REFERENCESのGitHub固定commitから取得した照会原文はsource_referenceへ同梱。巨大原本を再梱包/改変していない。再取得は対象を選び、素材IDとhashを照合する。protectionのlocal pathはこの研究環境の参照で、他PCに存在する保証はない。

手順: assets.py→record_visual_reviews.py→assets_followup.py、fx_extended.py→fx_followup.py、parity_full.py、b_fixtures.py、audio_fixtures.py、finish_research.py、reports.py、seal.py。各領域のみ再生成してもよい。read-only原文のAST抽出は指定関数だけを研究processで実行し、製品アプリは起動しない。b_fixturesは研究sandboxの日本語journalのみ書く。録画/本体UI/ネットワーク/DNS/音量を操作しない。

ZIP内research_scriptsは保存した再現ソース。seal/publish/verify_remoteは配布担当の作業記録であり、自動で再pushしない。新環境で再実行する前に出力先・Gitブランチと原本read-onlyを確認する。画像レビュー所見は既存記録で、スクリプトを回すだけで目視承認が増えない。
