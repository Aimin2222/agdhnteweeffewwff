# Codexへ送る一括実装指示

LoL AutoCineの3UI・70機能・研究残件を、この統合資料を基準にまとめて実装してください。基準PR #55 `bd93e2caf3bdb823d52b86fead0d71fc15c41327`。作業開始時に先頭との差を確認し、後続修正を巻き戻さないでください。

## 保持するもの

候補3=testA/T-A-M/旧テストA現行整理。references/C3_T-A-M_original.pngとC3_FIDELITY_CONTRACTを正本にします。R1=Track Desk、R2=Shot Canvasはそれぞれ原画像/ナビ/配置を維持。3UIを同じ見た目へ統一しない。旧候補1〜10、混合7+4、UI29、C3-P/S、既存カメラ・37バッジ・89原本・652候補・35FXを保持。配布停止した研究demoは復元/再配布しない。

## 最初に読むファイル

MASTER_INTEGRATION_SPEC_JA.md → UI3_COMPLETE_SPEC_JA.md → FUNCTION_IMPLEMENTATION_MATRIX.json → CAMERA_FINAL_SPEC_JA.md → FX_COLOR_MATERIAL_FINAL_JA.md → UNKNOWN_FUNCTION_DECISIONS_JA.md → IMPLEMENTATION_ORDER_JA.md → TEST_MASTER_PLAN_JA.md。

## 一括実装範囲

1. 共通Appのstate/保存/型/能力を整理し、3UIの全入口を同じbackendへ接続。従来エディタ入口だけの35機能を画面内の専用sectionへ移す。機能を隠す場合も詳細から到達可能にする。
2. 候補3の3列・下段2mode/5tab・4slider・素材3切替/5枠/6animationを原画どおり維持。R1/R2のメインだけでなく、簡単/詳細/カメラ/キー/カーブ/色/素材/FX/出力/設定/診断をSCREEN_SPECIFICATIONSの36契約で実装。
3. R2 1920版の539pxを維持し1366の固定高overrideを修正、transport/shotstrip/timeline重なり0。`v.third_y`を`v.third_yaw`へ修正。ライト/ダーク/systemを全input/select/option/popupまで同一tokenで指定し白背景白文字を防ぐ。
4. 既存相対キーAPIと評価器を使いcurveに値軸/曲線/drag/数値/keyboard/保存/Undoを接続。2点smoothstep/3点Hermiteの実式と表示を一致。絶対FOV、linear/hold、自由接線、XYZは既存と別能力で、判断ゲートに従う。
5. 既存露出/temperature/vibrance/LUT/grade/色curveをUIへ接続。scene色override/均一彩度はschema拡張。既存compose_compare/exactStillを利用し、比較は同一frameで実装。preview_playへ結線しない。
6. Flash causal_pts_v1/Zoom normalized_tmix_v1は既に実装され通常BATが有効化するので作り直さない。実revisionの保存、TimeMap、CPU/GPU経路、cut/seek境界、OverlayPlan/6motion/位置差修正を実装・検証。
7. 素材namespace/status/hash/仮geometry/userExcludedを分離。正式承認は変更せず、図鑑・独立FX・同名pair・6motionを実IDで接続。P2残523と19原本制約を合格扱いしない。
8. 実job/出力/encoder/LoL音声/診断を接続し、初心者のリプレイ→scan→scene/check→おまかせ→preview→MP4を完成。project JSONとMP4作成は別。focusとcheck集合は独立。
9. ENGAGE/BESTSHOT/新自動構図/空間radial等は契約に従ってdata取得可否から実装。利用できない入力を架空値で補わない。metadataのkill数採点をBESTSHOT、kill filterをENGAGEとして代用しない。

## 重複開発を防ぐ

AUDIT_26_IMPLEMENTATION_REMAINDERSの既存親IDを維持。静的解消6件は回帰確認のみ、18改善/1追加/1仕様を残件として処理。R-02の解消は誤接続だけで実比較は残る。R2-01の539pxは修正済みだがcompactは残る。元のCodexテスト/監査原本を編集して結果を良く見せない。

## 判断待ち

DECISION_REGISTERのD01〜D11は推奨と選択肢で、正式採用ではありません。必要な判断をまとめて提示できる実装計画にし、未決定の新動作は有効化しない。決定不要の既存接続/不具合修正は進めてください。画像選択の自由取込、絶対FOV+64誤送信、EV露出、自由Bezierのダミー成功は禁止。

## 検証・返却

TEST_CASESと旧284受入IDの対応を保ち、単体→統合→Windows→実media→LoL/GPU/音声/DPIを実行。実行なしはNOT_RUN、限定fixtureを実機PASSへ繰り上げない。各修正のbuild SHA、input hash、実state/値/処理revision、比較画像、実ログ、失敗理由を保存。原画との差と実LoL未接続を別分類。

返却物：実装commit/変更範囲、70+追加能力の完了台帳、26残件の差分、3UI全画面の1920/1366・light/dark比較、操作結果、実MP4/AV/GPU証拠、判断待ち/NOT_RUN一覧。Windows BAT試験版は既存の安全な方針で作り、Defender回避/無断設定変更/停止研究demo復元をしない。mainへマージしない。正式UI選定はユーザーが行います。
