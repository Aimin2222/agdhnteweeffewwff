from lab_common import *
import re,numpy as np
rows=[]
for c in load(O/'AV_SYNC_MATRIX_V4.json')['cases']:
 p=O/f"AV_{c['fps']}fps_{c['rate']}x_{c['audio_codec']}.mkv"
 v=ff(['-loglevel','info','-copyts','-i',str(p),'-an','-vf','scale=16:9,format=gray,showinfo','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','pipe:1'])
 a=ff(['-loglevel','info','-copyts','-i',str(p),'-vn','-af','ashowinfo','-ar','48000','-ac','1','-f','f32le','pipe:1'])
 pts=[float(x) for x in re.findall(r'n:\s*\d+.*?pts_time:([\d.e+-]+)',v.stderr.decode(errors='replace'))]
 ab=[(float(t),int(n)) for t,n in re.findall(r'pts_time:([\d.e+-]+).*?nb_samples:(\d+)',a.stderr.decode(errors='replace'))]
 va=np.frombuffer(v.stdout,np.uint8).reshape(-1,9,16).mean((1,2));aa=np.frombuffer(a.stdout,np.float32);vi=np.flatnonzero(va>200);ai=np.flatnonzero(np.abs(aa)>.1)
 vt=pts[int(vi[0])] if len(vi) and len(pts)==len(va) else None
 at=ab[0][0]+int(ai[0])/48000 if ab and len(ai) else None
 # Exact sample PTS accounting, including discontinuities between decoded audio blocks.
 if ab and len(ai):
  ix=int(ai[0]);total=0
  for t,n in ab:
   if total<=ix<total+n:at=t+(ix-total)/48000;break
   total+=n
 offset=1000*(at-vt) if vt is not None and at is not None else None
 rows.append(dict(fps=c['fps'],rate=c['rate'],codec=c['audio_codec'],video_pts_count=len(pts),decoded_frames=len(va),audio_blocks=len(ab),audio_sample_count=sum(n for _,n in ab),video_marker_pts=vt,audio_marker_pts=at,offset_ms=offset,frame_order_only_previous_offset_ms=c.get('offset_ms'),status='WITHIN_50MS_FIXTURE' if offset is not None and abs(offset)<=50 else 'REVIEW_FIXTURE',limit='threshold onset includes atempo transient and frame quantization; not LoL capture or product sync PASS'))
save('AV_PTS_REVIEW_V4.json',dict(cases=rows,method='decode with copyts, video showinfo PTS matched to threshold frame; audio block ashowinfo PTS + within-block sample index; no assumed CFR start',real_LoL_pass=False))
print(json.dumps(rows))
