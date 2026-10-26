from common import *
from collections import deque
import re,itertools,collections
Q=load(R/'outputs/autocine_implementation_specs_20261026/ASSET_REVIEW_QUEUE.json')['items'];SIM=load(R/'outputs/autocine_final_research_v3_20261024/SIMILARITY_TRIAGE_V3.json');PRE=R/'outputs/autocine_visual_proof_20261026'
REJECT={('effect','A'),('effect','C'),('effect','D'),('frame','023/main'),('frame','039/palette_reference_03')}
def thumb(p):return Image.open(p).convert('RGBA').resize((192,64),Image.Resampling.LANCZOS)
def desc(im):
 a=np.asarray(im).astype(float)/255;al=a[:,:,3];rgb=a[:,:,:3];weight=al.sum();mean=(rgb*al[:,:,None]).sum((0,1))/max(weight,1);mask=al>.20
 return {'rgba':a,'mask':mask,'mean':mean,'energy':float((rgb.mean(2)*al).mean())}
def metrics(a,b):
 ma,mb=a['mask'],b['mask'];inter=(ma&mb).sum();union=(ma|mb).sum();rgb=np.abs(a['rgba'][:,:,:3]*a['rgba'][:,:,3:]-b['rgba'][:,:,:3]*b['rgba'][:,:,3:]).mean()
 return {'alpha_support_iou':float(inter/max(1,union)),'premultiplied_rgb_MAE':float(rgb),'alpha_weighted_color_distance':float(np.linalg.norm(a['mean']-b['mean'])),'energy_ratio':float(max(a['energy'],b['energy'])/max(min(a['energy'],b['energy']),1e-8))}
def holes(im):
 a=im.getchannel('A').resize((256,max(1,round(im.height*256/im.width))),Image.Resampling.NEAREST);ar=np.asarray(a);m=ar<=24;h,w=m.shape;visited=np.zeros_like(m);regions=[]
 for y,x in zip(*np.nonzero(m)):
  if visited[y,x]:continue
  dq=deque([(int(x),int(y))]);visited[y,x]=True;xs=[];ys=[];border=False
  while dq:
   xx,yy=dq.popleft();xs.append(xx);ys.append(yy);border|=xx==0 or yy==0 or xx==w-1 or yy==h-1
   for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
    if 0<=nx<w and 0<=ny<h and m[ny,nx] and not visited[ny,nx]:visited[ny,nx]=True;dq.append((nx,ny))
  if not border and len(xs)>30:regions.append({'area':len(xs),'cx':float(np.mean(xs)),'cy':float(np.mean(ys)),'box':[min(xs),min(ys),max(xs)+1,max(ys)+1],'pixels':list(zip(xs,ys))})
 left=sorted([z for z in regions if z['cx']<w*.46],key=lambda z:-z['area']);right=sorted([z for z in regions if z['cx']>w*.54],key=lambda z:-z['area'])
 if not left or not right:return None
 out=[]
 for z in [left[0],right[0]]:
  box=z['box'];fill=z['area']/((box[2]-box[0])*(box[3]-box[1]));k=im.width/w;ky=im.height/h
  out.append({'center_native':[z['cx']*k,z['cy']*ky],'bbox_native':[box[0]*k,box[1]*ky,box[2]*k,box[3]*ky],'fill_ratio':fill,'mask_small_pixels':z['pixels'],'safe_inset_fraction':.10})
 return out
def geom_pair(im,g):
 out=Image.new('RGBA',im.size)
 for i,z in enumerate(g or []):
  mask=Image.new('L',(256,max(1,round(im.height*256/im.width))));d=ImageDraw.Draw(mask)
  for x,y in z['mask_small_pixels']:d.point((x,y),fill=255)
  mask=mask.resize(im.size,Image.Resampling.NEAREST);b=mask.getbbox();icon=Image.open(R/f'work/autocine_research_v4_20261025/official_icons/{["Yasuo","Jinx"][i]}.png').convert('RGBA');icon=ImageOps.fit(icon,(b[2]-b[0],b[3]-b[1]));layer=Image.new('RGBA',im.size);layer.paste(icon,b[:2]);layer.putalpha(mask);out.alpha_composite(layer)
 out.alpha_composite(im);return out
def on(im,light=False,size=(600,220)):
 out=Image.new('RGBA',size,'#e5e8ec' if light else '#172936');p=ImageOps.contain(im,size);out.alpha_composite(p,((size[0]-p.width)//2,(size[1]-p.height)//2));return out.convert('RGB')
def run():
 f={};geo=[];look={};paths={};items=[]
 for x in Q:
  key=(x['kind'],x['id']);im=Image.open(A/x['path']).convert('RGBA');paths[key]=A/x['path'];f[key]=desc(im.resize((192,64),Image.Resampling.LANCZOS));look[key]=im.resize((600,200),Image.Resampling.LANCZOS)
  g=holes(im) if x['kind']=='frame' else None
  if g:
   clean=[{k:v for k,v in z.items() if k!='mask_small_pixels'} for z in g]
   geo.append({'id':x['id'],'native_size':im.size,'status':'REVIEW','method':'connected transparent components on 256-wide alpha; candidate only, not authored geometry','portrait_candidates':clean,'center_decoration_anchor':[im.width/2,im.height/2],'recommended_fx_strength_research':.15,'safe_motion_contract':'clip to output video rect; keep face safe inset10%; entrance may be offscreen; no full-time validation','background_compatibility':'REVIEW; synthetic backgrounds only','original_constraint':'retain source limitations; no reconstruction','source_sha256':sha(A/x['path'])})
  elif x['kind']=='frame':geo.append({'id':x['id'],'status':'NOT_RUN','reason':'unambiguous paired enclosed holes not found; no guessed geometry','source_sha256':sha(A/x['path'])})
  category=5 if key in REJECT else (1 if x['catalog_status_unchanged']=='approved' else 5)
  items.append({'kind':x['kind'],'id':x['id'],'classification':category,'classification_label':{1:'優先的に残したい',5:'ユーザーに採否確認が必要'}[category],'user_rejected':key in REJECT,'recommendation_eligible':key not in REJECT,'formal_status_unchanged':x['catalog_status_unchanged'],'classification_scope':'research suggestion only; uninspected cases remain undecided','AI_new_visual_review':'NOT_RUN'})
  if len(f)%100==0:print('features',len(f),flush=True)
 save('A1_similarity/USER_REJECTED.json',{'items':[{'kind':k,'id':i,'reason':'user explicitly rejected as cheap-looking','recommendation_eligible':False,'source_preserved':True,'formal_status_changed':False,'palette_reference_retained_as_research':i=='039/palette_reference_03'} for k,i in sorted(REJECT)]})
 pairs=[]
 for x in SIM['pairs']:
  ka,kb=('frame',x['a']),('frame',x['b']);m=metrics(f[ka],f[kb]);hint='group_display_candidate' if m['alpha_support_iou']>.80 and m['premultiplied_rgb_MAE']<.06 else ('color_variant_candidate' if m['alpha_support_iou']>.80 else 'layout_similarity_only')
  pairs.append(dict(x,**m,machine_hint=hint,AI_new_visual_review='NOT_RUN',decision='retain both; no deletion/merge/approval'))
 save('A1_similarity/PAIR_METRICS_1464.json',{'pairs':pairs,'count':len(pairs),'method':'new RGB/alpha/energy metrics at192x64 on prior alpha-dHash candidate pairs; scores are not design judgement','identical_sha_groups_inherited':0,'all_pair_visual_review':False})
 # Family weak/strong and variants, rather than assuming labels imply meaningful differences.
 family=collections.defaultdict(list)
 for x in Q:
  if x['kind']=='frame':family[re.sub(r'(?:weak|strong|variant)_?\d*','',x['id'])].append(x['id'])
 fam=[]
 for name,ids in family.items():
  for a,b in itertools.combinations(ids,2):fam.append({'family':name,'a':a,'b':b,**metrics(f[('frame',a)],f[('frame',b)]),'status':'REVIEW'})
 save('A1_similarity/FAMILY_VARIATIONS.json',fam)
 legacy=load(R/'outputs/autocine_final_research_v3_20261024/LEGACY_BADGE_PROTECTION_V3.json')['items'];lf={z['path']:desc(thumb(OLD/'legacy_asset_cache_v3'/z['path'])) for z in legacy};near=[]
 for x in Q:
  if x['kind']!='frame':continue
  candidates=[{'legacy':n,**metrics(f[('frame',x['id'])],d)} for n,d in lf.items()];candidates.sort(key=lambda z:z['premultiplied_rgb_MAE']);near.append({'frame':x['id'],'top3':candidates[:3],'status':'REVIEW','scope':'composition differs; impression matching only, not duplicate proof'})
 save('A1_similarity/LEGACY37_IMPRESSION_CANDIDATES.json',near)
 chosen=[];used=set()
 for pool,count in [(sorted(pairs,key=lambda z:z['premultiplied_rgb_MAE']),8),(sorted([z for z in pairs if z['alpha_dhash_hamming']==0],key=lambda z:-z['alpha_weighted_color_distance']),6),(fam,10)]:
  for z in pool:
   key=tuple(sorted([z['a'],z['b']]))
   if key in used or any(('frame',v) in REJECT for v in key):continue
   used.add(key);chosen.append(z)
   if sum(1 for q in chosen if q.get('_pool')==len(used))<0:pass
   count-=1
   if count==0:break
 for i,z in enumerate(chosen):
  imgs=[on(look[('frame',n)],light) for light in [False,True] for n in [z['a'],z['b']]];path=f'A1_similarity/comparisons/pair_{i+1:02d}.png';sheet(path,imgs,[f'{n} / {"light" if light else "dark"}' for light in [False,True] for n in [z['a'],z['b']]],2,(600,200));z['comparison']=path
 save('A1_similarity/SELECTED_PAIR_REVIEW_QUEUE.json',chosen)
 save('A1_similarity/ASSET_CLASSIFICATION_DRAFT.json',items)
 save('A2_quality/GEOMETRY_CANDIDATES_652.json',{'items':geo,'count':len(geo),'formal_geometry_changes':0,'threshold_alpha':24,'author_verified_geometry':False})
 # New P2 visuals: prioritize high color/energy variety, keep known source constraints separate.
 selected=[x for x in Q if x['priority']=='P2' and (x['kind'],x['id']) not in REJECT][::22][:24]
 reviews=[]
 for i,x in enumerate(selected):
  im=Image.open(paths[('frame',x['id'])]).convert('RGBA');g=holes(im);candidate=geom_pair(im,g);imgs=[on(v,l) for l in [False,True] for v in [im,candidate]]
  path=f'A2_quality/P2_review/p2_{i+1:02d}.png';sheet(path,imgs,['source dark','research holes dark','source light','research holes light'],2,(600,220));reviews.append({'id':x['id'],'priority':'P2','sheet':path,'AI_new_visual_review':'NOT_RUN','source_hash':sha(paths[('frame',x['id'])]),'candidate_geometry':bool(g),'formal_status_unchanged':x['catalog_status_unchanged']})
 save('A2_quality/P2_VISUAL_QUEUE.json',reviews)
 print('pairs',len(pairs),'families',len(fam),'geometry',sum(x['status']=='REVIEW' for x in geo),'P2',len(reviews),flush=True)
if __name__=='__main__':run()
