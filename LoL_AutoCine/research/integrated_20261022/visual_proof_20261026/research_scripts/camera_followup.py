from common import *
import copy
sys.path.insert(0,str(S));from core import camera as c
j=load(O/'CAMERA_RESULTS.json');raw=j['new_candidate'];prev=None;vals=[];frames=[]
for n,r in enumerate(raw):
 x,z=r['candidate_center'];target={'selectionOffset':{'x':x,'y':650.,'z':z},'cameraRotation':{'x':0 if n<30 else 180,'y':-28.,'z':0.},'fieldOfView':60 if n<30 else 75,'selectionName':'Fixture-P1','cameraAttached':True}
 prev=c.limit_camera_post(target,prev,1/30,slow_api=True);vals.append(copy.deepcopy(prev))
 im=Image.new('RGB',(1200,600),'#172333');d=ImageDraw.Draw(im);label(im,'SYNTHETIC SWITCH / raw vs actual pinned slow-API limiter',(12,4),21)
 for col,(name,color) in enumerate([('raw center','#e68c9d'),('bounded packet','#8bdbb3')]):
  pts=[]
  for i in range(n+1):
   if col==0:a,b=raw[i]['candidate_center']
   else:a,b=vals[i]['selectionOffset']['x'],vals[i]['selectionOffset']['z']
   pts.append((col*600+200+a*.5,320-b*.5))
  if len(pts)>1:d.line(pts,fill=color,width=3)
  x,y=pts[-1];d.ellipse((x-9,y-9,x+9,y+9),fill=color);label(im,name,(col*600+12,55),20,color)
 label(im,f'frame {n} / t={n/30:.3f}; fixture coordinates only, no LoL projection',(12,520),18)
 label(im,'slow_api=True is forced for this test; ordinary-latency path bypasses guard',(12,560),16)
 frames.append(np.asarray(im))
def dist(a,b):return math.dist(a,b)
rawsteps=[dist(a['candidate_center'],b['candidate_center']) for a,b in zip(raw,raw[1:])]
steps=[dist(tuple(a['selectionOffset'].values()),tuple(b['selectionOffset'].values())) for a,b in zip(vals,vals[1:])]
angles=[abs((b['cameraRotation']['x']-a['cameraRotation']['x']+180)%360-180) for a,b in zip(vals,vals[1:])]
video=encode('camera/switch_raw_vs_bounded.mp4',frames,30)
sheet('camera/switch_raw_vs_bounded.jpg',[Image.fromarray(frames[n]) for n in [29,30,45,89]],[f'n{n}' for n in [29,30,45,89]],2,(600,300))
save('CAMERA_SWITCH_RESULTS.json',{'raw_max_center_step':max(rawsteps),'bounded_max_offset_step':max(steps),'offset_step_limit':14.,'max_angle_step_deg':max(angles),'angle_step_limit':1.4,'numeric_bound_status':'PASS' if max(steps)<=14+1e-9 and max(angles)<=1.4+1e-9 else 'FAIL','raw_continuity_status':'FAIL','attachment_fields_preserved':all(x['cameraAttached'] is True and x['selectionName']=='Fixture-P1' for x in vals),'samples':vals,'video':video,'scope':'candidate center sent as fixture offset, not coordinate-equivalent production integration; forced slow_api=True. velocity bounds only, no acceleration or collision guarantee','real_LoL':'NOT_RUN'})
print('camera switch complete')
