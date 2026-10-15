# v5.9.6 HUD・一括設定の統合結果

受領はフルアプリではなくv5.9.5→v5.9.6の差分ZIP。
README_CODEX_JA.md、パッチ全体、基準SHA256を確認した。
文書内の実機確認・診断送付の案内を新たなユーザー依頼とは区別する。

## 統合と保護

UIはfeature/ui-hud-batch-v596、共有jobsログはレビュー後にfeature/gpu-engine、
統合はintegration/v5.9.6へ保存。過去版を保持し、丸ごと上書きしない。
VERSION/jobsの基準ハッシュは一致。legacy_appは前回の表示修正3行だけが異なると確認し、
適用検査に成功したパッチを使用して、その修正も保持した。

HUDは既存Templateのhide_hud/keep_champion_barsへ接続する3択。
かんたん/詳細編集で共通の状態を使い、設定保存・再起動後の復元を追加。
名前の非表示はLoL内の設定が必要で、未知の名前表示APIを送らない。
一括適用は未保存Shotのカメラ・色・FXをチェックしたシーンにだけ適用し、
確認をキャンセルでき、既存put_manyの1回Undo/Redoを使う。

共有jobsの変更はHUD説明の開始ログとコメントのみ。
ログ差分を除いたASTが前版と一致し、録画/音声/mux/効果/エンコードの経路を維持。
旧core/uiファイル27個のうちjobs以外の26個はバイト単位で同一。
新規UI hud_presetsを追加したが、GPU・録音・TargetLock・時計・校正を上書きしていない。
旧位置引数・キーなしFOV、LoL専用録音も維持。GPU高速化そのものは未実装。

## 実行した確認

- Linux/Xvfb pytest tests -q: **100成功、12.55秒**。
- compileall: 追跡Python59ファイル。pip check、git diff --checkも成功。
- Git所有者・共有API・統合後検査: 終了0、競合・巻き戻しなし。
- 旧v5.9.4共有レビューでは期待どおり終了1、変更されたjobsを検出。
- 3択のTemplate受渡し、HUD状態の再起動復元、一括キャンセル、1回Undoを検証。

実Tkで未保存5点キーとYaw/シーンFXをチェックした2シーンへ一括適用した。
未チェックのコピー元を変更せず、1回Undoで既存値へ戻り、Redoで再適用することを確認。
850msの自動保存・JSON再読込、4区分切替の状態保持も確認。
確認ダイアログへの応答だけは自動試験で模擬した。

適用先を選んで実worker→jobs.preview_clip→Director→モックReplay APIを動かし、
HPバー中心のフラグ（チャンピオンHPだけTrue、他HUDフラグFalse）が1回送られ、
終了時に元の全HUDフラグへ復元されることを確認した。
名前表示の新しいAPIプロパティは使わない。対象固定、UIスレッドでの読取、
終了時停止、診断、プレビュー中の保存済みJSON保持も確認。
これはWindowsのLoL上でHPバーや名前の見た目を確認した意味ではない。

今回はFFmpeg通し出力を再実行していない。効果/音声/エンコード本体は同一で、
以前のv5.9.4の合成1080p/約60fps/カラー/音声検証は旧記録へ残す。
Windows・実LoL・GPU・Native録音は今回未検証。旧総合runnerの既知失敗や
GUI通し試験のCPU時間切れを解消したとは主張しない。

生ログ・個人設定・プロジェクトをGitへ含めない。
証跡は/workspace/.onboarding-results/autocine/v596-*、補助確認は
/workspace/.onboarding-tools/autocine/verify-v596-hud-batch.pyに保管する。

## 次の確認

Windowsでは旧版を別フォルダへ保管し、HUD3択の一致、LoL側の名前非表示設定、
一括適用のUndo/Redo、チェック2シーンのカラー・LoLのみの音声・対象追従を確認する。
Codex側GPU作業は能力と実行プローブ・フォールバック診断から小さく進める。
NVENC成功とGPU効果実行を区別する。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-hud-batch-v596 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.6.json --integration integration/v5.9.6
```

共有レビューは限定されたmode/blobを承認し、後続共有変更は再検査する。
mainへはマージせず、新しい取得用ブランチと全ブランチbundleへ保存する。
