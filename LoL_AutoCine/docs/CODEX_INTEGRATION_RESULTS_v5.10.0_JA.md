# v5.10.0 安全統合と検証記録

v5.9.9 ChampionPairFix統合版を基準に、受領v5.10.0差分をレビューして統合した。添付READMEの診断ZIP所見・183テスト成功・動画/診断共有の推奨は、Codexの実測やユーザーの新しい外部送信依頼として扱わない。大幅な作り直しは行わない。

## 採用した変更

- UI: Combobox/Spinbox上のホイールで値を変えずパネルをスクロールする。シーン一覧の左端チェック欄のみでON/OFF、文字側は通常選択。ホーム/テンプレート/参考/設定の実画面へのナビ、入力済み参考URLの利用を採用。
- キル装飾: 枠色/発光色、発光ON/OFFと強さ、枠幅、6中央マークを追加。4装飾/2チャンピオン画像/位置/サイズ/時間/不透明度を維持。色と数値を正規化し、旧Template位置引数を保つため7フィールドは末尾へ追加。
- エンコード方針: auto/gpu/cpuを録画・時間補正・FX・切替モンタージュへ渡す。CPU優先はGPUエフェクトの無効化ではない。NVENC登録一覧と実行結果を区別し、録画は開始前に実行プローブする。途中録画エラーは中断し、フレームを取り直したことにしない。
- 完成素材: NVENC選択時のFFmpeg失敗はlibx264へ一度再試行。入力、フィルター、音声map、FPSを保持し、-rなしのモンタージュにも対応。明示カスタムエンコーダは変更しない。時間補正失敗は元動画を保持してエラーを返す。
- 診断: 実際のコマンド/エンコーダと再試行理由を保存し、失敗/タイムアウトを成功やGPU実行確認済みと表示しない。GPU処理とNVENCを分けて表示。設定はJSONから再起動時も復元する。

## 巻き戻りの防止

受領effects/jobsフルファイルにはeffect_eventsと録画実時間の観測・補間が欠落していた。kill_iconsにはshortest=1、曖昧な名前照合、公式Fiddlesticks ID補正の欠落などがあった。フルファイル上書きは行わず、既存のeffect_events、shortest=0:eof_action=repeat、同名曖昧時の省略、正式ID、同一クリップ内の取得失敗の重複防止、同時キルの最新ペア、スマート計画の明示有効化条件を保持した。

共有jobsの前回からの変更はrec.encoder_policy設定とモンタージュの同名キーワード受け渡しだけ。camera/camera_clock/audio/Process Loopback/audio_worker/capture/gpu_pipeline/Native Helper/START.batは前回とバイト一致。エンコード・診断を変更するrecorderは独立レビューした。Bloom/DOFのGPU高速化やGPUフィルターの全面変更はしていない。

## Gitと検証

UI: feature/ui-killframe-v5100、GPU: feature/gpu-engine、統合: integration/v5.10.0。前回ChampionPairFixと全旧ブランチを保持し、全29ブランチ。共有レビューJSONは現在のjobs blobだけを更新し、camera/camera_clockの承認を保持。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-killframe-v5100 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.0.json --integration integration/v5.10.0
```

- pytest tests -q: **209件成功、失敗/skipなし**（19.16秒、Tk/Xvfb）。旧機能・GPU接続・イベント時刻・ペア表示、旧位置引数、今回のUI/設定/デザイン、NVENC再試行、録画途中失敗、CPU再試行タイムアウトの正しい診断、実Git担当検査を含む。
- pip checkと構文検査成功。GPU/UI担当相互編集・競合・統合後の所有ファイル不一致なし。旧v5.9.9共有レビューでは新jobsをレビュー必要として阻止（終了1）、新レビューでは成功（終了0）。
- 実Tk→worker→jobs→Director→モックAPIで5キー、対象固定、health HUDと復元、チェックシーン一括、Undo/Redo、自動保存、独立コピー、スレッド分離、保存済みJSON不変を確認。14項目の既存/新しい装飾・エンコード設定を実Tk再起動とJSON再保存で確認。
- 実apply_effects/FFmpegで4装飾/4位置、新色/発光/剣/枠幅と2ペアを1080p/60fpsへ出力。1.2/2.1秒で相手色が青→緑へ切り替わり、表示前/全表示後、通常版とのAAC完全一致、AV末尾差0、PNG削除を確認。肖像はテスト用合成画像。
- タイトル＋2ペア＋ゲーム音＋BGM、GPUフィルター失敗模擬→CPU経路を確認。NVENC選択を試験用に強制した実FFmpeg拒否→libx264再試行でもAAC完全一致・AV末尾差0。実GPU成功ではない。
- 実ClipRecorderのNVENCプローブ拒否→フレーム送信前にCPU録画（91フレーム/約1.505秒）。完成素材のNVENC選択を強制した時間補正は実拒否→libx264再試行、目標2.28秒に対し出力2.27秒。録画ログはCPU・理由付き、GPU効果成功と記録しない。
- 実App境界→jobs→録画→時間補正→FX→切替モンタージュを合成映像/音声・モックAPIで通した。スマートON/OFF各2クリップ＋モンタージュは全て1080p/60fps、音声あり、AV末尾差最大約0.056秒。手動逆順、Template、対象固定、5キー、録画中の動画時刻転送を保持。
- 追跡ソースだけの新package_v5100.pyで完全版と前回ChampionPairFix基準の差分を生成する。旧package_v599.pyと過去のZIP/bundleは保持。個人設定/プロジェクト/動画/音声/画像キャッシュ/.venv/ランタイム診断を含めない。

証跡: /workspace/.onboarding-results/autocine/v5100-*。補助: /workspace/.onboarding-tools/autocine/verify-v5100-{ui,settings,raw,render,badges}.py。生の診断や生成動画・設定はGitへ含めない。

## 限界と次の確認

Windows/実LoL/GTX 1070 Ti/実GPU/NVENC成功/Native録音は未検証。公式Data Dragonの実取得は現在のクラウドプロキシで403となり未検証。模擬通信・ローカルPNG・オフラインキャッシュは確認済み。既存環境設定ドラフトに公式ドメイン許可はあるが、保存だけで現在の403が解消したとは言わない。

旧tests/run_tests.py初回16件中11成功/5失敗（WAV不足4条件・低解像度静止画と1080p固定Bloom不一致）と旧CPU GUI通し240秒未完了は今回再実行せず、209件pytestと混同しない。

Windowsでは旧版を別フォルダへ保管し、新完全版のSTART.batで起動。10人取得→対象固定→スキャン、通常OFF/4装飾、連続する異なる敵、スロー時表示、色/発光/枠幅/中央マーク、ホイール/左端チェック/ナビ、設定再起動、LoLのみ音声/色/同期/HUD/対象追従/fpsを確認する。CPU優先と自動/GPU優先を比べ、実エンコーダ・エフェクト経路・理由を見る。

今後は実機のNVENCプローブ/フォールバックと診断を比較し、GPU効果の能力・接続条件・転送回数を調べた上でBloom/DOFを小さな差分で改善する。新GitHubブランチとDraft PRへ保存し、mainへマージしない。Windows取得にPublishは不要。将来のクラウド設定へ反映する場合だけ環境設定を確認・保存・Publishする。
