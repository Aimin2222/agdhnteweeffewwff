# 残件・実機検証パッケージ
## 必要な環境と入力
同patchで再生可能なROFL、LoL Replay API2999、BLUE/RED両陣営の対象とイベント正解、旧project/settings/golden出力、WGC/LoLプロセス音声helper、実GPU driver、採用UI記録、十分な空き容量。研究範囲Documents/Codexにrofl0、2999閉。勝手にLoL起動・camera POSTは行っていません。

## 実機手順
1. source commit/patch/OS/GPU/FFmpeg/helper/encoder/GPUFX能力、replay hashを記録。
2. 旧UIで同scene基準を保存。BLUE/RED各2scene、10camera、TargetLock on/off、左右逆位置、dash/壁/遮蔽/死亡/teleportを採取。
3. scan kill/assist/engage/no-killを正解照合。replay→capture→output TimeMapを保存しseek穴を跨がない。
4. 37badge/approved083/明示review候補の各motion・3段・HUD/HP、弱強FX、速度.5/1/2、30/60・3sizeを出力。651geometry未確定を見落とさない。
5. preview/厳密still/exportのbboxとevent同frameを比較。Flash単発/連戦/empty境界、Zoom飽和、固定1920graphを元revisionと比較。
6. CPU/NVENC/GPUFXを別に判定。GPUFX不可なら理由表示。LoL音声required時無音を成功にしない。他アプリ音混入を別音源で確認。
7. 長尺の先頭/中間/末尾でAV drift、cancel/retry、失敗clipだけ再出力、checkpoint整合、PythonなしPC配布を検証。
8. input/events/time_maps/ffmpeg_args/run_anonymized/output_probe/human_review/resultをT01–14別に保管し、証拠のある項目だけPASSへ。

## 未確定件数と担当
動画7/20の2通知未確定、音声20/20未聴取、全編精査17/20未完（3はほぼ全編の粗いサンプリング）。追加のブラウザー観察はWorkで継続可能ですが、HUDがないものを通知確認済みにはできません。
portrait geometry651、原本制約19、全652の実HUD審査、全35FXの実LoL/全時間人手審査、GPU FX parity、実LoL録画・音声・全14製品判定は未完。ユーザーの元資料/採用判断、Codexの製品統合、Windows/LoL入力が必要。
AV2条件とZoom/Flash/縮小mirror差は独立再現済み、製品jobへは未追試。未知値や再現ハーネス例外を実LoL障害確定にしない。

## 試した代替
原寸はテーマ別分割652・3背景66ページ、FX4形状人工背景/公式icon、144実pixel動画と全652幾何、GPUは別OpenCL filterとsandbox外再試行、AVはPCM/AAC/PTS再測定、動画は10未確定すべて別区間追加、原本は既知コピー探索55,578。全件合格の代替にはしていません。

## 再実行
research_scriptsは実行した研究用原文。Python/Pillow/numpy、FFmpeg、固定BASEのread-only core、元687素材・catalog・official icons、V3 JSONを必要とします。lab_commonのR/W/O/V3/OLD/S/FFを自分の研究用コピーに合わせる。製品checkoutへ出力しない。source_input_manifestでhash一致を確認し、flash_fx_lab→flash_compat_revision→fx_temporal_expanded→zoom_candidate、camera_math_qa/camera_recipe_rules、composition_motionを実行。ブラウザーobserverは当該computer-use実行環境専用で一般Pythonだけでは再生しません。元動画のダウンロードはしていません。
