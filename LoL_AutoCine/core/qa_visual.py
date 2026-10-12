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


def make_qa_contact_sheets(folder, camera_entries, transition_entries, *, log=lambda _m: None):
    folder = Path(folder)
    result = {"camera": [], "transitions": [], "images": [], "limitations":
              "Brightness and texture are only heuristics: cannot prove a champion or kill is visible."}
    camera_tiles = []
    for case in camera_entries:
        files = case.get("outputs") or []
        if not files:
            continue
        try:
            img = frame_at(Path(files[0]), 2.0)
            gray = ImageStat.Stat(img.convert("L"))
            contrast = round(gray.stddev[0],2)
            luminance = round(gray.mean[0],2)
            case_report = {"number": case.get("number"),"side": case.get("side"),
                           "mode":case.get("mode"),"mean_brightness":luminance,
                           "texture_contrast":contrast,
                           "suspected_black_or_flat":luminance<9 or contrast<6}
            result["camera"].append(case_report)
            camera_tiles.append((f'{case.get("number")} {case.get("side")} {case.get("mode")}',img))
        except Exception as exc:
            log(f"カメラ比較画像取得失敗: {exc}")
    try:
        path = _sheet(camera_tiles, folder/"camera_comparison.jpg")
        if path: result["images"].append(path)
    except Exception as exc:
        log("カメラ比較表作成失敗: "+str(exc))
    transitions = []
    try:
        camera_files = [Path(p) for case in camera_entries for p in case.get("outputs",[])]
        boundary = get_duration(camera_files[0], ffmpeg=str(ffmpeg_exe())) if camera_files else 2.0
    except Exception:
        boundary = 2.0
    for case in transition_entries:
        files = case.get("outputs") or []
        if not files:
            continue
        try:
            img = frame_at(Path(files[0]), boundary)
            transitions.append((case["style"],img))
        except Exception as exc:
            log(f"つなぎ演出比較のフレーム取得失敗 ({case.get('style')}): {exc}")
    try:
        path = _sheet(transitions,folder/"transition_comparison.jpg",columns=5)
        if path: result["images"].append(path)
    except Exception as exc:
        log("つなぎ比較表作成失敗: "+str(exc))
    if transitions:
        reference = next((im for style,im in transitions if style=="cut"),None)
        if reference is not None:
            for style,img in transitions:
                raw_a,raw_b=reference.tobytes(),img.tobytes()
                delta=round(sum(abs(x-y) for x,y in zip(raw_a,raw_b))/max(1,len(raw_a)),2)
                result["transitions"].append({"style":style,
                                              "mean_absolute_difference_from_cut":delta,
                                              "similar_at_join":style!="cut" and delta<5.0})
    return result
