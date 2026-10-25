from pathlib import Path
import subprocess,json,re,hashlib,csv
import numpy as np
R=Path(__file__).resolve().parents[2]
O=R/'outputs/autocine_v4_addendum_20261025'; O.mkdir(exist_ok=True)
FF='C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb/work/runtime-bin/ffmpeg.exe'
def ff(args):
 p=subprocess.run([FF,'-hide_banner','-loglevel','info','-y',*args],capture_output=True,timeout=90)
 if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
 return p
rows=[]
for fps in [30,60]:
 for onset in [.5,.517]:
  for length in [.1,.3]:
   for mode in ['atempo_pcm','atempo_aac','resample_pitch_control','atempo_passthrough_pts','atempo_explicit_fps']:
    if length==.3 and mode in ['atempo_passthrough_pts','atempo_explicit_fps']: continue
    rate=2;codec='aac' if mode.endswith('aac') else 'pcm_s16le'
    af='asetrate=96000,aresample=48000' if mode.startswith('resample') else 'atempo=2'
    vf=f'setpts=PTS/{rate}'+(f',fps={fps}:start_time=0' if mode=='atempo_explicit_fps' else '')
    timing=['-fps_mode','passthrough'] if mode in ['atempo_passthrough_pts','atempo_explicit_fps'] else ['-r',str(fps)]
    name=f'control_{fps}_{onset}_{length}_{mode}'; dest=O/(name+'.mkv')
    vi=f"color=c=black:s=160x90:r={fps}:d=2,drawbox=color=white:t=fill:enable='between(t,{onset},{onset+length})'"
    au=f'aevalsrc=if(between(t\\,{onset}\\,{onset+length})\\,0.5*sin(2*PI*1000*t)\\,0):s=48000:d=2'
    command=['-f','lavfi','-i',vi,'-f','lavfi','-i',au,'-filter_complex',f'[0:v]{vf}[v];[1:a]{af}[a]','-map','[v]','-map','[a]',*timing,'-c:v','libx264','-preset','ultrafast','-c:a',codec,str(dest)]
    ff(command)
    v=ff(['-copyts','-i',str(dest),'-an','-vf','scale=16:9,format=gray,showinfo','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','pipe:1'])
    a=ff(['-copyts','-i',str(dest),'-vn','-af','ashowinfo','-ar','48000','-ac','1','-f','f32le','pipe:1'])
    vp=[float(t) for t in re.findall(r'n:\s*\d+.*?pts_time:([\d.e+-]+)',v.stderr.decode(errors='replace'))]
    ab=[(float(t),int(n)) for t,n in re.findall(r'pts_time:([\d.e+-]+).*?nb_samples:(\d+)',a.stderr.decode(errors='replace'))]
    va=np.frombuffer(v.stdout,np.uint8).reshape(-1,9,16).mean((1,2));aa=np.frombuffer(a.stdout,np.float32)
    assert len(vp)==len(va) and sum(n for t,n in ab)==len(aa)
    ix=np.flatnonzero(va>200);vt=vp[int(ix[0])] if len(ix) else None
    thresholds=[]
    for threshold in [.01,.05,.1,.2]:
     ai=np.flatnonzero(np.abs(aa)>threshold); at=None;total=0
     if len(ai):
      index=int(ai[0])
      for t,n in ab:
       if total<=index<total+n: at=t+(index-total)/48000;break
       total+=n
     thresholds.append({'threshold':threshold,'audio_pts':at,'offset_ms':(at-vt)*1000 if at is not None and vt is not None else None,'audio_vs_ideal_ms':(at-onset/rate)*1000 if at is not None else None})
    rows.append({'id':name,'fps':fps,'source_onset':onset,'source_marker_duration':length,'rate':rate,'mode':mode,'codec':codec,'video_marker_pts':vt,'video_vs_ideal_ms':(vt-onset/rate)*1000 if vt is not None else None,'thresholds':thresholds,'decoded_frames':len(va),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'command':command,'scope':'synthetic diagnostic; resampling changes pitch and is not a product fix'})
    print(name,thresholds[2]['offset_ms'],flush=True)
result={'cases':rows,'executed':len(rows),'product_or_LoL_pass':False,'pts_accounting':'copyts; video showinfo; audio ashowinfo block PTS + sample index','resample_control_not_recommended_for_product':True}
(O/'AV_CONTROLS_ADDENDUM.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
with (O/'AV_CONTROLS_ADDENDUM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['id','fps','onset','duration','mode','threshold','video_pts','audio_pts','offset_ms','audio_vs_ideal_ms','video_vs_ideal_ms'])
 for r in rows:
  for t in r['thresholds']:w.writerow([r['id'],r['fps'],r['source_onset'],r['source_marker_duration'],r['mode'],t['threshold'],r['video_marker_pts'],t['audio_pts'],t['offset_ms'],t['audio_vs_ideal_ms'],r['video_vs_ideal_ms']])
