# LoL AutoCine v5.8.5 変更点 / テスト手順

## 元になったバージョン
v5.8.4（チェック済みシーン作成・クラッシュ追跡が実機確認済み）。カメラ、シーン検出、LoL音声処理を維持。

## 実装した修正
- Bloom（発光）を1080p sigma=22から540p sigma=11 + フルHD再合成に変更。近いぼけ半径で計算量を削減。細部はわずかに異なる可能性あり。
- DOFの焦点マスクを480x270で計算して拡大（色保持）。焦点の境界は近似。
- OpenCL実装にない `gblur_opencl` を `avgblur_opencl` に変更。実際に同じアップロード/ダウンロードで1フレームの適合性テストに成功した場合だけ有効化。GPU経路では平均ぼかし近似のためCPUと見え方が変わる可能性あり。
- CUDA/FFmpegの既知の `hwdownload,format=yuv420p` 不具合を避け、OpenCLの実機検証したNV12経路を使用。失敗時は元のCPUエフェクトで自動再試行。
- 診断JSONにGPU能力、実行GPU/CPUエフェクト、Bloom/DOF最適化、フィルタグラフ、処理FPSを記録。
- COLLECT_DIAGNOSTICS.bat はPython収集スクリプトへ変更し、`No logs found` の取りこぼしを改善。

## 注意点
- FFmpegがOpenCLフィルタを含むだけではGPUエフェクトは有効になりません。OpenCLデバイスを実際に初期化できる必要があります。
- GPU利用率はLoL自体の描画負荷も含むため、GPUエフェクト実行の証拠にはなりません。診断JSONのpipeline.gpu_effects_selectedを確認してください。
- NVENCがあってもGPUエフェクトが有効とは限りません。
- GPUエフェクトの成否や速度向上はWindows/GTX 1070 Ti上では未検証。旧バージョンv5.8.4を手元に残して比較してください。

## 手順
1. ZIPを**新しいフォルダ**に展開し START.bat で起動（旧フォルダへ上書きしない）。
2. エフェクトOFFでチェックした1シーン作成 → カラーとゲーム音確認。
3. Bloom有効のテンプレートでチェックした1シーンを作成 → 書き出し時間を比較。
4. Focus BlurとDOFをそれぞれ別にONにして1シーンずつ作成。色、ぼけ具合、音声を確認。
5. 2シーン一括生成。COLLECT_DIAGNOSTICS.batを実行してAutoCine_Diagnostics.zipを送付。

## ログの読み方
- diagnostics/performance/render_*.json の pipeline.gpu_backend / gpu_effects_selected / cpu_video_effects / bloom_cpu_optimized / dof_mask_cpu_optimized / effective_processing_fps
- fallback_reason がGPU失敗を意味します。
