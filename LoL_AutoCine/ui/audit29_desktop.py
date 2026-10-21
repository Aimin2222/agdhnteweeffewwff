"""Host the existing UI29 HTML inside a Windows WebView2 application window.

Tk and WebView2 each require their own GUI event loop. The sole AutoCine App
runs on the main thread of a child process; the parent hosts presentation only.
Both processes ship in the same portable EXE, and no external browser opens.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


APP = Path(__file__).resolve().parents[1]


def _select_fixed_webview2_runtime() -> Path | None:
    """Use an optional official Fixed Version runtime beside the portable EXE."""
    folder = Path(sys.executable).resolve().parent / "WebView2Fixed"
    if getattr(sys, "frozen", False) and (folder / "msedgewebview2.exe").is_file():
        os.environ["WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"] = str(folder)
        return folder
    return None


def _child_command(handoff: Path) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--ui29-backend", str(handoff)]
    return [sys.executable, str(APP / "app.py"), "--ui29-backend", str(handoff)]


def run_backend(handoff_file: str) -> None:
    import tkinter as tk
    from legacy_app import App
    from ui.audit29_server import UI29Server

    handoff = Path(handoff_file)
    root = tk.Tk()
    # Give the hidden legacy canvas its real layout dimensions before the
    # preview loop starts. A never-mapped canvas reports 1x1 and would force
    # the shared mirror compositor down to its 160x90 fallback.
    root.attributes("-alpha", 0.0)
    app = App(root)
    root.update()
    root.withdraw()
    server = UI29Server(app)
    handoff.write_text(json.dumps({"url": server.url}), encoding="utf-8")
    try:
        root.mainloop()
    finally:
        server.close()


def _wait_for_backend(child: subprocess.Popen, handoff: Path, timeout: float = 45) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError(f"AutoCine backend exited during startup ({child.returncode})")
        if handoff.exists():
            result = json.loads(handoff.read_text(encoding="utf-8"))
            if "error" in result:
                raise RuntimeError(result["error"])
            url = result["url"]
            try:
                with urlopen(url, timeout=2) as response:
                    if response.status == 200:
                        return url
            except OSError:
                pass
        time.sleep(0.1)
    raise TimeoutError("AutoCine backend did not become ready")


def _stop_backend(child: subprocess.Popen, url: str | None) -> None:
    if child.poll() is not None:
        return
    if url:
        parsed = urlsplit(url)
        endpoint = f"{parsed.scheme}://{parsed.netloc}/api/action?{parsed.query}"
        request = Request(endpoint, data=b'{"action":"desktop_exit","data":{}}',
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=8):
                pass
        except OSError:
            pass
    try:
        child.wait(timeout=12)
    except subprocess.TimeoutExpired:
        child.terminate()
        child.wait(timeout=5)


def _launch(*, smoke: bool, window_smoke: bool = False) -> None:
    with tempfile.TemporaryDirectory(prefix="autocine-ui29-") as temp:
        handoff = Path(temp) / "backend.json"
        log_path = Path(temp) / "backend.log"
        with log_path.open("wb") as log:
            child = subprocess.Popen(_child_command(handoff), cwd=APP, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            url = None
            try:
                try:
                    url = _wait_for_backend(child, handoff)
                except (RuntimeError, TimeoutError) as exc:
                    detail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
                    raise RuntimeError(f"{exc}\n{detail}") from exc
                if smoke:
                    parsed = urlsplit(url)
                    endpoint = f"{parsed.scheme}://{parsed.netloc}/api/state?{parsed.query}"
                    with urlopen(endpoint, timeout=5) as response:
                        state = json.load(response)
                    if len(state["workspace"]["screens"]) != 29:
                        raise RuntimeError("UI29 inventory missing in desktop backend")
                    return
                _select_fixed_webview2_runtime()
                import webview
                webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
                if window_smoke:
                    parsed = urlsplit(url)
                    view_url = f"{parsed.scheme}://{parsed.netloc}/choose?{parsed.query}"
                else:
                    view_url = url
                window = webview.create_window("LoL AutoCine — UI比較", view_url,
                                               width=1660, height=940,
                                               min_size=(1020, 650), hidden=window_smoke)
                if window_smoke:
                    result = {"count": None, "error": None}

                    def inspect_window():
                        try:
                            deadline = time.monotonic() + 20
                            while time.monotonic() < deadline:
                                try:
                                    count = window.evaluate_js(
                                        "document.querySelectorAll('button[data-id]').length")
                                    if count:
                                        result["count"] = count
                                        break
                                except Exception:
                                    pass
                                time.sleep(0.3)
                            if result["count"] != 12:
                                result["error"] = f"candidate chooser rendered {result['count']} groups"
                        finally:
                            window.destroy()

                    webview.start(inspect_window, gui="edgechromium",
                                  private_mode=True, debug=False)
                    if result["error"]:
                        raise RuntimeError(result["error"])
                else:
                    webview.start(gui="edgechromium", private_mode=True, debug=False)
            finally:
                _stop_backend(child, url)


def run_desktop(*, window_smoke: bool = False) -> None:
    _launch(smoke=False, window_smoke=window_smoke)


def smoke_backend() -> None:
    _launch(smoke=True)
