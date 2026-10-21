# FXの実体・名称・プレビュー一致の監査

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 既存と新規を分ける

22video effect、16grade、LUT/curves、Bloom、Fog、DOF、highlight pulse、Work35候補、montage transitionが既存の入口。単純に同じ名前の追加機能を新設しない。
原文：[core/effects.py:415](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/effects.py#L415)、[core/gpu_full.py:1](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/gpu_full.py#L1)、[core/preview.py:159](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/preview.py#L159)、[core/montage_fx.py:1](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/montage_fx.py#L1)、[core/render_fx.py:1](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/render_fx.py#L1)。

|名前|CPU出力の実体／相違点|改善の方向|
|---|---|---|
|radial_blur|tmixによる時間方向混合|名称を残し説明を正確にするか、真の放射状kernelを別実験|
|zoom_blur|拡縮crop＋tmix|中心とkill時刻を共有、端欠けと残像を審査|
|glitch / chroma_leak|RGBずらし・noise、適用窓が異なる|常時適用とkill窓をUIで明示|
|focus_blur / vr_blur / sphere_blur|類似の全面gblur系|既存IDは互換維持。UI説明で違い、パラメータ共通化は内部案|
|glint|unsharp＋eq等|選択的発光という説明とは分ける|
|vr_light_leak|kill窓の暖色化|空間的な光漏れtextureは追加案|
|panel_wipe / stretch_wipe|異なる時間のfadein|真の2映像wipeとは別。名前だけで完成としない|
|mirror|hflip|ゲーム内BLUE/RED補正として使わない|
|montage soft|連結後の明暗変化|重なりを使うdissolveは別設計・音声長さ検証|

上表はCPU経路の監査であり、OpenCL版が全て同じ近似だとは断定しない。GPU/CPUの値・時間窓・色空間・合成順を同一入力で比較する必要がある。

## 静的な疑義：flashの複数キル

CPU式ではenableは複数event窓を作る一方、輝度のexp中心に`events[0][0]`を使う。2回目以降の窓が開いてもpulseが極小になる可能性がある。これは原文上の疑義で、今回FFmpegで再現していない。修正前に2キルを十分離した無地クリップでkill±0.1秒の平均輝度を比較し、OpenCL経路と一致を確認する。連続pulseはmax/飽和制限の設計を先に決める。

## 優先改善案

1. A：共通event envelopeとreplay→wall clock写像を固定。イベント・カメラ・バッジ・音声に同じ時計を使う。
2. A：近似previewには「軽量近似」、厳密静止画と短い最終経路動画には「出力経路確認」と表示。既存render_exact_stillを活用し、時間方向FXは静止画で合格にしない。
3. B：Smart FXのbudgetを1killあたり主演出1＋補助1へ抑制。連続キル、集団戦、色の飽和で自動減衰。ただし既存手動設定は残す。
4. B：人物領域・HUD保護マスク。認識信頼度が低ければ全面blurや強flashを避ける。CPU/GPU転送コストも計る。
5. C：true radial、depth-aware blur、2入力transition、optical flow。別枝・別IDから試し、既存の見た目を勝手に置換しない。

負荷：LUT/色は低〜中、全面blurと時間方向混合は中〜高、光学フローとsegmentationは高。実測ではない。WindowsではFXoff基準→単独1効果→複合、CPU→GPU→GPU失敗時CPUの順で色、速度、バッジ合成、ゲーム音、所要時間を比較する。
