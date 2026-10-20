"""Capture real Tk UI layouts without touching the user's saved settings.

Run on an interactive Windows desktop with a monitor large enough for the
requested geometry. Captures the application window, never a mock image.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile
import tkinter as tk

from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import legacy_app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1366)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--layout", choices=("現行配置 A", "テスト配置 B"), default="テスト配置 B")
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        legacy_app.SETTINGS = Path(temp) / "settings.json"
        root = tk.Tk()
        root.tk.call("tk", "scaling", args.scale)
        app = legacy_app.App(root)
        # App chooses its startup size; override it only after construction.
        root.geometry(f"{args.width}x{args.height}+10+10")
        app.var_ui_layout.set(args.layout)
        app._apply_ui_layout(save=False)
        root.update()
        root.after(150, root.quit)
        root.mainloop()
        x, y = root.winfo_rootx(), root.winfo_rooty()
        width, height = root.winfo_width(), root.winfo_height()
        ImageGrab.grab(bbox=(x, y, x + width, y + height), all_screens=True).save(args.output)
        app._live_preview.close()
        root.destroy()


if __name__ == "__main__":
    main()
