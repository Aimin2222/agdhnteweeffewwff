# -*- coding: utf-8 -*-
"""Local batch-reference review for xMedia and unviewable clip uploads.

Video bytes stay on Windows. This helper writes only small JPEG contact
sheets and JSON; never executes code from videos, downloads from the web,
or uploads anything to GitHub. It does not perform AI character detection.
"""
from __future__ import annotations
import argparse
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import zipfile
import tempfile
import shutil

from PIL import Image, ImageDraw, ImageOps


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm"}
SAMPLE_FRACTIONS = (0.06, 0.22, 0.38, 0.54, 0.70, 0.88)


def sanitized_filename(name, limit=88):
    safe = re.sub(r'[^a-zA-Z0-9_.-]+', '_', name).strip('._')
    return (safe or 'reference')[:limit]


def find_reference_videos(directory):
    """Accept a folder of clips OR one MP4 dropped directly onto the BAT."""
    directory=Path(directory)
    if directory.is_file():
        if directory.suffix.lower() not in VIDEO_SUFFIXES:
            raise ValueError("動画ファイル（MP4/MOV/MKV/WEBM）か動画フォルダーを指定してください")
        return [directory]
    if not directory.is_dir():
        raise FileNotFoundError(f"Video file/folder not found: {directory}")
    return sorted(p for p in directory.rglob("*")
                  if p.is_file() and p.suffix.lower() in VIDEO_SUFFIXES)


def create_sheets(input_folder, output_folder, *, ffmpeg=None, logger=print):
    # Accept a reference ZIP as well as direct MP4 files/folders. Extraction
    # uses safe locally generated names: never trust archive member paths.
    src = Path(input_folder)
    if src.is_file() and src.suffix.lower() == ".zip":
        if not zipfile.is_zipfile(src):
            raise ValueError("このZIPは壊れているかZIP形式ではありません")
        with tempfile.TemporaryDirectory(prefix="autocine_reference_") as td:
            extracted = Path(td)
            mappings = []
            count = 0
            total_size = 0
            with zipfile.ZipFile(src) as archive:
                for member in archive.infolist():
                    if member.is_dir() or Path(member.filename).suffix.lower() not in VIDEO_SUFFIXES:
                        continue
                    count += 1
                    total_size += member.file_size
                    if count > 120 or member.file_size > 1_000_000_000 or total_size > 4_000_000_000:
                        raise ValueError("動画数・解凍後容量が安全上限を超えました（120本・4GB以内）")
                    filename = (f"{count:03d}_" +
                                sanitized_filename(Path(member.filename).stem) +
                                Path(member.filename).suffix.lower())
                    target = extracted / filename
                    with archive.open(member) as reader, target.open("wb") as writer:
                        shutil.copyfileobj(reader, writer, length=1024 * 1024)
                    mappings.append({"archived_name": member.filename, "extracted_name": filename})
            if not mappings:
                raise ValueError("ZIP内にMP4/MOV/MKV/WEBMがありません")
            result = create_sheets(extracted, output_folder, ffmpeg=ffmpeg, logger=logger)
            out = Path(output_folder)
            mapping_path = out / "reference_archive_names.json"
            mapping_path.write_text(json.dumps({"source_zip": src.name, "items": mappings},
                                               ensure_ascii=False, indent=2), encoding="utf-8")
            with zipfile.ZipFile(result, "a", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(mapping_path, "reference_archive_names.json")
            return result
    from core.gpu_binary import ffmpeg_exe
    from core.montage_fx import get_duration
    executable=str(ffmpeg or ffmpeg_exe())
    output=Path(output_folder)
    output.mkdir(parents=True,exist_ok=True)
    shots=output/"frames"
    shots.mkdir(exist_ok=True)
    videos=find_reference_videos(input_folder)
    input_root=Path(input_folder)
    if input_root.is_file():
        input_root=input_root.parent
    report={"schema_version":1,"video_count":len(videos),"items":[],
            "notice":"Human/assistant visual review required; no AI tracking or upload."}
    for index,path in enumerate(videos,1):
        entry={"number":index,"original_name":path.name,
               "relative_path":str(path.relative_to(input_root)),
               "size_bytes":path.stat().st_size,"samples":[],
               "contact_sheet":None,"errors":[]}
        try:
            length=float(get_duration(path,ffmpeg=executable))
            if not (0.2<=length<7200):
                raise ValueError("Unsupported duration")
            entry["duration_seconds"]=round(length,3)
            tiles=[]
            for sample,ratio in enumerate(SAMPLE_FRACTIONS,1):
                second=max(0.0,min(length-.06,length*ratio))
                command=[executable,"-nostdin","-hide_banner","-loglevel","error",
                         "-ss",f"{second:.3f}","-i",str(path),
                         "-frames:v","1","-vf","scale=480:270",
                         "-f","image2pipe","-vcodec","png","-"]
                result=subprocess.run(command,capture_output=True,timeout=40)
                if result.returncode!=0 or not result.stdout:
                    entry["errors"].append(f"frame {sample}: "+str(result.stderr[-200:]))
                    continue
                with Image.open(BytesIO(result.stdout)) as raw:
                    img=raw.convert("RGB").copy()
                tiles.append((img,second))
                entry["samples"].append(round(second,2))
            if tiles:
                # Three columns, two rows, all frames labeled by actual time.
                w,h,band=480,270,24
                sheet=Image.new("RGB",(w*3,(h+band)*2),"#e6ebf2")
                draw=ImageDraw.Draw(sheet)
                for n,(img,second) in enumerate(tiles):
                    x=(n%3)*w
                    y=(n//3)*(h+band)
                    sheet.paste(img,(x,y+band))
                    draw.text((x+8,y+5),f"Frame {n+1} | {second:.2f} s",fill="#182338")
                filename=f"{index:03d}_{sanitized_filename(path.stem)}.jpg"
                destination=shots/filename
                sheet.save(destination,quality=86,optimize=True)
                entry["contact_sheet"]=str(destination.relative_to(output))
                logger(f"[{index}/{len(videos)}] {path.name} -> {filename}")
        except (OSError,ValueError,subprocess.SubprocessError) as exc:
            entry["errors"].append(f"{type(exc).__name__}: {exc}")
            logger(f"[{index}/{len(videos)}] Could not inspect {path.name}: {exc}")
        report["items"].append(entry)
        (output/"reference_review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    with zipfile.ZipFile(output/"ReferenceReview_contact_sheets.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
        z.write(output/"reference_review.json","reference_review.json")
        for entry in report["items"]:
            if entry["contact_sheet"]:
                p=output/entry["contact_sheet"]
                z.write(p,entry["contact_sheet"])
    return output/"ReferenceReview_contact_sheets.zip"


def choose_source():
    """When BAT is double-clicked, choose an MP4 or a video folder."""
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root = tk.Tk()
    root.withdraw()
    try:
        selected = filedialog.askopenfilename(
            title="AutoCine - 参考動画のMP4を選択（キャンセルでフォルダーを選択）",
            filetypes=[("動画・ZIP", "*.mp4 *.mov *.mkv *.webm *.zip"),
                       ("すべてのファイル", "*.*")])
        if not selected:
            selected = filedialog.askdirectory(title="AutoCine - 動画フォルダーを選択")
        if not selected:
            return None
        return Path(selected)
    finally:
        root.destroy()


def main():
    parser=argparse.ArgumentParser(description="Create contact sheets for every reference MP4")
    parser.add_argument("input_folder",nargs="?",type=Path,
                        help="A video file or a folder. Omit to open a picker.")
    parser.add_argument("--output",type=Path,default=None)
    args=parser.parse_args()
    source=args.input_folder if args.input_folder is not None else choose_source()
    if source is None:
        print("No reference video selected; nothing was changed.")
        return
    # Default destination next to the selected source and never inside MP4.
    dest = args.output
    if dest is None:
        dest = (source/"_AutoCineReferenceReview" if source.is_dir()
                else source.parent / ("_AutoCineReferenceReview_"+sanitized_filename(source.stem)))
    out=create_sheets(source,dest)
    print("Contact-sheet ZIP:",out)


if __name__=="__main__":
    main()
