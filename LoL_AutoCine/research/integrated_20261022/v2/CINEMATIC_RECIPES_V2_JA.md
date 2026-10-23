# 実映像根拠による6レシピ改訂

全パラメータは実装検討用の提案。参考映像から正確なFOV/LUT/速度/秒数を逆算したものではない。AutoCineへ実装していない。既存対応はV1コード基準に依る。

## Cinematic

目的：戦闘の意味を残し、決着後に映画的な人物shot。根拠：V06, V08, V21（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：−4〜0秒は相手/進路を含むwide、通常cameraを保持
- 瞬間：kill中はwideを維持。multi中は寄りを抑制
- 後：最後のkill後0.4〜2秒に任意cutaway。次戦闘が続く場合は入れない
- 既存の土台：top/cinema_top/follow、相対camera key、控えめgrade、HUD選択、hard cut/fade
- 新規実装/追加検証：複数take収録・shot planner・次戦闘判定・選手名plate
- 注意：低角度のmap外/遮蔽。既存full_autoはclip境界のstyle選択でありshot plannerではない


## Impact

目的：連続kill全てを潰さずclimaxを強調。根拠：V15, V22（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：接近を広く残し、killアンカーを先に確定
- 瞬間：単発または最後のmulti killのみ短いpulse候補（80〜160msは提案値）
- 後：明暗を復帰し次の位置関係を表示。black移行はtransition扱い
- 既存の土台：flash/brightness系CPU FX、kill/multikillイベント、zoom key、fade
- 新規実装/追加検証：重複pulse抑制・最後のkill判定・図形impact layer・正確な時間再配置
- 注意：V15はkill同期未確定。pulse時間は参考動画の実測値ではない。CPU flash複数イベント時の中心式は原文上の疑義、未再現


## Elegant

目的：控えめな色と余白、cutawayで焦点を絞る。根拠：V08, V03（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：広い戦闘と低強度grade
- 瞬間：強い全面blur/flashを既定off。badgeを小さく抑える
- 後：任意の人物/小物shotでDOF。次sceneへ落ち着いて接続
- 既存の土台：grade、Replay DOF、follow、frame/FX強度、fade
- 新規実装/追加検証：小物/人物shot targetの選択・shot list・明暗背景のサムネイル
- 注意：Replay DOFと2D中心blurは別物。白背景で淡いFXが消えるためテーマ表示と映像の合成を分ける


## Competitive

目的：プレイとHUDの読みやすさ優先。根拠：V04, V07, V11, V12, V13, V20（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：−4秒程度から接近/相手/ミニオンを残す
- 瞬間：HUD on、広いcamera、FX offを既定。試験速度1.0x
- 後：1〜3秒の結果/退路を残してcut
- 既存の土台：scene scan/選択、top/follow、HUD保持、FX off、cut、出力設定
- 新規実装/追加検証：通知/顔/HUDの重なりを避けるsafe area検査（既存保証なし）
- 注意：低体力の赤縁と死亡灰色を画質異常と誤判定しない。参考動画全てが厳密1xとは未検証


## Montage

目的：戦闘のまとまりごとに表情の違うshotを接続。根拠：V02, V16, V22, V24, V25（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：同じ戦闘内では位置関係を保つ
- 瞬間：multi群を一つの編集単位にし、各killへ同じtransitionを重複させない
- 後：fade/hard cutを基準。任意の光/blur/roll移行とintroは別layer
- 既存の土台：scene cut、fade、基本title、相対key、grade
- 新規実装/追加検証：真の2映像dissolve・空間wipe/blur・複数take・任意intro・遷移域のQA注釈
- 注意：softの明るさdip、panel/stretchのfadeは見た目が別。V24のrollを通常camera挙動へ混ぜない。長いintroを既定にしない


## Low-load Cinema

目的：処理負荷を抑えた候補として安定した戦闘映像。根拠：V04, V07, V20（[観察詳細](MONTAGE_VIDEO_ANALYSIS_V2_JA.md)）。

- 前：既存追従と広い画角
- 瞬間：軽いgrade/静止badgeのみ候補。重いblurや多段合成off
- 後：hard cutまたは単純fade
- 既存の土台：既存camera、CPU基本grade、static badge、cut、GPU/NVENC設定への導線
- 新規実装/追加検証：端末別の計測と適応（本研究で性能実測なし）
- 注意：低負荷は設計意図でありFPS改善の実証ではない。NVENC encoderとGPU FXを分離、1080p60品質を勝手に下げない


## 既存機能の意味を保つ

既存10 styles、fixed_auto、full_auto、TargetLock、37asset badge、89原本、652候補、35FX、6登場動作を削除/統合しない。full_autoの選択はclip境界の承認側style群を使う設計で、未設定時fallbackを「常に最良shot」と呼ばない。

6motionsはinstant/slide_left/right/up/down/pop。既存slideは0.260秒smoothstep、popは横16pxの減衰振動であり、拡大bounce/alpha animationではない。V13の幾何学plateと同じものだと扱わない。CPU radial=tmix、zoom=scale/crop+tmix、glint=unsharp+eq、focus/vr/sphere系blur等は名称より実際のgraphを基準に比較する。

preview軽量近似・exact still・最終動画を区別する。exact stillだけではtemporal FXを検証できない。killイベント時刻はreplayとwall/ClipTake双方に写像し、retime追加時は合成写像を必要とする。GPU/NVENCはencodeとFXを分け、LoLプロセス音声をdesktop音声へfallbackしない。
