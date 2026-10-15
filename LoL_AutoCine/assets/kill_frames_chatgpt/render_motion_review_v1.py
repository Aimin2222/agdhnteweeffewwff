"""Offline motion design proofs; no application integration."""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import hashlib,json,math,random
import numpy as np
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
catalog_path=ROOT/'effect_specs/review_v1/animation_catalog.json'
catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def opacity(im,g):
    p=im.copy();p.putalpha(p.getchannel('A').point(lambda a:round(a*max(0,min(1,g)))));return p
def paste(canvas,im,x,y):canvas.alpha_composite(im,(round(x),round(y)))
for spec in catalog['specs']:
    source=Image.open(REPO/spec['layers']['ornament']).convert('RGBA');source.thumbnail((500,190))
    glow=Image.open(REPO/spec['layers']['glow']).convert('RGBA');glow.thumbnail((548,238))
    tiles=[]
    for rec in spec['layers']['particles']:
        im=Image.open(REPO/rec['file']).convert('RGBA');im.thumbnail((18,18));tiles.append(im)
    enter=spec['timing_seconds']['enter'];hold=spec['timing_seconds']['hold'];leave=spec['timing_seconds']['exit'];end=enter+hold+leave
    total=end+.12;count=32;times=np.linspace(-.12,end,count)
    frames=[];keyframes=[]
    for fi,t in enumerate(times):
        canvas=Image.new('RGBA',(640,320));p=smooth(t/enter);q=smooth((t-enter-hold)/leave);g=p*(1-q)
        scale=.92+.08*p
        if spec['motion']=='disco_bounce':scale+=.06*math.sin(math.pi*p)*math.exp(-3*p)
        if spec['motion'] in ['pixel_steps','stutter_scan']:g=math.floor(g*4)/4
        im=source.resize((max(1,round(source.width*scale)),max(1,round(source.height*scale))),Image.Resampling.LANCZOS)
        im=opacity(im,g);x=(640-im.width)/2;y=(320-im.height)/2
        if spec['family']=='A':
            mid=im.width//2;paste(canvas,im.crop((0,0,mid,im.height)),x-32*(1-p),y);paste(canvas,im.crop((mid,0,im.width,im.height)),x+mid+32*(1-p),y)
        elif spec['family']=='C':
            mid=im.width//2;paste(canvas,im.crop((0,0,mid,im.height)),x-48*(1-p),y);paste(canvas,im.crop((mid,0,im.width,im.height)),x+mid+48*(1-p),y)
        elif spec['motion'] in ['wing_open','wing_snap','mechanical_lock','four_piece_lock','piston_impact']:
            mid=im.width//2;paste(canvas,im.crop((0,0,mid,im.height)),x-24*(1-p),y);paste(canvas,im.crop((mid,0,im.width,im.height)),x+mid+24*(1-p),y)
        elif spec['motion'] in ['horizontal_scan','ink_reveal','stutter_scan']:
            limit=max(0,min(im.width,round(im.width*p)));paste(canvas,im.crop((0,0,limit,im.height)),x,y)
        else:paste(canvas,im,x,y)
        peak=spec['glow_peak'];gain=peak*math.sin(math.pi*p)*(1-q) if t<enter else peak*.12*(1-q)
        if -.12<t<0:gain=.08*smooth((t+.12)/.12)
        if t>=end:gain=0
        if spec['family']=='B' or spec['motion']=='glint_travel':
            ga=np.asarray(glow.getchannel('A')).copy();xx=np.arange(glow.width);band=np.exp(-((xx-glow.width*p)/12)**2);ga=np.uint8(ga*band[None,:]);gim=glow.copy();gim.putalpha(Image.fromarray(ga));paste(canvas,opacity(gim,.6*(1-q)),(640-glow.width)/2,(320-glow.height)/2)
        else:paste(canvas,opacity(glow,gain),(640-glow.width)/2,(320-glow.height)/2)
        seed=int.from_bytes(hashlib.sha256(spec['id'].encode()).digest()[:8],'big');rng=random.Random(seed)
        n=spec['particle_count'];motion=spec['motion']
        for i in range(n if tiles else 0):
            theta=2*math.pi*i/max(1,n)+rng.random()*.25;birth=rng.random()*.10;age=t-birth;life=spec.get('particle_lifetime_s',.5)
            if age<0 or age>=life:continue
            a=age/life;rot=spec.get('rotation_degrees',20)*math.pi/180*a;vx,vy=spec.get('particle_velocity_px_s',[70,0]);radius=24+abs(vx)*age
            if 'inward' in motion:radius=80*(1-a)
            xx=320+radius*math.cos(theta+rot);yy=160+.45*radius*math.sin(theta+rot)
            if motion in ['petal_sine','leaf_spiral','butterfly_flap','snowfall']:
                xx+=12*math.sin(2*math.pi*a+theta);yy+=vy*age
            elif motion in ['ballistic_drops','outward_sparks','glass_radial','ink_reveal']:yy+=vy*age+60*age*age
            elif motion=='dragon_curve':xx=320+vx*age*math.cos(theta);yy=160+22*math.sin(2*math.pi*a+theta)+vy*age
            elif motion in ['ember_rise','flame_rise','witch_arc']:yy+=vy*age
            elif motion=='disco_bounce':yy+=18*abs(math.sin(3*math.pi*a))
            elif motion in ['horizontal_scan','stutter_scan']:xx=320+(i%2*2-1)*(24+abs(vx)*age)
            tile=tiles[i%len(tiles)].rotate(spec.get('rotation_degrees',0)*a,resample=Image.Resampling.BICUBIC,expand=True)
            fade=math.sin(math.pi*a)**2*.7;paste(canvas,opacity(tile,fade),xx-tile.width/2,yy-tile.height/2)
        # Suppress all proof layers over measured portrait holes.
        source_rec=next(r for r in json.loads((ROOT/'original_alpha/review_v1/inventory.json').read_text(encoding='utf-8'))['assets'] if r['file']==spec['layers']['source_record']) if fi==0 else source_rec
        clear=Image.new('L',canvas.size);draw=ImageDraw.Draw(clear)
        sx=im.width/source_rec['dimensions'][0];sy=im.height/source_rec['dimensions'][1];box=source_rec['crop_box']
        for hole in source_rec['portrait_holes']:
            kind,values=next(iter(hole.items()))
            pts=np.asarray(values).reshape(-1,2);pts=(pts-np.array(box[:2]))*np.array([sx,sy])+np.array([x,y])
            shift=0
            if spec['family'] in ['A','C'] or spec['motion'] in ['wing_open','wing_snap','mechanical_lock','four_piece_lock','piston_impact']:
                amount=32 if spec['family']=='A' else 48 if spec['family']=='C' else 24
                shift=(-1 if pts[:,0].mean()<320 else 1)*amount*(1-p)
            pts[:,0]+=shift
            if kind=='polygon':draw.polygon([tuple(v) for v in pts],fill=255)
            else:getattr(draw,kind)(tuple(pts.reshape(-1)),fill=255)
        canvas.putalpha(ImageChops.multiply(canvas.getchannel('A'),ImageChops.invert(clear)))
        if t>=end:canvas=Image.new('RGBA',(640,320))
        frames.append(canvas)
    out=(REPO/spec['timing_preview']).parent
    duration=max(1,round(total*1000/(count-1)))
    frames[0].save(out/'motion_preview.webp',save_all=True,append_images=frames[1:],duration=duration,loop=0,lossless=True)
    for idx in [0,2,6,10,23,31]:frames[idx].save(out/f'motion_key_{idx:02}.png')
    # Still proof on both light and dark backgrounds, no captions in actual PNGs.
    proof=Image.new('RGB',(1280,320*3),'#888888')
    for row,idx in enumerate([6,10,23]):
        for col,color in enumerate(['white','black']):
            bg=Image.new('RGBA',(640,320),color);bg.alpha_composite(frames[idx]);proof.paste(bg.convert('RGB'),(col*640,row*320))
    proof.save(out/'motion_comparison.jpg',quality=94)
    spec.update(motion_preview=(out/'motion_preview.webp').relative_to(REPO).as_posix(),preview_scope='Offline draft motion with source ornament, derived glow and source-fragment particles. Not GPU/game integration or final QA.')
    if spec['id'] in ['A','B','C','D']:target=ROOT/f'abcd_designs/review_v1/{spec["id"]}/design.json'
    else:target=ROOT/f'effect_specs/review_v1/D/{spec["theme"]}.json'
    target.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(spec['id'],flush=True)
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
