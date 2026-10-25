# 新機能仕様・19提案・PR分割
新提案はPROPOSAL19_ROADMAP_V4.jsonの19件を維持し、採用済み0。本体への実装0。ユーザーとChatGPTの採用判断後に着手。

| 順 | PR範囲 | 合格条件 | rollback |
| --- | --- | --- | --- |
| 0 | UI29候補を全維持し比較可能にする | ユーザー選択記録。勝手にE/A統一しない | 候補画像/画面IDを削除しない |
| 1 | 採用UIの既存70adapterと設定保存 | 70行全command/model/ログ接続、unknownfield/手動値/テーマ保持、仮値の実行禁止 | 元UI/旧projectで開ける状態へ戻す |
| 2 | 既存CPU Flashとempty guard | 採用済みrevisionのみ変更、単発bit回帰+全event検証 | revision切替off/legacy維持 |
| 3 | Zoomと寸法/preview-export parity | 同一入力3解像度のgolden、色/輪郭/時刻/旧保存互換 | 新graph/座標revisionoff |
| 4 | 素材geometry/FX safe area | ユーザー審査・元hash保持・37/89/652/35回帰 | 別metadata版を無効、承認状態保護 |
| 5 | Windows/LoL baseline実機T01–14 | 全14の証拠、BLUE/RED、TargetLock、録画、音声required、CPU/NVENC/GPU別 | 旧出力を比較用に残す、失敗新機能はoff |
| 6 | event TimeMap/group ShotPlan | synthetic+実scene正解、manual優先、未知でbaseline、最大3takeは提案設定 | 保存planを残しbaselineで再出力 |
| 7 | 6recipe draft/overrideとbest-shot optional | 同一take比較、scoreとconfidence/不採用理由、未知値null | recipe適用差分を取消、元設定復元 |
| 8 | 警告QA/checkpoint/audio/配布 | 誤警告率・長尺AV drift・失敗clipのみretry・PythonなしPC | QA自動変更off、checkpointから旧jobを保護 |
| 9 | 真radial/glow/空間wipe/beat/CG | 新IDと新規素材、負荷/著作権/同期を個別審査 | 旧IDへ代入せず新機能off |


各PRは独立fixture/期待値/実測/製品revision/変更前golden/rollback手順を添付。camera候補のtake最大3、group3秒、visibility.9は未検証の提案値。UI状態・テーマ変更はProjectState/preview/captureを再構築しない。LoLプロセス音声失敗をdesktop全音声に自動代替しない。選択UIの自動採用・素材自動承認は禁止。

| 提案ID | 内容 | 難易度 | 依存 | 試験 |
| --- | --- | --- | --- | --- |
| A01 | multi CPU flashの中心式 | 中 | 原文と独立再現、最新job追試 | T03/T09/T08 |
| A02 | 空event helperとcall path防御 | 低 | 通常fallback経路の到達性確認 | T02/T09 |
| B01 | 旧10cameraとTargetLockのUI接続 | 中 | UI選定と旧設定fixture | T01/T13 |
| B02 | 旧FX ID/保存revision互換 | 中 | 旧project/golden output | T08/T09/T13 |
| B03 | 素材状態/顔形状/旧37の保持 | 中 | 素材審査・portrait metadata | T06/T07/T13 |
| B04 | 70機能adapterとtheme状態保持 | 高 | ユーザーUI選定 | T01–T14の既存該当範囲 |
| C01 | event/capture/output時刻map統一 | 高 | 録画時刻正解fixture | T02/T03/T08/T09/T11 |
| C02 | preview modeと最終graph差の説明 | 中 | 時間FX fixture | T08 |
| C03 | frame/peak/HUD safe-area審査 | 中 | 原寸審査と実顔/HUD | T06/T07 |
| C04 | GPU FX/encode別のfallback診断 | 中 | 実device/LoL同時動作 | T10/T11/T14 |
| D01 | checkpoint/失敗clipだけretry | 高 | settings/input/output hash設計 | T14 |
| D02 | group-aware shot list | 高 | 旧機能Windows合格/ユーザー採用 | T01/T03/T04/T12 |
| D03 | 複数takeのbest shot採点 | 高 | D02/可視性データ/正解annotation | T04/T10/T12 |
| D04 | 警告中心output QA | 高 | 負例annotation/metric由来 | T05/T06/T10/T11/T14 |
| D05 | 6recipeのdraft適用/override保存 | 中 | ユーザー採用/C01/D02は任意 | T12/T13 |
| E01 | 本物のradial/glow/空間wipe | 高 | 互換revision/B02 | T08/T09/T10 |
| E02 | 音楽beat同期/外部CG intro | 高 | 音源/映像素材と権利/長尺UX | T11/T12 |
| F01 | BLUE/RED実動/LoL専用音声/長尺1080p60 | 中〜高 | ユーザーWindows Replay fixture | T01/T04/T10/T11/T14 |
| F02 | WebView2/PythonなしPC配布 | 中 | clean Windows/依存bundle | T14 |
