"""Proposed contract reference model. Not a production camera or detection engine."""
from fractions import Fraction as F
import math,copy

def number(x):
 if isinstance(x,bool):raise ValueError('boolean is not time')
 r=F(str(x))
 try:
  if not math.isfinite(float(r)):raise ValueError('non-finite number')
 except OverflowError:raise ValueError('number out of range')
 return r

def canonical_events(events):
 out={}
 for e in events:
  if e['evidence']!='replay_event_verified':raise ValueError('visual evidence is not a runtime event')
  if e['type'] not in ['kill','assist','engage']:raise ValueError('unknown event type')
  t=number(e['replay_time'])
  if t<0:raise ValueError('negative replay time')
  row=copy.deepcopy(e)
  if not row['event_id']:raise ValueError('missing stable id')
  if row['event_id'] in out and out[row['event_id']]!=row:raise ValueError('conflicting stable event id')
  out[row['event_id']]=row
 return sorted(out.values(),key=lambda e:(number(e['replay_time']),e['event_id']))

def map_event(t,segments):
 """Piecewise exact map. Gaps are not interpolated; intervals half open."""
 t=number(t);last_replay=last_output=None;matched=None
 for s in segments:
  a,b,o,rate=map(number,[s['replay_in'],s['replay_out'],s['output_in'],s['rate']])
  if b<=a or rate<=0 or o<0:raise ValueError('invalid time segment')
  if last_replay is not None and (a<last_replay or o<last_output):raise ValueError('overlapping/non-monotonic segments')
  end=o+(b-a)/rate
  if a<=t<b:matched=o+(t-a)/rate
  last_replay,last_output=b,end
 return matched

def start_frame(t,rate):
 t,r=number(t),number(rate)
 if t<0 or r<=0:raise ValueError('invalid output timestamp/rate')
 return math.ceil(t*r)

def plan(context,events):
 """Fail-closed decision labels only. No inference of real 3D poses."""
 c=copy.deepcopy(context);ev=canonical_events(events);mode=c['control_mode']
 if mode not in [None,'manual','fixed_auto','full_auto']:raise ValueError('unknown control mode')
 result={'schema_version':1,'processing_revision':'research-plan-contract-v1','adopted':False,'event_ids':[e['event_id'] for e in ev],'camera':'retain_baseline','reason':None,'cutaway':False,'fx_events':[],'required_missing':[]}
 if mode is None:
  result['reason']='legacy_unspecified';return result
 if mode=='manual' or c.get('manual_override'):
  result['reason']='manual_priority';return result
 if c.get('side') not in ['BLUE','RED']:
  result['reason']='unknown_side';return result
 if not c.get('side_approved'):
  result['reason']='side_not_approved';return result
 if not c.get('target_lock_valid'):
  result['reason']='target_lock_unverified';return result
 kills=[e for e in ev if e['type']=='kill' and e['actor_id']==c['target_id']]
 result['fx_events']=[{'event_id':e['event_id'],'output_time':str(v),'start_frame':start_frame(v,c['fps'])} for e in kills if (v:=map_event(e['replay_time'],c['time_map'])) is not None]
 g=c.get('geometry')
 if not g or g.get('timestamp_verified') is not True or g.get('coverage') is None or g.get('occlusion') is None:
  result.update(reason='geometry_unknown',required_missing=['verified visible target/group geometry']);return result
 if not 0<=g['coverage']<=1 or not 0<=g['occlusion']<=1:raise ValueError('invalid metric range')
 if g['coverage']<.95 or g['occlusion']>.05:
  result['reason']='unsafe_visibility';return result
 if mode=='fixed_auto':result.update(camera='retain_fixed_pose_with_safe_framing_proposal',reason='fixed_pose_priority');return result
 if c.get('long_range') and not g.get('shooter_and_impact_verified'):
  result['reason']='long_range_geometry_missing';return result
 if g.get('participants',1)>=3 or c.get('long_range'):
  result['camera']='group_wide_proposal'
 else:result['camera']='follow_proposal'
 result['reason']='verified_geometry_candidate'
 # Unknown next engagement is not permission to insert a close-up.
 result['cutaway']=bool(kills and c.get('fight_finished') is True and c.get('next_engage_clear') is True and c.get('cutaway_take_validated') is True)
 return result

def selftest():
 e={'event_id':'K1','replay_time':100,'type':'kill','actor_id':'P1','victim_id':'P2','evidence':'replay_event_verified'}
 base={'control_mode':'full_auto','side':'BLUE','side_approved':True,'target_lock_valid':True,'target_id':'P1','fps':'60000/1001','time_map':[{'replay_in':99,'replay_out':101,'output_in':0,'rate':1}],'geometry':{'timestamp_verified':True,'coverage':.99,'occlusion':0,'participants':4},'fight_finished':True,'next_engage_clear':True,'cutaway_take_validated':True}
 rows=[]
 def ck(n,ok):rows.append({'id':n,'pass':bool(ok)})
 original=copy.deepcopy(base);r=plan(base,[e]);ck('wide_group',r['camera']=='group_wide_proposal');ck('explicit_cutaway_guards',r['cutaway']);ck('caller_state_not_mutated',base==original);ck('dedup',len(canonical_events([e,e]))==1)
 ck('legacy_unspecified_preserved',plan({**base,'control_mode':None},[e])['reason']=='legacy_unspecified')
 for name,change,reason in [('manual',{'control_mode':'manual'},'manual_priority'),('override',{'manual_override':True},'manual_priority'),('unknown_side',{'side':None},'unknown_side'),('unapproved_red',{'side':'RED','side_approved':False},'side_not_approved'),('lost_lock',{'target_lock_valid':False},'target_lock_unverified'),('no_geometry',{'geometry':None},'geometry_unknown'),('no_long_range_impact',{'long_range':True},'long_range_geometry_missing')]:
  c={**base,**change};ck(name,plan(c,[e])['reason']==reason)
 for field in ['coverage','occlusion']:
  c=copy.deepcopy(base);c['geometry'][field]=None;ck('unknown_'+field,plan(c,[e])['reason']=='geometry_unknown')
 c=copy.deepcopy(base);c['geometry']['coverage']=.94;ck('unsafe_target',plan(c,[e])['camera']=='retain_baseline')
 for key in ['fight_finished','next_engage_clear','cutaway_take_validated']:
  c={**base,key:None};ck('cutaway_missing_'+key,not plan(c,[e])['cutaway'])
 ck('assist_no_kill_fx',plan(base,[{**e,'type':'assist'}])['fx_events']==[])
 ck('other_actor_no_kill_fx',plan(base,[{**e,'actor_id':'P3'}])['fx_events']==[])
 ck('same_time_distinct_event_ids',len(canonical_events([e,{**e,'event_id':'K2','victim_id':'P3'}]))==2)
 ck('order_independence',canonical_events([e,{**e,'event_id':'K0','replay_time':99}])==canonical_events([{**e,'event_id':'K0','replay_time':99},e]))
 seg=[{'replay_in':10,'replay_out':12,'output_in':0,'rate':.5},{'replay_in':15,'replay_out':17,'output_in':4,'rate':2}]
 ck('slow_time_map',map_event(11,seg)==2);ck('fast_time_map',map_event(16,seg)==F(9,2));ck('seek_gap',map_event(14,seg) is None);ck('half_open_end',map_event(17,seg) is None);ck('millisecond_start_at_30',start_frame('.5004',30)==16);ck('millisecond_start_at_60',start_frame('.5004',60)==31);ck('fractional_fps',start_frame(1,'60000/1001')==60)
 bad=[('conflict',lambda:canonical_events([e,{**e,'victim_id':'other'}])),('visual_not_event',lambda:canonical_events([{**e,'evidence':'video_visual_only'}])),('nan',lambda:canonical_events([{**e,'replay_time':float('nan')}])),('inf',lambda:canonical_events([{**e,'replay_time':float('inf')}])),('negative',lambda:canonical_events([{**e,'replay_time':-1}])),('zero_rate',lambda:map_event(10,[{**seg[0],'rate':0}])),('overlap',lambda:map_event(11,[seg[0],{**seg[1],'replay_in':11}])),('bool_time',lambda:start_frame(True,30))]
 for n,f in bad:
  try:f();ck('reject_'+n,False)
  except (ValueError,TypeError):ck('reject_'+n,True)
 return rows,{'context':base,'events':[e],'decision':r}
