# FX検証・互換性仕様 V3

## 再現済みの独立テスト

`SYNTHETIC_EXECUTION_V3.json`はimmutable sourceの関数だけをAST抽出し、人工映像で14caseを実行した結果。アプリmodule起動、製品変更、LoL接続はしていない。

CPU flash：3秒320×180@60灰色、イベント.5/1.5/2.5秒、強度.7。生成式のenableは3窓だが輝度envelopeはevents[0][0]=.5だけ。実デコード平均は各時刻255/127/127、後2回の近傍max128。最初だけ強く明るくなる挙動を独立再現した（静的疑義から段階を進めた）。本体最新UI枝でもcore hash不変だが、実LoL jobでの影響と修正結果は未検証。

flashのhelperへ明示[]を渡すとIndexErrorを再現。ただし通常の_effect_eventsはkillなしでもfallbackイベントを返すため、通常操作で必ずcrashするとは断定しない。call pathとinvalid入力を分けて修正範囲を決める。

radial_blur(.4/.8)、zoom_blur(.4)、glint(.5)、panel_wipe(.5)、stretch_wipe(.5)のFFmpeg graphは人工入力で実行成功。成功は見た目、解像度対応、GPU一致を保証しない。

## 名称と実装の対応

|既存ID|原文上の処理|提案する扱い|
|---|---|---|
|radial_blur|tmix3/5frame、時間混合|保存ID維持。表示説明「時間残像（従来radial_blur）」案。真の放射ぼけは別ID|
|zoom_blur|1920×1080基準のscale/cropとtmix|動くgrid/画面端の文字で残像・FOV欠損を検査。1366出力の実動作未確認|
|glint|unsharpとeq|鮮鋭化/明暗寄り。発光抽出+glowとは区別|
|panel_wipe/stretch_wipe|fade in|名前の印象と空間wipeは別。2映像境界の移動maskは新機能|
|preview/exact still/final|軽量近似/厳密静止/時間FFmpeg|3modeを表示。temporal FXを静止一致だけで合格にしない|

FFmpegの[eq/tmix/setpts/atempo公式仕様](https://www.ffmpeg.org/ffmpeg-filters.html)を参照。ここでの具体的な生成graphの評価はAutoCineの原文と人工実行から得た独自調査。GPU側と同じ強度値の知覚的一致はT10待ち。

## 時刻変換契約

eventのreplay秒、capture wall秒、clip内秒、montage output秒を別fieldで持つ。seek区間/record速度の変更境界でmapを分割し、post retimeは単調piecewise mapを追加する。例：replay100〜102を1x、102〜103を0.5xで記録するとcapture0〜2/2〜4秒。replay102.5はcapture3秒。後段でcapture2〜4を0.5xならoutput4秒。kill、badge、peak、FX、字幕、音声を同じmapへ通し、各層が独自に速度を掛けない。出力frame=round(t*fps)、丸めと境界規則をログへ。spliceの重複イベントはevent_idで排除する。

## 互換性と重複抑制

- 既存ID/旧template原値を改名・削除しない。新しい処理はprocessing_revision（未指定=legacy_v1、新規提案corrected_v2）を明示し、旧見た目のgolden比較を残す。bugfixとして既定を変える場合もユーザー決定とmigration記録が必要。
- corrected flash案は各event中心のenvelopeを合成しclampするかgroup最後だけを選択。重複時はmax合成を基準とし、sumで白飛びを増幅しない。multi最終判断・pulse抑制の理由をログへ。
- fullscreen peakはgroup最後だけ、portrait peakはeventごと等、layer種別を別budgetで管理。manual all-eventsはoverrideとして警告付で保存。game内teleport光はpost pulse抑制の根拠に勝手に使わない。
- 旧37badge、Work frame、Work peak、動画global FXは別layer。frameとpeakのalpha/face clear/3stack、flashとの加算をT06〜09で評価。

## 音声retimeの人工実測

黒映像に.5〜.6秒の白pulse、同時刻1kHz burst、AACへencode後、setpts2*PTSとatempo.5、60fpsで再生成。239video frames、190464audio samples、白pulse開始.983333秒、音声閾値>.1の開始.959125秒（約24.2ms先行）。codec/atempo過渡/測定閾値を含む人工smokeで、LoL音ズレ不具合の証拠でも完全同期の合格でもない。元音声のPTS、codec delay、先頭padding、resample、tempo倍率をT11で比較する。
