# 参考映像とAutoCine出力の比較試験仕様

本書は今後の実機試験の仕様。実LoL・Windows録画・NVENC・音声試験を実施した記録ではない。参考映像の0.7〜1秒sampleから厳密frame数の正解を作らない。

## 二種類の比較
参考作品とAutoCineでは内容/patch/対象が違うため、SSIM等のpixel一致を要求しない。参考は「前に相手と進路が見える」「連続kill中wide」「最後にcutaway」「HUDを隠さない」等の意味・時間構造を人が比較する。

内部の旧出力と新出力は同じreplay、同じtake、同じ時刻・解像度を固定し、そこで初めて差分/SSIMを補助利用する。差分が大きいだけで不合格にしない。intentional grade/overlayをmask/別layerに分ける。

## 1試験の保存単位
匿名試験ID、replay patch、BLUE/RED、対象ID、camera style、全recipe値、HUD、素材ID/SHA256/承認状態、6motion、CPU/GPU FX、encoder/driver、API応答要約、入力/出力尺、frame rate、ログ、実行日時、結果・担当を保存。個人の診断情報/音声を公開repoへcommitしない。

referenceの時刻は視覚アンカー候補として持つ。AutoCineはreplay ChampionKill/assist/engageとwall/ClipTake時刻を写像し、retime時は逆変換も記録する。基本観察窓−4〜+3秒は提案で、動画参考の測定値ではない。multi群は最初の前〜最後の後でひとまとまりにし、重なる窓を独立killとして水増ししない。

## テスト一覧
### T01

入力：BLUE/RED各2シーン・左右入替。検査：既存camera/TargetLockのside判定、相手を含むwide。合格条件：同一replay時刻/対象/設定のbaseline比較。陣営逆転、対象外へ固定、未申告API失敗0。

### T02

入力：単発kill/assist/engage各1とkillなし1。検査：イベントanchorと前後文脈。合格条件：ChampionKillのAPI/replay時刻とwall/ClipTake写像を保存。候補beamだけでkill生成しない。

### T03

入力：multi kill 3件以上・間隔短/長。検査：連続戦闘groupとpulse抑制。合格条件：通知を3回読めてもtransitionを3重にしない。最終killのみの演出ログと出力を一致。

### T04

入力：dash・壁際・ジャングル・地形外を含む低角度。検査：通常cameraと任意cutaway。合格条件：通常域の未申告対象喪失0。transition域のintentional roll/occlusionは別ラベル。既知不足は要確認へ。

### T05

入力：死亡灰色/低体力赤縁/teleport/recall。検査：文脈付きQAの誤警告。合格条件：ゲーム固有状態を追加FXや色故障にしない。分類不能は自動修正せず要確認。

### T06

入力：652frame+35FX・明/暗/複雑ゲーム背景。検査：素材静止の合成とsafe area。合格条件：catalog hash不変、意図しない切断/顔隠しなし。thumb passで承認を進めない。レビュー担当の記録必須。

### T07

入力：適用素材×6motions、30/60fps。検査：動的見切れ・位置・一貫性。合格条件：実装した既存motion式と一致。slide/popの全途中frame確認。承認済み静止を動画承認としない。

### T08

入力：同一clipで軽量preview/exact still/final動画。検査：時間FXと最終結果の関係。合格条件：比較modeを表示。静止一致だけでflash/temporal blur合格不可。時刻写像・output frameを記録。

### T09

入力：scene先頭/中間/末尾の3kill、retimeあり/なし。検査：複数kill flash式と時間変換。合格条件：各pulseの中心/幅をframeから実測。CPU式疑義は再現した時だけ不具合確定。

### T10

入力：CPU FXと可能なGPU FX、NVENC/CPU encode。検査：性能・品質・fallback。合格条件：1080p60で設定とdevice/driver、fps、encode時間、メモリを実測。低負荷の効果未測定を埋める。

### T11

入力：LoLプロセス音声・無音・capture失敗。検査：音声範囲。合格条件：LoL以外のdesktop音が混入しない。失敗を明示、無断desktop fallbackなし。

### T12

入力：同一replay/takeのbaselineと新recipe。検査：色・映像の客観比較。合格条件：同一frameに限りSSIM/差分を補助。別動画同士のpixel一致を合格条件にしない。

### T13

入力：研究用候補と正式承認1件。検査：素材状態の保護。合格条件：review/approvedの元catalogが変わらない。未承認採用はユーザー決定待ち。

### T14

入力：長尺・cancel/resume・最終mux。検査：実動画作成の安定性。合格条件：ファイルdecode/尺/音声と映像、job statusを一致。atomic project保存とjob checkpointを混同しない。

## レビュー手順と判定
1. 正規の接続/対象/陣営/イベントをログと元Replayで確定。beamだけの推測を正解にしない。
2. FX off/HUD onのbaselineを作り、camera/素材/FXを一つずつ足す。前後の同じframeと短い動画を見比べる。
3. 0.1秒程度のflash/slideはframe steppingまたは高fpsで確認し、sample点列から継続時間を断定しない。
4. camera通常域と明示transition/cutaway域を区別。死亡灰色、低体力赤、teleportを含むnegative fixtureを先に通す。
5. 結果は合格/不合格/要確認/実行不能。未対応deviceやAPI失敗を見た目合格に埋めない。見切れ、TargetLock、情報の読みやすさ、素材承認、性能を個別欄で判定。
6. 演出採用はユーザーとChatGPTが決める。研究QAは正式承認を変更しない。

## 未検証を残す条件
20作品は全編未視聴、9作品以外は明示kill UIを2件以上確定した条件未達。V15/16/24のkill同期、V01追加区間、音楽/BPM、厳密速度/色/FOV、全素材原寸合成と全motion、実LoL実行・性能が残る。これを完了扱いにしない。
