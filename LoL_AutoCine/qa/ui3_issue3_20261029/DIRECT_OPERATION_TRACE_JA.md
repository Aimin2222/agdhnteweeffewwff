# 70既存＋16追加能力の直接操作追跡：今回確認した部分

この表はWork M03の全86能力の完了判定ではない。`FEATURE_STATUS_86.json` を上書きせず、今回Windows WebView2で実際に入力した経路だけを記録する。

| 能力・画面 | UI入力 | 実App状態 | 画面切替後 | Project/Scene保存・再読込 | 動画出力への反映 | 判定 |
|---|---|---|---|---|---|---|
| 共通露出 R1/R2/候補3 | 0.12、空欄、0、範囲外9 | 空欄/範囲外は0.12を保持、明示0は反映 | 0保持 | NOT_RUN | NOT_RUN | 限定PASS |
| カメラYaw R1/R2/候補3 | 32、空欄、0 | 空欄は32保持、明示0は反映 | 既存R1フローで32保持、今回の0は画面切替未確認 | NOT_RUN | 実LoL未接続 | 限定PASS |
| 前トリム 候補3 | 6、空欄 | 6保持 | 定期poll後に6表示 | NOT_RUN | NOT_RUN | 限定PASS |
| Workフレームと同名FX R1 | 実カタログカードを選択 | frame IDとeffect IDを確認 | R1/R2切替後に保持 | NOT_RUN | NOT_RUN | 限定PASS |
| FPS/encoder R1 | 144/GPU方針を選択 | 既存App設定を確認 | カメラ→出力画面で保持 | NOT_RUN | 実NVENC未実行 | 限定PASS |
| キーフレーム編集 R1/R2 | 無効値を送らない検証コードを追加 | 実シーンなし | NOT_RUN | NOT_RUN | NOT_RUN | REVIEW |

残りの能力は `FEATURE_STATUS_86.json` の従来の未検証扱いを維持する。「従来エディタを開く」入口だけでは直接操作PASSに数えない。Workの239件受入ケースも全件NOT_RUNのまま。
