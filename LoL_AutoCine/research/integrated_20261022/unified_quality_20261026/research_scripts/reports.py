from finish_research import textfile
from common import *
import collections,shutil,platform

docs={
'A1_similarity/README_JA.md':'''# A1 重複・類似・残す候補の整理
前回: alpha-dHash候補1464組、完全SHA重複0。今回: 1464組を色/alpha-support IoU/光量/全体RGBAの複数指標で再計測。同テーマweak/strong等1047組、全35FXの595組、652枠それぞれの既存37バッジへの印象上位3候補も生成。

新しいAI画像確認: 枠24組（前回1464内14＋別のfamily10）、FX8組、既存37との印象6組、計38比較シート。暗/明背景の縮小静止画像を実際に確認。人間の正式承認・全時間検査ではない。1464内の新規未目視1450組。legacy比較は652×37の総当たり目視ではない。

発見: alpha-dHash同点でも金角枠と氷円枠など明確な別デザインがある。weak/strongも中央紋章や外周形状が変わる例があり、明るさ違いだけとは扱えない。FX Bの細い金光と赤黒FXがMAE上近くなる例がある。大きい透過キャンバスが全体MAEを小さくするため、数値順を削除順・採用順位に使わない。次の自動類似判定はforeground union内差、色分布、肖像穴形状、中央紋章の局所比較を分けるべき。現段階は人の比較導線用候補生成。

ASSET_CLASSIFICATION_RESEARCH.jsonは687件を1優先保持/2意味のある差/3同族表示/4再設計検討/5ユーザー判断へ研究整理。未確認を良好と推測しない。No004の原本制約は5保留。根拠なく4を付けない。3は表示上まとめる提案で、ファイル統合や削除ではない。

ユーザー不採用5点: FX A/C/D、023/main、039/palette_reference_03。原本保護・再推奨禁止・再承認質問なし。最後のパレットは研究参照としてのみ保持。catalog承認状態は全件変更0。正式合格1/確認用651とFX35確認用を維持する。

Codexへ: 推薦可否フラグは素材承認と別。stable assetId、原本由来、兄弟variant、類似候補理由、正式状態、ユーザー除外を別フィールドにする。合格条件は除外5件が推薦・自動ペアに出ず、手動研究参照は理由を明示、既存37/89原本は同一hashであること。
再実行: assets.py→record_visual_reviews.py→assets_followup.py→finish_research.py。画像所見はAIが確認して記録した静的記録であり、スクリプト再実行だけで新しい目視をした意味にはならない。
''',
'A2_quality/README_JA.md':'''# A2 素材品質と肖像安全領域
前回687件機械検査、P0 50/P1 90のAI比較審査140件を継承。今回は未確認P2のテーマ分散24件を新たに画像確認。累計異なる素材164/687、P2残523。重複比較シートに再登場した素材を新規審査件数へ二重加算しない。

GEOMETRY_CANDIDATES_652.json: 256px幅のalpha<=24連結領域から左右の閉じた穴を探索し652/652で候補を取得。原寸center/bbox、384幅提示時のcenter/bbox、顔内容10%内側、中心紋章canvas中央、FX開始検討値.15を記録。すべて研究開始値であり、作者の肖像形状や最適値の確定ではない。651暫定形状は正式確定していない。No004見切れ8＋パレット11の19原本制約も未解決。

P2_reviewは元装飾と候補穴マスクに顔を入れた派生を明暗背景で比較。24件では顔中央の大きな隠れを抑える候補を確認した一方、低解像度穴maskの境界、明背景での白金/淡色の弱さ、暗背景での赤黒、中心の高密度、3段時の張り出しが残る。個別所見はP2_AI_IMAGE_REVIEWS.json。native全ピクセル、全35FX、6登場動作、実HUDとの時間審査を全652へ実施したものではない。

Codexへ: geometryRevisionとsourceHashを紐付け、元アートへ穴や顔を書き込まない。局所portraitmask→顔トリム→ornament→同じgeometryのFX→全体transformの順を契約化する。四角/円を名前だけで決めない。alpha閾値や256px maskを製品の最終高解像度maskとして無条件利用しない。候補採用には原寸暗/明/実映像＋1/2/3段×6motionの時間確認が必要。
''',
'A3_fx/README_JA.md':'''# A3 Flash・Zoom・その他FXの追加実証
前回のCFR Flash V5 48限定試験、Zoom12比較、切替履歴試験を継承。今回同じ結果を新規本数に加算しない。SOURCE_COMPARISON_7によりqueried PR49のeffects等7ファイルは旧snapshotとAST一致を確認した。別の最新開発ブランチ全体の不具合を断定しない。

## Flash
新規はVFR風PTS/seek戻り/pause/速度変更の4列をFFmpeg filterへ与えたCPU実行。各event項をgte(t,exactTime)で因果gateしmax合成。最初のeventより前のRGB差分0、event後は実際に明るくなる。FLASH_NEW_CLOCK_RESULTS.jsonにgraph/PTS/平均値を保存。VFRコンテナのmux往復や実Replayシーク成功ではない。合成列が戻るseekはアプリの履歴管理の代替ではない。

明背景RGB210/175/120で強度.15/.5/.9の既存加算系はclipし得る。独立RGB倍率上限候補は254/maxRGBにgainを制限し3patchで255飽和0。ただし3強度が同じ上限に張り付くため強弱差が消える。flash_headroom_patch.pngも同じ色に見える。これを最適解/採用済みにしない。因果gateと露出/色管理は別の修正。暗いpixelへの効果、輝度perceptual差、HDR/range、連続時の上限はREVIEW。

## Zoom
正規化した時間tmixと、独立Pillow空間radial候補（5scale平均）を分離。移動する橙点に既知の座標中心を与える比較18frameとPNGを保存。空間固定中心では対象も二重にずれ、対象中心候補では対象中心を保ち周囲が伸びる。時間tmixは過去位置の二重像。これは追跡器実装やゲーム対象認識ではない。シーンcut/seekで履歴を破棄する条件は前回結果を継承。GPU kernel、正規化weights、linear/encoded色、alpha/range、frame continuity ID、中心座標のview変換を独立受入項目にする。

## その他と組合せ
8FX×.15/.5=16 CPUサンプル動画（18 native1920処理frame、提示640幅）を生成し全frame decode。motion_camera/glitch/focus_blur/camera_shake/vignette_fx/glint/chroma_leak/radial_blur。現在のradial_blur名のgraphはtmix時間混合で、本来の空間放射blurではない。

4組合せを実CPU描画: motion_camera+camera_shake、glitch+chroma_leak、focus_blur+glint、zoom_blur+flash。.15は研究開始値。最後はtmix正規化のみでFlashは旧gateのまま。全render PASS、品質REVIEW。起動込み単回elapsedを保存したが、GPU/実時間FPS/性能順位の証明にしない。移動系重ね過ぎ、時間blur+flash、色ずれ同士は自動presetの既定で重ねず、プレビューと上限を確認する提案。

対象保持/背景のみモノクロは今回照会したeffects/jobs内で該当mask処理を確認できず、実証NOT_RUN。全projectに絶対存在しないとは断定しない。必要条件は対象mask、境界保護、遅延/欠損時fallback、CPU/GPU同一色空間。素材35FXの画像審査と映像filterの実行可能性は別の集合。
再実行: fx_extended.py→fx_followup.py。本体へ統合しない。
''',
'A4_parity/README_JA.md':'''# A4 全登場時間のプレビュー/出力比較
前回72条件×5sample=360frameから、今回はFXoff/on×1/2/3段×6motion×3解像度=108条件、各30fpsのn0..29、全1秒3240frameへ拡張。1920×1080/1366×768/1280×720、event.10/.15/.20秒、duration.55、scale.85、opacity.7。No083/a_simple_main＋D_project＋公式アイコンを研究コピーで使用。

既存CPU FFmpeg書出しとPillow previewでbbox差>2pxを持つ条件84FAIL、残24はREVIEW。欠落bbox比較48sampleがあり、0px合格へ置換しない。画面外登場/時刻境界/終端/段割りなどが混ざるのでFULL_ANIMATION_RESULTSの各frameで判断する。黒背景の旧経路と青灰背景の候補の背景差自体を改善根拠にしない。6比較PNGの登場中には端での見切れが残る。演出として許すかは別判断。

共通RGBA候補は同じ準備済みoverlay列を独立FFmpeg/Pillow合成器へ渡し108/108条件RGB最大差0。共有rasterを消費する合成器の一致であり、独立した2つの配置計算が正しい証明、全素材対応、製品修正、圧縮MP4のpixel完全一致ではない。

floatの開始/終了境界とmicrosecond量子化の差108行も記録。今回表のn21は.15+.55の終了境界が主因。すべてを「開始時刻の不具合」とまとめない。時刻を共通有理数/整数tickで定義しintervalは[start,end)、start/end丸め規則を一度決め、FFmpeg文字列とpreviewで同じ値を使う。

Codexへ: layer_plan、row割当、activation、elapsed、motion transform、anchor、scale、mask、opacity、FX layer、clipを共通OverlayPlanにする。1080を単純縮小する修正だけでは登場中の不一致が残る（前回FAIL）。実viewport letterboxとDPIは最後の画面変換とし動画座標へ混ぜない。6motionの既存意味（popは横方向減衰）を無断変更しない。native Windows DPI/スクロール/実アプリ/実ゲームはNOT_RUN。
受入: 全frameで前後境界の出現ID集合一致、同じraw RGBAでRGB差<=2px値（候補fixtureは0）、bbox差<=2px、重畳differenceを保存。欠落bboxは時刻/画面外の理由を記録し別審査。動画H264は色変換/圧縮許容を別定義。再実行parity_full.py。
''',
'B1_camera/README_JA.md':'''# B1 自動構図・切替の研究候補
採用済みthird/third_cinemaを変更せず、前回36条件の既存数値/BLUE・RED/90・180度可視化を継承。今回120frameの既知2D対象位置がn30/n75で切替わるfixtureを4方式で比較した。実LoL座標軸校正・TargetLock追従・地形遮蔽の実機成功ではない。

raw最大step626.498、速度制限14units/frame、速度＋加速度制限14units/frame/1800units/s²。速度だけは加速度最大12600で段差が残る。加速度制限は滑らかだが平均追従遅れ189.435units。hold-then-cutは切断として626.498の跳びを残す。小さなstepだけで採用せず、対象が構図から外れる遅れと意図したcutを同時評価する。

既存固定自動/フルオートは別モードのまま。提案条件: 既存三人称の斜め後ろanchorを初期値、manual override最優先、実サイドと座標変換のrevisionを明示、接続中の対象IDを維持。視点切替にはspeed/accel制約、追従遅れ上限、遮蔽confidence、hysteresis、cut許可区間を別管理。90/180回転は最短角のwrap規則とサイド別期待方向を実機で照合し、REDを画面の左右だけで反転しない。

複数キルは生存対象/直近victim/着弾先のscreen-space hullへ余白を取り、FOV上限と距離上限に達したらcut候補へ。長射程は発射/飛翔/着弾phaseで対象集合を切替える。地形meshやvisibilityが無いfixtureでは遮蔽成功と呼ばず、最後の安定姿勢へfallback。固定＋小補正と自由回り込みを同じスイッチに混ぜない。

METHOD_COMPARISON.json/png/mp4が新規証拠。研究座標にゲームunit換算の保証なし。LoL実機、遮蔽物、長射程、複数人実録画、回転酔い・視認性、API低速化はNOT_RUN。再実行b_fixtures.py。
''',
'B2_oneclick/README_JA.md':'''# B2 ワンクリック・既存モンタージュとの接続
PR49 smart_montage/highlight_director/montage_fx原文を読み、既存choose_scenesをpure fixtureで実行した。新たな自動映像理解を実装済みとはしない。5eventのscore順はa1,k1,k4,k2,k3。独立候補は同actorで間隔<=3秒のkillを3/1/1へgroup化し前4/後3秒を仮付与。

4限定assertion PASS: 同じevent_id重複除去、同時刻の別victim保持、手動順序優先、同戦闘group。既存scoreが意図する見せ場順と時間groupを別目的として比較する。自動候補のFX同時数1/peak alpha.35は研究開始値で最適値ではない。

Codexへ: 既存標準とスマートの入口を保持。event identity→user override→group候補→既存score→trim→camera recipe→FX budget→job snapshot。推奨結果はユーザー確認で覆せる。wait/slowはevent local時刻でなくsource→timelineの区分写像を明示し、キル数を失わない。実engage検出/被写体スキン認識/ベスト映像理解/6レシピの新しい実映像成功はNOT_RUN。20参考動画の観測資料は継承のみで今回の再生0本。

PLAN_FIXTURESと合成plan_compare動画はイベントデータの可視化でゲーム出力ではない。1クリック完了の受入は実LoL接続→scan→選択→ゲーム音のみ録画→CPU/GPU出力→音声/画角QA→成功/失敗通知まで別E2Eで行う。再実行b_fixtures.py。
''',
'B3_audio/README_JA.md':'''# B3 ゲーム音声・同期の実行可能範囲
今回の新規実行は48kHz mono合成880Hz pulse(.5/1.5/2.5秒)と合成flash映像のAAC/MP4 encode/mux/full decode。音を再生せずファイル数値解析を実施。LoL/システム/他アプリ音声の収録0。

4診断assertion PASS: 通常3秒、映像2倍長＋atempo.5、意図的に映像だけ伸長、意図的に音声なし。最後2つのPASSは不良出力を診断できた意味で、出力合格ではない。通常の時間長差約8ms、正しいslow約14.7ms、誤ったslow約2.959秒。音声なしstreamを検出。AV_FIXTURE_RESULTSにactual PTSと全frame時刻、音声envelope onsetを保存。

slowの映像flashは.966667/2.966667/4.966667秒、音声onsetは.96/2.97/4.97秒。対映像onset最大約6.7ms（10ms envelope測定）。理想的な1/3/5秒に対しては映像が約33ms早い。duration許容.1秒PASSだけで同期全合格にはしない。atempo/時刻変換/encoder frame複製を含むevent同期はREVIEW。

最初の測定では自動選択された15fpsを30fpsと仮定してしまったため無効化した。現結果は-r30 -fps_mode cfrを明示、FFmpeg showinfoでPTSを取得し、passthrough全decode枚数と照合して修正済み。過去の測定ミスを製品不具合として扱わない。ffprobeは環境になく、インストールしなかった。

既定はLoLの対象PID＋子プロセスだけ。全デスクトップloopbackへ黙ってfallbackしない。ゲーム音必須か無音許可かをjob設定で分離し、helper未起動/streamなしは明示停止かユーザー許可済み方針へ。CPUとNVENC双方で同じ基準PTS、concatでは各segmentのvideo/audio開始とdurationを照合する。実ゲーム音、複数クリップconcat、長尺drift、GPU/CPU差、参考20本の実音源解析はNOT_RUN。音源と実Replay/録画環境が必要。

参考: [Microsoft process-loopback sample](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/) は対象process treeのinclude/exclude取得設計を示す。既存helperがこの契約を実機で満たすかは別検証。再実行audio_fixtures.py。
''',
'B5_distribution/README_JA.md':'''# B5 配布・異常系・復元
研究用状態機械へnone/disk_full/lol_disconnect/cancel/clip_failure/write_failureの6条件を注入。日本語・空白path内のjournalへ一時ファイル→os.replace→再読込。完了clipを再生成せず欠落分のみretry、fixture camera/HUD/TargetLockを復元するassertionは6/6PASS。ディスクを実際に満杯にしたりLoL通信/サービスを切断した試験ではない。実製品のerror handler成功と混同しない。

日本語BATはUTF-8/CRLFの文字列検査だけPASS。実行していない。Python無し別PC、EXE起動、FFmpeg/helper/WebView2同梱、管理者権限なし、実録画、CPU fallback、強制終了復旧はNOT_RUN。

Codex受入: クリーンなWindows標準ユーザー/日本語空白path/書込不可path/FFmpeg不在/音声helper不在/WebView2不在/空き容量不足/NVENC失敗/clip単位失敗/キャンセル/クラッシュ再開を個別にテスト。OSサービス/防御/ネットワーク設定を変更して通さない。中止はcancelledとして成功件数へ加算せず、部分出力とログの場所を返す。job journalにはschema/version/source hash/clip id/encoder実値/source-PTS範囲/一時出力hashを記録し、rename済みclipだけ完了扱い。

frozen実行時に外部python.exeの存在を仮定しない。[PyInstaller runtime information](https://pyinstaller.org/en/stable/runtime-information.html) の__file__/sys.executable規則に基づき同梱resourceを解決する。[WebView2 distribution](https://learn.microsoft.com/microsoft-edge/webview2/concepts/distribution) のEvergreen/Fixedを配布方針として選び、単にWebView2不在を「ネットワーク設定を変えれば直る」と扱わない。今回は導入/変更なし。
再実行b_fixtures.py。異常系E2Eはユーザー許可された隔離テスト環境が別途必要。
'''}

for path,content in docs.items():textfile(path,content)

par=load(O/'A4_parity/FULL_ANIMATION_RESULTS.json');au=load(O/'B3_audio/AV_FIXTURE_RESULTS.json');review=load(O/'A2_quality/P2_AI_IMAGE_REVIEWS.json')
statuses=[
 ('A1-M','PASS','1464既存frame候補・595FX組・1047同族組の指標生成','一致素材の確定ではない'),
 ('A1-V','REVIEW','新規38組のAI比較画像審査','1464内1450組の新規目視は未実施。人間承認0'),
 ('A2-V','REVIEW','P2新規24、継承140、累計164/687','P2残523、全素材全時間の互換未完'),
 ('A2-G','REVIEW','652/652肖像穴候補数値を生成','651暫定・19原本制約は未解決'),
 ('A3-F','PASS','4合成clock列の先行RGB差分0','実Replay seek/VFR muxではない'),
 ('A3-H','REVIEW','3明色patchのheadroom候補で255clip0','上限に張り付き3強度の見た目差がない'),
 ('A3-O','PASS','16他FX+4組合せCPU描画','機械decode。全映像の品質/負荷承認ではない'),
 ('A3-Z','REVIEW','移動中心の時間/空間blur18frame比較','真の対象追跡/GPU成功ではない'),
 ('A4-L','FAIL','旧経路108条件中84条件にbbox差>2px','残24REVIEW、missingbbox48sampleは0px合格にしない'),
 ('A4-C','PASS','共通RGBA候補108条件3240frameでRGB最大差0','同じ準備rasterの2合成器比較限定'),
 ('B1-C','REVIEW','4カメラ切替方式120frame比較','滑らかさと追従遅れのtradeoff、LoL成功ではない'),
 ('B2-P','PASS','イベントgroup/ID/同時別victim/手動優先4assertion','映像理解/実戦闘境界検出ではない'),
 ('B3-D','PASS','合成AV4種の診断assertion','意図的な不良動画2種の検出を含む'),
 ('B3-S','REVIEW','actual PTS/合成pulseの同期を測定','slowの理想時刻差と10ms測定精度が残る'),
 ('B4-M','PASS','70機能ID対応漏れ/重複0、状態契約15件','製品GUI押下/遷移テストではない'),
 ('B5-R','PASS','注入異常6種のjournal/復元/再試行','実disk-full/LoL断/製品クラッシュではない'),
 ('LIVE','NOT_RUN','LoL/TargetLock/地形/長射程/実ゲーム音/GPU/NVENC/nativeDPI','この研究で実アプリを操作していない'),
 ('DIST','NOT_RUN','PythonなしPC・EXE・実concat/長尺drift','配布/実音源/実録画が必要'),
 ('UI-NEXT','NOT_RUN','League Director vs Lolnam Editor UI追加研究','現研究の保存・報告後の別工程、今回は未着手')]
checks=[dict(id=i,status=s,result=v,limit=l) for i,s,v,l in statuses];save('VALIDATION_REPORT.json',{'checks':checks,'counts':dict(collections.Counter(x['status'] for x in checks)),'PASS_definition':'記載した限定assertionが通った。製品リリース合格ではない','formal_material_changes':0,'production_integration':False,'live_game_success_claim':False})

textfile('README_JA.md','''# LoL AutoCine 統合品質研究・素材類似整理
研究期間2026-10-26〜27。前回成果991f107857ee789b90f9fb5c24d2224a7addb4dfを引継いだ追加実証。実行可能なCPU/合成fixtureの研究納品を整理した。製品修正・正式素材承認・実LoL成功は未完である。

index.htmlを開くと9分野の資料、比較画像、手動再生動画を見られる。自動再生なし。B3動画だけ合成pulse音声を含み、初期muted。研究結果と正式採用を分ける。

|分野|今回の追加|残件|
|---|---|---|
|A1 類似|1464枠候補再計測、FX595組、同族1047組、AI比較38組|全人間選別・1450既存候補組の新規目視|
|A2 品質|P2新規24素材AI審査、652肖像候補数値|P2残523、651正式形状、19原本制約|
|A3 FX|Flash4clock列、他FX16＋組合せ4、移動中心blur比較|実Replay/GPU/色・負荷/最適強度|
|A4 位置|108条件・全時間3240frame、旧84FAIL、共有RGBA108PASS|nativeDPI/GUI/独立planner/全素材|
|B1 カメラ|切替4方式の軌跡・遅れ比較|BLUE/RED/TargetLock/地形の実機確認|
|B2 一括|既存処理対group候補、4assertion|実戦闘・録画E2E|
|B3 音声|合成AV4動画のactual PTS/音声decode|ゲーム音/concat/長尺/GPU|
|B4 機能|混合7＋4と比較3/5/8の70機能対応、15状態fixture|製品GUI実行|
|B5 配布|注入異常6種・日本語journal・CRLF text|Python無しPC/EXE/実異常系|

素材AI審査は継承P0/P1 140＋新規P2 24＝164/687。今回の比較組数を素材件数に二重加算しない。機械PASS/AI REVIEW/人間正式承認は別。ユーザー不採用5点を再推薦しない。

詳しい条件/再実行手順/実装指示は各分野READMEとCODEX_HANDOFF_JA.md。VALIDATION_REPORTは限定試験の合否で、総合製品PASS表ではない。SOURCE_REFERENCES/SOURCE_COMPARISON_7は照会した原文の固定コミット、PROTECTIONは原本保護、CONTENT_MANIFESTはZIP内hash一覧。

League Director／Lolnam Editor UI追加研究は未着手。現在の保存・完了報告より先に開始しない。今回UI候補評価・順位付け・新UI画像/プロトタイプは制作していない。

封印ZIPのGitHub再取得・実展開・全hash結果と保存SHAは、循環hashを避けZIP外のSAVE_RECEIPT.jsonに記録する。
''')
textfile('CODEX_HANDOFF_JA.md','''# Codex向け 安全な修正・実装の引継ぎ
これは実装提案。AutoCine本体に研究コードをコピーして完了扱いしない。参照固定commitはSOURCE_REFERENCES。PR49 queried7ファイルは旧snapshotとAST一致だが、PR44など他ブランチを上書きする根拠にしない。

1. Flash: source/replay/event/timeline/encode PTSの写像を先に固定。CFRはceil(event×fps)の因果gate、VFRはactualPTS>=event。丸めは開始前へずらさず同時別victimを保持。max合成と残光上限を独立設定。通常/slow/seek/pause/長尺を別回帰にする。明るさ修正は因果性修正と別PR/別revision。
2. Zoom: tmix自動正規化を小さい独立修正候補にする。cut/seek/clip切替のcontinuity IDが変わったら履歴破棄。真の空間radialは新しいeffect IDで対象中心座標/weight正規化/端サンプル/alpha/color空間を定義し、時間blur修正と混ぜない。CPU/GPU同一PTS比較後に採用判断。
3. Overlay: 共有OverlayPlanでrowと時刻とtransformを一元化。先に準備RGBAの合成器一致を確認し、次に独立plannerの入力/出力同値を検証。画面上のDPI/letterboxは最後。旧84FAILを基準に全frame比較。missingbboxは失敗理由/画面外/非表示のどれかを記録する。
4. 素材: catalog formalStatusは不変。research geometry/AI review/userExcludedを別領域に保存。原本/37badge/89masterのhash照合、推薦から除外5件を落とす。alpha-dHash/MAEの低さだけで削除・統合・再承認しない。P2残523と19原本制約を明示する。
5. Camera: 採用済み斜め後ろを保持した別モードで研究。manual優先、BLUE/RED実軸、TargetLock対象IDを固定。速度/加速度/lag/cutの4基準をログ化し、対象画角・遮蔽confidenceを実機で確認。図の研究unitをそのままゲームunitへ代入しない。
6. Oneclick: 既存smart_montageへ全自動置換せず、score順と同戦闘groupの選択理由を保存。event重複IDだけ除去し別victim同時刻を残す。手動overrideは候補更新でも保持。ゲーム音のみを既定にし、成功通知は実出力QAの後。
7. AV: helper対象PID treeを検証し、無音時の全デスクトップfallbackは禁止。actual PTSとsample countからdrift/concat境界を測る。durationだけPASSにしない。合成testは録画機能の成功証明ではない。
8. UI/配布: ユーザー保持の7main＋4detail/material/frame、比較3/5/8維持。70機能導線・テーマstate不変の契約を接続。新しいUI採用判断なし。日本語path/標準ユーザー/FFmpeg/helper/runtime/CPU fallback/再開を隔離PCでE2E実施。Windows設定を変更して試験を通さない。

推奨修正順は時刻因果性→tmix正規化/履歴→Overlay共通化→実AV/復元→新しいcamera/素材整理。これは不具合修正の依存順で、UI順位や素材の正式採用順位ではない。各修正で旧状態へ戻せるrevisionとdiff、入力hash、raw比較frame、実エンコーダ、NOT_RUNを記録する。
''')
textfile('NEW_VS_INHERITED_JA.md','''# 前回と今回の差分
継承のみ: 20本の既存映像観測/6レシピ/12実装ルール/70監査/687機械審査/P0P1 140目視/旧Flash48/CFR/旧Zoom12＋cut/旧camera36/旧位置72×5sample。これらの本数を今回の新規実行数に加算しない。
新規: A1比較指標と38画像比較、P2 24と652穴候補、Flash4clock・16他FX・4組合せ・空間中心比較、108条件3240全frame位置比較、4カメラ方式、4group assertion、4合成AV診断、70接続表/15独立状態fixture、6注入異常。原文照会PR49/44/51/52の資料を固定した。実動画観測/実LoL録画/正式承認/製品コード統合0。
''')
textfile('REPRODUCE_JA.md','''# 再実行と依存入力
研究用Python+NumPy+Pillowと既存FFmpeg CPUを使用。pip install/RTK hook/Windows設定変更なし。scriptsはこのworkspaceのwork/autocine_unified_quality_20261026/に置いた構成でR=parents[2]を想定する。ZIP展開だけで687原本を同梱したものではない。別PCではcommon.pyのR/OLD/S/A/FFと関連読取rootを研究用コピーへ明示してから実行する。本体にパスを書き戻さない。

必要入力はINPUT_PROVENANCE/SOURCE_REFERENCES/PROTECTIONとREFERENCE_ASSET_REVIEW_QUEUEにhashを記録。原本687/37/89、公式アイコン、旧source snapshotが必要。SOURCE_REFERENCESのGitHub固定commitから取得した照会原文はsource_referenceへ同梱。巨大原本を再梱包/改変していない。再取得は対象を選び、素材IDとhashを照合する。protectionのlocal pathはこの研究環境の参照で、他PCに存在する保証はない。

手順: assets.py→record_visual_reviews.py→assets_followup.py、fx_extended.py→fx_followup.py、parity_full.py、b_fixtures.py、audio_fixtures.py、finish_research.py、reports.py、seal.py。各領域のみ再生成してもよい。read-only原文のAST抽出は指定関数だけを研究processで実行し、製品アプリは起動しない。b_fixturesは研究sandboxの日本語journalのみ書く。録画/本体UI/ネットワーク/DNS/音量を操作しない。

ZIP内research_scriptsは保存した再現ソース。seal/publish/verify_remoteは配布担当の作業記録であり、自動で再pushしない。新環境で再実行する前に出力先・Gitブランチと原本read-onlyを確認する。画像レビュー所見は既存記録で、スクリプトを回すだけで目視承認が増えない。
''')
textfile('OPERATION_LOG_JA.md','''# 実作業と変更範囲
2026-10-26〜27。追加依頼の順序に従い現統合研究を先行。Work research/private Git indexとoutputsの新専用フォルダのみ更新。GitHub照会は固定PR原文と研究head/main metadataの読み取り。PR/Issueへの投稿なし。本体アプリ起動・LoL Replay接続・GPU実行なし。
Python/Pillow/NumPy/FFmpegのCPU描画、合成AAC/MP4、PNG比較、JSON/CSV/Markdown/静的HTML、ZIP/manifestを生成。source_referenceは読取用複製。Python bytecodeは研究work内だけ。元素材変更・削除・catalog承認書換えなし。DNS/proxy/VPN/adapter/firewall/Defender/hosts/service/ブラウザーsecurity/global volume変更、インストール、RTK自動hookなし。
音声は合成wavをファイル処理のみ、実再生なし。参考20動画の再生/追加downloadなし。公開する動画は研究生成のみ。全画面再生・同時動画再生なし。
音声初回のfps仮定による誤測定は無効化し、actual PTS/明示CFRで再実行。A4の浮動小数点差は開始だけでなく終了境界もあるため説明を修正。hash類似の誤検出も明記。
保護全1251fileと旧sealed ZIP6点はsealで実再hash。GitHubへの変更pathを研究prefix内へ限定し既存main/UI29/各開発branchへpushしない。保存/remote再取得結果はSAVE_RECEIPTに追記（ZIP外）。追加UI研究は未着手。
''')

save('NEXT_UI_RESEARCH_NOT_STARTED.json',{'task':'League Director vs Lolnam Editor UI徹底比較・2prototype','status':'NOT_RUN','japanese_status':'未着手','reason':'現在研究のGitHub保存・完了報告後に開始する別工程。今回の完了を偽装して先行しない','current_mixed_candidate':'7 main + 4 detail/material/frame','alternatives_preserved':[3,5,8],'completion_report_separate':True})
save('INPUT_PROVENANCE.json',{'research_parent':'991f107857ee789b90f9fb5c24d2224a7addb4df','prior_impl_rules_commit':'f3b6056b57ee468d04fd8124a05d331f225aa310','source_snapshot':'fb03e0390805125fc063f4599af6c2541a653abf','python':sys.version,'numpy':np.__version__,'Pillow':Image.__version__,'platform':platform.platform(),'ffmpeg':subprocess.run([FF,'-version'],capture_output=True).stdout.decode().splitlines()[0],'ffprobe_available':False,'new_reference_video_playback':0,'live_Replay':'NOT_RUN','source_audit':'SOURCE_REFERENCES.json','input_protection':'PROTECTION.json','installed_packages':[]})
for name in ['ASSET_REVIEW_QUEUE.json','IMPLEMENTATION_RULES.json','02_TIME_COORDINATE_CONTRACT_JA.md']:
 shutil.copyfile(R/'outputs/autocine_implementation_specs_20261026'/name,O/('REFERENCE_'+name))

print('reports saved',len(docs)+7)
