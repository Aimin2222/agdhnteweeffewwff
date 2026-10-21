# Codex向け実装・検証指示資料

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## この資料の使い方

採用後に別開発依頼として使う設計資料。今回実装は行っていない。基準SHA、実機環境、進行中UI29作業との調整を再確認し、最新へ移す時はこの資料と変更差分を照合する。歴史的v5.8.5引継ぎより現在の原文と新しいQA記録を優先し、矛盾を残す。

|変更案|既存接続先|互換性・禁止事項|検証|
|---|---|---|---|
|job永続台帳|core/jobs.py run_auto_edit / ui/scene_project.py|UI threadで設定snapshot、workerからTk参照禁止|failure/cancel/restart、成功clip hash再利用|
|実行経路表示|effects.encoder_args / gpu_full / diagnostics|requested・supported・actual・fallbackを別field|GPU不在・列挙のみ・実行失敗・CPU代替|
|camera承認|smart_camera_director.decide_camera|10旧style保持、side/style/patch別、未知は代替|manual/None後方互換、全候補除外、BLUE/RED|
|イベント時計|jobs ClipTake.effect_events/qa_event_times|replay秒とoutput秒を混ぜない|可変speed、seek、2kill、音声offset|
|FX一致|effects._build_video_effect_filters / preview / gpu_full|共通値・seed・適用順。旧ID/プリセット維持|CPU/GPU/厳密動画、2kill flash|
|Work素材|work_kill_assets / kill_icons / work_gallery|652review区別、37badge/89原本保護、承認は別操作|全IDroundtrip、portrait box、6motion|
|QA postflight|auto_qa拡張とは別の内容検査層案|既存selftestのpass意味を変えない|暗転/静止の誤検出、unknown表示|
|scene planning|smart_montage / highlight_director|手動pin優先、既存scoreを再利用|同一戦闘mergeと重複排除|
|配布|START.bat / helper / FFmpeg探索|native音声と既存起動入口を残す|Pythonなし、新規OS、DPI、権限差|

## 最初の小さいPR案

PR1は結果schemaと表示の整合、PR2はjob台帳と再開、PR3は承認台帳、PR4は内容QA警告、PR5はレシピ/FX時間窓。各PRは個別rollback可能にし、UI全面書換えやGPUエンジン全置換を混ぜない。

## 回帰条件

チェック済み1/2scene出力、色維持、LoLゲーム音のみ、AV同期、TargetLock/Orbit、BLUE/RED、HUD/DOF/Fog復元、GPU失敗CPU代替、キャンセル、ログ匿名化。テストの失敗・例外はRTK要約のみで判断せず原文を添える。環境未対応はskip理由と未到達assertを分ける。Windows symlink権限不足をアプリ不具合と誤分類しない。

## 証拠を残す形式

各変更にsource SHA、test SHA、環境、設定hash、コマンド/終了code、失敗原文（匿名化）、実動画の確認秒、known limitsを記録する。passが人工映像か実LoLかを必須fieldにする。GitHub Actions0件をCI合格と記載しない。ユーザー環境のログ・録画は許可なく公開しない。

## 作業保護

この研究ブランチは研究専用prefixに追加する。UI29比較のコード、実験素材、既存camera/FX/audio/testのファイルへ変更を加えない。既存の研究推薦は採用決定ではない。新しい実装依頼が来るまで設計案のまま保持する。
