# T01〜T14実行可能な比較試験仕様

全項目を対象化。製品の完全PASSは0。PARTIALは研究の限られた実行範囲であり、テスト全体合格ではない。REPRODUCEDは問題再現。実機入力はユーザー/Codexが同patchのreplayから用意する。未提供fixtureを存在するファイルとして扱わない。

## 共通の実行/保存規約

実行前に本体commit、patch、匿名replay hash/対象/陣営、job snapshot、素材ID/hash/status、解像度/fps、camera原値、FX revision、motion、encoder、GPU FX device/driver、音声policyを固定。各runへinput.json、events.json、time_maps.json、ffmpeg_args.txt、匿名化log、output metadata/sha256、human_review.json、result.jsonを保存。私的なprocess名/アカウント/パス/生音声は公開しない。expected/observed/status/reasonを別欄に持つ。

原文のテスト失敗や例外をRTKで省略しない。CPU/GPUの品質比較は同take、参考映像は構成や時間関係の手本でありpixel一致の正解ではない。

## T01 BLUE/REDと旧10camera

状態：**UNEXECUTED_LIVE**。今回の結果：camera原文/全tree差分のみ確認、実Replay fixture未実行

入力：同patch/replayでBLUE/RED各2scene、左右配置違い、各旧10style、TargetLock on/off

期待値/合格条件：陣営/target取り違え0、未申告lock解除0。除外cameraへfallbackしない。未承認陣営を自動合格にしない

比較対象：元UIの同一設定出力・Replay対象と陣営

手順：対象選択→各styleを両陣営でpreview→同時刻takeを記録→左右/軸/対象を照合

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T02 eventとscene anchor

状態：**UNEXECUTED_LIVE**。今回の結果：no-kill fallbackの原文確認のみ。engage独立検出の新実装を既存扱いしない

入力：kill/assist/engage各1、no-kill1、同時/重複/境界event

期待値/合格条件：kill/assist種別一致、no-killで偽ChampionKill0、seek不連続mapなし、anchor誤差はoutput1frame以内の提案基準

比較対象：API/eventの正解annotation、V2の視覚beam候補とは分離

手順：全体scan→scene選択→event source照合→時刻mapをdump→cut前後を再生

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T03 連続kill/FX重複

状態：**PARTIAL_SYNTHETIC**。今回の結果：既存badge_planの5event/max3を実計算。実映像/新group plannerは未実装

入力：人工event.5/.6/.7/.8/1.0、実3kill以上を短間隔/長間隔で各1

期待値/合格条件：最大stack3という旧挙動を保持、group最後のみ設定で1pulse、manual override記録、戦闘途中の意図しないcut0

比較対象：旧badge_planと新group plan、FX off baseline

手順：group境界を表示→manual/auto比較→各kill/peak/transition時刻をframe記録

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T04 dash/壁/遮蔽/姿勢

状態：**UNEXECUTED_LIVE**。今回の結果：動画参考を観察、AutoCine候補収録/追跡は未実行

入力：BLUE/REDのdash/壁際/jungle/低角度scene、意図roll区間

期待値/合格条件：hard gate違反候補を選ばない。不明depthは要確認。通常/意図transition域を分け、未知を安全確定にしない

比較対象：同時刻wide baseline、planner候補take

手順：cameraごとに記録→対象/地形/姿勢を区間annotation→候補scoreとfallback照合

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T05 ゲーム状態QA誤検出

状態：**PARTIAL_SYNTHETIC**。今回の結果：人工14/14期待一致。LoL標本の誤検出率は未測定

入力：deathgray/lowHPred/teleport/recall/intentionalblack/still、対照capture故障

期待値/合格条件：人工期待集合一致。LoL false-positive率は独立clipで測定してから判定。色だけで自動修復0

比較対象：人のcontext annotation、14人工fixture

手順：同一検出設定で正常/異常を混ぜる→ruleごとTP/FP/FN/TN→閾値検討

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T06 全687素材

状態：**PARTIAL_MECHANICAL_AND_VISUAL**。今回の結果：機械687、thumb687、FX原寸35、端74部分とsourcecrop、083×FX140。frame全体原寸/実HUDは残件

入力：652frame/35FXの固定catalog、原本89、旧37、実顔2種類/明暗/複雑HUD

期待値/合格条件：機械687一致、全件の視覚欄を記録。thumbを原寸/動画合格へ昇格しない。未承認は維持

比較対象：hash台帳、原本mask/ROI、承認状態

手順：全hash/decode→原寸/背景/顔穴→左右/stack/HUD→全件台帳→別担当審査

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T07 6motionの全過程

状態：**PARTIAL_SYNTHETIC**。今回の結果：1080p60矩形6本各132frame decoded、3size式計算。全実素材/30fps/他size実encode未実行

入力：6motion×30/60fps×1920/1366/1280、代表円/四角/八角/横長frame、連続5event

期待値/合格条件：source式どおり.260s slide、pop左右振動、旧/Work開始時刻の違いを維持。静止後の意図しないclip0

比較対象：旧式数値、静止承認と動画審査を分離

手順：登場/定着/退場全frameをdecode→位置/alpha/顔同期/端/stackを測定→実HUD比較

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T08 preview/exact/final

状態：**UNEXECUTED_PRODUCT**。今回の結果：近似/厳密/最終の原文差を整理。実アプリ比較未実行

入力：同scene同時刻、temporal blur/flash/Workpeak on/off、同じsnapshot

期待値/合格条件：modeを偽らない、静止だけのtemporal合格なし、final graph/設定/時刻map一致

比較対象：軽量preview/厳密静止/最終decode frame

手順：3modeを表示→同time mapでjump→時間FXは前後frameも並べる→差の由来記録

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T09 multi flash/retime時刻

状態：**REPRODUCED_ISOLATED_NOT_PRODUCT_PASS**。今回の結果：旧式first-event-onlyを再現。255/127/127。空[]helper IndexError、通常fallback経路のcrashとは断定せず

入力：灰色3秒60fps、.5/1.5/2.5event、scene端、空配列、piecewise retime

期待値/合格条件：各eventの中心/幅を期待revisionどおり出す。旧compatと修正を別判定、map誤差≤1frameの提案条件

比較対象：旧graph/修正候補graph、event正解

手順：immutable関数抽出→FFmpeg実encode→各event±frame輝度→app同fixtureで追試

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T10 CPU/GPU FXとencode

状態：**PARTIAL_NVENC_SMOKE**。今回の結果：人工1秒1080p60 h264_nvenc成功。GPUFX/LoL競合/長尺未実行

入力：1080p60の同take、CPU/GPU FX×NVENC/CPU encode、FX強度2段階、10分stress

期待値/合格条件：同解像度/fps維持、fallback記録、GPUencode成功をGPUFX合格にしない。品質許容値は同一fixtureで事前指定

比較対象：同decode frame/音声/色と単位時間/peak memory

手順：device能力検出→4組実行→失敗fallback→出力decode→fps/時間/負荷比較

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T11 LoL専用音声/retime

状態：**PARTIAL_ARTIFICIAL_AV**。今回の結果：人工setpts/atempo/AACで約24.2msの閾値開始差。LoL音声/実app同期未検証

入力：実LoL音、別アプリ音、capture失敗、音声必須/任意、人工同期burst

期待値/合格条件：desktop混入0、必須音声失敗は成功扱いしない、任意無音は明示。同期許容±1frame等は実測基準を承認して使用

比較対象：元LoL対象process音とcapturePTS、人工marker時刻

手順：別app音を同時再生→LoL専用録画→retime→track/PTS/markerを確認→故障注入

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T12 同一takeのrecipe比較

状態：**UNEXECUTED_NEW_FEATURE**。今回の結果：6recipeは仕様のみ。本体未実装

入力：固定replay/take/patch/seed/targetで6recipe draftとFXoff

期待値/合格条件：異なる作品間SSIMを合格基準にしない。HUD/主役/連戦理解/clip構成を人が審査、手動override保持

比較対象：同一frame baseline、参考動画は意味構造の比較だけ

手順：原出力を固定→各recipe設定diff→同時刻frame/短動画→人の比較とmasked差分

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T13 素材・project互換/保護

状態：**PARTIAL_HASH_AUDIT**。今回の結果：全素材/原本/旧badgehashと最新tree不変を確認。UI roundtrip/実app試験は未実行

入力：旧catalog、旧37IDs、原本89、approved1/review651+35、旧project10camera/FXID

期待値/合格条件：原本/素材hash/承認変更0、ID欠落0、UI/theme切替でproject/preview reset0、未承認を正式扱いしない

比較対象：before/after hash、旧template snapshot

手順：readonly台帳→UI変更→project roundtrip→hash/enum/状態比較→未知field保持

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。

## T14 job resume/長尺/配布

状態：**UNEXECUTED_PRODUCT_AND_DISTRIBUTION**。今回の結果：job checkpoint仕様を作成。実製品への実装/故障注入/clean-PC検査は未実行

入力：30clip/30分以上、clip失敗、cancel、途中終了、破損checkpoint、空き容量不足、PythonなしPC

期待値/合格条件：validated/hash一致clipのみ再利用、破損/patch違いreuse禁止、音画尺/metadata一致、cancel後未完を成功扱いしない

比較対象：初回正常jobmanifestと再開後成果、既存atomicproject保存

手順：preflight→capture→途中失敗→再起動→整合性確認→失敗clipのみ再試行→mux→全decode→別PC起動

保存：共通ログ一式。対象別のmetric（camera/alpha/輝度/audio/framecount/承認等）をresult.jsonへ記録。
