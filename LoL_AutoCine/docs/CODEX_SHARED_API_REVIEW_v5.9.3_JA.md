# v5.9.3 共有カメラAPIの統合レビュー

## 範囲と接続点

受領ZIPの共有変更は `core/camera.py`、新規 `core/camera_clock.py`、
`core/jobs.py` の診断ログである。UI所有のコードは別ブランチ
`feature/ui-modes-v593` へ保存し、共有変更は `feature/gpu-engine` へ
レビュー後に取り込む。全ZIPによる上書きは行わない。

- `CameraDirector` の既存コンストラクター、start/stop、Replay APIの呼出形式を維持。
- `SmoothReplayClock` は純Pythonで、小さい時刻誤差を速度補正し、1.5秒を超える観測誤差をseekとして扱う。
- `CameraPlan` は2点の場合の従来smoothstepを維持。3点以上では単調性を保つHermite補間を使用する。
- jobsは録画終了後にDirectorの診断値を記録するだけで、録画・音声・出力への引数を変更しない。
- 診断のAPI回数・待ち時間は `set_render` の成功呼出しが対象。playback GETや失敗した呼出しの総待ち時間ではない。
- Tk値をコアやワーカースレッドへ持ち込まない。既存Templateの末尾追加フィールドも維持。

## 受領版から保持した互換性修正

受領パッチ全体の `git apply --check` はcamera.pyで失敗した。
v5.9.2統合版が持つ次の2点と、ChatGPT側の基準が異なるためである。

1. `CameraPlan.scene_keyframes` は末尾に保持し、height/sel_nameの旧位置引数を変えない。
2. キーなし、または三人称以外ではFOVを従来どおり返す。キー使用時だけ32〜100度に制限する。

上記を維持して新しいカメラ変更を統合した。`Template.scene_keyframes` の末尾配置、
jobsからCameraPlanへのキー受渡しも巻き戻さない。

## 検証

共有API・新カメラ回帰・Gitガードを合わせて41テスト成功。
実スレッドでDirectorへ30msの模擬render待ちを与え、遅延カウンターと対象固定を確認。
停止中の時計、補正上限、2点補間の旧動作、不等間隔で方向反転するキーの範囲も確認した。

AST比較で既存cameraの変更メソッドがkeyframe_values、Directorの初期化・start・runに限定されることを確認。
TargetLock、リグ校正、座標・回転計算、FOVガード、位置引数を維持。
effects、gpu_pipeline、recorder、audio、audio_worker、procloop、capture、scanner、
render_fx、performance_diagnostics、app、requirementsはv5.9.2とバイト単位で同一。

Linuxモックの成功はWindows/実LoL/Native録音/GPUの実機成功を意味しない。
Replay APIのHTTP待ちが長い場合や実機FPSの低下は残り得る。Windows実機の確認項目は
受領 `README_v5.9.3_JA.md` を参照する。

`CODEX_SHARED_API_REVIEW_v5.9.3.json` はこのレビュー済み共有3ファイルの
Gitオブジェクトだけを承認する。未知の共有変更や他方ブランチの変更を無条件で承認しない。
