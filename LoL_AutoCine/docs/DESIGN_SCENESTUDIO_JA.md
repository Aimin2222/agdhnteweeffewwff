# Scene Studio 設計書 v5.9.0

## アーキテクチャ

```
legacy_app.py (Tk/UI/Main thread)
  ├── ui/scene_timeline.py (pre/postのドラッグ入力)
  ├── ui/motion_graph.py (CameraPlan純計算をCanvasに可視化)
  ├── ui/scene_project.py (Shot, SceneProject, Undo, validation, JSON)
  └── ui/scene_batch.py (one-shot/sceneのレンダリング接続)
          ├── core.jobs.run_auto_edit (変更なし)
          ├── core.effects.concat_clips (変更なし)
          ├── core.camera.CameraPlan (変更なし)
          └── AudioCapture / GPU / Recorder (変更なし)
```

## 公開インターフェース

- `Shot`: motion profile, arc, dolly, yaw, pre/post seconds, intensity を扱う。`Shot.validated` が入力値を制限する。
- `scene_key(kill)`: event_id/time/killer/victimをもとにID作成（複数試合をまたぐ完全なグローバルIDではない）。
- `SceneProject`: `put/put_many/remove/undo/redo/save/load`。JSON version=1。
- `recommend(kill, pre, post)`: role/multikillをもとに純粋関数で決定論的にショットを生成する。
- `build_scene_templates(kills, base_template, overrides, auto)`: 書き出し時のコピー。UI変数/Tkにアクセスしない。
- `render_scenes(...)`: 既存 `core.jobs.run_auto_edit` を1シーンずつ実行し、必要な場合はconcat。録音/FFmpegはそのまま再利用。

## データフロー

```
UI (チェック済みシーン/ワンクリック)
 → Tk UIスレッドでテンプレート+シーン設定のスナップショットを取得
 → 既存Workerスレッド
    ├─ シーン別モードOFF: 従来のrun_auto_edit
    └─ シーン別モードON: render_scenes
             ├─ shot override またはキル内容から推薦
             ├─ Templateをdeepcopy（元を破壊しない）
             ├─ 3rd person→既存lolnam_cinemaを使用
             ├─ run_auto_edit(単一kill, montage=False)
             └─ concat_clips(複数の完成mp4)
```

## 色・GPU・音声との統合

本ZIPでは `core/` のコードを変更していない。Codex GPUブランチとの統合時、`core`を古い版へ戻さず、GPUブランチに対して `legacy_app.py` と `ui/` の追加コードだけをマージする。`run_auto_edit` と `Template` の互換性を保つ。

## カメラ・グラフ

`CameraPlan.third_pose_at` / `fov_at` を元にNormalized FOV/距離/Orbitの曲線を表示する。実際の出力は従来の CameraDirector が動かす。UI表示のグラフはリプレイ実機位置の絶対値ではなく合成ターゲットを基準にした**動きの概形**。カメラ基準座標は変更していない。

## エラー・トランザクション

Project書き込みはtmpファイル→`os.replace`で原子的。個別シーンの失敗は`BatchResult.failed`に残す。完了クリップは保存し、モンタージュに使う。クラッシュ時のログは既存診断機能に記録する。
