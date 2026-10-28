# 候補3／League Director／Lolnam Windows比較試験（2026-10-28）

## 正本と保護

- 候補3は `testA / T-A-M`。正本は `design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png`。C3-P/S、L03-N、R-A-mainと混同していない。
- Workの追加基準はコミット `d0523f43d911eea781451b91c01098393bd69e6f` の `three_ui_fidelity_20261027`。League Director＝R1 Track Desk（LD画像）、Lolnam＝R2 Shot Canvas（LN画像）。
- 旧候補3 HTML、7案比較版、従来UI、正式素材、mainは変更していない。追加2案は新規表示層。配布停止の研究デモの実行コードは取り込んでいない。

## 今回の実装

| UI | 骨格 | 実操作 | 差・制限 |
|---|---|---|---|
| 候補3 | 原画に沿う左準備／中央固定ミラー／右シーン表／下段編集・素材。10人、12行、カメラ3カード、数値4行、素材5枠を配置 | 既存AutoCineのリプレイ、スキャン、TargetLock、シーン、カメラ、素材・同名FX、ミラー、出力へ既存操作APIで接続。詳細・素材の往復 | オフラインなので映像・試合情報は実データ待ち。原画のゲーム画像や仮シーンを実接続表示として流用しない。文字・アイコン・素材欄の完全な見た目はREVIEW |
| League Director | 左シーン一覧／中央ミラー／右インスペクタ／下トラック | 上段8タブ、カメラ数値、素材・同名FX、ミラー・スキャン・出力など共通Appへ接続 | 原画の合成試合画像、密なキー編集、全画面別の装飾は未再現。キーは既存エディタへ開く導線 |
| Lolnam | 左ツールレール／中央ミラー／右インスペクタ／ショット列＋下トラック | 上段8タブと左レールの同一画面切替、カメラ数値、素材・同名FX、共通App接続 | 未スキャン時のショット列は空。原画の合成画像と複数詳細画面の見た目は未再現 |

3UIは同一の `UI29Server` と `Audit29Runtime` を使用する。UI切替でTk Appを再生成せず、既存の選択・素材・カメラ設定を保持する。追加2案の新規コードは `ui/reference_views.py`、`ui/reference_views.css`、`ui/reference_views.js`。BATで起動し、外部ブラウザを開かない。

## Windows証拠と判定

- 候補3：`qa/ui3_baseline_20261027/` に原画との50%重ね合わせ・差分・座標を保存。1672×941実画面の主要11領域はWork基準の±2px以内で **寸法PASS**。可変映像と文字・装飾を含む総合見た目は **REVIEW**。
- League Director／Lolnam：`qa/ui3_reference_20261027/` に1920×1080の実画面、LD/LN原画、50%重ね合わせ、差分を保存。各画面の総合見た目は **REVIEW**。原画の合成映像と未接続の実ミラーを同一画素の合否で扱わない。
- `qa/ui3_baseline_flow_20261027/index.json`：候補3のメイン→詳細→素材→メイン、カメラ距離、固定自動、素材・同名FX、弱FX、6登場アニメのうち左から、設定保持がオフラインWindows WebView2でPASS。
- `qa/ui3_reference_20261027/ld_flow.json` と `ln_flow.json`：各UIのカメラ距離変更、実素材と同名FX、別UIへの切替後の同一App状態保持がPASS。
- `tests/test_ui3_integration.py`、`test_ui29_runtime.py`、`test_ui29_desktop.py`：**28 passed、24 subtests passed**。localhostを使うため許可されたWindows環境で実行。
- Workの284件チェックリストを `WORK_ACCEPTANCE_284_ORIGINAL.json` として保存。`ACCEPTANCE_RESULTS_284.json` は **9 REVIEW、275 NOT_RUN、PASS 0、FAIL 0**。部分操作成功をケース全体の合格に繰り上げていない。

## 未接続・未検証

- 実LoLリプレイ接続、全試合スキャン、BLUE/RED全カメラ、上下反転、TargetLock実機、ミラー画質・FPS、NVENC、LoL音声、録画、1920×1080/60fps MP4、125%DPIは **NOT_RUN**。
- R1/R2のFOVキーフレーム直接編集、自由曲線、色調整の完全な画面内操作、全70機能の直接配置は未完了。既存エディタへの導線がある項目と直接操作を分けて扱う。
- R1/R2の元デザイン全20状態の忠実再現は未達。現在は各8タブを切り替えられるが、詳細タブの構成・装飾は原画像と差がある。次の詳細実装指示を受ける前に、元画像との差分をこの証拠で確認する。
- エンゲージ専用検出とベストショット選択は既存実装がなく、成功表示しない。

## 次の確認手順

1. `START_AUTOCINE_UI3.bat` をダブルクリック。候補3の画面を確認。
2. 下段タブの「Lolnam参考」「League Director参考」で切り替え。上部から候補3へ戻る。カメラ数値や素材の選択が残ることを確認。
3. 各参考UIの「カメラ」「素材」「出力」タブを操作。実LoL未接続なら映像・シーンを成功表示しないことを確認。
4. 実LoL、録画、GPU、音声、MP4の総合試験は次工程で実施し、284件台帳へ証拠を追加する。

この成果は比較試験版であり、候補3の正式採用や3UIの視覚合格、実LoLでの機能合格を示さない。
