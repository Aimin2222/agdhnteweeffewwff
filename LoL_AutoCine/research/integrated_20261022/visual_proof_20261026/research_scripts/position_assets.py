from common import *
import itertools,shutil
sys.path.insert(0,str(S));from core import work_kill_assets as k
k.ROOT=A;k.CATALOG=S/'assets/work_kill_assets/catalog.json'
CAT=k.catalog();FC={x['id']:x for x in CAT['frames']};EC={x['id']:x for x in CAT['effects']}
IC=[R/'work/autocine_research_v4_20261025/official_icons'/f'{x}.png' for x in ['Yasuo','Jinx']]
M=['instant','slide_left','slide_right','slide_up','slide_down','pop']
def template(frame='083/a_simple_main',effect='',motion='instant'):
 return NS(work_kill_frame_id=frame,work_kill_effect_id=effect,work_kill_review=True,work_kill_strength='strong',kill_icon_position='right-top',kill_icon_scale=1.,kill_icon_duration=1.55,kill_icon_opacity=1.,kill_icon_motion=motion,kill_stack_gap=4)
def entries(effect,stack):
 tmp=W/'position_inputs';tmp.mkdir(exist_ok=True);frame=FC['083/a_simple_main'];paths=[];groups=[]
 for row in range(stack):
  at=.1+row*.05;layers=[]
  if effect:
   for kind,image in [('frame',Image.open(A/frame['path']).convert('RGBA')),('peak',k.render_peak(frame,EC[effect],A/EC[effect]['path']))]:
    p=tmp/f'{effect}_{row}_{kind}.png';image.save(p);idx=len(paths);paths.append(p);layers.append({'index':idx,'kind':kind,'width':image.width,'height':image.height,**({'duration':.8} if kind=='peak' else {})})
  image=k.render_pair(frame['id'],*IC,review=True,include_ornament=not bool(effect));p=tmp/f'pair_{bool(effect)}_{row}.png';image.save(p);idx=len(paths);paths.append(p);layers.append({'index':idx,'kind':'frame','width':image.width,'height':image.height});groups.append({'time':at,'layers':layers})
 return NS(layers=groups,strength=k.strength('strong')),paths
def bbox(im):
 a=np.asarray(im);m=a[:,:,:3].max(2)>8;y,x=np.nonzero(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def position():
 rows=[];times=[3,6,9,12,18];fx='D_project'
 for effect,stack,motion in itertools.product(['',fx],[1,3],M):
  en,paths=entries(effect,stack);plan=k.layer_plan(en,.7,1.55);ref=None
  for w,h in [(1920,1080),(1366,768),(1280,720)]:
   graph=k.with_work_badges('[0:v]format=rgba[vout]',1,en,duration=.7,motion=motion)
   # Selection follows the real source graph, retaining its output PTS.
   graph=graph.replace('[vout]','[rendered]')+';[rendered]select=\''+'+'.join(f'eq(n,{n})' for n in times)+"\'[selected]"
   args=['-filter_complex_threads','1','-f','lavfi','-i',f'color=black:s={w}x{h}:r=30:d=0.7,format=rgba']
   for p in paths:args+=['-loop','1','-i',p]
   b=ff(args+['-filter_complex',graph,'-map','[selected]','-fps_mode','passthrough','-frames:v',len(times),'-f','rawvideo','-pix_fmt','rgba','pipe:1']);exp=np.frombuffer(b,np.uint8).reshape(len(times),h,w,4)
   if w==1920:ref=exp.copy()
   t=template(effect=effect,motion=motion);frames=[];samples=[]
   for ni,n in enumerate(times):
    time=n/30;mir=Image.new('RGBA',(w,h),(0,0,0,255))
    for group in en.layers:
     ix=group['layers'][-1]['index'];p=next((z for z in plan if z['index']==ix and z['start']<=time<z['end']),None)
     if p:mir.alpha_composite(k.render_preview_pair(t,*IC,time-group['time'],row=p['row'],size=(w,h)))
    exported=Image.fromarray(exp[ni]);candidate=Image.fromarray(ref[ni]).resize((w,h),Image.Resampling.LANCZOS)
    eb,mb,cb=map(bbox,[exported,mir,candidate]);err=lambda x,y:max(abs(a-b) for a,b in zip(x,y)) if x and y else (0 if x==y else None)
    def mask_iou(x,y):
     p=np.asarray(x)[:,:,:3].max(2)>8;q=np.asarray(y)[:,:,:3].max(2)>8;return float((p&q).sum()/max(1,(p|q).sum()))
    samples.append({'frame':n,'t':time,'legacy_export_bbox':eb,'preview_bbox':mb,'candidate_export_bbox':cb,'legacy_bbox_max_error_px':err(eb,mb),'candidate_bbox_max_error_px':err(cb,mb),'legacy_support_iou':mask_iou(exported,mir),'candidate_support_iou':mask_iou(candidate,mir),'candidate_rgb_MAE':float(np.abs(np.asarray(candidate).astype(float)-np.asarray(mir).astype(float))[:,:,:3].mean())})
    if n==9:
     diff=Image.fromarray(np.minimum(255,np.abs(np.asarray(exported)[:,:,:3].astype(int)-np.asarray(mir)[:,:,:3].astype(int))*4).astype(np.uint8));overlay=Image.blend(exported.convert('RGB'),mir.convert('RGB'),.5)
     ims=[exported,mir,overlay,candidate,diff];labels=['legacy CPU export','existing CPU preview','50% overlay','1080 reference resize candidate','abs difference x4']
     for dpi,vp in [(1.,(960,540)),(1.25,(800,600)),(1.5,(1024,576))]:
      target=(round(vp[0]*dpi),round(vp[1]*dpi));a=ImageOps.contain(mir,target,Image.Resampling.LANCZOS);b=ImageOps.contain(candidate,target,Image.Resampling.LANCZOS);samples[-1].setdefault('viewport_tests',[]).append({'dpi':dpi,'viewport':vp,'physical_picture':a.size,'rgba_MAE':float(np.abs(np.asarray(a).astype(float)-np.asarray(b).astype(float)).mean())})
     name=f'position/{w}_{motion}_{"fx" if effect else "frame"}_{stack}.jpg';sheet(name,ims,labels,3,(480,270))
     if motion=='instant' and stack==3 and effect:
      for tag,img in [('export',exported),('preview',mir),('candidate',candidate)]:
       dest=O/'position'/f'native_{w}_{tag}.png';img.save(dest)
   row={'size':[w,h],'motion':motion,'effect':effect,'stack':stack,'samples':samples,'sheet':name,'scope':'actual pinned CPU Work export/preview RGBA composited over identical opaque black; candidate is independent 1080-output resampling, no product modification','production':'NOT_RUN'};rows.append(row);print('position',len(rows),w,motion,bool(effect),stack,flush=True)
 save('POSITION_RESULTS.json',{'cases':rows,'cases_count':len(rows),'rgba_frames_compared':len(rows)*len(times),'live_LoL':False,'GPU':'NOT_RUN','dpi_method':'research bitmap viewport/physical pixels; not Windows DPI or native application validation','candidate_status':'REVIEW; same bbox is not pixel/art approval'})

def assets():
 queue=load(R/'outputs/autocine_implementation_specs_20261026/ASSET_REVIEW_QUEUE.json')['items'];items=[x for x in queue if x['priority'] in ['P0','P1']];items.sort(key=lambda x:(x['priority'],x['kind'],x['id']))
 root=Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository');masters={x['number']:x for x in load(R/'outputs/autocine_final_research_v3_20261024/ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files']};rows=[]
 for i,x in enumerate(items):
  meta=(FC if x['kind']=='frame' else EC)[x['id']];im=Image.open(A/x['path']).convert('RGBA');src=root/meta['source_path'];deriv_same=sha(src)==sha(A/x['path']) if src.exists() else None
  number=meta.get('number') or str(meta.get('spec',{}).get('source_number','')).zfill(3);master=masters.get(number);masterpath=root/master['path'] if master else None
  out=Image.new('RGB',(1500,1110),'#182333');label(out,f'{i+1:03d} {x["priority"]} {x["kind"]} {x["id"]} | status preserved: {x["catalog_status_unchanged"]}',(12,5),22)
  label(out,'89-source context (not reconstructed)',(8,42),16)
  if masterpath and masterpath.exists():
   z=Image.open(masterpath).convert('RGB');z.thumbnail((450,245));out.paste(z,(8,70))
  else:label(out,'Source context unavailable',(8,110),17)
  checker=Image.new('RGBA',im.size,'#d5dbe2');draw=ImageDraw.Draw(checker)
  for xx in range(0,im.width,40):
   for yy in range(0,im.height,40):
    if (xx//40+yy//40)%2:draw.rectangle((xx,yy,xx+39,yy+39),fill='#f1f3f5')
  checker.alpha_composite(im);z=checker.convert('RGB');z.thumbnail((1010,260));out.paste(z,(480,70));label(out,f'native RGBA overview {im.width}x{im.height}; derivation source identical={deriv_same}',(480,42),16)
  # Native edge samples, do not redraw or infer missing source pixels.
  al=np.asarray(im.getchannel('A'));edge=np.r_[al[0],al[-1],al[1:-1,0],al[1:-1,-1]]
  def clip(v,n,limit):return max(0,min(limit-n,int(v)-n//2))
  tx=clip(np.argmax(al[0]),180,im.width);bx=clip(np.argmax(al[-1]),180,im.width);ly=clip(np.argmax(al[:,0]),70,im.height);ry=clip(np.argmax(al[:,-1]),70,im.height)
  edge_crops=[(tx,0,tx+180,70),(bx,im.height-70,bx+180,im.height),(0,ly,180,ly+70),(im.width-180,ry,im.width,ry+70)]
  for j,box in enumerate(edge_crops):out.paste(checker.crop(box).convert('RGB'),(20+j*190,335))
  label(out,f'1:1 edge crops | solid edge px={(edge>=128).sum()} | soft edge px={(edge>8).sum()} | source constraints retained',(8,410),16)
  frame=x['id'] if x['kind']=='frame' else '083/a_simple_main';effect=x['id'] if x['kind']=='effect' else '';t=template(frame,effect)
  for light in [False,True]:
   scene=bg((750,360),light)
   for row in range(2):scene.paste(k.render_preview_pair(t,*IC,.08,row=row,size=(750,360)),(0,0),k.render_preview_pair(t,*IC,.08,row=row,size=(750,360)))
   out.paste(scene,(750*int(light),455));roi=scene.crop((550,5,750,160)).resize((360,279),Image.Resampling.NEAREST);out.paste(roi,(750*int(light)+15,465));label(out,('light' if light else 'dark')+' / 1.8x ROI left; actual CPU 2 rows right',(750*int(light)+8,428),16)
  for j,motion in enumerate(['slide_left','slide_up','pop','instant']):
   t.kill_icon_motion=motion;scene=bg((375,211),False);layer=k.render_preview_pair(t,*IC,.13,size=(375,211));scene.paste(layer,(0,0),layer);out.paste(scene,(j*375,865));label(out,motion+' / elapsed .13s',(j*375+8,828),16)
  path=f'assets/{i+1:03d}_{x["priority"]}_{x["id"].replace("/","_")}.jpg';p=O/path;p.parent.mkdir(exist_ok=True);out.save(p,quality=94)
  rows.append({'sequence':i+1,'kind':x['kind'],'id':x['id'],'priority':x['priority'],'sheet':path,'catalog_status_unchanged':x['catalog_status_unchanged'],'master_number':number,'master_available':bool(masterpath and masterpath.exists()),'derivation_source_available':src.exists(),'derivation_source_identical_hash':deriv_same,'work_sha256':sha(A/x['path']),'solid_edge_pixels':int((edge>=128).sum()),'soft_edge_pixels':int((edge>8).sum()),'native_edge_crops':edge_crops,'portrait_geometry':'catalog verified' if meta.get('portrait_boxes') else ('baseline083 used for FX' if x['kind']=='effect' else 'provisional fallback, not approved'),'visual_review':'NOT_RUN','formal_approval_changed':False})
  print('asset',i+1,x['priority'],x['id'],flush=True)
 save('ASSET_RENDER_LEDGER.json',{'items':rows,'P0_count':50,'P1_count':90,'P2_not_rendered':547,'production_background':'NOT_RUN; artificial contrast/HUD contexts','generated_not_automatically_visually_reviewed':True})
 # Two detailed sheets per review board, preserving readable display size.
 for start in range(0,len(rows),2):
  board=Image.new('RGB',(1500,2220))
  for j,row in enumerate(rows[start:start+2]):board.paste(Image.open(O/row['sheet']),(0,j*1110))
  board.save(W/f'review_board_{start//2+1:02d}.jpg',quality=94)
if __name__=='__main__':
 for name in sys.argv[1:] or ['position','assets']:globals()[name]()
