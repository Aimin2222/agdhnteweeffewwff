# UI受入チェックリスト

実装版未試験のため全件NOT_RUN。結果記入はspecs/UI_ACCEPTANCE_CHECKLIST.jsonへ。画像・数値・操作の証拠を伴わないPASSを付けません。

| ID | 分類 | 操作/確認 | 合格時の条件 | 結果 |
|---|---|---|---|---|
| ID01 | identity | 開発情報を取得 | candidate3/testA/T-A-Mと原画像SHA一致 | NOT_RUN |
| ID02 | identity | 候補2と新A Studioを開いて戻る | L03-N/R-A-mainを候補3の代替にしない | NOT_RUN |
| VIS01 | visual-original | 原本再現モードを原寸比較 | 3カラム役割、下部タブ・タイムライン・素材を維持 | NOT_RUN |
| VIS02 | visual-P | C3-P参照と同寸法で比較 | 専用のC3-P画像/JSONに合致 | NOT_RUN |
| VIS03 | visual-S | C3-S参照と同寸法で比較 | 専用のC3-S画像/JSONに合致 | NOT_RUN |
| VIS04 | visual-revision | 修正提案の有効版を記録 | 元画像との差分を改訂IDで列挙。未採用差分を原本一致扱いしない | NOT_RUN |
| PRE01 | preview | 左右/下部を各々スクロール | ミラーと再生列が固定 | NOT_RUN |
| PRE02 | preview | ミラー/演出の開始・停止を別々に操作 | 録画を開始せず、それぞれ実状態に一致 | NOT_RUN |
| PRE03 | preview | テーマ切替・詳細切替 | 映像色/セッション/時刻を保持 | NOT_RUN |
| SIZE01 | size | 1366×768の主画面/詳細/図鑑を表示 | 主要操作が到達可能、画面外への恒久見切れなし | NOT_RUN |
| SIZE02 | size | 100/125/150%DPIの証拠を取得 | DPI二重適用なし、狭幅時は明示ドロワー | NOT_RUN |
| SIZE03 | size | ミラー領域を測る | 原本派生の下限480×270目標とC3主画面640×360目標を混同せず記録 | NOT_RUN |
| THEME01 | theme | ライト/ダーク/Windows追従を順に選ぶ | 配置・編集値・選択・再生状態不変 | NOT_RUN |
| THEME02 | theme | 設定保存して再起動 | テーマ選択を保持、追従は指定時のみ | NOT_RUN |
| THEME03 | theme | 各テーマの選択/無効/警告を見る | 色以外の印・説明、主要文字と操作境界を確認 | NOT_RUN |
| SCR01 | scroll | 非フォーカス数値欄上でホイール | 意図せぬ値変更なし。ポインター下パネルだけスクロール | NOT_RUN |
| SCR02 | scroll | ドロワー/モーダル内でTabとホイール | フォーカス/背景操作が仕様に従う。閉じると起点に戻る | NOT_RUN |
| NUM01 | numeric | スライダーと数値欄を相互に変更 | 値・単位・有効範囲が同期 | NOT_RUN |
| NUM02 | numeric | 空欄/範囲外/不正入力/小数を入力 | 理由付き補正/拒否、確定前に予期せず送信しない | NOT_RUN |
| NUM03 | numeric | 手動48°とキー64°を切り替える | 入力元を明示、値を保持、現在補間値と選択キー値を区別 | NOT_RUN |
| KEY01 | keyframe | キーを追加/移動/削除/Undo | 時刻・値と実モデルが一致。重複時刻の方針を明示 | NOT_RUN |
| KEY02 | curve | 補間方式を変更・数値で時刻移動 | カーブがキーを通り、実評価値を表示。未実装は理由表示 | NOT_RUN |
| KEY03 | keyframe | キーをキーボードで操作 | 選択・移動・数値入力が可能 | NOT_RUN |
| ASSET01 | material | 正式/確認用/未審査/不採用を確認 | 区分はカタログ実値、承認変更なし | NOT_RUN |
| ASSET02 | material | 図鑑で一時選択→キャンセル→適用 | キャンセルで元に戻り、適用範囲だけ更新 | NOT_RUN |
| ASSET03 | material | 枠/FX/6アニメを切り替える | 別の能力・区分として接続、枠の承認をFXに継承しない | NOT_RUN |
| MODE01 | mode | 簡単→詳細→簡単 | シーン・キー・素材・チェック・時刻・TargetLockを保持 | NOT_RUN |
| MODE02 | mode | プリセット後に数値を変更 | カスタム表示、Undo、キーを無言で削除しない | NOT_RUN |
| SCENE01 | scene | 行選択と出力チェックを別々に変更 | 焦点と対象集合が独立 | NOT_RUN |
| STATE01 | state | ドラフト変更→別シーンへ移動 | 適用/破棄/戻るがあり誤適用なし | NOT_RUN |
| BTN01 | controls | 全表示ボタンを列挙して各起点で操作 | 孤立/空操作なし。無効は理由と必要条件を表示 | NOT_RUN |
| BTN02 | controls | スキャン/録画実行中に連打 | 二重ジョブなし、操作競合の理由を表示 | NOT_RUN |
| BEGIN01 | beginner | 初心者フロー6段階を1周する | 迷子にならずMP4作成まで到達。未接続は開始しない | NOT_RUN |
| BACK01 | backend | 実LoL環境でBLUE/REDとTargetLockを確認 | 実サイド・追従対象が正しい。模擬成功を使わない | NOT_RUN |
| BACK02 | backend | NVENC/CPU・LoLゲーム音で書き出す | 実出力とログで確認。無音/失敗は合格にしない | NOT_RUN |
| REG01 | regression | 既存候補・原本・承認状態を照合 | 1〜10/混合7＋4/R1/R2を保持、main無変更 | NOT_RUN |
| FN-REPLAY | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | Replay API接続：接続先・リプレイ状態と10人取得を実結果で表示。設定準備と実接続成功を分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-LAUNCH | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | ROFL起動・最近のリプレイ：接続先・リプレイ状態と10人取得を実結果で表示。設定準備と実接続成功を分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-PLAYER | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | 対象プレイヤー固定：選択プレイヤーIDを保持。BLUE/REDは実サイド。テーマ切替で解除しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-SCAN | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | 試合全体スキャン：進捗・失敗・キャンセルを処理から購読。押下直後に成功を表示しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-ASSIST | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | キル／アシスト／両方：キル／アシスト／キル＋アシスト。絞込と出力チェックを別管理。 未対応時は理由を表示。 | NOT_RUN |
| FN-MULTI | 70-feature | 詳細編集 > シーン/出力 > 対象・連続処理を開き操作する | 連続キル判定：安定シーンIDを共有。行の選択と書き出しチェックを別にする。 未対応時は理由を表示。 | NOT_RUN |
| FN-SCENE | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | シーン編集・保存：簡単／詳細と候補切替で値を初期化しない。画像の分割／削除は既存機能との意味を明示して実装。 未対応時は理由を表示。 | NOT_RUN |
| FN-TIMELINE | 70-feature | 詳細編集 > タイムライン > キー/カーブを開き操作する | シーンタイムライン：イベント選択と前後トリム1〜15秒・0.5秒刻み。4トラックは自由な多重動画編集エンジンを意味しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-KEYFRAME | 70-feature | 詳細編集 > タイムライン > キー/カーブを開き操作する | 相対yaw/zoom/FOVキーフレーム：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-HIGHLIGHT | 70-feature | 詳細編集 > シーン/出力 > 対象・連続処理を開き操作する | 既存おまかせ演出：対象1件／チェック分／全検出を明示。標準とスマートを選別。演出確認と録画を書き分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-SMARTMONTAGE | 70-feature | 詳細編集 > シーン/出力 > 対象・連続処理を開き操作する | 既存シーン採点・並べ替え：対象1件／チェック分／全検出を明示。標準とスマートを選別。演出確認と録画を書き分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-HUD | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | HUD非表示・復元：ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 未対応時は理由を表示。 | NOT_RUN |
| FN-MIRROR | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | ミラー・表示FPS：既存WGCの同一セッションを表示。未接続は明示。静止イラストで実接続成功を装わない。目標Hzと実測FPSを分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAPTURE | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | WGC/共有メモリ取得：既存WGCの同一セッションを表示。未接続は明示。静止イラストで実接続成功を装わない。目標Hzと実測FPSを分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-RECORD | 70-feature | 詳細編集 > 出力 > 作成内容確認 > 実録画を開き操作する | 録画・時刻整合：設定方針と実際に使用したエンコーダを区別。NVENC成功は実ログ・出力で検証。 未対応時は理由を表示。 | NOT_RUN |
| FN-JOB | 70-feature | 詳細編集 > シーン/出力 > 対象・連続処理を開き操作する | チェック済み・複数クリップ作成：対象1件／チェック分／全検出を明示。標準とスマートを選別。演出確認と録画を書き分ける。 未対応時は理由を表示。 | NOT_RUN |
| FN-AUDIO | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | LoLプロセス専用録音：ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 未対応時は理由を表示。 | NOT_RUN |
| FN-AUDIOGUARD | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | 音声必須時の失敗伝播：ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 未対応時は理由を表示。 | NOT_RUN |
| FN-BGM | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | BGMミックス・音量：ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 未対応時は理由を表示。 | NOT_RUN |
| FN-NVENC | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | GPUエンコード・CPU代替：設定方針と実際に使用したエンコーダを区別。NVENC成功は実ログ・出力で検証。 未対応時は理由を表示。 | NOT_RUN |
| FN-GPUFX | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | OpenCL全体FX経路：設定方針と実際に使用したエンコーダを区別。NVENC成功は実ログ・出力で検証。 未対応時は理由を表示。 | NOT_RUN |
| FN-GRADE | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | 16グレード・LUT・カーブ：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FOG | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | ゲーム内Fog：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-DOF | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | ゲーム内DOFと後段焦点表現：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-PULSE | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | キル時ハイライト：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-BADGE | 70-feature | 詳細編集 > 素材/登場アニメ > 図鑑を開き操作する | 既存37キルバッジ：Work652候補と分離。89原本と37バッジの素材は変更禁止。 未対応時は理由を表示。 | NOT_RUN |
| FN-WORKFRAME | 70-feature | 詳細編集 > 素材/登場アニメ > 図鑑を開き操作する | Workフレーム候補：参照時点は正式合格No.083/a_simple_mainの1件、確認用651件。実装時はカタログ実値を表示。 未対応時は理由を表示。 | NOT_RUN |
| FN-WORKFX | 70-feature | 詳細編集 > 素材/登場アニメ > 図鑑を開き操作する | Workエフェクト候補：35点はすべて確認用。枠合格を同名FXに継承しない。確認用使用チェックは承認ではない。 未対応時は理由を表示。 | NOT_RUN |
| FN-MOTION | 70-feature | 詳細編集 > 素材/登場アニメ > 図鑑を開き操作する | 登場アニメ6種：instant／slide_left／slide_right／slide_up／slide_down／pop。popは既存の横方向減衰位置ずれ。未実装の拡縮等を追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-REFERENCE | 70-feature | 詳細編集 > 素材 > 参考画像・局所抽出（既存能力の範囲）を開き操作する | 参考映像の局所特徴抽出：既存保存形式を保持。プリセット適用は明示操作。テーマや候補切替では適用しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-PREVIEW | 70-feature | 詳細編集 > シーン/接続状態を開き操作する | 近似プレビューと厳密静止画：録画しない確認操作。stop_ev共用があるため録画中の停止競合を実装段階で検証する。 未対応時は理由を表示。 | NOT_RUN |
| FN-MONTAGEFX | 70-feature | 詳細編集 > 色・FX > 連続キル/トランジションを開き操作する | 連結後の明暗トランジション：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-SELFQA | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | 既存自己診断：一括QAは動画・診断ZIPを作る。未実行・失敗・合格・要確認を実データで表示。 未対応時は理由を表示。 | NOT_RUN |
| FN-DIAG | 70-feature | 詳細編集 > 出力/テスト結果 > 基本設定・診断を開き操作する | 性能診断・QAパッケージ：一括QAは動画・診断ZIPを作る。未実行・失敗・合格・要確認を実データで表示。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_third_cinema | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | third_cinema：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_third | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | third：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_geo_aim | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | geo_aim：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_cinema | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | cinema：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_fps | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | fps：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_orbit | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | orbit：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_lolnam_cinema | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | lolnam_cinema：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_follow | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | follow：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_cinema_top | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | cinema_top：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-CAM_top | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | top：third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 未対応時は理由を表示。 | NOT_RUN |
| FN-FIXED | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | 固定自動：manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 未対応時は理由を表示。 | NOT_RUN |
| FN-FULL | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | フルオートシネマ：manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_motion_camera | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | motion_camera：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_radial_blur | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | radial_blur：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_zoom_blur | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | zoom_blur：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_glitch | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | glitch：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_kaleidoscope | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | kaleidoscope：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_vhs_damage | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | vhs_damage：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_block_motion | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | block_motion：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_spin_motion | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | spin_motion：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_chroma_leak | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | chroma_leak：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_flash | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | flash：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_focus_blur | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | focus_blur：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_vignette_fx | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | vignette_fx：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_glint | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | glint：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_camera_shake | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | camera_shake：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_wiggle | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | wiggle：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_vr_blur | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | vr_blur：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_vr_light_leak | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | vr_light_leak：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_sphere_blur | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | sphere_blur：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_panel_wipe | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | panel_wipe：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_stretch_wipe | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | stretch_wipe：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_mirror | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | mirror：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-FX_slice | 70-feature | 詳細編集 > カメラ または 色・FX > 専用設定を開き操作する | slice：CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 未対応時は理由を表示。 | NOT_RUN |
| FN-ENGAGE | 70-feature | 詳細編集 > テスト結果 > 研究・未対応機能（説明のみ）を開き操作する | エンゲージ独立検出：参照UIの対応モード・専用ハンドラーは確認できない。killへ偽装接続しない。能力がない時は「エンゲージ未対応」を説明付き表示。全案の受入は実能力追加後に別検証。 未対応時は理由を表示。 | NOT_RUN |
| FN-BESTSHOT | 70-feature | 詳細編集 > テスト結果 > 研究・未対応機能（説明のみ）を開き操作する | 画像品質によるベストショット選択：一括QAは動画・診断ZIPを作る。未実行・失敗・合格・要確認を実データで表示。 未対応時は理由を表示。 | NOT_RUN |
