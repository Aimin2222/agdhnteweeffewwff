from pathlib import Path
import ast,json,numpy as np,collections
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_integrated_research_20261022';O=R/'outputs/autocine_final_research_v3_20261024'
cat=json.loads((W/'source_readonly/LoL_AutoCine/assets/work_kill_assets/catalog.json').read_text('utf-8'));frame=next(x for x in cat['frames'] if x['id']=='083/a_simple_main')
scope={'json':json}
tree=ast.parse((W/'source_readonly/LoL_AutoCine/core/work_kill_assets.py').read_text('utf-8-sig'))
for fn in tree.body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'portrait_layout','_peak_cached'}:
        fn.decorator_list=[];exec(compile(ast.Module(body=[fn],type_ignores=[]),'isolated_work_peak','exec'),scope)
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',14);rows=[];tiles=[]
for effect in cat['effects']:
    peak=scope['_peak_cached'](json.dumps(frame),json.dumps(effect),(str(W/'asset_samples'/effect['path']),))
    alpha=np.asarray(peak.getchannel('A'));boxes=[list(map(round,b)) for b in frame['portrait_boxes']];remaining=[]
    for x,y,w,h in boxes:
        # Interior ellipse only; bounding-rectangle corners intentionally excluded.
        yy,xx=np.ogrid[:h,:w];mask=((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2<.90
        remaining.append(int((alpha[y:y+h,x:x+w][mask]>0).sum()))
    rows.append(dict(effect=effect['id'],portrait_inner_nonzero_alpha=remaining,placement=effect.get('placement'),strengths=[.45,1.0],scope='Isolated declared placement on approved static083, synthetic K/V portraits; no LoL/HUD final output approval'))
    tile=Image.new('RGB',(1440,170),(220,226,233));d=ImageDraw.Draw(tile);d.text((4,0),effect['id'],font=font,fill='black')
    for j,(bg,k) in enumerate([((244,245,246),.45),((244,245,246),1),((25,32,43),.45),((25,32,43),1)]):
        b=Image.new('RGBA',(frame['width'],frame['height']),bg+(255,));
        with Image.open(W/'asset_samples'/frame['path']) as src:b.alpha_composite(src.convert('RGBA'))
        pp=peak.copy();pp.putalpha(pp.getchannel('A').point(lambda a:round(a*k)));b.alpha_composite(pp)
        dd=ImageDraw.Draw(b)
        for z,(x,y,w,h) in enumerate(boxes):dd.ellipse((x,y,x+w,y+h),fill=(40,120,210,255) if z==0 else (190,60,80,255));dd.text((x+w//2-10,y+h//2-10),'K' if z==0 else 'V',fill='white')
        b.thumbnail((350,125));tile.paste(b.convert('RGB'),(j*360,25));d.text((j*360+4,150),('light' if j<2 else 'dark')+f' strength={k}',font=font,fill='black')
    tiles.append(tile)
for start in range(0,len(tiles),10):
    group=tiles[start:start+10];sheet=Image.new('RGB',(1440,len(group)*170))
    for i,t in enumerate(group):sheet.paste(t,(0,i*170))
    sheet.save(O/f'FX_COMBINATIONS_{start//10+1:02}.jpg',quality=92)
(O/'FX_COMBINATION_RESULTS_V3.json').write_text(json.dumps(dict(cases=rows,all_35_portrait_inner_masks_clear=all(not any(r['portrait_inner_nonzero_alpha']) for r in rows),approval_changed=False),ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(dict(effects=len(rows),masked_holes_pass=sum(not any(r['portrait_inner_nonzero_alpha']) for r in rows))))
