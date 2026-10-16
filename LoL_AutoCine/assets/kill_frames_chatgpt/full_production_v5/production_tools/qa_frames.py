from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,sys
import numpy as np,cv2
ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
plan=json.loads((Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'production.json').read_text(encoding='utf-8'))
original=json.loads((ROOT.parent/'full_production_v4/inventory.json').read_text(encoding='utf-8'))
expected={a['key']:[next(iter(h)) for h in a['portrait_holes']] for a in original['assets']}
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
rows=[]
for a in plan['assets']:
    if a['status']=='pending':continue
    p=Path(a['output']);assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
    im=Image.open(p);assert im.mode=='RGBA'
    aa=np.array(im.getchannel('A'));edge=np.r_[aa[0],aa[-1],aa[:,0],aa[:,-1]]
    opaque=(aa>25).astype('uint8');opaque=cv2.morphologyEx(opaque,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,labels,stats,centroids=cv2.connectedComponentsWithStats(1-opaque,8);holes=[]
    for side in [0,1]:
        found=[]
        for i,(x,y,w,h,area) in enumerate(stats[1:],1):
            cx,cy=centroids[i]
            if x<=0 or y<=0 or x+w>=im.width or y+h>=im.height or area<im.width*im.height*.015:continue
            if (cx<im.width*.35 if side==0 else cx>im.width*.65):found.append((int(area),i))
        if found:
            _,i=max(found);v=aa[labels==i];fill=float(len(v)/max(1,int(stats[i,2])*int(stats[i,3])))
            geometry=expected.get(a['key'],[]);registered=geometry[side] if len(geometry)>side else 'unknown'
            possible_mismatch=(registered in ['polygon','rectangle'] and fill<.86) or (registered=='ellipse' and fill>.91)
            holes.append(dict(side=side,area=int(len(v)),nonzero_alpha=int((v!=0).sum()),max_alpha=int(v.max()),fill_ratio=fill,registered_geometry=registered,possible_geometry_mismatch=possible_mismatch))
    visible=np.argwhere(aa>32)
    y0,x0=visible.min(axis=0);y1,x1=visible.max(axis=0)
    margins=[int(x0),int(y0),int(im.width-1-x1),int(im.height-1-y1)]
    rows.append(dict(key=a['key'],file=a['output'],sha256=a['sha256'],dimensions=list(im.size),native_long_edge_at_least_2048=max(im.size)>=2048,edge_nonzero=int((edge!=0).sum()),alpha_zero_pixels=int((aa==0).sum()),visible_alpha_gt32_margin_px=margins,portrait_holes=holes,portrait_holes_detected=len(holes),reference=a['reference'],source_partial=a['source_partial'],palette_reference=a['palette_reference'],visual_review='pending',final_approved=False))
(qa/'technical_snapshot.json').write_text(json.dumps(dict(count=len(rows),scope='Only currently saved candidates; not all production completed',final_approved=0,assets=rows),ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',16)
reviewed_path=qa/'visual_reviews.json'
reviewed={a['key']:a['sha256'] for a in json.loads(reviewed_path.read_text(encoding='utf-8'))['assets']} if reviewed_path.exists() else {}
new=[a for a in rows if reviewed.get(a['key'])!=a['sha256']]
snapshot=hashlib.sha256(''.join(a['sha256'] for a in rows).encode()).hexdigest()[:10];pages=[]
for start in range(0,len(new),6):
    page=new[start:start+6];canvas=Image.new('RGB',(1800,len(page)*320),'#30343a');d=ImageDraw.Draw(canvas)
    for i,a in enumerate(page):
        y=i*320;d.text((10,y+5),a['key']+' | reference crop / white / black | '+str(a['dimensions']),font=font,fill='white')
        src=ImageOps.contain(Image.open(a['reference']).convert('RGB'),(560,260),Image.Resampling.BICUBIC);canvas.paste(src,(15,y+40))
        im=ImageOps.contain(Image.open(a['file']).convert('RGBA'),(570,260),Image.Resampling.LANCZOS)
        for col,color in [(1,'white'),(2,'black')]:
            b=Image.new('RGBA',(590,270),color);b.alpha_composite(im,((590-im.width)//2,(270-im.height)//2));canvas.paste(b.convert('RGB'),(col*600,y+38))
    p=qa/f'review_{snapshot}_{start:04d}.jpg';canvas.save(p,quality=94)
    pages.append(dict(file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),assets=[dict(key=a['key'],sha256=a['sha256']) for a in page]))
(qa/'contacts_manifest.json').write_text(json.dumps(dict(snapshot=snapshot,saved_count=len(rows),unreviewed_count=len(new),pages=pages),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(saved=len(rows),all_native_2k=all(a['native_long_edge_at_least_2048'] for a in rows),holes_not_two=[a['key'] for a in rows if a['portrait_holes_detected']!=2],geometry_flags=[a['key'] for a in rows if any(h['possible_geometry_mismatch'] for h in a['portrait_holes'])],unreviewed=len(new),new_contact_pages=len(pages))))
