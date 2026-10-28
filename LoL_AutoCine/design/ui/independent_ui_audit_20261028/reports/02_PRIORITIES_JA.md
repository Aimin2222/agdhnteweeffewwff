# 修正優先順位

P0：指定デザインの中核操作/対象選択/映像領域を欠く最優先の修正。P1：忠実再現・導線を阻害する具体的な差。P2：装飾・補助入口・統合差分。実行時リスクは未再現として別記録します。P0はセキュリティ事故や実LoL不具合の発生を示す分類ではありません。

先に候補3の数値・素材、次にR2の下段スタック/対象チェックと共通キー/比較、続いて各設定画面と装飾を修正してください。UIの見た目を直すため本体カメラ計算や素材承認を変更しないこと。

| ID | 優先 | 対象 | 問題 | 根拠 |
|---|---|---|---|---|
| C3-01 | P0 | C3 / T-A-M | 4行の数値欄はあるが、原画の4スライダーとリセットがない。値950/170と原画900/420の違い自体は不具合としない。 | CAPTURE_CONFIRMED |
| C3-02 | P0 | C3 / T-A-M | 演出素材欄が枠カード5枚だけになり、フレーム/エフェクト/アニメの3切替、なし枠、登場6種入口、一覧の状態要約がない。 | CAPTURE_CONFIRMED |
| C3-03 | P1 | C3 / T-A-M | 上部操作が短い文言・狭い幅で極端に右へ寄った。リプレイ白面の左端は原画870、実画面1272で+402px。GPU/音声/HUDという設定の内容も見えない。 | CAPTURE_CONFIRMED |
| C3-04 | P1 | C3 / T-A-M | 4操作は存在するが中央寄せ・幅・文言・アイコンが原画と異なる。実画面の開始は約x549、原画はx465。 | CAPTURE_CONFIRMED |
| C3-05 | P1 | C3 / T-A-M | カメラカードの選択印がなく、見出し/画像が小さく、説明が1行へ減っている。下段が約20px下へずれ、固定領域に不要な縦スクロールがある。 | CAPTURE_CONFIRMED |
| C3-06 | P1 | C3 / T-A-M | 原画のBLUE/RED 2ボタンに自動を加えた3ボタンで、注目対象のドロップダウンも表示されず未選択文だけになっている。 | CAPTURE_CONFIRMED |
| C3-07 | P1 | C3 / T-A-M | 12個の行要素は用意されるが行高27pxで12行目の大半がスクロール外。原画は12行を同時表示している。 | CAPTURE_AND_BOUNDS |
| C3-08 | P1 | C3 / T-A-M | 左下プリセット選択が狭く、保存3操作が小さく離れており、原画の幅のある選択欄と均等な3ボタンの構成を失っている。 | CAPTURE_CONFIRMED |
| C3-09 | P2 | C3 / T-A-M | 原画の画像選択入口がなく、比較UIへの追加ボタンが下段タブの右を占有している。3UI切替の追加自体は必要な統合差分。 | CAPTURE_CONFIRMED |
| C3-10 | P1 | C3 / T-A-M | 原画はチェック付き4フィルター、実画面は細い4テキストボタン。選択状態・操作領域の視認性が弱い。 | CAPTURE_CONFIRMED |
| R-01 | P0 | R1,R2 / detail,curve | 詳細/カーブは既存エディタを開くボタン＋カメラ数値に置換。選択キーの時刻/FOV/補間/追加削除/適用、直接カーブがこの画面内にない。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-02 | P0 | R1,R2 / main,color,all preview headers | 原画の「調整前と比較」に相当する#compare-viewは、現コードでpreview_playを呼ぶ演出再生ボタンになっている。 | CAPTURE_AND_SOURCE |
| R2-01 | P0 | R2 / reference-ln / main | ショット列を.center内に入れ、270pxの全幅timelineを別に足している。映像面の高さ539→485（-54px）、timeline左端12（原画98）、timeline上端約779（原画819）。 | CAPTURE_AND_SOURCE |
| R2-02 | P0 | R2 / main / shot strip | 原画の対象チェック入口がない。ショット列はselect_sceneボタンだけで、チェックボックスはR2で非表示の.scene-pane内にしかない。 | SOURCE_CONFIRMED_NO_POPUP_CAPTURE |
| R-03 | P1 | R1,R2 / easy | 簡単編集の原画はカメラ/雰囲気/キル演出の3群カード。現body(easy)は縦モードボタンと素材画面へのリンクだけ。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-04 | P1 | R1,R2 / camera | モードが縦3ボタン、数値はnumberのみでFOVスライダー/数値がない。原画のモード横3カード、FOV/Yaw等のスライダー＋数値と異なる。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-05 | P1 | R1,R2 / color | 色調整が既存色/FX設定へ飛ぶ3ボタン＋frameControlsになり、ルック3枚・露出/彩度/暖かさ・分割比較がない。素材の設定が色タブへ混入。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-06 | P1 | R1,R2 / material | frameControlsは文字/状態のみのボタンで素材画像がなく、登場6種も2列。原画の大きな画像カード、FXの見た目/強度、登場3列×2行と違う。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-07 | P1 | R1,R2 / export | 出力内に原画の解像度選択/HUD欄がなく、項目順と作成前の確認パネルも変わっている。 | SOURCE_CONFIRMED_NO_VIEW_CAPTURE |
| R-08 | P1 | R1,R2 / main | 概要カードのFOVがカメラ名に、ゲーム音のみが出力FPSに置き換わった。初心者パネル/主ボタンも小さくなり、原画の全幅ボタンと背景のまとまりがない。 | CAPTURE_AND_SOURCE |
| R2-03 | P1 | R2 / main / all tool rail | 左レールは原画の7項目＋アイコンに対し、メインを加えた8項目の文字のみ。レール開始も原画y120に対し約132。 | CAPTURE_AND_SOURCE |
| R-09 | P1 | R1,R2 / main / transport | 原画の現在/総時刻と再生倍率の表示・操作がtransportにない。ミラー4操作を置いたことは接続要件上の追加だが、元の時間確認が失われている。 | CAPTURE_AND_SOURCE |
| R-10 | P2 | R1,R2 / main / header | ヘッダーのUndo/Redo/操作ガイド、ツールのアイコンがなく、body14px/見出し19px等で原画より小さい。3UI切替の追加は統合差分として分ける。 | CAPTURE_AND_SOURCE |
| R-11 | P1 | R1,R2 / all inputs | 1100msごとのsnapshot→renderがinspector-body.innerHTMLを置換するため、入力中のフォーカス/未確定文字/選択が失われるリスクがある。実Windows操作は未再試験。 | SOURCE_RISK_RUNTIME_NOT_RUN |
| R-12 | P1 | R1,R2 / export / fps and encoder | fps/encoderのselect生成でstateに対応するselectedがなく、render後は先頭の60/autoを表示する疑い。theme/trim以外は後段代入もない。実操作再現は未試験。 | SOURCE_RISK_RUNTIME_NOT_RUN |
| QA-01 | P1 | C3 / measurement script | xywh個別差の最大値で判定しており、位置差と幅差が合算する右辺ずれを見落とす。独立再計算は11領域中6 PASS/5 REVIEW。 | JSON_AND_SOURCE_CONFIRMED |
