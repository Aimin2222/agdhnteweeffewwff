from common import *
from assets import Q,REJECT,desc,thumb,metrics,on
import itertools
def run():
 effects=[x for x in Q if x['kind']=='effect'];f={x['id']:desc(thumb(A/x['path'])) for x in effects};pairs=[]
 for a,b in itertools.combinations(effects,2):pairs.append({'a':a['id'],'b':b['id'],**metrics(f[a['id']],f[b['id']]),'recommendation_eligible':all(('effect',x['id']) not in REJECT for x in [a,b]),'status':'REVIEW','AI_pair_review':'NOT_RUN'})
 save('A1_similarity/FX595_PAIR_METRICS.json',pairs);selected=sorted([p for p in pairs if p['recommendation_eligible']],key=lambda z:z['premultiplied_rgb_MAE'])[:8];by={x['id']:x for x in effects}
 for i,p in enumerate(selected,1):
  imgs=[on(Image.open(A/by[n]['path']).convert('RGBA'),light) for light in [False,True] for n in [p['a'],p['b']]];path=f'A1_similarity/comparisons/fx_pair_{i:02d}.png';sheet(path,imgs,[f'{n} / {"light" if l else "dark"}' for l in [False,True] for n in [p['a'],p['b']]],2,(600,200));p['image']=path
 save('A1_similarity/FX_PAIR_VISUAL_QUEUE.json',selected)
 nearest=load(O/'A1_similarity/LEGACY37_IMPRESSION_CANDIDATES.json');nearest=sorted(nearest,key=lambda z:z['top3'][0]['premultiplied_rgb_MAE']);seen=set();out=[];frames={x['id']:x for x in Q if x['kind']=='frame'}
 for p in nearest:
  n=p['top3'][0]['legacy']
  if n in seen or ('frame',p['frame']) in REJECT:continue
  seen.add(n);i=len(out)+1;path=f'A1_similarity/comparisons/legacy_impression_{i:02d}.png';old=Image.open(OLD/'legacy_asset_cache_v3'/n).convert('RGBA');new=Image.open(A/frames[p['frame']]['path']).convert('RGBA');sheet(path,[on(a,l) for l in [False,True] for a in [old,new]],[f'{name} / {"light" if l else "dark"}' for l in [False,True] for name in [Path(n).stem,p['frame']]],2,(600,200));out.append({'frame':p['frame'],'legacy':n,'image':path,'status':'REVIEW','AI_pair_review':'NOT_RUN','scope':'scaled whole art; single/pair composition may differ, no duplicate conclusion'})
  if len(out)==6:break
 save('A1_similarity/LEGACY_PAIR_VISUAL_QUEUE.json',out)
 g=load(O/'A2_quality/GEOMETRY_CANDIDATES_652.json')
 for x in g['items']:
  if 'native_size' not in x:continue
  width,height=x['native_size'];factor=384/width;x['research_frame_display_size_at_1920']=[384,height*factor];x['portrait_display_candidates_1920']=[{'center':[a*factor for a in z['center_native']],'box':[a*factor for a in z['bbox_native']],'face_content_safe_inset_fraction':.1} for z in x['portrait_candidates']];x['numeric_scope']='local coordinates within384-wide frame; add shared overlay transform. Not an approved crop, strength or safe area.'
 save('A2_quality/GEOMETRY_CANDIDATES_652.json',g)
if __name__=='__main__':run()
