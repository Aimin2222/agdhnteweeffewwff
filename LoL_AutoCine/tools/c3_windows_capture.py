"""Capture C3-P/S in real Windows WebView2 and compare with Work references.

Offline captures are visual/interaction evidence only. They do not pass LoL,
recording, GPU, audio, or export acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.parse import urlsplit

from PIL import Image, ImageChops

from ui29_windows_webview_capture import (
    _activate, _capture_webview, _child_command, _state, _stop_backend,
    _wait_for_backend, _wait_path,
)

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "design" / "ui" / "c3_refinement_20261027" / "screens"


def wait_js(window, condition: str, timeout: float = 10) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            if window.evaluate_js(condition):
                return
        except Exception:
            pass
        time.sleep(.15)
    raise TimeoutError(condition)


def capture(window, output: Path, reference: str) -> dict:
    source = REFERENCES / f"{reference}.png"
    with Image.open(source) as im:
        size = im.size
    target = output / f"{reference}_windows.png"
    _capture_webview(window, target, size)
    with Image.open(source) as original, Image.open(target) as actual:
        original = original.convert("RGB")
        actual = actual.convert("RGB")
        # Full-image comparison includes the Work schematic preview and the
        # intentionally blank real mirror when LoL is not connected.
        Image.blend(original, actual, .5).save(output / f"{reference}_overlay.png")
        ImageChops.difference(original, actual).save(output / f"{reference}_difference.png")
    boxes = json.loads(window.evaluate_js("JSON.stringify(Object.fromEntries("
        "[...document.querySelectorAll('[data-ui]')].map(e=>{const r=e.getBoundingClientRect();"
        "return [e.dataset.ui,[r.x,r.y,r.x+r.width,r.y+r.height]]})))"))
    return {"screen":reference,"size":size,"capture":target.name,
            "bounds":boxes,"visual_result":"REVIEW",
            "reason":"Work image uses a schematic game frame; offline real mirror is blank. UI geometry requires separate review."}


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    import webview
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    results=[];checks={}
    with tempfile.TemporaryDirectory(prefix="c3-webview-",dir=output) as temp:
        handoff=Path(temp)/"backend.json";log_path=Path(temp)/"backend.log"
        with log_path.open("wb") as log:
            env=os.environ.copy();env["AUTOCINE_UI3_LAUNCH"]="1"
            env["AUTOCINE_UI_COMPARE_PREFS"]=str(Path(temp)/"workspace.json")
            env["AUTOCINE_UI3_OUTPUT_DEFAULT"]=str(Path(temp)/"exports")
            child=subprocess.Popen(_child_command(handoff),cwd=ROOT,stdout=log,
                                   stderr=subprocess.STDOUT,env=env,
                                   creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
            backend=None
            try:
                backend=_wait_for_backend(child,handoff)
                parsed=urlsplit(backend)
                base=f"{parsed.scheme}://{parsed.netloc}"
                token=parsed.query
                window=webview.create_window("AutoCine C3 Windows QA","about:blank",
                                             width=1400,height=800,frameless=True)
                def worker():
                    try:
                        for variant,prefix in (("p","C3P"),("s","C3S")):
                            window.load_url(f"{base}/ui3/{variant}?{token}")
                            _wait_path(window,f"/ui3/{variant}")
                            wait_js(window,"!!document.querySelector('#editor-content > *')")
                            _activate(backend,"theme",{"value":"light"})
                            wait_js(window,"document.documentElement.dataset.theme === 'light'",5)
                            results.append(capture(window,output,f"{prefix}_main_light"))
                            if variant=="p":
                                window.evaluate_js("document.querySelector('[data-tab=detail]').click()")
                                results.append(capture(window,output,"C3P_detail_light"))
                                window.evaluate_js("document.querySelector('[data-tab=camera]').click()")
                                window.evaluate_js("document.querySelector('[data-drawer=camera]').click()")
                                wait_js(window,"!document.querySelector('#drawer').hidden")
                                results.append(capture(window,output,"C3P_camera_drawer"))
                                window.evaluate_js('''(() => {const input=document.querySelector('#num-third_dist');
                                  input.value='960';input.dispatchEvent(new Event('input',{bubbles:true}));
                                  document.querySelector('#drawer-apply').click()})()''')
                                wait_js(window,"document.querySelector('#drawer').hidden")
                                checks["camera_drawer_apply"]="PASS" if (
                                    _state(backend)["camera"]["values"]["third_dist"]==960) else "FAIL"
                                window.evaluate_js("document.querySelector('[data-tab=camera]').click()")
                            else:
                                window.evaluate_js("document.querySelector('[data-tab=easy]').click()")
                                results.append(capture(window,output,"C3S_easy_light"))
                                window.evaluate_js("document.querySelector('[data-tab=detail]').click()")
                                results.append(capture(window,output,"C3S_curve_light"))
                                window.evaluate_js("document.querySelector('[data-tab=easy]').click()")
                                window.evaluate_js("document.querySelector('[data-drawer=asset]').click()")
                                wait_js(window,"!document.querySelector('#drawer').hidden")
                                results.append(capture(window,output,"C3S_asset_drawer"))
                                paired=next((row for row in _state(backend)["frame"]["cards"]
                                             if row["paired_effect_id"]), None)
                                if paired is None:
                                    raise AssertionError("no same-theme frame/FX pair in catalog")
                                chosen=window.evaluate_js('''(() => {const card=document.querySelector('[data-frame="'''+
                                    paired["id"]+'''"]');
                                  card.click();return card.dataset.frame})()''')
                                window.evaluate_js("document.querySelector('#drawer-apply').click()")
                                wait_js(window,"document.querySelector('#drawer').hidden")
                                selected=_state(backend)["frame"]
                                checks["asset_and_paired_fx"]="PASS" if (
                                    selected["id"]==chosen and
                                    selected["effect_id"]==paired["paired_effect_id"]) else "FAIL"
                                window.evaluate_js("document.querySelector('[data-drawer=review]').click()")
                                wait_js(window,"!document.querySelector('#modalback').hidden")
                                results.append(capture(window,output,"C3S_export_review"))
                                window.evaluate_js("document.querySelector('#modal-cancel').click()")
                            _activate(backend,"theme",{"value":"dark"})
                            wait_js(window,"document.documentElement.dataset.theme === 'dark'",5)
                            results.append(capture(window,output,f"{prefix}_main_dark"))
                            _activate(backend,"theme",{"value":"light"})
                            wait_js(window,"document.documentElement.dataset.theme === 'light'",5)
                            results.append(capture(window,output,f"{prefix}_main_1366x768"))
                        # The two routes and original T-A-M share one App.
                        _activate(backend,"camera_number",{"key":"third_dist","value":930})
                        window.load_url(f"{base}/ui/T-A-M?{token}")
                        _wait_path(window,"/ui/T-A-M")
                        before=_state(backend)
                        window.load_url(f"{base}/ui3/s?{token}")
                        _wait_path(window,"/ui3/s")
                        after=_state(backend)
                        checks["shared_camera_state"]="PASS" if (before["camera"]["values"]["third_dist"]==
                            after["camera"]["values"]["third_dist"]==930) else "FAIL"
                        checks["shared_checked_scenes"]="PASS" if before["checked_count"]==after["checked_count"] else "FAIL"
                        checks["same_app_screen_id"]="PASS" if after["workspace"]["screen_id"]=="T-A-M" else "FAIL"
                    finally:
                        window.destroy()
                webview.start(worker,gui="edgechromium",private_mode=True,debug=False)
            finally:
                _stop_backend(child,backend)
    commit=subprocess.check_output(["git","-C",str(ROOT.parent),"rev-parse","HEAD"],text=True).strip()
    report={"kind":"C3_WINDOWS_WEBVIEW2_OFFLINE","source_commit":commit,
            "screens":results,"state_checks":checks,"live_lol":"NOT_RUN",
            "record_gpu_audio_export":"NOT_RUN"}
    (output/"index.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"screens":len(results),"checks":checks},ensure_ascii=False))
    return 0 if len(results)==12 and all(x=="PASS" for x in checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
