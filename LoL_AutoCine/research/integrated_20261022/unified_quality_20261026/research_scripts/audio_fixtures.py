from common import *
import wave,re,shutil
def run():
 folder=O/'B3_audio';folder.mkdir(exist_ok=True);rate=48000;duration=3.;events=[.5,1.5,2.5];samples=np.zeros(int(duration*rate),dtype=np.float32)
 if (folder/'AV_FIXTURE_RESULTS.json').exists():shutil.copyfile(folder/'AV_FIXTURE_RESULTS.json',W/'audio_first_measurement_invalid_fps_assumption.json')
 for t in events:
  ix=int(t*rate);n=np.arange(2400);samples[ix:ix+len(n)]=.25*np.sin(2*np.pi*880*n/rate)*np.hanning(len(n))
 wav=folder/'synthetic_pulses_only.wav'
 with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((samples*32767).astype('<i2').tobytes())
 frames=[]
 for n in range(90):
  t=n/30;im=bg((320,180),False,n);d=ImageDraw.Draw(im)
  if any(e<=t<e+.05 for e in events):d.rectangle((0,0,319,179),fill='#eee')
  frames.append(np.asarray(im))
 tmp=W/'audio_video_source.mp4';ff(['-f','rawvideo','-pix_fmt','rgb24','-s','320x180','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',tmp],np.asarray(frames).tobytes())
 results=[]
 for name,vg,ag,audio in [('normal','setpts=PTS','anull',True),('slow_correct','setpts=2*PTS','atempo=0.5',True),('slow_wrong_audio','setpts=2*PTS','anull',True),('missing_audio','setpts=PTS','anull',False)]:
  out=folder/(name+'.mp4');args=['-i',tmp]
  if audio:args+=['-i',wav]
  args+=['-vf',vg,'-map','0:v','-c:v','libx264','-preset','veryfast','-crf','20']
  if audio:args+=['-map','1:a','-af',ag,'-c:a','aac','-b:a','128k']
  else:args+=['-an']
  ff(args+['-r','30','-fps_mode','cfr',out]);audio_duration=None;peaks=[]
  probe=subprocess.run([FF,'-hide_banner','-nostdin','-i',str(out),'-map','0:v:0','-vf','showinfo','-an','-f','null','-'],capture_output=True,timeout=30);assert probe.returncode==0
  pts=[float(v) for v in re.findall(r'pts_time:([^\s]+)',probe.stderr.decode(errors='replace'))];audio_present=bool(re.search(r'Stream #0:\d+.*Audio:',probe.stderr.decode(errors='replace')));assert audio_present==audio
  if audio:
   b=ff(['-i',out,'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','pipe:1']);a=np.frombuffer(b,'<f4');audio_duration=len(a)/rate
   # Envelope support in 10ms blocks; encoder delay may spread pulse boundaries.
   step=480;energy=np.sqrt(np.mean(a[:len(a)//step*step].reshape(-1,step)**2,axis=1));active=np.flatnonzero(energy>.01);starts=[int(i) for i in active if i==active[0] or i-1 not in set(active.tolist())] if len(active) else [];peaks=[s*.01 for s in starts]
  b=ff(['-i',out,'-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);nframes=len(b)//(320*180*3);assert len(pts)==nframes;arr=np.frombuffer(b,np.uint8).reshape(nframes,180,320,3);bright=arr.mean((1,2,3))>200;vstart=[pts[i] for i in range(nframes) if bright[i] and (i==0 or not bright[i-1])];video_duration=pts[-1]+1/30
  expected=[e*(2 if name.startswith('slow') else 1) for e in events];drift=abs(video_duration-audio_duration) if audio else None
  detected='missing_audio' if not audio else ('duration_mismatch' if drift>.10 else 'duration_matches')
  results.append({'id':name,'video_frames':nframes,'video_pts_measured_showinfo':pts,'audio_stream_measured':audio_present,'video_duration_decoded_CFR30':video_duration,'audio_duration_decoded':audio_duration,'duration_difference':drift,'duration_tolerance_seconds':.1,'video_flash_onsets':vstart,'audio_envelope_onsets_10ms':peaks,'expected_event_times':expected,'diagnostic':detected,'status':'PASS' if detected=={'normal':'duration_matches','slow_correct':'duration_matches','slow_wrong_audio':'duration_mismatch','missing_audio':'missing_audio'}[name] else 'FAIL','meaning':'diagnostic assertion; intentionally wrong/missing fixtures are not approved outputs','sha256':sha(out),'audio_source':'generated pulse waveform only, not game audio'})
 save('B3_audio/AV_FIXTURE_RESULTS.json',{'cases':results,'real_game_audio':'NOT_RUN','system_audio_recorded':False,'playback':False,'long_export_drift':'NOT_RUN','NVENC_GPU_compare':'NOT_RUN','scope':'actual AAC/MP4 mux/decode of synthetic pulses; not LoL capture or musical listening'})
 sheet('B3_audio/video_pulse_frames.png',[Image.fromarray(frames[n]) for n in [14,15,16,44,45,46]],[f'synthetic n{n}' for n in [14,15,16,44,45,46]],3,(320,180));print('audio fixtures',len(results),flush=True)
if __name__=='__main__':run()
