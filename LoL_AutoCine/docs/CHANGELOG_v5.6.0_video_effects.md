# LoL AutoCine v5.6.0 - 映像演出追加

## 追加

Premiere / After Effects系の名称・操作感を意識した映像演出を追加。

### 映像切り替え
- Motion Camera
- Radial Blur（FFmpeg標準のフレームミックスによる軽量表現）
- Zoom Blur
- Glitch
- Kaleidoscope（ミラー合成による軽量表現）
- VHS Damage
- Block Motion
- Spin Motion

### キル瞬間
- Chroma Leak
- Flash

### 映像全体
- Focus Blur
- Vignette
- Glint
- Camera Shake
- Wiggle

### 照明系
- VR Blur
- VR Light Leak（Film Burn系）
- 球体ブラー

### ワイプ系
- Panel Wipe
- Stretch Wipe

### Transformers
- Mirror
- Slice

## 操作方針

- エフェクトはチェックボックスでON/OFF。
- 各エフェクトに個別の強度入力欄を用意。
- プリセット「キル瞬間」「カメラ演出」「VHS / Glitch」「シネマ」「全部控えめ」を用意。
- ミラー中のプレビューにも軽量近似を反映。
- 最終書き出しはFFmpeg標準フィルタを使用し、NVENC等のGPUエンコードを優先。GPU非対応フィルタはCPU側で処理して最後のエンコードをGPUへ渡す。

## 注意

各名称はPremiere/AEの同名エフェクトと完全同一のアルゴリズムを意味しない。AutoCineでは、LoLリプレイ編集で必要な見た目と操作性を優先し、標準FFmpegで安定して再現できる方式を採用する。
