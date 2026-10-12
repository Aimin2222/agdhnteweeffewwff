# -*- coding: utf-8 -*-
"""Generate actual frame contact sheets and conservative quality measurements.

Not an AI champion detector: empty combat scenes cannot be declared valid
without gameplay video understanding and actual screen-space person tracking.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageStat

from .gpu_binary import ffmpeg_exe
from .montage_fx import get_duration


def frame_at(path: Path, seconds: float, *, width=320, height=180):
    cmd = [str(ffmpeg_exe()), "-nostdin", "-hide_banner", "-loglevel", "error",
           "-ss", str(max(0.0, float(seconds))), "-i", str(path), "-frames:v", "1",
           "-vf", f"scale={width}:{height}", "-f", "image2pipe", "-vcodec", "png", "-"]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=35)
    if not result.stdout:
        raise RuntimeError("No video frame returned")
    return Image.open(BytesIO(result.stdout)).convert("RGB")


def _sheet(entries, destination, *, columns=4):
    entries = list(entries)
    if not entries:
        return None
    width, height, band = 320, 180, 26
    rows = (len(entries) + columns - 1) // columns
    sheet = Image.new("RGB", (width * columns, (height+band) * rows), "#E9EFF6")
    draw = ImageDraw.Draw(sheet)
    for idx, (name, image) in enumerate(entries):
        x = (idx % columns) * width
        y = (idx // columns) * (height+band)
        sheet.paste(image, (x,y+band))
        draw.text((x+8,y+5), str(name)[:36], fill="#17263C")
    sheet.save(destination, format="JPEG", quality=88)
    return str(destination)


def _delta(a, b):
    data_a, data_b = a.tobytes(), b.tobytes()
    return round(sum(abs(x-y) for x,y in zip(data_a,data_b)) / max(1,len(data_a)), 2)


def make_qa_contact_sheets(folder, camera_entries, transition_entries, *,
                           log=lambda _m: None, transition_inputs=None):
    """Review 3 real points per camera and 3 frames around each transition.

    Historical single-frame comparisons are kept for compatibility. A single
    screenshot at the flash peak made all ten transitions appear solid white,
    so sample before/during/after and compare temporal deltas as well.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    result = {"camera": [], "transitions": [], "images": [],
              "limitations": "Frame/pixel tests do not establish that a champion or kill is visible."}
    camera_tiles = []
    side_tiles = {"RED": [], "BLUE": []}
    for case in camera_entries:
        files = case.get("outputs") or []
        if not files:
            continue
        try:
            path = Path(files[0])
            duration = get_duration(path, ffmpeg=str(ffmpeg_exe()))
            times = (min(.8, duration*.2),duration*.5,min(duration*.82,duration-.04))
            frames = [frame_at(path, seconds) for seconds in times]
            img = frames[1]
            gray = ImageStat.Stat(img.convert("L"))
            contrast = round(gray.stddev[0], 2)
            luminance = round(gray.mean[0], 2)
            side = case.get("side", "?")
            mode = case.get("mode","?")
            result["camera"].append({
                "number":case.get("number"),"side":side,"mode":mode,
                "mean_brightness":luminance,"texture_contrast":contrast,
                "suspected_black_or_flat":luminance<9 or contrast<6,
                "sample_seconds": [round(t,2) for t in times],
                "frame_motion": [_delta(frames[j],frames[j+1]) for j in (0,1)]})
            camera_tiles.append((f'{case.get("number")} {side} {mode}',img))
            if side in side_tiles:
                for when, fr in zip(("PRE","KILL","POST"),frames):
                    side_tiles[side].append((f'{case.get("number")} {mode} {when}',fr))
        except Exception as exc:
            log(f"カメラ比較画像取得失敗: {exc}")
    try:
        path = _sheet(camera_tiles,folder/"camera_comparison.jpg")
        if path: result["images"].append(path)
        for side, items in side_tiles.items():
            if items:
                path=_sheet(items,folder/f"{side}_camera_3frames.jpg",columns=3)
                if path: result["images"].append(path)
    except Exception as exc:
        log("カメラ3時点比較表作成失敗: "+str(exc))

    inputs = transition_inputs or [Path(p) for case in camera_entries
                                    for p in case.get("outputs",[])]
    try:
        boundary = get_duration(Path(inputs[0]),ffmpeg=str(ffmpeg_exe())) if inputs else 2.0
    except Exception:
        boundary = 2.0
    center_tiles, strip_tiles, triplets = [], [], {}
    for case in transition_entries:
        files = case.get("outputs") or []
        if not files:
            continue
        name = case.get("style", "?")
        try:
            path=Path(files[0])
            # Spatial xfade previews are intentionally shorter than the full
            # montage. Their own midpoint is the true join; old previews use
            # the first source clip's duration instead.
            join = (get_duration(path,ffmpeg=str(ffmpeg_exe()))/2.0
                    if name.startswith("spatial_") else boundary)
            frames=[frame_at(path, max(.05,join+dt))
                    for dt in (-.16,0,.16)]
            triplets[name]=frames
            center_tiles.append((name,frames[1]))
            for phase,img in zip(("BEFORE","CUT","AFTER"),frames):
                strip_tiles.append((f"{name} {phase}",img))
        except Exception as exc:
            log(f"つなぎ演出比較のフレーム取得失敗 ({name}): {exc}")
    try:
        path=_sheet(center_tiles,folder/"transition_comparison.jpg",columns=5)
        if path:result["images"].append(path)
        path=_sheet(strip_tiles,folder/"transition_3frames.jpg",columns=3)
        if path:result["images"].append(path)
    except Exception as exc:
        log("つなぎ3時点比較表作成失敗: "+str(exc))
    reference=triplets.get("cut")
    if reference:
        for style,frames in triplets.items():
            control=(triplets.get("spatial_fade") if style.startswith("spatial_") else reference) or reference
            differences=[_delta(frames[i],control[i]) for i in range(3)]
            result["transitions"].append({
                "style":style,
                "comparison_reference":("spatial_fade" if style.startswith("spatial_") else "cut"),
                "frame_differences_from_cut":differences,
                "mean_absolute_difference_from_cut":differences[1],
                "similar_at_join":style!="cut" and max(differences)<5.0,
                "peak_white_frame":max(ImageStat.Stat(img.convert("L")).mean[0] for img in frames)>247.0})
    return result
