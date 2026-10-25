from composition_motion import *
folder=O/'frame_backgrounds';folder.mkdir(exist_ok=True)
records=[]
for start in range(0,len(frames),10):
 sheet=Image.new('RGB',(1152,10*180),'#192330');d=ImageDraw.Draw(sheet)
 for row,a in enumerate(frames[start:start+10]):
  t=SimpleNamespace(work_kill_frame_id=a['id'],work_kill_effect_id='',work_kill_review=True,work_kill_strength='strong')
  layers=k._preview_layers(t,ICON[0],ICON[1],(1920,1080),1.)
  badge=Image.new('RGBA',layers[0][0].size)
  for im,alpha,duration,*_ in layers:badge.alpha_composite(im)
  for col,bg in enumerate(['light','dark','complex']):
   tile=background((384,156),bg)
   tile.paste(badge,(0,(156-badge.height)//2),badge)
   sheet.paste(tile,(col*384,row*180+24))
   d.text((col*384+3,row*180+5),a['id']+' / '+bg,fill='white')
  records.append({'id':a['id'],'sheet':f'frame_backgrounds/{start//10+1:03d}.jpg','row':row,'width':384,'backgrounds':['light','dark','complex'],'real_LoL':False,'visual_review':'NOT_RUN','portrait_geometry':'verified' if a.get('portrait_boxes') else 'fallback circle, not validated against actual hole'})
 sheet.save(folder/f'{start//10+1:03d}.jpg',quality=93)
 print(start+len(frames[start:start+10]),flush=True)
save('FRAME_BACKGROUND_EXECUTION_V4.json',{'cases':records,'count':len(records),'scope':'384px output-width composition; native original PNG review separate; no real HUD approval'})
