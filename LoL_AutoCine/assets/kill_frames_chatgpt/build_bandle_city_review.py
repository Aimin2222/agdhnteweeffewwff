#!/usr/bin/env python3
"""ChatGPT-authored Bandle City transparent killframe graphics.
Use ONLY verified kill_concepts/image-gen-10(1).png as a visual/pixel reference.
Three central motifs x (subtle, ornate) = six separate 1800x400 RGBA sprites.
Not falsely designated pixel-identical originals: QA review candidates.
"""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

srcroot=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((out.parents[1]/"manifest.json").read_text(encoding="utf-8"))
rec=next(x for x in manifest["items"] if x["number"]=="015")
src=srcroot/rec["source"]
assert rec["source"]=="image-gen-10(1).png"
assert hashlib.sha256(src.read_bytes()).hexdigest()==rec["source_sha256"],"SOURCE SHA mismatch"
original=Image.open(src).convert("RGB")
assert original.size[0]>=960 and original.size[1]>=720

W,H=1800,400
GOLD=(226,186,95,255);LIGHT=(255,235,151,255);WARM=(123,79,54,255)
GREEN=(81,124,61,245);LILAC=(157,125,236,255);AZURE=(56,159,255,255)
def p(x,y):return (round(x),round(y))
def draw_line(d,pts,fill,width=2):
    d.line([p(*xy) for xy in pts],fill=fill,width=width,joint="curve")
def poly(d,ps,fill,outline=None,w=2):
    d.polygon([p(*v) for v in ps],fill=fill)
    if outline:draw_line(d,ps+[ps[0]],outline,w)
def bez(d,controls,fill,width=3):
    points=[]
    for t in range(41):
        u=t/40
        b=(1-u)**3; c=3*(1-u)**2*u;e=3*(1-u)*u*u;f=u**3
        points.append((b*controls[0][0]+c*controls[1][0]+e*controls[2][0]+f*controls[3][0],
          b*controls[0][1]+c*controls[1][1]+e*controls[2][1]+f*controls[3][1]))
    draw_line(d,points,fill,width)
def diamond(d,cx,cy,rx,ry,col,gold=True):
    coords=[(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)]
    poly(d,coords,col,LIGHT if gold else LILAC,2)
    draw_line(d,[(cx,cy-ry),(cx,cy+ry)],(246,242,183,215),2)
def sparkle(d,x,y,s=9,color=LIGHT):
    diamond(d,x,y,s*.25,s,color)
    diamond(d,x,y,s,s*.25,color)
def leaf(d,cx,cy,angle,scale=1,rose=False):
    a=math.radians(angle);ux,uy=math.cos(a),math.sin(a)
    vx,vy=-uy,ux
    L=63*scale;T=24*scale
    ps=[(cx,cy),(cx+ux*L*.60+vx*T,cy+uy*L*.60+vy*T),(cx+ux*L,cy+uy*L),
        (cx+ux*L*.56-vx*T,cy+uy*L*.56-vy*T)]
    poly(d,ps,(108,133,62,240) if not rose else (248,142,180,235),GOLD,2)
    draw_line(d,[(cx,cy),(cx+ux*L,cy+uy*L)],(253,226,149,220),2)

def cropped_motif(kind,ornate):
    # Crop whole center motif, not portrait, text or surrounding caption.
    weakboxes=[(211,177,305,270),(211,293,310,388),(208,409,309,507)]
    strongboxes=[(615,182,793,273),(617,297,790,392),(615,412,792,500)]
    v=(strongboxes if ornate else weakboxes)[kind]
    sx,sy=original.width/960,original.height/720
    box=(round(v[0]*sx),round(v[1]*sy),round(v[2]*sx),round(v[3]*sy))
    rgb=original.crop(box)
    raw=np.asarray(rgb,dtype=np.float32)
    # Beige parchment is pale and low chroma; subtract it with a soft mask,
    # preserving high-saturation cyan, indigo, pink, emerald and gold strokes.
    mx=raw.max(2);mn=raw.min(2)
    blue=raw[:,:,2]-raw[:,:,0]*.85
    saturated=(mx-mn)
    dim=255-mn
    # Parchement background is low-chroma pale tan. Avoid making this solid:
    # unlike naive brightness segmentation it should have alpha ~0.
    chroma=np.clip((saturated-53)/70,0,1)
    cool=np.clip((blue-23)/88,0,1)
    # Preserve the deep saturated ornament core without including shaded paper.
    green=np.clip((raw[:,:,1]-raw[:,:,0]*.68-29)/105,0,1)
    a=np.maximum.reduce([chroma,cool,green])
    a=np.where((mx>205)&(saturated<66)&(raw[:,:,0]>raw[:,:,2]*1.08),a*.12,a)
    a=np.clip((a-.075)*1.10,0,1)
    h,w=a.shape
    yy,xx=np.mgrid[0:h,0:w]
    rx=.49 if ornate else .47
    alpha_edge=np.clip((1.23-((xx-w/2)/(w*rx))**2-((yy-h/2)/(h*.49))**2)*2.0,0,1)
    a*=alpha_edge
    rgba=np.dstack((raw.astype(np.uint8),np.rint(a*255).astype(np.uint8)))
    return Image.fromarray(rgba,"RGBA")

def frame(d,x,y,accent,ornate):
    size=198 if ornate else 180
    left=x-size/2;right=x+size/2;top=y-size/2;bottom=y+size/2
    # Corner-cut square chrome framing like original Bandle City concept.
    def octagon(m):
        return [(left+m+20,top+m),(right-m-20,top+m),
               (right-m,top+m+20),(right-m,bottom-m-20),
               (right-m-20,bottom-m),(left+m+20,bottom-m),
               (left+m,bottom-m-20),(left+m,top+m+20)]
    for m,col,width in [(0,(71,44,38,251),12),(7,GOLD,7),(15,LIGHT,2),(20,(110,80,52,220),3)]:
        draw_line(d,octagon(m)+[octagon(m)[0]],col,width)
    for xx in (left+18,right-18):
        for yy in (top+18,bottom-18):
            sparkle(d,xx,yy,10,LIGHT)
    for dx,dy in ((-size/2-12,0),(size/2+12,0)):
        diamond(d,x+dx,y,11,18,accent)
    # This slot is deliberately empty and fully transparent.
    return left+24,top+24,right-24,bottom-24

def make(ornate,kind):
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    glow=Image.new("RGBA",im.size,(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    gd.ellipse((710,50,1090,350),fill=(77,101,227,105) if kind!=1 else (69,212,160,90))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(49)))
    d=ImageDraw.Draw(im)
    cy=200;cx=W//2
    # Fine filigree bridges from square slots to original center ornament.
    for mirror in (-1,1):
        x0=cx+mirror*143;x1=cx+mirror*633
        for off,w,color in ((0,5,(99,67,49,220)),(2,3,GOLD),(-3,1,LIGHT)):
            draw_line(d,[(x0,cy+off),(x1,cy+off)],color,w)
        for sign in (-1,1):
            bez(d,[(cx+mirror*130,cy+sign*12),(cx+mirror*258,cy+sign*(105 if ornate else 65)),
                (cx+mirror*392,cy+sign*(70 if ornate else 45)),(cx+mirror*606,cy+sign*36)],
                GOLD if ornate else (169,143,75,230),4)
            bez(d,[(cx+mirror*156,cy+sign*28),(cx+mirror*282,cy+sign*103),
                (cx+mirror*420,cy+sign*23),(cx+mirror*596,cy+sign*22)],
                (167,130,231,213) if kind==2 else (148,188,122,213),3)
            for i in range(3 if ornate else 2):
                lx=cx+mirror*(230+i*105); ly=cy+sign*(26+i%2*18)
                leaf(d,lx,ly,(-19 if mirror==1 else 199)+sign*27,.86 if ornate else .64,rose=(ornate and i==1))
        for x in (cx+mirror*321,cx+mirror*514):
            sparkle(d,x,cy,9+4*ornate)
    # Full square portrait frames (no pre-rendered character photos).
    holes=[]
    for x in (196,W-196):holes.append(frame(d,x,cy,AZURE if kind!=1 else LILAC,ornate))
    if ornate:
        # playful Bandle flowers, crystal beads and flowing ribbon curls
        for sign in (-1,1):
            for mirror in (-1,1):
                xx=cx+mirror*345
                yy=cy+sign*85
                for i in range(5):
                    rad=math.radians(72*i)
                    px=xx+19*math.cos(rad);py=yy+19*math.sin(rad)
                    d.ellipse((px-9,py-9,px+9,py+9),fill=(247,159,187,245),outline=GOLD,width=2)
                d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=(240,197,70,255))
        for mirror in (-1,1):
            bez(d,[(cx+mirror*130,cy-36),(cx+mirror*177,cy-160),
                (cx+mirror*380,cy-124),(cx+mirror*425,cy-90)],(187,135,235,230),6)
    center=cropped_motif(kind,ornate)
    tw=(430 if ornate else 260);th=(236 if ornate else 186)
    k=min(tw/center.width,th/center.height)
    center=center.resize((int(center.width*k),int(center.height*k)),Image.Resampling.LANCZOS)
    im.alpha_composite(center,((W-center.width)//2,(H-center.height)//2))
    d=ImageDraw.Draw(im)
    if kind==0:
        diamond(d,cx,cy,34 if ornate else 30,58 if ornate else 50,(29,114,174,230))
        diamond(d,cx,cy,22,38,(54,213,244,240))
    elif kind==1:
        for q in range(4):
            angle=math.radians(q*90)
            x=cx+math.cos(angle)*29;y=cy+math.sin(angle)*26
            d.ellipse((x-12,y-13,x+12,y+13),fill=(87,154,235,246),outline=LIGHT,width=3)
        d.ellipse((cx-25,cy-9,cx+25,cy+27),fill=(74,144,214,252),outline=LIGHT,width=4)
    else:
        diamond(d,cx,cy,38 if ornate else 31,52 if ornate else 45,(57,112,211,235))
        sparkle(d,cx,cy,26,LIGHT)
    d=ImageDraw.Draw(im)
    # Guarantee alpha=0 in exact square slot interiors.
    pixels=np.asarray(im).copy()
    for lx,ty,rx,by in holes:
        x1,y1,x2,y2=map(int,(lx,ty,rx,by))
        pixels[y1:y2,x1:x2]=0
    im=Image.fromarray(pixels,"RGBA")
    assert im.getpixel((0,0))[3]==0
    assert im.getpixel((196,cy))[3]==0
    assert im.getpixel((W-196,cy))[3]==0
    return im

variants=("spiral_crystal","paw_crest","star_portal")
inventory=[]
for ornate in (False,True):
    for kind,variant in enumerate(variants):
        name=f"bandle_{'strong' if ornate else 'weak'}_{variant}_review_rgba.png"
        im=make(ornate,kind)
        im.save(out/name,format="PNG",compress_level=6)
        qa=Image.new("RGB",(W,2*H))
        for i,bg in enumerate(((20,25,40),(245,243,238))):
            sheet=Image.new("RGBA",(W,H),(*bg,255));sheet.alpha_composite(im)
            qa.paste(sheet.convert("RGB"),(0,i*H))
        qa.thumbnail((1280,720),Image.Resampling.LANCZOS)
        qa.save(out/(name.replace("_review_rgba.png","_qa.jpg")),format="JPEG",quality=91)
        inv={"variant":variant,"strength":"strong" if ornate else "weak",
             "png":name,"resolution":list(im.size),"alpha_mode":im.mode,
             "alpha_on_corners":im.getpixel((0,0))[3],
             "icon_slot_alpha":im.getpixel((196,200))[3],
             "status":"review_only_not_pixel_identical"}
        inventory.append(inv)
(out/"inventory.json").write_text(json.dumps({"source_no":"015","source_file":rec["source"],
    "source_sha256":rec["source_sha256"],"note":"Reference-guided reconstruction: source motifs mixed with newly drawn geometries; NOT exact original.","assets":inventory},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(out/"README.md").write_text("""# No.015 Bandle City killframes — transparent review sprites

Source **only**: `LoL_AutoCine/assets/kill_concepts/image-gen-10(1).png`. Source SHA-256 verified.
6 high-resolution 1800 × 400 RGBA PNG: three original central motif themes
(spiral/crystal, paw, star/portal), each in weak and strong ornamentation.
Square character icon slots are transparent and have no baked-in character portraits.
A dark/light QA comparison JPEG accompanies each PNG.
Re-created frames and bridges approximate the source look rather than guarantee
pixel-identical reproduction; the results belong to the separate `review/`
folder, never to `final/` without an independent acceptance check.
No change to source images or Codex assets.
""",encoding="utf-8")
print(json.dumps({"rendered":len(inventory),"images":inventory}))
