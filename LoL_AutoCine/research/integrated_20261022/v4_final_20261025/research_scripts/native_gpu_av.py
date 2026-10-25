from lab_common import *
import numpy as np,sys,os,time,hashlib,importlib
sys.dont_write_bytecode=True
(W/'tmp').mkdir(exist_ok=True);os.environ['TMP']=str((W/'tmp').resolve());os.environ['TEMP']=os.environ['TMP']
rows=[]
# Probe the unchanged real GPU module against artificial input. No app launch.
try:
 sys.path.insert(0,str((OLD/'source_readonly/LoL_AutoCine').resolve()));g=importlib.import_module('core.gpu_full');ok,reason=g.full_runtime_probe(FF)
 rows.append({'test':'immutable_GPUFullStage_runtime_probe','status':'PASS' if ok else 'BLOCKED','observed':reason,'scope':'real module isolated artificial 64x64/3frames; not LoL or all GPU FX'})
except Exception as e:rows.append({'test':'immutable_GPUFullStage_runtime_probe','status':'BLOCKED','exception':type(e).__name__,'observed':str(e),'scope':'import/runtime dependency barrier; no product launch'})
# Independent FFmpeg OpenCL capability alternative, distinct from AutoCine shader.
r=ff(['-init_hw_device','opencl=ocl:,device_type=gpu','-filter_hw_device','ocl','-f','lavfi','-i','color=c=blue:s=64x64:r=30:d=0.2','-vf','format=rgba,hwupload,avgblur_opencl=sizeX=3:sizeY=3,hwdownload,format=rgba','-frames:v','3','-f','null','-'])
rows.append({'test':'ffmpeg_OpenCL_avgblur_alternative','status':'PASS' if not r.returncode else 'BLOCKED','return_code':r.returncode,'observed':r.stderr.decode(errors='replace')[-2400:],'scope':'3 artificial frames, not AutoCine CPU/GPU perceptual parity'})
enc=[]
for codec in ['libx264','h264_nvenc']:
 for dur in [2,5]:
  out=O/f'ENCODE_{codec}_{dur}s_1080p60.mp4';start=time.perf_counter();r=ff(['-f','lavfi','-i',f'testsrc2=s=1920x1080:r=60:d={dur}','-an','-c:v',codec,*(['-preset','ultrafast','-crf','23'] if codec=='libx264' else ['-preset','p4','-cq','23']),'-pix_fmt','yuv420p',str(out)]);wall=time.perf_counter()-start
  decoded=0
  if not r.returncode:
   d=ff(['-i',str(out),'-vf','scale=32:18','-f','rawvideo','-pix_fmt','gray','pipe:1']);decoded=len(d.stdout)//(32*18)
  enc.append({'encoder':codec,'input_seconds':dur,'expected_frames':dur*60,'decoded_frames':decoded,'wall_seconds':wall,'return_code':r.returncode,'status':'PASS' if not r.returncode and decoded==dur*60 else 'FAIL','stderr':r.stderr.decode(errors='replace')[-1500:],'quality_comparison':'CQ23 and CRF23 are not equivalent; no quality winner claimed'})
save('GPU_ENCODE_PROBE_V4.json',{'gpu_fx_probes':rows,'encodes':enc,'not_validated':['LoL rendering contention','long jobs','process audio capture','all22 CPU/GPU FX quality parity']})
av=[]
for fps in [30,60]:
 for rate in [.5,1.,2.]:
  for audio_codec in ['pcm_s16le','aac']:
   out=O/f'AV_{fps}fps_{rate}x_{audio_codec}.mkv'
   inp="color=c=black:s=320x180:r="+str(fps)+":d=2,drawbox=color=white:t=fill:enable='between(t,0.5,0.6)'"
   aud=r'aevalsrc=if(between(t\,0.5\,0.6)\,0.5*sin(2*PI*1000*t)\,0):s=48000:d=2'
   r=ff(['-f','lavfi','-i',inp,'-f','lavfi','-i',aud,'-filter_complex',f'[0:v]setpts=PTS/{rate}[v];[1:a]atempo={rate}[a]','-map','[v]','-map','[a]','-r',str(fps),'-c:v','libx264','-preset','ultrafast','-c:a',audio_codec,str(out)])
   item={'fps':fps,'rate':rate,'audio_codec':audio_codec,'return_code':r.returncode,'expected_marker_seconds':.5/rate,'stderr':r.stderr.decode(errors='replace')[-1000:]}
   if not r.returncode:
    v=ff(['-i',str(out),'-vf','scale=16:9,format=gray','-f','rawvideo','-pix_fmt','gray','pipe:1']);a=ff(['-i',str(out),'-vn','-ar','48000','-ac','1','-f','f32le','pipe:1']);va=np.frombuffer(v.stdout,np.uint8).reshape(-1,9,16).mean((1,2));aa=np.frombuffer(a.stdout,np.float32);vi=np.flatnonzero(va>200);ai=np.flatnonzero(np.abs(aa)>.1)
    vt=float(vi[0]/fps) if len(vi) else None;at=float(ai[0]/48000) if len(ai) else None;item.update(video_frames=len(va),audio_samples=len(aa),video_marker=vt,audio_marker=at,offset_ms=(at-vt)*1000 if vt is not None and at is not None else None,status='MEASURED_ARTIFICIAL_NOT_LOL_PASS')
   av.append(item)
save('AV_SYNC_MATRIX_V4.json',{'cases':av,'count':len(av),'method':'synthetic simultaneous white pulse and 1kHz burst; decode threshold luminance>200 / audio abs>.1; codec/tempo transients included','real_LoL_audio_pass':False})
print(json.dumps({'gpu_probes':rows,'encodes':len(enc),'AV_cases':len(av)}))
