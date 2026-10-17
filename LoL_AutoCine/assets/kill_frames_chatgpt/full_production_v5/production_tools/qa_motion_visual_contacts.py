"""Extract actual encoded comparison-video time strips for representative mode review.
Diagnostic images only; never edits production images or movies.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,cv2,sys
R=Path('LoL_AutoCine/assets/kill_frames_chatgpt/full_production_v5')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main(catalog):
 p=Path(catalog);raw=p.read_bytes();d=json.loads(raw);chosen={}
 for a in d['assets']:
  folder=Path(a['outputs'][0]['file']).parent;s=json.loads((folder/'motion.json').read_text(encoding='utf-8'))
  mode=s['mode'];score=bool(a.get('source_visual_repair_required'))
  if mode not in chosen or score<chosen[mode][0]:chosen[mode]=(score,a,s)
 tag=hashlib.sha256(raw).hexdigest()[:12];out=R/'qa'/('motion_timeline_'+tag);assert not out.exists();out.mkdir()
 rows=[];times=[-.2,.1,.24,.6,1.2,2.4];font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',17)
 for mode,(_,a,s) in sorted(chosen.items()):
  x=next(x for x in a['outputs'] if x['file'].endswith('.mp4'));video=Path(x['file']);assert sha(video)==x['sha256']
  cap=cv2.VideoCapture(str(video));assert round(cap.get(cv2.CAP_PROP_FRAME_COUNT))==90
  tiles=[]
  for t in times:
   k=round((t+.3)*30);cap.set(cv2.CAP_PROP_POS_FRAMES,k);ok,bgr=cap.read();assert ok
   im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));tile=im.crop((704,350,1216,638)).resize((256,144),Image.Resampling.LANCZOS);tiles.append(tile)
  cap.release();rows.append((a['key'],mode,x,tiles))
 pages=[]
 for start in range(0,len(rows),5):
  batch=rows[start:start+5];canvas=Image.new('RGB',(1536,len(batch)*180),'#1c2432');draw=ImageDraw.Draw(canvas)
  for j,(key,mode,x,tiles) in enumerate(batch):
   y=j*180;draw.text((8,y+3),key+' / '+mode+' / actual encoded MP4',font=font,fill='white')
   for k,tile in enumerate(tiles):
    canvas.paste(tile,(k*256,y+32));draw.text((k*256+5,y+150),str(times[k])+'s',font=font,fill='white')
  p=out/('page_'+str(start//5).zfill(2)+'.jpg');canvas.save(p,quality=94)
  pages.append(dict(file=p.as_posix(),sha256=sha(p),assets=[dict(key=k,mode=m,video_file=x['file'],video_sha256=x['sha256']) for k,m,x,_ in batch]))
 result=dict(scope='representative_modes_only_not_all_asset_visual_approval',catalog=Path(catalog).as_posix(),catalog_snapshot_sha256=hashlib.sha256(raw).hexdigest(),catalog_count=d['count'],representative_count=len(rows),times_s=times,pages=pages,visual_inspection_recorded=False,final_approved=0)
 (out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(manifest=(out/'manifest.json').as_posix(),modes=len(rows),pages=len(pages))))
if __name__=='__main__':main(sys.argv[1])
