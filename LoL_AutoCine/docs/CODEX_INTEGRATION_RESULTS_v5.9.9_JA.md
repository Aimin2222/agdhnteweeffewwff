# v5.9.9 安全統合・検証記録

## 採用と保持

受領LoL_AutoCine_v5.9.9_Codex_MergeChanges.zipを継続中の並行開発へ統合。添付資料の実機所見・外部送付推奨・完了予定は、こちらで検証した結果や新しいユーザー依頼とは区別する。全面作り直しは行わない。

- UI: キル装飾4種、位置・大きさ・長さ・濃さ、シーン別inherit/off/上書き、保存・Undo/Redo、任意のスマート構図、自動モンタージュ選別を採用。手動順序を保持。装飾と構図の既定はOFF。
- GPU担当: core/effects.py、camera.py、jobs.pyを既存修正との差分としてレビュー。Template/CameraPlan/ClipTakeの新フィールドとapply_effectsの任意引数は末尾へ追加し旧位置引数を維持。録音ヘルパー、TargetLock座標系、HUD復元、録画速度正規化・音声offset、既存GPU再試行を保持。
- 通常計画へ新機能が入り込む経路を制限。新API送信間隔調整・観測頻度・速度送信制限・構図補正はsmart_composition時のみ。追加スマートスローの0.40下限はsmart_impact有効時のみで、従来の0.35スローを保持。smart_impactと暗転自動採用・12件超の自動選別は明示スマート計画時のみ。
- スロー再生中はReplay時刻と出力動画時刻が一致しない。装飾/構図ONの録画だけ、既存playback観測とrec.started_perfからキル通過時の実時間を補間してClipTake.effect_eventsへ渡す。追加API要求なし。従来呼出しは既定Noneで元のイベント変換を維持。
- 受領PNG overlayのshortest=1が25fps装飾に合わせて60fps映像を短くし、AAC末尾も変える問題を実出力で発見。shortest=0:eof_action=repeatにして装飾素材で動画を打ち切らないよう修正。タイトル/BGM/ゲーム音の入力番号、GPU失敗時CPU再試行も確認。
- 版表示をv5.9.9へ更新。パッケージ作成ツールは単体ソースGitとGitHub取得用構成の双方に対応させ、Git追跡ファイルだけを採用。個人設定・プロジェクト・未追跡素材を含めず、差分パッチの構成別適用方法を明記。

## Gitと衝突検出

UI: feature/ui-killbadges-v599、GPU: feature/gpu-engine、統合: integration/v5.9.9。旧版ブランチを保持して全25ブランチ。共有レビューはdocs/CODEX_SHARED_API_REVIEW_v5.9.9.jsonの正確なcamera/jobs blobを承認し、camera_clockの既存承認を維持する。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-killbadges-v599 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.9.json --integration integration/v5.9.9
```

終了0。旧v5.9.7レビューでは新camera/jobsを拒否する終了1を確認。kill_iconsはGPU、新UIテストはUI、パッケージ作成ツールはインフラとして実Git履歴で担当違反を検出する。共有変更を無条件に承認しない。

## 実施した確認

- pytest tests -q: **162件成功、失敗/skipなし**（36.03秒、Tk/Xvfb）。旧位置引数・通常モード・構図/キル装飾・イベント実時間補間・PNGによる動画打切り禁止・旧機能と実Gitガードを確認。
- 追跡Python72ファイルの構文、pip check、git diff --check成功。
- 実Tk→worker→jobs→Director→モックAPIで5キー、対象固定、health HUD指定/復元、チェック2シーン限定一括適用、キル装飾のシーン保存、推薦と一括操作のUndo/Redo、自動保存・JSON往復、独立コピー、UI/workerスレッド分離、プレビュー中の保存済みJSON不変を確認。
- 追加7設定（装飾種別・位置・大きさ・秒数・濃さ・構図・モンタージュ）の保存→実Tk終了→新App起動→JSON再保存で値が保持されることを確認。個人設定の代わりに一時フォルダを使用。
- 実apply_effects/FFmpegで4装飾を4位置へ1080p/60fpsで生成。各々キル前・表示中・終了後の画素差、カラー、通常版とのAACデータ完全一致、AV末尾差0を確認。装飾ON時の表示外の差は丸めにより平均1/255。OFF経路は装飾なし。
- タイトル＋装飾＋ゲーム音＋BGMを実出力して入力接続・AV末尾差0を確認。GPUフィルター失敗を模擬し実FFmpegの失敗→CPU再試行で装飾とAACを保持、AV末尾差0。実GPU成功の試験ではない。
- 最終修正後のApp境界→jobs→録画→FFmpegで、明示スマート/従来双方の2クリップ＋flashモンタージュを1080p/60fpsで生成。逆順・5キー転送・対象固定・カラー・非無音合成音声・Template不変を確認。スロー時のキルはnominal pre=2.5/1秒より遅い実時間へ渡されることを4録画で確認。
- 完全版/差分ZIPをGit追跡ファイルから作成し、ZIP整合性、START.bat、個人設定・未追跡ファイル除外、v5.9.8基準へのgit apply --check -p2を確認。完全版と全25ブランチbundleを取得用ブランチへ保存する。

ローカル証跡: /workspace/.onboarding-results/autocine/v599-*。補助: /workspace/.onboarding-tools/autocine/verify-v599-{ui,settings,badges,render}.py。録画・音声・設定・個人診断はGitに含めない。

## 実機と次の作業

Windows、実LoL、GTX 1070 Ti、Native Process Loopback録音、実NVENC成功、実際の遮蔽回避・カクつき改善は未検証。スマート構図は距離/仰角等の安全範囲調整で、地形衝突判定ではない。添付の開発途中という申告を尊重し、Windows完成版として扱わない。

旧tests/run_tests.py初回16件中11成功/5失敗（WAVなし旧4条件、低解像度静止画と1080p固定Bloomの不一致）、旧CPU GUI通し試験240秒未完了は今回再実行せず、162件pytest成功と区別する。

装飾overlay・既存アクセントはCPU処理。Bloom/DOFのGPU高速化は未実装で、NVENCエンコード成功とGPU効果成功を混同しない。今後はGPU能力列挙と実行プローブ、正確なフォールバック理由、小さな段階導入、実機での色・音声・同期・性能比較を進める。旧hwdownload,format=yuv420p経路を安易に復活させない。

Windowsは旧版を別フォルダに保管して取得版のSTART.batで起動。通常OFF→各装飾/スマート→通常への切替、手動順序、個別設定優先、Undo/Redo・保存復元、スロー時の表示時刻、色・LoLのみ音声・HUD・対象追従・fpsを確認する。mainへマージしない。Windows取得に環境Publishは不要で、将来クラウド設定へ反映する場合だけ設定を確認・保存・Publishする。
