# v5.10.4 UI統合 / GPUFX Capture60

## 統合方法と維持した処理

UI側から受領したv5.10.4差分を統合。更新済みlegacy_app.pyをそのまま置き換えると既存MirrorFix/HangFixが失われるため、feature/ui-circle-v5103を共通基準として3方向でマージし、競合2箇所は既存非同期状態/監視終了処理と新しいプレビュー状態の両方を保持した。既存ミラーON/OFF/開始停止、非同期接続状態/GPUプローブ、終了、UI pump、映像準備、選択/全/チェック書き出しなど15メソッドはAST一致で維持を検査。

タブのホイール誤切替防止、カメラ再生中のミラー内簡易FX、録画・書き出し中はFX停止を適用。ミラー簡易FXはCPU/PIL、カメラのみのプレビュー時は約15Hz、書き出し中は約10Hzの非加工表示。LoLゲーム本体に画像加工を送る機能ではない。

core/camera.pyとcore/replay_api.pyも受領内容を共有境界としてレビューし、GPU側の専用ブランチへ分離して統合。HTTPS Keep-Aliveの接続再利用、遅いAPIに限る姿勢変化制限、細かい速度POST削減を適用。既存TargetLock座標系/リグ/カメラ公開引数/時計の144Hz/最大60Hzを維持。受領cameraの全モードへの速度下限0.40は従来0.35倍スローを変える回帰だったため、既存smart演出のみに適用して従来速度を維持。再生時刻確認0.5秒、全スタイルへの既存適応間隔適用も差分として確認。ReplayAPI公開get/post/seek/render/playback等を維持しcloseを追加。ローカルRiot自己署名TLS扱いは従来からの仕様で、外部ダウンロードのTLS/ハッシュ検証は変更しない。

core/effects.py・gpu_pipeline.py・gpu_bloom.py・gpu_binary.py・recorder.py・jobs.py・capture関連・focus_fx.py・preview.py・LoL専用音声/Native/START/依存などは前回Capture60とバイト一致。録画→必要な時間補正→加工→出力の標準60fps、GPU Bloom/円形DOF/Focus Blur、GPU失敗→CPU再描画、NVENC失敗→CPU、色/音声/時刻保護を維持。今回のUI ZIPでGPUコアを上書きしていない。

## 新しいWindows診断のCPU/GPU結果

これは統合前のv5.10.3 GPUFX Capture60実機結果。録画4本すべてoutput_fps=60、加工前のeffects_fps=60。約9.17～9.20秒の素材4本、BloomはGPU OpenCL、エンコードはh264_nvenc、returncode=0/gpu_effects_confirmed=true。加工46.927/47.611/50.160/51.644秒、必要な時間補正2.833～3.120秒、モンタージュ12.410秒で成功。runtimeは4本完了。今回DOFはGPU選択一覧にないため、この診断からDOF稼働は主張しない。

CPU処理は残る。実FFmpegグラフのscale・eq・colorbalance・vignette・noise・drawbox・fade・format等はCPU。取り込み/デコード/CPU⇔GPU転送、ミラー簡易FX、タイトル/肖像合成、音声mux/API処理もCPU部分がある。NVENCやBloomがGPUでも全工程がGPUにはならない。GPU使用率平均28.44～31.40%、システム全体CPU平均83.39～88.02%はアプリ単独のCPU値とは区別。cpu_video_effects=[]は追加video_effects辞書が空という意味で、色グレード・粒子・形式変換を含む全CPUフィルターが空ではない。設定が異なるため前回診断との厳密な改善率は算出しない。

元診断ZIP/個人パス/プレイヤー情報/録画をGitへ入れず、集計だけをVERIFICATIONへ記録。Windowsでこの新v5.10.4統合版のカメラ滑らかさ/Keep-Alive/ミラーFX/音声同期はまだ未検証。

## 検査と並行開発

UI: feature/ui-notebook-livefx-v5104。GPU/共有橋渡し: feature/gpu-shared-v5104。統合: integration/v5.10.4。旧GPU/UI/統合ブランチと全配布物を残す。新しいcore/camera.pyとcore/replay_api.pyの正確なblobをCODEX_SHARED_API_REVIEW_v5.10.4.jsonで承認し、旧jobs/capture/clockの承認を維持。公開API変更を無条件承認しない。core/replay_api.pyは共有境界として扱い、担当検査から隠さない。

受領5テストで実Tkタブ/プレビューFX/カメラ制限とHTTP/1.1接続再利用を検査。追加3テストで実HTTPのConnection: close後の再接続、HTTP500後の再利用、応答消失POSTを重複送信しないこと、同時問い合わせの直列化/共有接続を検査。既存HTTP/1.0モックAPI、カメラTargetLock、FPS/時刻、GPU/CPU、LoL音声、実Tk/子プロセスを含む全回帰を実行。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-shared-v5104 --ui feature/ui-notebook-livefx-v5104 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.4.json --integration integration/v5.10.4
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
```

CPU負荷削減の次候補は色補正・粒子等と転送。画質/色/イベント/音声を保つ実行比較が必要で、今回はUI統合中に新しいGPU効果を混ぜない。診断にないGPU稼働や改善率は主張しない。

## Windowsで取得・確認

codex/lol-autocine-v5104-handoffのCode→Download ZIP、旧版とは別フォルダに展開してLoL_AutoCine/START_GPU.bat。タブ上のホイールでタブが変わらずクリックで変わること、ミラーONとFX反映ONでカメラ再生中の円形ぼかし、録画中のFX停止、同じ1シーンのTargetLock/色/LoLのみ音声/同期、4シーン連続を確認。カメラAPI待ちのログも前回と比較する。

完全版/前回Capture60との差分/全ブランチbundleはtools/package_v5104.pyで生成。配布名v5.10.4_GPUFX_Capture60。GitHubのDraft PRに保存しmainは未マージ。Windows取得/起動に環境Publishは不要。
