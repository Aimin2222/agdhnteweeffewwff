# 参考ツール比較とAutoCineへの応用

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 調査方法

公式サイト・公式リポジトリ・操作資料を参照した。アプリ9本のインストール・実機比較はしていない。使い勝手と負荷評価は文書に基づく設計上の推論であり、実測ベンチではない。Lolnamのチュートリアルは約00:45のインストール設定画面のみ確認でき、編集全工程を視聴したとは扱わない。

|ツール・一次資料|確認した設計|AutoCineへ取り込む案|難点・適用限界|
|---|---|---|---|
|[Lolnam Editor](https://lolnam.gg/)|Replay→カメラsequence/色→録画、graph editor、LUT/曲線、比較|ゲーム映像を固定表示して相対カメラ曲線と色を分割比較|公式の宣伝と実機品質は別。敵座標やAutoCine側API可用性の証明にはならない|
|[League Director](https://github.com/RiotGames/leaguedirector)|camera attachment、FOV、fog/DOF、sequencer、保存、キャプチャ|カメラ設定と時間軸を分離、変更前後を保存|手動制作に向く。ワンクリック検出・品質判定は別設計|
|[League Director NG](https://github.com/LeagueOfPoro/LeagueDirectorNG)|sequenceの移動・コピー、curve等の改良|複数キーのまとめ移動、原点復帰|READMEのTODOは実装済みと扱わない。現在patch互換未実測|
|[DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/edit)|編集工程をページで分離、クリップ・速度編集|簡単作成→詳細編集、再利用できる演出レシピ|多機能ページをそのまま並べると初心者の操作が増える|
|[Premiere](https://helpx.adobe.com/au/premiere/desktop/edit-projects/change-clip-speed/change-clip-speed-and-duration-using-time-remapping.html)|時間再マップと速度キーの緩急|キル時刻を基準にした速度曲線、映像時刻とreplay時刻の対応|後処理retimeとゲーム内再生速度を混ぜると音声・イベントがずれる|
|[After Effects](https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/animation-keyframes/editing-moving-copying-keyframes.html)|value/speed graph、複数キー操作|アニメ6種を共通時間曲線へ、減衰を数値化|合成自由度を全部表に出すと操作負荷が高い|
|[CapCut](https://www.capcut.com/resource/how-to-do-slow-motion-on-capcut)|速度曲線を使う編集手順|短い用途別プリセットと強度の1操作|低fps素材を遅くしても情報は増えない。補間の破綻を別審査|
|[Filmora](https://filmora.wondershare.com/guide/change-video-speed.html)|速度変更の操作ガイド|プリセット→カーブ調整、元へ戻す導線|テンプレート依存でシーン情報を覆わないよう抑制|
|[Blender](https://www.blender.org/features/rendering/)、[VFX](https://www.blender.org/features/vfx/)|camera DOF、追跡・マスク・合成|対象と背景の分離、制約付きカメラ、品質診断|2D映像からゲーム内深度を正確復元できるという意味ではない。3Dレンダラ移植は過大|

## 採るもの・採らないもの

優先は「イベントを見つける→安定した画角→短い演出→実動画確認→書き出す」の流れ。ノード編集や全3D制作環境の再現は優先しない。AutoCine既存のhighlight_director、smart_montage、reference_safeへ段階統合し、同じ機能を別名で重ねて作らない。

負荷の見込み：グラフ・プリセット選択そのものは低い。全画面時間方向blur、光学フロー、追跡、複数候補録画は高い。各ソフトのGPU広告をAutoCineの速度保証に流用しない。各案の採用はユーザー判断であり、比較結果は推薦にとどまる。
