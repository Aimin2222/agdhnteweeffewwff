#!/usr/bin/env python3
"""ChatGPT-authored, reference-preserving experimental transparent sprite extraction.

The source concept sheets are never edited. This produces candidate sprites only;
transparent alpha and visual fidelity MUST be inspected before promoting to final.
Coordinates refer to the 960x720 reference previews and are scaled up to the
unmodified original dimensions (normally 1448x1086). No RGB repaint/upscale.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "LoL_AutoCine/assets/kill_frames_chatgpt/manifest.json"
OUT = ROOT / "LoL_AutoCine/assets/kill_frames_chatgpt/batch_011_020/candidates"
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "LoL_AutoCine/assets/kill_concepts"

# (center_x, center_y, width, height) in 960x720 preview coordinates.
# Regions are isolated visual motifs, never the portrait pixels or heading/text.
REGIONS = {
 "011": [("weak",253,232,104,82),("strong",682,232,130,100),("melee",128,616,110,96),("ranged",480,614,108,101),("hybrid",747,610,120,104)],
 "012": [("weak",255,288,155,102),("strong",705,288,190,110),("melee",142,638,132,122),("ranged",476,631,130,125),("hybrid",718,627,145,125)],
 "013": [("weak",173,250,115,99),("strong",675,250,135,105),("melee",169,551,165,111),("ranged",485,547,155,110),("hybrid",813,545,145,110)],
 "014": [("weak",200,220,122,95),("strong",685,220,130,106),("melee",92,610,114,100),("ranged",460,610,122,100),("hybrid",793,610,120,100)],
 "015": [("weak",252,220,130,106),("strong",693,217,165,122),("melee",163,622,135,119),("ranged",465,617,149,125),("hybrid",708,617,149,125)],
 "016": [("weak",238,210,138,110),("strong",685,209,165,125),("melee",258,610,145,115),("ranged",489,610,150,115),("hybrid",713,610,160,116)],
 "017": [("weak",236,267,140,110),("strong",702,267,161,131),("melee",230,609,135,99),("ranged",574,609,135,100),("hybrid",858,609,130,100)],
 "018": [("weak",172,220,147,125),("strong",676,222,176,130),("melee",100,612,140,130),("ranged",479,612,150,122),("hybrid",754,612,146,128)],
 "019": [("weak",185,220,135,120),("strong",660,220,170,145),("melee",100,609,145,122),("ranged",466,609,149,122),("hybrid",758,609,146,123)],
 "020": [("hero",348,165,140,97),("variant_default",101,415,174,80),("variant_lunar",286,415,170,80),("variant_solar",478,415,165,80),("variant_flora",674,415,176,80),("variant_prestige",861,415,172,80)],
}

def crop_center(img, cx, cy, rw, rh):
    sx, sy = img.width / 960.0, img.height / 720.0
    x0 = max(0, round((cx-rw/2)*sx))
    y0 = max(0, round((cy-rh/2)*sy))
    x1 = min(img.width, round((cx+rw/2)*sx))
    y1 = min(img.height, round((cy+rh/2)*sy))
    return img.crop((x0,y0,x1,y1)), (x0,y0,x1,y1)

def clean_alpha(src):
    """Foreground segmentation from full-resolution original pixels."""
    rgb = np.asarray(src.convert("RGB")).copy()
    h,w,_ = rgb.shape
    # GrabCut: edge 9% background, middle 45% probable foreground.
    ix,iy = max(2,int(w*.10)), max(2,int(h*.10))
    mask = np.full((h,w),cv2.GC_PR_BGD,np.uint8)
    mask[:iy,:] = cv2.GC_BGD
    mask[-iy:,:] = cv2.GC_BGD
    mask[:,:ix] = cv2.GC_BGD
    mask[:,-ix:] = cv2.GC_BGD
    cv2.ellipse(mask,(w//2,h//2),(max(4,int(w*.28)),max(4,int(h*.28))),0,0,360,cv2.GC_PR_FGD,-1)
    cv2.ellipse(mask,(w//2,h//2),(max(2,int(w*.10)),max(2,int(h*.10))),0,0,360,cv2.GC_FGD,-1)
    bg = np.zeros((1,65),np.float64)
    fg = np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,bg,fg,6,cv2.GC_INIT_WITH_MASK)
    bw = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    # Keep connected components that touch the center region; preserve small glow.
    n,labels,stats,centers=cv2.connectedComponentsWithStats(bw,8)
    keep=np.zeros(n,bool)
    for i in range(1,n):
        cx,cy=centers[i]
        if (abs(cx-w/2)<w*.32 and abs(cy-h/2)<h*.32 and stats[i,cv2.CC_STAT_AREA]>8):
            keep[i]=True
    if len(keep)>0: keep[0]=False
    alpha=(keep[labels]*255).astype(np.uint8)
    # Edge antialias only, preserving exact original RGB data for opaque pixels.
    alpha=cv2.GaussianBlur(alpha,(3,3),0.65)
    rgba=np.dstack([rgb,alpha])
    return Image.fromarray(rgba,"RGBA"), {
        "nonzero_alpha_pixels":int(np.count_nonzero(alpha)),
        "opaque_alpha_pixels":int(np.count_nonzero(alpha==255)),
        "alpha_fraction":round(float(np.count_nonzero(alpha))/(w*h),4)
    }

def checkerboard(img, darkness):
    w,h=img.size
    if darkness:
        a,b=(20,24,35),(45,51,64)
    else:
        a,b=(239,242,244),(206,214,220)
    result=Image.new("RGBA",(w,h),(*a,255))
    tile=max(9,round(min(w,h)/14))
    d=ImageDraw.Draw(result)
    for y in range(0,h,tile):
        for x in range(0,w,tile):
            if (x//tile+y//tile)%2:
                d.rectangle((x,y,x+tile-1,y+tile-1),fill=(*b,255))
    result.alpha_composite(img)
    return result.convert("RGB")

def sheet(rows):
    """Numbered proof sheet for side-by-side source/transparent QA, not final asset."""
    cellw=450
    perh=230
    proof=Image.new("RGB",(cellw*3,perh*len(rows)),(27,30,38))
    d=ImageDraw.Draw(proof)
    for i,(name, original, sprite) in enumerate(rows):
        for j,obj in enumerate([original.convert("RGB"),checkerboard(sprite,False),checkerboard(sprite,True)]):
            factor=min(1,(cellw-26)/obj.width,(perh-34)/obj.height)
            wh=(round(obj.width*factor),round(obj.height*factor))
            im=obj.resize(wh,Image.Resampling.LANCZOS) if factor<1 else obj
            proof.paste(im,(j*cellw+round((cellw-wh[0])/2),i*perh+28))
        d.text((8,i*perh+7),str(name)+" | source   /   light BG   /   dark BG",fill=(255,255,255))
    return proof

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    by_id={x["number"]:x for x in manifest["items"]}
    OUT.mkdir(parents=True,exist_ok=True)
    metadata=[]
    for number,regions in REGIONS.items():
        source=SOURCE / by_id[number]["source"]
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        assert sha==by_id[number]["source_sha256"], f"SHA256 mismatch: {number}"
        with Image.open(source) as im:
            image=im.convert("RGB")
        proofs=[]
        result_dir=OUT / number
        result_dir.mkdir(parents=True,exist_ok=True)
        for name,cx,cy,rw,rh in regions:
            cropped,bbox=crop_center(image,cx,cy,rw,rh)
            try:
                rgba,qa=clean_alpha(cropped)
                status="candidate_needs_visual_qa"
            except Exception as e:
                # Never conceal failed segmentation behind a purported usable image.
                rgba=Image.new("RGBA",cropped.size)
                qa={"error":str(e)[:250],"nonzero_alpha_pixels":0,"opaque_alpha_pixels":0,"alpha_fraction":0}
                status="segmentation_failed"
            dest=result_dir/(name+".png")
            rgba.save(dest,format="PNG",compress_level=6)
            proofs.append((name,cropped,rgba))
            metadata.append({"number":number,"original":by_id[number]["source"],"original_sha256":sha,"piece":name,"source_bbox":list(bbox),"dimensions":list(rgba.size),"file":dest.relative_to(ROOT).as_posix(),"status":status,"qa":qa})
        sheet(proofs).save(result_dir/"proof.jpg",format="JPEG",quality=88)
    outfile=OUT/"candidate_inventory.json"
    outfile.write_text(json.dumps({"source":"original full resolution PNGs; not scaled","status":"experimental candidates, NOT approved for AutoCine integration","records":metadata},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"originals":len(REGIONS),"candidate_pieces":len(metadata),"segmentation_failures":len([x for x in metadata if x["status"]!="candidate_needs_visual_qa"])}))

if __name__=="__main__":
    main()
