from common import *
import itertools,time
L=W/'latest_readonly/pr49/LoL_AutoCine';scope={'math':math,'Template':object}
for node in ast.parse((L/'core/effects.py').read_text('utf-8-sig')).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['_enable_expr','_build_video_effect_filters']:exec(compile(ast.Module(body=[node],type_ignores=[]),'latest_effects','exec'),scope)
def rgbgraph(src,graph,fps=60):
 n,h,w,_=src.shape;b=ff(['-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-vf',graph,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],src.tobytes());return np.frombuffer(b,np.uint8).reshape(-1,h,w,3)
def flash():
 rows=[];pictures=[]
 clocks={'VFR':[F(str(v)) for v in [0,.016,.05,.083,.1,.1003,.1008,.133,.2,.3,.301,.5]],'seek_back':[F(str(v)) for v in [0,.05,.1,.15,.2,.25,0,.05,.1,.15,.2]],'pause':[F(str(v)) for v in [0,.05,.1,.1,.1,.15,.2,.25]],'speed_change':[F(str(v)) for v in [0,.033,.066,.1,.116,.133,.15,.216,.283,.35]]}
 events=[F('.1004'),F('.1084'),F('.1084'),F('.3002')]
 for name,pts in clocks.items():
  # setpts can be nonmonotonic for synthetic seek-clock evaluation only; no mux claim.
  expr=str(int(pts[-1]*1e6))
  for i,t in reversed(list(enumerate(pts[:-1]))):expr=f'if(eq(N,{i}),{int(t*1e6)},{expr})'
  src=np.full((len(pts),90,160,3),80,np.uint8);term='0'
  for e in events:term=f'max({term},if(gte(t,{float(e):.12f}),0.278*exp(-18*abs(t-{float(e):.12f})),0))'
  graph=f"settb=1/1000000,setpts='{expr}',eq=brightness='{term}':eval=frame"
  a=rgbgraph(src,graph);base=rgbgraph(src,f"settb=1/1000000,setpts='{expr}',eq=brightness=0:eval=frame");d=np.abs(a.astype(int)-base.astype(int)).max((1,2,3));pre=[i for i,t in enumerate(pts) if t<min(events)];ok=bool(np.all(d[pre]==0));rows.append({'clock_case':name,'clock_pts':[str(t) for t in pts],'pre_event_max_delta':int(d[pre].max()),'status':'PASS' if ok else 'FAIL','graph':graph,'scope':'actual CPU filter clock, seek/pause simulated; no real seek API or VFR mux timestamps','patch_mean':a.mean((1,2,3)).tolist()})
  pictures.extend([Image.fromarray(a[i]) for i in range(len(a))]);sheet(f'A3_fx/flash_{name}.png',[Image.fromarray(v) for v in a],[f'{name} t={float(pts[i]):.4f}' for i in range(len(a))],4,(320,180))
 strong=[]
 for k in [.15,.5,.9]:
  src=np.empty((24,90,160,3),np.uint8);src[:]=[210,175,120];g=f"eq=brightness='if(gte(n,7),{.18+.65*k:.3f}*exp(-18*abs(t-.1004)),0)':eval=frame";a=rgbgraph(src,g);strong.append({'strength':k,'clip_channel_fraction':float((a==255).mean()),'peak_rgb':a.max((0,1,2)).tolist(),'status':'REVIEW','candidate':'luma/headroom limiter needed; causal gate alone does not preserve color'})
 save('A3_fx/FLASH_NEW_CLOCK_RESULTS.json',{'cases':rows,'strengths':strong,'real_replay_seek_pause':'NOT_RUN','VFR_container_roundtrip':'NOT_RUN','CFR_prior_48_tests':'inherited, not rerun'})
def effects():
 rows=[];N=18;src=[]
 for n in range(N):
  im=bg((640,360),False,n);d=ImageDraw.Draw(im);x=100+n*15;d.rectangle((x,120,x+50,185),fill=(175,75,40));d.line((0,180,639,180),fill='#aaa');src.append(np.asarray(im.resize((1920,1080),Image.Resampling.NEAREST)))
 src=np.asarray(src)
 for name in ['motion_camera','glitch','focus_blur','camera_shake','vignette_fx','glint','chroma_leak','radial_blur']:
  for strength in [.15,.5]:
   graphs=scope['_build_video_effect_filters'](NS(video_effects={name:strength}),.6,[(.2,.6)],False);g=','.join(graphs)+',scale=640:360:flags=lanczos';start=time.perf_counter()
   try:
    b=ff(['-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-vf',g,'-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],src.tobytes());a=np.frombuffer(b,np.uint8).reshape(N,360,640,3);seconds=time.perf_counter()-start;video=encode(f'A3_fx/samples/{name}_{strength}.mp4',a,30);sheet(f'A3_fx/samples/{name}_{strength}.png',[Image.fromarray(a[n]) for n in [0,6,10,17]],[f'{name} {strength} n{n}' for n in [0,6,10,17]],2,(640,360));rows.append({'id':name,'strength':strength,'status':'REVIEW','render':'PASS','elapsed_seconds':seconds,'scope':'18 native1920 CPU frames; one wall-clock run including process startup, not a performance benchmark','white_fraction':float((a.min(3)>250).mean()),'video':video,'graph':g})
   except Exception as e:rows.append({'id':name,'strength':strength,'status':'FAIL','error':str(e),'graph':g})
   print(name,strength,flush=True)
 save('A3_fx/OTHER_FX_RESULTS.json',rows)
 # Temporal and true spatial radial are intentionally separate algorithms.
 a=Image.fromarray(src[8]).resize((640,360));center=(220,160);rad=[]
 for factor in [1.,1.01,1.02,1.03,1.04]:
  rad.append(np.asarray(a.transform(a.size,Image.Transform.AFFINE,(factor,0,center[0]*(1-factor),0,factor,center[1]*(1-factor)),Image.Resampling.BILINEAR)).astype(float))
 result=Image.fromarray(np.rint(np.mean(rad,axis=0)).astype(np.uint8));sheet('A3_fx/spatial_radial_separate.png',[a,result],['single frame source','independent spatial radial average; no temporal history'],2,(640,360));save('A3_fx/SPATIAL_RADIAL_FIXTURE.json',{'status':'REVIEW','center':center,'sample_scales':[1,1.01,1.02,1.03,1.04],'temporal_history':False,'engine':'Pillow affine RGB average, CPU synthetic','moving_target_tracking':'NOT_RUN','GPU':'NOT_RUN'})
if __name__=='__main__':
 for n in sys.argv[1:] or ['flash','effects']:globals()[n]()
