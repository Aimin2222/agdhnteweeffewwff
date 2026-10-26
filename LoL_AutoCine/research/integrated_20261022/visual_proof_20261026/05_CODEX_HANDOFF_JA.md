# Codex向け修正・実装引継ぎ（未採用候補）
## 最初に
対象本体はfb03e039...のスナップショット。採用後にCodex側の現在のheadを固定して同じ症状を再現し、既に修正済みなら上書きしない。本研究は本体/UI29/原本/承認状態へ変更を加えていない。新しいrevisionを選べる形で段階的に比較する。12ルールと前回時刻/座標仕様はREFERENCE_*を参照。

## 優先1：Flashの小数3桁gate
接続先core/effects.py:_enable_expr/_build_video_effect_filters。eventのreplay timeから共通TimeMapでoutput時刻を得る。CFRなら有理数ceil(event*fps)で各項をgateし、出力frame時刻で減衰を評価。max合成で同時イベントの加算白飛びを防ぐ。既存IDを消さずlegacy/V5の処理revisionを保存。event重複排除は同一IDのみ、別victim同時killは保持。

受入：30/60/60000÷1001、rate1/.5、4系列、先行RGB差分=0。最初の正の差分frameも一致。後eventは前の残光があり得るため、追加event項の独立比較も行う。Flash0の同一色変換経路をbaselineにする。VFRはPTS列で最初のPTS>=event、seek/pause/連続性断絶/途中速度変更/長尺は追加。実AV同期は別gate。

## 優先2：Zoomの正規化と履歴
接続先core/effects.pyのzoom_blur graph。weights1,2,1のsumで正規化（scale0の使用可否は利用FFmpegで確認）。同じ色空間/alpha/rangeのfloat中間を使う。hard cut/seek/新clipで履歴をflushし、連続takeとは別continuity ID。正規化はradial blurの代わりではない。新空間ブラーは別IDでsample半径/weight/centerを定義。

受入：12groupに旧graph白飛びFAILを再現し、候補は新規の白クリップを増加させない。RGBパッチはズーム後の座標へ追従して測定し、今回の固定ROIで背景混入した平均を色変換エラーにしない。hard cutの最初のframeは旧shot色が0。GPUは別実行で同一PTSCPU対照、許容色差・VRAM/速度/失敗fallbackを確認。NVENC成功だけでGPU FX合格にしない。

## 優先3：preview/exportの共通overlay plan
接続先core/work_kill_assets.py:layer_plan/with_work_badges/render_preview_pair、およびcore/kill_icons.py:badge_motion_xy。同一plannerから有効event/row/start/end/reference rect/motion poseを生成し、各rendererへ渡す。view内でのイベントrow再計算や独自の早期丸めを避ける。native素材canvas/portrait穴/基準1920/output/video表示領域/DPIを別座標として扱う。half-upは最終辺だけ。

**今回の1920出力をただ縮小する候補は採用不可。** n9はよく揃うが登場中に最大163/116/109px差が残った。既存popの横揺れをbounce拡大へ変更しない。6IDと軌道を維持し共通時刻・座標の原因を修正する。

受入：実RGBAで3解像度×FX有無×1/3段×6motion、5点だけでなく全frame/開始前/終了後も比較。rowを含む各rect<=2pxを初期gate、alpha mask IoU/edge/RGB差は同じkernel/color条件で別測定。nativeWindows100/125/150%DPIとletterboxを追加。画面外入場中のbboxだけで合格/不合格を決めずlayerごとのposeを比較。frame083以外の円/四角/大きい装飾も追加。

## 素材とカメラ
651暫定portraitは素材別の穴形状/中心/マスクrevisionを確定してから接続。No004見切れを推測で正規原本にしない。35FXの今回の相手は083だけ。全652との互換・6動作・明暗実ゲーム/HUDの審査を追加。機械PASS/研究目視REVIEW/正式承認を分離し、ユーザー承認なしでcatalog statusを書き換えない。

カメラ接続先core.camera:CameraPlan/CameraDirector/limit_camera_post。third/third_cinemaと既存TargetLockを保持し、新plannerは独立した候補adapter。BLUE/REDと90/180°は実APIの軸校正fixtureを作成し、実TargetLock・両陣営・長射程・複数人・遮蔽の録画証拠を採る。geometry/side不明なら既存baseline、手動設定は維持。raw中心平均の即時切替は今回FAIL、速度制限だけで衝突安全としない。既存slow_api guardの通常bypass条件を守る。

## 再実行
同梱research_scriptsは独立試験。common.pyのR/S/A/FFを自分の読取スナップショットと素材rootへ設定する必要がある（この配布ZIPに1GBの原本群は重複同梱していない）。Python3＋NumPy/Pillow＋FFmpegが必要。出力先は新規研究用directoryにする。flash_zoom.py flash zoom、position_assets.py position assets、camera_proof.py、camera_followup.py、flash_isolated.pyの順。asset_recheck.pyはASSET_REVIEW_QUEUEと目視notesを読み、画像生成を目視完了へ変換しない。各スクリプトのhashと入力provenanceを先に確認。未知の最新本体へそのままコピー統合しない。

PASS/FAILはVALIDATION_REPORTの限定assertion。製品全体のリリース合格はNOT_RUN。研究提案の正式採用はユーザーとChatGPTの判断後。
