# 冬の祝祭・PROJECT・エルダウッド：元RGB不変の透過完成候補

基準：codex/browser-development-handoff-20261014 / e7b83d7。専用ブランチ：codex/killframes-three-theme-candidates-20261014。
素材元：codex/killframes-original-alpha-pilot-20261013 / 4d1ee858d799a14eba03cb6f0d0dbfe0757c7e8d。
カメラv5.10.27統合は保留し、3テーマの素材と台帳だけを扱った。元ブランチ全体のマージはしない。

## 成果物

[比較画像の入口](../assets/kill_frames/README_CANDIDATES_JA.md)

| テーマ | 背景比較 | 試作からの前後 | 肖像と全組合せ |
|---|---|---|---|
| 冬の祝祭 | [画像](../assets/kill_frames/qa/winter_festival_comparison.png) | [前後](../assets/kill_frames/qa/winter_festival_before_after.png) | [肖像](../assets/kill_frames/qa/winter_festival_portraits.png) |
| PROJECT | [画像](../assets/kill_frames/qa/project_comparison.png) | [前後](../assets/kill_frames/qa/project_before_after.png) | [肖像](../assets/kill_frames/qa/project_portraits.png) |
| エルダウッド | [画像](../assets/kill_frames/qa/elderwood_comparison.png) | [前後](../assets/kill_frames/qa/elderwood_before_after.png) | [肖像](../assets/kill_frames/qa/elderwood_portraits.png) |

[3テーマ×弱/強×3モチーフ＝18通りの一覧](../assets/kill_frames/qa/three_theme_overview.png)。
チェック柄は実透過の確認用、他3列は黒・白・LoL背景。各5素材は原寸で比較へ配置する。
肖像は公式ゲーム画像のAkali×Mordekaiserをサンプルとして使用。実試合のキラー/被害者ではない。ゲーム背景は試作ブランチに保存済みのHUDなし実機フレームを再利用。
素材PNGに肖像/背景/文字を焼き込まない。組合せプレビューは独立部品を重ねた検討用見本で、正式なUI/配置/動画/FXの仕様ではない。

## 実施した変更

- 3テーマの15 RGBA PNGと対応15 Lマスクを取り込み。比較前のマスクはqa/pilot_masks/、旧manifest/specも保存し、前後比較を再現可能にした。
- 元crop RGBは非表示画素も含め完全保持。背景モデルによる距離閾値、白紙色によるアルファ抑制、実測ROI/除外領域だけを調整。
- 孤立した1〜2画素のノイズを除去し、つながった枝/葉/細い線を一律侵食しない。
- 冬の祝祭の上部罫線、PROJECTの関係しない外周破片、エルダウッド強の罫線と葉/枝の接点を局所調整。
- エルダウッド強の上部を元画像で拡大確認し、除外しすぎた葉先を戻すROIへ再調整。元絵から消えている装飾は描き足さない。
- core/kill_frame_themes.pyのPROJECT/エルダウッドを実ファイル名へ修正し、冬の祝祭を追加。3テーマの1448×1086、各5実測crop、中央3種のnormalized中心を登録。実測crop/肖像穴/出力対応はsource_mapping.jsonにも保存。
- 登場FXは実装しない。冬の祝祭のintro_fx識別子も台帳の仮値で、正式仕様はChatGPT担当の確認へ残す。
- builder/verifyツールと素材回帰テストを追加。旧試作builderが完成候補を誤って上書きする実行は拒否する。

## 数値品質の確認

[candidate_verification.json](../assets/kill_frames/qa/candidate_verification.json)に全15点の詳細を保存した。

- RGB変更素材0：全RGBが元PNGの実測cropと完全一致。
- 15本体/15マスクのSHA、RGBA/L形式、alphaとmaskの全画素一致、肖像穴の中心20×20透過を検査。
- 元画像89枚のサイズ/SHAが台帳と全件一致。既存37素材のGit blobツリーも基準と一致。
- 試作からalphaを下げた画素116,838、孤立ノイズ除去180画素。エルダウッド強で277画素のalphaを上げて装飾を復元。
- alpha総量の試作に対する保持率67.638〜91.741%。背景除去で減少する量であり、画質スコアや全背景画素の識別正解率ではない。
- 3テーマの対応が解決。台帳全31件中、残28件の画像対応は未解決のまま。今回の対象以外は素材化しない。

## Windowsテスト

専用.venv Python3.14.7で隔離コピーを使用。既存LoL起動中は全件runnerが安全拒否し、ユーザーの終了後に実行した。
最終pytestは80ファイル・702件すべて成功、7バッチ全終了コード0。旧式総合16件もすべて成功（465.3秒）。失敗/skip/除外なし。
初回全件は700成功/1失敗で、最終再実行には追加した上書き防止1件も含めて702成功。失敗した初回記録も保持する。
素材関連47件は成功。旧試作の16件＋既存台帳8件＋候補品質23件。失敗/skip/除外なし、Pillow getdata非推奨警告1件。
初回素材試験で確認用肖像の寸法を120pxと仮定した検査が3件失敗。実キャッシュ128pxを確認して検査を修正し、再実行47件成功。
初回全件では既存tests/test_v5103_nonblocking_dispatch.pyのconnectionケースがqueued診断行の欠落で1件失敗。UIと当該テストは基準と差分ゼロ。単独再実行9件成功。原因は確定しておらず、断続的な診断ログ欠落の観測として記録する。UIや検査条件を変更して通す対応はしない。
構文6ファイル、git diff --check、JSONの個人パス混入検査も成功。
ログはGit除外のdiagnostics/local_dev/に保持。LoL実機の正式動画合成は未実行。

- 20261014_094418_373757：初回全件と総合16件成功。既存UIログ検査の失敗詳細。
- 20261014_094741_374533：最終素材47件成功。
- 20261014_094943_580666：既存UIモジュール単独9件成功。
- 20261014_095211_923429：最終全pytest702件成功。

## 保護したもの

camera/TargetLock/jobs/recorder/capture/audio/GPU/effects/kill_icons/legacy_app/UIには差分なし。
元89 PNGと既存37 PNGは変更/改名/削除なし。ユーザーのsettings.jsonとproject JSONは作業前後のSHA一致（2ファイル）。
カメラ基準監査の未追跡Markdown、ユーザー設定/プロジェクトは今回のコミットに含めない。
main、PR #29、v5.10.27、元の試作ブランチは変更・マージしない。既存環境や依存の再インストール/大容量取得/管理者導入は行っていない。

## 残る目視確認と次工程

全素材candidate_pending_visual_approval、visual_approval=false。黒/白フリンジや背景の残りを完全解消したという宣言ではない。
元RGBに背景色が焼き込まれた発光や、肖像/ボード線と重なる装飾は、alphaだけで真の元レイヤーを復元できない。RGB不変を優先し、描き直し/色の作り直しはしない。
黒/白背景では特にPROJECTの暗い金属/下地、冬の祝祭の淡い氷、エルダウッドの細枝と葉先、丸枠の接点を確認する。背景を減らしたことで薄い発光が弱くなりすぎていないかも確認する。
正式承認前に残テーマへ展開しない。本報告後、ChatGPTとユーザーが比較を確認し、次にA/B/C/D UI・配置・登場FX仕様を確定してから実動画/共有エンジン統合へ進む。

## 再現方法・変更範囲

LoL_AutoCine内で .venv/Scripts/python.exe -B tools/build_killframe_candidates.py、続いてtools/verify_killframe_candidates.py。
全テストはRUN_TESTS.bat（LoLを閉じる）。確認画像を見るだけならアプリ/LoLの起動は不要。
主な変更：assets/kill_frames/、孤立台帳core/kill_frame_themes.py、素材用tools 3本、素材テスト2本、本報告。
手順の詳細とリンク一覧はREADME_CANDIDATES_JA.mdへ集約した。
