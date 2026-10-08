# GPUパイプライン

AutoCine v5.7は「GPU優先・CPUフォールバック」のハイブリッド方式です。

1. 通常デコード
2. `scale_cuda` が利用可能ならGPUスケール
3. 既存の映像エフェクトをCPU側FFmpegフィルターで処理
4. `h264_nvenc` が利用可能ならGPUエンコード
5. 利用できない機能だけCPUへフォールバック

CUDA/CUVIDデコードは環境依存で `CUDA_ERROR_INVALID_VALUE` が発生する可能性があるため、強制しません。
