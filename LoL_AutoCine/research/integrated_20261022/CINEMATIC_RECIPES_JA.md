# シネマティック演出レシピ案

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 適用の前提

以下は新規の設計プリセット案で、実装・実機審査済みではない。既存CameraPlan、highlight_director、video_effects、highlight_pulse、Work選択を再利用する。相対時刻0=キル。距離倍率/FOV差分/FX強度0–1と、秒・度を混同しない。音声はLoL専用を基準に維持する。

|レシピ|対象条件|キル前→瞬間→キル後の提案値|複数キル時|既存／追加|負荷見込み|
|---|---|---|---|---|---|
|Cinematic|単発・追走、対象可視|pre4/post3秒、third_cinema、yaw−4→3→0度、zoom0→6→0%、FOV0→−1.5→0、pulse0.25|3kill以上はcinema_top、FOVを狭めない|既存chaseを土台、抑制規則を追加|低〜中|
|Impact|短い明確なキル|pre3.5/post2.5秒、キル±0.12秒flash0.12、shake0.08/0.20秒、zoom最大8%|0.5秒以内は重ねず強い方1回、flash連発を抑制|既存impact/FX、共通envelope追加|中|
|Elegant|色とキャラクターを見せる|pre5/post3、yaw最大±3、pulse0.10、bloom0.12、flash/shake0、LUT強度0.20|画角を広げカットを少なく|既存LUT/curve/バッジ、露出保護追加|低〜中|
|Competitive|プレイの理解優先|pre4/post3、top/follow、速度1.0、FXoff、frameoffまたは既存小バッジ、HUD選択保持|同一戦闘の時系列を保持|既存機能中心。品質基準としても保存|低|
|Montage|複数の見せ場を短く並べる|pre4/post3を起点、±0.8秒を基準1.0→0.65→1.0、cut優先、FX主1＋補助1|重複区間を統合、climax順は手動pin優先|既存smart_montageを拡張、音楽拍合わせは新規|中〜高|
|Low-load Cinema|低性能・非対応GPU|top/third、pre3/post2、色補正のみ、preview540p、出力1080p60維持|長い戦闘を短く選び直し、無断低fps化なし|既存CPU代替＋負荷profile|低〜中|

## 時間と音声

ゲーム再生速度の変更は録画のwall timeを変える。キルのreplay秒をそのまま出力秒へ入れない。録画中観測によるevent_video_secondsを使用し、後処理retimeを重ねる場合は写像を合成する。音声のpitch/retimeをどの層が担当するかを明示し、時間軸は1種類に正規化する。

## 合格までの手順

FXoffの同じ区間を比較基準にし、BLUE/RED単発、3連キル、集団戦、壁際で各レシピを比較する。対象可視性・キル瞬間の理解を第一、滑らかさ・色・演出はその後に評価。低負荷案も出力仕様1080p60を黙って下げず、処理時間の増加として扱う。未承認Work素材は確認用のまま使い、公式プリセットの既定素材へ自動採用しない。
