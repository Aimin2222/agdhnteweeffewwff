# 3UI全画面実装仕様

36の画面/子画面契約を定義しました。メイン原画を作り直したものではありません。R1/R2の8主タブを残し、キー/FX/設定/診断は子画面として付随させます。C3は原画の3列と下段2モード・5タブ・タイムライン・素材3切替を維持します。C3-P/C3-Sへ置き換えません。

## 画面一覧

|ID|表示部|原画の有無|操作数|
|---|---|---|---|
|C3.main|C3下段5タブ内の専用section|C3_T-A-M_original.png|26|
|C3.easy|C3下段5タブ内の専用section|C3_T-A-M_original.png|20|
|C3.detail|C3下段5タブ内の専用section|C3_T-A-M_original.png|23|
|C3.camera|C3下段5タブ内の専用section|C3_T-A-M_original.png|25|
|C3.keys|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|22|
|C3.curve|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|22|
|C3.color|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|24|
|C3.effects|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|21|
|C3.material|C3下段5タブ内の専用section|C3_T-A-M_original.png|19|
|C3.export|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|21|
|C3.settings|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|18|
|C3.diagnostics|C3下段5タブ内の専用section|独立原画なし・追加子画面仕様|11|
|R1.main|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_main_dark_1920x1080.png, LD_main_light_1366x768.png, LD_main_light_1920x1080.png|26|
|R1.easy|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_easy_light_1920x1080.png|20|
|R1.detail|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_detail_light_1920x1080.png|23|
|R1.camera|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_camera_light_1920x1080.png|25|
|R1.keys|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|22|
|R1.curve|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_curve_light_1920x1080.png|22|
|R1.color|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_color_light_1920x1080.png|24|
|R1.effects|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|21|
|R1.material|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_material_light_1920x1080.png|19|
|R1.export|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LD_export_light_1920x1080.png|21|
|R1.settings|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|18|
|R1.diagnostics|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|11|
|R2.main|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_main_dark_1920x1080.png, LN_main_light_1366x768.png, LN_main_light_1920x1080.png|26|
|R2.easy|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_easy_light_1920x1080.png|20|
|R2.detail|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_detail_light_1920x1080.png|23|
|R2.camera|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_camera_light_1920x1080.png|25|
|R2.keys|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|22|
|R2.curve|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_curve_light_1920x1080.png|22|
|R2.color|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_color_light_1920x1080.png|24|
|R2.effects|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|21|
|R2.material|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_material_light_1920x1080.png|19|
|R2.export|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|LN_export_light_1920x1080.png|21|
|R2.settings|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|18|
|R2.diagnostics|右inspector内。主ナビ8タブは保持しkeys/effects/settings/diagnosticsは子画面|独立原画なし・追加子画面仕様|11|

## 寸法・部品

`specs/LAYOUT_AND_RESPONSIVE.json`にXYWHを保存。C3は原寸1672×941からの辺変換、R1/R2は1920基準です。`CONTROL_CONTRACTS.json`は全操作の入出力・保存・既存action/新adapterを定義、`NUMERIC_CONTRACTS.json`は単位/範囲/刻みを定義します。追加レイアウト値は実装用契約で、回収した原ベクター寸法ではありません。

R2 1366×768は縦予算を先に配分：header58+nav44+shotstrip37+timeline170+status26=335px、残433px以内にworkspaceと余白を収めます。映像539px固定を小画面へ持ち込まない。全flex/grid祖先にmin-height:0、inspectorとrail内部を独立scroll、transport56pxを必ず残します。1920では元の539px映像・下部位置を保持します。

## 配色と状態

`THEME_TOKENS.json`の文字/背景をinput、select、option、カード、popupにも同時に設定。primaryの文字色はlight白、dark濃紺。darkで白背景のnative optionへ白文字を継承させない。選択は色に加えてチェックと枠、disabledは理由と属性で示します。previewにCSS filterを掛けてテーマへ追従させない。元C3ライトの紺headerは別tokenで維持。

## ポップアップ

素材図鑑は検索・テーマ・正式/確認用フィルター・明暗背景・一時preview・適用/取消。640px幅を基準、最大高viewport−64px、内部だけscroll、背景操作を止め、Esc取消/Tab循環/元のfocusへ復帰。設定はdirty差分、適用/取消を分離。出力はnon-modal progressでpreviewを隠さず、取消と実ログを常設。警告は原因/影響/再試行条件、成功は実job完了後のみ。popupの自動適用は禁止。

## 操作と保存

同じAppを3UIで共有。未確定数値draftは入力中のpollで上書きしない。sceneを移る時だけ確定/破棄/取消の選択を表示。UI/theme切替はcamera命令、project初期化、再スキャン、録画開始を呼ばない。hoverでカメラや素材を勝手に確定しない。全入口が機能台帳へ到達できることをテストします。

## 初心者フロー

リプレイ選択→接続と対象確認→試合全体スキャン→シーン/出力チェック→おまかせ適用→プレビュー→MP4作成。既存接続済みなら準備操作を再要求しない。エラーは発生段へ戻し、設定を保持。詳細編集へいつでも往復可能。原画像のdensityを減らして巨大ホームへ変更しません。
