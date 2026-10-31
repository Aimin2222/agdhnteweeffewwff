"""Capture actual Windows WebView2 pixels for the standalone UI study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import traceback
from urllib.parse import urlencode

from PIL import Image

from launcher import WEB, configure_fixed_runtime, start_local_server


LABELS = {"hybrid": "候補8", "flow": "候補9", "library": "候補10"}


def resize(window: object, size: tuple[int, int]) -> None:
    from System import Action
    from System.Drawing import Size
    from webview.platforms.winforms import BrowserView

    form = BrowserView.instances[window.uid]
    form.Invoke(Action(lambda: setattr(form, "ClientSize", Size(*size))))
    time.sleep(0.15)


def capture(window: object, path: Path, size: tuple[int, int]) -> None:
    from System import Action
    from System.IO import File
    from Microsoft.Web.WebView2.Core import CoreWebView2CapturePreviewImageFormat
    from webview.platforms.winforms import BrowserView

    form = BrowserView.instances[window.uid]
    stream = File.Create(str(path))
    try:
        pending = {}
        form.Invoke(Action(lambda: pending.update(task=form.browser.webview.CoreWebView2.CapturePreviewAsync(
            CoreWebView2CapturePreviewImageFormat.Png, stream))))
        if not pending["task"].Wait(20000):
            raise TimeoutError(f"Capture timed out: {path}")
    finally:
        stream.Dispose()
    with Image.open(path) as bitmap:
        if bitmap.size != size:
            raise AssertionError(f"Unexpected screenshot dimensions: {path}: {bitmap.size} != {size}")


def wait_for(window: object, layout: str, popup: str, timeout: float = 12) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            ready = window.evaluate_js("""(() => ({
              complete:document.readyState==='complete',
              layout:document.body.dataset.layout,
              dialog:!!document.querySelector('#dialog')?.open,
              drawer:!document.querySelector('#drawer')?.hidden,
              image:document.querySelector('.picture img')?.complete
            }))()""")
            if (ready["complete"] and ready["layout"] == layout and ready["image"] and
                (not popup or ready["dialog"] or ready["drawer"])):
                return
        except Exception:
            pass
        time.sleep(0.1)
    raise TimeoutError(f"UI did not render: {layout}, popup={popup}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--screen", action="append", help="Capture only named Work screen ID")
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    screens = json.loads((WEB / "SCREENS.json").read_text(encoding="utf-8"))
    if args.screen:
        screens = [row for row in screens if row["id"] in args.screen]
        if len(screens) != len(set(args.screen)):
            parser.error("One or more requested Work screen IDs are unknown")

    import webview

    configure_fixed_runtime(webview)
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    server, base_url = start_local_server()
    errors = []
    records = []
    try:
        window = webview.create_window("AutoCine 候補8〜10 QA", "about:blank",
                                       width=650, height=480, frameless=True)

        def worker() -> None:
            try:
                for row in screens:
                    query = urlencode({"layout": row["layout"], "view": row["view"],
                                       "theme": row["theme"], **({"popup": row["popup"]}
                                                               if row["popup"] else {})})
                    if records:
                        window.evaluate_js("sessionStorage.clear()")
                    size = (row["width"], row["height"])
                    window.load_url(base_url.split("?")[0] + "?" + query)
                    wait_for(window, row["layout"], row["popup"])
                    resize(window, size)
                    # Give WebView2 one paint turn after loading local raster assets.
                    time.sleep(0.16)
                    check = window.evaluate_js("""(() => ({
                      label:document.querySelector('#variant')?.textContent.trim(),
                      title:document.title,
                      visible:document.body.innerText,
                      popup:document.querySelector('#dialog')?.open ||
                            !document.querySelector('#drawer')?.hidden,
                      overflow:document.documentElement.scrollWidth > innerWidth
                    }))()""")
                    expected = LABELS[row["layout"]]
                    if check["label"] != expected or expected not in check["title"]:
                        raise AssertionError(f"{row['id']}: candidate label mismatch: {check['label']}")
                    if any(name in check["visible"] for name in
                           ("P1 Focus", "P2 Guided", "P3 Collection")):
                        raise AssertionError(f"{row['id']}: developer name visible")
                    if row["popup"] and not check["popup"]:
                        raise AssertionError(f"{row['id']}: popup did not open")
                    if check["overflow"]:
                        raise AssertionError(f"{row['id']}: horizontal page overflow")
                    path = args.output / f"{row['id']}.png"
                    capture(window, path, size)
                    records.append({"id": row["id"], "size": list(size), "file": path.name,
                                    "candidate": expected, "popup": bool(row["popup"]),
                                    "result": "CAPTURED_WINDOWS_WEBVIEW2_MOCK"})
            except Exception as exc:
                errors.append(traceback.format_exc())
            finally:
                window.destroy()

        webview.start(worker, gui="edgechromium", private_mode=True, debug=False)
    finally:
        server.shutdown()
        server.server_close()
    report = {"kind": "STANDALONE_WORK_UI_WINDOWS_MOCK", "screens": records,
              "errors": errors, "real_lol_connection": "NOT_IMPLEMENTED",
              "record_gpu_audio_export": "NOT_IMPLEMENTED"}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    for row in records:
        print(f"{row['id']} {row['candidate']} {row['result']}")
    if errors:
        print(errors[0], file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
