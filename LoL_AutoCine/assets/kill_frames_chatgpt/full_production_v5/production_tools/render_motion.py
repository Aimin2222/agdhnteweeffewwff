"""Offline frame-derived VFX design renderer; no AutoCine app imports or edits.

Renders motion from immutable frame PNGs using native texture UV fragments and
procedural light trails. Does not clean, repaint, or overwrite source art.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageChops
from concurrent.futures import ProcessPoolExecutor,as_completed
from functools import lru_cache
from itertools import permutations
import json,hashlib,math,random,subprocess,shutil,sys
import numpy as np,cv2

ROOT=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
FPS=30;COUNT=90;DURATION_MS=3000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)

def profile(theme):
    if theme in ['a_simple','a1_simple']:return 'minimal'
    if theme=='c2_arcane_collision':return 'collision'
    groups={
      'petal':['elderwood','spirit_blossom','faerie_court','forest_spirit','ionia','ixtal','spirit_flower','d_spirit_blossom','d4_vastaya'],
      'snow':['winter_festival','freljord','frosted'],
      'scan':['project','psyops','pulsefire','piltover','d_project'],
      'lock':['mecha','mecha_kingdoms','steel_valkyries','battlecast','mechanical_clock'],
      'flame':['infernal','nightbringer','noxus','sun_crown'],
      'water':['pool_party','ocean_song','bilgewater'],
      'pixel':['arcade'],
      'orbit':['cosmic','odyssey','space_groove','space_journey','targon'],
      'inward':['dark_star','dark_cosmic','void','black_mist','shadow_isles','ruined','deep_sea_horror'],
      'star':['star_guardian','moon_goddess','empyrean'],
      'wing':['dawnbringer','demacia','victorious','d_ornate'],
      'beat':['kda','heartsteel','battle_academia'],
      'arc':['blood_moon','blood_moon_ritual','bewitching','arcana','coven','d_blood_moon'],
      'slash':['high_noon','warring_kingdoms','broken_covenant','soul_fighter','c_cinema','c1_slash_burst','c2_arcane_collision'],
      'dragon':['dragonmancer','dragon_world','dragon_will','dragon_emperor'],
      'brush':['shan_hai_scrolls','shurima','desert_empire'],
    }
    for key,themes in groups.items():
        if theme in themes:return key
    return 'glint'

def holes(im):
    alpha=np.array(im.getchannel('A'));solid=cv2.morphologyEx((alpha>25).astype('uint8'),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,l,s,c=cv2.connectedComponentsWithStats(1-solid,8);mask=np.zeros(alpha.shape,'uint8');out=[]
    for side in [0,1]:
        candidates=[]
        for i,(x,y,w,h,area) in enumerate(s[1:],1):
            cx,cy=c[i]
            if x<=0 or y<=0 or x+w>=im.width or y+h>=im.height or area<im.width*im.height*.015:continue
            if (cx<im.width*.35 if side==0 else cx>im.width*.65):candidates.append((int(area),i))
        if candidates:
            _,i=max(candidates);mask[l==i]=255;out.append(dict(side=side,bbox=[int(v) for v in s[i,:4]],area=int(s[i,4])))
    return Image.fromarray(mask),out

def palette(im,alpha_threshold=180):
    ar=np.asarray(im);rgb=ar[:,:,:3];sel=(ar[:,:,3]>alpha_threshold)&(rgb.max(axis=2)>150)&(rgb.max(axis=2)-rgb.min(axis=2)>35)
    pixels=rgb[sel]
    if len(pixels)<20:
        visible=rgb[(ar[:,:,3]>alpha_threshold)&(rgb.max(axis=2)>90)]
        if len(visible)<3:return [[210,210,210],[240,240,240],[255,255,255]]
        ordered=visible[np.argsort(visible.max(axis=1))]
        return [ordered[round((len(ordered)-1)*q)].tolist() for q in [.25,.65,.95]]
    bins=(pixels//32).astype('int32');ids=bins[:,0]*64+bins[:,1]*8+bins[:,2];counts=np.bincount(ids,minlength=512)
    chosen=[]
    for k in np.argsort(counts)[::-1]:
        if counts[k]==0:break
        color=np.median(pixels[ids==k],axis=0).astype('int32')
        if all(np.linalg.norm(color-np.array(q))>60 for q in chosen):chosen.append(color.tolist())
        if len(chosen)==3:break
    while len(chosen)<3:chosen.append([240,245,255])
    return chosen

def make_spec_base(a,im):
    seed=int(hashlib.sha256(('frame-native-v5/'+a['key']).encode()).hexdigest()[:12],16);rng=random.Random(seed)
    mode=profile(a['theme']);strength=.62 if a['intensity']=='weak' else 1.0 if a['intensity']=='strong' else .8
    alpha=np.asarray(im.getchannel('A'));boxes=[];kinds=[];size=max(18,round(min(im.size)*.08))
    n,labels,stats,centroids=cv2.connectedComponentsWithStats((alpha>40).astype('uint8'),8)
    for x,y,w,h,area in sorted(stats[1:],key=lambda v:-v[4]):
        if 20<=area<=im.width*im.height*.002 and 5<=w<im.width*.14 and 5<=h<im.height*.3:
            boxes.append([max(0,int(x)-5),max(0,int(y)-5),min(im.width,int(x+w)+5),min(im.height,int(y+h)+5)])
            kinds.append('detached_alpha_component')
        if len(boxes)>=12:break
    # Explicitly source texture patches, never certified complete independent petals.
    for fy in [.20,.35,.50,.65,.80]:
        for fx in [.36,.43,.50,.57,.64]:
            x,y=round(im.width*fx),round(im.height*fy);b=[max(0,x-size),max(0,y-size),min(im.width,x+size),min(im.height,y+size)]
            v=alpha[b[1]:b[3],b[0]:b[2]]
            if np.count_nonzero(v>64)>v.size*.08:boxes.append(b);kinds.append('source_texture_patch')
    if not boxes:boxes=[[round(im.width*.42),round(im.height*.3),round(im.width*.58),round(im.height*.7)]];kinds=['source_texture_patch']
    particles=[]
    count=0 if mode=='minimal' else 12 if mode=='glint' else round(22*strength)+8
    for i in range(count):
        kind=kinds[i%len(boxes)]
        particles.append(dict(index=i,uv_box=boxes[i%len(boxes)],sprite_kind=kind,uv_window='ellipse_feather' if kind=='source_texture_patch' and mode!='pixel' else 'none',theta=math.tau*i/max(1,count)+rng.uniform(-.12,.12),birth_s=rng.uniform(0,.18),life_s=rng.uniform(.85,1.45),speed=rng.uniform(65,115)*strength,radius=rng.uniform(75,160),phase=rng.uniform(0,math.tau),spin_deg=rng.uniform(-110,110),size_px=rng.uniform(8,17)*strength))
    if a['theme'] in ['a_simple','a1_simple']:enter,hold,leave=.20,1.10,.15
    elif a['theme'] in ['b_prestige','b1_royal_gold','b2_blue_silver','a2_glass']:enter,hold,leave=.22,1.0,.18
    elif a['theme'] in ['c_cinema','c1_slash_burst','c2_arcane_collision']:enter,hold,leave=.24,1.0,.18
    else:enter,hold,leave=.28,1.2,.22
    return dict(version='frame-native-v5.2',key=a['key'],source_number=a['number'],theme=a['theme'],mode=mode,strength=strength,frame=a['output'],frame_sha256=sha(Path(a['output'])),reference=a['reference'],reference_sha256=a['reference_sha256'],palette=palette(im),seed=seed,particles=particles,coordinate_contract=dict(reference_canvas=[512,288],origin=[256,144],frame_width_px=460,scale_rule='Multiply positions, sizes and speeds by target width / 512'),timeline=dict(start_s=-.30,kill_s=0,end_s=2.70,fps=FPS,frame_enter_s=enter,hold_s=hold,frame_exit_start_s=enter+hold,frame_exit_end_s=enter+hold+leave,effects_zero_after_s=.45 if mode=='minimal' else 2.2),method='Code-native particle motion from unchanged native frame texture UVs plus procedural light; not newly AI-painted FX textures',source_partial=a['source_partial'],quality_flags=a.get('quality_flags',[]),final_approved=False)

def make_spec(a,im):
    spec=make_spec_base(a,im);spec['version']='frame-native-v5.4'
    spec['timeline']['pre_effect_start_s']=-.18 if spec['mode'] in ['collision','scan','flame','inward','lock'] else 0
    spec['uv_window_contract']='For ellipse_feather multiply sampled alpha by clamp((1-x*x-y*y)/0.35,0,1), UV x/y in [-1,1]; immutable source texture.'
    entry=select_shared_fx(a['theme'],spec['mode'])
    if entry:
        assert sha(Path(entry['output']))==entry['sha256']
        source_palette=shared_palette(entry['output']);sp=np.asarray(source_palette,dtype='float32');sp/=np.maximum(sp.max(axis=1,keepdims=True),1)
        tp=np.asarray(spec['palette'],dtype='float32');tp/=np.maximum(tp.max(axis=1,keepdims=True),1)
        order=min(permutations(range(3)),key=lambda order:float(((sp-tp[list(order)])**2).sum()))
        spec['base_fx']=dict(id=entry['id'],texture=entry['output'],sha256=entry['sha256'],palette_mapping='native_rgb' if spec['mode']=='pixel' else 'soft_chroma_3_anchor_preserve_neutral_white',source_palette=source_palette,target_palette=[spec['palette'][i] for i in order],source_texture_quality_warnings=entry.get('technical_warnings',[]),sample_alpha_floor_u8=2,end_s=(.65 if spec['mode']=='glint' else 1.25)*(.85 if a['intensity']=='weak' else 1),opacity=.72*spec['strength'])
    spec['side_palette']=dict(left=palette(im.crop((0,0,round(im.width*.35),im.height)))[0],right=palette(im.crop((round(im.width*.65),0,im.width,im.height)))[0])
    spec['method']='Immutable native frame UV particles plus selected existing AI theme VFX textures, per-frame palette material, and code-native animation. Shared sources unchanged.'
    spec['glow_contract']='Blur premultiplied RGBA, then unpremultiply for straight-alpha output.'
    return spec

@lru_cache(maxsize=1)
def shared_catalog():
    path=ROOT.parent/'effect_assets/frame_based_review_v2/production.json'
    return {a['id']:a for a in json.loads(path.read_text(encoding='utf-8'))['assets']}

def select_shared_fx(theme,mode):
    if mode=='minimal':return None
    catalog=shared_catalog();exact='D_'+theme
    family={'petal':'D_spirit_blossom','snow':'D_winter_festival','scan':'D_project','lock':'D_mecha','flame':'D_infernal','water':'D_pool_party','pixel':'D_arcade','orbit':'D_cosmic','inward':'D_dark_star','star':'D_star_guardian','wing':'D_dawnbringer','beat':'D_kda','arc':'D_blood_moon','slash':'C','collision':'C','dragon':'D_dragonmancer','brush':'D_shan_hai_scrolls','glint':'B'}
    return catalog.get(exact) or catalog.get(family.get(mode,'B'))

@lru_cache(maxsize=64)
def shared_palette(path):return palette(Image.open(path).convert('RGBA'),32)

@lru_cache(maxsize=8)
def shared_material(path,target_tuple,mapping):
    raw=Image.open(path).convert('RGBA')
    if mapping=='native_rgb':
        raw.putalpha(raw.getchannel('A').point(lambda a:0 if a<=2 else a));return raw
    array=np.asarray(raw);rgb=array[:,:,:3].astype('float32')/255;value=rgb.max(axis=2)
    chroma=rgb/np.maximum(value[:,:,None],1e-6)
    anchors=np.asarray(palette(raw,32),dtype='float32')/255;anchors=anchors/np.maximum(anchors.max(axis=1,keepdims=True),1e-6)
    target=np.asarray(target_tuple,dtype='float32').reshape(3,3)/255;target=target/np.maximum(target.max(axis=1,keepdims=True),1e-6)
    dist=((chroma[:,:,None,:]-anchors[None,None,:,:])**2).sum(axis=3)
    weights=1/(dist+.06)**2;weights/=weights.sum(axis=2,keepdims=True)
    mapped=np.einsum('hwk,kc->hwc',weights,target)*value[:,:,None]
    neutral=np.clip((rgb.min(axis=2)/np.maximum(value,1e-6)-.78)/.22,0,1)
    mapped=mapped*(1-neutral[:,:,None])+value[:,:,None]*neutral[:,:,None]
    result=np.dstack([np.uint8(np.clip(mapped,0,1)*255),np.where(array[:,:,3]<=2,0,array[:,:,3]).astype('uint8')])
    return Image.fromarray(result)

def glow_filter(image,radius):
    ar=np.asarray(image,dtype='float32')/255;premul=ar.copy();premul[:,:,:3]*=premul[:,:,3:4]
    blurred=np.asarray(Image.fromarray(np.uint8(np.clip(premul,0,1)*255)).filter(ImageFilter.GaussianBlur(radius)),dtype='float32')/255
    color=np.divide(blurred[:,:,:3],blurred[:,:,3:4],out=np.zeros_like(blurred[:,:,:3]),where=blurred[:,:,3:4]>0)
    return Image.fromarray(np.uint8(np.clip(np.dstack([color,blurred[:,:,3]]),0,1)*255))

def shared_layer(spec,t,width):
    scale=width/512;out=Image.new('RGBA',(width,round(288*scale)));base=spec.get('base_fx')
    if not base or t<0 or t>=base['end_s']:return out
    op=smooth(t/.06)*(1-smooth((t-.13)/max(.01,base['end_s']-.13)))*base['opacity'];mode=spec['mode']
    material=shared_material(base['texture'],tuple(v for c in base['target_palette'] for v in c),base['palette_mapping'])
    small=material.copy();small.thumbnail((round(410*scale),round(218*scale)),Image.Resampling.NEAREST if mode=='pixel' else Image.Resampling.LANCZOS)
    cx,cy=width/2,out.height/2;progress=smooth(t/.18)
    if mode in ['collision','wing','lock']:
        nx,ny=2,2 if mode=='lock' else 1
        for iy in range(ny):
            for ix in range(nx):
                x0=round(small.width*ix/nx);x1=round(small.width*(ix+1)/nx);y0=round(small.height*iy/ny);y1=round(small.height*(iy+1)/ny)
                patch=small.crop((x0,y0,x1,y1));direction=-1 if ix==0 else 1
                distance=(50*(1-progress) if mode in ['collision','lock'] else 15*progress)*scale
                px=cx-small.width/2+(x0+x1)/2+direction*distance
                py=cy-small.height/2+(y0+y1)/2+((-1 if iy==0 else 1)*25*(1-progress)*scale if mode=='lock' else 0)
                put(out,patch,px,py,op)
    elif mode in ['scan','glint','brush','dragon']:
        yy,xx=np.indices((small.height,small.width));u=xx/max(1,small.width-1)
        if mode=='glint':mask=np.clip(1-abs(u-((t/.5)%1))/.20,0,1)
        elif mode=='brush':mask=np.clip((progress-u)/.10,0,1)
        elif mode=='dragon':mask=np.clip(1-abs(yy/max(1,small.height-1)-(.5+.22*np.sin(u*math.tau-t*8)))/.30,0,1)
        else:
            rows=np.minimum(6,(yy*7/max(1,small.height)).astype('int32'));mask=np.clip((t-.025*rows)/.15-u*.45,0,1)*1.8;mask=np.clip(mask,0,1)
        small.putalpha(ImageChops.multiply(small.getchannel('A'),Image.fromarray(np.uint8(mask*255))));put(out,small,cx,cy,op)
    else:
        zoom=.86+.14*progress+(.07*t if mode!='inward' else -.12*t)
        if mode=='beat':zoom+=.025*math.sin(t*math.tau*3);op*=.9+.1*math.cos(t*math.tau*3)
        if mode=='pixel':zoom=round(zoom*8)/8;op=round(op*5)/5
        size=(max(1,round(small.width*zoom)),max(1,round(small.height*zoom)))
        put(out,small,cx,cy+(-10*t*scale if mode=='flame' else 8*t*scale if mode=='water' else 0),op,t*10 if mode in ['orbit','inward','arc'] else 0,size,pixel=mode=='pixel')
    return out

def pose(p,t,mode):
    age=t-p['birth_s'];u=age/p['life_s']
    if u<0 or u>=1:return None
    th=p['theta'];v=p['speed'];phase=p['phase']
    if mode in ['orbit','inward','star','arc']:
        r=p['radius']*((1-u) if mode=='inward' else .45+.55*u);angle=th+age*(1.5 if mode=='arc' else .9)
        x=r*math.cos(angle);y=.42*r*math.sin(angle)-(20*age if mode=='star' else 0)
    elif mode=='petal':x=math.cos(th)*95+16*math.sin(4*age+phase)+math.cos(th)*30*age;y=-50+42*age+22*age*age
    elif mode=='snow':x=math.cos(th)*165+10*math.sin(3*age+phase);y=-70+70*age
    elif mode=='water':x=math.cos(th)*v*age*1.2;y=math.sin(th)*35*age-32*age+48*age*age
    elif mode=='flame':x=math.cos(th)*65*age+9*math.sin(5*age+phase);y=15-v*.7*age-10*age*age
    elif mode=='scan':x=(-1 if p['index']%2 else 1)*(15+120*age);y=math.sin(th)*60
    elif mode=='dragon':x=math.cos(th)*v*age*1.2;y=40*math.sin(4*age+th)*math.sin(math.pi*u)
    elif mode=='brush':x=-105+185*u;y=math.sin(th)*50+12*math.sin(3*u+phase)
    elif mode=='wing':x=math.cos(th)*v*age;y=-abs(math.sin(th))*65*age
    elif mode=='beat':x=math.cos(th)*(20+v*age);y=math.sin(th)*50+8*math.sin(8*age+phase)
    elif mode=='slash':
        ang=(math.pi/4 if p['index']%2 else -math.pi/4)+(math.pi if p['index']%4>1 else 0)
        x=math.cos(ang)*v*age;y=math.sin(ang)*v*.6*age+22*age*age
    else:
        progress=min(age,.5) if mode=='lock' else age;x=math.cos(th)*v*progress;y=math.sin(th)*v*.55*progress
    op=math.sin(math.pi*u)**2*.86;angle=p['spin_deg']*u
    if mode=='pixel':x=round(x/6)*6;y=round(y/6)*6;op=round(op*4)/4;angle=90*(p['index']%4)
    return 256+x,144+y,op,angle

def put(dst,im,x,y,opacity=1,angle=0,size=None,pixel=False):
    if opacity<=0:return
    sprite=im
    if size:sprite=im.resize(size,Image.Resampling.NEAREST if pixel else Image.Resampling.LANCZOS)
    if angle:sprite=sprite.rotate(angle,resample=Image.Resampling.NEAREST if pixel else Image.Resampling.BICUBIC,expand=True)
    if opacity<1:
        sprite=sprite.copy();sprite.putalpha(sprite.getchannel('A').point(lambda a:round(a*max(0,min(1,opacity)))))
    dst.alpha_composite(sprite,(round(x-sprite.width/2),round(y-sprite.height/2)))

def effect(frame,spec,t,width=512):
    scale=width/512;height=round(288*scale);out=Image.new('RGBA',(width,height))
    if t<spec['timeline']['pre_effect_start_s'] or t>=spec['timeline']['effects_zero_after_s']:return out
    if t<0:
        u=smooth((t+.18)/.18);glow=math.sin(math.pi*u)*.30;layer=Image.new('RGBA',out.size);d=ImageDraw.Draw(layer)
        for side in [-1,1]:
            x=256+side*(145*(1-u)+15);y=144+side*12
            color=spec['side_palette']['left' if side<0 else 'right']
            d.line(((x+side*45)*scale,y*scale,x*scale,y*scale),fill=(*color,round(255*glow)),width=max(1,round(2*scale)))
        out.alpha_composite(glow_filter(layer,4*scale));out.alpha_composite(layer);return out
    out.alpha_composite(shared_layer(spec,t,width))
    mode=spec['mode'];op=smooth(t/.06)*(1-smooth((t-.12)/.8))*spec['strength'];center=(width/2,height/2)
    if mode=='minimal':op=smooth(t/.04)*(1-smooth((t-.10)/.32))*.4
    elif spec.get('base_fx'):op*=.30
    lines=Image.new('RGBA',out.size);d=ImageDraw.Draw(lines)
    if op>0:
        # Separate luminous trails, no full-canvas color wash or portrait rings.
        for i in range(0 if mode=='minimal' else 18 if mode=='pixel' else 6 if mode=='glint' else 12):
            color=spec['palette'][i%3];th=math.tau*i/12;r=40+145*smooth(t/.4)
            if mode=='scan':pts=[(-165+25*i,-55+(i%6)*20),(165-10*i,-55+(i%6)*20)]
            elif mode=='collision':
                side=-1 if i%2 else 1;dist=155*(1-smooth(t/.16));pts=[(side*(dist+48),-18+(i%6)*7),(side*dist,-18+(i%6)*7)];color=spec['side_palette']['left' if side<0 else 'right']
            elif mode in ['slash','wing']:pts=[(math.cos(th)*25,math.sin(th)*15),(math.cos(th)*r,math.sin(th)*r*.42-(20 if mode=='wing' else 0))]
            elif mode=='pixel':
                x=round(math.cos(th)*r/7)*7;y=round(math.sin(th)*r*.4/7)*7;q=3*scale;d.rectangle((center[0]+x*scale-q,center[1]+y*scale-q,center[0]+x*scale+q,center[1]+y*scale+q),fill=(*color,round(190*op)));continue
            else:
                pts=[(math.cos(th+u*.28)*r*(.45+.55*u),math.sin(th+u*.28)*r*.36+8*math.sin(u*math.pi)) for u in [j/8 for j in range(9)]]
            pts=[(center[0]+x*scale,center[1]+y*scale) for x,y in pts]
            d.line(pts,fill=(*color,round(180*op)),width=max(1,round(scale*(1.2 if mode!='brush' else 2.4))))
        core=round(10*scale*op)
        d.line((center[0]-core*3,center[1],center[0]+core*3,center[1]),fill=(245,250,255,round(210*op)),width=max(1,round(scale)))
        d.line((center[0],center[1]-core,center[0],center[1]+core),fill=(245,250,255,round(180*op)),width=max(1,round(scale)))
        out.alpha_composite(glow_filter(lines,3.5*scale));out.alpha_composite(lines)
    for p in spec['particles']:
        loc=pose(p,t,mode)
        if not loc:continue
        sprite=frame.crop(p['uv_box'])
        sprite.putalpha(sprite.getchannel('A').point(lambda a:0 if a<=2 else a))
        if p.get('uv_window')=='ellipse_feather':
            yy,xx=np.mgrid[-1:1:complex(sprite.height),-1:1:complex(sprite.width)];window=np.clip((1-xx*xx-yy*yy)/.35,0,1)
            sprite.putalpha(Image.fromarray(np.uint8(np.asarray(sprite.getchannel('A'))*window)))
        q=max(1,round(p['size_px']*scale));sprite.thumbnail((q,q),Image.Resampling.NEAREST if mode=='pixel' else Image.Resampling.LANCZOS)
        put(out,sprite,loc[0]*scale,loc[1]*scale,loc[2],loc[3],pixel=mode=='pixel')
    return out

def checker(size):
    yy,xx=np.indices((size[1],size[0]));v=np.where(((xx//18+yy//18)%2)==0,40,52).astype('uint8');return Image.fromarray(np.dstack([v,v+2,v+6,np.full_like(v,255)]))

def reusable_motion(folder,digest):
    prior=folder/'motion.json'
    if not prior.exists():return False
    try:
        previous=json.loads(prior.read_text(encoding='utf-8'))
        return previous.get('version')=='frame-native-v5.4' and previous['frame_sha256']==digest and all(sha(Path(x['file']))==x['sha256'] for x in previous['outputs'])
    except (OSError,KeyError,ValueError):return False

def output_folder(a):
    digest=sha(Path(a['output']))
    canonical=ROOT/'motion'/a['number']/a['id']
    if reusable_motion(canonical,digest):return canonical
    base=ROOT/'motion_versions'/a['number']
    name=a['id']+'.'+digest[:16]
    folder=base/name;attempt=1
    while folder.exists():
        if reusable_motion(folder,digest):return folder
        attempt+=1;folder=base/(name+'_'+str(attempt))
    return folder

def produce(a):
    folder=output_folder(a);folder.mkdir(parents=True,exist_ok=True)
    prior=folder/'motion.json'
    if prior.exists():
        previous=json.loads(prior.read_text(encoding='utf-8'))
        if previous.get('version')=='frame-native-v5.4' and previous['frame_sha256']==sha(Path(a['output'])) and all(sha(Path(x['file']))==x['sha256'] for x in previous['outputs']):return dict(key=a['key'],outputs=previous['outputs'],qa=previous['qa'])
    frame=Image.open(a['output']).convert('RGBA');spec=make_spec(a,frame)
    hole_mask,found=holes(frame);f=frame.copy();f.thumbnail((460,205),Image.Resampling.LANCZOS);hole_mask=hole_mask.resize(f.size,Image.Resampling.NEAREST)
    protect=Image.new('L',(512,288));protect.paste(hole_mask,((512-f.width)//2,(288-f.height)//2));spec['portrait_holes']=found
    spec['portrait_mask_is_preview_estimate']=True
    font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',23);sm=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',16)
    board=Image.new('RGBA',(1280,720),'#171d29');d=ImageDraw.Draw(board)
    d.text((28,18),a['key']+' / '+a['theme'],font=font,fill='white');d.text((28,56),'原本をもとに生成したキルフレーム',font=sm,fill='#d0daea')
    ref=frame.copy();ref.thumbnail((950,218),Image.Resampling.LANCZOS);board.alpha_composite(ref,((1280-ref.width)//2,87+(218-ref.height)//2))
    d.text((64,317),'エフェクト単体',font=sm,fill='white');d.text((704,317),'フレームと重ねた動き',font=sm,fill='white')
    for x in [64,704]:board.alpha_composite(checker((512,288)),(x,350))
    d.text((28,684),'確認版 / 原本比較・透過品質の判定と本体統合は別工程',font=sm,fill='#c4cedd')
    video=folder/'comparison.mp4';ffmpeg=shutil.which('ffmpeg');assert ffmpeg
    proc=subprocess.Popen([ffmpeg,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1280x720','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','20','-threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=[];unique=set();edge_hits=0
    for k in range(COUNT):
        t=-.3+k/FPS;fx=effect(frame,spec,t);frames.append(fx);alpha=np.asarray(fx.getchannel('A'));edge_hits+=int(np.count_nonzero(np.r_[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]));unique.add(hashlib.sha256(fx.tobytes()).hexdigest())
        canvas=board.copy();canvas.alpha_composite(fx,(64,350));combined=Image.new('RGBA',(512,288))
        timing=spec['timeline'];exit_start=timing['frame_exit_start_s'];exit_duration=timing['frame_exit_end_s']-exit_start
        op=smooth(t/timing['frame_enter_s'])*(1-smooth((t-exit_start)/exit_duration)) if t>=0 else 0
        put(combined,f,256,144,op);protected=fx.copy();protected.putalpha(ImageChops.subtract(protected.getchannel('A'),protect));combined.alpha_composite(protected);canvas.alpha_composite(combined,(704,350))
        draw=ImageDraw.Draw(canvas);draw.rectangle((28,648,1250,655),fill='#354256');draw.rectangle((28,648,28+round(1222*k/(COUNT-1)),655),fill='#7ac6ed');draw.text((1100,22),f'{t:+.2f}s',font=sm,fill='white')
        proc.stdin.write(canvas.tobytes())
        if k==18:canvas.convert('RGB').save(folder/'poster.jpg',quality=93)
    proc.stdin.close();error=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,error
    webp=folder/'effect_alpha.webp';durations=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(COUNT)];frames[0].save(webp,save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=90,method=3)
    peak=folder/'impact_2048_rgba.png';effect(frame,spec,.24,2048).save(peak)
    cap=cv2.VideoCapture(str(video));count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);cap.release();assert count==COUNT and abs(fps-FPS)<.01
    dec=Image.open(webp);duration=0;encoded_edge=0
    for k in range(dec.n_frames):
        dec.seek(k);dec.load();duration+=dec.info.get('duration',0);aa=np.array(dec.convert('RGBA').getchannel('A'));encoded_edge+=int(np.count_nonzero(np.r_[aa[0],aa[-1],aa[:,0],aa[:,-1]]))
    assert duration==DURATION_MS and dec.n_frames>10 and len(unique)>(5 if spec['mode']=='minimal' else 20)
    assert frames[0].getbbox() is None and frames[-1].getbbox() is None
    assert effect(frame,spec,.37).tobytes()==effect(frame,spec,.37).tobytes()
    spec['qa']=dict(mp4_frames=count,fps=fps,duration_ms=duration,webp_frames=dec.n_frames,unique_frames=len(unique),outer_edge_nonzero_samples=edge_hits,encoded_webp_edge_hits=encoded_edge,deterministic=True,zero_at_clip_boundaries=True,portrait_holes_detected=len(found),source_frame_alpha_warning=a.get('quality_flags',[]),final_approved=False)
    spec['outputs']=[dict(file=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in [video,webp,peak,folder/'poster.jpg']]
    prior.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=a['key'],outputs=spec['outputs'],qa=spec['qa'])

def main():
    plan=json.loads((ROOT/'production.json').read_text(encoding='utf-8'));pending=[a for a in plan['assets'] if a['status']=='pending']
    if pending:raise RuntimeError(f'Frames not all produced: {len(pending)} pending. Effects render is scheduled after frames.')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        tasks={pool.submit(produce,a):a['key'] for a in plan['assets']}
        for task in as_completed(tasks):
            result=task.result();rows.append(result);print(result['key']+' motion completed',flush=True)
    (ROOT/'motion_catalog.json').write_text(json.dumps(dict(count=len(rows),status='review',final_approved=0,assets=sorted(rows,key=lambda a:a['key'])),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
