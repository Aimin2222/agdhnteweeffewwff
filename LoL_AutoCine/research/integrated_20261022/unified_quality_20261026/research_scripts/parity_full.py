from common import *
import itertools,copy
sys.path.insert(0,str(S));from core import work_kill_assets as k
k.ROOT=A;k.CATALOG=S/'assets/work_kill_assets/catalog.json';CAT=k.catalog();FC={x['id']:x for x in CAT['frames']};EC={x['id']:x for x in CAT['effects']};IC=[R/f'work/autocine_research_v4_20261025/official_icons/{n}.png' for n in ['Yasuo','Jinx']]
def template(effect,motion):return NS(work_kill_frame_id='083/a_simple_main',work_kill_effect_id=effect,work_kill_review=True,work_kill_strength='strong',kill_icon_position='right-top',kill_icon_scale=.85,kill_icon_duration=.55,kill_icon_opacity=.7,kill_icon_motion=motion,kill_stack_gap=4)
def inputs(effect,stack):
 tmp=W/'parity_inputs';tmp.mkdir(exist_ok=True);frame=FC['083/a_simple_main'];paths=[];groups=[]
 for row in range(stack):
  layers=[];at=float(F(1,10)+F(row,20))
  if effect:
   images=[('frame',Image.open(A/frame['path']).convert('RGBA')),('peak',k.render_peak(frame,EC[effect],A/EC[effect]['path']))]
  else:images=[]
  images+=[('frame',k.render_pair(frame['id'],*IC,review=True,include_ornament=not bool(effect)))]
  for kind,im in images:
   p=tmp/f'{bool(effect)}_{row}_{len(paths)}.png';im.save(p);idx=len(paths);paths.append(p);layers.append({'index':idx,'kind':kind,'width':im.width,'height':im.height,**({'duration':.8} if kind=='peak' else {})})
  groups.append({'time':at,'layers':layers})
 return NS(layers=groups,strength=k.strength('strong')),paths
def bbox(im,bgval=(0,0,0)):
 a=np.asarray(im)[:,:,:3].astype(int);m=np.max(np.abs(a-np.array(bgval)),axis=2)>8;y,x=np.nonzero(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def error(a,b):return max(abs(x-y) for x,y in zip(a,b)) if a and b else (0 if a==b else None)
def run():
 rows=[];videos=[];boundary=[]
 for effect,stack,motion in itertools.product(['','D_project'],[1,2,3],['instant','slide_left','slide_right','slide_up','slide_down','pop']):
  t=template(effect,motion);en,paths=inputs(effect,stack);plan=k.layer_plan(en,1.,t.kill_icon_duration)
  for width,height in [(1920,1080),(1366,768),(1280,720)]:
   N=30;graph=k.with_work_badges('[0:v]format=rgba[vout]',1,en,duration=1.,scale=t.kill_icon_scale,seconds=t.kill_icon_duration,opacity=t.kill_icon_opacity,motion=motion)
   args=['-filter_complex_threads','1','-f','lavfi','-i',f'color=black:s={width}x{height}:r=30:d=1,format=rgba']
   for p in paths:args+=['-loop','1','-i',p]
   raw=ff(args+['-filter_complex',graph,'-map','[vout]','-frames:v',N,'-f','rawvideo','-pix_fmt','rgba','pipe:1']);export=np.frombuffer(raw,np.uint8).reshape(N,height,width,4)
   common=[];oldpre=[];samples=[]
   for n in range(N):
    time=n/30;old=Image.new('RGBA',(width,height),(0,0,0,255));new=Image.new('RGBA',(width,height))
    for group in en.layers:
     ix=group['layers'][-1]['index'];p=next((z for z in plan if z['index']==ix),None)
     if not p:continue
     oldactive=p['start']<=time<p['end'];tickactive=F(n,30)>=F(round(p['start']*1e6),1000000) and F(n,30)<F(round(p['end']*1e6),1000000)
     elapsed=max(0.,float(F(n,30)-F(round(group['time']*1e6),1000000)))
     if oldactive:old.alpha_composite(k.render_preview_pair(t,*IC,time-group['time'],row=p['row'],size=(width,height)))
     if tickactive:new.alpha_composite(k.render_preview_pair(t,*IC,elapsed,row=p['row'],size=(width,height)))
     if oldactive!=tickactive:boundary.append({'width':width,'motion':motion,'effect':effect,'stack':stack,'n':n,'start_float':p['start'],'old_active':oldactive,'tick_active':tickactive})
    common.append(np.asarray(new));oldpre.append(np.asarray(old));eb,pb=bbox(export[n]),bbox(old);samples.append({'n':n,'t':str(F(n,30)),'legacy_export_bbox':eb,'legacy_preview_bbox':pb,'legacy_bbox_error':error(eb,pb)})
   common=np.asarray(common);oldpre=np.asarray(oldpre)
   # Candidate shares a prepared RGBA raster, but two independent final compositors consume it.
   raw=ff(['-filter_complex_threads','1','-f','lavfi','-i',f'color=c=0x172936:s={width}x{height}:r=30:d=1,format=rgba','-f','rawvideo','-pix_fmt','rgba','-s',f'{width}x{height}','-r','30','-i','pipe:0','-filter_complex','[0:v][1:v]overlay=format=rgb:alpha=straight:shortest=1[out]','-map','[out]','-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],common.tobytes());ce=np.frombuffer(raw,np.uint8).reshape(N,height,width,3)
   pictures=[]
   for n in range(N):
    overlay=Image.fromarray(common[n]);cp=Image.alpha_composite(Image.new('RGBA',(width,height),'#172936'),overlay).convert('RGB');diff=np.abs(ce[n].astype(int)-np.asarray(cp).astype(int));samples[n].update({'candidate_rgb_max_error':int(diff.max()),'candidate_rgb_MAE':float(diff.mean()),'candidate_export_bbox':bbox(ce[n],(23,41,54)),'candidate_preview_bbox':bbox(cp,(23,41,54))})
    if width==1366 and stack==3 and effect:
     im=Image.new('RGB',(1280,400),'#172333')
     for j,v in enumerate([export[n,:,:,:3],oldpre[n,:,:,:3],ce[n],np.asarray(cp)]):im.paste(Image.fromarray(v).resize((320,180)),(j*320,30));label(im,['legacy export','legacy preview','shared raster FFmpeg','shared raster Pillow'][j],(j*320+4,5),13)
     label(im,f'n={n} / {motion}; research only; not product integration',(10,230),18);pictures.append(np.asarray(im))
   case={'size':[width,height],'motion':motion,'stack':stack,'effect':effect,'samples':samples,'legacy_status':'FAIL' if any((s['legacy_bbox_error'] or 0)>2 for s in samples) else 'REVIEW','candidate_compositor_status':'PASS' if all(s['candidate_rgb_max_error']<=2 for s in samples) else 'FAIL','candidate_scope':'prepared shared RGBA sequence; independent FFmpeg/Pillow compositors. Not independent planner proof or live app fix.'};rows.append(case)
   if pictures:
    name=f'A4_parity/comparison_{motion}';videos.append(encode(name+'.mp4',pictures,30));sheet(name+'.png',[Image.fromarray(pictures[n]) for n in [2,3,6,9,16,22]],[f'n{n}' for n in [2,3,6,9,16,22]],2,(640,200))
   del export,oldpre,common,ce
  print('parity',bool(effect),stack,motion,flush=True)
 save('A4_parity/FULL_ANIMATION_RESULTS.json',{'cases':rows,'count':len(rows),'frames':len(rows)*30,'fps':30,'sample_clock':'all n0..29, events .10/.15/.20, duration .55, opacity .7, scale .85','candidate':'shared raster, not final product fix','native_DPI_and_scroll':'NOT_RUN','videos':videos})
 save('A4_parity/FLOAT_ACTIVATION_MISMATCHES.json',{'items':boundary,'count':len(boundary),'reason':'binary layer_plan starts differ from six-decimal FFmpeg serialized gates; tick-quantized common activation is a new research candidate'})
if __name__=='__main__':run()
