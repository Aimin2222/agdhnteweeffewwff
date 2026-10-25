from lab_common import *
from PIL import Image,ImageDraw,ImageFont
import numpy as np,hashlib,csv,collections,time
q=load(V3/'ASSET_FULL_QA_V2.json')['items'];frames=[x for x in q if x['kind']=='frame'];cat=load(OLD/'source_readonly/LoL_AutoCine/assets/work_kill_assets/catalog.json');cb={x['id']:x for x in cat['frames']}
scope=extract('kill_icons.py',{'badge_motion_xy','normalize_motion','badge_plan'},{'math':math,'MOTION_STYLES':{x:x for x in MOTIONS}})
rows=[];motionrows=[];counts=collections.Counter();total_samples=0
for idx,a in enumerate(frames):
 with Image.open(OLD/'asset_samples'/a['path']) as im:
  im=im.convert('RGBA');ar=np.asarray(im);alpha=ar[:,:,3];rgb=ar[:,:,:3];h,w=alpha.shape
  edge=np.concatenate((alpha[0],alpha[-1],alpha[1:-1,0],alpha[1:-1,-1]));visible=alpha>8;ys,xs=np.nonzero(visible);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
  near=(alpha>0)&(alpha<64);red_excess=((rgb[:,:,0].astype(int)-rgb[:,:,1].astype(int)>60)&(rgb[:,:,0].astype(int)-rgb[:,:,2].astype(int)>40)&near)
  layout=cb[a['id']].get('portrait_boxes');r={'id':a['id'],'number':a['number'],'theme':a['theme'],'native_pixel_scan':True,'width':w,'height':h,'sha256_unchanged':hashlib.sha256((OLD/'asset_samples'/a['path']).read_bytes()).hexdigest()==a['actual_sha256'],'visible_bbox':bbox,'edge_alpha_gt8':int((edge>8).sum()),'edge_alpha_ge128':int((edge>=128).sum()),'low_alpha_red_excess_pixels':int(red_excess.sum()),'red_excess_not_automatic_failure':True,'portrait_geometry_verified':bool(layout),'formal_status':a['catalog_status'],'native_visual_state':'NOT_RUN','source_fidelity':'REVIEW_REQUIRED','actual_HUD_state':'NOT_RUN','criteria_pass':False}
  rows.append(r)
  # Product's Work default width and row spacing, not V3's illustrative 480 rectangle.
  for width,height in [(1920,1080),(1366,768),(1280,720)]:
   dw=384;dh=int(h*dw/w/2)*2;bx=width-dw-32;by=62;step=164
   for fps in [30,60]:
    ts=np.arange(round(2.5*fps))/fps
    events=[.35,.60,.85,1.10,1.35];plan=scope['badge_plan']([('artificial',x+.1) for x in events],2.6,1.45)
    for motion in MOTIONS:
     max_active=0;static_clip=0;enter_clip=0;hud_hits=0;max_delta=0.;active_samples=0
     for entry in plan:
      t=ts[(ts>=entry['start'])&(ts<min(2.5,entry['end']))];e=np.maximum(0,t-entry['start']);u=np.clip(1-e/.26,0,1);z=u*u*(3-2*u)
      dx=np.zeros_like(e);dy=dx.copy()
      if motion=='slide_left':dx=-(width+20)*z
      elif motion=='slide_right':dx=(width+20)*z
      elif motion=='slide_up':dy=(height+20)*z
      elif motion=='slide_down':dy=-(height+20)*z
      elif motion=='pop':dx=16*np.exp(-18*e)*np.cos(28*e)
      x=bx+dx;y=by+step*entry['row']+dy
      clip=(x<0)|(y<0)|(x+dw>width)|(y+dh>height);static_clip+=int((clip&(e>=.26)).sum());enter_clip+=int((clip&(e<.26)).sum())
      # Synthetic declared minimap region; real LoL HUD not asserted.
      hud_hits+=int(((x+dw>width-230)&(y+dh>height-230)).sum());active_samples+=len(t)
     max_active=max(sum(p['start']<=tt<p['end'] for p in plan) for tt in ts)
     total_samples+=active_samples
     motionrows.append({'frame_id':a['id'],'motion':motion,'width':width,'height':height,'fps':fps,'display_width':dw,'display_height':dh,'event_count':5,'max_active':max_active,'static_clipped_samples':static_clip,'entrance_clipped_samples':enter_clip,'synthetic_minimap_bbox_hits':hud_hits,'evaluated_active_layer_samples':active_samples,'scope':'source-equation geometry, all sampled frames, source Work at-kill plan; no rendered/video/actual-HUD PASS'})
 if (idx+1)%100==0:print('frames processed',idx+1,flush=True)
save('NATIVE_PIXEL_LEDGER_V4.json',{'items':rows,'count':len(rows),'native_visual_separate':True,'native_pixels_scanned':sum(x['width']*x['height'] for x in rows),'hash_changed':sum(not x['sha256_unchanged'] for x in rows)})
with (O/'ALL652_MOTION_GEOMETRY_V4.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(motionrows[0]));wr.writeheader();wr.writerows(motionrows)
save('MOTION_GEOMETRY_SUMMARY_V4.json',{'frame_count':652,'motions':6,'sizes':3,'frame_rates':[30,60],'scenario_count':len(motionrows),'active_layer_samples':total_samples,'scenarios_static_clip':sum(x['static_clipped_samples']>0 for x in motionrows),'max_active':int(max(x['max_active'] for x in motionrows)),'scenarios_synthetic_minimap_hit':sum(x['synthetic_minimap_bbox_hits']>0 for x in motionrows),'scope':'native pixel metrics and full sampled numeric motion geometry only, not artistic/native visual approval or GPU runtime'})
print(json.dumps({'frames':len(rows),'motion_scenarios':len(motionrows),'active_layer_samples':total_samples}))
