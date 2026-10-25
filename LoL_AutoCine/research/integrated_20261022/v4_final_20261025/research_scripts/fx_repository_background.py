from composition_motion import *
root=O/'fx_repository_background';root.mkdir(exist_ok=True)
src=W/'camera_comparison_20261020.jpg';im=Image.open(src).convert('RGB')
crops={'RED_reference':im.crop((0,26,320,206)),'BLUE_reference':im.crop((320,232,640,412))};rows=[]
for n,e in enumerate(fx):
 sheet=Image.new('RGB',(1280,4*202+42),'#e8edf4');d=ImageDraw.Draw(sheet)
 d.text((8,10),f"{e['id']} / repository camera QA still enlarged320x180 / not live LoL PASS / fallback geometry provisional",fill='black')
 for si,shape in enumerate(SHAPES):
  for pi,power in enumerate(['weak','strong']):
   for bi,(label,bg) in enumerate(crops.items()):
    scene=bg.resize((960,540),Image.Resampling.LANCZOS);badge=pair(shape,e['id'],power,elapsed=.08)
    for row in range(3):scene.paste(badge,(960-384-32,24+row*164),badge)
    x=(pi*2+bi)*320;y=42+si*202;sheet.paste(scene.resize((320,180)),(x,y+22));d.text((x+3,y+3),f'{shape}/{power}/{label}',fill='black')
    rows.append({'fx':e['id'],'shape':shape,'strength':power,'background':label,'native_background_crop':[320,180],'working_size':[960,540],'stack':3,'live_LoL':False,'geometry':'verified083 only','approval_changed':False})
 sheet.save(root/f"{n+1:02d}_{e['id']}.jpg",quality=93)
save('FX_REPOSITORY_BACKGROUND_V4.json',{'cases':rows,'count':len(rows),'source':{'url':'https://github.com/Aimin2222/agdhnteweeffewwff/blob/b32513ada0a5ada7585972e06716ff84829bcb23/LoL_AutoCine/assets/ui_reference/camera_comparison_20261020.jpg','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'dimensions':list(im.size),'scope':'repository camera QA image, crop enlarged, not current live capture, no original HUD evidence'},'offline_mock_rejected':{'file':'mock_preview_offline.jpg','reason':'offline mock provenance cannot certify real capture; not used as actual LoL background'},'visual_review':'separate log required'})
print('composites',len(rows))
