from common import *
import copy,itertools
sys.path.insert(0,str(S));from core import camera as c
def blocked(a,b,box):
 lo,hi=0.,1.
 for axis in range(2):
  d=b[axis]-a[axis]
  if abs(d)<1e-10:
   if not box[axis]<=a[axis]<=box[axis+2]:return False
  else:
   u,v=(box[axis]-a[axis])/d,(box[axis+2]-a[axis])/d;lo=max(lo,min(u,v));hi=min(hi,max(u,v))
 return bool(lo<=hi)
def pix(x,z):return (int(300+x*.20),int(320-z*.20))
def camera():
 trajectories=[];figs=[];videos=[];tests=[]
 for team,style in itertools.product(['BLUE','RED'],['third','third_cinema']):
  cases=[]
  for yaw,mode in itertools.product([0,90,180],[None,'fixed_auto','full_auto']):
   rig=c.RigInfo(mode='fps',third=True,h=(0,-1),pitch_axis='x',pitch_sign=-1,rot={'x':-32,'y':0,'z':0});original=copy.deepcopy(rig.__dict__)
   p=c.CameraPlan(style=style,rig=rig,team=team,side_yaw=c.side_yaw_for(team),third_yaw=yaw,kill_time=1.,kill_times=(1.,1.2,1.4),third_dist=950,third_elev=28);p.camera_control_mode=mode
   vals=[]
   for n in range(90):
    t=n/30;off=tuple(float(x) for x in p.offset_at(t));rot=p.rotation_at(t);vals.append({'t':t,'offset':off,'rotation':rot,'fov':float(p.fov_at(t)),'speed':float(p.speed_at(t))})
   finite=all(math.isfinite(z) for v in vals for z in [*v['offset'],v['fov'],v['speed'],*(v['rotation'] or {}).values()]);deltas=[math.dist(a['offset'],b['offset']) for a,b in zip(vals,vals[1:])];tests.append({'id':f'{team}_{style}_{yaw}_{mode}','numeric_finite':finite,'rig_input_unchanged':rig.__dict__==original,'max_offset_step_30fps':max(deltas),'live_TargetLock':'NOT_RUN','axis_calibration':'fixture only; unverified in LoL'})
   cases.append({'team':team,'style':style,'yaw':yaw,'mode':mode,'samples':vals})
  trajectories.extend(cases);movie=[]
  for n in range(90):
   im=Image.new('RGB',(1200,720),'#172333');d=ImageDraw.Draw(im);label(im,f'{team} / {style} / pinned source trajectories - SYNTHETIC WORLD',(12,4),21)
   for j,yaw in enumerate([0,90,180]):
    ox=j*400;d.rectangle((ox+4,48,ox+396,690),outline='#60758a');label(im,f'yaw {yaw} / XZ and height',(ox+14,52),18)
    center=(ox+200,340);d.ellipse((center[0]-6,center[1]-6,center[0]+6,center[1]+6),fill='#65dcab')
    for mode,color in [(None,'#ecba5f'),('fixed_auto','#83c4ff'),('full_auto','#e78eca')]:
     case=next(x for x in cases if x['yaw']==yaw and x['mode']==mode);pts=[(ox+200+v['offset'][0]*.16,340+v['offset'][2]*.16) for v in case['samples'][:n+1]]
     if len(pts)>1:d.line(pts,fill=color,width=2)
     px,py=pts[-1];d.line((px,py,*center),fill=color,width=1);d.ellipse((px-4,py-4,px+4,py+4),fill=color);v=case['samples'][n];idx=[None,'fixed_auto','full_auto'].index(mode);label(im,f'{mode or "adopted baseline"}: H={v["offset"][1]:.1f}',(ox+14,560+idx*32),14,color)
   label(im,'No Replay API writes / TargetLock packet preservation is not real target tracking',(12,694),16)
   movie.append(np.asarray(im))
  name=f'camera/{team}_{style}.mp4';videos.append(encode(name,movie,30));figs.append(Image.fromarray(movie[45]));print('camera',team,style,flush=True)
 sheet('camera/adopted_camera_trajectories.jpg',figs,[f'{a} {b}' for a,b in itertools.product(['BLUE','RED'],['third','third_cinema'])],2,(600,360))
 # Actual source limiter, copy/attachment preservation at 90 and 180 degree steps.
 guard=[]
 for yaw in [90,180]:
  prev={'fieldOfView':60.,'selectionOffset':{'x':0.,'y':500.,'z':0.},'cameraRotation':{'x':0.,'y':0.,'z':0.},'selectionName':'Fixture-P1','cameraAttached':True};samples=[]
  target=copy.deepcopy(prev);target['cameraRotation']['x']=yaw;target['selectionOffset']['x']=900
  for n in range(90):
   prev=c.limit_camera_post(target,prev,1/30,slow_api=True);samples.append(copy.deepcopy(prev))
  guard.append({'yaw':yaw,'samples':samples,'attachment_fields_preserved':all(x['cameraAttached'] is True and x['selectionName']=='Fixture-P1' for x in samples),'scope':'pure packet limiter; no API or physical tracking'})
 # New candidate: wide grouping/long-range/occlusion is an independent fixture.
 plan=[];frames=[];wall=(200,-150,450,150)
 for n in range(90):
  t=n/30;shooter=(-350+50*math.sin(t),-260);impact=(800,220);friends=[shooter,(-100,100),(160,-80),(320,250)];target=shooter if n<30 else tuple(np.mean(friends+[impact],axis=0));camera=(target[0]-700,target[1]-900);oc=blocked(camera,shooter,wall);reason='occluded_hold_baseline' if oc else ('group_or_long_range_wide' if n>=30 else 'baseline_follow');plan.append({'t':t,'participants':friends,'shooter':shooter,'impact':impact,'candidate_center':target,'wall_occluded':oc,'decision':reason,'adopted':False})
  im=Image.new('RGB',(1200,720),'#172333');d=ImageDraw.Draw(im);label(im,'INDEPENDENT RESEARCH CANDIDATE / group + long range + declared wall',(12,5),21)
  def project(p):return int(270+p[0]*.34),int(380-p[1]*.34)
  bx0,by0=project((wall[0],wall[3]));bx1,by1=project((wall[2],wall[1]));d.rectangle((bx0,by0,bx1,by1),fill='#6b5c4f');d.line((*project(shooter),*project(impact)),fill='#e5c267',width=3)
  for p in friends:
   x,y=project(p);d.ellipse((x-8,y-8,x+8,y+8),fill='#7fbefe')
  x,y=project(target);d.ellipse((x-17,y-17,x+17,y+17),outline='#8adbae',width=3);label(im,f'{reason} / t={t:.2f}',(680,80),18);label(im,'Look-at center is constructed fixture data',(680,130),16);label(im,'Not evidence of LoL visibility or TargetLock',(680,170),16);frames.append(np.asarray(im))
 videos.append(encode('camera/independent_group_occlusion.mp4',frames,30));sheet('camera/group_occlusion.jpg',[Image.fromarray(frames[n]) for n in [0,29,30,89]],[f'frame {n}' for n in [0,29,30,89]],2,(600,360))
 occlusion_tests=[{'a':(-500,0),'b':(500,0),'expected':True},{'a':(-500,300),'b':(500,300),'expected':False}]
 for x in occlusion_tests:x['actual']=blocked(x['a'],x['b'],(100,-100,300,100));x['pass']=x['actual']==x['expected']
 save('CAMERA_RESULTS.json',{'pinned_source_cases':tests,'trajectories':trajectories,'packet_guards':guard,'new_candidate':plan,'declared_wall_tests':occlusion_tests,'videos':videos,'real_LoL':'NOT_RUN','real_target_visibility':'NOT_RUN','baseline_third_and_third_cinema_preserved':True,'rotation_visualization':'XZ offset paths only; not calibrated engine projection or terrain mesh','camera_side_function':{'BLUE':c.side_yaw_for('BLUE'),'RED':c.side_yaw_for('RED')}})
if __name__=='__main__':camera()
