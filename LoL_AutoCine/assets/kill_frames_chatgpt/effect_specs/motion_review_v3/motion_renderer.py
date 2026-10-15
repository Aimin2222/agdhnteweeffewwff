"""Standalone design renderer. Does not import or modify the AutoCine application."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont, ImageChops
import cv2, numpy as np
import math, json, hashlib, random, subprocess, shutil, argparse

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT.parents[2]
OUT=ROOT/'animation_review_v3'
FPS=30; COUNT=78; W=512; H=288
RENDER_VERSION='motion-v3.1'
PROFILES={
'A':('minimal',0,0.35),'B':('glint',12,0.65),'C':('collision',30,0.75),'D':('wing',24,0.95),
'project':('scan',28,0.8),'star_guardian':('star',28,1.05),'spirit_blossom':('petal',30,1.25),
'winter_festival':('snow',30,1.25),'kda':('beat',24,0.95),'heartsteel':('beat',22,0.85),
'dark_star':('inward',32,1.05),'high_noon':('slash',28,0.75),'blood_moon':('arc',26,1.0),
'warring_kingdoms':('slash',22,0.9),'pool_party':('water',30,1.15),'elderwood':('petal',24,1.3),
'cosmic':('orbit',28,1.15),'dark_cosmic':('inward',26,1.15),'dawnbringer':('wing',26,1.0),
'nightbringer':('flame',28,1.05),'infernal':('flame',34,1.1),'arcade':('pixel',32,0.9),
'bewitching':('arc',24,1.1),'porcelain':('glint',20,1.1),'psyops':('scan',30,0.85),
'steel_valkyries':('lock',26,0.95),'broken_covenant':('slash',28,1.0),'faerie_court':('petal',28,1.25),
'space_groove':('orbit',30,1.2),'ocean_song':('water',28,1.25),'mecha_kingdoms':('lock',22,1.0),
'dragonmancer':('dragon',28,1.15),'shan_hai_scrolls':('brush',22,1.3),'mecha':('lock',28,0.85),
'battlecast':('lock',30,0.85)}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def fade(t,end):
    if t<0 or t>=end:return 0
    return smooth(t/.08)*(1-smooth((t-.16)/max(.01,end-.16)))
def overlay(dst,im,x,y,opacity=1,angle=0,scale=1,nearest=False):
    if opacity<=0:return
    im=im.copy()
    if scale!=1:im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.NEAREST if nearest else Image.Resampling.BICUBIC)
    if angle:im=im.rotate(angle,resample=Image.Resampling.NEAREST if nearest else Image.Resampling.BICUBIC,expand=True)
    if opacity<1:im.putalpha(im.getchannel('A').point(lambda a:round(a*max(0,min(1,opacity)))))
    dst.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))

def sprites(im):
    arr=np.asarray(im.getchannel('A'));n,labels,stats,centroids=cv2.connectedComponentsWithStats((arr>40).astype('uint8'),8)
    boxes=[]
    for x,y,w,h,area in stats[1:]:
        if 12<=area<=im.width*im.height*.008 and w>=3 and h>=3 and w<im.width*.17 and h<im.height*.3:
            boxes.append((int(x),int(y),int(x+w),int(y+h),'detached_alpha_component',int(area)))
    boxes.sort(key=lambda b:-b[-1]);boxes=boxes[:14]
    if len(boxes)<4:
        # Source texture patches, explicitly NOT certified complete petals/stars.
        for yy in range(1,5):
            for xx in range(1,9):
                x=round(im.width*xx/10);y=round(im.height*yy/6);q=max(12,round(min(im.size)*.07))
                if abs(x-im.width/2)<im.width*.12:continue
                b=(max(0,x-q),max(0,y-q),min(im.width,x+q),min(im.height,y+q))
                a=arr[b[1]:b[3],b[0]:b[2]];area=int((a>40).sum())
                if area>25:boxes.append((*b,'source_texture_patch',area))
    return boxes[:20]

def portrait_holes(frame):
    alpha=np.asarray(frame.getchannel('A'));solid=cv2.morphologyEx((alpha>25).astype('uint8'),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,l,s,c=cv2.connectedComponentsWithStats(1-solid,8);mask=np.zeros(alpha.shape,dtype='uint8');found=[]
    for side in [0,1]:
        valid=[]
        for i,(x,y,w,h,area) in enumerate(s[1:],1):
            cx,cy=c[i]
            if x<=0 or y<=0 or x+w>=frame.width or y+h>=frame.height:continue
            if area<frame.width*frame.height*.02:continue
            if (cx<frame.width*.28 if side==0 else cx>frame.width*.72):valid.append((int(area),i))
        if valid:
            _,i=max(valid);mask[l==i]=255;found.append(dict(side='left' if side==0 else 'right',area=int(s[i,4]),bbox=[int(v) for v in s[i,:4]]))
    return Image.fromarray(mask),found

def make_spec(a,im):
    key=a['id'][2:] if a['id'].startswith('D_') else a['id'];mode,num,end=PROFILES[key]
    seed=int(hashlib.sha256(('motion-v3/'+a['id']).encode()).hexdigest()[:12],16);rng=random.Random(seed)
    boxes=sprites(im);parts=[]
    for i in range(num):
        b=boxes[i%len(boxes)] if boxes else (0,0,im.width,im.height,'whole_texture_fallback',0)
        theta=2*math.pi*i/max(1,num)+rng.uniform(-.12,.12)
        parts.append(dict(index=i,uv_box=list(b[:4]),sprite_kind=b[4],birth_s=rng.uniform(0,.22),life_s=rng.uniform(.85,1.3),theta=theta,speed=rng.uniform(65,110),radius=rng.uniform(110,175),omega=rng.uniform(.8,1.6)*(-1 if i%2 else 1),size_px=rng.uniform(10,21),spin_deg=rng.uniform(-90,90),phase=rng.uniform(0,math.tau)))
    enter,hold,leave={'A':(.20,1.10,.15),'B':(.22,1,.18),'C':(.24,1,.18)}.get(a['id'],(.28,1.2,.22))
    return dict(id=a['id'],renderer_version=RENDER_VERSION,label=a['label'],source_number=a['source_number'],texture=a['output'],texture_sha256=a['sha256'],frame=a['reference'],frame_sha256=a['reference_sha256'],mode=mode,seed=seed,peak_texture_end_s=end,particles=parts,coordinate_contract=dict(canvas=[W,H],origin=[W/2,H/2],units='reference pixels; scale uniformly by actual frame width / 480',frame_width_px=480,effect_fit=[410,218]),timeline=dict(start_s=-.25,kill_s=0,end_s=2.35,fps=FPS,frame_enter_s=enter,frame_exit_start_s=enter+hold,frame_exit_end_s=enter+hold+leave,all_effects_zero_after_s=1.8),source_alpha_warnings=a['technical_warnings'],final_approved=False)

def position(p,t,mode):
    age=t-p['birth_s'];u=age/p['life_s']
    if u<0 or u>=1:return None
    th=p['theta'];r=p['radius'];v=p['speed'];phase=p['phase'];omega=p['omega']
    if mode in ['orbit','inward','star','arc']:
        radius=r*((1-u) if mode=='inward' else (.65+.35*u))
        ang=th+omega*age*(1.8 if mode=='arc' else 1)
        x=radius*math.cos(ang);y=.4*radius*math.sin(ang)-(22*age if mode=='star' else 0)
    elif mode=='petal':x=math.cos(th)*90+math.cos(th)*35*age+12*math.sin(4*age+phase);y=-35+34*age+18*age*age
    elif mode=='snow':x=math.cos(th)*190+10*math.sin(3*age+phase);y=-85+60*age
    elif mode=='water':x=math.cos(th)*v*age*1.25;y=math.sin(th)*35*age-36*age+55*age*age
    elif mode=='flame':x=math.cos(th)*70*age+7*math.sin(6*age+phase);y=15-v*.65*age-12*age*age
    elif mode=='dragon':x=math.cos(th)*v*age*1.3;y=42*math.sin(4*age+th)*math.sin(math.pi*u)
    elif mode=='brush':x=-90+145*u;y=math.sin(th)*58+15*math.sin(3*u+phase)
    elif mode=='scan':x=(-1 if p['index']%2 else 1)*(20+125*age);y=math.sin(th)*60
    elif mode=='beat':x=math.cos(th)*(25+v*age);y=math.sin(th)*45+8*math.sin(8*age+phase)
    elif mode=='slash':
        ang=(math.pi/4 if p['index']%2 else -math.pi/4)+(math.pi if p['index']%4>1 else 0)
        x=math.cos(ang)*v*age;y=math.sin(ang)*v*.5*age+28*age*age
    elif mode=='wing':x=math.cos(th)*v*age;y=-abs(math.sin(th))*65*age
    else:
        progress=min(age,.45) if mode=='lock' else age
        x=math.cos(th)*v*progress;y=math.sin(th)*v*.5*progress
    opacity=math.sin(math.pi*u)**2*.85;rotation=p['spin_deg']*u
    if mode=='pixel':x=round(x/5)*5;y=round(y/5)*5;opacity=round(opacity*4)/4;rotation=90*(p['index']%4)
    return [W/2+x,H/2+y,opacity,rotation]

def render_effect(im,small,sprite_images,spec,t):
    layer=Image.new('RGBA',(W,H));mode=spec['mode'];end=spec['peak_texture_end_s'];op=fade(t,end)*.75
    if op:
        progress=smooth(t/.18);cx=W/2;cy=H/2
        if mode in ['collision','wing','lock']:
            nx=2;ny=2 if mode=='lock' else 1
            for iy in range(ny):
                for ix in range(nx):
                    b=(ix*small.width//nx,iy*small.height//ny,(ix+1)*small.width//nx,(iy+1)*small.height//ny)
                    piece=small.crop(b);x=cx-small.width/2+(b[0]+b[2])/2;y=cy-small.height/2+(b[1]+b[3])/2
                    x+=(1-progress)*(52 if ix else -52);y+=(1-progress)*(18 if iy else -18) if ny==2 else 0
                    overlay(layer,piece,x,y,op)
        elif mode in ['glint','scan','brush','dragon']:
            overlay(layer,small,cx,cy,op*.3)
            yy,xx=np.mgrid[0:small.height,0:small.width];px=xx/small.width;py=yy/small.height
            if mode=='glint':mask=np.clip(1-np.abs(px-(t/.5))/.13,0,1)
            elif mode=='scan':mask=(np.mod(py*7+t*10,1)<.4).astype(float)*(px<min(1,math.floor(t/.035)/5))
            elif mode=='brush':mask=np.clip((t/.4-px)*9,0,1)
            else:mask=np.clip(1-np.abs(py-(.5+.2*np.sin(px*math.tau-t*8)))/.2,0,1)
            patch=small.copy();patch.putalpha(ImageChops.multiply(patch.getchannel('A'),Image.fromarray(np.uint8(mask*255))))
            overlay(layer,patch,cx,cy,min(1,op*1.2))
        else:
            scale=.85+.15*smooth(t/.12)+.08*max(0,t-.12)
            if mode=='beat':scale+=.035*math.sin(t*math.tau*6)*math.exp(-t*3);op*=.75+.25*math.cos(t*math.tau*6)**2
            if mode=='pixel':scale=round(scale*10)/10;op=round(op*4)/4
            overlay(layer,small,cx,cy,op,angle=(t*8 if mode in ['orbit','inward','arc'] else 0),scale=scale,nearest=mode=='pixel')
    if 0<=t<1.8:
        for p,sprite in zip(spec['particles'],sprite_images):
            pose=position(p,t,mode)
            if pose:overlay(layer,sprite,*pose[:2],pose[2],pose[3],nearest=mode=='pixel')
    return layer

def checker(size):
    a=np.indices((size[1],size[0])).sum(axis=0) # overwrite with square cells
    yy,xx=np.indices((size[1],size[0]));v=np.where(((xx//16+yy//16)%2)==0,38,51).astype('uint8')
    return Image.fromarray(np.dstack([v,v+3,v+8,np.full_like(v,255)]))

def produce(a):
    folder=OUT/a['id'];folder.mkdir(parents=True,exist_ok=True)
    assert digest(REPO/a['output'])==a['sha256'];assert digest(REPO/a['reference'])==a['reference_sha256']
    previous=folder/'motion.json'
    if previous.exists():
        saved=json.loads(previous.read_text(encoding='utf-8'))
        if saved.get('renderer_version')==RENDER_VERSION and saved['texture_sha256']==a['sha256'] and saved['frame_sha256']==a['reference_sha256'] and all(digest(REPO/q['file'])==q['sha256'] for q in saved['outputs']):
            return dict(id=a['id'],label=a['label'],source_number=a['source_number'],outputs=saved['outputs'],qa=saved['qa'],mode=saved['mode'])
    im=Image.open(REPO/a['output']).convert('RGBA');frame=Image.open(REPO/a['reference']).convert('RGBA')
    spec=make_spec(a,im);small=im.copy();small.thumbnail((410,218),Image.Resampling.LANCZOS)
    sprite_images=[]
    for p in spec['particles']:
        sprite=im.crop(p['uv_box']);sprite.thumbnail((round(p['size_px']),round(p['size_px'])),Image.Resampling.NEAREST if spec['mode']=='pixel' else Image.Resampling.LANCZOS);sprite_images.append(sprite)
    holes,found=portrait_holes(frame);f=frame.copy();f.thumbnail((480,215),Image.Resampling.LANCZOS);holes=holes.resize(f.size,Image.Resampling.NEAREST)
    protect=Image.new('L',(W,H));protect.paste(holes,((W-f.width)//2,(H-f.height)//2));spec['preview_portrait_holes']=found
    fontpath=Path('C:/Windows/Fonts/meiryo.ttc');font=ImageFont.truetype(str(fontpath),23);smallfont=ImageFont.truetype(str(fontpath),16)
    board=Image.new('RGBA',(1280,720),'#171d29');d=ImageDraw.Draw(board)
    d.text((35,20),a['label']+' / '+a['id'],font=font,fill='white');d.text((35,60),'元のキルフレーム',font=smallfont,fill='#d6dfed')
    ref=frame.copy();ref.thumbnail((750,220));board.alpha_composite(ref,((1280-ref.width)//2,85+(220-ref.height)//2))
    d.text((70,315),'エフェクト単体',font=smallfont,fill='white');d.text((710,315),'フレームと重ねた動き',font=smallfont,fill='white')
    for x in [64,704]:board.alpha_composite(checker((W,H)),(x,350))
    d.text((35,680),'確認用の動く見本 / 素材・本体コードの最終承認とは別です',font=smallfont,fill='#becbdd')
    ffmpeg=shutil.which('ffmpeg');mp4=folder/'comparison.mp4'
    cmd=[ffmpeg,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1280x720','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','21','-threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=[];hashes=[];edge_hits=0;extent=[]
    for k in range(COUNT):
        t=-.25+k/FPS;fx=render_effect(im,small,sprite_images,spec,t);frames.append(fx)
        alpha=np.asarray(fx.getchannel('A'));edge_hits+=int(np.count_nonzero(np.r_[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]))
        hashes.append(hashlib.sha256(fx.tobytes()).hexdigest())
        canvas=board.copy();canvas.alpha_composite(fx,(64,350));combined=Image.new('RGBA',(W,H))
        timing=spec['timeline'];exit_start=timing['frame_exit_start_s'];exit_duration=timing['frame_exit_end_s']-exit_start
        base_op=smooth(t/timing['frame_enter_s'])*(1-smooth((t-exit_start)/exit_duration)) if t>=0 else 0
        overlay(combined,f,W/2,H/2,base_op)
        masked=fx.copy();masked.putalpha(ImageChops.subtract(masked.getchannel('A'),protect));combined.alpha_composite(masked);canvas.alpha_composite(combined,(704,350))
        draw=ImageDraw.Draw(canvas);draw.rectangle((35,648,1245,655),fill='#354256');draw.rectangle((35,648,35+round(1210*k/(COUNT-1)),655),fill='#6cbbe8');draw.text((1080,20),f't={t:+.2f}s',font=smallfont,fill='white')
        proc.stdin.write(canvas.tobytes())
        if k==16:canvas.convert('RGB').save(folder/'poster.jpg',quality=92)
    proc.stdin.close();err=proc.stderr.read().decode(errors='replace');code=proc.wait()
    if code:raise RuntimeError(err)
    durations=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(COUNT)]
    webp=folder/'effect_alpha.webp';frames[0].save(webp,save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=88,method=3,minimize_size=False)
    decoded=Image.open(webp);duration=0
    for k in range(decoded.n_frames):decoded.seek(k);decoded.load();duration+=decoded.info.get('duration',0)
    capture=cv2.VideoCapture(str(mp4));video_frames=int(capture.get(cv2.CAP_PROP_FRAME_COUNT));video_fps=float(capture.get(cv2.CAP_PROP_FPS));capture.release()
    assert video_frames==COUNT and abs(video_fps-FPS)<.01
    assert duration==2600 and decoded.n_frames>10
    assert frames[0].getbbox() is None and frames[-1].getbbox() is None
    assert len(set(hashes))>(5 if spec['mode']=='minimal' else 20),a['id']
    # Random access must not depend on previous frames.
    assert render_effect(im,small,sprite_images,spec,.37).tobytes()==render_effect(im,small,sprite_images,spec,.37).tobytes()
    spec['qa']=dict(mp4_frames=video_frames,fps=video_fps,duration_ms=duration,webp_frames=decoded.n_frames,unique_effect_frames=len(set(hashes)),outer_edge_nonzero_samples=edge_hits,portrait_holes_detected=len(found),zero_before_and_after=True,deterministic_random_access=True,native_png_alpha_warning_retained=bool(a['technical_warnings']),final_approved=False)
    spec['outputs']=[dict(file=str(q.relative_to(REPO)).replace('\\','/'),bytes=q.stat().st_size,sha256=digest(q)) for q in [mp4,webp,folder/'poster.jpg']]
    (folder/'motion.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(id=a['id'],label=a['label'],source_number=a['source_number'],outputs=spec['outputs'],qa=spec['qa'],mode=spec['mode'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
    data=json.loads((ROOT/'effect_assets/frame_based_review_v2/production.json').read_text(encoding='utf-8'))['assets'];OUT.mkdir(exist_ok=True)
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks={pool.submit(produce,a):a['id'] for a in data}
        for task in as_completed(tasks):
            r=task.result();results.append(r);print(r['id']+' completed',flush=True)
    results.sort(key=lambda a:a['id']);(OUT/'catalog.json').write_text(json.dumps(dict(count=len(results),fps=FPS,duration_ms=2600,status='motion_design_review',final_approved=0,assets=results),ensure_ascii=False,indent=2),encoding='utf-8')
    print('ALL 35 COMPLETED',flush=True)
if __name__=='__main__':main()
