# 検証計画・Codex引継ぎ
今回の成果物は設計と研究fixture。AutoCine本体へ適用していない。UI10案比較/友人評価/採点/アンケート/順位付け/採用判断は一切対象外。

## 処理経路と変更の境界
core/effects.pyの_build_video_effect_filters/_enable_exprがCPU FlashとZoom段の既存接続。core/kill_icons.pyのbadge_motion_xy、core/work_kill_assets.pyの_render_preview_nativeとCPU合成が6motion/素材位置の接続。camera/TargetLock/BLUE-REDは既存controllerへadapter接続し、数理plannerを直接実機camera計算と置換しない。
素材承認はcatalog正本のまま。新revisionは明示選択・旧project保持・rollback可にし、研究候補を既定にしない。現開発branchへ取り込む前に最新code hashと今回のbaseline hashを比較し、異なれば再監査する。今回のbaselineはfb03e0390805125fc063f4599af6c2541a653abfの読み取りコピーで、最新実装で同じ不具合が残ることの証明ではない。

## 分割実装の順序（工程案、採用決定ではない）
S1: 共通TimeMap/座標/metadataだけを独立moduleへ。legacy経路は残す。
S2: CPU Flash丸め対策とtmix正規化を別revisionとして検査。変更後の単発/連打/色/全backendを比較。
S3: 素材/6motionを共通output-spaceへ接続し、preview/export/GPUの同一基準比較。
S4: verified geometry/長射程関連イベントの入力を実装できた時点でplannerを接続。なければ既存baseline。
S5: 実音源/実機でAV/GPU/長時間/失敗を試験。所定の正式審査後のみ採用。

## 再現方法
research_scripts/reference_contract.pyは提案のpure reference modelで、camera制御や検出器ではない。selftest()が既知の期待値と境界入力を検査する。research_scripts/research_lab.pyはFFmpeg/NumPyで人工Flash/Blur/音源/座標を再現する。Windows既定パスは元環境用で、別PCではR/FFのパスだけを研究領域へ合わせる。元アプリをimport/起動しない。FFmpegは公式/既設を使用し、新規installやhookは不要。
reference model初版の有理数fps parserで60000/1001文字列を受けられなかった点を修正し、最終37条件を確認。これは研究用コードの修正で製品の修正ではない。

## 受入ケース
### CT01 単発・追走
参照：V01/V07
入力：同Replay/patch/targetのpre/postとverified event
判定：全イベント含有、退路/対象可読、kill前後の切落としなし

### CT02 多人数・複数kill
参照：V05/V06/V11/V20/V22
入力：BLUE/RED、2/3/5人、同時/短間隔/別actor
判定：ID重複0、別victim保持、重要群可視率と遮蔽、余韻、手動優先

### CT03 長射程
参照：V25
入力：発射/弾道/命中の関連と時刻・位置が既知
判定：両端点の可視、発射/着弾のcut欠落0。不明ならbaseline

### CT04 挿入と切替
参照：V02/V08/V21/V23/V25
入力：戦闘終了/next engage/別take/外部素材の区別
判定：戦闘中cutawayなし、黒/CG誤判定なし、復帰先/時間map一致

### CT05 Flash因果性
参照：V01/V20の視覚参考＋人工fixture
入力：30/60/60000÷1001、VFR、同時/0.5004秒、2回/密集kill
判定：イベント前差分0、重複冪等、単発互換、revision比較。V4失敗6件を保持

### CT06 Blur/カラー
参照：V03/V09/V15/V20
入力：固定gray/RGB/HDR-SDR/動き/scene seek
判定：定数輝度、白飛び率、色metadata、履歴flush、ゲーム内発光と分離

### CT07 全素材/肖像枠
参照：652/35/89/37
入力：hash/namespace/承認状態、実portrait形状、実LoL背景
判定：見切れ/halo/目鼻/名前/左右/HUDの審査。暫定651/制約19は独立保留

### CT08 6motion/位置一致
参照：既存V4 disparity
入力：3解像度×30/60fps×DPI/viewport×6motions×3stack
判定：RGBA共通基準の端差<=1output px候補、overlay時刻差<=1frame候補。数理のみで合格しない

### CT09 安全・失敗復旧
参照：全20の構図参考
入力：未知side/失lock/遮蔽/未接続/手動/新engage不明
判定：状態不変、baselineと理由、勝手な反転/解除/無言fallback0

### CT10 誤検出対照
参照：V04/V12/V13/V15/V24
入力：objective/低HP/死亡/teleport/ad/black/title/再提示
判定：killへの誤昇格0を人手goldで判定。認識器の精度保証は別

### CT11 AV同期
参照：実音源待ち
入力：48k/44.1k stereo、PCM/AAC、0.5/1/2x、seek境界、長時間
判定：PTSでoffsetとdrift計測。±50msは暫定、固定補正で隠さない

### CT12 実機・負荷
参照：実Replay待ち
入力：CPU/GPU FX/NVENC/LoL音/失敗fallback
判定：drop/reorder/decoder/FPS/温度負荷/使用encoderを記録、NVENCのみでGPU合格にしない

各caseにsource_hashes/commands/version/timebase/seed/expected/actual/raw_log/output_hash/判断者を残す。PASS、FAIL、REVIEW、NOT_RUNを併記。閾値は提案で正式採用していない。LoL実機T01–T14の全体合格は今回も0/14。数理・人工CPUのPASSを移し替えない。

再実行時はprocess限定のAUTOCINE_RESEARCH_ROOTを既存研究workspace、AUTOCINE_RESEARCH_OUTPUTを新規の検証出力先、AUTOCINE_RESEARCH_FFMPEGを既設公式FFmpegへ設定する。既定出力もwork下rerun_resultsで、封印済みoutputsを上書きしない。Flash再現にはpinned baselineのcore/effects.py読み取りコピーが必要で、参照2関数の原文抜粋も同梱した。queue/audio inventoryの再現は既存V3/V4資料を必要とする。
