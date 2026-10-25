from pathlib import Path
import json, hashlib, shutil, csv, zipfile, html
R=Path(__file__).resolve().parents[2]; W=Path(__file__).resolve().parent
O=R/'outputs/autocine_quiet_pass_20261025'; O.mkdir(exist_ok=True)
def j(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def md(name,text): (O/name).write_text(text.strip()+'\n','utf-8')
notes={
'V09':('p6J1CkhYt3M','YASUO — WIND NEVER DIES',[
('0–17','レターボックスの人物・剣・雨のCG。リプレイ戦闘とは別の映像。'),
('19–89','bot/laneの俯瞰追従。30.79/33.59/53.28/64.48/74.51に通知。88.8付近はタワー通知でkill扱いしない。'),
('90–119','bot追走、93付近で人物が大きい構図、98–102ジャングル。101.67/110.06付近にkill通知。'),
('121–138','121灰色→124カラーDouble kill→126–134灰色→137ぼけ。死亡状態/観戦設定/編集グレードの原因は未確定。'),
('140–160','基地戦→mid追走、156.87付近通知、159付近暗転。')]),
'V23':('Uxw53vd0qYg','Last Lee Sin’s Montage',[
('0–74','人物CGとHUD付き戦闘を交互に挿入。12.16/38.56/47.99/72.47付近kill通知。50–61の身体・顔・蹴りCGはゲーム内カメラのみで再現できるとはいえない。'),
('75–129','追走→CG→基地戦→CG→川/ジャングル戦。101.60、127.59 Double kill。'),
('132–151','ジャングル追走から壁際へ。通常速度の補完でも146付近接触、148.96付近kill通知、150付近人物CGを確認。'),
('153–179','mid集団戦、160.68 Double /165.46 Triple、167イラスト→170 Thanks→174以降黒。')]),
'V22':('RvuvS7bDPlw','High Elo Yasuo Cinematic Montage',[
('0–43','俯瞰地形→青い装飾HUD枠のゲーム映像。21 kill/24 double/28 triple/36 quadra/38 penta、40–43人物アートと図形。'),
('45–110','左肖像列・大きいダメージ数値を伴うtop戦。66.83 quadra。mid 79 double/81 triple/86 quadra→88–96地形。102 triple/105 quadra/110暗い画面のpenta文字。'),
('112–174','基地/川/ジャングルの戦闘群。121/136 triple、140 quadra、153 double、158 triple/160 quadra/165 penta。167–172低い人物寄り→174地形俯瞰。'),
('177–231','blue buff集団戦193 penta。基地戦208 double/210 triple/212 quadra/215 penta。217以降ぼけた地形と終端告知。')]),
'V04':('eYopd5Ynq8o','Jarvan 2025 montage',[
('0–93','ロゴ/ぼけからHUD付きmid戦闘。低HP赤縁。46付近double、70–81川戦。56–74補完で68付近はfirst turret通知と識別。'),
('93–179','midタワー戦110通知→ジャングル追走、川、dragon pitからtop duel。'),
('180–269','dragon chase188/202通知。mid→jungle集団戦。251付近herald/towerの通知はkill扱いしない。'),
('271–373','tooltipが一部遮蔽。mid gank→集団戦302 double→top jungle/baron周辺→mid→jungle371 double。'),
('374–475','ぼけ転換からbot、midの複数kill、川追走。452/460通知。471 elder objectiveはkill扱いしない。'),
('477–564','jungle493/499 double→bot/jungle低HPの連続戦闘。549 fade、552以降end card。ゲームの低HP赤色を編集FXと断定しない。')]),
'V24':('s6mn5nydV8I','LOLNAM 18',[
('0–132','環境intro→地形俯瞰→top/mid/botの長い戦闘と追走。100付近は地形裏側の黒い形/白い隙間、102傾斜。HUDが隠れている。'),
('133–239','武器/顔、紫桃色の空を伴う寄り→mid/base広角。204.65付近地形裏。210–226補完で219付近青い縦光と倒れたモデル、明示kill通知なし。'),
('241–354','剣/人物背面/ぼけ→川duel→mid/jungle長い追走。265付近赤い縦光は候補。354.56黒は広告境界に隣接し意図的暗転と判定しない。'),
('356–428','広告を除外後356付近火球の黒背景寄り→mid wide→jungle pan→dragon集団戦→川追走→mid。'),
('430–493','傾いた地形→top/川duel→baron wide。470.78–493.39を通常速度でも確認。479–482接触、481.47赤橙の縦光、483–487残敵追走、488.45次mid戦。明示通知なし。'),
('489–510','mid duelと選手写真、503以降end card。kill候補Bと映像転換Cを明示kill確認Aへ昇格しない。')]),
'V05':('vvjTv5VJzQQ','OUTPLAYS WORLDWIDE Season 13',[
('0–74','HUDを抑え右kill feedと選手帯。jungle集団戦→top塔前→暖色top duel→mid戦。'),
('74–151','地面近い挿入→mid duel/追走→102–124集団戦で通知4–5段、複数kill後もwideを維持。126–150 mid、150ぼけ。'),
('152–221','基地戦→top gank/duelを長く追い、塔へ。219木/地面寄り→top。'),
('222–301','top追走233青い縦光。240–260 bot集団戦。259.80–277.88通常速度補完で261移動、264接触、273通知、274二段feed、277付近三段feed。282–299 mid/jungle→ぼけ。'),
('301–449','基地集団戦→jungle→短い寄り/レターボックス→339地面→川/mid duel→358–382複数人戦闘。385地形→387–420川/herald集団戦→jungle追走→top。'),
('449–527','top duelの457付近人物を大きく重ねた挿入→top戦へ。467以降別人物のtop戦、485/489/492付近feed増加後も残敵を映す。502以降mid→top塔前→mid→基地。'),
('528–600','基地戦535付近feed増加→538地形移動→top duel→mid gank→569top川境目→576–587集団戦でfeed最大4段以上。589以降Thanks/end card。')])}
notes['V15']=('Vv6ykcYJXrE','Skills of an expert you don’t want to miss — LOLNAM 24',[
('0–72','点滅注意の字幕、4付近人物寄り→橙の空と傾斜top戦。21–33mid duel、28付近グレーの挿入。35–51 top duelから地形裏/空へ移動、53以降baron集団戦。'),
('72–143','強い発光→77付近objective表示→79暗い地形→81–93bot duel→95mid戦、102付近強いぼけ、109黒背景に白い人物/橙の線→111通常色bot戦。123–130jungle duel→132川へ離れる→134midへ追従。'),
('143–216','mid長い追走→155–171mid集団戦→173基地へ移動→179–205mid基地入口の長い戦闘→207川/ジャングルのduel。'),
('216–287','mid追走→239基地入口集団戦。246.6背景黒で人物群のみ→248.8強い発光→251–253明るい地形。255川/baron周辺戦闘と追走、280botへ。'),
('286–328','botから290top duelへ。314付近赤い縦光、319塔前、324紫の渦を近く映す。326黒は広告境界に隣接し保留。観測ツール中断で消失した記録は285.96から再観測して補い、未保存の画像を根拠に使わない。'),
('328–475','328人物寄り→330–363 mid/川の多人数戦、365川の挿入→368–439川とmidの集団戦/追走。441地形移動→444–467top duel、470暗転→472人物寄り→475川。明示kill feedは確認できず縦光をkill確定へ昇格しない。'),
('475–547','選手ShowMakerの写真帯を伴うbot duel→498mid duel→521top duel→538top塔前の多人数戦。選手帯はkill通知と区別。'),('547–600','top塔前戦→555傾斜/ぼけ転換→top duel→562川からbot duelへ。576戦闘末尾、579–590会員謝辞、593以降Thanks/end card。')])
logs=[]; videos=[]
(O/'timing').mkdir(exist_ok=True)
for f in sorted((W/'private_screens').glob('*.json')):
 d=json.loads(f.read_text('utf-8')); valid=[x for x in d['records'] if not x.get('excluded')]
 if not valid:continue
 assert all(x['pre']['muted'] and not x['pre']['fullscreen'] and not x['pre']['ad'] for x in valid)
 shutil.copyfile(f,O/'timing'/f.name)
 logs.append({'label':f.stem,'samples':len(valid),'first':valid[0]['pre']['time'],'last':valid[-1]['post']['time'],'duration':valid[0]['pre']['duration'],'rates':sorted(set(x['pre']['rate'] for x in valid)),'excluded':sum(bool(x.get('excluded')) for x in d['records']),'sha256':sha(f)})
for vid,(yt,title,observations) in notes.items():
 ls=[x for x in logs if x['label'].startswith(vid+'_')]; pts=[]
 for l in ls:
  d=json.loads((O/'timing'/(l['label']+'.json')).read_text('utf-8'))
  pts += [r['pre']['time'] for r in d['records'] if not r.get('excluded')]
 pts.sort(); gaps=[{'from':a,'to':b,'seconds':b-a} for a,b in zip(pts,pts[1:]) if b-a>5]
 videos.append({'id':vid,'youtube_id':yt,'url':'https://www.youtube.com/watch?v='+yt,'title':title,'scope':'near-full coarse structure survey; intermittent screenshots during continuous muted playback; not frame-complete','first':min(x['first'] for x in ls),'last':max(x['last'] for x in ls),'duration':ls[0]['duration'],'samples':sum(x['samples'] for x in ls),'remaining_sample_gaps_gt5s':gaps,'audio_heard':False,'exact_fov_or_speed_measured':False,'observations':[{'seconds_approx':t,'observed':n} for t,n in observations]})
j(O/'VIDEO_OBSERVATIONS.json',videos);j(O/'TIMING_SUMMARY.json',logs)
md('README_JA.md','''# AutoCine V4・ミュート構成調査追補
観測継続日：2026-10-25〜26（JST）。この追補は研究継続の証拠保存であり、総合研究完了報告ではない。
前回追補の全体構成観測4作品に、V09/V23/V22/V04/V24/V05/V15の7作品を追加し累計11/20作品。20作品全件は区間観測済みだが、残る9作品の全体構成調査は未完了。2件以上の明示kill確認は従前13/20から変更しない。音声観測0。
通常1x/2x・ミュート・非全画面で1本ずつ連続再生し、時刻付き画像を間欠観測した。全フレーム目視、原動画速度倍率/FOV/音声同期の解析とは異なる。
原動画の連続画像はローカル研究用に留め、公開成果物には時刻状態ログと独自の観察文を収録する。元のV4/追補ZIPを変更しない。
資料：01_VIDEO_STRUCTURE_JA.md / 02_EVIDENCE_TO_RECIPES_JA.md / 03_COMPARISON_TEST_SPEC_JA.md / 04_OPERATION_LOG_JA.md / STATUS.json / VIDEO_OBSERVATIONS.json / TIMING_SUMMARY.json / timing。
''')
text=['# 7作品の追加実映像観測','秒数はプレイヤー実時刻の概数。観測事実と実装案は別資料に分離する。']
for v in videos:
 text += [f"\n## {v['id']} {v['title']}",v['url'],f"観測サンプル {v['first']:.3f}–{v['last']:.3f} / {v['duration']:.3f} 秒、{v['samples']}枚。音声なし。"]
 text += [f"- {x['seconds_approx']}秒：{x['observed']}" for x in v['observations']]
 text += [f"5秒超の残存サンプル間隔：{len(v['remaining_sample_gaps_gt5s'])}。詳細はJSON。間隔は映像を停止した時間ではなく、記録画像同士の差。"]
md('01_VIDEO_STRUCTURE_JA.md','\n'.join(text))
md('02_EVIDENCE_TO_RECIPES_JA.md','''# 映像根拠と6レシピの更新提案（未採用）
|レシピ|今回の観測根拠|既存で利用できる要素|新規実装/留保|
|---|---|---|---|
|Cinematic|V23 CGと戦闘の交互挿入、V22 167–174低い寄り→俯瞰|旧カメラ、clip、cut、カラーで一部近似|CGポーズ/人物抽出/任意モーションをリプレイカメラで再現できるとはいえない。外部素材トラックは新規|
|Impact|V05 457付近の人物を大きく重ねた挿入、V22 kill列と装飾|既存Flash/blur/キル素材/強度|人物レイヤー合成は新規。Flashの見た目を原動画と数値一致したとはいわない。CPU causal候補は独立研究のまま|
|Elegant|V09 121–138グレー/カラーの交替、V24 133武器/人物寄り|既存カラー/ビネット/控えめFX|灰色の原因未確定。死亡状態と意図的モノクロを分離。人物/背景別グレード・深度ぼけは新規|
|Competitive|V05 102–124/259–278/485–499、V24 479–488の残敵追走|旧10カメラ/手動/広角/clip保持|次engage判定・複数対象包含・最後のkillの確定はイベント連携を要する新規ルール|
|Montage|V23戦闘→CG→戦闘、V05短い地面挿入と長い集団戦の混在|既存clip選択/cut/カラー/FX|音楽beat同期未観測。固定秒数で一律に人物寄りへ切り替える仕様にしない|
|Low-load Cinema|V04長いHUD付き俯瞰追走、V05戦闘をwideで継続|既存カメラ、不要FXを切る構成|低負荷の実機計測結果ではない。高価なFXの自動削減/予算管理は新規|

BLUE/REDの通知色とカメラ安全性を結び付けない。全レシピで手動優先、旧IDとprocessing revisionを保持、未承認素材は確認用と表示、候補を正式既定にしない。V24の地形裏露出は原動画での観測でありAutoCineの不具合再現ではない。
''')
md('03_COMPARISON_TEST_SPEC_JA.md','''# 将来のAutoCine出力比較手順（未実行）
## 撮影入力
同じReplayのイベントID・対象participant・team・gameTimeを固定。kill前4秒〜最後のkill後2秒を最低範囲とし、次のengageがある場合はその開始まで残す。秒数は試験条件で正式既定値ではない。BLUE/REDそれぞれ、手動/旧camera/fixed-auto/new candidateを同じ条件で収録する。参照YouTubeは別試合のためピクセル一致を求めない。
## 追加した比較ケース
1. Q-WIDE：V05 259–278相当。複数kill後に残敵がいる入力。旧wideをbaselineに、kill直後の寄りで残敵/攻撃者が画面外に出ないか全フレーム点検。
2. Q-AFTER：V22 155–174相当。最後のkill後に低い寄り、次のengage前に戻る。group誤り/対象死亡/遮蔽で安全wideへ戻す。正確な閾値はユーザー実機比較まで未決。
3. Q-EDGE：V24 100/204/430相当の低角度/傾斜。地形裏・空白・人物欠落率を時間付きで保存。参照映像の演出を製品不具合として自動ラベル化しない。
4. Q-NOTIFY：V04 68 turret/471 elder、V05 273 feed、V24 481縦光を分離。縦光だけでkill確定にしない。Replayイベントで正解を確定。
5. Q-GRAY：V09 121–138。死亡グレー/編集モノクロ/正常カラーを別入力にし、警告をユーザー確認付き候補として記録。
6. Q-OCCLUDE：V22左肖像列、V05右4段feedに似た研究条件。AutoCine最大3段の素材表示とHUD/名前/HPの衝突を各解像度/テーマで測る。原動画の4段を製品要件へ自動追加しない。
## 保存と判定
入力Replayハッシュ、build SHA、設定JSON、ShotPlan、カメラ座標/FOV/TargetLock、イベント時刻、映像PTS、音声PTS、frame drop、encode経路を保存。比較は連続動画+contact sheet+評価票。各被写体可視率/切れ/地形外露出/HUD遮蔽/次engageへの食込み/AV差を記録。許容値は暫定と明示し、無条件PASSを作らない。
既存projectの再出力が変わらないこと、テーマ切替で再生/選択状態が維持されること、旧37/原本89/候補652のhashと承認状態が維持されることも別項目で確認。人工映像テストやNVENC成功を実LoL/GPU FX合格に昇格しない。
''')
md('04_OPERATION_LOG_JA.md','''# 操作・変更記録
## 今後も適用するユーザールール
Windows DNS/プロキシ/アダプター/ファイアウォール/VPN/Defender/hosts/サービス、ブラウザーのネットワーク・セキュリティ設定は変更しない。必要になれば理由・影響を説明し明示許可を待つ。異常が実際に観測された場合は停止・報告。動画はミュート、非全画面、1本ずつ、bulk downloadなし。Braveはインストール/設定変更しない。
## 実施操作
- CIM経由のGet-NetAdapter/Get-NetConnectionProfileを読み取り実行したが権限拒否。ネットワーク断の証拠ではない。昇格や設定変更で回避していない。ブラウザーでは動画再生ができた。原因未確定の以前の通信不具合との因果関係は判断しない。
- 既存Braveのユーザー動画は操作せず、制御可能なアプリ内ブラウザーの研究用1タブを使用。非全画面・mute=trueを状態記録で確認。
- 一時的viewportを1280×900へ。これは描画寸法で、network/security設定変更ではない。終了時resetする。
- 通常UIから無料の1x/2x再生。3xはPremium案内が出たため未購入/未利用。広告はmutedのまま可能な範囲でskip。V24 midrollは観測対象から除外。
- keyboard seekが意図した位置にならなかったV24_gap_470は実際81–106秒。ラベルだけで470秒補完に算入せず、t=470sの通常URLで再確認した。実測時刻が正。
- V04/V23/V24/V05の5秒超サンプル間隔を通常速度または明示した2xの補完観測で埋めた。広告境界のV24 354.56黒とV15 326秒付近の黒は広告境界に隣接するため保留。V15観測ツールのdeadline中断後にmute=trueを確認して一時停止、285.96秒から再観測した。これはネットワーク異常が確認されたという意味ではない。以降の観測呼出はfinallyで一時停止も確認。
## 実際の変更範囲
ローカル：work/autocine_quiet_pass_20261025/ の独立観測/集計スクリプト、private_screensの研究用画像とJSON、outputs/autocine_quiet_pass_20261025/ の資料とZIPのみ。公開保存時は研究専用ブランチの新規フォルダのみ。
Windows/network/security設定変更0、AutoCine本体変更0、UI29変更0、素材正式承認変更0。RTKフック導入0。Work全体クレジット削減は測定/主張しない。
保存前の終了状態確認：研究用動画はpaused=true、muted=true、fullscreen=false。末尾の広告表示も停止した状態。一時的viewportはreset実行済み。Windowsの表示設定は変更していない。
既存V4と前回追補のsealed ZIPは変更しない。追加UI改善の分析・画像制作は現研究を区切った後の依頼として保留し、採用UIを勝手に決めない。
''')
prior=['V02','V06','V08','V21']; new=list(notes); pending=['V01','V03','V07','V11','V12','V13','V16','V20','V25']
j(O/'STATUS.json',{'scope':'research in progress; checkpoint is not project completion','prior_near_full_structure':prior,'new_near_full_structure':new,'cumulative_structure_count':11,'target':20,'pending_near_full_structure':pending,'explicit_two_kill_notifications':13,'unresolved_explicit_two_kill':['V01','V02','V03','V08','V15','V16','V24'],'audio_heard_count':0,'product_T01_T14_full_pass':0,'material_formal_approval_changed':False,'ui_selected':False,'additional_ui_research_started':False,'work_can_continue':True,'requirements_blocked':['live Replay/TargetLock/BLUE-RED/hardware/LoL audio approval need actual Windows LoL evidence','19 reference-source constraints unchanged'],'observation_timestamps':'individual player pre/post times in timing/*.json; not FOV or source speed measurements'})
md('CHATGPT_COPY_REPORT.txt','''LoL AutoCine V4の研究を継続しました。総合研究は未完了です。
今回V09/V23/V22/V04/V24/V05/V15の7作品を末尾まで構成観測し、従前4作品と合わせ11/20作品になりました。間欠画像を使ったミュート1x/2x再生の構成調査で、全フレーム精査や音声同期解析ではありません。明示kill通知2件以上は従前13/20、音声観測0。残る全体構成調査9作品はSTATUS.jsonへ明記しました。
新しい根拠：連続kill後もwideを維持して残敵を追う構成、CG/地面寄りの短い挿入と長い戦闘の使い分け、タワー/elder通知とkillの区別、地形裏露出・灰色・広告境界の黒の誤判定防止。6レシピと比較試験6ケースへ対応付けました。新規実装案は未採用です。
Windows/network/security設定は変更していません。CIM読み取りは権限拒否で、ネットワーク障害の証拠ではありません。本体・UI29・素材正式承認は変更なし。動画は非全画面・ミュート・1本ずつ、bulk downloadなし。
追加UI/ポップアップ改善研究は、現研究を区切ってからという指示に従い未着手です。実Replay/BLUE-RED/TargetLock/LoL音声等の製品全体PASSは依然0/14。資料保存だけで完了扱いにしません。
''')
shutil.copyfile(W/'quiet_observer.mjs',O/'quiet_observer.mjs')
shutil.copyfile(Path(__file__),O/'build_checkpoint.py')
# Sealed previous packages are rehashed, never rebuilt.
sealed=[]
for name,expected in [('AutoCine_Research_V4_20261025.zip','1ee3a7315713915c788ef5e55cdeb24e9fb914b2deb82439c0b2406736ad4543'),('AutoCine_V4_Addendum_20261025.zip','1ef56cc14d641b2d2d4da1282608c093c1db734e4d2127d393881bd4ddb2a31c')]:
 actual=sha(R/'outputs'/name);assert actual==expected;sealed.append({'file':name,'sha256':actual,'unchanged':True})
j(O/'SEALED_PREVIOUS_PACKAGES.json',sealed)
# Protected inputs: hash original records, never rewrite them.
old=R/'work/autocine_integrated_research_20261022';v3=R/'outputs/autocine_final_research_v3_20261024'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
groups=[('source',old/'source_readonly',read(old/'source_hashes.json')['files'],'sha256'),('work_asset',old/'asset_samples',read(v3/'ASSET_FULL_QA_V2.json')['items'],'actual_sha256'),('original',Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository'),read(v3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files'],'sha256'),('legacy37',old/'legacy_asset_cache_v3',read(v3/'LEGACY_BADGE_PROTECTION_V3.json')['items'],'sha256')]
checks=[]
for group,root,items,key in groups:
 for x in items: checks.append({'group':group,'path':x['path'],'match':sha(root/x['path'])==x[key]})
assert len(checks)==1251 and all(x['match'] for x in checks)
j(O/'PROTECTION.json',{'count':len(checks),'changed':0,'checks':checks})
parts=['<!doctype html><html lang="ja"><meta charset="utf-8"><title>AutoCine 動画構成調査追補</title><style>body{max-width:1120px;margin:40px auto;padding:24px;background:#f4f5f7;color:#202b39;font:17px/1.8 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#174c9d}section{background:white;padding:24px;margin:20px 0;border-radius:12px}</style><h1>AutoCine V4・動画構成調査追補</h1><p>累計11/20作品。研究継続中。音声未観測・正式採用なし。</p>']
for name in ['README_JA.md','01_VIDEO_STRUCTURE_JA.md','02_EVIDENCE_TO_RECIPES_JA.md','03_COMPARISON_TEST_SPEC_JA.md','04_OPERATION_LOG_JA.md','CHATGPT_COPY_REPORT.txt']:
 parts.append('<section><a href="'+name+'">'+name+'</a><pre>'+html.escape((O/name).read_text('utf-8'))+'</pre></section>')
parts.append('<h2>データ</h2>'+''.join('<p><a href="'+p.name+'">'+p.name+'</a></p>' for p in sorted(O.glob('*.json')))+'<p>原動画スクリーンショットは公開物に含めない。</p></html>')
md('index.html',''.join(parts))
files=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['CONTENT_MANIFEST.json','SAVE_RECEIPT.json']]
j(O/'CONTENT_MANIFEST.json',{'files':files})
zpath=R/'outputs/AutoCine_Quiet_Video_Research_20261026.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file() and p.name!='SAVE_RECEIPT.json':z.write(p,'AutoCine_Quiet_Research/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None; members=len(z.namelist())
j(W/'package_result.json',{'zip':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath),'members':members,'public_files':len(files)+1})
print(json.dumps({'videos':len(videos),'logs':len(logs),'samples':sum(x['samples'] for x in logs),'protected':len(checks),'zip_sha256':sha(zpath),'zip_bytes':zpath.stat().st_size,'public_files':len(files)+1}))

