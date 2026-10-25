from lab_common import *
import sys,copy
sys.dont_write_bytecode=True;sys.path.insert(0,str(S.parent))
from core import camera as c
rows=[]
def test(name,fn):
 try:
  evidence=fn();rows.append(dict(id=name,status='PASS',evidence=evidence))
 except Exception as e:rows.append(dict(id=name,status='FAIL',exception=type(e).__name__,message=str(e)))
for team in ['ORDER','CHAOS']:
 for style in c.STYLES:
  def case(team=team,style=style):
   rig=c.RigInfo(mode='fps',third=True,h=(0,-1),pitch_axis='x',pitch_sign=-1,rot={'x':-32,'y':0,'z':0})
   p=c.CameraPlan(style=style,rig=rig,side_yaw=c.side_yaw_for(team));before=copy.deepcopy(rig.__dict__)
   values=[]
   for t in [-1.,0.,.01,.26,1.,3.,10.]:
    off=p.offset_at(t);rot=p.rotation_at(t);fov=p.fov_at(t);speed=p.speed_at(t)
    assert all(math.isfinite(float(x)) for x in [*off,*rot.values(),fov,speed]);assert fov>0 and speed>0
    values.append(dict(t=t,offset=off,rotation=rot,fov=fov,speed=speed))
   assert before==rig.__dict__
   return dict(team=team,style=style,samples=values,rig_unchanged=True,live_TargetLock_verified=False)
  test(f'CAM-{team}-{style}',case)
for team in ['ORDER','CHAOS','BLUE','RED','unknown']:
 for choice in ['auto','blue','red','invalid']:
  def case(team=team,choice=choice):
   value=c.side_yaw_for(team,choice);expect=180. if choice=='red' or choice not in ['blue','red'] and team in ['CHAOS','RED'] else 0.
   assert value==expect;before=c.live_side_profile(team,choice,style='third');a=c.live_side_profile(team,choice,style='third');a['distance']=99999;assert c.live_side_profile(team,choice,style='third')==before
   return dict(side_yaw=value,profile=before,profile_copy_isolated=True)
  test(f'SIDE-{team}-{choice}',case)
for slow in [False,True]:
 for elapsed in [0.,.01,.1,1.]:
  def case(slow=slow,elapsed=elapsed):
   prev=dict(fieldOfView=60.,selectionOffset=dict(x=0.,y=500.,z=0.),cameraRotation=dict(x=0.,y=0.,z=0.),selectionName='Fixture',cameraAttached=True)
   target=copy.deepcopy(prev);target.update(fieldOfView=100.,selectionOffset=dict(x=900.,y=1500.,z=-800.),cameraRotation=dict(x=190.,y=160.,z=-170.));snapshot=copy.deepcopy(target)
   out=c.limit_camera_post(target,prev,elapsed,slow_api=slow);assert target==snapshot
   assert out['selectionName']=='Fixture' and out['cameraAttached'] is True
   dt=max(.016,min(.35,elapsed))
   if slow:assert abs(out['fieldOfView']-60)<=22*dt+1e-8;assert math.sqrt(sum((out['selectionOffset'][k]-prev['selectionOffset'][k])**2 for k in ['x','y','z']))<=420*dt+1e-8
   else:assert out==target
   return dict(slow=slow,dt=dt,output=out,attachment_fields_preserved=True)
  test(f'GUARD-{slow}-{elapsed}',case)
save('CAMERA_SOURCE_MATH_V4.json',dict(cases=rows,executed=len(rows),passed=sum(x['status']=='PASS' for x in rows),live_LoL=False,scope='unchanged camera pure functions and CameraPlan; synthetic rig, not real BLUE/RED framing or TargetLock quality'))
print('camera math',len(rows),'fail',sum(x['status']=='FAIL' for x in rows))
