# Workキル素材統合 2026-10-19

## 品質と素材の境界

固定Work commit `30fdce48dd83a2f73083cf99b569f6fdb71ffffc` から作成した `assets/work_kill_assets/catalog.json` を使用する。正式承認は静止画No.083 `083/a_simple_main` の1件のみ。エフェクト35案はすべてreviewで、本番の自動選択に入れない。review指定も品質合格への昇格ではない。

原本、Work画像、既存37バッジは変更しない。catalogのコピー元とSHA256を保持し、初回読込時に検証する。同一サイズ・更新時刻のファイルはSHA結果をキャッシュし、変更検出時は再検証する。レンダリング生成物は出力先の一時ファイルで、既存のcleanupへ登録する。

311レイヤーは独立した311種の新パーティクルではない。本統合は最新単発peak35枚を使用する。旧装飾コピー、glow派生、原本断片はcatalogに参照情報として保持し、ランダム散布や架空の新規粒子へ変換しない。

## Template / UI API

- `work_kill_frame_id`: 空文字で既存経路。承認標準は`083/a_simple_main`。
- `work_kill_effect_id`: 空文字でpeakなし。35種のIDはcatalog参照。
- `work_kill_review`: 明示opt-in。既定false。
- `work_kill_strength`: `weak`=.45倍、`strong`=1倍。peakだけに適用。
- 位置、寸法、表示時間、不透明度、6種登場motionは既存`kill_icon_*`を共有する。

`list_assets('frames'|'effects', review=False)` は品質ゲート後の候補を返す。未検証の肖像穴座標を持つreview frameは原画見本として確認するだけで、合成時は明示エラーになる。穴座標を推測しない。

`render_preview_pair(template, icon_a_path, icon_b_path, elapsed, size=(1920,1080), row=0)` は透明RGBA全画面を返す。elapsedは録画・リプレイのキル出力時刻との差であり、別の壁時計ではない。任意preview sizeへの縮小は1080p座標でレイアウト・motion後に行う。実チャンピオンのアイコンが取得できないイベントは装飾を省略しログへ理由を残す。偽アイコン、文字、x1は生成しない。

## 合成順序と時刻

最新specの順序は元フレーム装飾→peak→肖像。peakを実肖像穴から除外し、肖像も検証済み円形穴へclipする。No.083穴は原寸2520x1050、中心(528,525)/(1998,525)、半径340.8。peakはspecの配置・縦横比・幅上限・高さ上限を保持してフレーム空間に一度配置する。

6種は既存の`instant, slide_left, slide_right, slide_up, slide_down, pop`をそのまま再利用する。回転・拡大は新たに追加しない。peakの提案scale keyframeはこの段階で採用しない。opacityはキル前0、0秒0、.04秒.8、.08秒1、.20秒.65、終了0で線形補間。終了はA .35秒/C .65秒/ほか .8秒（catalogのdurationが正）。キル時刻は既存のeffect_eventsから取得し、表示は開始包含・終了非包含で統一する。

連続キルは既存の3行feed設計を使用し、4件目では最古の行を終了させる。画面幅384pxを基準にフレームの元縦横比で縮小する。既存37バッジ経路はWorkがoffのとき同じまま残る。

## CPU / GPU

CPUはFFmpeg overlay＋原alphaを保持するgeq envelope。Full OpenCLが利用可能な場合は既存GPUFullStageのresident overlayカーネルを再利用し、同じ素材・行・時刻・強度・順序で合成する。GPU出力のdownloadは既存の1回だけ。NVENC設定とLoL専用音声mux経路は変更しない。

Full GPU非対応時は従来のCPU経路へfallbackし、`work_kill_compositor`を`cpu`と記録する。NVENCが動いたことをGPUエフェクト成功と同一視しない。正式静止画1件の承認は、GPU実行やアニメーション・実LoL録画の品質合格を意味しない。

## 検証の範囲

`tests/test_work_kill_assets.py`: 品質ゲート、SHA変更拒否、円形肖像・中央装飾のpixel検査、元peak穴mask、複数キルの行、6種mirror入口・時刻、FFmpeg実filter出力30frame、OpenCLグラフ・shader構築、Template JSON roundtrip、実No.083原寸と穴alphaを検査する。

OpenCLテストはカーネル生成の自動検査で、Windows GPU上の実行合格ではない。LoL実機、実チャンピオンの可読性、カメラとpeakの同時録画、長時間同期の最終評価は実機QAで別途行う。最新peakは旧motionプレビューのQAを引き継がない。
