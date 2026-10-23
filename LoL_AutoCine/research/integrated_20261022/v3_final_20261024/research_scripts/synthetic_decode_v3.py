from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,numpy as np,hashlib
R=Path(__file__).resolve().parents[2];O=R/'outputs/autocine_final_research_v3_20261024';FF='${FFMPEG_EXE}'
def run(args):return subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],capture_output=True)
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',14);rows=[]
for motion in ['instant','slide_left','slide_right','slide_up','slide_down','pop']:
    p=O/f'MOTION_{motion}_SYNTHETIC_1080p60.mp4';r=run(['-i',str(p),'-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);assert r.returncode==0
    arr=np.frombuffer(r.stdout,np.uint8).reshape(-1,270,480,3);times=[0,.4,.5,.65,.667,1.0,1.8,1.817];sheet=Image.new('RGB',(1920,600),'#dfe7ef');d=ImageDraw.Draw(sheet);samples=[]
    for i,t in enumerate(times):
        idx=round(t*60);fr=arr[idx];mask=(fr[:,:,2]>140)&(fr[:,:,0]<90);yy,xx=np.nonzero(mask);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
        samples.append({'time':idx/60,'bbox_in_480x270':bbox,'blue_pixels':len(xx)});x=i%4*480;y=i//4*300;sheet.paste(Image.fromarray(fr),(x,y+24));d.text((x+5,y+3),f'{motion} frame={idx} t={idx/60:.4f}',font=font,fill='black')
    sheet.save(O/f'MOTION_{motion}_DECODED.jpg',quality=92)
    rows.append({'motion':motion,'decoded_frames':len(arr),'expected_frames':132,'constant_rate_input':60,'duration_by_decoded_count':len(arr)/60,'samples':samples,'result':'DECODED_ARTIFICIAL_VIDEO','product_compositor_verified':False})
r=run(['-f','lavfi','-i','testsrc2=s=1920x1080:r=60:d=1','-an','-c:v','h264_nvenc','-pix_fmt','yuv420p',str(O/'NVENC_ARTIFICIAL_SMOKE.mp4')])
gpu={'test':'single 1s artificial 1080p60 encode','encoder':'h264_nvenc','return_code':r.returncode,'result':'ENCODE_EXECUTED' if not r.returncode else 'UNAVAILABLE_OR_FAILED','stderr':r.stderr.decode(errors='replace')[-1200:],'not_tested':['GPU FX','product capture','LoL rendering contention','long-run performance','audio capture']}
if r.returncode and (O/'NVENC_ARTIFICIAL_SMOKE.mp4').exists():(O/'NVENC_ARTIFICIAL_SMOKE.mp4').unlink()
# Synthetic simultaneous video flash and audio pulse, then matched speed change.
p=O/'AV_SYNC_ARTIFICIAL.mp4';r=run(['-f','lavfi','-i',"color=c=black:s=320x180:r=60:d=2,drawbox=color=white:t=fill:enable='between(t,0.5,0.6)'",'-f','lavfi','-i',"aevalsrc=if(between(t\,0.5\,0.6)\,0.5*sin(2*PI*1000*t)\,0):s=48000:d=2",'-c:v','libx264','-preset','ultrafast','-c:a','aac',str(p)])
av={'created_return_code':r.returncode,'stderr':r.stderr.decode(errors='replace')[-500:]}
if not r.returncode:
    ret=O/'AV_SYNC_RETIMED_0p5x.mp4';r=run(['-i',str(p),'-filter_complex','[0:v]setpts=2*PTS[v];[0:a]atempo=0.5[a]','-map','[v]','-map','[a]','-r','60','-c:v','libx264','-preset','ultrafast','-c:a','aac',str(ret)]);av['retime_return_code']=r.returncode
    if not r.returncode:
        v=run(['-i',str(ret),'-vf','scale=32:18,format=gray','-f','rawvideo','-pix_fmt','gray','pipe:1']);a=run(['-i',str(ret),'-vn','-ar','48000','-ac','1','-f','f32le','pipe:1']);vv=np.frombuffer(v.stdout,np.uint8).reshape(-1,18,32).mean(axis=(1,2));aa=np.frombuffer(a.stdout,np.float32);vi=np.flatnonzero(vv>200);ai=np.flatnonzero(np.abs(aa)>.1)
        av.update(video_flash_start=float(vi[0]/60) if len(vi) else None,audio_pulse_start=float(ai[0]/48000) if len(ai) else None,video_frames=len(vv),audio_samples=len(aa),scope='Artificial AAC/retime smoke only. Encoder delay/atempo transients measured, not actual LoL process audio or an end-to-end sync guarantee.')
(O/'MOTION_DECODED_RESULTS_V3.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8');(O/'ENCODE_AUDIO_SMOKE_V3.json').write_text(json.dumps({'gpu':gpu,'av':av},ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'motion_videos_decoded':len(rows),'nvenc_result':gpu['result'],'av':av}))
