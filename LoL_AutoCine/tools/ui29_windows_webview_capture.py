"""Capture real Windows WebView2 pixels from the source-host UI29 app.

The App bridge is live, but this deliberately uses no replay or recording.
Its images are offline visual evidence, not LoL functional acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui.audit29_desktop import (_child_command, _configure_webview2_runtime,
                                _stop_backend, _wait_for_backend)


def _activate(url: str, action: str, data: dict) -> dict:
    parsed = urlsplit(url)
    endpoint = f"{parsed.scheme}://{parsed.netloc}/api/action?{parsed.query}"
    payload = json.dumps({"action": action, "data": data}).encode("utf-8")
    with urlopen(Request(endpoint, data=payload,
                         headers={"Content-Type": "application/json"}), timeout=30) as response:
        return json.load(response)


def _capture_webview(window, path: Path, size: tuple[int, int]) -> None:
    from System import Action
    from System.Drawing import Size
    from System.IO import File
    from Microsoft.Web.WebView2.Core import CoreWebView2CapturePreviewImageFormat
    from webview.platforms.winforms import BrowserView

    form = BrowserView.instances[window.uid]
    pending = {}

    def resize() -> None:
        form.ClientSize = Size(*size)

    form.Invoke(Action(resize))
    time.sleep(0.25)
    stream = File.Create(str(path))
    try:
        def begin() -> None:
            pending["task"] = form.browser.webview.CoreWebView2.CapturePreviewAsync(
                CoreWebView2CapturePreviewImageFormat.Png, stream)

        form.Invoke(Action(begin))
        if not pending["task"].Wait(20000):
            raise TimeoutError("WebView2 screenshot timed out")
    finally:
        stream.Dispose()
    with Image.open(path) as image:
        if image.size != size:
            raise RuntimeError(f"WebView2 screenshot is {image.size}; expected {size}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "ui29" / "windows_webview2_offline")
    parser.add_argument("--screen", help="capture one audited screen")
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / "design" / "ui" / "implementation_audit_29_20261021" /
                            "SCREENS_29.json").read_text(encoding="utf-8"))
    screens = [screen for screen in inventory if not args.screen or screen["id"] == args.screen]
    if not screens:
        parser.error(f"unknown audited screen: {args.screen}")
    frozen = bool(getattr(sys, "frozen", False))
    capture_result = "CAPTURED_FROZEN_EXE_OFFLINE" if frozen else "CAPTURED_SOURCE_HOST_OFFLINE"

    import webview
    _configure_webview2_runtime(webview)
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    results = []
    with tempfile.TemporaryDirectory(prefix="ui29-webview-", dir=args.output) as temp:
        handoff = Path(temp) / "backend.json"
        log_path = Path(temp) / "backend.log"
        with log_path.open("wb") as log:
            child = subprocess.Popen(_child_command(handoff), cwd=ROOT, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            url = None
            try:
                url = _wait_for_backend(child, handoff)
                window = webview.create_window("LoL AutoCine UI29 Windows QA", "about:blank",
                                               width=640, height=480, frameless=True)

                def worker() -> None:
                    try:
                        for screen in screens:
                            sid = screen["id"]
                            try:
                                _activate(url, "screen", {"id": sid})
                                _activate(url, "theme", {"value": screen["theme"]})
                                parsed = urlsplit(url)
                                route = f"{parsed.scheme}://{parsed.netloc}/ui/{sid}?{parsed.query}"
                                window.load_url(route)
                                deadline = time.monotonic() + 15
                                while time.monotonic() < deadline:
                                    try:
                                        ready = window.evaluate_js(
                                            "document.readyState === 'complete' && "
                                            f"location.pathname.endsWith('/ui/{sid}')")
                                        if ready:
                                            break
                                    except Exception:
                                        pass
                                    time.sleep(0.1)
                                else:
                                    raise TimeoutError(f"WebView2 route did not load: {sid}")
                                time.sleep(0.3)
                                size = tuple(screen["resolution"])
                                path = args.output / f"{sid}.png"
                                _capture_webview(window, path, size)
                                bounds_json = window.evaluate_js(
                                    "JSON.stringify(Object.fromEntries([...document.querySelectorAll('[data-ui]')]"
                                    ".map(e=>{const r=e.getBoundingClientRect();"
                                    "return [e.dataset.ui,[r.x,r.y,r.width,r.height]]})))")
                                bounds = json.loads(bounds_json)
                                footer = window.evaluate_js(
                                    "(()=>{const r=document.querySelector('footer')?.getBoundingClientRect();"
                                    "return r?[r.x,r.y,r.width,r.height]:null})()")
                                if footer is not None:
                                    bounds[f"footer-{len(bounds)}"] = footer
                                bounds_dir = args.output / "bounds"
                                bounds_dir.mkdir(exist_ok=True)
                                (bounds_dir / f"{sid}.json").write_text(
                                    json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
                                results.append({"id": sid, "result": capture_result,
                                                "capture": path.name, "size": size,
                                                "bounds": f"bounds/{sid}.json"})
                            except Exception as exc:
                                results.append({"id": sid, "result": "FAIL", "error": repr(exc)})
                            print(sid, results[-1]["result"], flush=True)
                    finally:
                        window.destroy()

                webview.start(worker, gui="edgechromium", private_mode=True, debug=False)
            finally:
                _stop_backend(child, url)
    report = {"kind": "WINDOWS_WEBVIEW2_FROZEN_EXE_OFFLINE" if frozen else
              "WINDOWS_WEBVIEW2_SOURCE_HOST_OFFLINE", "lol_replay": "NOT_RUN",
              "gpu_record_audio_export": "NOT_RUN", "screens": results}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if len(results) == len(screens) and all(row["result"].startswith("CAPTURED") for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
