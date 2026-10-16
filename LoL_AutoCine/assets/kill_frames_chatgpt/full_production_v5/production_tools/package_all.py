"""Build offline review ZIP and byte-preserving native PNG packs after production."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from PIL import Image
from urllib.parse import quote
from functools import lru_cache
import json,hashlib,shutil,subprocess,zipfile,re,html
BASE=Path('LoL_AutoCine/assets/kill_frames_chatgpt');ROOT=BASE/'full_production_v5';VIEW=ROOT/'offline_review';DOWNLOAD=BASE/'downloads/full_production_v5'
RAW='https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/refs/heads/chatgpt/killframes-source-numbering-20261014/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def online(p):return RAW+quote(str(p).replace('\\','/'),safe='/')

@lru_cache(maxsize=1)
def reviewed_notes():
    path=ROOT/'qa/visual_reviews.json'
    return {a['key']:a for a in json.loads(path.read_text(encoding='utf-8'))['assets']} if path.exists() else {}
def preview(a):
    folder=VIEW/'media'/a['number']/a['id'];folder.mkdir(parents=True,exist_ok=True)
    source=ROOT/'motion'/a['number']/a['id']
    im=Image.open(a['output']).convert('RGBA');im.thumbnail((1024,500),Image.Resampling.LANCZOS);im.save(folder/'frame.webp',quality=84,method=4)
    ref=Image.open(a.get('comparison_reference',a['reference'])).convert('RGB');ref.thumbnail((600,340));ref.save(folder/'source.jpg',quality=94)
    poster=Image.open(source/'poster.jpg');poster.thumbnail((480,270));poster.save(folder/'poster.jpg',quality=80)
    movie=folder/'comparison.mp4'
    subprocess.run([shutil.which('ffmpeg'),'-v','error','-y','-i',str(source/'comparison.mp4'),'-an','-map_metadata','-1','-vf','scale=640:360:flags=lanczos','-r','24','-c:v','libx264','-preset','medium','-threads','1','-b:v','160k','-maxrate','180k','-bufsize','360k','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
    assert movie.stat().st_size>3000
    spec=VIEW/'specs'/a['number']/(a['id']+'.json');spec.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/'motion.json',spec)
    review=reviewed_notes().get(a['key'],{})
    if review.get('sha256')!=a['sha256']:review={}
    return dict(id=a['key'],label='No.'+a['number']+' / '+a['theme']+' / '+a['id'],mode=json.loads(spec.read_text(encoding='utf-8'))['mode'],video=movie.relative_to(VIEW).as_posix(),poster=(folder/'poster.jpg').relative_to(VIEW).as_posix(),alpha=online(source/'effect_alpha.webp'),spec=spec.relative_to(VIEW).as_posix(),source=(folder/'source.jpg').relative_to(VIEW).as_posix(),frame=(folder/'frame.webp').relative_to(VIEW).as_posix(),native_frame=online(a['output']),native_fx=online(source/'impact_2048_rgba.png'),full_video=online(source/'comparison.mp4'),frame_sha256=a['sha256'],source_partial=a['source_partial'],palette_reference=a['palette_reference'],review_notes=review.get('notes',['原本比較は未記録。']),repair_required=review.get('repair_required',False),quality_flags=a.get('quality_flags',[]))
def build_viewer(items):
    page=(BASE/'animation_review_v3/ここから確認.html').read_text(encoding='utf-8')
    count=len(items)
    page=re.sub(r'const items=.*?;let index=0,choices=\{\};',lambda m:'const items='+json.dumps(items,ensure_ascii=False).replace('<','\\u003c')+';let index=0,choices={};',page,count=1,flags=re.S)
    page=page.replace('35種類',str(count)+'件').replace('35種類',str(count)+'件')
    page=page.replace("(index+1)+'/35 '+a.label","(index+1)+'/'+items.length+' '+a.label")
    page=page.replace('autocine-motion-v3','autocine-all-frames-v5').replace('version:3,choices','version:5,choices,frames:items.map(a=>({id:a.id,sha256:a.frame_sha256}))')
    page=page.replace('追加ソフトや通信は不要です。','軽量版の比較動画は通信不要です。高画質PNGと透過動画のリンクはGitHubを開きます。')
    page=page.replace('透過付きの動く見本を開く','透過の動く見本（GitHub）').replace('動くエフェクト_選択結果.json','全キルフレーム_選択結果_v5.json')
    extra='<p><a id="nativeFrame" target="_blank">高画質フレームPNG</a> ／ <a id="nativeFx" target="_blank">高画質エフェクトPNG</a> ／ <a id="fullVideo" target="_blank">高画質の比較動画</a></p><details><summary>原本との静止画比較を開く</summary><p>左は比較用crop、右は生成版の縮小表示です。顔のある左画像は比較参照で、素材ではありません。</p><img id="sourceImage" style="width:40%;vertical-align:middle"><img id="frameImage" style="width:58%;vertical-align:middle;background:repeating-conic-gradient(#333 0% 25%,#777 0% 50%) 50%/20px 20px"></details><p id="sourceNote"></p>'
    page=page.replace('<p class="meta">',extra+'<p class="meta">',1)
    hook="$('nativeFrame').href=a.native_frame;$('nativeFx').href=a.native_fx;$('fullVideo').href=a.full_video;$('sourceImage').src=a.source;$('frameImage').src=a.frame;$('sourceNote').textContent=a.source_partial?'原本自体に見切れがあります。未確認の部分を含む候補です。':a.palette_reference?'小型の配色見本からの再構成候補です。':'確認用候補。原本との細部の一致・最終採用は別に判定します。';"
    hook+="$('sourceNote').textContent=(a.repair_required?'要修正候補：':'確認記録：')+(a.review_notes||[]).join(' ／ ')+' — '+$('sourceNote').textContent;"
    page=page.replace("$('specLink').href=a.spec;","$('specLink').href=a.spec;"+hook)
    page=page.replace("if($('auto').checked)show(index+1);else", "if($('auto').checked&&index<items.length-1)show(index+1);else if(!$('auto').checked)")
    (VIEW/'ここから全件確認.html').write_text(page,encoding='utf-8')
    js=page.split('<script>')[1].split('</script>')[0];js=re.sub(r'const items=.*?;let index', 'const items=[];let index',js,count=1,flags=re.S)
    Path('all_v5_viewer_syntax_tmp.js').write_text(js,encoding='utf-8')
    subprocess.run(['C:/Program Files/nodejs/node.exe','--check','all_v5_viewer_syntax_tmp.js'],check=True,capture_output=True)
def native_packs(assets):
    entries=[]
    for a in assets:
        entries.append((Path(a['output']),f'native/frames/{a["number"]}/{a["id"]}.png',a['key'],'frame'))
        entries.append((ROOT/'motion'/a['number']/a['id']/'impact_2048_rgba.png',f'native/effects/{a["number"]}/{a["id"]}.png',a['key'],'effect'))
    groups=[];group=[];size=0
    for e in entries:
        n=e[0].stat().st_size
        if group and size+n>80*1024*1024:groups.append(group);group=[];size=0
        group.append(e);size+=n
    if group:groups.append(group)
    inventory=[]
    for i,group in enumerate(groups,1):
        dest=DOWNLOAD/f'AutoCine_高画質透過PNG_v5_part{i:02d}.zip';records=[]
        cards=[]
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,6) as z:
            for p,name,key,kind in group:
                z.write(p,name);records.append(dict(key=key,kind=kind,file=name,sha256=sha(p),bytes=p.stat().st_size))
                cards.append('<figure><img loading="lazy" src="'+html.escape(name)+'"><figcaption>'+html.escape(key+' / '+kind)+'</figcaption></figure>')
            z.writestr('内容一覧_part%02d.json'%i,json.dumps(records,ensure_ascii=False,indent=2))
            gallery='<!doctype html><html lang="ja"><meta charset="utf-8"><title>高画質透過PNG</title><style>body{background:#252a32;color:white;font:16px sans-serif}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:15px}figure{margin:8px}img{width:100%;height:240px;object-fit:contain;background:repeating-conic-gradient(#333 0% 25%,#888 0% 50%) 50%/20px 20px}</style><h1>高画質透過PNG part__PART__</h1><p>確認用候補。原本不足・要修正は全件台帳と検査記録を参照してください。</p><main>'.replace('__PART__',f'{i:02d}')+''.join(cards)+'</main></html>'
            z.writestr('高画質画像一覧_part%02d.html'%i,gallery)
        with zipfile.ZipFile(dest) as z:assert z.testzip() is None
        assert dest.stat().st_size<95*1024*1024
        inventory.append(dict(file=dest.as_posix(),bytes=dest.stat().st_size,sha256=sha(dest),image_count=len(group)))
    return inventory
def main():
    plan=json.loads((ROOT/'production.json').read_text(encoding='utf-8'));assets=plan['assets'];assert len(assets)==652 and not any(a['status']=='pending' for a in assets)
    for a in assets:assert sha(Path(a['output']))==a['sha256'] and max(Image.open(a['output']).size)>=2048
    motion=json.loads((ROOT/'motion_catalog.json').read_text(encoding='utf-8'));assert motion['count']==len(assets)
    VIEW.mkdir(exist_ok=True);DOWNLOAD.mkdir(parents=True,exist_ok=True)
    items=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        tasks={pool.submit(preview,a):a['key'] for a in assets}
        for task in as_completed(tasks):items.append(task.result());print('review preview '+tasks[task],flush=True)
    items.sort(key=lambda a:a['id']);build_viewer(items)
    (VIEW/'catalog.json').write_text(json.dumps(dict(count=len(items),status='review_not_final_approved',assets=items),ensure_ascii=False,indent=2),encoding='utf-8')
    (VIEW/'確認方法_JA.md').write_text('ZIPをすべて展開し「ここから全件確認.html」を開いてください。一覧・原本比較・連続再生・スロー・採否記録に対応します。比較動画は軽量640×360/24fpsで、素材本体の画質とは別です。フレームは横2K以上の透過PNG、エフェクトピークPNGは2048×1152。本体組み込み・実LoL映像・GPU動作は別工程です。原本見切れや再構成の差分は品質記録に残しています。高画質素材は別のPNG ZIP、または一覧のGitHubリンクから取得できます。',encoding='utf-8')
    for name in ['technical_snapshot.json','visual_reviews.json','source_integrity.json','delivery_summary.json']:
        source=ROOT/'qa'/name
        if source.exists():shutil.copyfile(source,VIEW/name)
    specdir=VIEW/'実装仕様';specdir.mkdir(exist_ok=True);shutil.copyfile('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5/production_tools/render_motion.py',specdir/'frame_native_renderer.py')
    shutil.copyfile(ROOT/'production.json',specdir/'production.json')
    for name in ['CHATGPT_HANDOFF_JA.md','IMPLEMENTATION_JA.md']:
        if (ROOT/name).exists():shutil.copyfile(ROOT/name,specdir/name)
    package=DOWNLOAD/'AutoCine_全キルフレームと動き_一括確認_v5.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,6) as z:
        for p in sorted(VIEW.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(VIEW).as_posix())
    with zipfile.ZipFile(package) as z:assert z.testzip() is None
    assert package.stat().st_size<95*1024*1024,'Review ZIP exceeds repository file limit; reduce review-only bitrate'
    packages=[dict(file=package.as_posix(),bytes=package.stat().st_size,sha256=sha(package),kind='all_offline_review')]+native_packs(assets)
    (DOWNLOAD/'inventory.json').write_text(json.dumps(dict(count=len(assets),status='review_not_final_approved',packages=packages),ensure_ascii=False,indent=2),encoding='utf-8')
    print('ALL REVIEW AND NATIVE PACKS CREATED',flush=True)
if __name__=='__main__':main()
