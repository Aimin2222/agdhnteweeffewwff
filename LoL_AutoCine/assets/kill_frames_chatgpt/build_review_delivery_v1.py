"""Offline asset packaging only. Never imports or changes the application."""
from pathlib import Path
import ast, csv, hashlib, json, math, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
SOURCE_REPO=REPO.parent
ART=SOURCE_REPO/'LoL_AutoCine/assets/kill_frames'
ORIGINALS=SOURCE_REPO/'LoL_AutoCine/assets/kill_concepts'
OUT=ROOT/'original_alpha/review_v1'
FX=ROOT/'effect_assets/review_v1'
DESIGNS=ROOT/'abcd_designs/review_v1'
SPECS=ROOT/'effect_specs/review_v1'
for p in [OUT,FX,DESIGNS,SPECS]:p.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(REPO).as_posix()
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert sha(src)==sha(dst),str(dst)
    else:shutil.copyfile(src,dst)
    return dict(file=rel(dst),sha256=sha(dst),bytes=dst.stat().st_size)
def shape_mask(size,shape,offset=(0,0)):
    result=Image.new('L',size);d=ImageDraw.Draw(result)
    for key,coords in shape.items():
        if key not in ['ellipse','rectangle','polygon']:continue
        pts=np.asarray(coords).reshape(-1,2)-np.array(offset)
        if key=='polygon':d.polygon([tuple(map(float,p)) for p in pts],fill=255)
        else:getattr(d,key)(tuple(pts.reshape(-1).tolist()),fill=255)
    return result

records=[];sources=[];by_source={}
for n in range(1,90):
    info=read(ART/f'all_sources/s{n:03}/manifest.json')
    source=ORIGINALS/info['source_file'];assert sha(source)==info['source_sha256']
    original=Image.open(source).convert('RGB')
    entries=[]
    for a in info['assets']:
        src=ART/a['file'];mask=ART/a['mask_file']
        assert sha(src)==a['sha256'] and sha(mask)==a['mask_sha256']
        im=Image.open(src);assert im.mode=='RGBA'
        assert np.array_equal(np.asarray(im)[:,:,:3],np.asarray(original.crop(a['crop_box']))), (n,a['id'],'RGB differs')
        assert np.array_equal(np.asarray(im.getchannel('A')),np.asarray(Image.open(mask)))
        target=OUT/f'{n:03}'/(a['id']+'.png');rec=copy(src,target)
        rec.update(copy(mask,target.with_suffix('.alpha.png')) if False else {})
        mask_rec=copy(mask,target.with_suffix('.alpha.png'))
        alpha=im.getchannel('A');hist=alpha.histogram()
        holes=[]
        for hole in a.get('portrait_holes',[]):
            m=shape_mask(im.size,hole,a['crop_box'][:2]);selected=np.asarray(alpha)[np.asarray(m)>0]
            holes.append(dict(declared_pixels=int(selected.size),nonzero_pixels=int(np.count_nonzero(selected))))
        rec.update(source_number=f'{n:03}',source_file=source.name,source_sha256=info['source_sha256'],origin_file='LoL_AutoCine/assets/kill_frames/'+a['file'],origin_commit=subprocess.check_output(['git','-C',str(SOURCE_REPO),'rev-parse','HEAD'],text=True).strip(),id=a['id'],theme=a['theme'],component=a['component'],intensity=a['intensity'],role=a['role'],crop_box=a['crop_box'],portrait_holes=a.get('portrait_holes',[]),mask=mask_rec,rgb_exact=True,dimensions=im.size,mode=im.mode,transparent_pixels=hist[0],partial_pixels=sum(hist[1:255]),opaque_pixels=hist[255],portrait_hole_check=holes,quality_flags=a.get('quality_flags',[]),original_quality_metrics=a.get('quality_metrics',{}),status='review_user_selection_pending',final_approved=False,provenance='Existing Codex extraction copied unchanged; not a new AI generation')
        records.append(rec);entries.append(rec)
    for proof in sorted((ART/f'all_sources/s{n:03}').glob('*.jpg')):copy(proof,OUT/f'{n:03}'/proof.name)
    write(OUT/f'{n:03}'/'inventory.json',dict(source_number=f'{n:03}',source_file=source.name,source_sha256=info['source_sha256'],assets=entries,final_approved=False))
    by_source[n]=entries;sources.append(dict(number=f'{n:03}',source=source.name,sha256=info['source_sha256'],part_count=len(entries)))
    print('source',n,len(entries),flush=True)
write(OUT/'inventory.json',dict(source_count=89,part_records=len(records),all_rgb_exact=True,status='Review collection; existing extraction provenance retained',sources=sources,assets=records,final_approved=False))
for name in ['source_inventory.json','theme_correspondence.json','quality_issues.csv','unsupported_parts.json','verification_report.json','all_design_quality.csv']:
    copy(ART/'all_sources'/name,OUT/'upstream_evidence'/name)

# Effect names/colors are recovered from checked-in catalog AST without importing app code.
catalog={}
for node in ast.walk(ast.parse((SOURCE_REPO/'LoL_AutoCine/core/kill_frame_themes.py').read_text(encoding='utf-8-sig'))):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Theme':
        args=[ast.literal_eval(x) for x in node.args[:5]]
        catalog[args[0]]=dict(label=args[1],effect=args[3],color=args[4])
themes=read(ART/'all_sources/theme_correspondence.json')['registered_themes']
profiles={
'snow_reveal':('snowfall',0,28,35,80), 'scan_glitch':('horizontal_scan',0,12,180,0),
'starlight':('radial_star',32,24,80,-25),'stage_pulse':('beat_steps',0,18,40,-10),
'sound_pulse':('wave_expand',0,16,70,0),'petal_reveal':('petal_sine',65,22,35,20),
'void_orbit':('inward_orbit',-110,18,-55,0),'spark_dust':('outward_sparks',18,28,140,80),
'blood_moon':('crescent_sweep',-45,16,60,-10),'banner_slash':('diagonal_slash',-25,12,120,10),
'water_splash':('ballistic_drops',0,28,65,110),'leaf_bloom':('leaf_spiral',40,20,40,-15),
'star_orbit':('elliptic_orbit',90,20,65,0),'gravity_well':('inward_spiral',-150,22,-65,0),
'light_wings':('wing_open',25,16,80,-20),'ember_wings':('ember_rise',-25,26,55,-70),
'flame_burst':('flame_rise',0,32,65,-110),'pixel_spawn':('pixel_steps',0,24,80,0),
'witch_sparks':('witch_arc',55,22,50,-40),'ceramic_shine':('glint_travel',0,12,90,0),
'psi_static':('stutter_scan',0,18,130,0),'plasma_wings':('wing_snap',35,20,115,-20),
'rose_glass':('glass_radial',-35,24,95,35),'butterfly_reveal':('butterfly_flap',70,18,40,-20),
'disco_bounce':('disco_bounce',95,20,60,20),'ocean_ripple':('ripple_expand',0,24,65,40),
'imperial_mecha':('mechanical_lock',15,12,55,0),'dragon_trace':('dragon_curve',120,26,90,-35),
'ink_paint':('ink_reveal',-20,14,70,25),'mecha_assembly':('four_piece_lock',0,12,100,0),
'red_assembly':('piston_impact',0,20,115,20)}

def alpha_version(im,alpha):
    out=im.copy();out.putalpha(alpha);return out
def layer_set(key,record):
    im=Image.open(REPO/record['file']).convert('RGBA');alpha=im.getchannel('A')
    folder=FX/key;folder.mkdir(parents=True,exist_ok=True)
    copy(REPO/record['file'],folder/'ornament_rgba.png')
    # Derived bloom is a rendering layer, not replacement source artwork.
    pad=24;canvas=Image.new('RGBA',(im.width+pad*2,im.height+pad*2));canvas.alpha_composite(im,(pad,pad))
    a=canvas.getchannel('A');blur=a.filter(ImageFilter.GaussianBlur(6))
    arr=np.asarray(canvas).astype(float);prem=arr[:,:,:3]*(arr[:,:,3:4]/255)
    channels=[]
    for c in range(3):channels.append(np.asarray(Image.fromarray(np.uint8(prem[:,:,c])).filter(ImageFilter.GaussianBlur(6))).astype(float))
    ba=np.asarray(blur).astype(float);rgb=np.stack(channels,axis=2)/np.maximum(ba[:,:,None]/255,1/255)
    bloom=Image.fromarray(np.dstack([np.uint8(np.clip(rgb,0,255)),np.uint8(ba*.65)]),'RGBA');bloom.save(folder/'glow_rgba.png')
    # Actual disconnected pieces of the source alpha, never invented themed shapes.
    import cv2
    count,labels,stats,centers=cv2.connectedComponentsWithStats(np.uint8(np.asarray(alpha)>96),8)
    pieces=[]
    for idx in sorted(range(1,count),key=lambda j:int(stats[j,4]),reverse=True):
        x,y,w,h,area=map(int,stats[idx]);
        if area<4 or area>im.width*im.height*.08:continue
        mask=np.where(labels[y:y+h,x:x+w]==idx,np.asarray(alpha)[y:y+h,x:x+w],0).astype('uint8')
        tile=im.crop((x,y,x+w,y+h));tile.putalpha(Image.fromarray(mask));name=f'particle_{len(pieces):02}.png';tile.save(folder/name)
        pieces.append(dict(file=rel(folder/name),source_local_bbox=[x,y,x+w,y+h],original_rgb_retained=True))
        if len(pieces)>=8:break
    return dict(ornament=rel(folder/'ornament_rgba.png'),glow=rel(folder/'glow_rgba.png'),glow_offset=[-pad,-pad],particles=pieces,particle_status='extracted_components' if pieces else 'no_separable_particle; use motif reveal only',native_dimensions=im.size,source_record=record['file'],status='review_user_selection_pending',final_approved=False)

family_defs={'A':('シンプル','a_simple_main',.20,1.10,.15),'B':('高級感','b_prestige_main',.22,1.0,.18),'C':('シネマ','c_cinema_main',.24,1.0,.18),'D':('スキン・地域テーマ','d_ornate_main',.28,1.2,.22)}
specs=[]
for family,(label,part,enter,hold,leave) in family_defs.items():
    rec=next(x for x in by_source[83] if x['id']==part)
    layer=layer_set('ABCD/'+family,rec)
    spec=dict(id=family,label=label,family=family,source_number='083',source_file=rec['source_file'],source_record=rec['file'],layers=layer,confirmed_definition_source='docs/KILLFRAME_ABCD_IMPLEMENTATION_HANDOFF_20261013_JA.md and original No.083',timing_seconds=dict(pre_start=-.12,enter=enter,hold=hold,exit=leave),timing_evidence='enter/hold/exit read from No.083; A hold 0.9-1.4 allowed, 1.10 selected. Pre-start and detailed curves are NEW design proposals.',motion={'A':'split_slide','B':'metal_glint','C':'opposed_collision','D':'theme_reveal'}[family],glow_peak={'A':.15,'B':.38,'C':.75,'D':.55}[family],particle_count={'A':0,'B':8,'C':24,'D':18}[family],status='design_proposal_user_selection_pending',final_approved=False)
    specs.append(spec);write(DESIGNS/family/'design.json',spec)
    copy(REPO/rec['file'],DESIGNS/family/'source_frame_rgba.png')
for theme in themes:
    key=theme['theme'];meta=catalog[key];n=theme['primary_source_index'];candidates=[r for r in by_source[n] if r['theme']==key]
    if not candidates:candidates=by_source[n]
    frames=[r for r in candidates if r['component']=='frame'];assert frames,key
    frames.sort(key=lambda r:0 if r['intensity']=='strong' else 1)
    selected=frames[0];layer=layer_set('D/'+key,selected)
    motif_records=[r for r in candidates if r['component']!='frame']
    role_paths={role:[r['file'] for r in motif_records if r['role']==role] for role in ['melee','ranged','hybrid']}
    motion,rotation,particles,vx,vy=profiles[meta['effect']]
    spec=dict(id='D_'+key,family='D',theme=key,label=theme['label'],source_number=f'{n:03}',source_file=theme['actual_source_file'],catalog_effect=meta['effect'],catalog_color=meta['color'],layers=layer,frames={level:[r['file'] for r in frames if r['intensity']==level] for level in ['weak','strong']},roles=role_paths,role_policy='Only source-labelled roles. Empty role arrays mean not confirmed; do not invent a role.',timing_seconds=dict(pre_start=-.12,enter=.28,hold=1.2,exit=.22),timing_evidence='D family default from No.083; skin-specific numeric timing is a new proposal, not a recovered historical decision.',motion=motion,rotation_degrees=rotation,particle_count=particles,particle_velocity_px_s=[vx,vy],particle_lifetime_s=.5,glow_peak=.55,intensity_multiplier=dict(weak=.45,strong=1.0),status='design_proposal_user_selection_pending',final_approved=False)
    specs.append(spec);write(SPECS/'D'/f'{key}.json',spec)

def smooth(p):p=max(0,min(1,p));return p*p*(3-2*p)
def preview(spec):
    im=Image.open(REPO/spec['layers']['ornament']).convert('RGBA');im.thumbnail((520,210))
    size=(640,320);frames=[];times=[-.12,0,.08,.18,.28,.6,1.0,1.3,1.48,1.7]
    for t in times:
        enter=spec['timing_seconds']['enter'];end=enter+spec['timing_seconds']['hold'];leave=spec['timing_seconds']['exit']
        p=smooth(t/enter);opacity=p*(1-smooth((t-end)/leave))
        scaled=im.resize((max(1,round(im.width*(.92+.08*p))),max(1,round(im.height*(.92+.08*p)))),Image.Resampling.LANCZOS)
        alpha=scaled.getchannel('A').point(lambda a:round(a*opacity));scaled.putalpha(alpha)
        canvas=Image.new('RGBA',size);canvas.alpha_composite(scaled,((size[0]-scaled.width)//2,(size[1]-scaled.height)//2));frames.append(canvas)
    out=DESIGNS/spec['id'] if spec['family']!='D' or spec['id']=='D' else DESIGNS/'D_themes'/spec['theme']
    out.mkdir(parents=True,exist_ok=True)
    for idx in [0,1,4,6,8,9]:frames[idx].save(out/f'key_{idx:02}.png')
    frames[0].save(out/'timing_preview.webp',save_all=True,append_images=frames[1:],duration=[120,80,100,100,320,400,300,180,220,120],loop=0,lossless=True)
    spec['timing_preview']=rel(out/'timing_preview.webp')
    spec['preview_scope']='Timing/scale/opacity proof only; theme-specific motion and particles are specified in JSON and not all rendered here.'
for spec in specs:preview(spec)
write(SPECS/'animation_catalog.json',dict(families=4,d_themes=len(themes),specs=specs,final_approved=False))
with (SPECS/'theme_register.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['id','label','source_number','motion','color','enter_s','hold_s','exit_s','state'])
    for s in specs:w.writerow([s['id'],s['label'],s['source_number'],s['motion'],s.get('catalog_color','source colors'),s['timing_seconds']['enter'],s['timing_seconds']['hold'],s['timing_seconds']['exit'],s['status']])
write(ROOT/'DELIVERY_REVIEW_V1.json',dict(original_source_count=89,original_part_records=len(records),d_theme_count=len(themes),family_count=4,status='Review collection for user selection; not final integration approval',final_approved_count=0,original_alpha_index=rel(OUT/'inventory.json'),effect_catalog=rel(SPECS/'animation_catalog.json')))
print('DONE',len(records),len(specs),flush=True)
