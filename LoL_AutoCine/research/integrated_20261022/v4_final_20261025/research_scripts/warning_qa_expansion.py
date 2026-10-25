"""Proposed independent warning rules; synthetic pixels/metadata, never product QA PASS."""
from lab_common import *
import numpy as np
def check(a,m):
 out=[];lum=a.mean((1,2,3));delta=np.abs(np.diff(a.astype(float),axis=0)).mean((1,2,3))
 if sum(lum<5)>=m['fps'] and not m.get('intentional_black'):out.append('BLACK_REVIEW')
 if len(delta)>=m['fps']-1 and max(delta)<.1 and m.get('motion_expected'):out.append('FREEZE_REVIEW')
 if m.get('orientation_reference')=='inverted':out.append('ORIENTATION_REVIEW')
 if m.get('max_pts_gap',1/m['fps'])>1.5/m['fps']:out.append('FRAME_GAP_REVIEW')
 if m.get('audio_expected') and not m.get('audio_stream',True):out.append('MISSING_AUDIO')
 if abs(m.get('offset_ms',0))>50:out.append('AV_SYNC_REVIEW')
 if np.mean(lum>245)>.2 and not m.get('teleport') and not m.get('intentional_flash'):out.append('FLASH_REVIEW')
 if m.get('critical_occlusion_fraction',0)>.1:out.append('OCCLUSION_REVIEW')
 if m.get('clipped_fraction',0)>.01 and not m.get('entrance'):out.append('CLIPPING_REVIEW')
 if m.get('grayscale') and not m.get('dead'):out.append('GRAYSCALE_REVIEW')
 if m.get('red_border') and not m.get('low_hp'):out.append('RED_BORDER_REVIEW')
 return out
groups=[('black',{'black':True},['BLACK_REVIEW'],{'black':True,'intentional_black':True},[]),('freeze',{'still':True,'motion_expected':True},['FREEZE_REVIEW'],{'still':True},[]),('orientation',{'orientation_reference':'inverted'},['ORIENTATION_REVIEW'],{'orientation_reference':'upright'},[]),('drop',{'max_pts_gap_factor':3},['FRAME_GAP_REVIEW'],{},[]),('audio',{'audio_expected':True,'audio_stream':False},['MISSING_AUDIO'],{'audio_expected':False,'audio_stream':False},[]),('sync',{'offset_ms':-80},['AV_SYNC_REVIEW'],{'offset_ms':40},[]),('flash',{'white':True},['FLASH_REVIEW'],{'white':True,'intentional_flash':True},[]),('occlusion',{'critical_occlusion_fraction':.4},['OCCLUSION_REVIEW'],{'critical_occlusion_fraction':.05},[]),('clipping',{'clipped_fraction':.2},['CLIPPING_REVIEW'],{'clipped_fraction':.2,'entrance':True},[]),('death_gray',{'grayscale':True},['GRAYSCALE_REVIEW'],{'grayscale':True,'dead':True},[]),('low_hp_red',{'red_border':True},['RED_BORDER_REVIEW'],{'red_border':True,'low_hp':True},[]),('teleport',{'white':True},['FLASH_REVIEW'],{'white':True,'teleport':True},[]),('intentional_black',{'black':True},['BLACK_REVIEW'],{'black':True,'intentional_black':True},[]),('normal_camera',{'orientation_reference':'inverted'},['ORIENTATION_REVIEW'],{'orientation_reference':'upright','offset_ms':-20},[])]
rows=[]
for fps in (30,60):
 for name,bad,be,good,ge in groups:
  for variant,m,expected in [('abnormal_or_unexplained',bad,be),('normal_or_context_explained',good,ge)]:
   m=dict(m,fps=fps);a=np.zeros((fps*2,24,32,3),np.uint8)
   for j in range(len(a)):a[j]=80+(j%20)*3
   if m.get('black'):a[:]=0
   if m.get('still'):a[:]=90
   if m.get('white'):a[:fps]=255
   if 'max_pts_gap_factor' in m:m['max_pts_gap']=m.pop('max_pts_gap_factor')/fps
   actual=check(a,m);rows.append(dict(id=f'{name}_{variant}_{fps}',category=name,fps=fps,metadata=m,expected=expected,actual=actual,status='PASS' if expected==actual else 'FAIL',scope='designed fixture only; orientation/semantic/occlusion/clipping supplied metadata, not learned pixel detection'))
save('WARNING_QA_EXPANDED_V4.json',dict(cases=rows,executed=len(rows),passed=sum(x['status']=='PASS' for x in rows),product_pass=False,thresholds='research proposals; warning only; no auto-fix/delete/approval changes',unverified='actual LoL false-positive/negative rates; unknown context should ask for review rather than silently suppress'))
print(json.dumps({'executed':len(rows),'passed':sum(x['status']=='PASS' for x in rows)}))
