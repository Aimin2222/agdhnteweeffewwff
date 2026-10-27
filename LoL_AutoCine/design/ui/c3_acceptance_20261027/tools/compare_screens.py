"""Offline screenshot comparison aid. No app launch, browser, network or UI acceptance automation."""
from PIL import Image,ImageChops,ImageStat,ImageDraw
from pathlib import Path
import argparse,json

def compare(expected,actual,out,masks=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 a=Image.open(expected).convert('RGB');b=Image.open(actual).convert('RGB')
 result=dict(status='REVIEW',scope='static pixels only; not functional acceptance',expected_size=list(a.size),actual_size=list(b.size),resized=False,mask_boxes=masks or [])
 if a.size!=b.size:
  result.update(status='FAIL',reason='pixel-size mismatch; do not silently resize')
 else:
  allowed=Image.new('L',a.size,255);draw=ImageDraw.Draw(allowed)
  for box in masks or []:
   if len(box)!=4 or any(not isinstance(v,int) for v in box):raise ValueError('mask box must contain 4 integer px values')
   x,y,x2,y2=box
   if not (0<=x<x2<=a.width and 0<=y<y2<=a.height):raise ValueError('mask outside image')
   draw.rectangle((x,y,x2-1,y2-1),fill=0)
  remaining=allowed.histogram()[255]
  if remaining<a.width*a.height*.5:raise ValueError('more than half the image masked; narrow the comparison scope explicitly')
  diff=ImageChops.difference(a,b);diff.paste((0,0,0),mask=ImageChops.invert(allowed))
  sums=ImageStat.Stat(diff).sum;rr,gg,bb=diff.split();peak=ImageChops.lighter(ImageChops.lighter(rr,gg),bb);hist=peak.histogram();changed=sum(hist[1:]);result.update(mean_absolute_RGB_error=sum(sums)/(remaining*3),changed_UI_pixels=changed,compared_UI_pixels=remaining,changed_UI_fraction=changed/remaining,reason='metrics require human region/geometry review; no automatic PASS')
  Image.blend(a,b,.5).save(out/'overlay_50.png');diff.save(out/'difference.png');allowed.save(out/'compared_region_mask.png')
 (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--expected',required=True);p.add_argument('--actual',required=True);p.add_argument('--out',required=True);p.add_argument('--masks',help='JSON list of [x1,y1,x2,y2] int boxes. Dynamic image/time areas only.');args=p.parse_args();masks=json.loads(Path(args.masks).read_text('utf-8-sig')) if args.masks else []
 print(json.dumps(compare(args.expected,args.actual,args.out,masks),ensure_ascii=True))
