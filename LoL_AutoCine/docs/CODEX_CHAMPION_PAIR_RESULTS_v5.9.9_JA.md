# v5.9.9 ChampionPairFix 安全統合・検証記録

## 採用と修正の保持

受領ChampionPairFix差分の目的は、文字付きキル装飾をキラーと犠牲者のチャンピオン肖像ペアへ変更し、同じクリップ内でも相手画像をキルごとに切り替えること。資料の画像/診断送付推奨はユーザーの外部送信依頼とは扱わない。提供側の165テスト成功と今回の実測を区別する。

- 受領core/effects.pyフルファイルには前回のeffect_events引数と録画実時間への補正がなく、受領kill_icons.pyにはshortest=1への巻き戻りがあった。全ファイル上書きをせず差分をレビューし、末尾の任意effect_events引数とshortest=0:eof_action=repeatを保持して新ペア経路へ接続した。
- legacy_app.pyフルファイルはv5.9.8表示へ戻っていたため、採用はcurrent_templateの全プレイヤー情報のプレーンdictスナップショット1行のみ。レイアウトとv5.9.9表示を保持。UIスレッドで読み、渡したデータはプレイヤー一覧から独立する。
- Template.kill_icon_playersを末尾へdefault_factory=listで追加。旧位置引数と独立した既定値を確認。シーン適用のdeepcopyで一覧も保持する。
- 名前はチャンピオン名から推測せずプレイヤー名で照合する。同名の複数プレイヤーは省略し、タグ付きの完全一致を優先。Wukong等の既知IDとFiddleSticks→Fiddlesticksの正式ファイル名を正規化する。どちらかの情報/画像がない場合はペアを省略する。
- Riot Data DragonのTLS検証を維持した画像取得、ローカルPNG/キャッシュの検証、オフライン利用を採用。各クリップで同一チャンピオンを一度だけ検索し、失敗でもキル数分の再接続をしない。省略理由はプレイヤー名を含めず警告へ記録する。
- 後続キルの表示開始で前ペアを終了し、同時刻は最後のペアを表示する。複数PNGに合わせてタイトル/ゲーム音/BGMの入力番号を更新し、GPU失敗時のCPU再試行・色保持再試行にも同じペアを渡す。
- camera/jobs/audio/Process Loopback/recorder/gpu_pipeline/Native Helperは前回v5.9.9とバイト一致。共有承認は変更がないためdocs/CODEX_SHARED_API_REVIEW_v5.9.9.jsonを保持。装飾はCPU overlayでGPU高速化ではない。

## Gitと検証

UI: feature/ui-champion-pair-v599、GPU: feature/gpu-engine、統合: integration/v5.9.9-champion-pair。前回integration/v5.9.9と旧ブランチを保持し、全27ブランチ。肖像レンダラの受領テストはGPU所有、オフライン配置説明はmetadataとして実Gitガードで検出を確認。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-champion-pair-v599 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.9.json --integration integration/v5.9.9-champion-pair
```

- pytest tests -q: **182件成功、失敗/skipなし**（16.82秒、Tk/Xvfb）。旧機能、肖像ペア、同名/タグ/欠落、旧位置引数、OFF、イベント補間・動画打切り禁止、取得模擬/オフライン、UIスナップショット・Git担当検査を含む。
- Python74ファイルの構文、pip check、今回差分のgit diff --check成功。
- 実Tk→worker→jobs→Director→モックAPIでプレーン一覧スナップショット、5キー・対象固定・health HUD/復元、チェック2シーン一括・Undo/Redo・自動保存・JSON往復・コピー独立・UI/worker分離・保存済みJSON不変を確認。
- 実apply_effects/FFmpegで合成肖像の異なる2ペアを4装飾/4位置で1080p/60fpsへ出力。任意の動画実時間1.2秒/2.1秒に相手色が青→緑へ切り替わること、表示前と全表示終了後、カラー、通常版とのAACデータ完全一致、AV末尾差0、成功時のペアPNG削除を確認。実チャンピオン画像の見た目の検証とは区別する。
- タイトル＋2ペア＋ゲーム音＋BGMの実出力と入力接続を確認。GPUフィルター失敗を模擬した実FFmpeg失敗→CPU再試行でもペア/AACを保持し、AV末尾差0。実GPU成功ではない。
- 公式Data Dragonへの実アクセスはクラウドのHTTPSプロキシから403 Forbiddenで拒否された。実画像取得は未検証。模擬通信による正しいURL/PNG検証/キャッシュ再利用と、合成ローカルPNGのオフライン経路は成功。既存の許可先を保ち、公式画像ドメインddragon.leagueoflegends.comを環境設定ドラフトへ追加する。ドラフト保存だけでは現在の403解消を意味しない。
- パッケージツールはChampionPairFixの説明ファイルを検出すると固有の完全版/差分ZIP名と前回v5.9.9基準を選ぶ。従来v5.9.9の取得用ZIP/履歴を上書きしない。Git追跡ファイルだけを採用し、個人設定・録画・音声・未追跡画像は含めない。

ローカル証跡: /workspace/.onboarding-results/autocine/v599-pair-*。補助: /workspace/.onboarding-tools/autocine/verify-v599-pair-{ui,badges}.py。生成映像・音声・設定・公式画像キャッシュをGitへ含めない。

## Windowsと次の確認

Windows/実LoL/GTX 1070 Ti/Native録音/実NVENCは未検証。旧tests/run_tests.pyの既知5失敗と旧CPU GUI通し240秒未完了は今回再実行せず、182件pytest成功と区別する。Bloom/DOFのGPU高速化は未実装。

別フォルダに完全版を展開してSTART.batで起動。10人取得→対象固定→スキャン後に、装飾OFFの通常編集と4装飾、異なる犠牲者の連続キル、スロー時の表示、位置/サイズ/秒数/濃さ・保存復元、カラー・LoLのみ音声・対象追従・HUD・fpsを確認する。画像の初回取得には公式サイトへのネット接続が必要。キャッシュ先はWindowsのLOCALAPPDATA/LoL_AutoCine/champion_icons。未取得時は装飾を省略し、手動のassets/champion_icons/<ChampionID>.pngでも利用できる。

新しい取得用GitHubブランチとDraft PRへ保存し、mainへマージしない。Windows取得にPublishは不要。将来のクラウド復元設定へ反映する場合だけ環境設定を確認・保存・Publishする。公式画像取得の403は環境設定反映後に再検証する。
