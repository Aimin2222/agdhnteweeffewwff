# V2→V3差分

V1/V2は原本のまま保護。V3は別folderへ追加。重複の機械台帳はbyte単位コピーでV2のsnapshotを維持し、今回再検査した原本89/旧37/最新treeは別JSON。

|領域|V2|V3|
|---|---|---|
|ゲーム映像|20作品の部分観察|20作品すべて追加区間再確認|
|明示2kill UI|9|10、V05を追加|
|全編/音声|0/0|0/0、未完を維持|
|短FX精度|通常sample|V22だけ114有効paused-step、failed A〜Dを除外|
|機械687|全件|台帳継承、原本/旧badge保護を新確認|
|thumb|frame93/FX35|frame652/FX35、全687|
|FX原寸/組合せ|未完|全35、083との140合成|
|edge74|数値flag|原寸部分74＋sourcecrop74を目視|
|frame完全原寸|未完|未完、0/652完全審査|
|6motion|式確認|人工6本60fps実生成/全decode、3size数値|
|CPUflash|静的疑義|独立FFmpegでfirst-event-only再現|
|GPU/音声|未実機|人工NVENC/AV smokeのみ、製品未合格|
|仕様|14tests/6recipe概念|全input/expected/steps/log/status、JSON契約、70行接続台帳|
|実装/素材承認/UI採用|なし|なし|
