# v5.9.8 安全統合・検証記録

## 採用と保持

受領ZIPはv5.9.7向け差分。継続中の安全統合として扱い、資料の診断ZIP/動画送付推奨を外部送信依頼とは扱わない。

- UI: スマート演出4種、イベント情報による5点キー生成、キル強調スライダー、全シーン推薦、旧JSON互換、Undo/Redo、SCENE_PLANへの強度とキー数を追加。
- GPU担当: 新しいcore/highlight_pulse.pyとbuild_graphへの限定接続をレビュー。キルの相対時刻にCPU標準eqで短い明るさ・彩度アクセントを付ける。強度0・イベントなし・静止画では追加しない。自動計画フラグだけで映像グラフを変えない。
- core/effects.pyの受領フルファイルは使わない。scene_keyframes/montage_fxの位置を保ち、新フィールド3個は末尾に追加。既存v5.8.5/v5.9.6/v5.9.7の位置引数を検証。新設定・パルス接続を除いたASTはv5.9.7と同一。
- jobs/音声/カメラ/時計/GPU経路/モンタージュを含む既存core22ファイルはバイト一致。Native録音ヘルパー、起動バッチ、v5.9.5出力同期修正、HUD3種と一括適用、v5.9.7モンタージュ失敗復旧を保持。
- 受領版ではスマート実行後に詳細編集の通常自動作成も新自動計画を引き継いだ。再現テストの失敗を確認し、ジョブ開始時のTemplateスナップショットだけでsmart引数を反映する修正を採用。通常ボタンは従来推薦へ戻り、保存済み個別演出は保持。タイトル/見出しの旧版表示も更新。

## Gitと衝突検出

UI: feature/ui-highlight-v598、GPU: feature/gpu-engine、統合: integration/v5.9.8。旧版ブランチを保持。共有ファイルは今回変更しないためv5.9.7の正確なblob承認をそのまま再利用する。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-highlight-v598 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.7.json --integration integration/v5.9.8
```

終了0: 担当違反・共有未承認・merge衝突・GPU/UI巻き戻しなし。新pulseモジュールをGPU所有、新受領テストをUI所有とし、実Git履歴による検出を確認。

## 実施した確認

- pytest tests -q: **133件成功、失敗/skipなし**（14.56秒、Tk/Xvfb）。受領11テスト＋通常切替回帰1、GPU接続/ABI3、担当ガード3を追加。添付READMEの「76件」は提供側の申告であり、こちらの結果とは区別する。
- Python67ファイルの構文、pip check、git diff --check成功。
- 実Tk→worker→jobs→Director→モックAPIで5キー転送、HUD指定/復元、対象固定、チェック2シーン限定の一括適用、パルス値保存、全シーン推薦のUndo/Redo/Undo、850ms自動保存とJSON往復、独立コピー、メインスレッド読取、プレビュー中の保存済みJSON不変を確認。
- 実apply_effects/FFmpegで1080p/60fps・2イベントのパルスを生成。両キル時刻の平均明るさ差は約+19.67/255、離れた時刻の差は最大2/255。カラー維持、通常版とのAACデータ完全一致、映像/音声の末尾長差0、Template不変を確認。
- 補助試験の初回は強調外の差を「2未満」としたため実測2で失敗。映像再エンコード/フィルターの丸めを含む差として、3/255未満（約1.2%未満）の許容幅で確認し直した。アプリやpytestのassertを弱めたものではなく、差の実測を記録している。通常の強調OFFグラフは変更されない。
- Appの既存境界から録画・jobs・FFmpegまで通し実行。明示スマートと従来モードの双方で2クリップ＋flashモンタージュを1080p/60fpsで生成。スマートはhighlight=0.70/keyframes=5を記録し、逆順の適用、実Directorへのキー転送、対象固定、カラー、合成音声非無音、Template不変を確認。映像/音声の末尾長差は最大約0.052秒。

ローカル証跡: /workspace/.onboarding-results/autocine/v598-*。補助: /workspace/.onboarding-tools/autocine/verify-v598-highlight.py、verify-v598-pulse.py、verify-v598-render.py。生成映像・音声・診断・設定はGitに含めない。

## 実機と次の作業

Windows、実LoL、GTX 1070 Ti、Native Process Loopback録音、実NVENC成功は未検証。合成音声/モック成功と混同しない。参考動画の完全再現・敵の実位置/スキル軌跡推定は未実装。生成キーの始終端は相対差分がゼロで、既存カメラ計画・座標系を置換しない。

旧tests/run_tests.py初回16件中11成功/5失敗（WAVなし旧4条件、低解像度静止画と1080p固定Bloomの不一致）、旧CPU GUI通し試験240秒未完了は今回再実行せず、133件pytest成功とは区別する。

Windowsでは旧版を別フォルダに保管してSTART.batで起動。通常→スマート4種→通常の切替、既存個別設定の優先、全シーン推薦Undo/Redo・保存復元、チェック2シーンの色・LoLのみ音声・対象追従・HUD・fps・モンタージュを確認する。

新アクセントはCPU処理でありGPU高速化ではない。今後のGPU担当作業は能力列挙と実行プローブの区別、正しい診断理由、安全なフォールバック、Bloom/DOFの小さな段階導入と実機での色・音声・同期・性能比較。旧hwdownload,format=yuv420p経路を安易に復活させない。

完全ソースと全ブランチbundleを取得用新ブランチ・Draft PRへ保存し、mainへマージしない。Windowsへの取得に環境Publishは不要。将来クラウドへの設定反映だけ環境設定で確認・保存・Publishする。
