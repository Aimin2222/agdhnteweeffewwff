#!/usr/bin/env python3
"""Reference-guided, rebuildable PROJECT frames; QA CANDIDATES ONLY, not final."""
import sys,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

src=Path(sys.argv[1])/"image-gen-1(8).png"
out=Path(sys.argv[2])
out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((out.parents[1]/"manifest.json").read_text(encoding="utf-8"))
entry=next(a for a in manifest["items"] if a["source"]=="image-gen-1(8).png")
actual=hashlib.sha256(src.read_bytes()).hexdigest()
assert actual==entry["source_sha256"],"Source SHA mismatch! Stop."
whole=Image.open(src).convert("RGB")
sx,sy=whole.width/1100,whole.height/825

def take(v):
    return whole.crop(tuple(round(a*(sx if i%2==0 else sy)) for i,a in enumerate(v))).convert("RGB")

def sprite(segment,coords,mode):
    a=np.asarray(segment).astype(np.float32)
    x0,y0,x1,y1=coords
    region=a[y0:y1,x0:x1];r,g,b=region[:,:,0],region[:,:,1],region[:,:,2]
    light=np.maximum.reduce([r,g,b])
    if mode=="weak":
        energy=np.maximum((.82*b+.18*g-r-24)*1.10,(light-110)*.90)
        mask=np.clip(energy/85,0,1)
        mask=np.where(light>175,np.maximum(mask,np.clip((light-95)/100,0,1)),mask)
    else:
        pink=np.maximum(0,r+.62*b-1.3*g-33)
        blue=np.maximum(0,b+.48*g-1.05*r-38)
        bright=np.maximum(0,light-108)
        mask=np.clip(np.maximum.reduce([pink*.88,blue*.94,bright*.78])/86,0,1)
        mask=np.maximum(mask,np.where(light>220,.94,0))
    xx,yy=np.meshgrid(np.arange(x1-x0),np.arange(y1-y0))
    radius=(98,59) if mode=="weak" else ((x1-x0)*.53,(y1-y0)*.57)
    ell=((xx-(x1-x0)/2)/radius[0])**2+((yy-(y1-y0)/2)/radius[1])**2
    mask *= np.clip((1.2-ell)*4,0,1)
    mask[:4,:]=0
    mask[-2:,:]=0
    return Image.fromarray(np.dstack((region.astype("uint8"),(mask*255).astype("uint8"))),"RGBA")

def render(mode,subcrop,center,borders,shape):
    s=3
    w,h=shape
    result=Image.new("RGBA",(w*s,h*s))
    vector=Image.new("RGBA",result.size)
    d=ImageDraw.Draw(vector)
    def p(x,y):return(round(x*s),round(y*s))
    for side,(x,y,dx,dy,primary,soft,hi) in enumerate(borders):
        for pad,color,width in ((0,soft,3),(1,primary,2),(4,(16,32,52,185) if mode=="weak" else (68,13,50,190),2)):
            d.line([p(x+pad,y+pad),p(x+dx-pad,y+pad),p(x+dx-pad,y+dy-pad),p(x+pad,y+dy-pad),p(x+pad,y+pad)],fill=color,width=width*s)
        d.line([p(x+3,y+3),p(x+dx*.45,y+3)],fill=hi,width=s)
        d.line([p(x+4,y+dy-3),p(x+dx-4,y+dy-3)],fill=primary,width=s)
        for px,py,fx,fy in ((x,y,1,1),(x+dx,y,-1,1),(x,y+dy,1,-1),(x+dx,y+dy,-1,-1)):
            d.line([p(px+fx*3,py+fy*16),p(px+fx*3,py+fy*3),p(px+fx*15,py+fy*3)],fill=hi,width=s)
        if mode=="weak":
            near=x+dx if side==0 else x
            end=135 if side==0 else 288
            d.line([p(near,54),p(end,66)],fill=(*primary[:3],130),width=s)
            d.line([p(near,75),p(end,62)],fill=(*primary[:3],100),width=s)
    result.alpha_composite(vector)
    crop=sprite(subcrop,center,mode)
    crop=crop.resize((crop.width*s,crop.height*s),Image.Resampling.LANCZOS)
    x0,y0,_,_=center
    result.alpha_composite(crop,(x0*s,(y0+7 if mode=="weak" else y0+5)*s))
    return result

weaksrc=take((36,236,355,324))
weak=render("weak",weaksrc,(122,8,305,114),[
    (20,15,100,92,(42,182,248,230),(16,65,111,185),(166,236,255,255)),
    (307,15,100,92,(228,63,143,230),(76,25,86,185),(255,196,225,255))
],(420,128))
strongsrc=take((555,234,951,329))
strong=render("strong",strongsrc,(145,4,392,123),[
    (47,19,95,94,(235,59,141,246),(68,13,50,255),(255,180,214,245)),
    (398,19,95,94,(252,73,128,246),(68,13,50,255),(255,180,214,255))
],(521,143))
for name,im in (("weak",weak),("strong",strong)):
    im.save(out/f"project_{name}_review_rgba.png")
    W,H=im.size
    proof=Image.new("RGB",(W*2,H*2))
    for i,bg in enumerate([(19,24,38),(245,247,250),(39,39,42),(184,190,200)]):
        block=Image.new("RGBA",(W,H),(*bg,255))
        block.alpha_composite(im)
        proof.paste(block.convert("RGB"),((i%2)*W,(i//2)*H))
    proof.save(out/f"project_{name}_qa.jpg",quality=92)
    assert im.mode=="RGBA"
    assert im.getpixel((0,0))[3]==0
    print(name,im.size,"alpha_checked",True)
(out/"README.md").write_text(
"""# PROJECT preview / not final
Source: `kill_concepts/image-gen-1(8).png` (SHA-256 checked against manifest).
Files are original-reference-guided RGBA candidate reconstructions with EMPTY icon areas and no text.
Frame outlines have been rebuilt rather than perfectly copied; original source color is retained for the central X.
Visual reference matching is NOT exact, so these are in `review/`, **not** `final/`.
The originals, Codex assets and all other themes were untouched.
\n""",encoding="utf-8")
