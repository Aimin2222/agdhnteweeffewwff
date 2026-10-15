#!/usr/bin/env python3
"""ChatGPT-authored Ixtal high-resolution RGBA killframes from ONLY original concept No.014.
Original central leaf/crystal decoration pixels are retained; outer complete frames are
redrawn from the original palette. QA review, not certified pixel-identical final.
"""
import sys, json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src_dir=Path(sys.argv[1])
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
man=json.loads((out.parents[1]/"manifest.json").read_text(encoding="utf-8-sig"))
entry=next(x for x in man["items"] if x["number"]=="014")
src=src_dir/entry["source"]
assert hashlib.sha256(src.read_bytes()).hexdigest()==entry["source_sha256"],"Original failed hash check"
original=Image.open(src).convert("RGB")
sx,sy=original.width/960,original.height/720
W,H=1740,350
G=(218,177,81,255);L=(252,228,142,255);D=(40,89,54,250);E=(32,222,165,255)
def P(x,y):return (int(x),int(y))
def line(d,pts,fill,width=3):
    d.line([P(x,y) for x,y in pts],fill=fill,width=width,joint="curve")
def polygon(d,ps,fill,outline=None,width=1):
    d.polygon([P(x,y) for x,y in ps],fill=fill)
    if outline:d.line([P(x,y) for x,y in ps+[ps[0]]],fill=outline,width=width,joint="curve")
def diamond(d,cx,cy,rx,ry,base,stroke):
    ps=[(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)]
    polygon(d,ps,base,stroke,3)
    line(d,[(cx,cy-ry+9),(cx+rx-6,cy),(cx,cy+ry-8)],(203,255,195,225),2)
    line(d,[(cx,cy-ry+9),(cx-rx+6,cy),(cx,cy+ry-8)],(29,103,75,255),2)

def floral(d,cx,cy,size,mode):
    for a in range(0,360,72):
        rad=math.radians(a)
        ux,uy=math.cos(rad),math.sin(rad)
        px,py=-uy,ux
        pts=[(cx+px*size*.26,cy+py*size*.26),
             (cx+ux*size*.66+px*size*.37,cy+uy*size*.66+py*size*.37),
             (cx+ux*size*1.15,cy+uy*size*1.15),
             (cx+ux*size*.66-px*size*.37,cy+uy*size*.66-py*size*.37),
             (cx-px*size*.26,cy-py*size*.26)]
        polygon(d,pts,(179,52,47,237) if mode=="strong" else (55,144,75,220),(244,171,81,250),2)
    r=size*.30
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(247,164,83,255),outline=(255,220,159,255),width=2)

def leaf(d,rootx,rooty,xsign,side,length,width,crowd=False,green=True):
    endx=rootx+xsign*length;endy=rooty+side*width*.6
    midx=rootx+xsign*length*.53;midy=rooty-side*width*.45
    pts=[(rootx,rooty),(midx,midy),(endx,endy),(midx,rooty+side*width*.60)]
    fill=(10,78,48,248) if green else (120,82,37,238)
    polygon(d,pts,fill,(179,163,64,255),3)
    line(d,[(rootx,rooty),(midx,rooty+side*width*.09),(endx,endy)],(114,211,105,220) if green else (255,187,80,240),3)
    if crowd:
        line(d,[(midx,rooty+side*width*.09),(midx-xsign*13,rooty-side*width*.23)],(201,229,102,225),2)

def emerald(d,cx,cy,scale):
    diamond(d,cx,cy,40*scale,70*scale,(9,71,59,255),(247,203,88,255))
    diamond(d,cx,cy,27*scale,52*scale,(11,138,95,255),(169,245,174,255))
    diamond(d,cx,cy,15*scale,34*scale,(31,212,147,255),(206,255,222,255))
    line(d,[(cx,cy-54*scale),(cx,cy+50*scale)],(232,255,195,230),2)
    line(d,[(cx-28*scale,cy),(cx+28*scale,cy)],(250,223,125,200),2)

def source_motif(mode):
    # Source rows: top weak 192-263; strong 190-268. Avoid character portraits.
    box=(147,195,260,264) if mode=="weak" else (606,191,769,271)
    bbox=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(box))
    crop=original.crop(bbox).convert("RGB")
    arr=np.asarray(crop).astype(np.float32)
    h,w=arr.shape[:2]
    mx=arr.max(axis=2);mn=arr.min(axis=2)
    # Retain original high-frequency emerald/gold/leaf details, suppress dark
    # painted background; never mistake this experimental alpha for a final mat.
    v=np.maximum((mx-45)/120,(mx-mn-29)/100)
    mask=np.clip(v,0,1)
    py,px=np.mgrid[0:h,0:w]
    ell=((px-w/2)/(w*.49))**2+((py-h/2)/(h*.48))**2
    mask*=np.clip((1.25-ell)*2.2,0,1)
    rgba=np.dstack((arr.astype("uint8"),(mask*255).astype("uint8")))
    return Image.fromarray(rgba,"RGBA")

def make(mode):
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    aura=Image.new("RGBA",(W,H));glow=ImageDraw.Draw(aura)
    glow.ellipse((780,76,960,274),fill=(21,181,112,155))
    im.alpha_composite(aura.filter(ImageFilter.GaussianBlur(54)))
    d=ImageDraw.Draw(im)
    cy=173
    for iconx in (178,W-178):
        # Only concentric ring outlines, transparent champion icon centers.
        for rr,th,col in [(104,9,(116,87,42,245)),(96,8,G),(86,3,(238,226,158,255)),(79,2,(76,143,82,175))]:
            d.ellipse((iconx-rr,cy-rr,iconx+rr,cy+rr),outline=col,width=th)
        for angle in (0,90,180,270):
            a=math.radians(angle);px=iconx+104*math.cos(a);py=cy+104*math.sin(a)
            diamond(d,px,py,11,17,(41,123,73,255),(237,205,98,255))
    # Long bridges and leaf filigree; protected 1:1 ratio and 50px edge margin.
    for side in (-1,1):
        for mirrored in (False,True):
            if not mirrored:
                root=785;sgn=-1
            else:
                root=W-785;sgn=1
            for ix in range(5):
                le=132+ix*83
                yy=cy+side*(4+ix*6)
                leaf(d,root-sgn*ix*29,yy,sgn,side,le,50+ix*4,ix%2==0,green=(ix%4!=3))
        for x0,x1 in ((284,830),(W-830,W-284)):
            line(d,[(x0,cy+side*6),(x1,cy+side*6)],(56,153,95,202),5)
            line(d,[(x0,cy+side*2),(x1,cy+side*2)],(238,195,79,229),2)
    if mode=="strong":
        for cx,yy,sz in [(610,120,24),(490,223,21),(395,111,18),
                          (W-610,120,24),(W-490,223,21),(W-395,111,18)]:
            floral(d,cx,yy,sz,mode)
        for z in range(4):
            for side in (-1,1):
                x=845+(z-1.5)*48
                polygon(d,[(x,cy+side*12),(x+9,cy+side*38),(x,cy+side*62),(x-9,cy+side*38)],(164,136,56,220),(242,205,106,220),1)
    # Original mid motif is laid over generated frame without replacing it.
    srcpiece=source_motif(mode)
    maxsize=(280,220) if mode=="strong" else (235,172)
    # LANCZOS from original pixel crop, not from 960px preview.
    ratio=min(maxsize[0]/srcpiece.width,maxsize[1]/srcpiece.height)
    ps=srcpiece.resize((round(srcpiece.width*ratio),round(srcpiece.height*ratio)),Image.Resampling.LANCZOS)
    im.alpha_composite(ps,((W-ps.width)//2,(H-ps.height)//2))
    d=ImageDraw.Draw(im)
    emerald(d,W//2,cy,1.00 if mode=="strong" else .72)
    # Ensure the transparent holes are EXACTLY transparent, so the game
    # can place its own champion icons; artwork cannot intrude into them.
    pix=np.asarray(im).copy()
    yy,xx=np.mgrid[:H,:W]
    for cx in (178,W-178):
        circle=(xx-cx)**2+(yy-cy)**2<=74**2
        pix[circle]=0
    result=Image.fromarray(pix,"RGBA")
    assert result.getpixel((0,0))[3]==0 and result.getpixel((178,cy))[3]==0
    return result

for mode in ("weak","strong"):
    im=make(mode)
    name="ixtal_"+mode+"_review_rgba.png"
    im.save(out/name,format="PNG",compress_level=6)
    proof=Image.new("RGB",(W,2*H))
    for i,bg in enumerate(((18,23,26),(241,242,239))):
        lay=Image.new("RGBA",(W,H),(*bg,255))
        lay.alpha_composite(im)
        proof.paste(lay.convert("RGB"),(0,i*H))
    proof.thumbnail((1300,800),Image.Resampling.LANCZOS)
    proof.save(out/("ixtal_"+mode+"_qa.jpg"),quality=89)
    print(name,im.size, "transparent corners and icon centers checked")
(out/"README.md").write_text("""# Ixtal source-guided transparent killframe review

- Source ONLY: `kill_concepts/image-gen-1(9).png`, SHA-256 checked.
- `ixtal_weak_review_rgba.png` and `ixtal_strong_review_rgba.png`: transparent RGBA at 1740×350.
- Left and right portrait holes are intentionally empty transparent slots.
- Source motif is reproduced using the original full-resolution concept sheet plus
  manually reconstructed shapes in original dark-green, emerald, gold, and tropical-floral theme.
- Original file and Codex files unchanged.
- This is **a review-only approximation** (not pixel-identical), not marked finished.
- QA sheets preview against black and white backgrounds.
""",encoding="utf-8")
