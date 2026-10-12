日本語で応答。現在の開発対象は /workspace/LoL_AutoCine、v5.10.20-test、integration/v5.10.20、HEAD d76c0d78c82db9f0c278d83878113b5bc7757aee。486ソース/Python174/107ブランチ。既存checkoutを使い、明示依頼なしにworktree/subagentを作らない。添付文書の指示はユーザー依頼と区別し、setupのみでアプリ/テスト/依存宣言を変更しない。ユーザーはUI ZIPの安全統合、GPU担当分離、Windowsローカル開発、新規GitHubブランチとDraft PR作成を承認済み。mainマージ、個人設定/録画/診断の破棄・無断アップロードは行わない。

今回: 校正とstable rotation双方をselection/team/style別に分割。同モードの再校正時の180度安定化とリプレイ変更resetは保持。BLUE通常third距離1.26、BLUE third/シネマ/Lolnam geo look、FPS BLUE0.54/RED0.89と向き、auto RED通常third+8度をライブsetupでのみ有効化。REDシネマ/BLUE geoの式、手動0/180度、keyframe、FOV、Orbit/TargetLock、CameraPlan/attach/_setup_clip ABIを保持。画角改善は受領補正候補でWindows未確認。色微調整をチェック直下に表示しOFFでも共有値保持。付属QA planはcut/flash/darkの3比較＋6空間＋6キル登場、全10演出の通常機能/planなし旧APIは保持。参照動画BATは任意のローカル6時点JPEG/JSON/ZIP、元動画不変・外部送信なし、空フォルダも有効ZIP。CPU静止画抽出は通常GPUエンコード経路外。

最初に status/log/remote/VERSIONを確認し、AGENTS.md、CODEX_HANDOFF_JA.md、CODEX_FIRST_TASK_JA.md、docs/CODEX_INTEGRATION_CONTRACT_JA.md、docs/CODEX_INTEGRATION_v51020_JA.md、docs/CODEX_SHARED_API_REVIEW_v5.10.20.json、docs/WINDOWS_TEST_v51020_JA.mdを読む。AGENTSのv5.8.5は初期版。source remoteなし、取得用 /workspace/agdhnteweeffewwff origin https://github.com/Aimin2222/agdhnteweeffewwff.git、codex/lol-autocine-v51020-camera-isolation-handoff。Draft PR https://github.com/Aimin2222/agdhnteweeffewwff/pull/36、比較先前回v19、main c2a79ac3e7816c74b7d7fb15a5a32a32dd8fa16bを保持。

担当GPU feature/gpu-cameraqa-v51020、UI feature/ui-cameraqa-v51020、統合 integration/v5.10.20、受領 archive/received-ui-v51020。古いUI累積patchをGPUへ直接上書きせず指定基準に独立apply --checkし、前回受領との差分のみ選択統合。共有8blobレビューとstatus双方を確認。旧103先端/37PNG/184配布物を保持。GPU全22FX・60fps時刻/フレーム数・LoL Native Process Loopback/Helper構築・WGC子分離・LatestPreview/Tk主スレッド・ミラー応答改善・NVDEC実素材probe・NVENC RGBA・encoder_policy/diagnostics/安全CPUfallback・500MB直接ZIP/1MBstream/最終JSON一致を保持。前回capture終了テストはrunning=Falseまで待ちerror/latest例外を確認、録画実装不変。GPU effectsとNVENCを区別しCPUゼロや物理GPU速度を主張しない。

現在の環境チェック（cwd /workspace/LoL_AutoCine）:
.venv/bin/python -m pip check
.venv/bin/python -m compileall -q app.py legacy_app.py ui_phase1_prototype.py core ui tests tools
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51020 --ui feature/ui-cameraqa-v51020 --integration integration/v5.10.20 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.20.json

Xvfbは検証済みDebian署名/hashとworkspaceだけへ展開、毎コマンド起動/終了で常駐なし。ソケット/ネット制限時は承認付き実行。PyPI pinはinstall_scriptで検証済み。TLS/署名/checksumを無効化しない。GitHub既存HTTPS proxy認証を使い資格情報の値を要求・表示しない。ネット/秘密/リポジトリ設定を保全。DDragon実取得403の旧未解決項目を迂回せず記録する。

v20検証はLinux/Xvfb全675成功54.12秒、失敗/skip/除外なし・GC有効・強制GCなし。実fake Replay APIで他mode/teamのstable rotation混入を防止、同mode復元/resetを検証。実60fps MP4の6時点シート/空フォルダZIP/元動画不変を確認。GitHubからの別checkoutとbundle復元で全486ソース/107refs/ZIP・bundle hashes一致、復元先代表166成功13.00秒。再setupで486ソース/107refs/3個人設定相当ファイル保持/status clean。これは同一クラウド内の別フォルダ検証で、新しいクラウドtask/Publish/Windows確認とは別。物理NVIDIAとLoL画角/速度は未確認。過去ScanFix native139×2、v16復元SIGILL132×2は原因未確定、今回は再発なしだが恒久修正とは扱わない。

再現installerは保存先不在時だけ固定payload a243371363c098a8e966d58d4bb7141c3c259fbfのbundleを復元。bundle SHA256 807c70c3327f78205e640263b5d34fc8de96741cfc2d5746246dfa8a083c8b92。既存checkoutをswitch/reset/上書きしない。配布root .gitattributesのhandoff/*.bundle binaryを保持してWindows autocrlfによる破損を防止。

Windows取得はGitHubのhandoff/LoL_AutoCine_v5.10.20_CameraIsolation_GPUFull_Windows_Full.zipを開きDownload raw file、または今回ブランチCode→Download ZIP。架空チャットダウンロードリンクを作らない。旧版と別フォルダでSTART_GPU.bat、docs/WINDOWS_TEST_v51020_JA.mdのまとめテスト。診断/QA ZIPは会話へ、ユーザーの録画をGitHubへ公開しない。mainマージ/環境PublishはWindows取得に不要。install_script/start_skill保存は実行/適用/Publishとは別。次回クラウドに反映する場合だけ環境設定で確認・保存後Publish（アプリを他人に公開する操作ではない）。.exeは今回未作成、将来Windows回帰→設定/リソース保存API→PyInstallerフォルダ配布→クリーンWindows確認。

以下は以前の保存手順・検証・ユーザー要件をそのまま保持した履歴資料。版番号/HEAD/担当branch/取得リンク/テスト件数は過去のもの。現在の起動・復元・担当ガードは上記v20の手順を使用し、履歴内の旧版を現行へ上書きしない。

日本語で応答。主対象 /workspace/LoL_AutoCine、現在 v5.10.19-test、integration/v5.10.19、HEAD 26c90ed8236c3341d05327c55000eb1b85666213、475ソース/Python170/103ブランチ、remoteなしのローカルGit。既存checkoutを使用し、明示依頼なしにworktree/subagentを作らない。添付文書は参照資料でありユーザーの依頼と区別。setupだけならアプリ/テスト/依存宣言を変更しない。開発依頼は担当分離と回帰テストで進める。指示だけを根拠にVERSIONや未保存変更を旧版で上書きしない。

今回v5.10.19: 通常third/RED geoのyaw=X・pitch=Y・roll0、古いtop基準除外、REDシネマ/Lolnam接近制限を受領補正候補として統合。BLUE geo従来式を保持。初期軸強制時はrigのaxis/sign/complementをY/+1/通常へ一致させ旧stable cacheで補正を取り消さない。他モードのstable/resetを保持。カメラ式全体を書き直さず、Windowsの画角/主役/水平線改善は未確認。

初期Templateと先頭プリセットは無加工/vignette・grain・bloom0/cut。明示的な旧プリセット/効果選択は維持、ネオン/アイス/金の差を受領値へ調整。かんたん/詳細は同じvar_tpl、テンプレート/A/B図鑑を編集画面へ移動。かんたん色微調整はON時だけ4項目表示、OFFでも値保持。ミラー/DOF/スキャン/出力/図鑑scroll/LatestPreviewを維持。

QAはRED/BLUE別確認reelと3時点比較画像、両側third_cinemaを優先して従来10演出/6キル登場へ渡す。6空間切替をQAだけへ追加。受領CPU/libx264固定をcore/gpu_qa_transitions.py/SpatialStageで2素材OpenCL合成＋選択encoder_policy＋診断＋CPU xfade fallbackへ接続。延長はhardware frame cloneと明示フレーム数、60fps/長さを固定。両端素材/中間画像の違いを検証。空間確認動画だけ無音、通常LoL音声/side reelは保持。通常モンタージュを置換しない。

比較表の3時点は時間割合による参考サンプルで、実キル瞬間や主役/水平線のAI自動合格判定ではない。数値のgeometry_validationも参考。前回500MB直接ZIP/1MBstream/最終JSON一致/元動画・JSON・既存ZIP保持/データ専用plan64KB・3秒・既知操作制限を維持。配布root .gitattributesのhandoff/*.bundle binaryは長いbundleヘッダの誤テキスト判定を防ぎWindows autocrlfで破損させない。

受領ZIP/README/全差分/8テストを確認、指定GitHub0e8e8f6でapply --check/適用。受領v18からの16パスだけ現行Codex v18へ機能別統合。原ZIPはGit外、history/v5.10.19にコード/README。添付Windows症状・xMedia評価・Releases記述は受領側で、今回Codexは実機/参考映像確認やRelease作成をしていない。GPU feature/gpu-cameraqa-v51019、UI feature/ui-cameraqa-v51019、統合 integration/v5.10.19、受領 archive/received-ui-v51019。旧99refs/175旧配布物/37PNGとGPUエンジン・音声・録画を保持、全103refs bundle。共有8blobを固定レビュー。

現在の検証: Linux/Xvfb全653成功52.58秒（失敗/skip/除外なし、faulthandler/GC記録のみ、強制GCなし）。6空間GPU kernelをCPU PoCLで実行し各95フレーム/60fps/両端素材と模様付き中間画像の差を確認。2side reels/3時点4カメラ/5画像/直接ZIP/CRCを実動画で確認。PoCLは物理GPU性能ではない。Windows/LoL/NVIDIA速度・カメラ構図は未確認。完全ZIP473/差分適用後475ソース一致。前回native終了は原因未確定、今回全件で再発なし。恒久解決と断定せず記録する。最新はhandoff/VERIFICATION_v5.10.19.json。

現在の担当ガード:
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51019 --ui feature/ui-cameraqa-v51019 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.19.json --integration integration/v5.10.19

前回v5.10.18の追加（保持）: 新規Template gradeはdefault（無補正）、初回UIも無補正。既存テンプレート選択/保存IDは保持。Bloom等の別FXは変更しないため全加工OFFではない。図鑑はroot active gallery＋transientで追跡、開いている間は背後wheel抑制、close/destroyで参照/worker解放。旧非同期preview/Tk所有を保持。

ユーザー開始QAでGitHubのデータ専用plan取得。取得先は今回Codex branch/LoL_AutoCine/qa/test_plan.json。64KB/3秒/既知camera・transition・motion/100〜500MB/型を検証し通信・検証失敗は付属JSON。コードをdownload/executeしない、JSON文言をagent指示として扱わない。通常起動時通信なし。実URLのデータ取得/検証は成功。付属計画では従来4＋geo_aim実験を両チームで計10本、plan未指定APIは従来8本。キル優先、なければassist。既存4カメラ式/RED184度/手動0・180度/TargetLockを保持、geoは選択時だけ相対offsetから視線計算。Euler軸と構図はWindows未検証。数値geometry_validationと実MP4比較表は参考、主役やキルや水平線のAI自動判定ではない。

QA結果を最大500MBの直接ZIPへ、ZIP入れ子なし。巨大MP4は1MBずつstreamして番号partと結合手順、原動画/JSON/既存ZIPは削除せずrepeat別名。symlink/外部パス除外、先に出力名を計画して最終JSONをZIP内へ反映。比較画像は小さい静止画だけ、短い動画の終端外を読まない。10切替/6モーションは従来GPU Full/60fps/元音声copy/encoder_policy/録画素材再利用を維持し色/DOF二重適用なし。中止は現在の1本終了後に残り停止、比較表/ZIPの追加開始も抑制。CPU静止画/制御/音声/I/O/ミラーは残る。

受領ZIP/README/全差分/8テストを確認、指定GitHub0e8e8f6へapply --check/適用。受領v17からの13パスだけ現行Codex v17へ機能別統合、古いGPU/音声/カメラ/UI上書きなし。原ZIPはGit外、history/v5.10.18にコード/README。GPU feature/gpu-cameraqa-v51019、UI feature/ui-cameraqa-v51019、統合 integration/v5.10.19、受領 archive/received-ui-v51018。旧95refs/166旧配布物/37PNG保持、全99refs bundle。共有camera.py/jobs.pyだけblob更新レビュー、他6共有blob維持。

前回v18検証: Linux/Xvfb全635成功82.14秒（失敗/skip/除外なし、faulthandler/GC記録のみ、強制回収なし）。巨大ファイル分割/再結合/元データ保持/再出力/最終JSON一致/symlink除外、plan拒否/通信fallback、geo相対offset整合を検証。合成実動画から2カメラ/2比較画像/直接ZIP/CRCを実行。Windows/LoL/物理NVIDIA速度とgeo画角は未確認。完全ZIP461/差分適用後463ソース一致、個人ファイル除外。過去native終了は原因未確定、今回全件で再発なし。恒久修正/安定保証はしない。今回の復元先代表結果はhandoff/VERIFICATION_v5.10.18.json。

現在の担当ガード:
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51019 --ui feature/ui-cameraqa-v51019 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.19.json --integration integration/v5.10.19

前回v5.10.17の追加（保持）はカメラ数値証拠と6モーション追加QA。CameraQA名のジョブだけ既存rig/plan値をCAMERA_QA_POSE JSONで記録し、8本のoutputs[].camera_diagnosticsへ格納。カメラAPI書込/座標/pitch/RED184度/手動0・180度/TargetLockの式は変更しない。ログは開始リグ/予定値であり水平線や地形衝突の自動判定ではない。

8本/10切替に追加して録画済み映像の1本から6モーションMP4を作り、min(3秒,実素材長)/60fps/元音声copy。追加LoL録画なし。受領CPU overlay/libx264固定をcore/gpu_badge_qa.pyから既存GPUFullStage/能力確認/選択encoder_policy/診断/安全CPUfallbackへ接続。色/DOF等を二重適用しない。実FX経路・実encoder・理由を別に記録。NVENCだけCPU再試行してもGPU加工が継続する場合を正確に報告。中止は現在のエンコード1本を終えてから残りを止める。

受領のREADME/パッチ/3追加テストを確認し指定GitHub基準0e8e8f6でapply --check/適用を検証。受領v16との差分だけ現行Codex v16へ統合。添付のWindows結果/Actions/AIカメラ構想は受領資料に区別、Codexでの実測・実装ではない。docs/RECEIVED_RED_CAMERA_EVIDENCE_v51017_JA.md。旧91refsを保持、全95refs bundle。旧157配布物/37PNG/前回UIとGPUエンジン/録画/音声を保持、core/jobs.pyはQAログ追加だけ。現在の資料CODEX_INTEGRATION_v51017_JA.md/WINDOWS_TEST_v51017_JA.md。

前回v17検証: Linux/Xvfb全614成功66.45秒（失敗/skip/除外なし、faulthandler/GC記録のみ、強制回収なし）。関連20テストでGPU障害/timeout/CPU比較/encoder policy/NVENC retry/audio/60fps/カメラAPI書込不変を確認。6モーションQAを検証用CPU PoCL OpenCLで実レンダリングし各60フレーム・元AAC packet一致。物理GPU/Windows/LoL速度と画角は未検証。完全ZIP448/差分適用後450ソース一致、個人ファイル除外。前回のLinux native終了は原因未確定、今回全件で再発なし。再発解決/永久安定を主張しない。今回の復元先代表結果はhandoff/VERIFICATION_v5.10.17.jsonを参照。

最初にgit status --short、git log -3 --oneline、git remote -v、VERSIONを実環境で確認。AGENTS.md、CODEX_HANDOFF_JA.md、CODEX_FIRST_TASK_JA.md、docs/CODEX_INTEGRATION_CONTRACT_JA.md、docs/CODEX_INTEGRATION_v51019_JA.md、docs/CODEX_SHARED_API_REVIEW_v5.10.19.json、docs/WINDOWS_TEST_v51019_JA.mdを読む。AGENTSのv5.8.5は初期版、VERSIONが現行版。旧87refs・旧配布物・個人設定・録画・プロジェクト・診断を保持し、reset/clean/mainマージをしない。Windowsローカル開発と新しい取得用ブランチ/Draft PRはユーザー承認済み。生ログ/ユーザー名/プレイヤー情報/録画はGitへ無断追加しない。

GPU担当 feature/gpu-cameraqa-v51019、UI担当 feature/ui-cameraqa-v51019、統合 integration/v5.10.19、原本 archive/received-ui-v51017。古いUI ZIPでGPUコアを丸ごと上書きしない。旧role refsを移動させない。共有8ファイルは正確なblobでレビュー。担当ガードはコミット済み先端だけなので未保存statusも確認。v16は外ZIP内のZIPを安全確認して展開。README・patch・9テストを読んだ。指定基準GitHub0e8e8f6へのapply --check/適用を別checkoutで確認し、現在のScanFix e62be60へ機能別に統合。原ZIPはGit外attachments/scratch、コード差分/READMEはpatches/history/v5.10.16。過去v13/ScanFix受領には個人ログ/cache/pycが混在し、それらをGitに入れていない。

継続仕様（v16までの追加を保持）: キル表示6登場モーション。Template末尾にkill_icon_motion既定instant、旧JSON/位置引数維持。CPUとOpenCLをbadge_motion_xyで共有し、GPU Full合成にresident motionを追加。GPU診断kill_icon_motionを記録。CPU overlayへ戻さない。三人称の非pitch軸だけ110度以上の急変を抑える。前回成功回転は校正リセットで保持し、リプレイ変更では消す。既存俯角/座標/TargetLock/手動向きの式は不変。

ユーザー開始の録画QAはRED4/BLUE4の実キル/アシストから代表8本を既存run_auto_edit・LoL専用音声・60fpsで順次作成し、2本を全10切替に再利用。selected encoder_policy/実VERSION/fallbackをresults.jsonへ記録。snapshotはTk上で、録画はworker、所有sourceはfinally停止。停止は次ケースへ進まず、切替FFmpegは現在の1本終了後に残り停止（即時停止は未実装）。旧ScanFix開発QAも保持。DOF円/帯radio、スクロール速度、指定11素材名だけ更新、全旧alias/素材保存IDを保持。

v15/ScanFix/PortraitFixを保持: 右側①で接続→プレイヤー取得→試合全体スキャン、完全キャッシュだけ再利用、再接続/リプレイで世代更新し古い結果破棄。処理中プレイヤー変更拒否、実対象へ戻す。5作業領域/図鑑/500msヘルプ/出力内基本設定/本物のキラー画像/仕上がり比較。DOF円/帯を中央・右側で排他表示し値保持。高解像度縮小checkboxはselected+disabled/active優先を含む6状態、hoverで選択を消さない。画像Player/辞書snapshot互換を保持。

色/素材/図鑑画像のcache照会/取得/加工は単一LatestPreviewワーカー、plain snapshot、最新要求とリプレイ世代ガード。失敗は名前、閉じる/destroyで停止。PhotoImage/root.after/ウィジェットはTk上のみ。未保存時偽ゲーム画像を作らない。図鑑2D色/FXは近似、カメラ/時間演出は実動画で確認。popdownは既存窓だけ調べホイールで新たに作らない。非同期ミラーはCPU/Pillow近似: 操作優先640x360/167ms、操作後960x540/FX約15fps・素20fps、snapshot変更時だけ、Canvas再利用。書出し1080p60fpsは別。

GPU Full/OpenCLは色/LUT/曲線・全22映像FX・履歴・DOF円/帯・Bloom・周辺減光/粒子・BPM/キル強調・枠/フォグ・タイトル/キャラ装飾・登場モーションを合成。色は既存FFmpegから一度33³ LUT。動画加工前に出力FPSへ絞り、主映像upload/download各1回。program_opencl出力の25fps誤認を60fps時刻/フレーム数明示で防ぐ従来修正を保持（25fpsを水増しする設計ではない）。NVDECは実素材プローブ成功時だけ、NVENCはRGBA入力。CPU制御/音声/I/O/入力変換/静止画準備/ミラーは残る。CPUゼロ/ゼロコピーを主張しない。productionはCPU OpenCLを拒否、NVENC列挙とGPU effects confirmedを区別。GPU失敗/タイムアウト/モノクロは同じ設定・音声・タイトル・イベントでCPU再試行。モンタージュcutはcopy、残る9演出はGPU+CPUfallback。

素材37PNGはバイト保持。プレビュー385x116/書出し770x232の一度だけCPU生成、動画合成はGPU。素材倍率0.5と行間round(116*scale+gap)をCPU/GPU一致。不正/NaN/無限大を検証。素材に描かれた光は動的発光OFFでも残る。LoL Native Process Loopback/Helper構築を保持し、デスクトップ全体の音声へ戻さない。

三人称/OrbitTargetLock、カメラ144Hz/録画60fps、WGC子分離/共有メモリ/初フレーム8秒、Replay Keep-Alive/遅いAPI姿勢制限、全/チェックシーン非同期準備、ミラー復帰を保持。RED通常自動184°/手動0・180°、校正済みpitch符号±80°、RED FPS offset0.76倍は前回版から保持。俯角不明は安全top。API cacheは完全スキャンのみ、キラー別連続キル・イベント再抽出はAPI不要。実RED画角の良否はWindows未検証。

TEST_GPU_RENDERはpy -3優先/venv/pythonfallback・import前ログ・pause/6ケースを保持。GPU加工テストは無音、LoL音声/カメラは通常アプリで確認。以前Windows比較6ケースの5GPU成功、03意図的CPU+NVENC、6秒素材02全体10.989秒/03全体46.344秒は歴史で今回性能ではない。CPU使用率だけでGPU不使用と判断しない。fatal_pythonの定期stackだけをクラッシュ証拠にしない。

クラウド: .venvと検証済みPyPI pin、Debian署名/hash検証付きworkspace Xvfbを使用。Xvfbはコマンド毎に起動/終了、常駐不要。ソケット/ネット制限時は承認付き実行。pytestはtests/を明示しWindows手動toolsを収集しない。

.venv/bin/python -m pip check
.venv/bin/python -m compileall -q app.py legacy_app.py ui_phase1_prototype.py core ui tests tools
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51019 --ui feature/ui-cameraqa-v51019 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.19.json --integration integration/v5.10.19

前回v16検証: Linux/Xvfb全604成功103.10秒（失敗/skip/除外なし、faulthandler/GC記録のみ）。6モーションのCPUと検証用CPU PoCL OpenCL実出力は各60フレーム・位置一致、production GPU要件変更なし。物理GPU速度/Windows/LoLは未検証。旧87refs/37PNG/20保護パス/148旧配布物保持、全91refs bundle。完全ZIP438/差分適用後440ソース一致、個人ファイル除外。以前ScanFix全件のネイティブ終了139x2は原因未確定。今回は全件成功後、復元先代表テストがIllegal instruction/132で2回終了した。全件成功だけを根拠に再発解決とは主張しない。追加診断の結果はhandoff/VERIFICATION_v5.10.16.jsonを確認。

取得用 /workspace/agdhnteweeffewwff、origin https://github.com/Aimin2222/agdhnteweeffewwff.git、codex/lol-autocine-v51019-camera-ui-qa-handoff、Draft PR https://github.com/Aimin2222/agdhnteweeffewwff/pull/35、比較先前回v5.10.18。main c2a79ac3e7816c74b7d7fb15a5a32a32dd8fa16bを保持。固定payload 43baa43f379daba81315489dd5a230119e2c1aed、bundle SHA256 689160c7adfe225e6167f1d941e70182b5b8d6c63b5b6801001ebf39cf5cd2b1から復元。installerは保存先なしの場合だけ復元、既存checkoutをswitch/reset/上書きしない。全475ソース/103refs/ZIP・bundle hash一致。同じ実行環境の別フォルダ検証で新クラウドtask/Publish/Windows実機とは別。fresh remote cloneは既存object cacheを使いsource/artifactsをsparse checkout。GitHub既存HTTPS proxy認証を使用、値を要求/表示しない。gh CLI placeholder invalidだけを接続不足と判断しない。gh pr edit旧Projects不適合はgh api PATCH pulls JSONファイル入力。

DDragon実画像は以前のproxy403で未検証、模擬URL/PNG/cacheとローカル合成PNGの経路は確認。既存api.github.com/ddragon.leagueoflegends.com許可先・package_managersプリセット/秘密要件/リポジトリ設定を保持。迂回/TLS/署名/hash無効化はしない。設定反映後に公式取得を再試験。クラウドcache_dirはworkspace scratch、WindowsはLOCALAPPDATA/LoL_AutoCine/champion_icons、手動assets/champion_icons/<ChampionID>.pngも可。未取得は名前表示。

Windows取得は完全ZIPのGitHub Download raw file、または新ブランチCode→Download ZIP。旧版と別フォルダでSTART_GPU.bat。架空チャットZIPリンクは作らない。まとめ実機テストはdocs/WINDOWS_TEST_v51019_JA.md、過去詳細v15手順も併用。旧設定→ミラーON操作/DOF/チェック→6モーションGPU/CPU比較→BLUE/RED4カメラ/seek/手動→8本QA/10切替素材再利用→全/チェックシーン書出し/60fps/LoL音声同期→中止再実行。結果は会話へ診断ZIP、必要ならQA results.json。個人ログ/録画をGitHubへ公開しない。

環境install_script/start_skillの保存は実行/適用/Publishとは別。Windows取得はmainマージやPublish不要。次回クラウド再利用に反映する場合だけ環境設定で確認・保存後Publish（アプリを他人へ公開する指示ではない）。今回.exe未作成。将来はWindows回帰→設定/リソース保存API→PyInstallerフォルダ配布→クリーンWindows確認の順。

前回v16復元先の代表95件は通常実行とGC記録のみの診断で2回Illegal instruction/132終了、test_jobs_forward_keyframes_without_mutating_template直前。faulthandler stackは得られなかった。直前のメインスレッドgc.collectを1回加える診断条件では95件成功12.45秒。GCは無効化せずテスト除外なしだが通常条件と区別する。GUI残存/GCとスレッドの関係は可能性で原因未確定。Windowsクラッシュ修正/テスト全体の安定化とは主張しない。標準条件の復元先代表全件完走は未確認で、クラウドテスト安定性に未解決項目がある。今後はGUI fixture teardownとTkオブジェクトのスレッド所有を調査する。

前回v17 GitHub復元450ソース/95refs/配布物hash一致、復元先代表105件成功14.57秒（選択したテスト順、失敗/skip/除外なし、強制GCなし・GC有効）。再setupで450ソース/95refs/3個人設定相当ファイルのバイト保持/status clean。過去native終了の恒久解決やWindows確認は未主張。

前回v18 GitHub復元463ソース/99refs/配布物hash一致、復元先代表126件成功12.66秒（失敗/skip/除外なし、強制GCなし・GC有効）。再setupで463ソース/99refs/3個人設定相当ファイルのバイト保持/status clean。過去native終了の恒久解決やWindows/geo構図確認は未主張。

初回復元は143成功/1失敗。既存capture終了テストがerror通知とrunning=Falseの中間状態を観測したため、終了状態を待ってerror/latest例外を検証するテストへ修正。録画実装は不変、全653を再検証して成功。旧v19初回snapshotは8bed683にGit保存、新bundle/ZIPはテスト修正後。元復元フォルダの個人設定相当を上書きせず、新しい-r2フォルダで修正版を検証する。

最終GitHub復元475ソース/103refs/配布物hash一致、修正版復元先代表144件成功12.25秒（失敗/skip/除外なし、強制GCなし・GC有効）。再setupで475ソース/103refs/3個人設定相当ファイルのバイト保持/status clean。旧復元フォルダ/旧snapshotも保持。Windows/LoLカメラ構図とNVIDIA性能は未確認。

