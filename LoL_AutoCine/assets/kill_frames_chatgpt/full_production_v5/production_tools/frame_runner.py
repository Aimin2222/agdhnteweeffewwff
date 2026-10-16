from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import json,hashlib,shutil,sys,time,msvcrt
import os
import numpy as np

BASE=Path('LoL_AutoCine/assets/kill_frames_chatgpt');OUT=BASE/'full_production_v5';PLAN=OUT/'production.json'
SOURCE=Path(os.environ.get('AUTOCINE_KILL_SOURCE_DIR','LoL_AutoCine/assets/kill_concepts'))
if not SOURCE.exists() and Path('../LoL_AutoCine/assets/kill_concepts').exists():SOURCE=Path('../LoL_AutoCine/assets/kill_concepts')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(data):
    temporary=PLAN.with_suffix('.json.new');temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(5):
        try:temporary.replace(PLAN);break
        except PermissionError:
            if attempt==4:raise
            time.sleep(.15*(attempt+1))
def load():return json.loads(PLAN.read_text(encoding='utf-8'))
def initialize():
    assert not PLAN.exists()
    OUT.mkdir(exist_ok=True)
    inv=json.loads((BASE/'full_production_v4/inventory.json').read_text(encoding='utf-8'))
    rows=[]
    for a in inv['assets']:
        if a['scope']!='frame_production':continue
        n=a['number'];folder=OUT/'frames'/n;folder.mkdir(parents=True,exist_ok=True)
        ref=folder/(a['id']+'.source_crop.png')
        box=a.get('corrected_reference',{}).get('crop_box',a['crop_box'])
        src=SOURCE/a['source_file'];assert sha(src)==a['source_sha256']
        with Image.open(src) as im:im.crop(box).save(ref)
        prompt=(f'Use case: stylized-concept, precise reference-based game UI reconstruction. Make ONE high-resolution isolated horizontal kill-frame asset, source No.{n}, exact variant {a["id"]}, theme {a["theme"]}, intensity {a["intensity"]}, role {a["role"]}. '
        'Image 1 is the exact cropped variant to reconstruct. Image 2 is the complete original sheet for context: reconstruct ONLY the variant shown in Image 1, never another row. '
        'Create a crisp richly detailed 2K-or-higher painted metallic/fantasy/sci-fi UI asset on an actual transparent RGBA canvas, preferably 2560 pixels wide, no blurry upscaling. '
        'Preserve the reference silhouette, palette, material, exact portrait-ring shape (round or angular), both left/right borders, central ornament, connecting bars, spacing, line weights and theme motifs. Weak and strong variants must remain distinct. '
        'Remove champion faces, heads, hair, people, portrait occupants, ALL text/numbers/labels and scenery. Both portrait interiors must be entirely empty alpha-zero holes. Keep native decorative animal/mascot ornaments only if part of the frame. '
        'Do not add generic symbols, larger invented central emblems, extra frames or a whole contact sheet. No logo, watermark, paper or checkerboard painted into pixels. '
        'Keep the ENTIRE frame and every feather/flame/light/particle tip inside a generous fully transparent 15% margin on every side. Local translucent glow is allowed; the background and all negative spaces must be truly transparent. '
        'Single usable frame only, no title or presentation. '
        +('Original itself is partly cut off: preserve only supported visible design; do not invent missing details, this will be labeled source-incomplete.' if a['source_partial'] else ''))
        row=dict(index=len(rows),key=a['key'],number=n,id=a['id'],theme=a['theme'],intensity=a['intensity'],role=a['role'],source_file=a['source_file'],source_sha256=a['source_sha256'],source_partial=a['source_partial'],palette_reference=a['palette_reference'],reference=ref.as_posix(),reference_crop_box=box,reference_sha256=sha(ref),original_reference=src.resolve().as_posix(),output=(folder/(a['id']+'.generated.png')).as_posix(),prompt=prompt,status='pending',effect_status='pending_after_frame',final_approved=False)
        prior=a.get('prior_exact_part_candidate')
        if prior:
            row.update(status='existing_review_candidate',output=prior['file'],sha256=prior['sha256'],reused_exact_part=True)
        elif a['key']=='002/victorious_variant_1':
            p=BASE/'full_production_v4/002/victorious_variant_1.attempt_04.png'
            row.update(status='existing_review_candidate',output=p.as_posix(),sha256=sha(p),reused_exact_part=True)
        rows.append(row)
    data=dict(version=5,status='production_in_progress',scope='All registered source-sheet frame variants except UI layout example; keep palette samples and source-incomplete flags',source_count=89,frame_entries=len(rows),excluded_ui_layouts=1,auxiliary_centers_not_counted_as_frames=602,final_approved=0,assets=rows)
    write(data)
    print(json.dumps(dict(total=len(rows),existing=sum(a['status']=='existing_review_candidate' for a in rows),pending=sum(a['status']=='pending' for a in rows))))
def save_unlocked(index,path):
    data=load();a=data['assets'][index];p=Path(a['output'])
    if a['status']!='pending':
        assert a['sha256']==sha(Path(path))
        print(json.dumps(dict(key=a['key'],already_saved=True)));return
    if p.exists():assert sha(p)==sha(Path(path)),'Existing candidate differs; do not overwrite'
    else:
        temporary=OUT/'staging'/a['number']/(a['id']+'.png')
        temporary.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,temporary);temporary.replace(p)
    with Image.open(p) as im:
        mode=im.mode;size=list(im.size)
        alpha=np.array(im.getchannel('A')) if mode=='RGBA' else None
    a.update(status='generated_review_pending',sha256=sha(p),bytes=p.stat().st_size,mode=mode,dimensions=size,generator='built-in image_gen',generated_epoch=int(time.time()),final_approved=False)
    a['generation_prompt']=a['prompt']+' Canvas composition: very wide 3:1 landscape, at least 2048 pixels on the long edge; keep vertical frame proportions faithful, centered with transparent padding.'
    flags=[]
    if alpha is not None:
        edge=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
        a.update(alpha_zero_pixels=int((alpha==0).sum()),edge_alpha_nonzero=int((edge>0).sum()))
        if a['edge_alpha_nonzero']:flags.append('outer_edge_alpha_residue')
        if not a['alpha_zero_pixels']:flags.append('no_transparent_pixels')
    else:flags.append('not_rgba')
    if max(size)<2048:flags.append('native_long_edge_below_requested_2k')
    if a['source_partial']:flags.append('original_incomplete_not_fully_reconstructable')
    if a['palette_reference']:flags.append('tiny_palette_reference_not_independent_high_detail_original')
    a['quality_flags']=flags
    a['visual_review']='pending_original_comparison'
    data['status']='production_in_progress'
    data['last_updated_utc']=datetime.now(timezone.utc).isoformat()
    data['saved_candidates']=sum(x['status']!='pending' for x in data['assets'])
    data['counts']={s:sum(x['status']==s for x in data['assets']) for s in sorted({x['status'] for x in data['assets']})}
    data['next_unproduced_key']=next((x['key'] for x in data['assets'] if x['status']=='pending'),None)
    write(data)
    print(json.dumps(dict(key=a['key'],status=a['status'],dimensions=size,flags=flags)))
def save(index,path):
    receipts=Path('v5_generation_receipts_tmp');receipts.mkdir(exist_ok=True)
    (receipts/f'{index:04d}.json').write_text(json.dumps(dict(index=index,generated_path=str(path),receipt_epoch=int(time.time()))),encoding='utf-8')
    with (OUT/'production.lock').open('a+b') as lock:
        lock.seek(0,2)
        if lock.tell()==0:lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
        try:save_unlocked(index,path)
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
def jobs_unlocked():
    start,count=int(sys.argv[2]),int(sys.argv[3])
    config=Path('production_batch_config.json')
    if start==0 and len(sys.argv)==4 and config.exists():
        count=max(count,min(12,int(json.loads(config.read_text(encoding='utf-8'))['parallel_assets'])))
    data=load();rows=[a for a in data['assets'] if a['status']=='pending'];rows=rows[start:start+count]
    if len(sys.argv)==4 and rows:
        for a in rows:
            if a.get('prompt_guidance_revision')!='source-fidelity-20261016-r2':
                a['prompt']+=' Additional source-fidelity constraints: empty reference spaces must remain empty. If portrait frames and the central ornament are separate in the exact crop, preserve those gaps; do not invent connecting bars, outer arcs, stars, gems, flowers or spikes. Never borrow ornament from adjacent strong variants. A central X or cross that belongs to the frame is a required structural ornament: retain its exact form; remove explanatory writing only, not the cross. '
                a['prompt_guidance_revision']='source-fidelity-20261016-r2'
        write(data)
    if len(sys.argv)>4 and sys.argv[4]=='metadata':
        fields=['index','key','number','id','theme','role','intensity','source_file','source_partial','palette_reference','reference','output']
        rows=[{k:a[k] for k in fields} for a in rows]
    print(json.dumps(rows,ensure_ascii=True))
def jobs():
    with (OUT/'production.lock').open('a+b') as lock:
        lock.seek(0,2)
        if lock.tell()==0:lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
        try:jobs_unlocked()
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

def atlas(start,count):
    data=load();page=[a for a in data['assets'] if a['status']=='pending'][start:start+count]
    im=Image.new('RGB',(1500,len(page)*220),'#30343b');d=ImageDraw.Draw(im)
    for i,a in enumerate(page):
        d.text((10,i*220+8),str(a['index'])+' '+a['key']+' | '+a['theme'],fill='white')
        ref=Image.open(a['reference']).convert('RGB');ref.thumbnail((1450,180));im.paste(ref,(10,i*220+35))
    p=OUT/f'input_atlas_{start:04d}.jpg';im.save(p,quality=95);print(p.resolve().as_posix())
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='init':initialize()
    elif cmd=='jobs':jobs()
    elif cmd=='save':save(int(sys.argv[2]),sys.argv[3])
    elif cmd=='atlas':atlas(int(sys.argv[2]),int(sys.argv[3]))
