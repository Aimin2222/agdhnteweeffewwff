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
from ui.comparison_detail import DERIVED_DETAILS


PRIORITY_FIVE = (
    ("T-B-M", "T-B-C", "T-B-F"),
    ("L03-N", "L03-D", "L03-D"),
    ("T-A-M", "derived-testA", "derived-testA"),
    ("L06-L", "L06-E", "L06-L"),
    ("R-E-main", "R-E-studio", "R-E-frames"),
)


def _activate(url: str, action: str, data: dict) -> dict:
    parsed = urlsplit(url)
    endpoint = f"{parsed.scheme}://{parsed.netloc}/api/action?{parsed.query}"
    payload = json.dumps({"action": action, "data": data}).encode("utf-8")
    with urlopen(Request(endpoint, data=payload,
                         headers={"Content-Type": "application/json"}), timeout=30) as response:
        return json.load(response)


def _state(url: str) -> dict:
    parsed = urlsplit(url)
    with urlopen(f"{parsed.scheme}://{parsed.netloc}/api/state?{parsed.query}", timeout=5) as response:
        return json.load(response)


def _wait_path(window, path: str, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if window.evaluate_js("location.pathname") == path:
                return
        except Exception:
            pass
        time.sleep(0.1)
    raise TimeoutError(f"WebView2 navigation did not reach {path}")


def _priority_flow(window, url: str, main_id: str) -> dict:
    """Offline UI click-through. Checks the shared App state, never starts LoL/recording."""
    _, detail_id, material_id = next(row for row in PRIORITY_FIVE if row[0] == main_id)
    controls = window.evaluate_js('''(() => {
      const labels=[...document.querySelectorAll('button')].map(b=>b.textContent.trim());
      const has=s=>labels.some(label=>label.includes(s));
      return {mirror:has('ミラー開始'),scan:has('スキャン')||!!document.querySelector('[data-ui="scene-list"]'),
        scenes:!!document.querySelector('[data-ui="scene-list"], [data-ui^="scene-card-"]'),
        export:has('動画を作成')||has('書き出')||has('自動作成'),
        settings:has('基本設定')||has('GPU・音声・HUD設定'),
        preview:!!document.querySelector('[data-ui="preview-stage"]')};
    })()''')
    if main_id == "R-E-main":
        opened = window.evaluate_js('''(() => {const step=[...document.querySelectorAll('.step')]
          .find(e=>e.querySelector('strong')?.textContent.trim()==='02');
          if(!step)return false;step.click();
          return document.querySelector('[data-ui="scene-list"]')?.style.display==='block'})()''')
        controls["scan_scene_drawer_opened"] = bool(opened)
    if not all(controls.values()):
        raise AssertionError(f"{main_id}: missing main controls: {controls}")
    clicked = window.evaluate_js('''(() => {const button=document.querySelector('[data-compare="detail"]')||
      [...document.querySelectorAll('button')].find(b=>b.textContent.includes('詳細編集へ'));
      if(!button)return false;button.click();return true})()''')
    if not clicked:
        raise AssertionError(f"{main_id}: detail entrance missing")
    detail_path = ("/compare/detail/testA" if detail_id == "derived-testA" else f"/ui/{detail_id}")
    _wait_path(window, detail_path)
    distance = window.evaluate_js('''(() => {const input=document.querySelector('input[data-setting="third_dist"]');
      if(!input)return false;input.value='910';input.dispatchEvent(new Event('change',{bubbles:true}));
      return true})()''')
    if not distance:
        raise AssertionError(f"{main_id}: detailed camera distance input missing")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["camera"]["values"].get("third_dist") != 910:
        time.sleep(0.1)
    if _state(url)["camera"]["values"].get("third_dist") != 910:
        raise AssertionError(f"{main_id}: camera input did not reach AutoCine App")
    detail_controls = window.evaluate_js('''(() => {const text=document.body.innerText;
      return {camera:!!document.querySelector('input[data-setting="third_dist"]'),
        fx:text.includes('FX')||text.includes('エフェクト'),
        material:text.includes('キルフレーム')||text.includes('素材'),
        scene:text.includes('シーン'),timeline:text.includes('タイムライン')||!!document.querySelector('[data-ui="timeline"]'),
        color:text.includes('色')||text.includes('DOF')};})()''')
    if not all(detail_controls.values()):
        raise AssertionError(f"{detail_id}: missing detail controls: {detail_controls}")
    if material_id != detail_id:
        selector = (f'[data-action="screen"][data-action-value="{material_id}"]'
                    if material_id != "R-E-frames" else 'a[href="E_frames.html"]')
        clicked = window.evaluate_js('''(() => {const button=document.querySelector(''' +
                                     json.dumps(selector) + ''');if(!button)return false;
                                     button.click();return true})()''')
        if not clicked:
            raise AssertionError(f"{main_id}: in-candidate material entrance missing")
        _wait_path(window, f"/ui/{material_id}")
    # The catalog arrives asynchronously after navigation, especially in a
    # frozen EXE. Wait for a real catalog id instead of racing its first render.
    frame_id = ''
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and not frame_id:
        frame_id = window.evaluate_js('''(() => {const card=document.querySelector(
          '[data-ui^="material-card-"], [data-ui^="library-card-"][data-frame-id]');
          if(!card||!card.dataset.frameId)return '';const id=card.dataset.frameId;card.click();return id})()''')
        if not frame_id:
            time.sleep(0.1)
    if not frame_id:
        raise AssertionError(f"{main_id}: selectable real material card missing")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["frame"]["id"] != frame_id:
        time.sleep(0.1)
    if _state(url)["frame"]["id"] != frame_id:
        raise AssertionError(f"{main_id}: frame selection did not reach AutoCine App")
    if material_id != main_id:
        back = window.evaluate_js('''(() => {const button=document.querySelector('[data-compare="main"]')||
          [...document.querySelectorAll('button')].find(b=>b.textContent.includes('メインへ戻る'));
          if(!button)return false;button.click();return true})()''')
        if not back:
            raise AssertionError(f"{main_id}: return to main missing")
        _wait_path(window, f"/ui/{main_id}")
    restored = _state(url)
    if restored["camera"]["values"].get("third_dist") != 910 or restored["frame"]["id"] != frame_id:
        raise AssertionError(f"{main_id}: shared settings lost on return to main")
    return {"main_controls": controls, "detail_controls": detail_controls,
            "camera_distance_input": "PASS", "frame_selection": {"result": "PASS", "id": frame_id},
            "main_detail_main": "PASS", "shared_state_retained": "PASS"}


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
    parser.add_argument("--detail-family", choices=tuple(DERIVED_DETAILS),
                        help="capture one explicitly derived comparison detail (outside the 29 audited screens)")
    parser.add_argument("--priority-five-flow", action="store_true",
                        help="capture and click through the five priority candidates offline")
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / "design" / "ui" / "implementation_audit_29_20261021" /
                            "SCREENS_29.json").read_text(encoding="utf-8"))
    screens = [screen for screen in inventory if not args.screen or screen["id"] == args.screen]
    if args.priority_five_flow:
        if args.screen or args.detail_family:
            parser.error("--priority-five-flow cannot be combined with --screen or --detail-family")
        wanted = {row[0] for row in PRIORITY_FIVE}
        screens = [screen for screen in inventory if screen["id"] in wanted]
    if args.detail_family:
        if args.screen:
            parser.error("--screen and --detail-family cannot be combined")
        main_id = DERIVED_DETAILS[args.detail_family][2]
        reference = next(screen for screen in inventory if screen["id"] == main_id)
        screens = [{"id": f"derived-{args.detail_family}", "family": args.detail_family,
                    "main_id": main_id, "resolution": reference["resolution"], "theme": "light"}]
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
                                _activate(url, "screen", {"id": screen.get("main_id", sid)})
                                _activate(url, "theme", {"value": screen["theme"]})
                                parsed = urlsplit(url)
                                route_path = (f"/compare/detail/{screen['family']}" if args.detail_family
                                              else f"/ui/{sid}")
                                route = f"{parsed.scheme}://{parsed.netloc}{route_path}?{parsed.query}"
                                window.load_url(route)
                                deadline = time.monotonic() + 15
                                while time.monotonic() < deadline:
                                    try:
                                        ready = window.evaluate_js(
                                            "document.readyState === 'complete' && "
                                            f"location.pathname.endsWith({route_path!r})")
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
                                if args.detail_family:
                                    # Exercise the actual WebView navigation and shared Tk
                                    # state, not only a direct HTTP request to the route.
                                    _activate(url, "camera_number", {"key": "third_dist", "value": 900})
                                    window.evaluate_js("document.querySelector('[data-compare=main]').click()")
                                    deadline = time.monotonic() + 10
                                    while time.monotonic() < deadline:
                                        if window.evaluate_js("location.pathname") == f"/ui/{screen['main_id']}":
                                            break
                                        time.sleep(0.1)
                                    else:
                                        raise TimeoutError("detail → main navigation failed")
                                    deadline = time.monotonic() + 10
                                    while time.monotonic() < deadline:
                                        if window.evaluate_js("!![...document.querySelectorAll('button')]"
                                                              ".find(b=>b.textContent.includes('詳細編集へ'))"):
                                            break
                                        time.sleep(0.1)
                                    else:
                                        raise TimeoutError("main comparison button did not load")
                                    window.evaluate_js("[...document.querySelectorAll('button')]"
                                                       ".find(b=>b.textContent.includes('詳細編集へ')).click()")
                                    deadline = time.monotonic() + 10
                                    while time.monotonic() < deadline:
                                        if window.evaluate_js("location.pathname") == route_path:
                                            break
                                        time.sleep(0.1)
                                    else:
                                        raise TimeoutError("main → detail navigation failed")
                                    parsed = urlsplit(url)
                                    state_url = f"{parsed.scheme}://{parsed.netloc}/api/state?{parsed.query}"
                                    with urlopen(state_url, timeout=5) as response:
                                        restored = json.load(response)
                                    if restored["camera"]["values"]["third_dist"] != 900:
                                        raise AssertionError("camera setting was lost during view switch")
                                flow = _priority_flow(window, url, sid) if args.priority_five_flow else None
                                results.append({"id": sid, "result": capture_result,
                                                "capture": path.name, "size": size,
                                                "bounds": f"bounds/{sid}.json",
                                                "main_detail_roundtrip": ("PASS" if args.detail_family or flow else "NOT_RUN"),
                                                **({"priority_five_flow": flow} if flow else {})})
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
