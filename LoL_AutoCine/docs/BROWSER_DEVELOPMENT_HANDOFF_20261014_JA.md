# LoL AutoCine — 旧ブラウザ開発からWindowsローカルへの引き継ぎ

調査日：2026-10-14（日本時間）。対象リポジトリ：Aimin2222/agdhnteweeffewwff。

## 1. この資料から再開する

現行基準は `codex/legacy-suite-fixes-20261014`、コミット `98e736e9d757bdc5c02327c722ae521907e362d1`。
`VERSION.txt` は **5.10.26-test**。Windows開発環境整備と旧式総合7件修正を含む。
本書はそこから派生した `codex/browser-development-handoff-20261014` に保存する。
今回の変更は本Markdownだけ。コード・画像・設定・録画の変更、別ブランチのマージ、統合、配布物作成は行わない。

旧チャットの全発言・添付MP4・私的診断・未保存作業は復元できない。GitHubにある資料・Gitオブジェクト・現行ソースと、存在するローカル検証ログだけを根拠にする。
資料上の旧実機報告は「過去資料に記録された報告」、今回読んだコードは「実装確認」、ログを確認したテストは「実測記録確認」と区別する。
最新のユーザー指示、現行ソース、新しい実測結果を優先し、古い「現在」「次版」「完成」の文言で巻き戻さない。

### 調査した必須資料

以下の現行資料は基準コミット `98e736e` の `LoL_AutoCine/` 以下を確認した。

| 資料 | 用途・採用範囲 |
|---|---|
| [AGENTS.md](../AGENTS.md)・[CODEX_HANDOFF_JA.md](../CODEX_HANDOFF_JA.md) | 日本語、機能保護、TargetLock、音声、GPU、Tkスレッド、安全な小差分。v5.8.5という版記述は過去のもの。 |
| [HANDOFF_MASTER_2026-10-09_JA.md](HANDOFF_MASTER_2026-10-09_JA.md) | v5.9.8以前の重要履歴、過去障害、製品方向、参考資料の索引。 |
| [HANDOFF_TO_NEW_CHAT_2026-10-11_JA.md](HANDOFF_TO_NEW_CHAT_2026-10-11_JA.md) | 2系列のv5.10.15、担当分担、共有API、37素材、編集UI、未検証の注意。 |
| [IMPLEMENTATION_AND_WINDOWS_TEST_v51026_JA.md](IMPLEMENTATION_AND_WINDOWS_TEST_v51026_JA.md) | 古い実行版の誤認防止、版/fingerprint、空・マップ外の疑いの補助検知。 |
| [LEGACY_SUITE_FIXES_20261014_JA.md](LEGACY_SUITE_FIXES_20261014_JA.md) | 現行Windowsテスト663件・総合16件、t12/t16修正、実機未検証の範囲。 |
| [v5.10.27 CODEX_INTEGRATION](https://github.com/Aimin2222/agdhnteweeffewwff/blob/cf8d6e0c79b0b58907bc987e240bf34a6ff2a1b5/LoL_AutoCine/docs/CODEX_INTEGRATION_v51027_JA.md) | 別系統のカメラ軸修正候補。基準への統合済み資料ではない。 |
| [3テーマ README_PILOT](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4d1ee858d799a14eba03cb6f0d0dbfe0757c7e8d/LoL_AutoCine/assets/kill_frames/README_PILOT_JA.md) | 元RGB不変の15点透過試作。視覚承認・アプリ統合は未完了。 |

追加でWindows環境整備資料、A/B/C/D引き継ぎ、source_import_manifest、試作manifest/verification、v5.10.27のVERIFICATION/SOURCE_GIT_REPORT、ブランチ履歴、現行app/legacy_appとcore/UIの主要経路を確認した。

## 2. GitHubの保存位置と混同禁止

指定ブランチをfetchし、GitHubの参照と一致する先端を確認した。checkoutして旧コードをコピーする方法は使わず、別ブランチの資料・画像は `git show` で読み取った。

| 系列 | 固定コミット | 現状 |
|---|---|---|
| 現行ローカル基準 | `98e736e9d757bdc5c02327c722ae521907e362d1` | Windows環境＋7件修正＋89元画像。通常開発の出発点。 |
| Windows環境整備 | `164d1067e77fd3ae578bf4e2702ef1e8dea1ad16` | 現行基準の親。 |
| 元画像取り込み | `ae73309d9066f5389cb443fd999dbe10239ad524` | 89枚・台帳をGitへ保存。 |
| カメラ候補 `codex/lol-autocine-v51027-camera-axes-handoff` | `cf8d6e0c79b0b58907bc987e240bf34a6ff2a1b5` | 5.10.27-test。別系統の改善と配布/QA変更が蓄積。現行へ未統合。 |
| 素材候補 `codex/killframes-original-alpha-pilot-20261013` | `4d1ee858d799a14eba03cb6f0d0dbfe0757c7e8d` | 89元画像＋3テーマ試作。現行へ未統合。 |
| main（保護） | `c2a79ac3e7816c74b7d7fb15a5a32a32dd8fa16b` | 今回変更しない。 |

現行とカメラ候補の共通祖先は `830206b15653fcf9137962986d5accaf685ae383`（v5.10.15系列）。
両先端の `LoL_AutoCine/` 差分は269パス、coreは18パス。**「v5.10.26の上にv5.10.27だけを載せた差分」ではない。**
候補ブランチには元画像89枚、現行A/B/C/D台帳、Windows .venv起動/検証ツール、直近7件修正がない。
全体置換でこれらを失うため、丸ごとcheckout/ZIP上書き/無選別マージをしない。

[PR #29](https://github.com/Aimin2222/agdhnteweeffewwff/pull/29) は今回APIでread-only確認：open、draft、未マージ。
baseは `codex/lol-autocine-v51014-studio-gpu-handoff`、headは `codex/lol-autocine-v51015-ui-scan-camera-handoff`（`0e8e8f65362fd10a3ab9509c3fcbb4580b72691d`）。
main向けの現行統合PRと誤認しない。今回コメント・編集・マージは行わない。

## 3. 引き継ぐ重要な開発履歴

| 時期・版 | 保存資料/履歴で確認した内容 | 現在への意味 |
|---|---|---|
| v4.x〜v5.7.x | Orbit/TargetLock、三人称斜め後ろ、LoL音声、録画/速度/FFmpeg CUDA障害の反復改善という過去資料の記録。 | 良好なカメラを根拠なく変更しない。8倍速、音声欠落、白黒化、access violationを回帰項目にする。 |
| v5.8.4〜v5.9.8 | チェック済み出力のクラッシュ改善、カラー・LoL専用音声・NVENCの過去実機報告。 | 当時の安定比較資料。現在版をこの版へ戻す指示ではない。 |
| v5.9.9〜v5.10.8 | キル装飾、スマート編集、GPU、色/FX、円形DOF等が段階追加された。 | 旧「6機能が未実装」は現在の一括判定に使わず、現行実装を個別確認する。 |
| v5.10.9〜13 | 高解像度素材、肖像、実シーン比較、全体スキャンキャッシュ、21＋16＝37素材。 | 37件と設定/実イベント対応を保護。 |
| v5.10.14〜15 | 5編集ゾーン、ホイール誤操作抑止、500ms比較/ヘルプ、10切替、非同期画像処理、UI/GPUの選択的統合。 | 同番号のChatGPT側/Codex側ブランチやZIPを同一視しない。共有ファイル上書き禁止。 |
| v5.10.16〜25 | カメラ構図・QA・比較画像・版更新が両系列で積み上がる。 | 現行とCodexカメラ候補では履歴が分岐。タイトル/版番号だけで採用しない。 |
| v5.10.26 | `1311c6d`版/fingerprint、`3afce85`空候補警告、`82f5f6a`引き継ぎ、`bec275d`警告閾値テスト。 | 5.10.23-testの画像を5.10.25の実測として扱った誤りを再発させない。 |
| 2026-10-13 | `a5bafac`A/B/C/D台帳、`ae73309`元画像89枚。 | 「素材未アップロード」は古い情報。台帳/抽出/動画統合は別段階。 |
| 2026-10-14 | `164d106`Windows整備、`98e736e`旧式7件修正。 | 現行のローカル測定基準。旧9成功/7失敗は解消済み。 |
| 別カメラ系列 | `86443c9`カメラ軸・モード独立性の修正候補、`cf8d6e0`CI/復元記録。 | 候補としてレビューし、現在へ未統合・修正後LoL構図未確認とする。 |

重大回帰防止：`hwdownload,format=yuv420p`の失敗経路を根拠なく復活させない。LoL専用録音を全デスクトップ録音へ戻さない。音声ONで欠落を黙認しない。Tk変数はUIスレッドで取得する。時計・最終FPS・実時間録画・停止/キャンセル・二重起動防止・カラー保持を保護する。

## 4. 現行実装の所在と限界

| 機能 | 実装の主な所在 | 状態・注意 |
|---|---|---|
| 起動/既存UI | `app.py`→`legacy_app.py`、`ui/*` | かんたん/詳細、5ゾーン、シーン設定を維持。古いdocstringの版は現行VERSIONではない。 |
| リプレイ/イベント/対象 | `core/replay_api.py`, `players.py`, `scanner.py`, legacy_appの全体スキャンキャッシュ | 対象切替時にキャッシュを絞り込み、別リプレイで破棄する実装あり。実LoL接続は今回未実行。 |
| シーン/自動編集/保存 | `ui/scene_project.py`, `highlight_director.py`, `smart_montage.py` | schema 3で旧schema 1/2を受け付ける。イベント情報から5キーフレームと見せ場選定を行う。敵の実位置や遮蔽を推定するAIではない。 |
| カメラ/TargetLock | `core/camera.py`, `camera_tuning.py`, `camera_clock.py`, `jobs.py` | 校正、対象追従、シーク、平滑化、安全topが存在。v5.10.27の新しい軸修正ポリシーは未導入。 |
| 録画 | `core/capture.py`, `capture_process.py`, `capture_worker.py`, `recorder.py`, `jobs.py` | WGC窓取り込み、実時間管理、停止検知。`recording_fps=min(capture_fps,fps)`で最終60fpsに不要な144fps録画を抑制。 |
| ゲーム音 | `PreferredGameAudio`, `tools/native_audio/lol_audio_helper.cpp`, `core/procloop.py` | UIの実録音factoryはNative LoL Process Loopback。helperとPIDが必要。`audio.py`冒頭の全出力録音説明/旧LoopbackAudioクラスだけを見て通常経路を判断しない。失敗時に全デスクトップへ代替しない。 |
| 動画/色/FX/GPU | `core/effects.py`, `gpu_full.py`, `gpu_bloom.py`, `gpu_pipeline.py`, `gpu_binary.py` | GPU経路・能力プローブ・CPU recovery・NVENC/CPUエンコーダ・音声結合が存在。NVENCとGPU FXは別。すべての効果/場面の実機画質合格を意味しない。 |
| 静止画/軽量比較 | `core/preview.py`, `ui/frame_comparison.py`, `template_gallery.py` | 正確静止画の寸法/色形式修正済み。numpy表示は近似で画素一致保証なし。 |
| 37キルフレーム | `core/kill_icons.py`, `ui/kill_frame_gallery.py`, `assets/kill_badges/` | 既存PNGを使う経路。新Dテーマの完成素材/選択UIとは別。 |
| A/B/C/D候補 | `core/kill_frame_themes.py` | 独立台帳・選択値検証・切り出し・登場タイミング計算のみ。通常UI/動画合成からの呼び出しは確認できず、試作3テーマも未接続。 |
| QA | `core/camera_qa.py`, `qa_visual.py`, `qa_plan.py`, `qa/test_plan.json` | 5.10.26版識別とPRE/KILL/POSTの単色領域警告。遠隔JSONは既知操作のデータ計画として検証、通信失敗時は付属計画。空/敵/キル視認の証明ではない。 |

横型1920×1080/60fpsを標準とし、内部カメラ/ミラーHzと最終fpsを混同しない。縦型Shortsの追加は旧確定要件に反する。
参考動画/Lolnamは技法と操作思想の参考であり、未読MP4の解析・モデル学習・全構図再現を完了と主張しない。

## 5. カメラv5.10.27と現行の具体的差異

候補の説明基準はCodex単一QA版 `fa13295637e7c1e97c60c74f332430de707a96ae`。現行HEADとは別物。
候補の最小変更を調べる出発点は `86443c9^..86443c9` の19パスで、両ブランチ先端の269パスを全部取り込む方法ではない。

| 項目 | 現行98e736e | 候補v5.10.27 |
|---|---|---|
| Euler/視線 | BLUEの既存geo-lookやFPS・REDの一部で別経路。旧軸校正/補正を残す。 | BLUE5種とRED2/4は実送信offsetからX=水平yaw、Y=俯角、Z=0を算出。共有target_center_rotationの数学自体は同じ。 |
| モード独立 | チーム別プロファイルとSHOT_TUNINGあり。 | チーム×5モードの独立プロファイル/ポリシー、deepcopyしたキーフレーム、モード別キャッシュを明示検査。 |
| RED1 | 既存自動サイド補正。 | 自動サイド距離に追加1.08倍。手動サイドと角度は保護方針。 |
| RED3/5 | 現行独自履歴を含む既存経路。 | 候補の旧fa13295との固定goldenで6条件×5時刻のoffset/rotation/FOV/speed一致を検査。現行HEADとの一致を保証するテストではない。 |
| BLUE6 | 現行SHOT_TUNING X=-2°。 | 旧SHOT_TUNINGは互換用に残し、新live軸経路では誤軸補正を使わない。X=-4°の別試験案を採用しない。 |
| stale基準座標 | 既存校正・再読込・キャッシュ復旧。 | 同じ対象/モード/ゼロoffset/有限座標/距離を確認し最大2回再取得。不成立は理由付き安全top。 |
| 録画冒頭 | `_prepare_clip_capture`で校正/映像更新後に録画。 | `_apply_initial_camera_pose`で最終姿勢を最大3回確認してから録画/音声開始。不反映時は中止。 |
| director送信 | 平滑化と遅いAPIの制限がある。 | 制限後の実際の送信offsetから同時に視線再計算、yawの360°境界を連続化。 |
| QA/配布 | 現行500MB枠の計画、5.10.26版・空候補警告。 | 開発QA入口1つ、送信用540p60/各30MB以下、initial_pose_checks等。通常1080p録画とは区別。 |

候補で中心となる編集は `core/camera.py`, `camera_tuning.py`, `jobs.py`, `camera_qa.py`, `qa_plan.py` と対応テスト・版/QAメタデータ。
先端比較には `camera_geometry`, `kill_icons`, `gpu_full`, `effects`, QA包装・UIも含まれる。これらはv5.10.27軸修正だけの差分ではなく、個別に理由を確認する。
候補の古い `effects/preview` を使うと今回のt16修正が失われる。古い起動/テストバッチでWindows整備を戻さない。

カメラ識別：Git blobのcamera.py＋camera_tuning.py連結SHA256先頭16桁は現行 `9e8b67454cb10e33`、候補 `d24f6d6fa573b4e2`。
今回のWindows作業ツリーの実バイトでは現行 `2be46598b039096c`。改行の違いがあるため、Git blob指紋と実行時resultsの指紋を混同しない。
QA実装は**実際に起動したファイルのバイト**をハッシュする。試験時は同じ展開/checkout方式の基準と照合し、VERSIONだけで同一としない。

候補資料に記録された旧実機評価はRED3/5良好、RED1近い、RED2反転、RED4地形裏、BLUE全般不適切。
これは修正前の証拠を解析した記録であり、**修正後v5.10.27の実機構図合格ではない**。私的MP4原本は今回未取得・未再解析。
候補VERIFICATIONにはLinux853件、Windows CI79件成功とrun 38372750998が保存されている。今回そのテストやCIを再実行していない。
同資料はWindows physical device=false、過去Tk native exit原因未解決を明記。CI・モック合格でLoL実機合格にしない。

## 6. キルフレーム素材の状態

| 素材群 | 現行基準 | 試作ブランチ | カメラ候補 |
|---|---:|---:|---:|
| 元コンセプトPNG | 89 | 89 | 0 |
| 既存kill_badges PNG | 37 | 37 | 37 |
| 新3テーマRGBA本体 | 0 | 15 | 0 |
| 対応アルファマスク | 0 | 15 | 0 |

今回、元89枚のサイズ/SHA-256を `assets/kill_concepts/source_import_manifest.json` と全件照合した。
37素材のGit blob一覧も現行/試作/カメラの3系列で一致。元画像は改名・再生成・削除しない。
89枚は完成した89種類のフレームではなく、元コンセプトボード。37素材、30テーマ台帳、3テーマ試作を同じ件数として扱わない。

### 保存場所と試作品の構成

現行の元画像は `assets/kill_concepts/`、既存37は `assets/kill_badges/`。
新素材は試作ブランチの `assets/kill_frames/themes/{winter_festival,project,elderwood}/` にある。
各テーマは `frame_weak.png`, `frame_strong.png`, `center_melee.png`, `center_ranged.png`, `center_hybrid.png` の5点と対応 `*.alpha.png` の5点。
採寸・SHA・状態は `assets/kill_frames/manifest.json`, `pilot_extraction_spec.json`、監査は `qa/verification.json`, `qa/catalog_source_audit.json`。
比較は `qa/<theme>_comparison.png`、採寸図は `qa/<theme>_source_regions.png`。大量の原画像をチャットへ添付しない。

| テーマ | 実在する元画像 | 元寸法 | 残る品質問題（README記録） |
|---|---|---|---|
| 冬の祝祭 | `assets/kill_concepts/image.png` | 1448×1086 | 氷の発光、青い下地の縁、ボード罫線との接点。 |
| PROJECT | `assets/kill_concepts/image-gen-1(8).png` | 1448×1086 | 白背景で暗い縁、背景線・細片、暗い金属と背景の判別。 |
| エルダウッド | `assets/kill_concepts/image-gen-1(10).png` | 1448×1086 | 葉/花/枝の輪郭、紙背景の発光、肖像/罫線と重なる枠の欠け。 |

今回Git blobをメモリ上で読み、15本体＋15マスクのSHA、RGBA/L形式、元cropのRGB全画素一致、出力alphaとマスク一致を再確認。画像の書き出しや抽出の再実行はしていない。
試作verificationには数値16テスト成功とあるが、今回16テストを再実行したという意味ではない。
statusは `prototype_not_approved`、visual_approval=false、needs_manual_mask。数値一致は視覚品質の合格ではない。
焼き込まれた発光の元RGBと本来のalphaは一意に復元できず、隠れた装飾を想像で描き足さない。

### 未統合のブロッカー

現行 `core/kill_frame_themes.py` の30件すべてのsource_fileが実ファイル名と不一致。冬の祝祭は未登録。
既定motif_centersは仮値。実画像のcrop_box/中心/肖像穴を確認し、将来の明示マッピングへ反映する必要がある。
A=シンプル、B=高級感、C=シネマ、D=スキン/地域テーマの選択検証とタイミング計画はあるが、A/B/C/D UI、保存互換、FFmpeg接続、テーマ登場FX動画化は未完了。
台帳の存在を完成素材の選択機能として案内しない。古い「元画像がない」は解消済みで、現在は対応表・マスク品質・統合が課題。

## 7. 最新検証結果と未実装・未検証

この資料作成ではアプリ起動/録画/pytestを再実行していない。コードを変更していないため、2026-10-14の直近実測を引き継ぐ。
実在する `diagnostics/local_dev/20261014_021834_885339/summary.json` の8スイート終了コード0とlegacy.logの16 PASSを読み直した。
検証の詳細はLEGACY_SUITE_FIXES資料にあり、個人パス付き生ログはGit除外のまま。

- Windows Python3.14.7/.venv：pytest **663/663**（78ファイル）、旧式総合 **16/16**成功。失敗/skip/除外なし。
- t06/t07/t10/t11/t12/t13は旧テスト条件修正。音声WAV欠落拒否・LoL不在時のキャプチャ禁止は維持。t12は録画区間のtop/追従/最低高度を検査しカメラ実装変更なし。
- t16は静止画の寸法/色形式/stillモード修正。全21テンプレートのCPU動画グラフ比較、4寸法×Bloom/帯DOFを検査。通常動画グラフ92ケースが前基準と同一。
- 直近スモーク：GUI起動/終了、1080p60、合成音声、h264_nvenc/libx264、OpenCL実行/CPU fallbackが成功。PATH FFmpegでも追加11件成功。
- 既定imageio FFmpeg7.1にはOpenCLがなくCPU FX＋NVENC。既存PATH FFmpegではGPU FX成功。旧「GPU FX未稼働」は全環境に共通する現在状態ではない。
- Native Helperはビルド/Usage確認まで。LoLプロセス限定収録・他アプリ音声除外はこの現行Windows基準で未検証。
- Pillow Image.getdata非推奨警告1件。現在のテスト停止原因ではない。

| 課題 | 現在の分類 |
|---|---|
| カメラv5.10.27 | 別ブランチ実装候補、現行へ未統合。修正後のLoL構図・RED3/5維持は未実機確認。 |
| 3テーマ透過 | 元画素試作保存済み、マスク手直し/視覚承認/アプリ合成未完了。残テーマへ未展開。 |
| A/B/C/D | 台帳/検証/計画部分あり。対応表、UI、保存、動画FXは未完了。 |
| スマート構図 | 距離/仰角の安全補正あり。実際の地形遮蔽、敵の見切れ、対象認識の解決を保証しない。 |
| 自動編集/モンタージュ | イベント由来のキーフレーム/見せ場選定あり。音楽ビート/敵位置/映像理解による高度編集が完成した証拠なし。 |
| 実機回帰 | Replay API、WGC、LoL音だけ、同期、HUD、TargetLock、全10カメラ、停止/ミラー復帰、長時間1080p60、37素材の実動画は現行基準で未検証。 |
| GPU品質/速度 | 短い合成テスト成功。全FX/全切替/長時間/実ゲームの性能・画質は未確定。 |
| 製品配布 | .exe/インストーラ完成の証拠なし。開発QA入口の最終製品での除去は将来工程。 |

旧チャットだけの判断、失われた私的動画の全フレーム解析、未アップロード診断からの原因確定、環境復元の未Publish設定を利用可能とする判断は補完しない。
過去のZIP/bundle SHAや復元手順はそのpayload用。現在98e736eを復元する保証には使わない。

## 8. ChatGPTとCodexの分担

| 担当 | 主な責任 |
|---|---|
| ChatGPT | 製品/UI/シーン/テンプレート設計、素材・見た目、カメラ構図の希望と実映像評価、弱/強/モチーフ/FXの承認材料。 |
| Codex | Windows環境、録画、LoL専用音声、GPU/FFmpeg/Replay APIの安定性、共有コアの安全修正、回帰・診断、素材/カメラの最終結線とパッケージ検証。 |
| ユーザー | 実リプレイ・同一イベントの評価、良好カメラ保護基準、素材視覚承認、統合開始/配布範囲の判断。 |

カメラ設計/見た目をChatGPT、実API・録画開始保証・共有core実装をCodexが協調して扱う。
`core/camera.py`, `jobs.py`, `effects.py`, `kill_icons.py`, `camera_clock.py`, `replay_api.py`, `capture*.py`, `audio*.py` は共有影響が大きい。
変更前に固定base/対象ファイル/目的/保持するAPI・設定キーを共有し、同じファイルを並行で古いZIPから上書きしない。
旧担当ガード/共有API JSONは参考。対象ref/blobが現在のものか再確認してから使用する。
この調査では他チャットへのメッセージ送信や別タスクの開始は行わない。

## 9. 次の安全な統合手順（提案、未着手）

1. **この引き継ぎを報告して一度停止する。** 次の統合はユーザーの開始指示を受けて別ブランチにする。main/PR29/旧候補を変更しない。
2. 98e736e（または本書だけを追加したその子）からカメラ専用ブランチを作る。現在の37/89素材、UI/保存、GPU/音声/録画、起動バッチ、t12/t16を保持対象として固定する。
3. 現行の同じリプレイ/対象/イベントでRED1〜5・BLUE6〜10の比較基準を採取する。VERSION、実バイトfingerprint、PRE/KILL/POST、MP4、ゲーム音/同期を記録。未検証基準を合格版と呼ばない。
4. 86443c9の局所差分とfa13295前提をレビューし、必要な軸/独立性/stale確認/録画前姿勢確認だけを現行のAPIへ移植する。19パス一括適用や269パス置換はしない。QA30MB化・包装・他GPU変更は独立要件として扱う。
5. 候補のgoldenをそのまま現在の真実としない。現行RED3/5の数値を固定し、候補の旧goldenとの差を説明する。10モード独立、stale、Zロール、yaw境界、低速API、姿勢未確認時の録画/音声非開始、t12安全top、停止/復帰をテストする。
6. Windowsの全pytest・総合16件・GUI/1080p60/合成音声/NVENC/OpenCL/CPUを再実行。その後、同一LoLシーンのRED3/5維持、RED1距離、RED2反転、RED4遮蔽、BLUE5種と冒頭0〜0.5秒を実動画で判定する。失敗時は理由付き中止/安全topを希望構図の合格にしない。
7. カメラの結果を独立コミット・報告し、素材は別ブランチで扱う。3テーマの黒/白/チェック柄/実ゲーム背景比較を目視承認し、RGB不変のアルファ手直しを先に確定する。承認前に残テーマへ展開しない。
8. 元ファイル名→theme_id/crop/肖像穴の明示マッピングを設計する。既存37キーと保存schemaを保護し、A/B/C/D UI・素材選択を実装してから静止画合成、CPU動画、GPU登場FXの順に結線する。追加x1/ロゴ/説明文字を動画へ勝手に描かない。
9. 実キラー/被害者肖像、イベント時刻、複数キル、弱/強/3モチーフ、OFF無影響、設定保存/再読込、37素材回帰、音声/カラー/1080p60/fallbackを確認。完成時のみ必要に応じフルZIP/差分ZIPを実際に作成しCRC/SHAを検証する。

## 10. ローカル再開の入口

現在のPythonは `.venv` の3.14.7。requirements＋pytest導入済み。3.12への切替はしていない。
環境再構築時は [WINDOWS_LOCAL_DEV_SETUP_20261014_JA.md](WINDOWS_LOCAL_DEV_SETUP_20261014_JA.md) を参照し、既存.venvを無断削除しない。
LoL_AutoCineフォルダで `START.bat`、既存PATH GPU FFmpegを使う場合は `START_LOCAL_GPU.bat`。
`START_GPU.bat` は未導入時に大容量FFmpeg取得の可能性があり、今回の調査では実行しない。
`RUN_TESTS.bat` は隔離コピーでpytest＋旧式総合を実行し、実LoL稼働中は拒否する。`--pytest-only` はpytestのみ。
Native Helperは `tools/bin/lol_audio_helper.exe`（Git除外）。別PCではビルド要件を確認する。管理者インストール/大容量取得は事前に確認する。

今回の完了条件：必須資料、Git履歴、現行/候補差分、89/37/3テーマの状態、未知事項、役割分担と統合手順を本書へ保存し、専用ブランチだけにPush。統合作業は開始しない。
