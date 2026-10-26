# Issue #53: 従来アプリ基準とUI差替え接続契約

## 基準の確認

- 調査基準は従来Tkアプリ `v5.10.32-test`、`codex/camera-effects-integration-20261019` の `feb895491ca4bc780da4aab91990f25177cd35ab`。`VERSION.txt`、ユーザーが提示したv5.10.32画面、PR #49の実装・Windows試験記録が一致する。実際に現在起動中のユーザー配布フォルダまでは特定できていないため、そのバイナリとの完全一致は未確定。
- PR #48 `de453046` はこの基準の祖先。PR #44 `cf8d6e0` は祖先ではなく別系統であり、カメラ差分を機械的に取り込まない。PR #50は#49を基準にしたUI比較研究、PR #51/#52も比較用で参照専用。`main`は基準にしていない。
- Work研究は `f3b6056b57ee468d04fd8124a05d331f225aa310` の `implementation_quality_audio_20261026/` を確認。Flash V4の6/42失敗、V5の限定probe、tmixの人工12件、座標1458数理条件、素材687件の審査キュー、人工音源7件を製品合格と区別する。
- このブランチは上記#49からの独立worktree。従来配布物・ユーザー設定・研究/比較ブランチは変更しない。

## 従来機能の台帳（コード到達性と実機品質は別判定）

| 領域 | 既存経路 | 状態と検証境界 |
|---|---|---|
| `.rofl`/Replay API/10人 | `legacy_app.App.on_open_replay`, `core/replay_api.py`, `core/players.py` | 実装済。現ユーザー環境の接続はNOT_RUN。 |
| 試合全体スキャン/kill・assist | `App.on_scan`→`_scan`, `core/scanner.scan_kills` | 実装済。engage専用検出は未実装。再スキャン後チェック状態は別途回帰確認が必要。 |
| 選択/チェック/全件とタイムライン | `App.on_scene_selection`, `on_toggle_checked`, `on_make_selected`, `on_make_checked`, `on_make_clips`, `ui/scene_project.py` | 実装済。実Replayと複数kill品質はNOT_RUN。 |
| ミラー/演出プレビュー | `App.on_mirror_start/stop`, `on_preview_play/stop`, `ui/mirror_capture.py`, `core/preview.py` | 実装済。実測FPS/録画との同期はNOT_RUN。 |
| 手動/固定自動/フルオート、BLUE/RED、TargetLock | `App.current_template`, `ui/director_work_controls.py`, `core/camera.py`, `core/smart_camera_director.py` | 実装済。全視点の実画角はREVIEW。PR #44を無条件に上書きしない。 |
| FX/色/曲線/DOF/テンプレート | `core/effects.py`, `core/preview.py`, `App.current_template` | 実装済。今回Flash/Zoom候補だけ別revisionで比較。プレビューと出力の全効果一致は未検証。 |
| 既存37/89、Work652/35FX/6登場 | `core/kill_icons.py`, `core/work_kill_assets.py`, `ui/director_work_controls.py` | 接続済。正式枠No.083 Aのみ、他651と35FXは確認用。6motionのpop横揺れを保持。 |
| 録画/1080p60/NVENC/GPU | `core/capture_process.py`, `core/recorder.py`, `core/effects._apply_effects`, `core/performance_diagnostics.py` | 実装済。NVENCとGPU FXを別判定し、実LoL/WGC/長時間はNOT_RUN。 |
| LoL音声/書き出し/診断 | `core/audio.py`, `core/jobs.py`, `tools/native_audio/`, `tools/collect_diagnostics.py` | 実装済。実LoL専用音・AV drift・helper配布はNOT_RUN。 |

## UI接続境界

`core/ui_bridge.py` の `LegacyUIBridge` は既存`App`を保持し、UIイベントを**同じAppの実ハンドラ**へ渡す。`switch_view()`は画面識別子だけを更新し、Replay API、ミラー、録画ジョブを停止・再作成しない。Tkイベントは作成元UIスレッドだけで実行し、バックグラウンドからは`root.after`へ配送する。

| UIイベント | 従来の呼び先 |
|---|---|
| `replay.open` / `scan.start` | `on_open_replay` / `on_scan` |
| `scene.open` / `camera.open` / `fx.open` / `output.open` | `_focus_editor_zone(scene/camera/fx/output)` |
| `preview.play` / `preview.stop` | `on_preview_play` / `on_preview_stop` |
| `mirror.start` / `mirror.stop` | `on_mirror_start` / `on_mirror_stop` |
| `assets.open` / `frames.open` | `_open_work_gallery` / `_open_kill_frame_gallery` |
| `export.selected` / `export.checked` / `export.all` | `on_make_selected` / `on_make_checked` / `on_make_clips` |
| `jobs.cancel` / `settings.open` / `diagnostics.open` | `on_stop` / `_focus_settings` / `on_show_diagnostics` |

共有状態`SharedUIState`はreplaySessionId、targetPlayerId、selectedSceneId、checkedSceneIds、camera side/mode/style/parameters、output settings、mirrorSessionId、activeJobId、viewKey相当をUIから独立して保持する。イベント例外は呼出元に返し、見た目側は失敗表示・再試行・取り消しを提供する。**このadapterは接続準備で、候補1〜10の実UIをこの時点で実接続したという意味ではない。**

## 候補別の未接続部分と選定後の最小作業

- 候補1〜7（PR #51）は既存バックエンドを共有する比較経路があるが、各ボタン/設定の完全到達性、実LoL映像・出力との同値性は未合格。採用候補の`ui/comparison_detail.py`等のイベントを上表へ逐一照合する。
- 候補8〜10（PR #52）は独立したUI体験モック。Replay/scan/mirror/record/export/GPU/audioは未接続。画像忠実な見た目側とこのadapterをつなぐ作業が必要。
- 選定後は(1)候補画面のコピーを新ブランチへ、(2)ボタン・入力ID→イベント契約の一覧化、(3)状態移管、(4)プレビュー/ジョブの寿命検査、(5)各機能到達性、(6)Windows Replay/録画/音声試験、(7)旧UIへ戻せる切替の順。UIの再構築で`App`を破棄しない。
- 想定競合は`legacy_app._build/current_template/_save_settings`、候補側HTML/JSイベント名、`core/preview.py`の画像転送。`core/camera.py`・`core/audio.py`・`core/recorder.py`への接続変更は最小にし、問題時は新UI起動経路だけを外して従来`START.bat`へ戻す。
