# v5.9.3 統合結果

## 今回の変更

受領 `LoL_AutoCine_v5.9.3_Codex_MergeChanges.zip` のガイドと全差分を確認した。
UIは `feature/ui-modes-v593`、共有カメラはレビュー後に `feature/gpu-engine`、
統合結果は `integration/v5.9.3` へ保存。前回の統合ブランチと元v5.8.5を保持する。

UIにはかんたん/詳細表示切替、仕上がりプリセット、編集可能なキーフレーム型、
三人称設定リセット、かんたん作成時だけ手動シーン上書きを適用しない経路が追加された。
受領UI、VERSION、新規UIテストはZIPとバイト単位で同一。
ウィンドウタイトルとブランド表示も受領版でv5.9.3へ修正されている。

カメラの小さい時刻補正は速度で吸収し、3点以上のキーはHermite補間する。
共有APIの互換性修正を残した詳細は `CODEX_SHARED_API_REVIEW_v5.9.3_JA.md` を参照。
TargetLock、校正、座標計算、LoL専用録音、GPU効果・エンコード処理を保持。
GPU処理本体の高速化実装は今回も行っていない。

## 今回実行した検証

| 検証 | 結果 |
| --- | --- |
| Linux/Xvfb `.venv/bin/python -m pytest tests -q` | 79成功、10.94秒 |
| compileall app/legacy/prototype/core/ui/tests/tools | 成功、追跡Python54ファイル |
| pip check / git diff --check | 成功 |
| 所有者・共有API・統合後のファイルオブジェクト検査 | 終了0、競合・巻き戻しなし |
| 旧v5.9.2レビュー指定の検査 | 期待どおり終了1、新しい共有3ファイルを検出 |
| カメラの既存メソッドAST比較 | TargetLock・校正・座標計算・既存FOVガードを維持 |
| 保護された実行ファイル12個のv5.9.2との比較 | バイト単位で同一 |

実FFmpeg・モックReplay API・合成映像/音声で、新しいDirectorも動かした。
シーン別ONは逆順2クリップ＋モンタージュ、OFFは従来の隣接キル結合1クリップ。
キーとシーンFXが渡り、プレイヤー固定と元Templateを維持することを確認。
4出力とも1920×1080、約60fps。RGB復号でカラー、音声復号RMS約0.19で
非無音を確認。映像と音声の末尾長差は最大約0.066秒。
3クリップでカメラ診断ログを確認した。

生ログ、合成録画、個人設定はGitへ入れない。
証跡は `/workspace/.onboarding-results/autocine/v593-*`、機能確認ヘルパーは
`/workspace/.onboarding-tools/autocine/verify-v593-render.py`。

## 制限と次の開発

Windows・実LoL・実GPU・Native Process Loopbackの実機動作は未検証。
添付ガイドのWindows実機確認はこのLinux環境では実行できない。
過去の総合runnerの既知失敗とGUI通し試験のCPU時間切れは解消したと主張しない。
今回の79件はpytestであり、旧 `tests/run_tests.py` の再実行ではない。
既知事項は `CODEX_AUDIT_RESULTS_JA.md` と旧統合記録を参照。

Windowsでは旧版を別フォルダに保持し、1クリップ・2シーンの順序、対象追従、
カラー、LoLのみの音声、NVENCとGPU効果の診断を確認する。
その後Codex側では `CODEX_GPU_ANALYSIS_JA.md` に沿って実行プローブ・
CPUフォールバック・正確な診断から小さく改善する。UI作業は別ブランチを継続する。

Gitガードは最新UIブランチと共有レビューを明示して実行する:

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-modes-v593 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.3.json --integration integration/v5.9.3
```

共有レビューは指定されたGitオブジェクトだけを承認し、後続変更は再検査する。
取得用GitHubブランチと全ブランチbundleの説明は `handoff/` に保存する。
mainへのマージは行わない。
