# v5.10.3 統合・検証記録

基準はローカルのintegration/v5.10.1（169fedca69010785350c9285748c7df730786705）。受領ZIPのREADMEとv5.10.2→v5.10.3パッチを確認したが、v5.10.2完全版は提供されていないため、同梱のフルファイルから必要な差分をレビューして採用した。v5.10.2の独立した動作版/履歴/READMEがあるとは扱わない。

## 採用した変更

- 円形DOFのCPUマスク・軽量プレビュー・UI位置調整・おすすめ設定。半径は画面高さ基準、480×270マスクを1080pへ拡大し、540pでぼかす。内側の原画と外側のぼかしを合成する。実深度や人物検出は使わない。プレビューはPIL、出力はFFmpegなので画素一致ではない。
- 新しい5フィールドは末尾へ追加。従来の位置引数、JSON保存・再読込を確認。形状指定がないJSONはcircleが既定値となる。bandを指定した旧上下DOFのフィルターは維持。
- iceblue/goldenの2カラーと4つのワンクリックプリセット、全FXの日本語ヘルプ、画面上部とタイトルとVERSION.txtの5.10.3表示。
- 受領版で廃止されたcenter_mosaicはこの環境へ一度も導入せず、古いJSONにあるキーだけを除去。Template生成時は辞書をコピーして呼び出し元JSONを変更しない。保存時にも除去。他FXとブロックモーションは保持。

## 保持したCodex修正

受領effects.pyに欠落していたeffect_events引数・イベント時刻転送、肖像解決失敗の警告、PNG後片付けのOSError保護を保持。apply_effectsは前回の関数を基に、円形設定の診断メタデータだけ追加した。NVENC選択、CPU再試行、音声入力/出力map、キルペア、タイトル/BGM、fpsの経路は変更しない。

core/jobs.py、gpu_pipeline.py、recorder.py、camera.py、camera_clock.py、capture.py、audio.py、procloop.py、audio_worker.pyとNative Helper/START.batはv5.10.1とバイト一致。WGC初回プレロール、カメラ反映後の新フレーム待ち、失敗/停止時の中断、実時間キル補間、TargetLockとLoLプロセス専用録音を保持。

## 並行開発

UIはfeature/ui-circle-v5103、GPUはfeature/gpu-engine、統合はintegration/v5.10.3。旧ブランチは全て保持。core/focus_fx.pyとcore/preview.pyをGPU所有として明示し、混在テストをUIのtest_v5102_circle_focus_preset.pyとGPUのtest_gpu_circle_focus_v5103.py/test_gpu_dof_only_v5103.pyへ分けた。旧位置引数テストには5つの新フィールドを除外した従来フィールド列を使用し、別テストでv5.10.1の全位置引数が変わらないことを検査した。

共有jobsは未変更なのでdocs/CODEX_SHARED_API_REVIEW_v5.10.1.jsonの正確なblob承認を継続使用。ガードは担当違反・Git merge conflict・共有未承認・統合ファイル不一致を検出する。JSONの無条件再承認はしない。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-circle-v5103 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.1.json --integration integration/v5.10.3
```

## 実測

- Linux Python3.12.14/Tk Xvfb、pytest253件成功・失敗/skipなし、25.22秒。初回は252成功と古いmontage位置引数テストの更新漏れ1件を確認し、追加された末尾項目を従来フィールド列から除外して再実行した。アプリの引数順序を変更した修正ではない。
- 実FFmpegで円形DOF強度5/10を1080p PNGへ出力。追加の市松模様テストでは中心と水平/垂直150px位置の模様を保持、円外の水平/垂直500px位置の模様をぼかすことを定量確認。プレビューでも中心保持/外側ぼかしを確認。4プリセット全ての実フィルターでPNG出力成功。
- 実FFmpegの円形DOF付き1080p/60fps動画と合成音声でCPUエンコード成功。試験だけでNVENC選択を強制し、実拒否→libx264再試行も成功。AV末尾差0秒、通常CPU出力とのAAC完全一致、診断に拒否理由がありgpu_effects_confirmedはfalse。実NVIDIA GPUを実行した試験ではない。
- 依存/構文/空白/担当ガード、完全版・差分ZIPの整合性、Git両構成のパッケージと差分適用、GitHubから別フォルダへの新規復元はhandoff/VERIFICATION_v5.10.3.jsonとSOURCE_GIT_REPORT_JA.mdを参照する。録画・診断・設定・画像キャッシュをGitへ含めない。

## 未検証と今後

Windows/実LoLのネクサス開始問題、カメラ追従、Native音声、実GPU/NVENC成功はこのLinuxでは未検証。公式DDragonの実取得は現在のHTTPSプロキシ403で未確認。ローカル画像/モック/cache経路と欠落時の省略は既存テストで確認。

次はWindowsで既存版と比較して録画/カラー/音声/fps/円形DOFと同期を確認する。CodexはGPU能力・フィルター対応・転送回数・エンコード実績を計測し、Bloom/DOFのGPU化を小さな差分で進める。NVENC利用だけで効果もGPU処理と判断しない。元のUI/カメラ/音声を大幅に作り直さない。
