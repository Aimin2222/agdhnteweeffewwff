"""Capture real Windows WebView2 pixels from the source-host UI29 app.

The App bridge is live, but this deliberately uses no replay or recording.
Its images are offline visual evidence, not LoL functional acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
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
from ui.comparison_detail import DERIVED_DETAILS, DERIVED_MATERIALS
from ui.comparison_labels import CANDIDATE_ORDER, public_label


PRIORITY_SEVEN = (
    ("T-B-M", "T-B-C", "T-B-F"),
    ("L03-N", "L03-D", "material-legacy03"),
    ("T-A-M", "derived-testA", "material-testA"),
    ("L06-L", "L06-E", "L06-L"),
    ("R-E-main", "R-E-studio", "R-E-frames"),
    ("L02-M", "derived-legacy02", "material-legacy02"),
    ("L05-M", "derived-legacy05", "material-legacy05"),
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


def _issue3_numeric(window, url: str, sid: str, output: Path) -> dict:
    """Exercise native WebView2 numeric events against the real App state."""
    reference = sid.startswith("reference-")
    if reference:
        window.evaluate_js('document.querySelector(\'.topnav [data-view="color"]\').click()')
        selector = 'input[data-key="exposure"]'
    else:
        window.evaluate_js("document.querySelector('.ui3-tools-opener').click()")
        selector = '[data-ui3-global-color="exposure"]'
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if window.evaluate_js(f"!!document.querySelector({json.dumps(selector)})"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError(f"numeric exposure field missing: {sid}")

    def change(raw: str) -> dict:
        return window.evaluate_js(f'''(() => {{
          const input=document.querySelector({json.dumps(selector)});
          input.value={json.dumps(raw)};
          input.dispatchEvent(new Event('input',{{bubbles:true}}));
          input.dispatchEvent(new Event('change',{{bubbles:true}}));
          return {{value:input.value,badInput:input.validity.badInput,
                  invalid:input.getAttribute('aria-invalid')}};
        }})()''')

    def await_value(expected: float) -> None:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if _state(url)["global_color"]["values"].get("exposure") == expected:
                return
            time.sleep(0.1)
        raise AssertionError(f"exposure did not reach {expected}")

    change("0.12")
    await_value(0.12)
    checks = {}
    for label, raw in (("empty", ""), ("nonnumeric_normalized_to_empty", "abc"),
                       ("out_of_range", "9")):
        entered = change(raw)
        time.sleep(0.15)
        actual = _state(url)["global_color"]["values"].get("exposure")
        visible = window.evaluate_js(f'''(() => {{const input=document.querySelector({json.dumps(selector)});
          return {{value:input.value,invalid:input.getAttribute('aria-invalid'),
                  message:document.querySelector('#message')?.textContent ||
                    document.querySelector('[role="status"]')?.textContent}};}})()''')
        if actual != 0.12 or visible["value"] != "0.12" or visible["invalid"] != "true":
            raise AssertionError(f"{sid} {label}: backend={actual}, entered={entered}, ui={visible}")
        checks[label] = {"result": "PASS", "backend": actual, "visible": visible}
        if label == "empty":
            _capture_webview(window, output / f"issue3_{sid}_empty.png", (1920, 1080))
    change("0")
    await_value(0)
    time.sleep(1.25)
    retained = _state(url)["global_color"]["values"].get("exposure")
    if retained != 0:
        raise AssertionError(f"{sid}: explicit zero was not retained")
    checks["explicit_zero"] = {"result": "PASS", "backend": retained}
    checks["native_badInput_keystroke"] = "NOT_RUN"
    _capture_webview(window, output / f"issue3_{sid}_zero.png", (1920, 1080))
    if reference:
        window.evaluate_js('document.querySelector(\'.topnav [data-view="camera"]\').click()')
        window.evaluate_js('document.querySelector(\'.topnav [data-view="color"]\').click()')
    else:
        window.evaluate_js("document.querySelector('.ui3-route-opener').click()")
        _wait_path(window, "/compare/detail/testA")
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if window.evaluate_js("!!document.querySelector('[data-compare=main]')"):
                break
            time.sleep(0.1)
        else:
            raise AssertionError("candidate 3 detail return button missing")
        window.evaluate_js("document.querySelector('[data-compare=main]').click()")
        _wait_path(window, "/ui/T-A-M")
        window.evaluate_js("document.querySelector('.ui3-tools-opener').click()")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            visible = window.evaluate_js(f"document.querySelector({json.dumps(selector)})?.value")
            if visible == "0":
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        raise AssertionError(f"{sid}: zero not retained after screen transition")
    checks["screen_switch_retains_zero"] = "PASS"
    if reference:
        window.evaluate_js('document.querySelector(\'.topnav [data-view="camera"]\').click()')
        selector = 'input[data-camera="third_yaw"]'
    else:
        selector = 'input[data-setting="third_yaw"]'
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if window.evaluate_js(f"!!document.querySelector({json.dumps(selector)})"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError(f"{sid}: camera numeric field missing")
    change("32")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if _state(url)["camera"]["values"].get("third_yaw") == 32:
            break
        time.sleep(0.1)
    else:
        raise AssertionError(f"{sid}: camera numeric value 32 was not applied")
    change("")
    time.sleep(0.15)
    yaw = _state(url)["camera"]["values"].get("third_yaw")
    if yaw != 32 or window.evaluate_js(f"document.querySelector({json.dumps(selector)})?.value") != "32":
        raise AssertionError(f"{sid}: blank camera value replaced {yaw}")
    checks["camera_empty_keeps_32"] = "PASS"
    change("0")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if _state(url)["camera"]["values"].get("third_yaw") == 0:
            break
        time.sleep(0.1)
    else:
        raise AssertionError(f"{sid}: explicit camera zero was not applied")
    checks["camera_explicit_zero"] = "PASS"
    if sid == "T-A-M":
        selector = 'input[data-setting="pre"]'
        change("6")
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if _state(url)["trim"].get("pre") == 6:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("candidate 3 pre-trim did not reach App")
        change("")
        time.sleep(1.25)
        pre = _state(url)["trim"].get("pre")
        visible = window.evaluate_js(f"document.querySelector({json.dumps(selector)})?.value")
        if pre != 6 or visible != "6":
            raise AssertionError(f"candidate 3 blank pre-trim changed value: {pre}, {visible}")
        checks["trim_empty_keeps_6_after_poll"] = "PASS"
    return checks


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
    _, detail_id, material_id = next(row for row in PRIORITY_SEVEN if row[0] == main_id)
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
    detail_path = (f"/compare/detail/{detail_id.removeprefix('derived-')}"
                   if detail_id.startswith("derived-") else f"/ui/{detail_id}")
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
    camera_mode_clicked = window.evaluate_js('''(() => {const button=
      document.querySelector('[data-action="camera_mode"][data-action-value="fixed_auto"]')||
      [...document.querySelectorAll('.camera-card')].find(b=>b.textContent.includes('固定視点'));
      if(!button)return false;button.click();return true})()''')
    if not camera_mode_clicked:
        raise AssertionError(f"{main_id}: fixed-auto camera choice missing")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and "固定視点" not in _state(url)["camera"]["mode"]:
        time.sleep(0.1)
    if "固定視点" not in _state(url)["camera"]["mode"]:
        raise AssertionError(f"{main_id}: camera mode click did not reach AutoCine App")
    detail_controls = window.evaluate_js('''(() => {const text=document.body.innerText;
      return {camera:!!document.querySelector('input[data-setting="third_dist"]'),
        fx:text.includes('FX')||text.includes('エフェクト')||
          !!document.querySelector('[data-action="screen"][data-action-value="T-B-F"]'),
        material:text.includes('キルフレーム')||text.includes('素材'),
        scene:text.includes('シーン'),timeline:text.includes('タイムライン')||!!document.querySelector('[data-ui="timeline"]'),
        color:text.includes('色')||text.includes('DOF')};})()''')
    if not all(detail_controls.values()):
        raise AssertionError(f"{detail_id}: missing detail controls: {detail_controls}")
    if material_id != detail_id:
        selector = ('[data-compare="material"]' if material_id.startswith("material-") else
                    'a[href="E_frames.html"]' if material_id == "R-E-frames" else
                    f'[data-action="screen"][data-action-value="{material_id}"]')
        clicked = window.evaluate_js('''(() => {const button=document.querySelector(''' +
                                     json.dumps(selector) + ''');if(!button)return false;
                                     button.click();return true})()''')
        if not clicked:
            raise AssertionError(f"{main_id}: in-candidate material entrance missing")
        material_path = (f"/compare/material/{material_id.removeprefix('material-')}"
                         if material_id.startswith("material-") else f"/ui/{material_id}")
        _wait_path(window, material_path)
    # The catalog arrives asynchronously after navigation, especially in a
    # frozen EXE. Wait for a real catalog id instead of racing its first render.
    frame_id = ''
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and not frame_id:
        frame_id = window.evaluate_js('''(() => {const cards=[...document.querySelectorAll(
          '[data-ui^="material-card-"][data-frame-id], [data-ui^="library-card-"][data-frame-id]')];
          const card=cards.find(c=>c.dataset.frameId==='083/a_simple_main')||cards[0];
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
    effect_id = _state(url)["frame"]["effect_id"]
    if not effect_id:
        raise AssertionError(f"{main_id}: same-name FX did not follow selected frame")
    fx_clicked = window.evaluate_js('''(() => {const button=
      document.querySelector('[data-action="effect_strength"][data-action-value="weak"]')||
      [...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='弱');
      if(!button)return false;button.click();return true})()''')
    if fx_clicked:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and _state(url)["frame"]["strength"] != "weak":
            time.sleep(0.1)
        if _state(url)["frame"]["strength"] != "weak":
            raise AssertionError(f"{main_id}: FX strength click did not reach AutoCine App")
    motion_clicked = window.evaluate_js('''(() => {const button=
      document.querySelector('[data-action="motion"][data-action-value="slide_left"]')||
      [...document.querySelectorAll('.motion-grid .motion')]
        .find(b=>b.textContent.includes('左から登場'));
      if(!button)return false;button.click();return true})()''')
    if motion_clicked:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and _state(url)["frame"]["motion"] != "左から登場":
            time.sleep(0.1)
        if _state(url)["frame"]["motion"] != "左から登場":
            raise AssertionError(f"{main_id}: motion click did not reach AutoCine App")
    if material_id != main_id:
        back = window.evaluate_js('''(() => {const button=document.querySelector('[data-compare="main"]')||
          [...document.querySelectorAll('button')].find(b=>b.textContent.includes('メインへ戻る'));
          if(!button)return false;button.click();return true})()''')
        if not back:
            raise AssertionError(f"{main_id}: return to main missing")
        _wait_path(window, f"/ui/{main_id}")
    restored = _state(url)
    if (restored["camera"]["values"].get("third_dist") != 910 or
            "固定視点" not in restored["camera"]["mode"] or
            restored["frame"]["id"] != frame_id or
            restored["frame"]["effect_id"] != effect_id or
            (fx_clicked and restored["frame"]["strength"] != "weak") or
            (motion_clicked and restored["frame"]["motion"] != "左から登場")):
        raise AssertionError(f"{main_id}: shared settings lost on return to main")
    return {"main_controls": controls, "detail_controls": detail_controls,
            "camera_distance_input": "PASS", "camera_mode_choice": "PASS",
            "same_name_fx": {"result": "PASS", "id": effect_id},
            "fx_strength_choice": "PASS" if fx_clicked else "NOT_EXPOSED_IN_THIS_VIEW",
            "entrance_motion_choice": "PASS" if motion_clicked else "NOT_EXPOSED_IN_THIS_VIEW",
            "frame_selection": {"result": "PASS", "id": frame_id},
            "main_detail_main": "PASS", "shared_state_retained": "PASS"}


def _reference_flow(window, url: str, variant: str) -> dict:
    """Exercise the new LD/LN WebView with the shared native App, offline."""
    initial = window.evaluate_js('''(() => ({nav:document.querySelectorAll('.topnav [data-view]').length,
      rail:document.querySelectorAll('.tool-rail [data-view]').length,
      mirror:!!document.querySelector('[data-action="mirror_start"]'),
      scan:!!document.querySelector('[data-action="scan"]'),
      export:!!document.querySelector('[data-view="export"]')}))()''')
    if initial != {"nav": 8, "rail": 7, "mirror": True, "scan": True, "export": True}:
        raise AssertionError(f"reference controls missing: {initial}")
    audit = window.evaluate_js('''(() => ({compareDisabled:document.querySelector('#compare-view')?.disabled,
      shotInTimeline:document.querySelector('.timeline #shot-strip')!==null,
      shotCheck:document.querySelector('#open-shot-checks')!==null,
      stageHeight:document.querySelector('.preview-stage')?.getBoundingClientRect().height}))()''')
    if audit["compareDisabled"] is not True:
        raise AssertionError("unimplemented before/after comparison appears active")
    if variant == "ln":
        if not audit["shotInTimeline"] or not audit["shotCheck"] or audit["stageHeight"] < 525:
            raise AssertionError(f"Lolnam lower stack or selection entrance missing: {audit}")
        window.evaluate_js("document.querySelector('#open-shot-checks').click()")
        if not window.evaluate_js("document.querySelector('#shot-check-dialog').open"):
            raise AssertionError("shot output checklist did not open")
        window.evaluate_js("document.querySelector('#shot-check-close').click()")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="camera"]\').click()')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if window.evaluate_js('!!document.querySelector(\'input[data-camera="third_dist"]\')'):
            break
        time.sleep(0.1)
    else:
        raise AssertionError("reference camera tab missing numeric input")
    window.evaluate_js('''(() => {const input=document.querySelector('input[data-camera="third_dist"]');
      input.focus();input.value='937';input.dispatchEvent(new Event('input',{bubbles:true}));})()''')
    time.sleep(1.5)
    kept_draft = window.evaluate_js('''(() => {const input=document.querySelector('input[data-camera="third_dist"]');
      return input?.value==='937' && document.activeElement===input})()''')
    if not kept_draft:
        raise AssertionError("1100ms snapshot replaced an active numeric draft")
    window.evaluate_js('''(() => {const input=document.querySelector('input[data-camera="third_dist"]');
      input.value='920';input.dispatchEvent(new Event('change',{bubbles:true}));})()''')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["camera"]["values"].get("third_dist") != 920:
        time.sleep(0.1)
    if _state(url)["camera"]["values"].get("third_dist") != 920:
        raise AssertionError("reference camera input did not reach the native App")
    window.evaluate_js('''(() => {const input=document.querySelector('input[data-camera="third_yaw"]');
      input.value='32';input.dispatchEvent(new Event('change',{bubbles:true}));})()''')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["camera"]["values"].get("third_yaw") != 32:
        time.sleep(0.1)
    if _state(url)["camera"]["values"].get("third_yaw") != 32:
        raise AssertionError("reference yaw input did not reach the native App")
    time.sleep(1.3)
    if window.evaluate_js('document.querySelector(\'input[data-camera="third_yaw"]\')?.value') != "32":
        raise AssertionError("reference yaw reset after the 1100ms state poll")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="material"]\').click()')
    card = window.evaluate_js('''(() => {const x=document.querySelector('.inspector-body [data-action="frame"]');
      if(!x)return '';const id=JSON.parse(x.dataset.data).id;x.click();return id})()''')
    if not card:
        raise AssertionError("real frame catalog not shown in reference inspector")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["frame"]["id"] != card:
        time.sleep(0.1)
    current = _state(url)
    if current["frame"]["id"] != card or not current["frame"]["effect_id"]:
        raise AssertionError("reference frame and paired FX did not reach native App")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="color"]\').click()')
    window.evaluate_js('''(() => {const input=document.querySelector('input[data-key="exposure"]');
      input.value='0.12';input.dispatchEvent(new Event('change',{bubbles:true}));})()''')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _state(url)["global_color"]["values"].get("exposure") != 0.12:
        time.sleep(0.1)
    if _state(url)["global_color"]["values"].get("exposure") != 0.12:
        raise AssertionError("global exposure did not reach the native Template value")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="export"]\').click()')
    window.evaluate_js('''(() => {for(const [id,value] of [['fps','144'],['encoder','gpu']]){
      const input=document.getElementById(id);input.value=value;
      input.dispatchEvent(new Event('change',{bubbles:true}));}})()''')
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        output = _state(url)["output"]
        if str(output["fps"]).startswith("144") and str(output["encoder_policy"]).startswith("GPU"):
            break
        time.sleep(0.1)
    else:
        raise AssertionError("fps/encoder settings did not reach native App")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="camera"]\').click()')
    window.evaluate_js('document.querySelector(\'.topnav [data-view="export"]\').click()')
    selected_output = window.evaluate_js('''(() => ({fps:document.querySelector('#fps')?.value,
      encoder:document.querySelector('#encoder')?.value}))()''')
    if selected_output != {"fps": "144", "encoder": "gpu"}:
        raise AssertionError(f"fps/encoder controls lost saved values: {selected_output}")
    window.evaluate_js('document.querySelector(\'.topnav [data-view="main"]\').click()')
    other = "ln" if variant == "ld" else "ld"
    window.evaluate_js(f'document.querySelector(\'[data-route="{other}"]\').click()')
    _wait_path(window, f"/ui3/reference/{other}")
    retained = _state(url)
    if (retained["camera"]["values"].get("third_dist") != 920 or
            retained["camera"]["values"].get("third_yaw") != 32 or
            retained["global_color"]["values"].get("exposure") != 0.12 or
            retained["frame"]["id"] != card):
        raise AssertionError("reference UI switch reset native settings")
    return {"main_controls": "PASS", "audit_p0": audit, "camera_input": "PASS",
            "camera_yaw_roundtrip": "PASS",
            "global_exposure_roundtrip": "PASS",
            "fps_encoder_retained": "PASS", "real_frame": card,
            "paired_effect": current["frame"]["effect_id"], "cross_variant_state": "PASS",
            "live_lol_gpu_record_audio_mp4": "NOT_RUN"}


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
    parser.add_argument("--reference", choices=("ld", "ln"),
                        help="capture a Work reference layout using the real UI3 backend")
    parser.add_argument("--reference-all", action="store_true",
                        help="with --reference, capture all eight tabs, dark and 1366x768")
    parser.add_argument("--detail-family", choices=tuple(DERIVED_DETAILS),
                        help="capture one explicitly derived comparison detail")
    parser.add_argument("--material-family", choices=("legacy02", "legacy03", "legacy05", "testA"),
                        help="capture a complemented material view")
    parser.add_argument("--priority-seven-flow", action="store_true",
                        help="capture and click through the seven comparison candidates offline")
    parser.add_argument("--ui3-flow", action="store_true",
                        help="click through candidate 3 only, including its integrated tools")
    parser.add_argument("--issue3-numeric", action="store_true",
                        help="regress empty, bad, out-of-range and explicit zero in WebView2")
    parser.add_argument("--numbered-label-audit", action="store_true",
                        help="capture chooser/switchers and reject old candidate names in Windows WebView2")
    args = parser.parse_args(argv)
    if args.reference_all and not args.reference:
        parser.error("--reference-all requires --reference")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / "ui" / "comparison7_screens.json").read_text(encoding="utf-8"))
    screens = [screen for screen in inventory if not args.screen or screen["id"] == args.screen]
    if args.reference:
        if args.screen or args.detail_family or args.material_family or args.ui3_flow or args.priority_seven_flow:
            parser.error("--reference must be used alone")
        screens = [{"id": f"reference-{args.reference}", "main_id": "T-A-M",
                    "family": args.reference, "resolution": [1920, 1080], "theme": "light"}]
    if args.priority_seven_flow:
        if args.screen or args.detail_family or args.material_family:
            parser.error("--priority-seven-flow cannot be combined with another selection")
        wanted = {row[0] for row in PRIORITY_SEVEN}
        screens = [screen for screen in inventory if screen["id"] in wanted]
    if args.ui3_flow:
        if args.screen or args.detail_family or args.material_family or args.priority_seven_flow:
            parser.error("--ui3-flow must be used alone")
        screens = [screen for screen in inventory if screen["id"] == "T-A-M"]
    if args.issue3_numeric:
        if args.reference or args.screen or args.ui3_flow or args.detail_family or args.material_family:
            parser.error("--issue3-numeric must be used alone")
        screens = [{"id": sid, "main_id": "T-A-M", "family": "testA",
                    "resolution": [1920, 1080], "theme": "light"}
                   for sid in ("reference-ld", "reference-ln", "T-A-M")]
    if args.detail_family:
        if args.screen or args.material_family:
            parser.error("choose exactly one screen/detail/material selector")
        main_id = DERIVED_DETAILS[args.detail_family][2]
        reference = next(screen for screen in inventory if screen["id"] == main_id)
        screens = [{"id": f"derived-{args.detail_family}", "family": args.detail_family,
                    "main_id": main_id, "resolution": reference["resolution"], "theme": "light"}]
    if args.material_family:
        if args.screen:
            parser.error("choose exactly one screen/detail/material selector")
        main_id = DERIVED_MATERIALS[args.material_family][2]
        reference = next(screen for screen in inventory if screen["id"] == main_id)
        screens = [{"id": f"material-{args.material_family}", "family": args.material_family,
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
            child_env = os.environ.copy()
            child_env["AUTOCINE_UI_COMPARE_PREFS"] = str(Path(temp) / "comparison_workspace.json")
            if args.reference or args.ui3_flow or args.issue3_numeric:
                child_env["AUTOCINE_UI3_LAUNCH"] = "1"
            child = subprocess.Popen(_child_command(handoff), cwd=ROOT, stdout=log,
                                     stderr=subprocess.STDOUT, env=child_env,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            url = None
            try:
                url = _wait_for_backend(child, handoff)
                window = webview.create_window("LoL AutoCine UI29 Windows QA", "about:blank",
                                               width=640, height=480, frameless=True)
                chooser_audit = None

                def worker() -> None:
                    nonlocal chooser_audit
                    try:
                        if args.numbered_label_audit:
                            parsed = urlsplit(url)
                            window.load_url(f"{parsed.scheme}://{parsed.netloc}/choose?{parsed.query}")
                            _wait_path(window, "/choose")
                            time.sleep(0.2)
                            chooser_audit = window.evaluate_js('''(() => ({
                              labels:[...document.querySelectorAll('button[data-id]')]
                                .map(button=>button.textContent.trim()),
                              title:document.title,
                              visible:document.body.innerText
                            }))()''')
                            expected = [public_label(family) for family, _ in CANDIDATE_ORDER]
                            if chooser_audit["labels"] != expected:
                                raise AssertionError(f"chooser labels are not numbered: {chooser_audit['labels']}")
                            if any(name in chooser_audit["visible"] for name in
                                   ("旧テスト", "旧案", "新E", "Flow", "ハイブリッド", "ウィザード")):
                                raise AssertionError("old candidate name remains on chooser")
                            _capture_webview(window, args.output / "chooser.png", (1280, 800))
                        previous_candidate_state = None
                        for screen in screens:
                            sid = screen["id"]
                            try:
                                _activate(url, "screen", {"id": screen.get("main_id", sid)})
                                _activate(url, "theme", {"value": screen["theme"]})
                                if previous_candidate_state is not None:
                                    switched = _state(url)
                                    if (switched["camera"]["values"].get("third_dist") !=
                                            previous_candidate_state["camera"]["values"].get("third_dist") or
                                            switched["frame"]["id"] != previous_candidate_state["frame"]["id"] or
                                            switched["frame"]["effect_id"] !=
                                            previous_candidate_state["frame"]["effect_id"]):
                                        raise AssertionError(f"{sid}: settings lost when switching candidates")
                                parsed = urlsplit(url)
                                route_path = (f"/ui3/reference/{sid.split('-')[1]}" if args.issue3_numeric and
                                              sid.startswith("reference-") else
                                              f"/ui3/reference/{args.reference}" if args.reference else
                                              f"/compare/material/{screen['family']}" if args.material_family else
                                              f"/compare/detail/{screen['family']}" if args.detail_family
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
                                if (args.reference or sid.startswith("reference-")) and not window.evaluate_js(
                                        "Boolean(document.querySelector('#inspector-title'))"):
                                    raise AssertionError(f"reference UI did not render: {sid}")
                                time.sleep(0.3)
                                size = tuple(screen["resolution"])
                                path = args.output / f"{sid}.png"
                                _capture_webview(window, path, size)
                                reference_captures = []
                                reference_compact_bounds = None
                                reference_dark_contrast = None
                                if args.reference_all:
                                    prefix = args.reference.upper()
                                    for view_id in ("main", "easy", "detail", "camera", "curve",
                                                    "color", "material", "export"):
                                        if view_id != "main":
                                            window.evaluate_js(
                                                f'document.querySelector(\'.topnav [data-view="{view_id}"]\').click()')
                                        deadline = time.monotonic() + 8
                                        while time.monotonic() < deadline:
                                            if window.evaluate_js("document.querySelector('#inspector-title').textContent") == {
                                                "main": "メイン", "easy": "かんたん", "detail": "詳細編集",
                                                "camera": "カメラ", "curve": "カーブ", "color": "色調整",
                                                "material": "素材", "export": "出力"}[view_id]:
                                                break
                                            time.sleep(0.1)
                                        else:
                                            raise TimeoutError(f"reference tab failed: {view_id}")
                                        time.sleep(0.15)
                                        name = f"{prefix}_{view_id}_light_1920x1080.png"
                                        _capture_webview(window, args.output / name, (1920, 1080))
                                        reference_captures.append(name)
                                    window.evaluate_js('document.querySelector(\'.topnav [data-view="main"]\').click()')
                                    _activate(url, "theme", {"value": "dark"})
                                    deadline = time.monotonic() + 8
                                    while time.monotonic() < deadline:
                                        if window.evaluate_js("document.body.classList.contains('dark')"):
                                            break
                                        time.sleep(0.1)
                                    else:
                                        raise TimeoutError("reference dark theme did not apply")
                                    reference_dark_contrast = window.evaluate_js('''(() => {
                                      const luminance = text => {
                                        const values=text.match(/[\\d.]+/g)?.slice(0,3).map(Number);
                                        if(!values || values.length!==3)return null;
                                        const channel=values.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
                                        return .2126*channel[0]+.7152*channel[1]+.0722*channel[2];
                                      };
                                      return ['.timeline-foot input','.topnav button.active','.variants button.active']
                                        .map(selector=>{const node=document.querySelector(selector);
                                          if(!node)return {selector,contrast:null};
                                          const style=getComputedStyle(node),a=luminance(style.color),b=luminance(style.backgroundColor);
                                          return {selector,color:style.color,background:style.backgroundColor,
                                            contrast:a===null||b===null?null:Math.round((Math.max(a,b)+.05)/(Math.min(a,b)+.05)*100)/100};});
                                    })()''')
                                    if any(row["contrast"] is None or row["contrast"] < 4.5
                                           for row in reference_dark_contrast):
                                        raise AssertionError(f"dark controls have low contrast: {reference_dark_contrast}")
                                    name = f"{prefix}_main_dark_1920x1080.png"
                                    _capture_webview(window, args.output / name, (1920, 1080))
                                    reference_captures.append(name)
                                    _activate(url, "theme", {"value": "light"})
                                    deadline = time.monotonic() + 8
                                    while time.monotonic() < deadline:
                                        if not window.evaluate_js("document.body.classList.contains('dark')"):
                                            break
                                        time.sleep(0.1)
                                    else:
                                        raise TimeoutError("reference light theme did not restore")
                                    name = f"{prefix}_main_light_1366x768.png"
                                    _capture_webview(window, args.output / name, (1366, 768))
                                    reference_captures.append(name)
                                    reference_compact_bounds = window.evaluate_js('''(() => {
                                      const box = selector => {
                                        const node=document.querySelector(selector);
                                        if (!node) return null;
                                        const rect=node.getBoundingClientRect();
                                        return {top:rect.top,bottom:rect.bottom,height:rect.height};
                                      };
                                      return {stage:box('.preview-stage'),timeline:box('.timeline'),
                                        footer:box('footer'),viewportHeight:innerHeight,
                                        scrollHeight:document.documentElement.scrollHeight};
                                    })()''')
                                    if args.reference == "ln":
                                        bounds = reference_compact_bounds
                                        if (not bounds["stage"] or not bounds["timeline"] or
                                                bounds["stage"]["bottom"] > bounds["timeline"]["top"] + 1 or
                                                bounds["timeline"]["bottom"] > bounds["footer"]["top"] + 1):
                                            raise AssertionError(f"compact LN layout overlaps: {bounds}")
                                    _capture_webview(window, args.output / path.name, size)
                                label_audit = None
                                if args.numbered_label_audit:
                                    label_audit = window.evaluate_js('''(() => {
                                      const tab=document.querySelector('button[aria-controls="ui29-switch-panel"]');
                                      const panel=document.querySelector('#ui29-switch-panel');
                                      const picker=panel?.querySelector('select');
                                      tab?.click();
                                      return {tab:tab?.textContent.trim(),title:document.title,
                                        labels:[...picker.options].map(option=>option.textContent.trim()),
                                        selected:picker?.value,visible:document.body.innerText,
                                        panel_open:panel?.style.display==='block'};
                                    })()''')
                                    expected = public_label(screen["family"])
                                    if (label_audit["tab"] != expected or
                                            label_audit["labels"] !=
                                            [public_label(family) for family, _ in CANDIDATE_ORDER] or
                                            label_audit["selected"] !=
                                            dict(CANDIDATE_ORDER)[screen["family"]] or
                                            not label_audit["panel_open"] or
                                            expected not in label_audit["title"] or
                                            any(name in label_audit["visible"] for name in
                                                ("旧テスト", "旧案", "新E", "Flow", "ハイブリッド",
                                                "現行UI整理型", "標準編集", "ウィザード",
                                                 "A案", "B案", "E案"))):
                                        raise AssertionError(f"{sid}: candidate name audit failed: {label_audit}")
                                    _capture_webview(window, args.output / f"switch_{sid}.png", size)
                                    window.evaluate_js(
                                        'document.querySelector("button[aria-controls=ui29-switch-panel]").click()')
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
                                if args.ui3_flow:
                                    candidate_p0 = window.evaluate_js('''(() => ({
                                      sliders:document.querySelectorAll('.ui3-camera-range').length,
                                      reset:!!document.querySelector('.ui3-camera-reset'),
                                      materialTabs:document.querySelectorAll('.ui3-material-tabs button').length,
                                      none:!!document.querySelector('[data-ui3-none="1"]'),
                                      imageEntryDisabled:document.querySelector('.tabs .ui3-image-unavailable')?.disabled,
                                      switchInTools:!!document.querySelector('#ui3-tools .ui3-switch-opener'),
                                      referenceInTabs:document.querySelectorAll('.tabs .ui3-reference-opener').length}))()''')
                                    if candidate_p0 != {"sliders": 4, "reset": True,
                                                        "materialTabs": 3, "none": True,
                                                        "imageEntryDisabled": True,
                                                        "switchInTools": True,
                                                        "referenceInTabs": 0}:
                                        raise AssertionError(f"candidate 3 P0 controls missing: {candidate_p0}")
                                    window.evaluate_js('''(() => {const slider=document.querySelector(
                                      '.ui3-camera-range[data-camera-key="third_dist"]');slider.value='930';
                                      slider.dispatchEvent(new Event('change',{bubbles:true}));})()''')
                                    deadline = time.monotonic() + 8
                                    while time.monotonic() < deadline and _state(url)["camera"]["values"].get("third_dist") != 930:
                                        time.sleep(0.1)
                                    if _state(url)["camera"]["values"].get("third_dist") != 930:
                                        raise AssertionError("candidate 3 slider did not update native camera")
                                    window.evaluate_js("document.querySelector('.ui3-camera-reset').click()")
                                    deadline = time.monotonic() + 8
                                    while time.monotonic() < deadline and _state(url)["camera"]["values"].get("third_dist") != 950:
                                        time.sleep(0.1)
                                    if _state(url)["camera"]["values"].get("third_dist") != 950:
                                        raise AssertionError("candidate 3 camera reset did not apply")
                                    window.evaluate_js("document.querySelector('[data-ui3-none=\"1\"]').click()")
                                    deadline = time.monotonic() + 8
                                    while time.monotonic() < deadline and _state(url)["frame"]["id"]:
                                        time.sleep(0.1)
                                    if _state(url)["frame"]["id"]:
                                        raise AssertionError("candidate 3 none material did not clear frame")
                                    motion_controls = window.evaluate_js('''(() => {
                                      document.querySelector('.ui3-material-tabs [data-tab="motion"]').click();
                                      return document.querySelectorAll('.ui3-motion-choice').length})()''')
                                    if motion_controls != 6:
                                        raise AssertionError(f"candidate 3 entrance motion controls: {motion_controls}")
                                    window.evaluate_js('''(() => {
                                      document.querySelector('.ui3-material-tabs [data-tab="effect"]').click();
                                      document.querySelector('.ui3-material-tabs [data-tab="frame"]').click();})()''')
                                    tools_ready = window.evaluate_js(
                                        "document.querySelectorAll('#ui3-tools button').length")
                                    if tools_ready < 18:
                                        raise AssertionError(f"candidate 3 tools missing: {tools_ready}")
                                    _activate(url, "native_editor_zone", {"zone": "fx"})
                                    if not _state(url)["workspace"]["native_editor_visible"]:
                                        raise AssertionError("candidate 3 did not reveal the real FX editor")
                                    _activate(url, "native_legacy_hide", {})
                                    if _state(url)["workspace"]["native_editor_visible"]:
                                        raise AssertionError("candidate 3 did not return from the real editor")
                                flow = _priority_flow(window, url, sid) if (
                                    args.priority_seven_flow or args.ui3_flow) else None
                                if args.ui3_flow and flow is not None:
                                    window.evaluate_js("document.querySelector('.ui3-tools-opener')?.click()")
                                    if not window.evaluate_js("!!document.querySelector('[data-ui3-global-color=exposure]')"):
                                        raise AssertionError("candidate 3 global color control is missing")
                                    window.evaluate_js('''(() => {const input=document.querySelector(
                                      '[data-ui3-global-color=exposure]');input.value='0.12';
                                      input.dispatchEvent(new Event('change',{bubbles:true}));})()''')
                                    deadline = time.monotonic() + 8
                                    while (time.monotonic() < deadline and
                                           _state(url)["global_color"]["values"].get("exposure") != 0.12):
                                        time.sleep(0.1)
                                    if _state(url)["global_color"]["values"].get("exposure") != 0.12:
                                        raise AssertionError("candidate 3 color did not reach native App")
                                    flow["candidate_p0"] = {**candidate_p0,
                                        "camera_slider_native": "PASS", "camera_reset_native": "PASS",
                                        "none_material_native": "PASS", "motion_six_controls": "PASS",
                                        "global_color_native": "PASS"}
                                reference_flow = _reference_flow(window, url, args.reference) if args.reference else None
                                issue3_result = _issue3_numeric(window, url, sid, args.output) if args.issue3_numeric else None
                                if flow:
                                    previous_candidate_state = _state(url)
                                results.append({"id": sid, "result": capture_result,
                                                "capture": path.name, "size": size,
                                                "reference_captures": reference_captures,
                                                **({"reference_compact_bounds": reference_compact_bounds}
                                                   if reference_compact_bounds else {}),
                                                **({"reference_dark_contrast": reference_dark_contrast}
                                                   if reference_dark_contrast else {}),
                                                "bounds": f"bounds/{sid}.json",
                                                "main_detail_roundtrip": ("PASS" if args.detail_family or flow else "NOT_RUN"),
                                                **({"reference_flow": reference_flow} if reference_flow else {}),
                                                **({"issue3_numeric": issue3_result} if issue3_result else {}),
                                                **({"numbered_label_audit": label_audit} if label_audit else {}),
                                                **({"priority_seven_flow": flow,
                                                    "previous_candidate_state_retained":
                                                        "PASS" if len(results) else "FIRST_CANDIDATE"}
                                                   if flow else {})})
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
              "gpu_record_audio_export": "NOT_RUN", "screens": results,
              **({"chooser": chooser_audit} if args.numbered_label_audit else {})}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if len(results) == len(screens) and all(row["result"].startswith("CAPTURED") for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
