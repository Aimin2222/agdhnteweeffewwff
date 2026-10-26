"""Independent research fixtures. Never imports or writes the application."""
from pathlib import Path
import json,hashlib,subprocess,ast,math,wave,re,sys,os
from types import SimpleNamespace
from fractions import Fraction as F
import numpy as np
R=Path(os.environ.get('AUTOCINE_RESEARCH_ROOT',Path(__file__).resolve().parents[2]));O=Path(os.environ.get('AUTOCINE_RESEARCH_OUTPUT',R/'work/autocine_implementation_specs_20261026/rerun_results'));O.mkdir(exist_ok=True,parents=True)
S=R/'work/autocine_integrated_research_20261022/source_readonly/LoL_AutoCine/core/effects.py'
FF=Path(os.environ.get('AUTOCINE_RESEARCH_FFMPEG','C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb/work/runtime-bin/ffmpeg.exe'))
def save(n,a):(O/n).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
def ff(args):
 p=subprocess.run([str(FF),'-hide_banner','-nostdin','-loglevel','info',*args],capture_output=True,timeout=45)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3500:])
 return p
def flash():
 scope={'math':math,'Template':object}
 for n in ast.parse(S.read_text('utf-8-sig')).body:
  if isinstance(n,ast.FunctionDef) and n.name in ['_enable_expr','_build_video_effect_filters']:exec(compile(ast.Module(body=[n],type_ignores=[]),str(S),'exec'),scope)
 def render(graph,fps):
  p=ff(['-f','lavfi','-i',f'color=c=gray:s=64x36:r={fps}:d=2','-vf',','.join(graph+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1']);return np.frombuffer(p.stdout,np.uint8).reshape(-1,36,64)
 rows=[]
 patterns={'single':[.5],'two_short':[.5,.6],'duplicates':[.5,.5],'subframe':[.503,.511],'irregular':[.1,.43,1.0,1.89],'dense':[.4+i*.02 for i in range(8)],'millisecond_rounding':[.5004,.6004]}
 for fps in [30,60]:
  baseline=render([],fps)
  for strength in [.15,.5,.9]:
   for name,ev in patterns.items():
    amp=float(f'{.18+.65*strength:.3f}');events=[(t,min(2,t+.42)) for t in ev]
    old=scope['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':strength}),2,events,False)
    def candidate(events):
     ts=[f'if(gte(t,{t:.3f}),{amp:.3f}*exp(-18*abs(t-{t:.3f})),0)' for t in events];b=ts[0]
     for t in ts[1:]:b=f'max({b},{t})'
     gate=scope['_enable_expr']([(t,min(2,t+.42)) for t in events],after=.15)
     return [f'eq=brightness=\'{b}\':eval=frame:enable={gate}']
    a=render(candidate(ev),fps);b=render(old,fps);times=np.arange(len(a))/fps;pre=times<min(ev);prefix=times<(ev[1] if len(ev)>1 else 2)
    previous=render(candidate(ev[:1]),fps) if len(ev)>1 else b
    dedup=render(candidate(sorted(set(ev))),fps) if name=='duplicates' else a
    checks={'all_frames_decoded':len(a)==fps*2,'no_pre_first_leak':bool(np.array_equal(a[pre],baseline[pre])),'no_future_event_influence':bool(np.array_equal(a[prefix],previous[prefix])),'duplicate_idempotence':bool(np.array_equal(a,dedup))}
    if name=='single':checks['single_bit_equal_legacy']=bool(np.array_equal(a,b))
    v5=None
    if name=='millisecond_rounding':
     terms=[f'if(gte(n,{math.ceil(F(str(t))*fps)}),{amp:.3f}*exp(-18*max(0,t-{t:.9f})),0)' for t in ev];expr=f'max({terms[0]},{terms[1]})';gate=scope['_enable_expr'](events,after=.15);graph=[f'eq=brightness=\'{expr}\':eval=frame:enable={gate}'];fixed=render(graph,fps)
     pastgraph=[f'eq=brightness=\'{terms[0]}\':eval=frame:enable='+scope['_enable_expr'](events[:1],after=.15)];past=render(pastgraph,fps)
     v5={'revision':'research_v5_CFR_tick_gate_unadopted','graph':graph,'no_pre_first_leak':bool(np.array_equal(fixed[pre],baseline[pre])),'no_future_event_influence':bool(np.array_equal(fixed[prefix],past[prefix])),'event_start_frames':[math.ceil(F(str(t))*fps) for t in ev],'requires_CFR_and_output_time_map':True}
    rows.append({'fps':fps,'strength':strength,'case':name,'events':ev,'candidate_graph':candidate(ev),'legacy_graph':old,'checks':checks,'v5_tick_gate_probe':v5,'candidate_peak_gray':int(a.max()),'candidate_white_fraction':float((a==255).mean()),'legacy_peak_gray':int(b.max()),'sample_around_second':[{'t':float(times[i]),'legacy':float(b[i].mean()),'candidate':float(a[i].mean())} for i in range(len(a)) if len(ev)>1 and abs(times[i]-ev[1])<.04]})
    print('flash',fps,strength,name,flush=True)
 save('FLASH_BOUNDARY_RESULTS.json',{'scope':'synthetic CPU only; causal v4 candidate unadopted','cases':rows,'cases_count':len(rows),'assertions':sum(len(x['checks']) for x in rows),'failures':[x for x in rows if not all(x['checks'].values())],'saturation_is_separate_quality_issue':True,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest()})
def zoom():
 rows=[]
 for mode in ['flat32','flat96','flat180','moving_step']:
  a=np.full((8,36,64,3),int(mode[4:]) if mode.startswith('flat') else 0,np.uint8)
  if mode=='moving_step':
   for i in range(3,8):a[i,:,max(0,(i-3)*6):max(0,(i-3)*6)+12]=180
  src=O/('_tmix_'+mode+'.rgb');src.write_bytes(a.tobytes())
  for scale in [4,0,.25]:
   graph=f"format=gbrp,tmix=frames=3:weights='1 2 1':scale={scale},format=rgb24"
   p=ff(['-f','rawvideo','-pixel_format','rgb24','-video_size','64x36','-framerate','30','-i',str(src),'-vf',graph,'-frames:v','8','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);b=np.frombuffer(p.stdout,np.uint8).reshape(8,36,64,3)
   rows.append({'input':mode,'scale':scale,'graph':graph,'input_mean':float(a.mean()),'output_mean':float(b.mean()),'white_fraction':float((b==255).mean()),'all_frames_decoded':True,'flat_max_absolute_error':int(np.abs(b.astype(int)-a.astype(int)).max()) if mode.startswith('flat') else None,'first_nonzero_frame':next((i for i,z in enumerate(b) if np.any(z)),None),'frame_means':b.mean((1,2,3)).tolist()})
  src.unlink()
 save('TMIX_NORMALIZATION_RESULTS.json',{'scope':'isolated tmix stage, not full Zoom Blur or GPU/LoL; transient smear remains after normalization','cases':rows,'flat_normalized_identity_pass':all(x['flat_max_absolute_error']==0 for x in rows if x['input'].startswith('flat') and x['scale']!=4),'moving_input_has_no_pre_step_energy':all(x['first_nonzero_frame']==3 for x in rows if x['input']=='moving_step')})
def geometry():
 def contain(sw,sh,x,y,w,h):
  k=min(F(w,sw),F(h,sh));return k,F(x)+(F(w)-sw*k)/2,F(y)+(F(h)-sh*k)/2
 def rnd(x):return math.floor(x+F(1,2))
 rows=[]
 # Three reference rectangles, including a half-pixel and frame at right edge.
 rects=[[1527,84,339,116],[1500,72,384,128],[F(1,2),F(1,2),1,1]]
 for ow,oh in [(1920,1080),(1366,768),(1280,720)]:
  for vw,vh in [(1280,720),(1024,576),(800,600)]:
   for dpi in [F(1),F(5,4),F(3,2)]:
    k0,x0,y0=contain(1920,1080,0,0,ow,oh);k1,x1,y1=contain(ow,oh,0,0,vw,vh)
    for motion in ['instant','slide_left','slide_right','slide_up','slide_down','pop']:
     for progress in [F(0),F(1,2),F(1)]:
      for n,rr in enumerate(rects):
       x,y,w,h=map(F,rr);dx=dy=F(0)
       u=1-progress;ease=u*u*(3-2*u)
       if motion=='slide_left':dx=-1940*ease
       if motion=='slide_right':dx=1940*ease
       if motion=='slide_up':dy=1100*ease
       if motion=='slide_down':dy=-1100*ease
       if motion=='pop':
        elapsed=float(progress)*.260;dx=F(str(16*math.exp(-18*elapsed)*math.cos(28*elapsed)))
       corners=[(x+dx,y+dy),(x+dx+w,y+dy+h)];exp=[];mir=[]
       for px,py in corners:
        ex,ey=px*k0+x0,py*k0+y0
        exp.append([rnd((ex*k1+x1)*dpi),rnd((ey*k1+y1)*dpi)])
        mir.append([math.floor(float((px*k0*k1+x0*k1+x1)*dpi)+.5),math.floor(float((py*k0*k1+y0*k1+y1)*dpi)+.5)])
       err=max(abs(a-b) for a,b in zip(sum(exp,[]),sum(mir,[])))
       rows.append({'output':[ow,oh],'viewport':[vw,vh],'dpi':str(dpi),'motion':motion,'phase':str(progress),'rect_id':n,'max_edge_error_device_px':err})
 save('COORDINATE_CONTRACT_RESULTS.json',{'scope':'reference math only, no production renderer called','cases':len(rows),'max_error':max(x['max_edge_error_device_px'] for x in rows),'failures':[x for x in rows if x['max_edge_error_device_px']>1],'rounding':'half-up once at final pixel edges','clip_offscreen_motion_only_at_destination':True,'cases_detail':rows})
def audio():
 folder=O/'audio_lab';folder.mkdir(exist_ok=True);rows=[];sr=48000;n=sr*3;t=np.arange(n)/sr
 fixtures={
 'silence':np.zeros((n,2)),
 'tone_440':np.stack([.25*np.sin(2*np.pi*440*t),.125*np.sin(2*np.pi*440*t)],1),
 'anti_phase':np.stack([.25*np.sin(2*np.pi*440*t),-.25*np.sin(2*np.pi*440*t)],1),
 'clip_plateau':np.clip(np.stack([1.5*np.sin(2*np.pi*440*t)]*2,1),-1,1),
 'dc_offset':np.stack([.1+.1*np.sin(2*np.pi*440*t)]*2,1),
 }
 rng=np.random.default_rng(20261026)
 for name,offset in [('pulses',0),('stereo_delay',.03)]:
  a=np.zeros((n,2));
  for start in [.5,1,1.5,2]:
   z=rng.uniform(-.7,.7,960)
   for c,dt in [(0,0),(1,offset)]:idx=round((start+dt)*sr);a[idx:idx+960,c]=z
  fixtures[name]=a
 version=subprocess.run([str(FF),'-version'],capture_output=True).stdout.decode(errors='replace').splitlines()[0]
 caps=subprocess.run([str(FF),'-hide_banner','-filters'],capture_output=True).stdout.decode(errors='replace')
 save('AUDIO_ENVIRONMENT.json',{'ffmpeg_version':version,'ffmpeg_sha256':hashlib.sha256(FF.read_bytes()).hexdigest(),'available_filters':{x:bool(re.search(r'\b'+x+r'\b',caps)) for x in ['astats','ebur128','silencedetect','axcorrelate','atempo']},'numpy':np.__version__,'extra_packages_installed':False,'audio_output_used':False,'local_signal_analysis_supported':True,'reference_video_audio_assets_obtained':0,'reference_audio_20_status':'NOT_RUN: no local source audio or permitted observed download asset in this research evidence','semantic_listening_available':False})
 for name,a in fixtures.items():
  path=folder/(name+'.wav');pcm=np.round(np.clip(a,-1,1)*32767).astype('<i2')
  with wave.open(str(path),'wb') as z:z.setnchannels(2);z.setsampwidth(2);z.setframerate(sr);z.writeframes(pcm.tobytes())
  p=ff(['-i',str(path),'-af','astats=metadata=1:reset=0,ebur128=peak=true,silencedetect=noise=-50dB:d=0.1','-f','null','-']);(folder/(name+'_ffmpeg.log')).write_bytes(p.stderr)
  b=pcm.astype(float)/32768;rms=np.sqrt((b*b).mean(0));peak=np.max(abs(b),axis=0);active=[]
  for c in range(2):
   env=np.max(abs(b[:len(b)//480*480,c].reshape(-1,480)),1);ons=np.flatnonzero((env>.1)&~np.r_[False,env[:-1]>.1]);active.append((ons*.01).tolist())
  lag=None
  if name=='stereo_delay':
   # FFT cross correlation. Known direction: positive right delay.
   N=1<<(2*n-1).bit_length();cc=np.fft.irfft(np.fft.rfft(b[:,1],N)*np.conj(np.fft.rfft(b[:,0],N)),N);ix=int(cc.argmax());lag=(ix if ix<n else ix-N)/sr
  oracle={'silence':bool(np.max(peak)==0),'tone_440':bool(np.allclose(rms,[.25/math.sqrt(2),.125/math.sqrt(2)],atol=2/32768)),'anti_phase':bool(np.sqrt(np.mean(b.mean(1)**2))<1e-9 and rms[0]>.17),'clip_plateau':bool((abs(b)>=.999).mean()>.2),'dc_offset':bool(np.allclose(b.mean(0),[.1,.1],atol=2/32768)),'pulses':active==[[.5,1,1.5,2],[.5,1,1.5,2]],'stereo_delay':abs(lag-.03)<1/sr if lag is not None else False}[name]
  rows.append({'id':name,'sr':sr,'channels':2,'sample_frames':n,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sample_peak':peak.tolist(),'rms':rms.tolist(),'rms_dbfs':[20*math.log10(x) if x else None for x in rms],'dc':b.mean(0).tolist(),'sample_near_fullscale_fraction':(abs(b)>=.999).mean(0).tolist(),'mono_rms':float(np.sqrt(np.mean(b.mean(1)**2))),'active_onset_10ms_candidates':active,'right_delay_seconds':lag,'loudness_summary':p.stderr.decode(errors='replace').split('Summary:')[-1].strip(),'oracle_pass':oracle})
 save('AUDIO_FIXTURE_RESULTS.json',{'scope':'7 synthetic WAV fixtures, no reference montage audio and no listening','fixtures':rows,'all_oracles_pass':all(x['oracle_pass'] for x in rows),'silence_dbfs_serialized_as_null':True,'onset_is_not_a_verified_music_beat':True})
 # Probe only existing research media, not arbitrary user folders.
 inventory=[]
 for root in [R/'outputs/autocine_research_v4_20261025',R/'outputs/autocine_v4_addendum_20261025']:
  for path in sorted(root.rglob('*')):
   if path.suffix.lower() not in ['.wav','.flac','.mp3','.aac','.m4a','.mp4','.mkv','.ogg']:continue
   p=subprocess.run([str(FF),'-hide_banner','-nostdin','-i',str(path)],capture_output=True,timeout=15);txt=p.stderr.decode(errors='replace');streams=[z.strip() for z in txt.splitlines() if 'Audio:' in z]
   inventory.append({'path':path.relative_to(R).as_posix(),'bytes':path.stat().st_size,'audio_streams':streams,'scope':'existing synthetic research media, not original reference work audio'})
 save('LOCAL_AUDIO_MEDIA_INVENTORY.json',{'searched_roots':['outputs/autocine_research_v4_20261025','outputs/autocine_v4_addendum_20261025'],'files':inventory,'with_audio':sum(bool(x['audio_streams']) for x in inventory),'reference_works_matched':0,'probe_exit_1_without_output_is_expected':True})
def queue():
 a=json.loads((R/'outputs/autocine_final_research_v3_20261024/ASSET_FULL_QA_V2.json').read_text('utf-8-sig'));rows=[]
 for x in a['items']:
  reasons=[]
  if x['number']=='004':reasons.append('SOURCE_004_REFERENCE_CONSTRAINT_CHECK')
  if x.get('border_solid_ge128',0):reasons.append('SOLID_EDGE_CONTACT')
  if x.get('border_visible_gt8',0):reasons.append('SOFT_EDGE_CONTACT')
  if min(x['width']/1920,x['height']/1080)<1:reasons.append('CHECK_RENDERED_SIZE_NOT_CANVAS_SIZE')
  if x.get('transparent_pixels_with_nonzero_rgb',0):reasons.append('RESAMPLE_ALPHA_FRINGE_CHECK')
  priority='P0' if x['number']=='004' or x.get('border_solid_ge128',0) else ('P1' if x['kind']=='effect' or x.get('border_visible_gt8',0) else 'P2')
  rows.append({'kind':x['kind'],'id':x['id'],'path':x['path'],'source_sha256':x['actual_sha256'],'catalog_status_unchanged':x['catalog_status'],'priority':priority,'reasons':reasons,'not_a_failure_verdict':True,'visual_backgrounds':['bright','dark','high_chroma','HUD-motion'],'required_next_check':'actual output-size compositing, temporal playback, portrait boundary source confirmation where applicable','assigned_reviewer':None,'new_manual_visual_review_this_stage':False})
 from collections import Counter
 save('ASSET_REVIEW_QUEUE.json',{'frames':sum(x['kind']=='frame' for x in rows),'fx':sum(x['kind']=='effect' for x in rows),'priority_counts':dict(Counter(x['priority'] for x in rows)),'catalog_status_counts':{k:dict(Counter(x['catalog_status_unchanged'] for x in rows if x['kind']==k)) for k in ['frame','effect']},'criteria':'mechanical flags inherited from V2; priority is an explicit new research triage, not approval or confirmed clipping','items':rows})
if __name__=='__main__':
 for name in sys.argv[1:] or ['flash','zoom','geometry','audio','queue']:
  globals()[name]();print('completed',name,flush=True)
