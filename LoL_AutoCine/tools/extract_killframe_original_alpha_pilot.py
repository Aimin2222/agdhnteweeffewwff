"""Three-theme source-pixel alpha prototype, no generation or inpainting.

RGB is never edited. Fitted local background only informs alpha; original
flattened pixels cannot uniquely recover obscured artwork or true glow color.
No application imports, no camera/GPU/audio edits, no private path in metadata.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw

APP=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def shape_mask(size,shapes,box):
    scale=4;out=Image.new('L',(size[0]*scale,size[1]*scale),0);draw=ImageDraw.Draw(out)
    for shape in shapes:
        kind,values=next(iter(shape.items()))
        if kind=='polygon':
            points=[((x-box[0])*scale,(y-box[1])*scale) for x,y in values];draw.polygon(points,fill=255)
        else:
            coords=[(v-box[i%2])*scale for i,v in enumerate(values)]
            if kind=='ellipse':draw.ellipse(coords,fill=255)
            elif kind=='rectangle':draw.rectangle(coords,fill=255)
            else:raise ValueError(kind)
    return np.asarray(out.resize(size,Image.Resampling.BOX),dtype=np.float32)/255.

def extract(source,config):
    box=config['crop_box'];crop=source.crop(box).convert('RGB');rgb=np.asarray(crop)
    h,w=rgb.shape[:2];yy,xx=np.mgrid[:h,:w];design=np.stack([np.ones_like(xx),xx/max(w-1,1),yy/max(h-1,1)],axis=-1).astype(float)
    # Robust plane fit from low-contrast pixels; texture/glow remains ambiguous.
    values=rgb.reshape(-1,3).astype(float);matrix=design.reshape(-1,3)
    luma=np.mean(values,axis=1);light=config['background_kind']=='light'
    selected=luma>=np.percentile(luma,55) if light else luma<=np.percentile(luma,45)
    for _ in range(5):
        coeff=np.linalg.lstsq(matrix[selected],values[selected],rcond=None)[0]
        residual=np.linalg.norm(values-matrix@coeff,axis=1)
        selected=residual<=np.percentile(residual,40)
    bg=(matrix@coeff).reshape(h,w,3);distance=np.linalg.norm(rgb.astype(float)-bg,axis=-1)
    low,high=(10.,58.) if light else (13.,75.)
    t=np.clip((distance-low)/(high-low),0,1);alpha=t*t*(3-2*t)
    if config['roi_regions']:alpha*=shape_mask(crop.size,config['roi_regions'],box)
    if config['portrait_holes']:alpha*=1-shape_mask(crop.size,config['portrait_holes'],box)
    if config.get('exclude_regions'):alpha*=1-shape_mask(crop.size,config['exclude_regions'],box)
    rgba=np.dstack([rgb,np.rint(alpha*255).astype('uint8')]);image=Image.fromarray(rgba)
    return image,{'model':'robust_local_rgb_plane','coefficients':coeff.tolist(),'distance_thresholds':[low,high],'iterations':5,'rgb_modified':False}

def checker(size):
    y,x=np.mgrid[:size[1],:size[0]];v=np.where(((x//16+y//16)%2)[...,None],185,235).astype('uint8');return Image.fromarray(np.repeat(v,3,axis=2)).convert('RGBA')

def build(app=APP):
    root=app/'assets/kill_frames';spec=json.loads((root/'pilot_extraction_spec.json').read_text(encoding='utf-8'));manifest={'schema_version':1,'status':'prototype_not_approved','source_base_commit':spec['base_commit'],'generated_or_inpainted':False,'rgb_policy':'Every output RGB pixel equals the source crop, including hidden pixels; only alpha changes.','game_background':'qa/lol_background.png','assets':[],'limitations':['Flattened RGB cannot uniquely identify underlying alpha, recover decorations occluded by portraits, or unmatte glows without changing RGB.','White/light background motifs and dark metal require human mask review; automated alpha integrity is not visual approval.']}
    game=Image.open(root/'qa/lol_background.png').convert('RGBA')
    for theme,data in spec['themes'].items():
        sourcepath=app/'assets/kill_concepts'/data['source_file'];source=Image.open(sourcepath).convert('RGB');target=root/'themes'/theme;target.mkdir(parents=True,exist_ok=True)
        sheet=Image.new('RGB',(2080,1100),(48,51,60));draw=ImageDraw.Draw(sheet);draw.text((12,8),theme+' | ORIGINAL PIXELS / ALPHA PROTOTYPE / NOT APPROVED',fill='white')
        for j,(name,config) in enumerate(data['assets'].items()):
            image,method=extract(source,config);path=target/(name+'.png');image.save(path);mask=target/(name+'.alpha.png');image.getchannel('A').save(mask)
            a=np.asarray(image.getchannel('A'));manifest['assets'].append({'theme':theme,'source_file':data['source_file'],'source_sha256':sha(sourcepath),'source_dimensions':list(source.size),'file':path.relative_to(root).as_posix(),'sha256':sha(path),'mask_file':mask.relative_to(root).as_posix(),'mask_sha256':sha(mask),'crop_box':config['crop_box'],'portrait_holes':config['portrait_holes'],'roi_regions':config['roi_regions'],'exclude_regions':config.get('exclude_regions',[]),'alpha_model':method,'alpha_counts':{'zero':int((a==0).sum()),'partial':int(((a>0)&(a<255)).sum()),'opaque':int((a==255).sum())},'status':'needs_manual_mask','visual_review_notes':['Prototype: inspect glow/background remnants and fine edges on all four backgrounds before acceptance.']})
            for k,kind in enumerate(['checker','black','white','LoL gameplay']):
                size=(520,190);bg=checker(size) if k==0 else Image.new('RGBA',size,'black' if k==1 else 'white') if k<3 else game.resize(size,Image.Resampling.LANCZOS)
                bg.alpha_composite(image,((520-image.width)//2,(190-image.height)//2));sheet.paste(bg.convert('RGB'),(k*520,50+j*210));draw.text((k*520+10,35+j*210),name+' | '+kind,fill='white')
        sheet.save(root/'qa'/(theme+'_comparison.png'))
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--app',type=Path,default=APP);args=parser.parse_args();m=build(args.app);print(json.dumps({'assets':len(m['assets']),'status':m['status'],'rgb_changed':False}))
