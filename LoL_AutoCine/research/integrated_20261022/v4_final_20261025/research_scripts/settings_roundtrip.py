from composition_motion import *
import dataclasses,types,importlib.util,copy
text=(S/'effects.py').read_text('utf-8-sig');tree=ast.parse(text);module=types.ModuleType('core.v4_template_fixture');sys.modules[module.__name__]=module
module.__dict__.update(dataclass=dataclasses.dataclass,field=dataclasses.field,asdict=dataclasses.asdict,INTENSITY={'natural':.6,'standard':1.,'strong':1.4})
for x in tree.body:
 if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='VIDEO_EFFECT_DEFAULTS' for t in x.targets):exec(compile(ast.Module(body=[x],type_ignores=[]),'effects.py','exec'),module.__dict__)
cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Template');exec(compile(ast.Module(body=[cls],type_ignores=[]),'effects.py','exec'),module.__dict__);T=module.Template
rows=[]
def case(name,actual,expected):rows.append({'name':name,'actual':actual,'expected':expected,'status':'PASS' if actual==expected else 'FAIL'})
base=T().to_dict();restored=T(**json.loads(json.dumps(base))).to_dict()
for key in base:case('default_field_'+key,restored[key],base[key])
for motion in MOTIONS+['unknown_motion']:
 t=T(kill_icon_motion=motion);case('motion_normalize_'+motion,t.kill_icon_motion,motion if motion in MOTIONS else 'instant')
t=T(video_effects={'center_mosaic':.7,'flash':.4});case('retired_center_mosaic_removed',t.video_effects,{'flash':.4});t.video_effects['center_mosaic']=1.;case('retired_not_serialized',t.to_dict()['video_effects'],{'flash':.4})
try:T(**{**base,'future_unknown_field':1});actual='accepted'
except Exception as e:actual=type(e).__name__
case('unknown_Template_constructor_field',actual,'TypeError')
spec=importlib.util.spec_from_file_location('v4_readonly_scene_project',S.parent/'ui/scene_project.py');sp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sp;spec.loader.exec_module(sp)
P=sp.SceneProject;p=P();p.put('fixture-A',sp.Shot(yaw=20));p.put('fixture-B',sp.Shot(pre=7));before=copy.deepcopy(p.to_dict());p.save(O/'PROJECT_ROUNDTRIP_FIXTURE_V4.json');case('project_atomic_save_load',P.load(O/'PROJECT_ROUNDTRIP_FIXTURE_V4.json').to_dict(),before)
p.put('fixture-A',sp.Shot(yaw=50));case('undo_available',p.undo(),True);case('undo_restores',p.to_dict(),before);case('redo_available',p.redo(),True);case('redo_yaw',p.shots['fixture-A'].yaw,50)
for version in [1,2,3]:case('project_version_'+str(version),len(P.from_dict({'schema_version':version,'shots':before['shots'],'sequence':[]}).shots),2)
for label,data in [('future_version',{'schema_version':999}),('bad_shots',{'schema_version':3,'shots':[]}),('bad_sequence',{'schema_version':3,'sequence':[1]})]:
 try:P.from_dict(data);actual='accepted'
 except Exception as e:actual=type(e).__name__
 case(label,actual,'ValueError')
for value in [float('nan'),float('inf'),float('-inf'),'bad',None]:case('nonfinite_yaw_'+str(value),sp.Shot.validated({'yaw':value}).yaw,0.)
try:sp.validate_keyframes([{}]*41);actual='accepted'
except Exception as e:actual=type(e).__name__
case('keyframe_limit41',actual,'ValueError')
case('keyframe_duplicate_time_last',sp.validate_keyframes([{'time':1,'yaw':2},{'time':1,'yaw':3}]),[{'time':1.,'yaw':3.,'zoom':0.,'fov':0.}])
with_unknown=P.from_dict({**before,'future_unknown_metadata':'value'}).to_dict();case('unknown_project_metadata_currently_not_preserved','future_unknown_metadata' in with_unknown,False)
save('SETTINGS_PROJECT_ROUNDTRIP_V4.json',{'cases':rows,'passed':sum(a['status']=='PASS' for a in rows),'failed':sum(a['status']=='FAIL' for a in rows),'scope':'actual unchanged Template AST and scene_project module; independent files only, no GUI/LoL pass','unknown_field_policy':'existing Template rejects unknown kwargs, SceneProject ignores unknown top metadata; preservation in proposed new schema is not an existing verified property'})
print(json.dumps({'cases':len(rows),'passed':sum(a['status']=='PASS' for a in rows),'failed':sum(a['status']=='FAIL' for a in rows)}))
