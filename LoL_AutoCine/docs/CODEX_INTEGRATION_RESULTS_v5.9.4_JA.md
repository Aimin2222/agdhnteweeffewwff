# v5.9.4 統合結果

## 統合内容

受領ZIPの `MERGE_NOTICE_JA.md`、README、変更履歴、診断所見と全差分を確認した。
添付資料の推奨実機テストはユーザーからの新たな外部操作依頼とは区別する。
既存の並行開発・GitHub保存依頼に沿い、UIは `feature/ui-preview-v594`、
共有カメラはレビュー後に `feature/gpu-engine`、統合版は `integration/v5.9.4` へ保存。
前回の統合、元v5.8.5、過去UIの履歴を保持する。

未保存キーを含む現在のShotをUIスレッドでスナップショット化し、既存workerの
実カメラプレビューへ接続した。時計の経過時間上限を250msへ変更し、
105〜180msのAPI待ちを切り捨てない。プレビュー終了時の診断ログを追加。
共有APIの詳細は `CODEX_SHARED_API_REVIEW_v5.9.4_JA.md` を参照。

パッチの適用検査は成功。camera.py全体の上書きは旧位置引数とFOVの互換性修正を
失うため、差分のみ適用した。UI、VERSION、新規受領テストはZIPと同一。
GPU効果、エンコード、LoL専用録音、TargetLock座標・校正の処理本体を維持。
GPU高速化そのものは未実装。
受領UIの画面タイトル・ブランド表示はv5.9.3のまま、VERSION.txtは5.9.4。

## 今回実行した検証

| 検証 | 結果 |
| --- | --- |
| Linux/Xvfb pytest tests -q | 86成功、12.35秒 |
| compileall / pip check / git diff --check | 成功、追跡Python56ファイル |
| Git所有者・共有API・統合後のファイル検査 | 終了0、競合・巻き戻しなし |
| 旧v5.9.3共有レビューによる検査 | 期待どおり終了1、新しい共有3ファイルを検出 |
| cameraのAST比較 | Director.run以外の既存クラス・関数・互換性を維持 |
| 保護されたGPU/音声等の実行ファイル12個 | v5.9.3とバイト単位で同一 |

模擬105ms待ちをDirectorの実ループへ与え、時計が待ち時間を反映することを確認。
250msを超える停止の上限と、一時停止中に時計を進めない挙動も確認した。

実Tkのコールバック→worker→jobs→Director→モックReplay APIまでのプレビューで、
未保存の5点キー、UIスレッドでの値取得、workerでの実行、保存済みJSONと
プロジェクトの非変更、対象固定、終了時の停止、診断ログを確認した。
実LoLミラー上の見た目を確認したという意味ではない。

実FFmpeg・モックAPI・合成映像/音声では、逆順2クリップ＋モンタージュと
従来OFFの隣接キル結合1クリップを確認。全4出力で1920×1080・約60fps・
RGB復号のカラー・音声復号RMS約0.19の非無音を確認。
映像音声の末尾長差は最大約0.071秒。キー/個別FX、対象固定、元Templateを維持。
生ログ・録画はGitへ含めず `/workspace/.onboarding-results/autocine/v594-*` に保管。
機能確認ヘルパーは `/workspace/.onboarding-tools/autocine/verify-v594-preview.py` と
`verify-v594-render.py`。取得用Gitには含めない。

## 診断資料の扱いと次のGPU開発

受領 `DIAGNOSTIC_FINDINGS_v5.9.4_JA.md` には、前版のWindows書き出し4回で
NVENC成功、同梱FFmpegのOpenCL未対応によるCPU Effects、約9秒動画の効果処理に
約68〜69秒かかったと記載されている。元の生診断ログは今回受領しておらず、
この所見は独立検証していない。NVENC成功とGPU効果実行を混同しない。

次のCodex側GPU作業は、FFmpeg能力と実行プローブの確認、正確な理由の記録、
安全なCPUフォールバックから小さく進める。OpenCLがないFFmpegでは
NVENCを使っても効果フィルターはCPUで動き得る。時計修正はHTTP呼出しそのものを速くしない。

Windows・実LoL・実GPU・Native録音は今回未検証。
旧総合runnerの既知5失敗、GUI通し試験のCPU時間切れを解消したと主張しない。
86件はpytestであり、旧tests/run_tests.pyの再実行ではない。
Windowsでは旧版を保管して、未保存キーのプレビュー→保存して1クリップ→2シーンの
順序・カラー・LoLのみの音声・対象追従・GPU/NVENC診断を確認する。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-preview-v594 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.4.json --integration integration/v5.9.4
```

共有レビューは限定されたmode/blobだけを承認し、後続の共有変更は再検査する。
mainにはマージせず、新しい取得用ブランチと全ブランチbundleへ保存する。
