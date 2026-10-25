from pathlib import Path
import json,hashlib,shutil,csv,zipfile,html,statistics
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_v4_addendum_20261025';O=R/'outputs/autocine_v4_addendum_20261025';V=R/'outputs/autocine_research_v4_20261025';OLD=R/'work/autocine_integrated_research_20261022';V3=R/'outputs/autocine_final_research_v3_20261024'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(name,data):(O/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(O/'video_timing').mkdir(exist_ok=True);(O/'research_scripts').mkdir(exist_ok=True)
timing=[]
for p in sorted((W/'video_evidence').glob('*.json')):
 d=load(p); valid=[x for x in d['screenshots'] if 'time' in x]
 if p.stem=='V02_add_full_11':valid=valid[:-1] # screenshot crosses into post-roll ad; reject non-atomic terminal sample
 times=[x['time'] for x in valid]; gaps=[b-a for a,b in zip(times,times[1:])]
 timing.append({'id':p.stem,'first_sample':times[0],'last_valid_sample':times[-1],'valid_samples':len(times),'max_sample_gap_seconds':max(gaps,default=0),'duration':d['initial']['d'],'audio_heard':False,'terminal_sample_excluded':p.stem=='V02_add_full_11','scope':'continuous playback, intermittently observed screenshots; not frame-complete'})
 shutil.copy2(p,O/'video_timing'/p.name)
save('VIDEO_COVERAGE_ADDENDUM.json',{'segments':timing,'new_works_near_complete':['V02'],'total_near_complete_sampled':4,'two_explicit_notification_works':13,'unresolved_notification_works':['V01','V02','V03','V08','V15','V16','V24'],'V02_valid_first':min(x['first_sample'] for x in timing if x['id'].startswith('V02')),'V02_valid_last':max(x['last_valid_sample'] for x in timing if x['id'].startswith('V02')),'V02_observation_count':sum(x['valid_samples'] for x in timing if x['id'].startswith('V02')),'terminal_race':'last V02 sample queries main video at 500.837531s but screenshot shows a post-roll ad; excluded. Next state explicitly reports ad=true. Endpoint ad is not source content.'})
observations=[
 [0,14,'傾いた地形からmid対面へ。約5秒からプレイヤー紹介帯。8.96秒の接触後、12.52秒では片側が倒れたように見える。','通知なし・キル候補B','紹介帯はキル通知ではない。画面から勝者/時刻を確定しない。'],
 [14,43,'mid複数人戦を俯瞰追従。21.42秒に青い縦光、34.05秒に赤い縦光、39.40秒に橙の縦光。41.22秒は倒れたモデルが残る。','通知なし・複数キル候補B','複数人物を広く残す構図。ビームの色からkill/victim/チームを確定しない。白い多角形は元映像にあるが由来未確定。'],
 [44,65,'mid対面から川側へ追走、両者の距離に合わせてパン。接触中は上から両者を残す。','観測','追走と戦闘終端のcutawayを分離する。'],
 [66,72,'66.45秒は黒背景に人物、68.21秒は橙の強い発光、69.98秒は地形の大きなぼけ、71.75秒は別の集団戦。','演出観測','人物切り出し・背景置換の実装方法は推測。意図的暗転候補で、AutoCineの黒画面不具合とはしない。'],
 [72,104,'midからジャングルへ複数人物を追う。91.35秒付近の青い縦光、98〜102秒は残った対面を追う。','通知なし・キル候補B','戦闘が続く限りワイドを維持するレシピ候補。'],
 [104,119,'ジャングル通路の対面。111〜116秒の接触後、118.42秒にカメラが大きく傾き地形が外へ流れる。','観測','終端カメラの地形外露出をQA候補へ。正確なFOV/速度は未測定。'],
 [120,135,'midから基地側の複数人戦へ。カメラは戦闘の広がりを追う。','観測','中央1人物だけの追従では周辺人物を落とし得る。'],
 [135,151,'topの戦闘から川へ追走。150.47秒は川・地形を大きく傾けたショット。','観測','戦闘終了検出とカメラ安全判定は別に扱う。'],
 [152,182,'midのUzi紹介帯付き集団戦。複数人物が倒れたように見えても、残敵を画面に残して戦闘を続ける。182.48秒で地形外が大きく映る。','通知なし・キル候補B','最後のkill直後と決めつけず、次のengage/可視性のガードが必要。'],
 [184,208,'top対面からタワー方向へ追走。202〜205秒に接触・片側消失後、207.75秒で空・地形端を見せる。','通知なし・キル候補B','キル後人物ショットの前にマップ境界チェックを提案。'],
 [209,234,'topと川の往復・追走。232.59秒は青い縦光と倒れたモデル。234.36秒で黒。','通知なし・キル候補B','暗転は前後の連続性から演出候補として記録。'],
 [236,259,'黒背景の青緑人物ショットから基地戦へ。248.92秒は赤い縦光、256〜258秒は倒れたような人物が残る。','通知なし・キル候補B','装備/人物を別に扱うショットは新規機能領域。'],
 [259,304,'暗い青緑のmid対面・タワー追走。終端で別対面へ切り替える。','観測','彩度/明度/ビネットの類似表現は既存処理候補。使用LUTは特定不可。'],
 [304,349,'top対面の長い追走の後mid複数人戦、344.39秒に青い縦光。','通知なし・キル候補B','長い追走を急な人物closeで中断しない案。'],
 [349,374,'botの対面から4人程度の戦闘。365.78秒は倒れたモデルがあるが、369秒台まで残敵を追う。','通知なし・キル候補B','単発の消失でグループを閉じない。'],
 [374,399,'明るいmid複数人戦。392.16秒に青い縦光、397.93秒にも青い縦光と倒れたモデル。399.72秒で地形パンへ。','通知なし・キル候補B','約5.8秒離れた2候補だけを根拠にgroup閾値を正式採用しない。'],
 [400,418,'川からmidへ対面を追走し、壁際へ。残った対面を広く残す。','観測','壁で人物を隠すカメラ候補は可視性未確認なら採用しない。'],
 [419,435,'基地周辺の多数人物戦。広い画面で戦闘を追う。','観測','密集戦で強い全画面FXを抑える案。'],
 [435,457,'明るい黄系のmid対面。455.65秒で片側の倒れたようなモデル、457.45秒で基地の俯瞰に切り替わる。','通知なし・キル候補B','カラーの全体構成は観測、数値/効果チェーンは推測。'],
 [459,493,'基地の高い俯瞰から集団戦、487.99秒で泉周辺の俯瞰、移動する複数人物。','観測','全体終端の確定はkill通知を根拠にしていない。'],
 [493,499.02,'黒背景の終了カード、後半にYouTube推薦サムネイルが重なる。','エンドカード観測','500.84秒ラベルのスクリーンショットは後付け広告へ切り替わっており、作品の画として除外。']]
save('VIDEO_OBSERVATIONS_ADDENDUM.json',{'V01':{'url':'https://www.youtube.com/watch?v=NolHvXjZA4A','range':[326.33103,370.523681],'observed':'midからジャングル追走、331〜358秒は低体力の人物と追手を広く追う。345.87秒に赤い縦光、349.5秒に金の像、351〜356秒の再戦後358秒に倒れたモデル。359.99秒に別midシーンへ。通知は確認できない。','inference':'金の像・縦光・人物消失だけではkillを確定しない。広い追走と終端cutの設計参考。','two_explicit_notifications':False},'V02':{'url':'https://www.youtube.com/watch?v=d-r2kgeFfus','segments':[dict(start=a,end=b,observed=c,evidence_tier=d,inference_or_limit=e) for a,b,c,d,e in observations],'two_explicit_notifications':False,'scope':'near-complete sampled visual observation; audio not heard; notification-confirmed count remains 13/20'}})
av=load(O/'AV_CONTROLS_ADDENDUM.json'); avrows=[]
for r in av['cases']:
 t=r['thresholds'][2];avrows.append([r['fps'],r['source_onset'],r['source_marker_duration'],r['mode'],f"{r['video_marker_pts']:.3f}",f"{t['audio_pts']:.6f}",f"{t['offset_ms']:.3f}"])
def table(headers,rows):return '| '+' | '.join(map(str,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n'
video_text='# V4追補：映像の追加観測\n\n元20作品を保持。V01の別区間1本、V02の冒頭から終端まで11区間を追加。明確なキル通知2件の作品数は13/20のまま。ほぼ全体の画面観測はV06/V08/V21/V02の4/20、残16作品は部分区間。音声聴取0作品。\n\nV02: https://www.youtube.com/watch?v=d-r2kgeFfus\n\n'+table(['秒付近','実際に見た内容','区分','推測・留保'],[[f'{a}–{b}',c,d,e] for a,b,c,d,e in observations])+'\n1.6秒の待機を挟む画面観測で、実測間隔には処理時間が加算される。全フレーム、正確なcut時刻、速度倍率、FOVの測定ではない。観測時刻とスクリーンショットは別取得のため、終端広告への切り替わりを除外。個人用の確認スクリーンショットはwork領域に残し、元動画の連続画像は公開ZIP/GitHubへ再配布しない。\n\nV01: https://www.youtube.com/watch?v=NolHvXjZA4A&t=326s\n\n326.33–370.52秒を追加。追走・復活/無敵のような金の像・再戦・倒れたモデル・次のmidへのcutを確認。通知のない画だけから復活スキル名やキル数を確定しない。\n'
(O/'01_VIDEO_ADDENDUM_JA.md').write_text(video_text,'utf-8')
av_text='# V4追補：AV同期の対照検証\n\n32出力を生成・デコードし、4音声閾値で128測定。2fps条件×2開始位相×2パルス長×3経路=24に、パルス長0.1秒で映像時刻制御2種類×2fps×2位相=8を追加。30/60fps、2倍速、PCM/AAC、atempo、音程が変わるresample診断対照を含む。\n\nV4の30fps/2倍速で約−58.8msを再現。0.5秒マーカー・PCMでは映像0.300秒、音声0.241209秒。映像を明示fpsフィルターまたはpassthroughへ切り替えた人工対照では映像0.233秒、音声は同じ0.241209秒、差は+8.209ms。0.517秒開始では−25.646ms。音声だけの一定遅延を足す修正は、この測定からは正当化できない。\n\n同一audioに対する出力映像のタイムスタンプ制御の寄与を示す対照。passthroughではPTS量子化やVFRになり得るため、製品の置き換え候補を承認した試験ではない。resampleは音程を変える診断用で、BGM/LoL音声の代替方式にしない。\n\n'+table(['FPS','開始','長さ','経路','映像PTS','音声PTS','差ms (閾値0.1)'],avrows)+'\n## 製品との接続に関する留保\n\n固定監査ソース fb03e0390805125fc063f4599af6c2541a653abf の全Pythonを原文検索。core/recorder.py:161–162は速度正規化にsetptsと-anを使う。core/effects.py:678–679は出力-rを指定する。atempoは当該ソースのPython内に見つからない。今回の合成AVのsetpts+atempoグラフを、現在のLoLゲーム音声経路そのものとして扱わない。実際の製品ジョブ・速度・録画音声で同じ測定をする必要がある。\n\nデコード成功32/32、AV同期製品合格0。人工出力、フルコマンド、SHA256、PTSと128測定をJSON/CSVに保存。音声は波形閾値で測定し、主観聴取は実施していない。\n'
(O/'02_AV_CONTROLS_JA.md').write_text(av_text,'utf-8')
recipe=[['Cinematic','V02 66–72/236–239：人物を黒背景で強調し戦闘へ戻る','既存の映像全体カラー・Flash・cutで一部近似','人物/武器アンカー、深度、背景置換は新規。黒背景を自動で不具合扱いしない'],['Impact','V02 68秒の強い橙発光、69秒のぼけから切替','Flashと既存blurで類似方向','当該一瞬の速度/強度は未測定。旧Flash互換性とprocessing revisionを維持'],['Elegant','V02 236秒の青緑人物ショットと暗い基地色','既存のカラー・ビネットを弱く利用する案','肌/人物と背景の独立グレードは新規'],['Competitive','V02 152–180/349–373：残敵を映したまま追走','旧10カメラ、手動、固定自動を保持','戦闘継続/次engage判定は新規提案。3秒groupを正式既定にしない'],['Montage','V02 冒頭から戦闘→短い人物ショット→次の戦闘という単位を反復','既存clip選択/カラー/FX/cutの組み合わせ','beat同期は音声未測定。紹介帯をkill通知と誤認しない'],['Low-load Cinema','V01 331–358とV02の多数区間：俯瞰追従が演出の大半を担う','既存カメラと控えめなカラー、不要FXを切る案','低負荷を実LoLで測定した結果ではない']]
(O/'03_RECIPE_EVIDENCE_AND_QA_JA.md').write_text('# 6レシピへの追加根拠とQA留保\n\n'+table(['レシピ','追加映像根拠','既存機能への接続案','新規/留保'],recipe)+'\n## キル確定と映像演出の観測を分離\n\nA：明示kill通知/KDA等で確認。B：HP低下・縦光・消失/倒れたモデルの複合でkill候補。C：見栄えだけの人物ショット/転換。B/CをAに昇格しない。候補を再現する撮影時刻はReplayイベントログで確定させる。原動画にHUDがない場合は「通知未確認」と「映像未確認」を区別する。\n\nV02 118/150/182/207秒には地形外露出/傾きがある。角度のみの異常判定は演出の誤検知になる。対象可視率、地形外面積、遮蔽、続く戦闘、ユーザーの手動設定と併せたQAが必要。いずれも認識器の精度検証ではない。\n\n将来比較：同じリプレイイベントの前4秒〜最後のkill後2秒を収録し、全員を含むwideの可視時間、人物closeが次engageへ食い込む時間、HUD/FX遮蔽面積、映像/音声marker PTSを保存。原動画のゲーム時刻が分からないため同一状況の数値一致は求めず、表現の相違を人が評価する。閾値は採用前の検討値とし、旧camera/FX IDと旧projectの見た目を変えない。\n','utf-8')
roots={'source':OLD/'source_readonly','work_asset':OLD/'asset_samples','original':Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository'),'legacy37':OLD/'legacy_asset_cache_v3'}
maps={'source':{x['path']:x['sha256'] for x in load(OLD/'source_hashes.json')['files']},'work_asset':{x['path']:x['actual_sha256'] for x in load(V3/'ASSET_FULL_QA_V2.json')['items']},'original':{x['path']:x['sha256'] for x in load(V3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files']},'legacy37':{x['path']:x['sha256'] for x in load(V3/'LEGACY_BADGE_PROTECTION_V3.json')['items']}}
checks=[]
for x in load(V/'PROTECTION_RECHECK_V4.json')['checks']:
 p=roots[x['group']]/x['path'];checks.append({'group':x['group'],'path':x['path'],'same':sha(p)==maps[x['group']][x['path']]})
assert all(x['same'] for x in checks)
sealed=R/'outputs/AutoCine_Research_V4_20261025.zip'; assert sha(sealed)=='1ee3a7315713915c788ef5e55cdeb24e9fb914b2deb82439c0b2406736ad4543'
save('PROTECTION_ADDENDUM.json',{'rehash_count':len(checks),'changes':[],'checks':checks,'sealed_V4_zip_sha256':sha(sealed),'UI_selection':'not_selected','product_modifications':0,'formal_approval_changes':0})
copy='''LoL AutoCine V4追補（2026-10-25）
追加実行：V01の別区間を観測。V02約8分21秒の冒頭〜終了カードを11分割で画面観測。
ほぼ全体を間欠画面観測した作品は3→4/20。明確な2キル通知は13/20のまま。残16作品は部分区間、通知未確定7作品、音声聴取0作品。
AVは独立人工出力32本・音声閾値128測定。30fps/2倍速の約−59msを再現し、映像出力時刻制御で差が変化することを確認。現在の製品音声の不具合確定・修正採用ではない。
6レシピに追加映像根拠を対応付け、kill通知/死亡候補/演出だけの3区分を整理。
保護対象1,251ファイルを再ハッシュし変更0。V4の既存ZIPもSHA256一致。本体/UI29/素材/正式承認は変更0。
未完了：動画16作品の全体観測、音声、651件の肖像枠、原本制約19件、実LoL/HUD/TargetLock、GPU FX、製品T01–T14。ユーザーのUI選定・素材承認・新規機能採用は未決定。
この追補は研究の追加分であり、総合研究全完了の報告ではありません。
保存先：研究ブランチ work/autocine-integrated-research-20261022 内 v4_addendum_20261025。
コミットSHAは別添SAVE_RECEIPT_ADDENDUM.jsonを参照。
'''
(O/'CHATGPT_COPY_REPORT_ADDENDUM.txt').write_text(copy,'utf-8')
(O/'README.md').write_text('# LoL AutoCine V4追補\n\nV4確定成果物を変更せず、追加の実映像観測とAV人工対照検証を収録。アプリ変更なし。\n\n- 01_VIDEO_ADDENDUM_JA.md：V01追加・V02ほぼ全体\n- 02_AV_CONTROLS_JA.md：32出力/128閾値測定と適用限界\n- 03_RECIPE_EVIDENCE_AND_QA_JA.md：6レシピと安全判定の追加根拠\n- VIDEO_*：観測・時刻のJSON\n- AV_CONTROLS_*：測定・コマンド・ハッシュ\n- PROTECTION_ADDENDUM.json：保護対象1,251件の変更0\n- CHATGPT_COPY_REPORT_ADDENDUM.txt：コピペ報告\n- index.html：日本語閲覧\n\n本体・UI29・素材承認を変更しない。V4 ZIPを上書きしない。MKVは独立人工試験であり、実LoL音声の合格ではない。\n','utf-8')
for p in W.glob('*.py'):shutil.copy2(p,O/'research_scripts'/p.name)
shutil.copy2(W/'observer.mjs',O/'research_scripts'/'observer.mjs')
def render_md(text):
 lines=text.splitlines();out=[];i=0
 while i<len(lines):
  line=lines[i]
  if line.startswith('| '):
   block=[]
   while i<len(lines) and lines[i].startswith('| '):block.append(lines[i]);i+=1
   rows=[[html.escape(c.strip()) for c in a.strip('|').split('|')] for a in block]
   out.append('<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+c+'</th>' for c in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in r)+'</tr>' for r in rows[2:])+'</tbody></table></div>');continue
  if line.startswith('# '):out.append('<h3>'+html.escape(line[2:])+'</h3>')
  elif line.startswith('## '):out.append('<h3>'+html.escape(line[3:])+'</h3>')
  elif line:out.append('<p>'+html.escape(line)+'</p>')
  i+=1
 return ''.join(out)
sections=''
for name in ['README.md','01_VIDEO_ADDENDUM_JA.md','02_AV_CONTROLS_JA.md','03_RECIPE_EVIDENCE_AND_QA_JA.md','CHATGPT_COPY_REPORT_ADDENDUM.txt']:
 sections+=f'<section><h2>{html.escape(name)}</h2>'+render_md((O/name).read_text('utf-8'))+'</section>'
links=''.join(f'<li><a href="{p.name}">{p.name}</a></li>' for p in sorted(O.glob('*.mkv')))
(O/'index.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AutoCine V4追補</title><style>body{font:17px/1.8 "Yu Gothic UI",sans-serif;margin:36px auto;padding:0 24px;max-width:1200px;background:#f3f5f8;color:#1d2b3c}section{background:#fff;border:1px solid #bac6d4;border-radius:12px;padding:24px;margin:24px 0;min-width:0}p,h2,li{overflow-wrap:anywhere}a{color:#195db4}h1{font-size:30px}.table-scroll{max-width:100%;overflow:auto}table{border-collapse:collapse;width:100%;min-width:800px;font-size:15px;line-height:1.8}th,td{border:1px solid #bac6d4;text-align:left;vertical-align:top;padding:12px}th{background:#e7edf5}tbody tr:nth-child(even){background:#f4f7fa}</style><h1>LoL AutoCine V4追補</h1><p>追加の実映像観測・人工AV対照検証。研究全体は未完了。本体変更なし。</p>'+sections+'<section><h2>人工AV出力32本</h2><ul>'+links+'</ul></section></html>','utf-8')
files=[p for p in sorted(O.rglob('*')) if p.is_file() and p.name!='CONTENT_MANIFEST_ADDENDUM.json']
save('CONTENT_MANIFEST_ADDENDUM.json',{'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]})
z=R/'outputs/AutoCine_V4_Addendum_20261025.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in sorted(O.rglob('*')):
  if p.is_file():f.write(p,'AutoCine_V4_Addendum/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(z) as f:
 assert f.testzip() is None
 for x in load(O/'CONTENT_MANIFEST_ADDENDUM.json')['files']:assert hashlib.sha256(f.read('AutoCine_V4_Addendum/'+x['path'])).hexdigest()==x['sha256']
print(json.dumps({'zip':str(z),'sha256':sha(z),'bytes':z.stat().st_size,'members':len(zipfile.ZipFile(z).namelist()),'protection':len(checks),'video_segments':len(timing),'av_outputs':len(av['cases'])}))
