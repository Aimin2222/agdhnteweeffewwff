# LoL AutoCine v5.8.1 — GPU Effects 安定化 / 色保持 / DOF高速化

## 今回の修正

- GPU Effects の判定を `scale_cuda` の存在だけで「GPUエフェクト対応」と表示しないよう変更。
- OpenCLエフェクトは実際に1フレームを通すランタイムプローブを実行し、成功した環境だけで使用。
- OpenCL GPUエフェクト経路が実行時に失敗した場合、自動的にCPUエフェクト経路へ再試行。
- Focus Blur / VR Blur / 球体ブラーのCPUフォールバックを 960x540 → blur → 1920x1080 にして負荷を低減。
- DOFのぼかしブランチも半解像度で処理してから1920x1080へ戻し、フル解像度の重いgblurを回避。
- NVENC出力へ BT.709 の色空間/プライマリ/トランスファー/レンジ情報を明示。
- 既存のLoLゲーム音声のNative Process Loopback + 後段AAC muxは維持。
- 旧GUIスモークテストのバックグラウンドスレッドからのTk `StringVar.get()` エラーを修正。

## 重要

GPUエフェクトは「GPUフィルターが存在する」だけではなく、実際のOpenCLランタイムが通ることを確認してから選択します。環境によってはNVENCはGPUで動作しつつ、特定のGPUエフェクトだけCPUへ自動フォールバックします。
