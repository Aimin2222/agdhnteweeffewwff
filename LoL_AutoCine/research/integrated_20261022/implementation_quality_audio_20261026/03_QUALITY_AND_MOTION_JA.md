# 素材・FX・登場アニメの品質仕様
652フレーム、35の静止RGBA FX素材、アプリの映像全体FX（Flash/Zoom Blur等）を別カタログ/処理として扱う。例えば35FXのD_project/impact_rgba.pngとCPU Flash filterは別物。同名フレーム承認をFXへ伝播しない。

## 全687件の次段階審査キュー
ASSET_REVIEW_QUEUEに652+35全件を元hash/承認状態付きで整理した。今回の新規目視は0件で、過去の検査を再度実施済みとは数えない。機械検査全687合格/原寸・背景審査の既存記録はV2–V4から継承。全12条件合格0、承認1/確認用651、FX35確認用のまま。
P0=50件（No004の原本制約確認またはsolid edge接触）、P1=90件（FXまたはsoft edge）、P2=547件。これは研究上の優先度で、不良認定や承認ではない。テーマ/種類別にはJSONのid/kind/reasonsで絞れる。edge接触は意図的発光か見切れかを原本と照合する。
651の暫定肖像枠、19原本制約（見切れ8/パレット11）は未解消。穴形状を円として確定せず、作者原本/完全版か独立した境界審査が必要。原本89/既存37は不変。

## 審査ゲート
G0 provenance：catalog ID/hash/status、原本と派生を分離。
G1 decode：画像全件decode、native寸法/色/alpha mode、hash一致。canvasサイズだけで1080p overlayの解像度を落第としない。実際の描画サイズと比べる。
G2 alpha：transparent/partial/opaque、bbox、edge接触、alpha0のRGB、縮小時halo。明/暗/高彩度/実LoL/HUD背景で比較。
G3 portrait：A/Bの穴/中心/枠形状、対象アイコンのトリミング・左右・名前/VSとの干渉。暫定651はgeometry_revision=provisional。
G4 temporal：35FX×weak/strong×6motions×30/60fps×複数kill/3段stack。連打で明滅/消失/先行/残像/切断がないか全frame metric＋通常速度の人手確認。
G5 position：実output/preview/GPUの同一RGBA基準に対する辺差、safe area/HUD遮蔽、stack overflowを検査。
G6 art/readability：原本テーマ、形状、文字、portraitの表情/目鼻、隣接badgeの識別性。自動hash成功を代替にしない。
G7 runtime：LoL・GPU・録画・AV・長時間・失敗fallback。承認はユーザー/既存正式工程でのみ変更。

## 6登場の原文照合（訂正を含む）
core/kill_icons.py:badge_motion_xyとcore/work_kill_assets.py:_render_preview_nativeを確認した。u=clamp(1−elapsed/0.260,0,1)、ease=u²(3−2u)。slide_left/rightは基準幅+20、slide_up/downは基準高さ+20だけ外から入る。up=下から、down=上から。instantは固定。
**popは16*exp(−18*elapsed)*cos(28*elapsed)の横方向揺れ**。拡大bounceでもopacityだけでもない。以前の資料に異なる説明がある場合はこの原文照合を優先する。強い拡大を足すなら別ID/revisionで、既存popは変更しない。
今回1458条件はこの軌道を使った座標変換の数理検査。実6motionの全画素/全動画/全素材を今回再審査したものではない。既存の144CPU clips/23472幾何条件は過去の結果として保持。

## リリース判定
機械PASS、視覚REVIEW、原本制約、実機NOT_RUNを別軸で保持。確認用使用チェックで正式承認を書き換えない。承認済み素材でも新renderer/revisionの互換性は別に検査する。
