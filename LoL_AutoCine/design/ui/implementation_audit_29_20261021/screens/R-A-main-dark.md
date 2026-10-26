# R-A-main-dark — 新A Studio

原本：[A_main_dark.png](../references/research/A_main_dark.png)。原寸 1920×1080。論理基準 1920×1080。テーマ `dark`。ルート `/candidates/researchA/R-A-main-dark`。採用未決定。

SHA-256 `0f3483147495cf360de5106e9da6c5bdb7a7bbbf06caf2f206ca007a6cc04664`

元HTMLのリンクは資料用。候補間へ飛ぶリンクは実装にコピーせず、この候補内の対応状態へ結ぶ。

## 座標・測定の根拠

deterministic DOM; fractional native pixels retained。原点はクライアント描画領域左上。矩形は [x,y,width,height]。OSの外枠は加算しない。

原本→論理座標：X×1.000000000、Y×1.000000000。旧PNGはリサイズせず保存。旧原本にない正確なフォント名・制約値を復元できたとは扱わない。

## パネル配置・固定／スクロール

| 領域 | 意味 | x | y | 幅 | 高さ | 表示 |
|---|---|---:|---:|---:|---:|---|
| header | 上部バー／出力・基本設定 | 0 | 0 | 1920 | 76 | 固定／親領域に従う |
| theme-switch | テーマ選択 | 1207.58 | 17.5 | 163 | 40 | 固定／親領域に従う |
| export | 動画作成 | 1640.77 | 17.5 | 92.8281 | 40 | 固定／親領域に従う |
| subbar | 画面タブ／操作案内 | 0 | 76 | 1920 | 64 | 固定／親領域に従う |
| workspace | 作業領域 | 0 | 140 | 1920 | 908 | 固定／親領域に従う |
| scene-list | 検出シーン・スキャン | 24 | 156 | 264 | 650 | この内部だけスクロール |
| scene-card-0 | scene-card-0 | 45 | 351 | 222 | 88 | 固定／親領域に従う |
| scene-card-1 | scene-card-1 | 45 | 449 | 222 | 88 | 固定／親領域に従う |
| scene-card-2 | scene-card-2 | 45 | 547 | 222 | 88 | 固定／親領域に従う |
| scene-card-3 | scene-card-3 | 45 | 645 | 222 | 88 | 固定／親領域に従う |
| scene-card-4 | scene-card-4 | 45 | 743 | 222 | 88 | 固定／親領域に従う |
| scene-card-5 | scene-card-5 | 45 | 841 | 222 | 88 | 固定／親領域に従う |
| preview-panel | 固定ミラーパネル | 304 | 156 | 1200 | 650 | 固定／親領域に従う |
| preview-stage | ライブ映像の表示面 | 321 | 215 | 1166 | 490.5 | 固定／親領域に従う |
| preview-controls | ミラー／演出の操作 | 321 | 717.5 | 1166 | 44 | 固定／親領域に従う |
| inspector | 設定（独立スクロール） | 1520 | 156 | 376 | 650 | この内部だけスクロール |
| camera-modes | 既存／固定自動／フルオート | 1541 | 256.5 | 334 | 241 | 固定／親領域に従う |
| slider-third_dist | slider-third_dist | 1541 | 655 | 334 | 36 | 固定／親領域に従う |
| slider-cam_height | slider-cam_height | 1541 | 707 | 334 | 36 | 固定／親領域に従う |
| slider-third_yaw | slider-third_yaw | 1541 | 759 | 334 | 36 | 固定／親領域に従う |
| timeline | 固定タイムライン／トリム | 24 | 822 | 1872 | 210 | 固定／親領域に従う |
| trim | 前後トリム | 45 | 954 | 1830 | 36 | 固定／親領域に従う |
| footer-22 | footer-22 | 0 | 1048 | 1920 | 32 | 固定／親領域に従う |
中央映像と再生列はスクロール祖先に入れない。表の子部品が画面外でも、親スクロール内なら配置ミスではない。初期スクロール位置は0。
実映像16:9のcontain矩形：`[468.0, 215.0, 872.0, 490.5]`。外側表示面と区別する。元の説明イラストの画角を実LoLへ強制しない。


## 操作部品・動作・接続先
Fxxは共通機能対応、NAVは候補内遷移。各部品の動作は同じ状態モデルへ接続する。
| 部品ID | ラベル | x,y,w,h | 接続 | 押下／変更時の動作 |
|---|---|---|---|---|
| R-A-main-dark-C000 | 配色モード | 1207.5781,17.5,163,40 | F25 | light / dark / systemを保存。状態は同じモデルから購読し、バックエンド再生成をしない。 |
| R-A-main-dark-C001 | リプレイを開く | 1380.5781,17.5,100.3281,40 | F01 | 接続先・リプレイ状態と10人取得を実結果で表示。設定準備と実接続成功を分ける。 |
| R-A-main-dark-C002 | 基本設定 | 1490.9062,17.5,82,40 | F22 | ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 |
| R-A-main-dark-C003 | ログ | 1582.9062,17.5,47.8594,40 | F24 | 一括QAは動画・診断ZIPを作る。未実行・失敗・合格・要確認を実データで表示。 |
| R-A-main-dark-C004 | 動画を作成 | 1640.7656,17.5,92.8281,40 | F23 | 対象1件／チェック分／全検出を明示。標準とスマートを選別。演出確認と録画を書き分ける。 |
| R-A-main-dark-C005 | メイン | 1552.375,86.5,63.4688,42 | NAV | 同じ候補内のmainへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C006 | Studio編集 | 1621.8438,86.5,107.2031,42 | NAV | 同じ候補内のstudioへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C007 | カメラ | 1735.0469,86.5,62.9531,42 | NAV | 同じ候補内のcameraへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C008 | 素材図鑑 | 1804,86.5,92,42 | NAV | 同じ候補内のframesへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C009 | ⌕ 試合全体をスキャン | 45,221,222,40 | F03 | 進捗・失敗・キャンセルを処理から購読。押下直後に成功を表示しない。 |
| R-A-main-dark-C010 | キル | 45,304,44.6406,35 | F04 | イベント／プレイヤー／カテゴリの該当フィルターだけを変更し、チェック集合を保持。 |
| R-A-main-dark-C011 | アシスト | 95.6406,304,63.4219,35 | F04 | イベント／プレイヤー／カテゴリの該当フィルターだけを変更し、チェック集合を保持。 |
| R-A-main-dark-C012 | 両方 | 165.0625,304,48,35 | F04 | イベント／プレイヤー／カテゴリの該当フィルターだけを変更し、チェック集合を保持。 |
| R-A-main-dark-C013 | ✓12:34BLUEトリプルキル | 45,351,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C014 | ✓ | 59,384,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C015 | ✓15:02REDキル | 45,449,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C016 | ✓ | 58,482,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C017 | ✓18:21BLUEアシスト | 45,547,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C018 | ✓ | 58,580,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C019 | ✓22:10REDダブルキル | 45,645,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C020 | ✓ | 58,678,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C021 | 26:48BLUEキル | 45,743,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C022 |  | 58,776,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C023 | 30:12REDアシスト | 45,841,222,88 | F06 | 安定シーンIDを現在選択に設定。実時刻・プレビュー・詳細へ反映。 |
| R-A-main-dark-C024 |  | 58,874,22,22 | F07 | このシーンの出力チェックだけを切替。行選択やカメラ値を変更しない。 |
| R-A-main-dark-C025 | 選択シーンへ移動 | 45,962,222,40 | F06 | 安定シーンIDを共有。行の選択と書き出しチェックを別にする。 |
| R-A-main-dark-C026 | ▶ 演出を確認 | 321,719.5,110.6719,40 | F09 | 録画しない確認操作。stop_ev共用があるため録画中の停止競合を実装段階で検証する。 |
| R-A-main-dark-C027 | ■ 停止 | 441.6719,719.5,71.8594,40 | F09 | 録画しない確認操作。stop_ev共用があるため録画中の停止競合を実装段階で検証する。 |
| R-A-main-dark-C028 | ミラー開始 | 1313,719.5,82,40 | F08 | 既存WGCの同一セッションを表示。未接続は明示。静止イラストで実接続成功を装わない。目標Hzと実測FPSを分ける。 |
| R-A-main-dark-C029 | ミラー停止 | 1405,719.5,82,40 | F08 | 既存WGCの同一セッションを表示。未接続は明示。静止イラストで実接続成功を装わない。目標Hzと実測FPSを分ける。 |
| R-A-main-dark-C030 | 従来の手動カメラ選んだスタイルと数値を使用 | 1541,256.5,334,73 | F10 | manual / fixed_auto / full_autoを選択。None（既存維持）の経路も保持。 |
| R-A-main-dark-C031 | 固定視点＋自動構図補正視点を保ち、構図を補正 | 1541,339.5,334,75 | F10 | manual / fixed_auto / full_autoを選択。None（既存維持）の経路も保持。 |
| R-A-main-dark-C032 | フルオートシネマ確認済み候補のみ。候補なしは固定視点 | 1541,424.5,334,73 | F10 | manual / fixed_auto / full_autoを選択。None（既存維持）の経路も保持。 |
| R-A-main-dark-C033 | ◉ 自動 | 1541,566,84.4062,42 | F10 | manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 |
| R-A-main-dark-C034 | BLUE | 1633.4062,567,67.0156,40 | F10 | manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 |
| R-A-main-dark-C035 | RED | 1708.4219,567,59.7188,40 | F10 | manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 |
| R-A-main-dark-C036 | 距離 | 1801,655,76,36 | F12 | 同じ設定変数へ数値を入力。既存の範囲と刻みで検証しスライダーを同期。 |
| R-A-main-dark-C037 | 高さ | 1801,707,76,36 | F12 | 同じ設定変数へ数値を入力。既存の範囲と刻みで検証しスライダーを同期。 |
| R-A-main-dark-C038 | 回転角 | 1801,759,76,36 | F12 | 同じ設定変数へ数値を入力。既存の範囲と刻みで検証しスライダーを同期。 |
| R-A-main-dark-C039 | カメラを詳しく設定 | 1541,828,334,40 | NAV | 同じ候補内のcameraへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C040 | 枠・FX・登場を画像で選ぶ | 1541,926.5,334,40 | NAV | 同じ候補内のframesへ遷移。project・selectedScene・mirrorを継続。 |
| R-A-main-dark-C041 | キル前 | 93.0781,954,76,36 | F17 | 同じ設定変数へ数値を入力。既存の範囲と刻みで検証しスライダーを同期。 |
| R-A-main-dark-C042 | キル後 | 1773,954,76,36 | F17 | 同じ設定変数へ数値を入力。既存の範囲と刻みで検証しスライダーを同期。 |

## 配色・寸法・共通部品
全操作部品の色・文字・枠・角丸は `SCREENS_29.json` の該当IDの `controls[].style`、旧画面は `component_contract_native` と `observed_neutral_palette`。[共通仕様](../COMPONENTS_AND_THEMES_JA.md) と併用。旧パレットは原画サンプル、テーマトークンは新規テーマの仕様であり混同しない。
## 合格条件
1. このIDの原本・原寸・スクロール状態で比較。別候補のレイアウトで代替しない。
2. 主パネル、映像表示面、操作列、左右列、下部ドックを重ね合わせる。新画面は各辺±2px、旧ラスタ再構成は各辺±8原画pxを初回許容範囲とし、差分を記録する。8pxはピクセル一致の主張ではない。
3. 部品の順序、タブ選択、列数、カード枚数、主要ラベルを一致させる。文字や操作を消して一致率を上げない。
4. 生きた映像・実カタログ画像・時刻・実測値は比較除外領域を明示する。UIの枠や操作部品は除外しない。
5. 全F01〜F25へ到達できる。同じ状態モデルで実接続、スキャン、TargetLock、録画、音声、書き出しを確認。未対応F05は未合格として残す。
6. テーマ／候補／簡単詳細／ウィンドウ寸法を変更し、選択シーン、カメラ値、プロジェクト、プレビューセッションが保たれる。
7. この画面の未提供のダーク版・補助タブは派生実装。別の参照画像IDを勝手に増やして29件の判定を置換しない。

## 個別の文字・枠・色・角丸

| 部品ID | 文字px／行高 | 余白 | 枠 | 角丸 | 背景 | 文字色 |
|---|---|---|---|---|---|---|
| R-A-main-dark-C000 | 14px / normal | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C001 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C002 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C003 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C004 | 14px / 21px | 7px 12px | 1px solid rgb(155, 198, 255) | 7px | rgb(155, 198, 255) | rgb(19, 36, 59) |
| R-A-main-dark-C005 | 16px / 24px | 9px 14px | 0px none rgb(155, 198, 255) | 7px | rgb(52, 77, 107) | rgb(155, 198, 255) |
| R-A-main-dark-C006 | 16px / 24px | 9px 14px | 0px none rgb(177, 192, 208) | 7px | rgba(0, 0, 0, 0) | rgb(177, 192, 208) |
| R-A-main-dark-C007 | 16px / 24px | 9px 14px | 0px none rgb(177, 192, 208) | 7px | rgba(0, 0, 0, 0) | rgb(177, 192, 208) |
| R-A-main-dark-C008 | 16px / 24px | 9px 14px | 0px none rgb(177, 192, 208) | 7px | rgba(0, 0, 0, 0) | rgb(177, 192, 208) |
| R-A-main-dark-C009 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C010 | 14px / 21px | 5px 9px | 2px solid rgb(155, 198, 255) | 7px | rgb(52, 77, 107) | rgb(237, 242, 247) |
| R-A-main-dark-C011 | 14px / 21px | 5px 9px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C012 | 14px / 21px | 5px 9px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C013 | 16px / 24px | 12px | 2px solid rgb(155, 198, 255) | 8px | rgb(52, 77, 107) | rgb(237, 242, 247) |
| R-A-main-dark-C014 | 16px / normal | 0px | 2px solid rgb(155, 198, 255) | 4px | rgb(155, 198, 255) | rgb(19, 36, 59) |
| R-A-main-dark-C015 | 16px / 24px | 12px | 1px solid rgb(70, 85, 104) | 8px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C016 | 16px / normal | 0px | 2px solid rgb(155, 198, 255) | 4px | rgb(155, 198, 255) | rgb(19, 36, 59) |
| R-A-main-dark-C017 | 16px / 24px | 12px | 1px solid rgb(70, 85, 104) | 8px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C018 | 16px / normal | 0px | 2px solid rgb(155, 198, 255) | 4px | rgb(155, 198, 255) | rgb(19, 36, 59) |
| R-A-main-dark-C019 | 16px / 24px | 12px | 1px solid rgb(70, 85, 104) | 8px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C020 | 16px / normal | 0px | 2px solid rgb(155, 198, 255) | 4px | rgb(155, 198, 255) | rgb(19, 36, 59) |
| R-A-main-dark-C021 | 16px / 24px | 12px | 1px solid rgb(70, 85, 104) | 8px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C022 | 16px / normal | 0px | 2px solid rgb(141, 161, 185) | 4px | rgba(0, 0, 0, 0) | rgb(237, 242, 247) |
| R-A-main-dark-C023 | 16px / 24px | 12px | 1px solid rgb(70, 85, 104) | 8px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C024 | 16px / normal | 0px | 2px solid rgb(141, 161, 185) | 4px | rgba(0, 0, 0, 0) | rgb(237, 242, 247) |
| R-A-main-dark-C025 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C026 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C027 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C028 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C029 | 14px / 21px | 7px 12px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C030 | 16px / 24px | 12px | 1px solid rgb(141, 161, 185) | 8px | rgba(0, 0, 0, 0) | rgb(237, 242, 247) |
| R-A-main-dark-C031 | 16px / 24px | 12px | 2px solid rgb(155, 198, 255) | 8px | rgb(52, 77, 107) | rgb(237, 242, 247) |
| R-A-main-dark-C032 | 16px / 24px | 12px | 1px solid rgb(141, 161, 185) | 8px | rgba(0, 0, 0, 0) | rgb(237, 242, 247) |
| R-A-main-dark-C033 | 16px / 24px | 7px 14px | 2px solid rgb(155, 198, 255) | 7px | rgb(52, 77, 107) | rgb(237, 242, 247) |
| R-A-main-dark-C034 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C035 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C036 | 15px / normal | 5px 8px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C037 | 15px / normal | 5px 8px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C038 | 15px / normal | 5px 8px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C039 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C040 | 16px / 24px | 7px 14px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C041 | 15px / normal | 5px 8px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |
| R-A-main-dark-C042 | 15px / normal | 5px 8px | 1px solid rgb(141, 161, 185) | 7px | rgb(37, 47, 60) | rgb(237, 242, 247) |


## 映像の最小値と変形

ライブ映像は論理480×270を下限の目標とし、表示面に16:9でcontain。下回る有効領域では、この候補内で左右ペインをタブまたはドロワーへ畳む。別候補へ切替しない。原画にない再配置は派生状態として記録する。
