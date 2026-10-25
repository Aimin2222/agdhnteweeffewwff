from lab_common import *
from PIL import Image,ImageDraw
import numpy as np,re
s=extract('effects.py',{'_enable_expr','_build_video_effect_filters'},{'math':math,'Template':object});previous=load(O/'FLASH_COMPAT_REVISION_V4.json')['cases'];rows=[];all_arrays={}
def run(g):
 r=ff(['-f','lavfi','-i','color=c=gray:s=160x90:r=60:d=3','-vf',','.join(g+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1']);return r,np.frombuffer(r.stdout,np.uint8).reshape(-1,90,160)
for old in previous:
 ev=old['events'];k=old['strength'];amp=old['legacy_amplitude'];terms=[f'if(gte(t,{t:.3f}),{amp}*exp(-18*abs(t-{t:.3f})),0)' for t in ev];body=terms[0] if terms else '0'
 for term in terms[1:]:body=f'max({body},{term})'
 if ev:
  legacy=s['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':k}),3,[(t,t) for t in ev],False);gate=re.search(r":enable='([^']+)'",legacy[0]).group(1);graph=[f"eq=brightness='{body}':eval=frame:enable='{gate}'"]
 else:legacy=[];graph=[]
 r,a=run(graph);_,baseline=run(legacy);single=bool(np.array_equal(a,baseline)) if old['case']=='single' else None
 row={'case':old['case'],'strength':k,'events':ev,'graph':graph,'frames':len(a),'rc':r.returncode,'single_event_bit_equal_legacy':single,'event_gray':[float(a[min(len(a)-1,round(t*60))].mean()) for t in ev],'revision':'research_max_v4_causal_start_gate','scope':'research-only, not product revision adoption'}
 if old['case']=='two_short':
  _,v3=run(old['graph']);row['pre_second_event_at_34_over60']={'time':34/60,'legacy':float(baseline[34].mean()),'v3_global_gate':float(v3[34].mean()),'v4_event_start_gate':float(a[34].mean()),'v4_matches_legacy_before_second':bool(np.array_equal(a[34],baseline[34]))}
  if k==.15:
   sheet=Image.new('RGB',(1280,360),'#e8edf4');d=ImageDraw.Draw(sheet)
   for i,(tag,ar) in enumerate([('legacy',baseline),('v3-global',v3),('v4-causal',a)]):
    for j,n in enumerate([30,33,34,35,36,37,39,42]):sheet.paste(Image.fromarray(ar[n]).convert('RGB'),(j*160,i*120+30));d.text((j*160+2,i*120+3),f'{tag} f{n} gray{ar[n].mean():.0f}',fill='black')
   sheet.save(O/'FLASH_OVERLAP_CAUSAL_GATE.jpg',quality=94)
 rows.append(row)
save('FLASH_GATED_REVISION_V4.json',{'cases':rows,'executed':len(rows),'single_bit_equal':sum(a['single_event_bit_equal_legacy'] is True for a in rows),'finding':'v3 global union gate can expose a future event pulse early while a previous event window is active; v4 event-start gate suppresses this in short-overlap fixture','status':'additional research candidate; not product or adopted default'})
print(json.dumps({'cases':len(rows),'single_bit_equal':sum(a['single_event_bit_equal_legacy'] is True for a in rows),'overlap':[a['pre_second_event_at_34_over60'] for a in rows if a['case']=='two_short']}))
