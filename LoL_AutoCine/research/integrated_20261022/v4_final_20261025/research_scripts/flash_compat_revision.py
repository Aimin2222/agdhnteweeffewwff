from lab_common import *
import re,numpy as np
from PIL import Image,ImageDraw
s=extract('effects.py',{'_enable_expr','_build_video_effect_filters'},{'math':math,'Template':object});rows=[]
sets=[('single',[1.]),('two_short',[.5,.6]),('two_long',[.3,2.2]),('three',[.3,1.4,2.7]),('dense',[.5,.55,.6,.65]),('edges',[0.,1.5,2.95]),('empty',[]),('retimed',[.4,1.6,2.4])]
def run(graph):
 p=ff(['-f','lavfi','-i','color=c=gray:s=320x180:r=60:d=3','-vf',','.join(graph+['format=gray']),'-f','rawvideo','-pix_fmt','gray','pipe:1']);return p,np.frombuffer(p.stdout,np.uint8).reshape(-1,180,320) if not p.returncode else np.empty((0,180,320))
for label,ev in sets:
 for k in [.15,.45,.9]:
  one=s['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':k}),3,[(1.,1.)],False)
  amplitude=re.search(r"brightness='([^*]+)\*exp",one[0]).group(1)
  terms=[f'{amplitude}*exp(-18*abs(t-{x:.3f}))' for x in ev]
  body=terms[0] if terms else '0'
  for term in terms[1:]:body=f'max({body},{term})'
  gate=s['_enable_expr']([(x,x) for x in ev],.15,3) if ev else ''
  # Preserve original enable construction exactly rather than guessing helper semantics.
  legacy=s['_build_video_effect_filters'](SimpleNamespace(video_effects={'flash':k}),3,[(x,x) for x in ev],False) if ev else []
  if ev:gate=re.search(r":enable='([^']+)'",legacy[0]).group(1)
  graph=[f"eq=brightness='{body}':eval=frame:enable='{gate}'"] if ev else []
  p,a=run(graph);means=a.mean((1,2)) if len(a) else [];old,oa=run(legacy) if ev else (None,None)
  eq=bool(np.array_equal(a,oa)) if ev else None
  r=dict(case=label,strength=k,revision='candidate_max_v3_legacy_amplitude',legacy_amplitude=amplitude,events=ev,graph=graph,return_code=p.returncode,decoded_frames=len(a),single_event_bit_equal_legacy=eq if label=='single' else None,gray_at_events=[float(means[min(len(means)-1,round(t*60))]) for t in ev],scope='isolated artificial input; v2 amplitude changed so not compatibility-safe',empty_policy='v3 no-op; legacy helper would IndexError; normal event caller not diagnosed')
  rows.append(r)
  if label=='three' and k==.15:
   sheet=Image.new('RGB',(960,230),'#e7edf4');d=ImageDraw.Draw(sheet)
   for j,t in enumerate(ev):sheet.paste(Image.fromarray(a[round(t*60)]).convert('RGB'),(j*320,30));d.text((j*320+5,5),f'v3 {t}s gray={r["gray_at_events"][j]}',fill='black')
   sheet.save(O/'FLASH_three_candidate_v3_COMPAT.jpg')
save('FLASH_COMPAT_REVISION_V4.json',dict(cases=rows,executed=len(rows),single_event_comparisons=3,single_event_bit_equal_count=sum(x['single_event_bit_equal_legacy'] is True for x in rows),v2_rejected_for_compatibility=True,policy='Missing processing_revision selects unchanged legacy_v1. Explicit max_v3 only on adoption; no automatic project upgrade.'))
print('compat cases',len(rows))
