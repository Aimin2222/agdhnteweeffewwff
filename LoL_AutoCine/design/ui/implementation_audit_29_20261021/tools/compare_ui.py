"""Design review helper. Reads UI screenshots only; does not access or change AutoCine."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
def main():
 p=argparse.ArgumentParser();p.add_argument('screen_id');p.add_argument('actual');p.add_argument('--output',required=True);p.add_argument('--mask-json',help='JSON list of explicit [x,y,w,h] dynamic image masks in source-native pixels');args=p.parse_args()
 root=Path(__file__).resolve().parents[1];screens=json.loads((root/'SCREENS_29.json').read_text('utf-8'));s=next(x for x in screens if x['id']==args.screen_id)
 ref=Image.open(root/s['reference']).convert('RGB');actual=Image.open(args.actual).convert('RGB')
 if ref.size!=actual.size:raise SystemExit('Size mismatch: reference=%s actual=%s. Capture matching client-area pixels; do not auto-resample.'%(ref.size,actual.size))
 masks=json.loads(Path(args.mask_json).read_text('utf-8')) if args.mask_json else []
 out=Path(args.output);out.mkdir(parents=True,exist_ok=True);Image.blend(ref,actual,.5).save(out/'overlay-50.png');ImageChops.difference(ref,actual).save(out/'absolute-difference.png')
 diff=np.abs(np.asarray(ref,dtype=np.float64)-np.asarray(actual,dtype=np.float64));valid=np.ones((ref.height,ref.width),dtype=bool)
 for x,y,w,h in masks:
  if min(x,y,w,h)<0 or x+w>ref.width or y+h>ref.height:raise ValueError('Mask outside canvas')
  valid[int(y):int(y+h),int(x):int(x+w)]=False
 if not valid.any():raise ValueError('Mask excludes all pixels')
 regions=[]
 for r in s['regions']:
  x,y,w,h=map(round,r['rect']);x1=max(0,x);y1=max(0,y);x2=min(ref.width,x+w);y2=min(ref.height,y+h)
  if x2<=x1 or y2<=y1:continue
  v=valid[y1:y2,x1:x2];regions.append({'id':r['id'],'mean_abs_rgb_0_to_255':float(diff[y1:y2,x1:x2][v].mean()) if v.any() else None})
 report={'screen_id':s['id'],'native_size':ref.size,'explicit_masks':masks,'masked_fraction':float(1-valid.mean()),'mean_abs_rgb_0_to_255':float(diff[valid].mean()),'regions':regions,'automatic_acceptance':False,'note':'Inspect geometry, labels, state and real function evidence separately. No score alone is a pass.'}
 (out/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
 print(json.dumps({'screen_id':s['id'],'mean_abs_rgb_0_to_255':report['mean_abs_rgb_0_to_255'],'automatic_acceptance':False}))
if __name__=='__main__':main()
