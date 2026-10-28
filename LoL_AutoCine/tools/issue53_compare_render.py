"""Measure decoded pixels and format for opt-in versus legacy short renders."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def inspect(path: Path) -> dict:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Cannot decode {path.name}")
    result = dict(name=path.name, width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                  height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                  fps=capture.get(cv2.CAP_PROP_FPS),
                  frame_count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT)), samples={})
    for index in (0, 28, 29, 30, 31, 32, 60, 90):
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        okay, frame = capture.read()
        if okay:
            result["samples"][str(index)] = dict(mean=round(float(frame.mean()), 2),
                                                   clipped_pct=round(float(np.mean(frame >= 250) * 100), 2))
    capture.release()
    return result


def contact_sheet(legacy: Path, trial: Path, destination: Path) -> None:
    tiles = []
    for path, label in ((legacy, "Legacy"), (trial, "Trial")):
        capture = cv2.VideoCapture(str(path))
        row = []
        for index, moment in ((30, "PRE"), (31, "ONSET")):
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            okay, frame = capture.read()
            if not okay:
                raise ValueError(f"Frame {index} missing from {path.name}")
            frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_AREA)
            cv2.rectangle(frame, (0, 0), (320, 46), (8, 17, 30), -1)
            cv2.putText(frame, f"{label} {moment} frame {index}", (12, 31),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.76, (255, 255, 255), 2)
            row.append(frame)
        tiles.append(np.hstack(row))
        capture.release()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), np.vstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 92]):
        raise OSError(f"Could not write {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--contact-sheet", type=Path, help="First video legacy, second trial")
    args = parser.parse_args()
    data = [inspect(path) for path in args.videos]
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    if args.contact_sheet:
        if len(args.videos) != 2:
            parser.error("--contact-sheet requires exactly two videos")
        contact_sheet(*args.videos, args.contact_sheet)
    print(serialized)


if __name__ == "__main__":
    main()
