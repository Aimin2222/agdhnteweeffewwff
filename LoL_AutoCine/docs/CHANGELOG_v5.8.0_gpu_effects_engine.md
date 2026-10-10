# LoL AutoCine v5.8.0 - GPU Effects Engine Foundation

## 目的
v5.7.8で安定化したNVENC出力を維持しつつ、エフェクト処理をGPU優先へ移行するための基盤を追加。

## 変更
- `core/gpu_pipeline.py` を追加。
- FFmpegのGPUフィルター能力を起動時に検出。
- NVIDIA NVENCを引き続き優先。
- `gblur_opencl` が利用可能な環境では Focus Blur / VR Blur / 球体ブラーをGPU側で処理。
- `unsharp_opencl` が利用可能な環境では Glint のシャープ処理をGPU側で処理。
- GPUステージからCPU側へ戻す場合も、フレーム転送は1回に限定する設計。
- GPU非対応エフェクトは従来のCPUフィルターへ自動フォールバック。
- 既存の音声録音・Native Process Loopback・NVENCエンコード経路は維持。

## 今後
GPUネイティブ実装を段階的に増やし、Blur / Color / Transform / Composite / Dynamic EffectsをGPUパイプラインへ移行する。

## 注意
この環境ではWindows NVIDIA GPU上での実機レンダーは実行していない。v5.8.0はGPU能力に応じて安全にGPU経路へ入れるための基盤版。
