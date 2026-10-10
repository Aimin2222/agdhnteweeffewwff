# v5.10.6 GPU Full 統合

## 原因と変更

直近の受領診断では約8.9秒の加工に48.7〜55.1秒。NVENCとGPU Sphere/DOF/Bloomは成功していた一方、色/温度/彩度、2段の周辺減光、粒子、枠、フェード、合成/形式変換がCPUに残っていました。主映像は部分GPUとCPUの間を2回往復していました。

`core/gpu_full.py` を既存レンダラの前に追加し、色/LUT/曲線・22映像エフェクト・時間ブラー・円形/帯DOF・Bloom・周辺減光/粒子・BPM/キルアクセント・枠/フォグ・タイトル/キル画像をGPUに対応させます。テンプレート単位で33³の色LUTをCPUで一度準備してGPUへ送り、動画の各画素はGPUで補間します。外部LUTを変更した場合は再生成します。時間履歴はGPUフレームの参照を保持し、主映像はOpenCLに一度upload、一度download。PNGは一度uploadして再利用します。

映像加工前に出力fpsを選択。OpenCLフィルターが失うfps/時刻メタデータを補い、PNG側も同じtime baseに合わせて時間ブラーやイベント時刻を維持します。Zoomの旧 `tmix scale=4` は正規化された1:2:1へ直し、白飛びを避けます。GPUのGaussian、拡大縮小（bicubic）、乱数粒子はCPU版とビット単位で同一ではありません。見た目の比較はWindowsテストへ含めます。

NVDECは入力素材の実デコードプローブに成功した場合だけ使います。OpenCLからRGBAをNVENCへ渡し、最後のRGB→YUV変換をNVENCドライバへ任せます。NVENC失敗時はlibx264/yuv420p、GPU加工失敗/タイムアウト/意図しない白黒化なら同じCPUグラフへ自動再描画。エフェクト設定、タイトル、装飾、音声入力/イベント/trimは保持します。OpenCL/CUDA間のゼロコピーは導入していません。入口のソフトウェアYUV→RGBA変換は残ります。

音声のNative Process Loopback、後段mux、録画60fps/カメラ144Hz、カメラTargetLockとUIの非同期ワーカーは維持します。ミラー簡易合成/ヒストグラム/Tk描画はCPUです。これは映像書き出しのGPU経路をまとめて追加する版で、CPUだけの制御処理までGPUへ置き換えるものではありません。

カットのモンタージュは再エンコードなしのcopyを維持。flash/darkの結合アクセントもGPUへ対応させ、失敗時は同じCPUアクセント→通常連結の順で復旧。整数CFR以外の素材は時刻を保つ従来CPU経路を選びます。

## 受領ホットフィックス

受領 `v5106_camera_hover_against_v5104.patch` は正式なv5.10.6全UI版ではなくv5.10.4基準の部分差分です。jobsの録画/音声失敗後にミラーを安全な俯瞰へ戻す変更を採用し、UIのホバーはv5.10.5のクリック説明と非同期処理を保つよう手で統合しました。録画中の三人称や完成MP4は変更しません。

## ブランチと検証

GPU/共有 `feature/gpu-full-v5106`、UI `feature/ui-hover-v5106`、統合 `integration/v5.10.6`。既存ブランチを保持し、共有jobsは正確なGit blobのレビューを更新します。metadataの担当設定は統合のみで追加。

```
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-full-v5106 --ui feature/ui-hover-v5106 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.6.json --integration integration/v5.10.6
```

Linuxで全回帰、実Tkホバー/応答性、CPU OpenCLシェーダーで色・時間履歴・フレーム数・合成時刻を検証します。productionのGPU選択はCPU OpenCLを拒否。診断にFFmpeg単体CPUとPC全体CPU、実際の選択/成功/切替を区別して記録します。数値・取得物・復元確認はhandoff/VERIFICATION_v5.10.6.jsonへ保存します。Windows/LoL/NVIDIAの画質/音声/速度はユーザーによる一括実機テスト待ちです。
