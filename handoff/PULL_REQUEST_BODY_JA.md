約8.9秒の映像加工に約49～55秒かかる受領診断では、NVENC・GPUぼかしが成功していても色/周辺減光/粒子/枠/フェード/合成がCPUに残り、主映像がCPUとOpenCLの間を2回往復していました。

新しいGPUFullStageは色/LUT/カーブ、全22映像演出、時間ブラー、円/帯DOF、Bloom、周辺減光/粒子、BPM/キルアクセント、枠/フォグ、タイトル/実チャンピオンキル画像をGPUへ対応させます。色の定義は既存FFmpegからテンプレート単位で一度LUTへ焼き、GPUで補間。144fps素材は加工前60fpsへ絞り、主映像のOpenCL転送は各1回、PNGはGPUで再利用。時刻/fpsメタデータを補い、旧Zoom tmix scale=4の白飛びを正規化して修正しました。

素材の実プローブ成功時だけNVDEC。NVENCへRGBAを渡し最終色変換をハードウェアへ委ね、libx264再試行では互換yuv420pへ戻します。OpenCL失敗/タイムアウト/意図しないモノクロ化は同じ設定/タイトル/装飾/イベント/音声をCPUへ再試行。モンタージュflash/darkもGPU対応、cutは無加工copy、音声はstream copy。

受領v5106ホットフィックスの安全な録画後ミラー復帰とホバー説明を統合し、v5105のクリック説明/非同期UI/TargetLock/LoL専用Native録音/録画60fpsとカメラ144Hzを維持。UI/Tk、音声、制御/I/O、入口YUV→RGBA、ミラー簡易合成はCPUです。CPUゼロやCUDA/OpenCLゼロコピーを主張しません。

全回帰348件成功（35.67秒、失敗/skipなし）。CPU PoCLによるシェーダー実行で色MAE0.52～1.10/255、時間履歴最大誤差1.5/255、60fps/装飾時刻/全演出のグラフを検証。実FFmpegで144fps→60fps、音声offset/mux、GPUモンタージュと音声copy確認。実Tkのホバー/操作も検査。Windows/NVIDIA実機の性能/画質/LoL動作は未検証。担当ガード、パッケージ、復元と保存検証をhandoffへ記録。旧51ブランチ/旧配布物を保持。

WindowsではCode→Download ZIP→別フォルダ→START_GPU.bat。TEST_GPU_RENDER.batで同じraw素材の6ケースをまとめて比較し、通常アプリで音声/カメラ/複数シーン確認後COLLECT_DIAGNOSTICS。前回v5105を比較先とするDraft PRで、mainへマージしません。
