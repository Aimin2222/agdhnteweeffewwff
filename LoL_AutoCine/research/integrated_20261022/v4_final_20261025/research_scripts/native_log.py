from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_research_v4_20261025';O=R/'outputs/autocine_research_v4_20261025'
q=json.loads((W/'native_queue.json').read_text('utf-8'));p=O/'NATIVE_VISUAL_LOG_V4.json'
d=json.loads(p.read_text('utf-8')) if p.exists() else {'scope':'actual original-detail full PNG viewing; not original-fidelity/portrait/HUD approval','viewed':{}}
if len(sys.argv)>1:
 start=int(sys.argv[1]);notes=json.loads(sys.argv[2]);assert start+len(notes)<=len(q)
 for a,n in zip(q[start:],notes):d['viewed'][a['id']]={'native_full_png_viewed':True,'note':n,'sha256':a['actual_sha256'],'formal_approval_changed':False,'complete_12_criteria_pass':False}
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'viewed':len(d['viewed']),'remaining_full_png_views':652-len(d['viewed'])}))
