from lab_common import *
import types,sys,dataclasses,copy,random
# Immutable pure clip-boundary selector; no Replay/network/recording calls.
mod=types.ModuleType('research_immutable_smart_camera');sys.modules[mod.__name__]=mod
exec(compile((S/'smart_camera_director.py').read_text('utf-8-sig'),'immutable_smart_camera','exec'),mod.__dict__)
rows=[]
def case(name,got,expected):rows.append({'id':name,'observed':got,'expected':expected,'status':'PASS' if got==expected else 'FAIL','scope':'independent offline rule test; not live camera'})
for side in ['BLUE','RED']:
 for style in mod.SUPPORTED_STYLES:
  for mode in ['manual','fixed_auto','full_auto']:
   x=mod.decide_camera(mode,side,style,[1,2],approved={side:[style]});case(f'{side}_{style}_{mode}',x.style,style)
  x=mod.decide_camera('full_auto',side,style,[],approved={});case(side+'_'+style+'_empty_qa_is_fallback',x.fallback,True)
  x=mod.decide_camera('future_mode',side,style,[]);case(side+'_'+style+'_unknown_manual',x.mode,'manual')
for side in ['BLUE','RED']:
 x=mod.decide_camera('full_auto',side,'top',[1,2],approved={side:['top','orbit']},excluded=['top']);case(side+'_exclusion',x.style,'orbit')
 try:mod.decide_camera('full_auto',side,'top',[],approved={},excluded=list(mod.SUPPORTED_STYLES));actual='NO_EXCEPTION'
 except Exception as e:actual=type(e).__name__
 case(side+'_all_excluded',actual,'ValueError')
# Research-only proposal with explicit, testable missing-data and manual guards.
def group_events(events,gap=3.):
 if gap<=0:raise ValueError('gap must be positive')
 unique={str(e['id']):e for e in events if e.get('kind')=='kill' and math.isfinite(float(e['time']))}
 groups=[]
 for e in sorted(unique.values(),key=lambda e:(e['time'],e['id'])):
  if not groups or e['time']-groups[-1][-1]['time']>gap:groups.append([])
  groups[-1].append(e)
 return groups
def plan(group,*,manual=False,next_engage=None,target_alive=True,visible=None,side_approved=False):
 end=group[-1]['time'];reasons=[]
 if manual:reasons.append('manual_override')
 if next_engage is None:reasons.append('unknown_next_engage')
 elif next_engage-end<1.5:reasons.append('next_engage_too_close')
 if not target_alive:reasons.append('target_dead')
 if visible is None or visible<.9:reasons.append('visibility_unverified')
 if not side_approved:reasons.append('side_unapproved')
 shots=[{'kind':'wide','start':max(0,group[0]['time']-4),'end':end+2}]
 if not reasons:shots.append({'kind':'cutaway_optional','start':end+.4,'end':end+1.4})
 return {'group':[e['id'] for e in group],'shots':shots[:3],'cutaway':not reasons,'reasons':reasons,'maximum_takes':3,'status':'PROPOSAL_NOT_PRODUCTION'}
e=[{'id':str(i),'time':t,'kind':'kill'} for i,t in enumerate([1.,2.,5.,8.01])]
case('group_exact_gap_inclusive',[[x['id'] for x in g] for g in group_events(e)],[['0','1','2'],['3']])
case('group_duplicate_id',len(group_events(e+[e[0]])[0]),3)
case('group_assist_not_kill',len(group_events(e+[{'id':'a','time':3,'kind':'assist'}])[0]),3)
group=e[:2]
base={'manual':False,'next_engage':10.,'target_alive':True,'visible':.95,'side_approved':True}
for key,val in [('manual',True),('next_engage',None),('next_engage',2.5),('target_alive',False),('visible',None),('visible',.5),('side_approved',False)]:
 opt=dict(base);opt[key]=val;p=plan(group,**opt);case('suppress_'+key+'_'+str(val),p['cutaway'],False)
case('qualified_cutaway',plan(group,**base)['cutaway'],True)
plans=[]
for gap in [.5,1.5,3.,5.]:
 for times in [[1,1.1,1.2],[1,4,7],[1,2,8],[0,0,3.01]]:
  groups=group_events([{'id':str(i),'time':t,'kind':'kill'} for i,t in enumerate(times)],gap)
  plans.append({'proposal_gap':gap,'events':times,'groups':[[x['time'] for x in g] for g in groups],'plans':[plan(g,**base) for g in groups]})
for recipe in load(V3/'SIX_RECIPE_PROPOSALS_V3.json')['recipes']:
 snap=copy.deepcopy(recipe);encoded=json.dumps(recipe,sort_keys=True);decoded=json.loads(encoded);case('recipe_roundtrip_'+recipe['id'],decoded,recipe)
 override={'camera_style':'orbit','frame_id':'legacy37','fps':60};draft={**recipe,**override};case('recipe_manual_preserved_'+recipe['id'],all(draft[k]==v for k,v in override.items()),True);case('recipe_original_unchanged_'+recipe['id'],snap,recipe)
save('CAMERA_RECIPE_RULE_RESULTS_V4.json',{'cases':rows,'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'shotplan_examples':plans,'thresholds_are_proposals':True,'live_camera_pass':False,'all_ten_styles_retained':list(mod.SUPPORTED_STYLES),'proposal_gap_sensitivity_not_accuracy':True})
print(json.dumps({'cases':len(rows),'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'shotplan_sensitivity_examples':len(plans)}))
