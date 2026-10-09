# v5.10.3 GPUFX — Bloom / 円形DOFのGPU処理

## 問題と変更

ユーザーの診断ではNVENCエンコードは成功している一方、BloomはCPUで処理されていた。FFmpeg同梱版に必要なOpenCLフィルターがなく、約9秒/13秒の素材のエフェクト処理に約81秒/122秒かかっていた。これらは旧版のユーザー診断の集計で、新版の性能測定ではない。元ログ・パス・プレイヤー情報は配布しない。

GPUFX版は既存v5.10.3 HangFixに、OpenCLのRGBA処理によるBloomと円形DOFを追加する。Windowsでは検証済みの追加FFmpegを利用できる。フィルター名の存在に加え、GPUデバイスでRGBAアップロード・プログラムのコンパイル・ダウンロードを実行してから採用する。CPUのOpenCLデバイスは採用しない。

色補正や既存の映像効果の後に円形DOF、Bloomの順で適用する。540pで縦横のGaussianぼかしを計算し、円形焦点マスク・画面合成もGPUで処理する。両方有効なら同じGPUメモリ上で続けて計算し、この区間のアップロード/ダウンロードは各1回。Pythonへ各フレームを読み戻す処理はない。Gaussian計算法は旧FFmpegのgblurと異なるため画素完全一致ではない。

GPU非対応・GPU実行失敗・出力の不意なモノクロ化では既存CPUフィルターへ戻す。イベント時刻、同じキル肖像、タイトル、ゲーム音、BGM入力番号、出力fps、音声マップを維持する。NVENC失敗時のlibx264再試行も維持する。診断にGPU効果選択・実行成否・不使用/再試行理由と実際のFFmpegを記録する。

UI、カメラ、LoL専用録音、録画と時刻の実装は変更していない。Tkの画面操作や軽量PILプレビューはCPU。色補正/LUT、粒子、ビネット、字幕・肖像、音声、上下帯DOFなどは引き続きCPU。既存のOpenCL Focus Blur/VR Blur/Sphere Blur/Glintも対応判定を維持する。アプリ全体をGPUだけで動かす変更ではない。

## Windowsで使う

1. GitHub取得ブランチの **Code → Download ZIP** を使い、旧版とは別のフォルダへ展開する。
2. **LoL_AutoCine/START_GPU.bat** を実行する。初回のみ約184 MiBのFFmpeg ZIPをGitHubからダウンロードし、固定SHA256・必須フィルター・エンコーダーを検査して別ディレクトリへ配置する。その後、元のSTART.batを呼び出すのでNative Audio Helperの構築手順も維持する。
3. GPU優先、Bloomを有効にしてチェック1シーンを作成する。円形DOF単独、併用、全検出シーンの順で旧版と比較する。LoLだけの音声、色、焦点、同期、fps、追従、中止の応答を確認する。
4. COLLECT_DIAGNOSTICS.batで診断を採取する。対象の最終effects JSONの `returncode=0`、`error=null`、`gpu_effects_confirmed=true` と `pipeline.gpu_blur_effects` の `bloom` / `dof` を確認する。`encoder=h264_nvenc` はGPUエンコードの別の証拠。GPU使用率だけで判定しない。

設定後のSTART.batも追加FFmpegを選択する。明示的なIMAGEIO_FFMPEG_EXE指定は優先するため、古いFFmpegをその変数で固定していれば追加版へ切り替わらない。GPU判定が失敗すればCPUに戻り、理由は `pipeline.gpu_effects_unavailable_reason` / `gpu_capabilities.rgba_probe_reason` に残る。GPU表示は利用可能な能力の表示で、各書き出しの実行証拠は診断JSON。

旧imageio同梱FFmpegは残している。元版の別フォルダへ戻れば従来経路で動作する。ダウンロードできない場合も旧START.batで起動可能。GPUドライバー/OpenCLランタイムが必要で、追加FFmpegのNVENCと既存ドライバーの互換性は実機で確認する。追加版が新しいドライバーを必要とする場合、エンコードがCPUへ戻る可能性がある。

## 追加FFmpegの出所

BtbN/FFmpeg-Buildsの固定リリース `autobuild-2026-10-08-13-05`、`ffmpeg-n8.1.3-14-g330caae0c1-win64-gpl-8.1.zip`。URLと固定SHA256はcore/gpu_binary.pyに記録する。実際に193,034,772バイトのZIPを取得し、公式GitHubアセットのSHA256と一致することを確認した。TLS/ハッシュ検証を無効化しない。追加版はGPLビルドで、インストーラーは同梱LICENSEを保存する。FFmpeg本体と検証用OpenCLライブラリはAutoCineのGit/配布ZIPへ同梱しない。取得元にはビルド手順・ソースの案内がある。

## 検証と限界

新GPUテスト9件成功。GPUへの振り分けと順序、GPU転送回数、失敗と色保持のCPU再描画、時刻・音声・タイトル・肖像の維持、一時ファイル削除、CPUデバイス拒否、FFmpegのハッシュ/明示指定/安全な追加配置を検査した。

Linux FFmpeg 7.1.5 + CPU PoCLで実際のOpenCLプログラムを実行し、1080pのBloom/円形DOF/併用PNGを生成した。これはカーネルの動作検証で、GPU実機成功や高速化の証拠ではない。CPU版とのRGB平均絶対誤差は0〜255スケールでBloom 0.6377、DOF 0.4491、併用 0.6889。赤・緑・青の色を保持し、市松模様の中心と水平/垂直150pxの標準偏差85、外側500pxでは0を確認した。本番のGPU指定はこのCPU OpenCLを拒否しGPU対応とは記録しない。

全体回帰テスト・配布検証の結果はhandoff/VERIFICATION_v5.10.3_GPUFX.jsonに記録する。Windows/GTX 1070 Ti/実LoL/Native録音/追加Windows FFmpegの実行と速度はこのクラウドでは未検証。同じ素材・設定で旧版と新版の処理時間と診断を比較する必要がある。次のGPU移行候補はスケーリング/色補正で、CPUとGPU間の余分な転送を避けつつ個別に検証する。

## 並行開発と保存

GPU所有はfeature/gpu-engine、UI所有はfeature/ui-dispatch-hangfix-v5103、統合版はintegration/v5.10.3-gpu-effects。元integration/v5.10.3-hangfixと全旧版を保持し、mainへマージしない。共有APIは既存署名を維持。build_graphの最後に任意のGPU段階引数を追加したが、既存の位置引数は維持する。共有ガードは追加GPUファイルも分類し、共有ファイルの既存blob承認を使う。

```sh
.venv/bin/python tools/check_parallel_integration.py --ui feature/ui-dispatch-hangfix-v5103 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.1.json --integration integration/v5.10.3-gpu-effects
```

配布名はGPUFX、バージョン番号は5.10.3を維持。差分の基準はHangFix版。個人設定・診断・録画は配布しない。Windowsへの取得や起動にクラウド環境のPublishは不要。
