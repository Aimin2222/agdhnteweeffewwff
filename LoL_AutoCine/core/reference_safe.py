# -*- coding: utf-8 -*-
"""参考動画から安全にテンプレートを作る軽量解析。
v4.1基準版のカメラ設定・録画・書き出しには触れず、色/テンポ/切替/枠/質感だけを学習する。
複数動画は「1本失敗しても全体を落とさない」方式。
"""
from __future__ import annotations
import json, subprocess, dataclasses
from pathlib import Path
import numpy as np
from .effects import FFMPEG, Template

W,H,FPS=240,135,6

def _decode(path: Path, max_seconds=90.0):
    cmd=[FFMPEG,"-v","error","-i",str(path),"-t",str(max_seconds),
         "-vf",f"fps={FPS},scale={W}:{H}:flags=fast_bilinear",
         "-f","rawvideo","-pix_fmt","rgb24","-"]
    r=subprocess.run(cmd,capture_output=True)
    size=W*H*3
    n=len(r.stdout)//size
    if r.returncode and n<3:
        raise RuntimeError("動画を読み込めません: "+r.stderr.decode("utf-8","replace")[-400:])
    if n<3:
        raise RuntimeError("3フレーム未満のため参考動画として使えません")
    return np.frombuffer(r.stdout[:n*size],dtype=np.uint8).reshape(n,H,W,3).copy()

def _metrics(fr):
    x=fr.astype(np.float32)/255.0
    y=.299*x[...,0]+.587*x[...,1]+.114*x[...,2]
    mean=y.mean(axis=(1,2))
    diff=np.abs(y[1:]-y[:-1]).mean(axis=(1,2))
    dark=(y.mean(axis=2)<.035).mean(axis=0)
    top=0
    while top<H//3 and dark[top]>.82: top+=1
    bot=0
    while bot<H//3 and dark[H-1-bot]>.82: bot+=1
    body=y[:,top:max(top+1,H-bot),:]
    px=x[:,top:max(top+1,H-bot),:,:].reshape(-1,3)[::8]
    lum=.299*px[:,0]+.587*px[:,1]+.114*px[:,2]
    mx,mn=px.max(1),px.min(1)
    sat=float(np.mean((mx-mn)/np.maximum(mx,.001)))
    contrast=float(np.clip(lum.std()/.22,.7,1.6))
    brightness=float(np.clip((lum.mean()-.40)*.3,-.12,.12))
    color={}
    for band,mask in (("s",lum<.25),("m",(lum>=.25)&(lum<.65)),("h",lum>=.65)):
        q=px[mask]
        dev=q.mean(0)-q.mean() if len(q)>=20 else np.zeros(3)
        for c,v in zip("rgb",dev): color[c+band]=float(np.clip(v*1.15,-.3,.3))
    flashes=int(np.sum((mean[1:-1]>.84)&(mean[:-2]<.72)&(mean[2:]<.72)))
    med=float(np.median(diff)) if len(diff) else 0.0
    cuts=int(np.sum(diff>max(.12,med*5.0)))
    motion=float(np.clip(diff.mean()/max(.001,med),.5,2.5)) if med else 1.0
    center=body[:,body.shape[1]//3:2*body.shape[1]//3,W//3:2*W//3].mean()
    corner=np.mean([body[:,:max(1,body.shape[1]//3),:max(1,W//3)].mean(),
                    body[:,:max(1,body.shape[1]//3),-max(1,W//3):].mean(),
                    body[:,-max(1,body.shape[1]//3):,:max(1,W//3)].mean(),
                    body[:,-max(1,body.shape[1]//3):,-max(1,W//3):].mean()])
    vignette=float(np.clip((.96-corner/max(.001,center))/.45,0,1))
    grain=float(np.clip((diff.std()-.004)/.025,0,1))
    duration=len(fr)/FPS
    cut_density=cuts/max(.1,duration)
    tempo=float(np.clip(1+cut_density*.08+motion*.06,.75,1.4))
    transition="flash" if flashes>=max(1,cuts//3) else ("fade" if cuts==0 else "cut")
    return dict(duration=duration,bars_frac=(top+bot)/(2*H),flashes=flashes,cuts=cuts,
                cut_density=cut_density,tempo=tempo,motion=motion,
                saturation=float(np.clip(sat/.40,.6,1.8)),contrast=contrast,brightness=brightness,
                color=color,vignette=vignette,grain=grain,transition=transition)

def analyze_video(path, max_seconds=90.0):
    p=Path(path)
    if not p.exists(): raise RuntimeError("ファイルが存在しません")
    if p.stat().st_size<1024: raise RuntimeError("ファイルサイズが小さすぎます")
    m=_metrics(_decode(p,max_seconds))
    m["file"]=str(p)
    return m

def template_from_references(paths, name, camera_template=None):
    ok=[]; errors=[]
    for p in paths:
        try: ok.append(analyze_video(p))
        except Exception as e: errors.append((str(p),str(e)))
    if not ok: raise RuntimeError("参考動画を1本も解析できませんでした")
    t=Template(name=name)
    if camera_template is not None:
        for k in ("style","intensity","dist_scale","cam_height","third_elev","third_dist"):
            if hasattr(camera_template,k): setattr(t,k,getattr(camera_template,k))
        t.pre=float(camera_template.pre); t.post=float(camera_template.post)
        t.merge_multikill=bool(camera_template.merge_multikill)
        t.hide_hud=bool(camera_template.hide_hud); t.keep_champion_bars=bool(camera_template.keep_champion_bars)
        t.game_audio=bool(camera_template.game_audio)
        t.game_volume=float(camera_template.game_volume); t.bgm_volume=float(camera_template.bgm_volume)
    t.grade="standard"; t.grade_strength=0.0
    t.contrast=float(np.clip(np.mean([r["contrast"] for r in ok]),.6,1.6))
    t.vignette=float(np.clip(np.mean([r["vignette"] for r in ok]),0,1))
    t.grain=float(np.clip(np.mean([r["grain"] for r in ok]),0,1))
    t.bars=float(np.clip(np.mean([r["bars_frac"] for r in ok])/.12,0,1))
    flashes=sum(r["flashes"]>0 for r in ok)
    t.transition="flash" if flashes*2>=len(ok) else ("fade" if sum(r["transition"]=="fade" for r in ok)*2>=len(ok) else "cut")
    t.bpm=0.0
    tempo=float(np.mean([r["tempo"] for r in ok]))
    t.vibrance=float(np.clip((np.mean([r["saturation"] for r in ok])-1)*.7,-1,1.5))
    t.exposure=float(np.clip(np.mean([r["brightness"] for r in ok]),-.3,.3))
    colors={k:float(np.mean([r["color"].get(k,0) for r in ok])) for k in ok[0]["color"]}
    t.temperature=float(np.clip(colors.get("rh",0)-colors.get("bh",0),-.4,.4))
    t.reference_dna={"version":2,"source_count":len(ok),"tempo":round(tempo,4),
        "cut_density":round(float(np.mean([r["cut_density"] for r in ok])),4),
        "motion":round(float(np.mean([r["motion"] for r in ok])),4),
        "flash_ratio":round(flashes/len(ok),3),"transition":t.transition,
        "failed_sources":errors}
    t.reference_sources=[r["file"] for r in ok]
    t.template_origin="reference"
    return t,errors

def save_template(t: Template, path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(t.to_dict(),ensure_ascii=False,indent=2),encoding="utf-8")

def load_template(path: Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    valid=set(Template.__dataclass_fields__)
    return Template(**{k:v for k,v in d.items() if k in valid})

def make_remixes(t: Template):
    out=[]
    for name,gm,bars,grain in (
        ("REF-HERO",1.25,min(1,t.bars+.04),min(1,t.grain+.08)),
        ("REF-CLEAN",.75,max(0,t.bars-.03),max(0,t.grain-.12)),
        ("REF-HYPE",1.45,min(1,t.bars+.06),min(1,t.grain+.12))):
        x=dataclasses.replace(t,name=name)
        x.grade_strength=float(np.clip(t.grade_strength*gm,0,1.4))
        x.bars=bars; x.grain=grain
        x.reference_dna=dict(t.reference_dna,remix=name)
        out.append(x)
    return out
