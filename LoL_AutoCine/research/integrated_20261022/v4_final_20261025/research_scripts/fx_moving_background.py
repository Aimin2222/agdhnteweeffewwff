from composition_motion import *
folder=O/'fx_moving';folder.mkdir(exist_ok=True);rows=[]
for n,e in enumerate(fx):
 path=folder/f"{n+1:02d}_{e['id']}.mp4";p=subprocess.Popen([FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','ultrafast','-crf','27',str(path)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 stills=[];cached={}
 for j in range(90):
  t=j/30;canvas=Image.new('RGB',(1280,720))
  for si,shape in enumerate(SHAPES):
   scene=background((768,432),'complex',j);power='weak' if t<1.5 else 'strong';elapsed=(t%1.5)
   # Quantized alpha samples from the real existing renderer, fixed 4 shapes; no new product function.
   key=(shape,power,round(elapsed*30));badge=cached.get(key)
   if badge is None:badge=pair(shape,e['id'],power,elapsed);cached[key]=badge
   for row in range(3):scene.paste(badge,(352,38+row*128),badge)
   tile=scene.resize((640,360));d=ImageDraw.Draw(tile);d.text((8,25),f'{shape} / {power} / {t:.2f}s / artificial',fill='white');canvas.paste(tile,(si%2*640,si//2*360))
  p.stdin.write(canvas.tobytes())
  if j in (12,57):stills.append(canvas.copy())
 p.stdin.close();err=p.stderr.read().decode(errors='replace');rc=p.wait();dec=ff(['-i',str(path),'-vf','scale=32:18','-f','rawvideo','-pix_fmt','gray','pipe:1'])
 count=len(dec.stdout)//576;rows.append(dict(effect=e['id'],shape_count=4,strengths=['weak','strong'],max_stack=3,frames=count,expected_frames=90,status='PASS' if rc==0 and dec.returncode==0 and count==90 else 'FAIL',scope='artificial moving backdrop, existing peak alpha function, 4 shape variants; not native LoL or product GPU',stderr=err))
 sheet=Image.new('RGB',(1280,1440));[sheet.paste(im,(0,i*720)) for i,im in enumerate(stills)];sheet.save(folder/f"{n+1:02d}_{e['id']}.jpg",quality=92)
 save('FX_MOVING_EXECUTION_V4.json',dict(cases=rows,planned=35,formal_approval_changed=False));print('moving FX',n+1,flush=True)
