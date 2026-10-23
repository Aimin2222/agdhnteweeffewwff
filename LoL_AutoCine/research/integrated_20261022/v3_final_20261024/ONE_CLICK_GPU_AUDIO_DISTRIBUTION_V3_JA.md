# ワンクリック・再開・GPU・音声・Windows配布

## ワンクリックの失敗点と復旧

preflight→Replay接続/patch→対象/scene確定→capture→FX→encode→mux→decode QA→成果manifestの状態機械を提案。preview再生/停止と実動画作成は別command。開始時にimmutable settings snapshotを作り、編集中の変更を進行jobへ混入させない。

|失敗|提案する復旧|再利用/停止条件|
|---|---|---|
|Replay不在/patch不一致|理由と対象を表示、利用者が再接続|cameraを動かすPOSTを無条件再送しない|
|scan/event不足|取得範囲/endpointを表示、元scene保持|beam推測でkillを捏造しない|
|capture停止/音声必須失敗|clipをfailedにしrawを隔離|無断desktop audio fallbackなし|
|GPU FX unavailable|policyに従いCPU処理へ、差分表示|GPU encode可否とは別判定|
|NVENC失敗|CPU encode案、予想時間と条件を表示|1080p60を無断低下しない|
|一部clipのFX/encode失敗|rawが健全なら当該段階のみ再処理|原take/settings/assets hash一致が必要|
|disk不足/cancel|完了clipとcheckpointを保持、明示中断|未完fileを成功出力にrenameしない|
|最終mux失敗|validated clipからmux再試行|各clipのdecode/音声方針/PTSを照合|

現在のatomic project保存（temp/fsync/replace）とjob再開checkpointは別。研究のcheckpoint schemaを既存実装済みと扱わない。checkpointはjob専用folderへ原子的に保存し、phase/attempt/error/入力hash/成果hash/manifest versionを持つ。resume時にpatch/source/settings/素材が違えば再利用禁止を明示。validatedかつhashとdecodeが一致したclipだけ再利用する。failed clipのみのretryは最大2回案、同じエラーは無限再試行しない。cancelは停止要求を確認しプロセス終了待ち/一時file状態を記録する。

## GPUと1080p60

今回はWindowsのFFmpeg7.1 h264_nvencで人工1秒1080p60の実encodeが成功した。これはGPU FX、LoL描画競合、長尺性能、完成アプリを合格にしない。encodeとOpenCL FXを独立した能力表示にし、decode/scale/CPUfilter/転送/encode各区間の時間とmemoryを計測する。CPU fallbackで品質と解像度/fpsを保てても処理時間は増える。低負荷レシピの効果は実測後に報告する。

30分/30clip以上、3段badge/重いFX、別take候補、LoL同時動作でwalltime、平均/最悪fps、RAM/VRAM peak、drop、temp diskを測定。capture60fpsとencode60fpsタグを区別し、欠落/重複frameやPTSを調べる。最初はcapture/重いFXの同時数を1とする提案、余裕を測って増やす。長尺全frameをRAMへ保持しない。clipごとのrawを安全に再利用し、勝手に削除しない。

## 音声

LoLプロセス専用captureを維持し、別app/desktop音を含めない。source processの再起動/失敗はpolicyに従い明示し、音声必須なら成功を返さない。任意無音は成果manifestへ記載。BGMとLoL音のgain/音量正規化は別field、retime後はvideo/audio共通のtime map。AAC先頭delay、resample、atempo過渡、切出し、mix長を人工markerと実LoLで確認する。今回の人工pulse約24.2ms差から実game同期の良否を推定しない。

## パッチ/APIと配布

preflightへreplay patch/game version/API endpointと必要field型を記録。未知patch/欠測は警告、parse失敗を空event成功にしない。保存fixtureをread-only contract testにし、camera POSTは使い捨てテストReplayでのみ実行。UI統合直前に最新commitとの差分を取得し、core変更があれば該当研究/回帰を更新する。

[Microsoft公式WebView2配布資料](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)に基づきRuntime存在を確認する。Evergreenのonline bootstrap/offline installerとFixed Version同梱を比較し、配布方式/更新責任を決める。EdgeがあるだけでRuntime存在を保証しない。ライセンス/容量/architecture/ネット無しの起動をclean Windowsで検査する。

[PyInstaller公式](https://pyinstaller.org/en/stable/operating-mode.html)はinterpreterをbundleしPython不要の配布を可能にするが、OS/bitnessに依存する。AutoCineで必要なDLL/FFmpeg/QtまたはWebView2/画像/モデル等は別途収集確認が必要。Pythonを消した普段のPCではなく、Pythonなしのclean VM/別PCへEXE/ZIPを展開し、標準ユーザー/日本語とspaceのpath/offline/初回起動/動画出力をT14で確認する。今回はビルド/配布/署名/clean-PC合格を行っていない。

## 匿名診断

診断は版・匿名jobID・相対clipID・stage/error code・設定の必要最小値・能力フラグ・時間metric中心。ユーザー名、絶対path、Riot ID、token、IP、音声内容を既定除外。画像/音声/詳細logは利用者が内容確認して選択。送信は自動化せずローカルZIPから開始。障害原文はローカルで確認し、共有用のみredactする。研究で作った匿名テストlogと、ユーザーの実logを混在させない。
