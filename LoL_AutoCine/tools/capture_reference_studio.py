"""Capture the actual interactive comparison window (no generated UI bitmap)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk

from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import legacy_app
from ui.layout_variants import LAYOUT_NAMES
from ui.reference_studio import ReferenceStudio


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", default=1660, type=int)
    parser.add_argument("--height", default=940, type=int)
    parser.add_argument("--scale", default=1.0, type=float)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output) as temp:
        legacy_app.SETTINGS = Path(temp) / "settings.json"
        root = tk.Tk()
        root.tk.call("tk", "scaling", args.scale)
        app = legacy_app.App(root)
        studio = ReferenceStudio(app)
        studio.window.geometry(f"{args.width}x{args.height}+0+0")
        files = []
        for n, name in enumerate(LAYOUT_NAMES, 1):
            app.var_ui_layout.set(name)
            studio._build()
            root.update()
            studio._offline_reference()
            root.update_idletasks()
            target = args.output / f"reference_{n:02d}_{args.width}x{args.height}.png"
            ImageGrab.grab(window=studio.window.winfo_id()).save(target)
            files.append(target.name)
        (args.output / "capture_manifest.json").write_text(json.dumps({
            "capture": "actual Tk comparison window",
            "game_connected": False,
            "preview": "labelled mock reference still because no LoL replay was connected; not live video",
            "size": [args.width, args.height],
            "scale": args.scale,
            "screens": files,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        app._live_preview.close()
        studio.window.destroy()
        root.destroy()


if __name__ == "__main__":
    main()
