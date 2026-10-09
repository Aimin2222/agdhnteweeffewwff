# v5.8.2 自動パフォーマンス診断

通常どおりクリップを書き出すと、`diagnostics/performance/render_*.json`（処理経路と平均・最大）、同名CSV（1秒間隔の推移）、`diagnostics/ffmpeg/render_*.log`（実行コマンドとFFmpegのエラー）、`diagnostics/latest_diagnostics.zip`（最新のレンダーパスの診断一式）を自動生成します。

**注意**: NVIDIAのGPU統計は`nvidia-smi`がPATHにある場合のみ取得します。GPU全体の利用率はLoLなど他アプリも含みます。`gpu_effects_confirmed`はGPUフィルターパスがエラーなく終了した意味であり、GPU負荷が当該アプリだけに由来することの証明ではありません。CSVのCPU値はシステム全体です。GPUフォールバック時は別の診断ファイルが作成されます。最新ZIPは最後に走ったFFmpeg映像レンダーのみを含み、全クリップの診断はperformance/に残ります。LoL音声録音・muxは従来のままです。

Windowsで `nvidia-smi` が見つからない場合、GPUメトリクス欄は空欄になります。psutilがインストールされていない場合もレンダーは続行します。書き出し終了後、`diagnostics` フォルダをZIPにして送ると全レンダー分を解析できます。
