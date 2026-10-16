"""Build a clearly provisional offline still-image review pack; never edit native art."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from urllib.parse import quote
import hashlib,json,zipfile,shutil,subprocess,sys

BASE=Path('LoL_AutoCine/assets/kill_frames_chatgpt');ROOT=BASE/'full_production_v5'
DEST=BASE/'downloads/review_snapshot_20261017';WORK=Path('v5_quick_review_20261017_tmp')
COMMIT='120ed3bad77914ea29b66dbc760c008250d89afb'
ZIPNAME='AutoCine_652候補_すぐ確認_20261017.zip'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

SUMMARY='''# ChatGPT向け — LoL AutoCine制作の現状（2026-10-17）

全制作完了の報告ではありません。今回は、途中候補を一括で確認する静止画ZIPを追加しました。

## 作成・保存済み

- 原本89枚から抽出した652登録の初回フレーム候補が揃いました。新規634件＋既存の修正版から継承18件です。652枚の独立した原本がある意味ではありません。
- 原本crop・白背景・黒背景で現在の652候補を比較済み。GitHub実在とSHAの対応も全件確認済みです。
- 085/targon_variant_1をネイティブ2172×724で再生成し、旧版を残してgenerated_v5_1.pngを追加保存しました。
- 長辺2048px以上は651件。086/faerie_court_strongの1件は1983×793で再生成待ちです。
- 原本89枚のSHAに変更なし。既存37キルバッジとAutoCine本体コードは変更していません。

## 品質と未完了部分

- 全てreview候補です。最終合格は0件。不合格画像をfinalに入れていません。
- 形状・配色・文字残り等の目視要修正220件、外周alpha非ゼロ590件。201件が重複し、重複除外では609件が要対応です。単純合計810件としないでください。
- 薄いalphaの残りも完全透過の合格とは扱いません。縮小プレビューだけで透過品質を判定しないでください。
- 原本自体の見切れ8件と、小型配色参照11件を含みます。見えない部分を忠実に復元できたとは扱っていません。
- 652件全てに対応する個別エフェクト・動く確認版・完成素材ZIPは未制作です。既存の動くエフェクト35種は保存されていますが、全件版ではありません。

## 停止理由と再開位置

内蔵画像生成がHTTP 429 / usage_limit_reachedを返したため追加修正は停止しています。ツールが示した解除予定は2026-10-17 17:55:47（日本時間）。解除の保証・自動再開の予約ではありません。有料APIは使用していません。

次は086/faerie_court_strongのネイティブ2K再生成から。続いて形状・文字・背景残り・外周alpha等を修正し、新しいSHAで原本比較をやり直します。その後、全フレームのエフェクトとアニメーション確認版、確認ZIPを作成・検査する順序です。

## 今回の確認ZIP

「ここから確認.html」を開くと652候補を検索・一覧表示でき、画像をクリックすると原本比較と検査メモが開きます。背景切替、前後移動、キーボード操作、仮の採否記録とJSON書き出しに対応します。

ZIP内の候補画像は確認用に縮小したWebPです。ネイティブPNGの画素は変更していません。原寸PNGは各候補の「原寸PNG」リンクからGitHubの固定コミットを開いてください。原本cropは顔を含む比較用参照で、ゲーム用素材ではありません。このZIPは静止画の途中確認版で、動画・最終合格素材の一括納品ではありません。

## 保存先・証拠・分担

- GitHub: Aimin2222/agdhnteweeffewwff
- 専用ブランチ: chatgpt/killframes-source-numbering-20261014
- 制作物: LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5/
- 制作物固定コミット: 120ed3bad77914ea29b66dbc760c008250d89afb
- 全候補の照合記録: qa/github_current_candidate_coverage.json（605件は読み戻し済みと同一Gitオブジェクト、47件は固定コミットから直接取得・照合）
- 詳細: CURRENT_STATUS_20261017_JA.md、qa/visual_reviews.json、qa/strict_transparency_queue.json、qa/production_state_20261017.json
- Work: 画像素材・視覚演出設計・品質管理・素材仕様書とGitHub保存。
- ChatGPT: 企画・デザイン方針・UI/UX・全体仕様・完成基準。
- Codex: 本体統合・GPU処理・アニメーション実装・カメラ・録画・音声・技術テスト。Workは本体プログラムを変更しません。

この文書は引継ぎ用です。他チャットへ自動送信していません。
'''

PAGE=r'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AutoCine 652候補の途中確認</title>
<style>*{box-sizing:border-box}body{margin:0;background:#121722;color:#edf3ff;font:15px/1.6 system-ui,sans-serif}header{padding:22px 4vw;background:#1c2535}h1{margin:0;font-size:24px}p{margin:8px 0}.notice{color:#ffd48d}a{color:#9ccaff}button,input,select{font:inherit;padding:8px 12px;border:1px solid #50617b;border-radius:7px;background:#243248;color:inherit}button{cursor:pointer}button:hover{background:#364d6d}.tools{position:sticky;top:0;z-index:2;padding:12px 4vw;background:#171f2ff5;display:flex;flex-wrap:wrap;gap:8px}.grid{padding:18px 4vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px}.card{border:1px solid #36445a;border-radius:10px;background:#1b2332;padding:10px;text-align:left}.card img{width:100%;height:130px;object-fit:contain}.title{display:block;overflow-wrap:anywhere;font-weight:650}.badge{font-size:12px;color:#ffd48d}.checker{background:repeating-conic-gradient(#323a48 0% 25%,#697080 0% 50%) 50%/20px 20px}.white{background:white}.black{background:black}dialog{width:min(1350px,97vw);max-height:96vh;border:1px solid #61728c;border-radius:12px;background:#172131;color:#edf3ff;padding:18px}dialog::backdrop{background:#000b}.bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px}.compare{display:grid;grid-template-columns:1fr 1.25fr;gap:12px;margin-top:14px}.compare img{width:100%;height:280px;object-fit:contain}.panel{border:1px solid #45556b;border-radius:7px;overflow:hidden}.panel p{padding:6px 10px;margin:0}.info{white-space:pre-line;overflow-wrap:anywhere}small{color:#bdcadd}.muted{color:#bdcadd}.active{outline:2px solid #9bcaff}#count{padding:6px}#empty{padding:30px;display:none}@media(max-width:750px){.compare{grid-template-columns:1fr}.compare img{height:200px}.tools input{width:100%}}:focus-visible{outline:2px solid #b1d8ff}</style>
<header><h1>AutoCine｜652候補の途中確認</h1><p>原本89枚からの初回候補を一覧で確認できます。画像をクリックして原本と比較してください。</p><p class="notice">全てreview／最終合格0件。要対応609件（目視220・外周alpha590の重複を除く）。長辺2K未満1件。全件分の動くエフェクトは未制作です。</p><p><a href="ChatGPT向け_現状まとめ_JA.md">ChatGPT向けの現状まとめ</a> ／ <a href="詳細資料/CURRENT_STATUS_20261017_JA.md">詳しい制作状況</a></p><small>画像は縮小した確認版です。原寸PNGは詳細のリンクから取得できます（通信が必要）。仮選択は最終品質合格とは別です。</small></header>
<div class="tools"><input id="search" aria-label="候補検索" placeholder="番号・テーマ・候補名で検索（例：016 / PROJECT）"><select id="filter" aria-label="候補絞り込み"><option value="all">全候補</option><option value="issue">要対応</option><option value="visual">目視の要修正</option><option value="alpha">外周alphaに残り</option><option value="low">長辺2K未満</option><option value="partial">原本見切れ</option><option value="palette">小型配色見本</option><option value="picked">仮選択した候補</option></select><select id="background" aria-label="プレビュー背景"><option value="checker">市松背景</option><option value="black">黒背景</option><option value="white">白背景</option></select><button id="export">仮選択をJSON保存</button><span id="count"></span></div>
<main class="grid" id="grid"></main><p id="empty">該当する候補がありません。</p>
<dialog id="detail"><div class="bar"><button id="prev">← 前</button><button id="next">次 →</button><strong id="position"></strong><button id="close" style="margin-left:auto">閉じる</button></div><h2 id="title"></h2><div class="compare"><div class="panel"><p>原本の該当部分 <small>比較専用・素材ではありません</small></p><img id="source" alt="原本の該当部分"></div><div class="panel"><p>生成候補 <small>縮小プレビュー</small></p><div id="frameBoard" class="checker"><img id="frame" alt="生成候補"></div></div></div><p id="status" class="notice"></p><p id="notes" class="info"></p><div class="bar"><button data-choice="usable">使えそう</button><button data-choice="revise">修正して使う</button><button data-choice="reject">使わない</button><button data-choice="clear">仮選択を解除</button><span id="choiceLabel"></span></div><p><a id="native" target="_blank" rel="noopener">原寸PNG（GitHub）</a> ／ <a id="qaLink">この候補の記録JSON</a></p><details><summary>保存元・SHAを確認</summary><p id="identity" class="info"></p></details><small>← →キーで前後、Escで閉じる。WebPの拡大表示だけで原寸画質や厳格な透過合格を判断しないでください。</small></dialog>
<script>const items=__ITEMS__;const $=s=>document.getElementById(s);let choices={},visible=[],current=null;const storageKey='autocine-static-review-20261017';try{choices=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){}const labels={usable:'使えそう',revise:'修正して使う',reject:'使わない'};
function selection(a){let c=choices[a.key];return c&&c.sha256===a.sha256?c.choice:null}
function flags(a){let f=[];if(a.visual_repair)f.push('目視：要修正');if(a.edge_nonzero)f.push('外周alpha：残りあり');if(!a.native_2k)f.push('2K未満');if(a.source_partial)f.push('原本見切れ');if(a.palette_reference)f.push('小型配色参照');return f.length?f.join(' ／ '):'比較記録あり・最終合格は未判定'}
function matches(a){let q=$('search').value.trim().toLowerCase();if(q&&!(`${a.key} ${a.theme} ${a.number} ${a.notes.join(' ')}`).toLowerCase().includes(q))return false;let f=$('filter').value;return f==='all'||f==='issue'&&(a.visual_repair||a.edge_nonzero||!a.native_2k)||f==='visual'&&a.visual_repair||f==='alpha'&&a.edge_nonzero>0||f==='low'&&!a.native_2k||f==='partial'&&a.source_partial||f==='palette'&&a.palette_reference||f==='picked'&&!!selection(a)}
function render(){visible=items.filter(matches);$('grid').replaceChildren();for(const a of visible){let b=document.createElement('button');b.className='card';let im=document.createElement('img');im.src=a.frame;im.alt=a.key;im.loading='lazy';im.className=$('background').value;let title=document.createElement('span');title.className='title';title.textContent=`No.${a.number} / ${a.id}`;let tag=document.createElement('span');tag.className='badge';tag.textContent=flags(a);let pick=document.createElement('div');pick.className='muted';pick.textContent=selection(a)?'仮選択：'+labels[selection(a)]:a.theme;b.append(im,title,tag,pick);b.onclick=()=>openItem(a);$('grid').append(b)}$('count').textContent=`${visible.length} / ${items.length}件`;$('empty').style.display=visible.length?'none':'block';$('frameBoard').className=$('background').value}
function openItem(a){current=a;let i=visible.indexOf(a);$('position').textContent=`${i+1} / ${visible.length}`;$('prev').disabled=i<=0;$('next').disabled=i>=visible.length-1;$('title').textContent=`No.${a.number} / ${a.id}`;$('source').src=a.source;$('frame').src=a.frame;$('status').textContent=flags(a);$('notes').textContent=a.notes.join('\n');$('native').href=a.native;$('qaLink').href=a.record;$('identity').textContent=`元ファイル：${a.native_file}\n寸法：${a.dimensions.join(' × ')} / RGBA\nSHA-256：${a.sha256}\n外周alpha非ゼロの検出数：${a.edge_nonzero}\n最終合格：未承認`;$('choiceLabel').textContent=selection(a)?'現在：'+labels[selection(a)]:'未選択';for(const b of document.querySelectorAll('[data-choice]'))b.classList.toggle('active',b.dataset.choice===selection(a));if(!$('detail').open)$('detail').showModal()}
function step(n){let i=visible.indexOf(current)+n;if(i>=0&&i<visible.length)openItem(visible[i])}
$('search').oninput=render;$('filter').onchange=render;$('background').onchange=render;$('close').onclick=()=>$('detail').close();$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);document.addEventListener('keydown',e=>{if(!$('detail').open||/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowLeft'){e.preventDefault();step(-1)}if(e.key==='ArrowRight'){e.preventDefault();step(1)}});
for(const b of document.querySelectorAll('[data-choice]'))b.onclick=()=>{if(b.dataset.choice==='clear')delete choices[current.key];else choices[current.key]={choice:b.dataset.choice,sha256:current.sha256};try{localStorage.setItem(storageKey,JSON.stringify(choices))}catch(e){}openItem(current)};
$('detail').addEventListener('close',render);$('export').onclick=()=>{let active={};for(const a of items)if(selection(a))active[a.key]=choices[a.key];let out={version:'review-snapshot-20261017',status:'user_provisional_choices_not_quality_final_approval',source_commit:'120ed3bad77914ea29b66dbc760c008250d89afb',exported_at:new Date().toISOString(),choices:active};let url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));let a=document.createElement('a');a.href=url;a.download='AutoCine_652候補_仮選択.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};render();</script></html>'''

def main():
 resume='--resume-unpublished' in sys.argv
 assert not (DEST/ZIPNAME).exists(),'Preserve an existing published ZIP; use a new version'
 if not resume:
  assert not DEST.exists(),'Preserve an existing published snapshot; use a new version'
  assert not WORK.exists(),'Use a fresh staging folder'
 DEST.mkdir(parents=True,exist_ok=resume);WORK.mkdir(exist_ok=resume);(WORK/'media').mkdir(exist_ok=resume);(WORK/'records').mkdir(exist_ok=resume);(WORK/'詳細資料').mkdir(exist_ok=resume)
 d=json.loads((ROOT/'checkpoints/checkpoint_0634_repair0001_quota.json').read_text(encoding='utf-8'))
 reviews={a['key']:a for a in json.loads((ROOT/'qa/visual_reviews.json').read_text(encoding='utf-8'))['assets']}
 technical={a['key']:a for a in json.loads((ROOT/'qa/technical_snapshot.json').read_text(encoding='utf-8'))['assets']}
 def preview(a):
  v=reviews[a['key']];t=technical[a['key']];assert v['sha256']==t['sha256']==a['sha256']
  native=Path(a['output']);assert sha(native)==a['sha256']
  stem=f'{a["number"]}_{a["id"]}';frame='media/'+stem+'.webp';source='media/'+stem+'_source.jpg';record='records/'+stem+'.json'
  with Image.open(native) as im:
   assert im.mode=='RGBA';im.thumbnail((1024,420),Image.Resampling.LANCZOS);im.save(WORK/frame,quality=84,method=4)
  with Image.open(a.get('comparison_reference',a['reference'])) as im:
   im=im.convert('RGB');im.thumbnail((560,300),Image.Resampling.LANCZOS);im.save(WORK/source,quality=84)
  row=dict(key=a['key'],number=a['number'],id=a['id'],theme=a['theme'],frame=frame,source=source,record=record,native='https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/'+COMMIT+'/'+quote(a['output'],safe='/'),native_file=a['output'],sha256=a['sha256'],dimensions=t['dimensions'],native_2k=t['native_long_edge_at_least_2048'],visual_repair=v['repair_required'],edge_nonzero=t['edge_nonzero'],source_partial=a['source_partial'],palette_reference=a['palette_reference'],notes=v['notes'],final_approved=False)
  (WORK/record).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');return row
 with ThreadPoolExecutor(max_workers=4) as pool:items=list(pool.map(preview,d['assets']))
 assert len(items)==652
 items.sort(key=lambda a:a['key']);page=PAGE.replace('__ITEMS__',json.dumps(items,ensure_ascii=False).replace('<','\\u003c'))
 (WORK/'ここから確認.html').write_text(page,encoding='utf-8')
 js=page.split('<script>')[1].split('</script>')[0];Path('v5_quick_review_script_tmp.js').write_text(js,encoding='utf-8')
 subprocess.run(['C:/Program Files/nodejs/node.exe','--check','v5_quick_review_script_tmp.js'],check=True)
 (WORK/'ChatGPT向け_現状まとめ_JA.md').write_text(SUMMARY,encoding='utf-8')
 (WORK/'最初にお読みください.txt').write_text('ZIPを右クリックして「すべて展開」し、「ここから確認.html」をダブルクリックしてください。\n652件の静止画候補の確認版です。全てreview・最終合格0件。候補画像をクリックすると原本比較と検査メモが開きます。\n原寸PNGリンク以外はオフラインで使えます。仮選択はJSONで保存できます。\nZIP内の画像は縮小確認用です。原寸素材の変更・修正は行っていません。\n',encoding='utf-8-sig')
 for name in ['CURRENT_STATUS_20261017_JA.md','IMPLEMENTATION_JA.md']:
  shutil.copyfile(ROOT/name,WORK/'詳細資料'/name)
 for name in ['production_state_20261017.json','source_integrity.json','github_current_candidate_coverage.json']:
  shutil.copyfile(ROOT/'qa'/name,WORK/'詳細資料'/name)
 (WORK/'catalog.json').write_text(json.dumps(dict(count=652,status='provisional_still_review_not_final',source_commit=COMMIT,assets=items),ensure_ascii=False,indent=2),encoding='utf-8')
 files=sorted(p for p in WORK.rglob('*') if p.is_file())
 manifest=[dict(file=p.relative_to(WORK).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
 (WORK/'contents_sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 out=DEST/ZIPNAME
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,6) as z:
  for p in sorted(WORK.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(WORK).as_posix())
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for a in manifest:assert hashlib.sha256(z.read(a['file'])).hexdigest()==a['sha256']
  assert sum(n.endswith('.webp') for n in z.namelist())==652
  assert sum(n.endswith('_source.jpg') for n in z.namelist())==652
 assert out.stat().st_size<95*1024*1024,'Review ZIP must stay under GitHub file size limit'
 (DEST/'ChatGPT向け_現状まとめ_JA.md').write_text(SUMMARY,encoding='utf-8')
 inventory=dict(status='provisional_still_review_not_final',image_count=652,zip=out.as_posix(),bytes=out.stat().st_size,sha256=sha(out),source_commit=COMMIT,native_images_modified=False,all_zip_contents_sha256_verified=True)
 (DEST/'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(inventory,ensure_ascii=False))

if __name__=='__main__':main()
