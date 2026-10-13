# LoL AutoCine — 最新完全引き継ぎ書 v5.10.26（2026-10-13・新しいChatGPTチャット向け）

> **重要な事実**：この文書は、これまでに確認できたユーザー発言・画像による評価・開発仕様・GitHubコード・テストログ・既存引き継ぎ書を総合した**実務上の包括的引き継ぎ書**。文字どおり過去全会話の逐語録ではない。チャット履歴の全発言や添付MP4のバイト列をこのMarkdownに復元することはできない。「一言一句抜けなく」を文字どおり満たすには、元ChatGPT会話のエクスポートや原資料も新チャットに渡す必要がある。事実・推測・未確認・過去時点の内容を明確に区別すること。

## 0. 新しいチャットへの最優先指示
1. ユーザーへの説明は日本語。最初に**本書の全文**、過去の2本の旧ハンドオフ（2026-10-09/10-11）、2026-10-12の包括的ハンドオフ、現行v5.10.26実装仕様、AGENTS.mdと最新ソースを順番に読む。
2. **テストの基準は v5.10.26-test**。v5.10.25やv5.10.23の比較画像を最新版の結果だと断定しない。ZIPを別フォルダーに展開しVERSION.txtとresults.jsonに記録されたversion/installed_versionを照合する。
3. ユーザーは**新しいチャットでWindows実機テストを行う予定**。最初は、ユーザーが送る画像・動画・results.json・診断ログ・分割ZIPを受け取る。ユーザーが**「完了」**と言うまでは解析・開発・GitHub変更・ZIP作成を開始しない。途中のファイルを根拠に早まった修正をしない。
4. 別チャットでは以前Pythonやコンテナが InvalidArgumentError / ClientError で止まった。新チャットでまず**本当にPythonツールを呼んで print("test") を実行する**。ただのコード表示を成功と誤認しない。次に添付の小さいMP4をFFprobe/FFmpegで実際にデコードしフレームを抽出できるか検証。失敗したら原因の断定や「見たふり」をしない。
5. ユーザーが「完了」と告げた後、素材をまとめて読み、RED/BLUE各カメラの変化・空/マップ外・動画切替・音声・GPU・バージョン不一致を解析し、必要な修正版の開発を始める。
6. 現行の良い構図やGPU Full、LoL専用音声、HUD、ミラー、TargetLock、UI設定保存を勝手に壊さない。実行不能なツールや取り込めない動画があれば、未検証と明記する。
7. 修正後は**Windows用フル版ZIP**と**Codex統合用差分ZIP**を**別々**に配布（二重ZIPなし）。テスト数・失敗数・Windowsで確認してほしい項目・修正範囲・未確認事項をセットにする。

## 1. GitHub、正しいバージョン、実在のダウンロード
- リポジトリ：https://github.com/Aimin2222/agdhnteweeffewwff
- アプリの正確なルート：LoL_AutoCine/。ほかの静的サイト等のファイルやmainへ無関係な変更を加えない。
- **現行テスト版**：v5.10.26-test。
- **コードの本流**：autocine/v5.10.26-stale-qa-sky-detection-releasefix
- **実在コミット**：bec275d4655c09ce674260efe7cadc755d370de6
- **修正版GitHub Release**：https://github.com/Aimin2222/agdhnteweeffewwff/releases/tag/autocine-v5.10.26-test-bec275d465
- Windows用フルZIP（67,031,740 bytes）：
  https://github.com/Aimin2222/agdhnteweeffewwff/releases/download/autocine-v5.10.26-test-bec275d465/LoL_AutoCine_v5.10.26_Windows_Test_Full.zip
  SHA256: 8bd7f580e95b0d4e4959a30fdf624f743a7c47c7063b8bba3b2452751ce30a43
- Codex統合用累積差分ZIP（88,222 bytes）：
  https://github.com/Aimin2222/agdhnteweeffewwff/releases/download/autocine-v5.10.26-test-bec275d465/LoL_AutoCine_v5.10.26_Codex_MergeChanges.zip
  SHA256: b2b4186b9b2f691cbf3e36c67b508e46d2869dd20299d9370da63db8e26c1a2d
- **最終成功CI**：https://github.com/Aimin2222/agdhnteweeffewwff/actions/runs/38290644252
  Windows job success。Linux GUI Xvfb回帰テスト **644 passed / 0 failed**（7バッチ 85+153+111+109+79+58+49）。構文・文字コード、Codex差分適用・ZIP CRC/SHA・Windows BAT MP4/フォルダー/日本語名/動画ZIP/壊れたZIPまで成功。
- 成功は**コードと自動テスト、人工短尺MP4の確認**であり、ユーザーのWindows LoLでの新しいカメラ構図、音声品質、NVIDIA負荷は**まだ実機未確認**。
- 本ハンドオフは**別の文書専用ブランチ** autocine/handoff-v51026-20261013-new-chat に置く。そこに書類を保存したことで配布アプリのSHAや挙動が変更されたわけではない。新チャットは必ず上記v5.10.26の本流ソースを使う。

## 2. 複数ブランチの混在に関する重大な注意
- 2026-10-13時点で、v5.10.25には少なくとも**2系列の実装**がある：
  1. autocine/v5.10.25-blue6-framing-reference-handoff：BLUE #6の角度X=-2.0。CI成功run 38276276450。これを基準に次のv5.10.26成功版を作成した。
  2. autocine/v5.10.25-blue6-vertical-frame-qa：別の試験枝でBLUE #6の角度X=-4.0。初期CIで古いテストがX=3.0を期待し失敗し、別CIでZIPを閉じた後にwriteし失敗。修正後の成功run 38289590821もあるが**現在配布するv5.10.26とは別系列**。
- 過去の失敗ログの「X=-4.0」は、**v5.10.26の実値ではない**。成功版v5.10.26のcore/camera_tuning.pyではBLUE thirdが距離1.10/角度X=-2.0。古い実行ログだけで数値を直さない。
- 過去のv5.10.23にも同一見かけの名前で違う複数のreleaseがあり、バージョン文字列だけでSHAや機能を同一扱いしない。
- 過去v5.10.15にはCodex GPU統合系とChatGPT UI/カメラ系が独立。パッケージを丸ごと上書きせず変更点を精査。
- 現行Codex GPU系：codex/lol-autocine-v51015-ui-scan-camera-handoff、元PR #29 https://github.com/Aimin2222/agdhnteweeffewwff/pull/29（確認時点open/draft、未マージ）。mainやCodex GPU側へ勝手にマージしない。
- CodexはGPU/NVENC・プロセス専用音声・録画安定化・Replay APIを重視。ChatGPTはUI/カメラ/演出/実機QAを中心に修正。core/camera.py、core/jobs.py等は共有なので差分レビューを必須とする。

## 3. ずっと守るアプリのコンセプトと完成条件
- ユーザーが求めるLoL AutoCine：LoLリプレイを選択し、キル/アシスト/エンゲージの見せ場を取得、選んだプレイヤーに固定して簡単にシネマ動画を生成するWindowsアプリ。最優先は「**誰でも簡単ワンクリック**」。
- 標準書き出しは**横型1920×1080、16:9、60fps**。144fpsでLoL録画できることと最終60fpsは別。縦型Shorts不要。
- LoL**ゲーム音だけ**収録する（Windows Native Process Loopback）。PCの他アプリ音声や全デスクトップ音声へ勝手に戻さない。音声の欠落/ずれがないか実機確認。
- GPU/NVENC優先。GPU Full/OpenCLエフェクトとNVENCエンコードは異なる。GPU効果が使えない環境では安全なCPUフォールバックを維持。書き出しが8倍速になる、ガクつく、GPUを使わないなど過去の問題を再発させない。
- TargetLock座標系、三人称追従、FPSフォールバック、BLUE/RED背面方向、Replay API経由のカメラ制御を残す。
- ミラー/プレビューは常時視認でき、再生/停止、スクロール固定、UIイベント応答を保つ。Qt/Python-Tk等をUIスレッド以外から直接触らない（現行TkinterではTk呼び出しはUIスレッドのみ）。
- キル検出だけでなくアシスト/エンゲージの選択、全キル一括/選択キル、検出種別フィルター、10人取得、スキャン済みキャッシュを残す。
- 一度全試合スキャンしたら、プレイヤーや検出種別（kill/assist/both）の切替で不必要に全試合を再スキャンしない。
- 主要FX、Premiere風トランジション、Kill前後のZoom/Flash/Slow、HUD設定、色/カーブ/FOG/DOF、詳細編集の保存/Undo/Redo、テンプレートを削除しない。

## 4. UIの詳細で過去に何度も要望されたこと
- UIは白基調（LoLnam風＋動画編集ソフト風）、日本語、初心者が見て分かる言葉。Orbitは「被写体の周囲を回る」、Dollyは「カメラが近づく」など説明やラベルを分かりやすく。簡単編集/詳細編集に意味を持たせる。
- スキャン入口は**右側の「スキャン」**に接続→10人取得→試合全体スキャンを集約。左側の重複する「接続して10人をスキャン」を不要にする方針。
- シーン選択チェックは鮮明なレ点。チェックがぼやけると指摘。検出シーンのチェック、シーンへ移動、一覧のスクロール領域は見切れさせない。
- コンボボックス/プルダウン操作時に後ろがスクロールしたり、ホイールで意図せず選択が変わるバグ、右側のスクロール感度低下を調整。キルフレーム図鑑表示時も後ろの画面をスクロールさせない。? の説明は約0.5秒ホバーで出す。
- ミラー固定、必要に応じて中央と右側の分割スクロール。UI操作中にプレビューが止まらないよう非同期で更新。色・エフェクト・テンプレート比較画面と出力結果が乖離しない。
- 簡単編集の**テンプレートA/Bボタンを消さない**。左側に独立していたテンプレート選択を簡単編集/詳細編集の適切な場所に統合。名称は分かりやすい日本語とスキンテーマ名。
- 簡単編集の「色味だけ細かく変更」は**チェックONで直下に数値とスライダーを展開**。以前ONにしても何も出なかったことがある。自動ディレクターONの強度スライダーも直下に表示する。スライダーの現在値・直接入力と出力先フォルダー選択ボタンを保つ。
- DOFは最初に**円形/従来方式のラジオボタン**を表示、選択した側のパラメータだけを下に展開。従来方式は図形を用いて何が変わるのか説明する。双方同時表示は不要。
- カメラモード（通常3人称/3人称シネマ/FPS/Lolnam）を連続2回押すと天地逆転する過去バグ。再選択でカメラ上限/ロールを破壊しない。
- 全体映像の自動ビネットで画面四隅が暗くなる問題があったため、ユーザーが色/エフェクトを設定しないときは**デフォルトの色・強制ビネットなし**を基本とする。HUDは全部シネマ非表示／HPバーは残し名前だけ非表示など柔軟に設定。
- 37種類のキルフレームは**LoLスキンテーマ風**の区別できるデザイン/名称。UI名をダサい連番にせず、分かりやすくする。実際のキャラクター肖像×相手肖像を使い、x1・余計な文字を載せない。PNG解像感のある装飾、イン/アウト動作は一気に出る、左/右から、下/上から等**6種類**。プレイヤーデータがdict/Player dataclassどちらでもクラッシュしない。
- 用意したプリセットは実際に見比べて違いが分かるようにする。見本が同じにしか見えない場合、色/強度だけ変えただけの類似品を水増ししない。
- 曲線エディタ、グラフのFOG補正、カーブ、カメラ高さ/フォーカス距離、シーン別保存を保持。高品質1080p/60固定、速度選択不要、ショート動画は不要。

## 5. カメラ10モードの厳密な対応関係
| 番号 | チーム | mode | 表示 |
|---|---|---|---|
| 1 | RED / CHAOS | third | 通常三人称 |
| 2 | RED / CHAOS | third_cinema | 三人称シネマ |
| 3 | RED / CHAOS | fps | FPS風 |
| 4 | RED / CHAOS | lolnam_cinema | Lolnam風シネマ |
| 5 | RED / CHAOS | geo_aim | 座標追従（実験） |
| 6 | BLUE / ORDER | third | 通常三人称 |
| 7 | BLUE / ORDER | third_cinema | 三人称シネマ |
| 8 | BLUE / ORDER | fps | FPS風 |
| 9 | BLUE / ORDER | lolnam_cinema | Lolnam風シネマ |
| 10 | BLUE / ORDER | geo_aim | 座標追従（実験） |

### v5.10.26で実際に確認できた個別補正設定
**注意**：これは現在のGitHubソースから読んだ数値。最新実機の良否を意味しない。REDはX/Yの扱いがBLUEと異なるルートがあるため、チームを跨いで同じEuler軸に単純に当てはめない。

| チーム / mode | distance | angles | fps_back |
|---|---:|---|---:|
| RED third | 1.13 | なし（ベクトル中央固定） | 1.0 |
| RED third_cinema | 0.96 | なし | 1.0 |
| RED fps | 1.0 | なし（ベクトル中央固定） | 1.60 |
| RED lolnam_cinema | 1.0 | X=-3.0°, Y=-3.0° | 1.0 |
| RED geo_aim | 1.12 | X=-4.0° | 1.0 |
| BLUE third | 1.10 | X=-2.0° | 1.0 |
| BLUE third_cinema | 1.08 | なし | 1.0 |
| BLUE fps | 1.0 | なし | 1.38 |
| BLUE lolnam_cinema | 1.08 | X=+2.5° | 1.0 |
| BLUE geo_aim | 1.08 | X=+2.5° | 1.0 |

- 実装の位置：core/camera_tuning.py の SHOT_TUNING、core/camera.py、core/jobs.py。
- カメラエンジン/Replay API/録画経路は共通。ただしモード×陣営ごとの数値とRED専用の中央固定フラグは隔離。**完全に10個の独立プログラムではない**。
- RED 1/3には v5.10.24で新設した target_center_rotation(offset) を実際の相対オフセットから適用。水平方位を atan2(-dx,-dz)、俯角を atan2(dy,hypot(dx,dz)) から計算しZロール=0。ユーザーの比較では以前のRED1/3の画面端問題が改善。ただしプレイヤーが中央に必ず写ることを数学だけで証明できない。
- RED 2/4/5は過去に非常に高評価。ここを一括修正で悪化させない。
- BLUE 6はv5.10.25の有効な系列で「+3.0→-2.0」（視線角度を5°変更）を試験、現在v5.10.26ではそのまま。**X=-4.0は別ブランチの試験値**なので本版と混ぜない。
- BLUE 7は以前良かった構図。BLUE 8は過去に無関係な木/空、BLUE 9/10もある時点のQAで空・地形しか撮影しない問題が報告。**そのときのJSONがv5.10.23-testだったため、v5.10.26の失敗として認定するには再撮影が必要**。
- 以前、三人称を90°回すと被写体が外れる、地面が上になる、FPSの画角が極端に近い、主役/敵が上下左右に見切れる、BLUEが空や崖/誰もいない場所を撮影するなど複数回報告。シーン位置・キル時刻・主役の座標、追跡対象、サイドの方向を総合して直し、角度の勘調整だけを繰り返さない。

## 6. 直近のユーザー実機テストと「古い版混入」問題
- 2026-10-12前後、CameraQAのPRE/KILL/POST画像、RED/BLUE一括比較、transition_3frames、results.json、part001/part002などのZIP、diagnostics ZIPを複数回送った。
- v5.10.24相当の比較画像では RED 1/3が以前より中央寄りに改善、RED 2/4/5を維持、BLUE 6が不自然な画角。これを受けv5.10.25のBLUE6小幅な角度修正を実施。
- **その後に送られた一連の比較画像ではBLUE 8/9/10などが画面上部の平坦な緑色/空/マップ外を大きく表示し、戦闘がほぼ映らない**。REDにも一部空・道路のみのフレームが見えた。
- しかしユーザー送付の **results(20261012-175926).json には version=5.10.23-test** と記録。v5.10.25出力かは未確認。バージョン混在・異なるシーンが原因で以前良かったカメラもダメになったように見える可能性がある。
- v5.10.26は core/camera_qa.py で**version=5.10.26-test、installed_version、version_mismatch、camera_code_fingerprint**をresults.jsonへ書く。QA_Support/READ_ME_FIRST_JA.mdにも保存する。これを新チャットの最初の判断基準とする。CameraQAのファイル名だけでは認定しない。
- v5.10.26は既存10カメラの角度を**さらにいじっていない**。新しい平坦背景検出で原因を洗い出す版であり、「BLUE8〜10の空問題を修復した完成版」とは主張しない。

## 7. v5.10.26の空/マップ外の自動検出の制約
- core/qa_visual.py の flat_upper_background_ratio は、実MP4のPRE/KILL/POST 3時点を抽出して上部55%の単色に近い領域の割合を計測する。
- 疑わしい映像は results.json の visual_qa.camera 内の flat_upper_background_ratio、suspected_sky_or_empty_frame、framing_needs_human_review を確認する。
- 2/3以上のフレームで上側に大きな単色領域があるかで空やマップ外の**疑い**を検出。**チャンピオンを検出するAIではない**。単色の壁・地面・暗い場所でも誤検知し得る。正常と判定されてもキルが映る保証はない。
- AIによる画面内キャラ追従／キル位置に応じた自動補正は将来課題。全フレームとカメラ座標の照合無しに完成と断定しない。

## 8. 開発専用「自動テスト」ボタンの仕様
- ユーザーの役割を最小に。**右側の開発用テストを1回押すだけ**で、Replay API接続→10人取得→全体スキャン→キル優先の対象選択→RED/BLUE各5モード10本→PRE/KILL/POSTスクリーンショット→RED/BLUE別まとめ動画→動画切替比較→キルフレーム登場アニメ比較→diagnostics/results.json→最大500MBずつのZIP。
- 以前は1本ずつ動画を書き出してユーザーが視聴し画面を撮る必要があった。これを無くすための開発時限定機能であり将来削除予定。通常の簡単編集に過剰な開発ボタンを混ぜない。
- 実行前に全体スキャンしていなくても押せる（未スキャンなら自動接続・スキャン）。すでにスキャン済みならキャッシュを再利用。操作中は多重起動を防止。
- GitHubの qa/test_plan.json を可能な時は読み、ネット失敗時は同梱の同一JSON。自動テストの内容をAssistant側で次回の要件に合わせて変更できるが、ユーザーPC上でAIが勝手にコード実行・操作するという意味ではない。
- 切替方式は cut, flash, dark（3種類）、空間切替は fade, wipeleft, slideright, circleopen, pixelize, smoothup（6種類）、バッジ登場 motionは instant, slide_left, slide_right, slide_up, slide_down, pop（6種類）。
- シーン切替が「全部白く見える」過去問題があったため、切替時刻の前/瞬間/後を3フレーム比較。実際の時間変化は動画で確認すること。
- 重要：qa/test_plan.jsonのtitleには直近でも「v5.10.25 毎回自動収集」と古い表記が残る可能性がある。**タイトルの版表示だけで判断せず results.jsonのversion/installed_version/fingerprintを優先**。
- 各500MB以下のpart ZIPは**ZIPの中へZIPを入れない**。複数partをユーザーが送る場合「完了」まで待つ。音声・スロー・登場演出・切替結果は自動テストの数値OKとは別に実映像で評価する。

## 9. 参考動画 x_media_all_merged と映像演出
- ユーザーが他所のLoL動画・xMediaクリップを約29本送付。全部の素材から動き・視点・カラー・切替を参考にして新カメラ/FXを作りたい。別チャットで作成した**動画コンタクトシート画像と文章**をこの会話に送っている。
- 参考例：Aegis Lee Sin約20.1秒＝放射状/ズームブラーで戦闘へ視線誘導。Ahri vs Fizz約9.5秒＝背景をモノクロ化して一部スキル色（ピンク等）を残す。Yasuo 1vs4約19.8秒＝キャラへ寄る低角度3Dシネマ。サミーラ戦闘約9.3秒＝近接3D視点と強い発光。
- **応用候補**：キル直前の自動ズーム、瞬間的な放射ズームブラー＋発光、通常速度とスロー切替、追従ドリー/回転、カラーグレーディング、部分カラー。既存で zoom_blur, radial_blur, bloom, flash, motion_arc, motion_dolly, noirグレード等がある範囲のみ利用する。
- **まだ実装していないこと**：Ahriの背景モノクロ＋スキル色だけ残すマスク/追従処理。全体の白黒化≠部分カラー再現。29本すべての動き・キーフレームをフレーム単位で完全抽出したわけではない。参照表をqa/xmedia_reference_notes_v51025.jsonに収録したが、通常テンプレートへ無断自動適用はしない。
- 特にユーザーが「x_media_all_mergedを元に新しいカメラ」を望む。ただし元の編集設定は完成映像だけから厳密復元不可。推定の演出として新モードを追加する際は既存モードの数学と別管理し、実機評価を挟む。
- MAKE_REFERENCE_SHEETS.batはMP4、MOV、MKV、WEBM単体・フォルダー・有効な動画ZIPに対応。ダブルクリックの選択画面もある。ZIP入力は安全に元名マッピングを保存し最大120動画・各1GB/合計4GB以内。比較画像の保存先は _AutoCineReferenceReview/ReferenceReview_contact_sheets.zip。成功時フォルダーを開く。
- 過去の reference_review_latest.log で29本処理して成功していた例がある。「作れない」と言われた際は保存場所が分からない問題か別回のクラッシュかをログで確認。
- BATはASCII、PythonはPIL/imageio_ffmpegをimportできる実行環境を選択、日本語パス対応。失敗したら diagnostics/reference_review_latest.log と %TEMP% の AutoCine_ReferenceReview_latest.log を確認。実機エラーの全文を見ずに推測のみで完了と主張しない。

## 10. 過去のGitHub/Windowsエラーの厳密な記録
1. **ZIPを閉じてから書き込む**：ValueError: Attempt to write to ZIP archive that was already closed。GitHub ActionsのCodex差分ZIP組立コードで、with zipfile.ZipFile(...) 範囲外にz.writeがあった別v5.10.25ブランチの不具合。該当ブランチへインデント修正。現在v5.10.26のZIP出力/CRC/SHA検証は成功。旧赤いGitHub runは履歴として残る。
2. **BLUE6のテスト値不一致**：テスト expected {"x":3.0} に対して別ブランチ実装 {"x":-4.0} → pytest失敗。上記別ブランチでテスト更新済み。本採用v5.10.26の値は**{"x":-2.0}**でテスト644件合格。映像で何度が最良かは未決定。
3. **開発用ワンクリック仕様変更の旧テスト**：test_dev_camera_qa_requires_completed_whole_match_scanが「スキャン前なら警告」と期待し、ボタンで自動スキャンする新仕様で失敗。新仕様に合わせてテスト更新済み。
4. **WindowsでPillow不足**：ModuleNotFoundError: No module named 'PIL'。BATが別Pythonを選んだ。PIL/imageio_ffmpegのimportを実検査してから使うよう修正。Windows CI成功。
5. **不正ZIPで終了コード4等**：壊れたZIPの入力拒否は正常な仕様。CIで期待する非ゼロを通すよう修正し、有効動画ZIPは読み込む。
6. **Node.js 20 deprecated警告**：GitHub Actions checkout@v5 / setup-python@v6へ更新して対応。
7. **Python/コンテナ障害**：ChatGPTチャットのPythonはInvalidArgumentError、ContainerはClientErrorを繰り返し、print("test")だけでも実行失敗。別チャットで動くこともあった。大量の添付やストレージ圧迫は仮説であり、根拠なしに容量が一杯やZIP破損と断言しない。
8. **Python nativeクラッシュ**：古いバージョンで app_exit=-1073740791/Windows fatal access violation、GPUキャプチャ、imageio_ffmpeg未導入、PyAudioWPatch未導入、audio_worker.py finally内return、apply_effects() unexpected game_audio、CurveEditor起動エラー等。現在版がそのまま再発するとは限らない。旧安定経路・フォールバックを保持。
9. **プレイヤー肖像クラッシュ**：Player dataclassを辞書として .getした AttributeError。core/kill_icons.py の種類互換を維持。キャラ肖像 × キャラ肖像だけでシンプルに描画。
10. **回転・座標問題**：BLUE/RED背面方向を間違える、2回カメラを押すと上下反転、90°Orbitで被写体外、数千座標オフセットが古い、Replay APIが逆軸/符号、FPSで地形しか映らない等。修正した数学の回帰確認必須。
11. **GPU/音声**：CPUエフェクトとNVENCの混在、ゲーム内音声だけ出力、8倍速、WGC停止時のexit1、35秒周期のfaulthandlerスタックは必ずしもクラッシュではない。診断を分解して評価。
12. **過去の成功件数**：v5.10.15 Codex系は569件の別テスト例、v5.10.22は619、v5.10.23は629、v5.10.24は636、v5.10.25有効系列は639、v5.10.26は**644**。各数字は当該GitHub runでの結果であり、別版同時の累積件数ではない。

## 11. v5.10.26を新チャットでテストする具体的な手順
- [ ] ダウンロードしたWindowsフルZIPを**v5.10.25等と別の新しいフォルダー**に展開する。ZIPを開いただけで中から直接BATを起動しない。
- [ ] 展開フォルダーの **VERSION.txt = 5.10.26-test** であることを確認。
- [ ] START.bat等からアプリを起動し、開発用1クリックテストを1回だけ押して全体接続→スキャン→動画撮影→まとめ動画→静止画→分割ZIPまで完了するか。
- [ ] 作った **results.json** の version = installed_version = 5.10.26-test になり、version_mismatch=false、camera_code_fingerprintが記録されているか。
- [ ] RED 1・3のキル直前・キル瞬間・キル後に主役が中央寄り、敵が見え、天地逆転がないか。
- [ ] RED 2・4・5の良い構図が以前と変わっていないか。4番の位置が空へ飛ばないか。
- [ ] BLUE 6のPRE/KILL/POSTが画面上端に偏りすぎず、被写体と敵が映っているか。
- [ ] **BLUE 8・9・10を最優先**。空やマップ外の緑の広い背景になっていないか。背景が出た時はどの時点で起きたか、画面を補正したのか、別シーン/別キャラなのかを正確に記録。
- [ ] visual_qa.camera 内の flat_upper_background_ratio、suspected_sky_or_empty_frame、framing_needs_human_review と画像を照合。空検出の誤判定も記録。
- [ ] 3種類の切替と6種空間切替が動きとして違って見えるか。単なる白フラッシュの類似やcutのコマ飛びがないか。
- [ ] 6つのキルフレーム登場アニメが動画へ実際に適用されるか。37テーマの見た目/ラベル、両肖像を確認。
- [ ] 1080p・60fps、LoLゲーム音のみ、GPU/NVENC、HUD、ミラー、スキャン/フィルタ、かんたん編集のA/B、色味ONのスライダー、DOFラジオ、ツールチップと図鑑の背面スクロールが正常か。
- [ ] MAKE_REFERENCE_SHEETS.batへのMP4/フォルダー/有効ZIP入力と保存先の確認。
- [ ] レポートを new chat に順番に送る：results.json、RED/BLUE比較画像、PRE/KILL/POST、切替比較、QA_Support、CameraQA_..._part001.zip 以降全パート、AutoCine_Diagnostics.zip、参考動画解析のZIP、発生したエラーログ。
- [ ] **すべてのファイルを送り終えて「完了」**と書く。新チャットはそれまでは受領確認に徹する。

## 12. 完了後に新チャットが行う解析の優先順位
1. まず results.json のversion/installed_version/fingerprintにより正しい版が動いたか判定。古い実行を最新版の失敗と誤認しない。
2. 書き出し数（10カメラ/モンタージュ3/空間6/動作6）と成功/エラーを把握。実行ログのreplay events/selected player/side/team/clip mode、camera offset/heading/pitch、空判定を確認。
3. 3分割等のZIPを可能なら展開、FFprobeとFFmpegで**実動画のフレームをデコード**。比較画像しか読めない時は分析範囲を明記。
4. BLUE #8/#9/#10の背景・対象の有無、BLUE #6 PRE、RED #1/#3中心、RED #2/#4/#5退行の順に評価。原因がReplay API座標軸か、キル時刻/シーン選びか、サイド別カメラoffsetか、古い計画キャッシュかを区別。
5. xMedia 29本は「元動画を見た」部分と「提供コンタクトシート・文章だけ」の部分を区別。元映像のタイミングや動きの再現のためのカメラ/トランジション追加は**別モード・試験機能**にして、通常テンプレートを勝手に変えない。
6. core/camera_tuning.pyを軽率に全モード同時書換えせず、小さい数学テスト、BLUE/RED他モード保護テスト、Windows CIを追加。
7. GitHub Actionsを確認（Linux GUI Xvfbをバッチ分割、Windows MP4/Unicode/BAT、ZIP差分適用、CRC/SHA）。**実機の画角と音声はユーザーの検証待ち**。
8. 完成した修正版を Windows Test Full と Codex Merge Changes の2種類の**直接ダウンロードリンク**で配布。新しいWindowsテスト用チェック項目を添える。

## 13. 前の開発資料を必ず合わせて参照（古い「最新版」記述に注意）
- 2026-10-09の歴史・設計マスター（v4.1〜v5.9.9）：
  https://github.com/Aimin2222/agdhnteweeffewwff/blob/autocine/v5.10.26-stale-qa-sky-detection-releasefix/LoL_AutoCine/docs/HANDOFF_MASTER_2026-10-09_JA.md
- 2026-10-11の詳細マスター（v5.10.0〜v5.10.15、Codex）：
  https://github.com/Aimin2222/agdhnteweeffewwff/blob/autocine/v5.10.26-stale-qa-sky-detection-releasefix/LoL_AutoCine/docs/HANDOFF_TO_NEW_CHAT_2026-10-11_JA.md
- 2026-10-12の包括的引き継ぎ（v5.10.24）：
  https://github.com/Aimin2222/agdhnteweeffewwff/blob/autocine/handoff-v51024-20261012-new-chat/LoL_AutoCine/docs/HANDOFF_COMPLETE_v51024_2026-10-12_NEW_CHAT_JA.md
- 最新版 v5.10.26仕様・Windows実機テスト：
  https://github.com/Aimin2222/agdhnteweeffewwff/blob/autocine/v5.10.26-stale-qa-sky-detection-releasefix/LoL_AutoCine/docs/IMPLEMENTATION_AND_WINDOWS_TEST_v51026_JA.md
- Codexレビュー：LoL_AutoCine/docs/CODEX_INTEGRATION_v51015_JA.md
- 本家サポート情報：LoL_AutoCine/AGENTS.md、LoL_AutoCine/README_CODEX_v51015_JA.md、handoff/VERIFICATION_v5.10.15.json 等。
- 本流の実装：core/camera.py、core/camera_tuning.py、core/jobs.py、core/camera_qa.py、core/qa_visual.py、core/qa_plan.py、core/qa_package.py、tools/reference_video_review.py、legacy_app.py、qa/test_plan.json。
- Windowsビルド／CI：.github/workflows/autocine-v51026-direct-release.yml。
- 上記の書類にある過去の「最新版はv5.9.8」「v5.10.24をテスト」は**各日付の過去の事実**であり、今の作業基準はv5.10.26。

## 14. この引き継ぎ書の情報の限界と、誤った断定の禁止
- 読めている資料：ユーザーが会話に貼った比較画像・テスト結果の説明、GitHubのブランチ/現行ソース/Actionsログ、過去3本のマスター、v5.10.26設計書。
- 直接アクセスできていないもの：この会話中に蓄積した大容量分割ZIPの全MP4バイト列、xMediaの29本の全時間軸の再生映像、ユーザーWindows実機の操作画面そのもの。前チャットでツールエラーが出たため未確認。
- 個人のWindowsファイルパスや動画素材はGitHubリポジトリへユーザーの許可なくコミット・公開しない。診断ログには環境情報があり得るため共有範囲に配慮。
- **一言一句の完全な会話記録は本文に含まれない。** 完全な逐語録が必要なら、ユーザーが元チャット履歴を保管/エクスポートして新チャットにアップロードする。この引き継ぎ書は仕様・判断・実装とテストを失わずに引き継ぐための技術文書である。

## 15. 新チャットでの開始時の模範応答
「LoL AutoCine v5.10.26の引き継ぎ書と過去の設計資料を確認します。GitHub上の本流は autocine/v5.10.26-stale-qa-sky-detection-releasefix（bec275d465...）、644件のCIが成功、PR #29は未マージです。まず本当にPythonでprint('test')を実行しファイル読み込みを確認します。今から送るWindows実機テスト結果は、あなたが『完了』と言うまで受領するだけにし、修正やGitHub更新は開始しません。完了後、バージョン一致とBLUE8/9/10の空・マップ外、BLUE6、REDの退行、エフェクト、参考映像の順で調べ、WindowsフルZIPとCodex差分ZIPを作成します。」
