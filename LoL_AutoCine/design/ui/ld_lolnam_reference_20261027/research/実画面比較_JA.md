# 実画面と操作構造の比較

2026-10-27。実アプリ起動は未実施。公式UI画像4枚を実際に見て、公式説明とLeague Director原文へ照合。第三者画像は調査用ローカルに限定し、GitHub/ZIPへ転載しない。

League Directorは固定commit `6ddb4ceb45974d6518b43d14522fa9b5ea422139`。1682×896の公式画像とQMdiArea/各子窓を確認した。ドッキング枠と同一視しない。[原文](https://github.com/RiotGames/leaguedirector/blob/6ddb4ceb45974d6518b43d14522fa9b5ea422139/leaguedirector/app.py)。

Lolnamは配布元の1200×675画像3枚（timeline/graph/grade）と公式サイトのgraph/timeline説明を確認。listingの版は1.0.16だが、画像撮影版は未確定。[配布元](https://www.overwolf.com/app/lolnam-lolnameditor)、[公式](https://lolnam.gg/)。

|観点|League Director|Lolnam|AutoCineの提案|
|---|---|---|---|
|メイン|MDI子窓でRendering/Timeline/Visibility/Recording等を配置|中央Mirror Viewと下部timeline|R1は固定3領域、R2はtool rail＋shotstrip|
|かんたん編集|専用wizardは今回未確認|専用wizardは今回未確認|AutoCine独自に3段階画面を提案|
|カメラ|位置/回転/lock/attached/FOV等の数値|camera/rotation/FOVのキーとXYZ表示|既存10style・3制御mode・AUTO/BLUE/REDを維持|
|タイムライン|多段パラメーターとsequence操作|mirror下のtimeline/graph切替|焦点・出力チェック・キーを分離|
|キーフレーム|Time/Blend/Value編集|カメラ/FOV等のキー|デモはFOVだけ実編集、他trackは参照|
|カーブ|補間選択は確認。自由曲線UIは未確認|位置/回転/FOVの曲線を公式画像で確認|時刻/値の点編集＋linear/smooth/hold、自由接線は未実装|
|FX/描画|Particles/Visibility/Fog/DOF等|Render/Particle/Visibility入口|ゲーム粒子と後処理FX35を混同しない|
|色調整|Fog色等。専用LUT/mixer画面は未確認|split比較・色域slider・color wheels|R2は映像固定＋右調整。デモはCSS近似|
|録画/出力|webm/png、時刻/FPS/lossless/保存先/中止|高品質export説明。codec設定の詳細は未確認|JSON保存と実動画作成を分け、後者は無効|
|素材/ショット|sequence保存/読込|Replay Managerの公式説明|自動ハイライトと枠/FX図鑑はAutoCine独自に維持|

数値を俯瞰する構造は詳細調整向き、映像＋curve切替はショットの仕上げ向きと推論する。初回操作では選択肢を絞り、ワンクリックから必要な詳細へ進む順序を両案へ追加した。これは構造からの設計判断で、実アプリ習熟度やユーザー評価・採点の結果ではない。

未観測を製品の「機能不在」と断定しない。Lolnamの録画設定詳細、両ソフトの専用簡単画面、実gesture/接続/録画は未検証。tutorial cover単体取得403は未取得のまま。動画再生、インストール、Replay/Windows設定変更は行わなかった。詳細URL/hashはSOURCES.json。
