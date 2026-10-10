# -*- coding: utf-8 -*-
"""LoL AutoCine v5.0.2 - complete white UI.

The Phase 1 white UI prototype is kept in ui_phase1_prototype.py.
This launcher activates the feature-complete white UI implemented in legacy_app.py,
while preserving the original core modules and handlers.
"""
import importlib.util
import subprocess
import tkinter as tk


def _ensure_dependencies() -> None:
    """Install missing runtime packages before importing the legacy application.

    The previous package assumed requirements.txt had already been installed,
    which caused a hard startup failure on a clean Windows PC.
    """
    required = {
        "numpy": "numpy",
        "PIL": "pillow",
        "imageio_ffmpeg": "imageio-ffmpeg>=0.5.1",
    }
    missing = [pkg for module, pkg in required.items() if importlib.util.find_spec(module) is None]
    if not missing:
        return
    try:
        print("[AutoCine] Installing missing dependencies:", ", ".join(missing), flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except Exception as exc:
        raise RuntimeError(
            "必要なPythonパッケージをインストールできませんでした。\n"
            "インターネット接続を確認してから START.bat を再実行してください。\n\n"
            f"詳細: {exc}"
        ) from exc


import sys
_ensure_dependencies()
from legacy_app import App


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
