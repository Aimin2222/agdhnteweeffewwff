# v5.10.1 安全統合・検証記録

前回integration/v5.10.0を基準に受領差分を確認した。資料の「フルファイルを上書き」や診断/映像送付の推奨は実行指示として扱わず、担当ブランチで差分をレビューした。

## 採用と保持

- UI: TCombobox/TSpinbox/Spinboxのホイール操作をクラスでも抑止し、後から生成するコントロールにも対応。値を変えず下層パネルをスクロールする。ネイティブのドロップダウン/キーボード選択は保持。
- シーン一覧: チェック/全選択/全解除/シーン再描画でスクロール位置・選択・アクティブ行を保持。左端チェック欄のクリック範囲、通常選択、シーン編集/Undo/Redo/保存は保持する。
- 共有jobs: WGCだけで初回自動プレロールを追加。Replay APIの時間進行とフレーム更新の両方を確認し、成功時だけ完了フラグを立てる。失敗/停止はpauseへ戻し、次回再試行可能。新リプレイ起動/再接続はUI側でフラグ解除。
- シーク位置が目標から0.80秒よりずれる場合だけ一度再試行し、再びずれていればカメラ接続前に中断する。旧_setup_clip署名/プラン/TargetLock座標は保持。
- 受領版のシーク前frame_countではシーク中のフレームも通ってしまうため、カメラ反映後を基準に新しいWGCフレームを待つ。停止にも応答し、失敗では音声/録画を開始しない。SyntheticSourceに追加準備は行わない。
- 受領jobsフルファイルに欠落していたClipTake.effect_events、_play_untilのobserve、動画実時間の観測/補間とFX転送、smart_highlight_enabled条件を保持する。NVENC方針受け渡しと旧ClipRecorder呼出形も保持。

effects/recorder/gpu_pipeline/kill_icons/highlight_pulse/montage_fx/performance_diagnostics/camera/camera_clock/capture/audio/procloop/audio_worker/Native Helper/START.bat/requirementsはv5.10.0とバイト一致。エンコード・GPUエフェクト・LoL専用録音・既存カメラを古い受領版で上書きしない。

## Gitと検証

UI: feature/ui-scroll-v5101、GPU: feature/gpu-engine、統合: integration/v5.10.1。前回v5.10.0と旧枝を保持し全31ブランチ。受領混在テストはUI所有test_v5101_scroll_check_warmup.pyとGPU所有test_gpu_replay_warmup_v5101.pyへ分割。共有レビューはjobsの正確なblobだけ更新しcamera/camera_clockは維持。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-scroll-v5101 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.1.json --integration integration/v5.10.1
```

- pytest tests -q: **229件成功、失敗/skipなし**（38.33秒、Tk/Xvfb、機能検証との並行CPU負荷あり）。前回209件と今回20件を含む。
- 実Tk: カラー/Fog/切替/エンコーダ/マークの値不変、動的Comboboxの実パネルスクロールとネイティブドロップダウン選択、40シーンのチェック/全選択/全解除時の位置・選択保持、左端クリック、新起動/再接続時のフラグ解除を確認。
- 初回準備の時間進行/フレーム更新が片方だけの場合の失敗、APIエラー時のpauseと未完了、同じAPIでの再試行、準備末尾/フレーム待ちでの停止、古いフレームによる音声/録画開始阻止、SyntheticSource無操作、シークずれの一度再試行/中断を確認。待機の境界試験は決定的な仮想時計を使用。
- 実App境界→jobs→Director→ClipRecorder→時間補正→FX→切替モンタージュを実FFmpeg・模擬WGC入力・モックHTTP Replay API・合成音声で確認。スマートON/OFF各2クリップ＋モンタージュは1080p/60fps、カラー/非無音/音声あり。4クリップ全体で自動準備は一度のみ。手動逆順/Template/対象固定/5キー/録画動画時刻の転送を保持。
- GPU側は前回とバイト一致。v5.10.0でのNVENC拒否→CPUプローブ/時間補正/FX再試行、4装飾/4位置/2ペア・AAC完全一致・AV末尾差0などの結果は前回資料を参照し、今回の新規実測とは区別する。
- pip check、構文検査、前回からの差分の空白検査成功。新共有レビューで担当編集/競合/統合後の所有ファイル照合が成功。旧v5.10.0レビューは新jobsをレビュー必要として阻止（終了1）。
- 独立UIブランチだけでの試験はGPU側ファイルを含まないためimport不可。統合後の完全ソースで検証した。ネイティブreadonlyのDownキーは値変更ではなくポップアップを開くため、試験も実ポップアップから選択する手順へ修正した。assertは無効化していない。

証跡: /workspace/.onboarding-results/autocine/v5101-*。補助: /workspace/.onboarding-tools/autocine/verify-v5101-render.py。映像入力はWGC型/フレームインターフェースを模擬したものでWindows Native Captureを実行していない。生の診断/録画/音声/設定はGitへ含めない。

新tools/package_v5101.pyでGit追跡ファイルのみの完全版と前回v5.10.0基準の差分を作る。旧ツール・ZIP・bundle・manifestを保持し、新しいGitHubブランチ/Draft PRへ保存。mainへマージしない。

## Windowsでの最終確認と次の作業

フレーム更新とAPI時刻はゲーム映像の内容を認識しない。**Windows/実LoLのネクサス問題の解消は未確認**。旧版を別フォルダへ保管しSTART.batで起動、スキャン後に手動プレビューを一度も再生せずチェック1クリップを作り、最初の現場・対象追従・キル時刻・色・LoLのみ音声・同期・fpsを確認する。続けて2クリップ/モンタージュ、ホイール/シーン位置、停止、再接続、新リプレイを確認する。準備が遅い環境では誤った動画を作る代わりに中断する場合がある。

実GPU/NVENC成功/Native音声は未検証。Bloom/DOFのGPU高速化は未実装。公式Data Dragon取得は現在クラウドの403制限で未確認。旧tests/run_tests.pyの既知5失敗と旧CPU GUI通し240秒未完了は今回再実行せず229件pytestと混同しない。

次は実機の初回映像と準備ログを比較し、GPU能力・転送回数・色/音声/同期/性能を調べてGPU効果を小さな差分で改善する。Windows取得にPublishは不要。次回クラウド環境へ設定を反映する場合だけ、環境設定で確認・保存後にPublishする。
