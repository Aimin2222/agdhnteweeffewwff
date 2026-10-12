# -*- coding: utf-8 -*-
"""Local xMedia video contact sheet and objective edit-rhythm summary.

Camera angle reconstruction from a rendered MP4 alone is not possible without
3D scene geometry; this module does NOT claim to reverse-engineer Replay API
camera parameters. It creates source-derived evidence to review instead.
"""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat

from .qa_visual import frame_at
from .montage_fx import get_duration


def extract_reference_contact(paths, folder, *, max_videos=32, log=lambda _m:None):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    tiles=[]
    width,height,label_height=320,180,30
    for index, raw in enumerate(list(paths)[:max_videos]):
        path=Path(raw)
        row={"source":str(path),"name":path.name,"frames":[],"errors":[]}
        try:
            length=get_duration(path)
            times=[min(max(.1,length*position),max(.1,length-.1))
                   for position in (.15,.50,.85)]
            pictures=[]
            for t in times:
                im=frame_at(path,t)
                pictures.append(im)
                row["frames"].append(round(float(t),3))
            deltas=[ImageStat.Stat(ImageChops.difference(a,b).convert("L")).mean[0]
                    for a,b in zip(pictures,pictures[1:])]
            row["mean_visual_difference"]=round(sum(deltas)/max(1,len(deltas)),2)
            row["note"]="視覚的な変化量。カメラだけでなくキャラ移動・エフェクト・カットも含みます。"
            for ix,im in enumerate(pictures):
                tiles.append((f"{index+1:02d} {path.stem[:22]} {ix+1}/3",im))
        except Exception as exc:
            row["errors"].append(f"{type(exc).__name__}: {exc}")
            log(f"参考動画 {path.name} のプレビュー作成失敗: {exc}")
        rows.append(row)
    if tiles:
        canvas=Image.new("RGB",(width*3,(height+label_height)*(len(tiles)+2)//3+height+label_height),"#EDF3F8")
        drawer=ImageDraw.Draw(canvas)
        for ix,(name,im) in enumerate(tiles):
            x=ix%3*width
            y=ix//3*(height+label_height)
            canvas.paste(im,(x,y+label_height))
            drawer.text((x+6,y+7),name[:35],fill="#102945")
        used_rows=(len(tiles)+2)//3
        dest=folder/"xmedia_reference_contact.jpg"
        canvas.crop((0,0,width*3,used_rows*(height+label_height))).save(dest,quality=87)
    report=folder/"xmedia_reference_analysis.json"
    report.write_text(json.dumps({"status":"source_media_sampled",
                                  "limitations":"Camera 3D path, target coordinates and clip edit timing cannot be recovered reliably from sampled images alone.",
                                  "videos":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    return report
