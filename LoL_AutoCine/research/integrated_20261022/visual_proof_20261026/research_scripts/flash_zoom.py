from common import *
import itertools

def flash():
 e=extract_effects();rows=[];videos=[];clean_cache={};patterns={'single':[.1004],'continuous':[.1004,.3002,.5004],'simultaneous':[.1004,.1004],'short':[.1004,.1084]}
 for fps,rate,(kind,replay_events) in itertools.product([F(30),F(60),F(60000,1001)],[F(1),F(1,2)],patterns.items()):
  ev=[F(str(t))/rate for t in replay_events];duration=F(6,5)/rate;N=math.ceil(duration*fps);width,height=320,180
  source=[]
  for n in range(N):
   im=bg((width,height),False,n);ImageDraw.Draw(im).rectangle((0,0,50,40),fill=(80,80,80));source.append(np.asarray(im))
  source=np.asarray(source);amp=float(f'{.18+.65*.15:.3f}');events=[(float(t),float(t)+.42) for t in ev];legacy=e['_build_video_effect_filters'](NS(video_effects={'flash':.15}),float(duration),events,False)
  key=(str(fps),str(rate))
  if key not in clean_cache:
   raw=ff(['-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-vf','eq=brightness=0:eval=frame','-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],source.tobytes());clean_cache[key]=np.frombuffer(raw,np.uint8).reshape(source.shape)
  clean=clean_cache[key]
  def graph(rev):
   if rev=='legacy':return legacy
   terms=[]
   for t in ev:
    gate=f'gte(t,{float(t):.3f})' if rev=='v4' else f'gte(n,{math.ceil(t*fps)})'
    time=f'{float(t):.3f}' if rev=='v4' else f'{float(t):.12f}'
    terms.append(f'if({gate},{amp:.3f}*exp(-18*abs(t-{time})),0)')
   b=terms[0]
   for term in terms[1:]:b=f'max({b},{term})'
   return [f'eq=brightness=\'{b}\':eval=frame:enable='+e['_enable_expr'](events,after=.15)]
  arrays={};detail=[];pre=np.array([F(n,1)/fps<min(ev) for n in range(N)])
  for rev in ['legacy','v4','v5']:
   g=graph(rev);b=ff(['-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-vf',','.join(g),'-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],source.tobytes());a=np.frombuffer(b,np.uint8).reshape(N,height,width,3);arrays[rev]=a
   # Fixed gray patch, compare to same-frame clean decoded input.
   delta=np.abs(a[:,:40,:50].astype(int)-clean[:,:40,:50].astype(int)).max((1,2,3));changed=np.flatnonzero(delta>0)
   detail.append({'revision':rev,'graph':g,'pre_event_max_rgb_delta':int(delta[pre].max()) if pre.any() else 0,'pre_event_frame_count_nonzero':int((delta[pre]>0).sum()),'first_changed_frame':int(changed[0]) if len(changed) else None,'expected_first_event_frame':math.ceil(min(ev)*fps),'peak_patch_mean':float(a[:,:40,:50].mean((1,2,3)).max()),'patch_mean_per_frame':a[:,:40,:50].mean((1,2,3)).tolist(),'status':'PASS' if not np.any(delta[pre]>0) else 'FAIL'})
  name=f'flash_{fps.numerator}_{fps.denominator}_{str(rate).replace("/","_")}_{kind}';frames=[]
  for n in range(N):
   im=Image.new('RGB',(960,216),'#172333')
   for j,rev in enumerate(['legacy','v4','v5']):im.paste(Image.fromarray(arrays[rev][n]),(j*320,36));label(im,f'{rev} / n={n} t={float(F(n)/fps):.5f}',(j*320+4,3),14)
   if any(math.ceil(t*fps)==n for t in ev):ImageDraw.Draw(im).rectangle((0,31,959,35),fill='#e5b44b')
   frames.append(np.asarray(im))
  videos.append(encode('flash/'+name+'.mp4',frames,fps));numbers=sorted(set(max(0,min(N-1,math.ceil(t*fps)+d)) for t in ev for d in [-1,0,1]))
  imgs=[Image.fromarray(arrays[rev][n]) for rev in ['legacy','v4','v5'] for n in numbers];labels=[f'{rev} n{n} t{float(F(n)/fps):.5f}' for rev in ['legacy','v4','v5'] for n in numbers]
  sheet('flash/'+name+'.jpg',imgs,labels,cols=len(numbers),tile=(240,135))
  rows.append({'id':name,'fps':str(fps),'replay_rate':str(rate),'replay_events':replay_events,'output_events':[str(t) for t in ev],'kind':kind,'cases':detail,'video':videos[-1]['path'],'sheet':'flash/'+name+'.jpg','sample_frames':numbers,'scope':'pinned CPU eq and independent v4/v5 graphs on synthetic moving input; not live LoL'})
  print(name,flush=True)
 save('FLASH_RESULTS.json',{'groups':rows,'rendered_variants':len(rows)*3,'videos':videos,'v5_no_early_all':all(x['cases'][2]['status']=='PASS' for x in rows),'metric_threshold_rgb':0,'baseline':'same-frame eq=brightness=0 decoded input; preserves color-conversion control','gold_marker':'first CFR frame >= exact output event time; rate conversion is explicit'})

def zoom():
 e=extract_effects();rows=[];videos=[]
 for strength,light,moving in itertools.product([.15,.5,.9],[False,True],[False,True]):
  N=18;src=[]
  for n in range(N):
   im=bg((640,360),light,n if moving else 0);d=ImageDraw.Draw(im)
   for j,c in enumerate([(160,32,32),(32,160,32),(32,32,160)]):d.rectangle((70+j*150,70,170+j*150,160),fill=c)
   src.append(np.asarray(im.resize((1920,1080),Image.Resampling.NEAREST)))
  src=np.asarray(src);old=e['_build_video_effect_filters'](NS(video_effects={'zoom_blur':strength}),.6,[(.2,.62)],False)[0];graphs={'legacy':old,'normalized':old.replace(':scale=4',':scale=0')};arrays={};metrics=[]
  for rev,g in graphs.items():
   b=ff(['-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-vf',g+',scale=640:360:flags=lanczos','-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],src.tobytes());a=np.frombuffer(b,np.uint8).reshape(N,360,640,3);arrays[rev]=a
   metrics.append({'revision':rev,'graph':g,'sampled_mean_rgb':a.mean((0,1,2)).tolist(),'sampled_white_fraction':float((a.min(3)>250).mean()),'sampled_primary_patches_rgb':[a[-1,90:130,95+j*150:145+j*150].mean((0,1)).tolist() for j in range(3)],'status':'FAIL' if rev=='legacy' and (a.min(3)>250).mean()>.5 else 'REVIEW','scope':'full 1920 filter graph; metrics on 640x360 presentation frames'})
  name=f'zoom_{strength}_{"light" if light else "dark"}_{"moving" if moving else "static"}';frames=[]
  for n in range(N):
   im=Image.new('RGB',(1280,394),'#172333')
   for j,rev in enumerate(graphs):im.paste(Image.fromarray(arrays[rev][n]),(j*640,34));label(im,rev+' / strength '+str(strength),(j*640+6,3),16)
   frames.append(np.asarray(im))
  videos.append(encode('zoom/'+name+'.mp4',frames,30));nums=[0,1,8,17];sheet('zoom/'+name+'.jpg',[Image.fromarray(arrays[rev][n]) for rev in graphs for n in nums],[f'{rev} frame {n}' for rev in graphs for n in nums],4,(320,180));rows.append({'id':name,'strength':strength,'background':'light' if light else 'dark','moving':moving,'variants':metrics,'video':videos[-1]['path'],'sheet':'zoom/'+name+'.jpg'});print(name,flush=True)
 # Exact hard-cut diagnostic: temporal residual vs explicit state reset.
 src=np.zeros((12,90,160,3),np.uint8);src[:6]=[160,32,32];src[6:]=[32,32,160];g="format=gbrp,tmix=frames=3:weights='1 2 1':scale=0,format=rgb24"
 def tmix(a):return np.frombuffer(ff(['-f','rawvideo','-pix_fmt','rgb24','-s','160x90','-r','30','-i','pipe:0','-vf',g,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],a.tobytes()),np.uint8).reshape(a.shape)
 continuous=tmix(src);reset=np.concatenate([tmix(src[:6]),tmix(src[6:])]);sheet('zoom/scene_cut_history.jpg',[Image.fromarray(a[n]).resize((320,180)) for a in [src,continuous,reset] for n in [5,6,7,8]],[f'{rev} n{n}' for rev in ['source','continuous','reset'] for n in [5,6,7,8]],4,(320,180))
 save('ZOOM_RESULTS.json',{'groups':rows,'videos':videos,'history_cut_frame':6,'history_continuous_frame6_rgb':continuous[6,0,0].tolist(),'history_reset_frame6_rgb':reset[6,0,0].tolist(),'history_reset_matches_new_source':bool(np.array_equal(reset[6],src[6])),'true_radial_blur_evaluated':False,'GPU_actual_render':'NOT_RUN','scope':'synthetic full CPU graph and separate tmix history diagnostic; candidate unadopted'})
if __name__=='__main__':
 for name in sys.argv[1:] or ['flash','zoom']:globals()[name]()
