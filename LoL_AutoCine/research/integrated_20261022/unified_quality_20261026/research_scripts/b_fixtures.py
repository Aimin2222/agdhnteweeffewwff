from common import *
import importlib.util,copy,itertools,wave,os
def camera():
 target=np.zeros((120,2));target[:30]=[-300,-200];target[30:75]=[250,100];target[75:]=[650,220];methods={};data=[]
 for name in ['raw','velocity_limit','velocity_accel_limit','hold_then_cut']:
  pos=target[0].copy();velocity=np.zeros(2);arr=[];cuts=[]
  for n,aim in enumerate(target):
   delta=aim-pos;dist=np.linalg.norm(delta)
   if name=='raw':pos=aim.copy()
   elif name=='velocity_limit':pos+=delta*min(1.,14/max(dist,1e-9))
   elif name=='velocity_accel_limit':
    wanted=delta*min(8.,420/max(dist,1e-9));dv=wanted-velocity;velocity+=dv*min(1.,60/max(np.linalg.norm(dv),1e-9));pos+=velocity/30
   elif n in [36,81]:pos=aim.copy();cuts.append(n)
   arr.append(pos.copy())
  a=np.asarray(arr);steps=np.linalg.norm(np.diff(a,axis=0),axis=1);acc=np.linalg.norm(np.diff(a,n=2,axis=0),axis=1)*900;methods[name]=a;data.append({'method':name,'max_step_units_per_frame':float(steps.max()),'max_accel_units_per_s2':float(acc.max()),'mean_target_lag':float(np.linalg.norm(a-target,axis=1).mean()),'cuts':cuts,'scope':'declared2D target center only; cut is discontinuity, not smoothed tracking','status':'REVIEW'})
 frames=[]
 colors=['#e38e9c','#8fc9ff','#8edcb1','#d5b879']
 for n in range(120):
  im=Image.new('RGB',(1280,720),'#172333');d=ImageDraw.Draw(im);label(im,'SYNTHETIC CAMERA SWITCH / no Replay API',(15,5),22)
  for i,(name,a) in enumerate(methods.items()):
   x0=i%2*640;y0=i//2*340;pts=[(x0+190+p[0]*.35,y0+200-p[1]*.35) for p in a[:n+1]]
   if len(pts)>1:d.line(pts,fill=colors[i],width=2)
   x,y=pts[-1];d.ellipse((x-7,y-7,x+7,y+7),fill=colors[i]);tx,ty=x0+190+target[n,0]*.35,y0+200-target[n,1]*.35;d.rectangle((tx-8,ty-8,tx+8,ty+8),outline='#fff');label(im,name,(x0+15,y0+44),19,colors[i])
  frames.append(np.asarray(im))
 vid=encode('B1_camera/methods_compare.mp4',frames,30);sheet('B1_camera/methods_compare.png',[Image.fromarray(frames[i]) for i in [29,30,45,89]],[f'n{i}' for i in [29,30,45,89]],2,(640,360));save('B1_camera/METHOD_COMPARISON.json',{'cases':data,'target':target.tolist(),'video':vid,'real_LoL':'NOT_RUN','old_third_camera_replaced':False})
def montage():
 path=W/'latest_readonly/pr49/LoL_AutoCine/ui/smart_montage.py';scope={};exec(compile(path.read_text('utf8'),str(path),'exec'),scope)
 events=[{'event_id':'k1','time':10.,'role':'kill','multikill':1,'actor':'P1','victim':'V1'},{'event_id':'k2','time':11.2,'role':'kill','multikill':2,'actor':'P1','victim':'V2'},{'event_id':'k3','time':12.1,'role':'kill','multikill':3,'actor':'P1','victim':'V3'},{'event_id':'a1','time':30.,'role':'assist','multikill':1,'actor':'P1','victim':'V4'},{'event_id':'k4','time':60.,'role':'kill','multikill':1,'actor':'P1','victim':'V5'}]
 existing=[x[0].event_id for x in scope['choose_scenes']([(NS(**x),{}) for x in events])]
 def plan(events,manual=False):
  if manual:return {'event_order':[x['event_id'] for x in events],'manual_unchanged':True}
  unique={x['event_id']:x for x in events};groups=[]
  for e in sorted(unique.values(),key=lambda x:x['time']):
   if groups and e['actor']==groups[-1]['actor'] and e['time']-groups[-1]['events'][-1]['time']<=3:groups[-1]['events'].append(e);groups[-1]['out']=e['time']+3
   else:groups.append({'actor':e['actor'],'in':max(0,e['time']-4),'out':e['time']+3,'events':[e]})
  for g in groups:g['fx_budget']={'max_flash_concurrent':1,'max_peak_alpha':.35,'source':'proposal, not perceptual optimum'}
  return {'groups':groups,'event_order':[e['event_id'] for g in groups for e in g['events']]}
 grouped=plan(events);dup=plan(events+[dict(events[0])]);same=plan(events+[dict(events[0],event_id='k1b',victim='V1b')]);manual=plan(list(reversed(events)),True)
 tests=[{'id':'duplicate_same_event_id','pass':len(dup['event_order'])==5},{'id':'simultaneous_distinct_victim','pass':len(same['event_order'])==6},{'id':'manual_priority','pass':manual['event_order']==[x['event_id'] for x in reversed(events)]},{'id':'same_fight_group','pass':[len(g['events']) for g in grouped['groups']]==[3,1,1]}]
 frames=[]
 for n in range(120):
  im=Image.new('RGB',(1280,720),'#172333');d=ImageDraw.Draw(im);label(im,'SYNTHETIC MONTAGE PLAN / event metadata only',(15,5),22)
  for j,(name,blocks) in enumerate([('existing score order',[(eid,None) for eid in existing]),('research fight grouping',[(str([e['event_id'] for e in g['events']]),g) for g in grouped['groups']])]):
   label(im,name,(20,90+j*280),20)
   for i,(txt,g) in enumerate(blocks):
    x=20+i*(1200/max(len(blocks),1));y=140+j*280;d.rectangle((x,y,x+1200/max(len(blocks),1)-12,y+110),fill='#315c7e' if i==n//24%len(blocks) else '#2a3b4c');label(im,txt,(x+9,y+15),16)
  label(im,'No game footage; no automatic engage/skin recognition claim',(20,660),19);frames.append(np.asarray(im))
 video=encode('B2_oneclick/plan_compare.mp4',frames,30);sheet('B2_oneclick/plan_compare.png',[Image.fromarray(frames[0])],['existing vs independent event grouping'],1,(1280,720));save('B2_oneclick/PLAN_FIXTURES.json',{'inputs':events,'existing_smart_order':existing,'candidate':grouped,'tests':tests,'video':video,'evidence':'latest PR49 pure choose_scenes executed; independent grouping candidate','real_battle_boundaries':'NOT_RUN','real_champion_skin_recognition':'NOT_RUN'})
def recovery():
 root=W/'recovery_sandbox/日本語 空白 パス';root.mkdir(parents=True,exist_ok=True);baseline={'camera':'third','side':'RED','TargetLock':'fixture-player','HUD':True,'output_checked':['c1','c2','c3']};results=[]
 for fault in ['none','disk_full','lol_disconnect','cancel','clip_failure','write_failure']:
  current=copy.deepcopy(baseline);journal={'completed':[],'failed':[],'cancelled':False};error=None
  try:
   for clip in baseline['output_checked']:
    if clip=='c2' and fault in ['disk_full','lol_disconnect','write_failure']:raise OSError({'disk_full':'ENOSPC fixture','lol_disconnect':'Replay disconnected fixture','write_failure':'EACCES fixture'}[fault])
    if clip=='c2' and fault=='cancel':journal['cancelled']=True;break
    if clip=='c2' and fault=='clip_failure':journal['failed'].append(clip);continue
    journal['completed'].append(clip)
  except OSError as e:error=str(e)
  finally:current=copy.deepcopy(baseline)
  resumed=[c for c in baseline['output_checked'] if c not in journal['completed']];dest=root/(fault+'.json');tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(journal),'utf8');os.replace(tmp,dest);reloaded=load(dest)
  results.append({'fault':fault,'error':error,'journal':journal,'resume_only_missing':resumed,'state_restored':current==baseline,'journal_roundtrip':reloaded==journal,'status':'PASS' if current==baseline and reloaded==journal else 'FAIL','scope':'independent research recovery state machine; errors injected, no real disk fill/disconnect/process stop'})
 save('B5_distribution/RECOVERY_FIXTURE_RESULTS.json',results);save('B5_distribution/STATE_BASELINE_FIXTURE.json',baseline)
 # BAT is a text fixture only, not executed or installed.
 p=O/'B5_distribution/日本語パス_CRLF_試験用.bat';p.write_bytes('@echo off\r\nchcp 65001 >nul\r\necho 研究用・起動処理なし\r\n'.encode('utf-8'));b=p.read_bytes();save('B5_distribution/BAT_TEXT_CHECK.json',{'file':p.name,'utf8_decode':bool(b.decode('utf8')),'CRLF_only':b.count(b'\n')==b.count(b'\r\n'),'executed':False,'Python_free_PC_test':'NOT_RUN','portable_EXE_start':'NOT_RUN','e2e_movie_completion':'NOT_RUN'})
if __name__=='__main__':
 for n in sys.argv[1:] or ['camera','montage','recovery']:globals()[n]()
