from composition_motion import *
import io

def decode_existing():
 rows=[];tiles=[]
 for p in sorted(O.glob('FX_*_ARTIFICIAL.mp4')):
  r=ff(['-i',str(p),'-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
  a=np.frombuffer(r.stdout,np.uint8).reshape(-1,180,320,3)
  nums=[0,min(8,len(a)-1),min(12,len(a)-1),len(a)-1]
  sheet=Image.new('RGB',(1280,204),'#e8edf4');d=ImageDraw.Draw(sheet)
  for i,n in enumerate(nums):
   sheet.paste(Image.fromarray(a[n]),(i*320,24));d.text((i*320+3,3),f'{p.stem} / frame {n}',fill='black')
  name=p.stem+'_TEMPORAL.jpg';sheet.save(O/name,quality=94)
  rows.append({'video':p.name,'decoded_frames':len(a),'expected':18,'rc':r.returncode,'status':'PASS' if len(a)==18 and r.returncode==0 else 'FAIL','sample_frames':nums,'sheet':name,'scope':'decode integrity only; visual review separate'})
 save('EXISTING_FX_DECODE_V4.json',{'cases':rows})

def preview_export():
 rows=[]
 original=k.render_pair('083/a_simple_main',ICON[0],ICON[1],review=True)
 layerpath=W/'tmp'/'parity_badge.png';original.save(layerpath)
 entries=SimpleNamespace(layers=[{'time':.3,'layers':[{'width':original.width,'height':original.height,'index':0,'kind':'base'}]}],strength=1.)
 t=SimpleNamespace(work_kill_frame_id='083/a_simple_main',work_kill_effect_id='',work_kill_review=True,work_kill_strength='strong',kill_icon_position='right-top',kill_icon_scale=1.,kill_icon_duration=1.55,kill_icon_opacity=1.,kill_icon_motion='instant',kill_stack_gap=4)
 for w,h in [(1920,1080),(1366,768),(1280,720)]:
  graph=k.with_work_badges('[0:v]null[vout]',1,entries,duration=1.,motion='instant')
  r=ff(['-f','lavfi','-i',f'color=black@0.0:s={w}x{h}:r=30:d=1,format=rgba','-loop','1','-i',str(layerpath),'-filter_complex',graph,'-map','[vout]','-frames:v','20','-f','rawvideo','-pix_fmt','rgba','pipe:1'])
  if r.returncode:rows.append({'size':[w,h],'rc':r.returncode,'stderr':r.stderr.decode(errors='replace')});continue
  a=np.frombuffer(r.stdout,np.uint8).reshape(-1,h,w,4);exp=Image.fromarray(a[15]);mir=k.render_preview_pair(t,ICON[0],ICON[1],.2,size=(w,h))
  def bbox(im):return im.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox()
  # FFmpeg auto overlay may force background alpha opaque; difference-from-black bbox is also recorded.
  rgb=np.asarray(exp)[:,:,:3];mask=rgb.max(2)>8;ys,xs=np.nonzero(mask)
  exportbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
  mirrorbox=bbox(mir)
  rows.append({'size':[w,h],'rc':r.returncode,'decoded_frames':len(a),'export_visible_rgb_bbox':exportbox,'mirror_alpha_bbox':mirrorbox,'export_nominal_width':384,'mirror_nominal_width':round(384*w/1920),'same_layout':w==1920,'scope':'isolated unchanged CPU export graph vs mirror with same source pair; RGB and alpha boxes not identical metrics'})
  sheet=Image.new('RGB',(1280,382),'#e8edf4');d=ImageDraw.Draw(sheet)
  for i,im in enumerate([exp,mir]):
   bg=Image.new('RGBA',im.size,'#141b22');bg.alpha_composite(im);sheet.paste(bg.convert('RGB').resize((640,360)),(i*640,22));d.text((i*640+6,3),f'{w}x{h} '+('EXPORT fixed384' if i==0 else 'MIRROR scaled384'),fill='black')
  sheet.save(O/f'PREVIEW_EXPORT_{w}.jpg',quality=94)
 save('PREVIEW_EXPORT_PARITY_V4.json',{'cases':rows,'live_LoL':False,'proposal':'explicit reference coordinate space, preserve legacy revision, compare export at actual output resolution before changing scaling'})

def protection():
 checks=[]
 for a in load(OLD/'source_hashes.json')['files']:
  p=OLD/'source_readonly'/a['path'];checks.append({'group':'source','path':a['path'],'exists':p.exists(),'same':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']})
 for a in load(V3/'ASSET_FULL_QA_V2.json')['items']:
  p=OLD/'asset_samples'/a['path'];checks.append({'group':'work_asset','path':a['path'],'exists':p.exists(),'same':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==a['actual_sha256']})
 root=Path('C:/Users/saoan/Documents/Codex/2026-10-18/lol-autocine-work-windows-pc-usb-2/work/restored_repository')
 for a in load(V3/'ORIGINAL_89_PROTECTION_MAPPING_V3.json')['files']:
  p=root/a['path'];checks.append({'group':'original','path':a['path'],'exists':p.exists(),'same':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']})
 for a in load(V3/'LEGACY_BADGE_PROTECTION_V3.json')['items']:
  p=OLD/'legacy_asset_cache_v3'/a['path'];checks.append({'group':'legacy37','path':a['path'],'exists':p.exists(),'same':p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']})
 save('PROTECTION_RECHECK_V4.json',{'checks':checks,'checked':len(checks),'different_or_missing':sum(not a['same'] for a in checks),'formal_status_mutations':0,'scope':'read-only local caches; remote commit prefix audited separately'})
 rofl=list(Path('C:/Users/saoan/Documents/Codex').rglob('*.rofl'))
 save('REPLAY_INPUT_SEARCH_V4.json',{'scope':'Documents/Codex recursively, no arbitrary user folders','rofl_count':len(rofl),'paths':[str(p) for p in rofl],'no_launch_or_replay_command_sent':True})

if __name__=='__main__':
 decode_existing();preview_export();protection()
