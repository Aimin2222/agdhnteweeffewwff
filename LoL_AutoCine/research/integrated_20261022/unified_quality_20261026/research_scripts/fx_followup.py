from common import *
import time
from fx_extended import scope
def run():
 N=18;src=[];centers=[]
 for n in range(N):
  im=bg((640,360),False,n);c=(100+20*n,150);centers.append(c);d=ImageDraw.Draw(im);d.ellipse((c[0]-20,c[1]-20,c[0]+20,c[1]+20),fill=(210,120,50));src.append(np.asarray(im))
 src=np.asarray(src);native=np.asarray([np.asarray(Image.fromarray(x).resize((1920,1080),Image.Resampling.NEAREST)) for x in src]);g=scope['_build_video_effect_filters'](NS(video_effects={'zoom_blur':.5}),.6,[(.2,.6)],False)[0].replace(':scale=4',':scale=0')
 b=ff(['-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-vf',g+',scale=640:360','-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],native.tobytes());temporal=np.frombuffer(b,np.uint8).reshape(N,360,640,3)
 spatial_fixed=[];spatial_track=[]
 for n,a in enumerate(src):
  im=Image.fromarray(a)
  for center,out in [((320,180),spatial_fixed),(centers[n],spatial_track)]:
   acc=[]
   for f in [1,1.015,1.03,1.045,1.06]:acc.append(np.asarray(im.transform(im.size,Image.Transform.AFFINE,(f,0,center[0]*(1-f),0,f,center[1]*(1-f)),Image.Resampling.BILINEAR)).astype(float))
   out.append(np.rint(np.mean(acc,axis=0)).astype(np.uint8))
 frames=[]
 for n in range(N):
  im=Image.new('RGB',(1280,790),'#172333')
  for j,a in enumerate([src[n],temporal[n],spatial_fixed[n],spatial_track[n]]):
   xy=(j%2*640,35+j//2*395);im.paste(Image.fromarray(a),xy);label(im,['source moving target','CPU normalized temporal zoom','new spatial fixed center','new spatial declared target center'][j],(xy[0]+8,xy[1]-30),17)
  frames.append(np.asarray(im))
 video=encode('A3_fx/zoom_center_tracking_compare.mp4',frames,30);sheet('A3_fx/zoom_center_tracking_compare.png',[Image.fromarray(frames[i]) for i in [0,8,17]],[f'n{i}' for i in [0,8,17]],1,(1280,790));save('A3_fx/ZOOM_CENTER_TRACKING.json',{'centers':centers,'video':video,'status':'REVIEW','tracking':'declared synthetic center, no detector','spatial_vs_temporal':'different algorithms; not equivalent fixes','real_game_tracking':'NOT_RUN','GPU':'NOT_RUN'})
 combos=[]
 for effects in [{'motion_camera':.15,'camera_shake':.15},{'glitch':.15,'chroma_leak':.15},{'focus_blur':.15,'glint':.15},{'zoom_blur':.15,'flash':.15}]:
  graph=','.join(scope['_build_video_effect_filters'](NS(video_effects=effects),.6,[(.2,.6)],False));original=graph
  if 'zoom_blur' in effects:graph=graph.replace(':scale=4',':scale=0')
  name='_'.join(effects);start=time.perf_counter()
  try:
   b=ff(['-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-vf',graph+',scale=640:360','-frames:v',N,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],native.tobytes());a=np.frombuffer(b,np.uint8).reshape(N,360,640,3);elapsed=time.perf_counter()-start;sheet(f'A3_fx/combo_{name}.png',[Image.fromarray(a[i]) for i in [0,6,10,17]],[f'{name} n{i}' for i in [0,6,10,17]],2,(640,360));combos.append({'effects':effects,'render':'PASS','quality':'REVIEW','elapsed_seconds_single_run':elapsed,'white_fraction':float((a.min(3)>250).mean()),'original_graph':original,'research_graph':graph,'candidate_change':'zoom tmix normalization only where applicable; Flash legacy timing remains in this combo'})
  except Exception as e:combos.append({'effects':effects,'render':'FAIL','error':str(e)})
 save('A3_fx/COMBINATION_RESULTS.json',combos)
 # Separate RGB headroom candidate: causal multiplicative light, not adopted eq replacement.
 color=np.array([210,175,120.]);imgs=[];metrics=[]
 for strength in [.15,.5,.9]:
  gain=1+(.18+.65*strength);bounded=min(gain,254/color.max());result=np.rint(color*bounded).astype(np.uint8);metrics.append({'strength':strength,'source_rgb':color.tolist(),'candidate_rgb':result.tolist(),'clipped_channels':int((result==255).sum()),'gain_used':bounded,'status':'PASS' if max(result)<255 else 'FAIL','scope':'one solid RGB patch; alternate perceptual look and color management unvalidated'})
  imgs.append(Image.new('RGB',(320,180),tuple(result)))
 sheet('A3_fx/flash_headroom_patch.png',imgs,[f'RGB gain candidate {x["strength"]}' for x in metrics],3,(320,180));save('A3_fx/FLASH_HEADROOM_FIXTURE.json',{'cases':metrics,'candidate_adopted':False,'causal_gate':'apply only after V5 event gate; this patch test does not itself test scheduling'})
if __name__=='__main__':run()
