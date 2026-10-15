# Codex向け実装契約

- clock: 出力タイムラインのkill時刻をt=0とする。-0.25秒〜2.35秒の見本。t<0で新しいFXは非表示。1.8秒以降はFX・粒子・フレームを非表示。
- 入力: motion.jsonのtextureとframeをリポジトリ相対パスで読む。SHA一致必須。ネイティブPNGは同ブランチの既存frame_based_review_v2を使用する。
- 基準座標: 512×288、中心(256,144)、フレーム幅480。実フレーム幅/480で一様拡大し、人物アイコンの実マスクを利用する。肖像穴は参照画像アルファから自動検出した比較用マスクであり、実マスクの代替だと断定しない。
- PNGはstraight alpha。参照レンダラはPillowのsRGB source-overで合成する。GPU内部の線形合成との明るさの一致は実装時に調整し、二重premultiplyをしない。
- motion.jsonのmodeとparticles全件を使用する。rendererのposition()が粒子軌道、render_effect()が光の走査・分割衝突・開示・パルスを規定する。毎フレームの積分に依存せず、時刻から直接評価する。
- event seedはSHA256('motion-v3/'+theme_id)の先頭12桁を整数化した確認用固定seed。実装時はevent_idを加えても良いが、同一イベントのシーク結果は固定する。
- source_texture_patchは四角いUV領域の装飾断片。元PNGは上書きしない。独立した完全な花弁の保証ではない。
- 確認用Python依存: Pillow / NumPy / OpenCV / FFmpeg(libx264) / Windows Meiryo。リポジトリのeffect_specs/motion_review_v3/motion_renderer.pyを使用する。ZIP内のコピー単独では元PNGパスが存在しないため、見るだけならHTML/MP4を利用する。
- GPU・カメラ・録画・音声・AutoCineの既存コードは変更していない。連続キル、実映像での可読性、実マスク、GPU合成は統合後に検証する。最終合格は利用者の確認後。

## フレーム本体の時間

既存No.083のA/B/C/Dを基準とし、Aは登場.20秒・保持1.10秒・退場.15秒、Bは.22/1.00/.18、Cは.24/1.00/.18、Dは.28/1.20/.22。Dの31テーマもこの共通値を確認用初期値に使うが、各テーマの過去の確定値だとは主張しない。粒子はフレーム退場後に短い余韻を残し、t=1.8秒までに必ず消える。フレーム退場時にイベント全体を即時破棄しない。レンダラ変更時はRENDER_VERSIONを更新し、古い出力のキャッシュを再利用しない。
