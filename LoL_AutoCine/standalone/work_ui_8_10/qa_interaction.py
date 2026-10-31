"""Offline click-through checks in the real standalone Windows WebView2 host."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import traceback

from launcher import configure_fixed_runtime, start_local_server


def wait_js(window: object, expression: str, timeout: float = 8) -> object:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = window.evaluate_js(expression)
            if value:
                return value
        except Exception:
            pass
        time.sleep(0.1)
    raise AssertionError(f"Timed out waiting for: {expression}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    import webview

    configure_fixed_runtime(webview)
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    server, url = start_local_server()
    checks = []
    errors = []
    try:
        window = webview.create_window("AutoCine 候補8〜10 操作QA", url,
                                       width=1600, height=900, frameless=True)

        def check(name: str, value: object) -> None:
            if not value:
                raise AssertionError(name)
            checks.append(name)

        def worker() -> None:
            try:
                wait_js(window, "document.querySelector('#variant')?.textContent==='候補8'")
                check("candidate8_main", True)
                window.evaluate_js("document.querySelector('#theme').click()")
                check("dark_theme", window.evaluate_js(
                    "document.documentElement.dataset.theme==='dark'"))
                changed = window.evaluate_js("""(() => {
                  const row=[...document.querySelectorAll('.setting')]
                    .find(e=>e.querySelector('label')?.textContent.includes('FXの強さ'));
                  if(!row)return false;
                  const input=row.querySelector('input[type=number]');
                  input.value='55';input.dispatchEvent(new Event('input',{bubbles:true}));
                  return row.querySelector('input[type=range]').value==='55';
                })()""")
                check("slider_number_link", changed)
                window.evaluate_js("""(() => {
                  document.querySelectorAll('.scene')[1].click();
                  document.querySelector('.scene input').click();
                })()""")
                check("scene_and_checkbox_are_separate", window.evaluate_js(
                    "document.querySelectorAll('.scene')[1].classList.contains('active') && "
                    "!document.querySelector('.scene input').checked"))
                window.evaluate_js("document.querySelector('[data-view=detail]').click()")
                wait_js(window, "new URLSearchParams(location.search).get('view')==='detail' && "
                                "document.querySelector('#variant')?.textContent==='候補8'")
                check("detail_keeps_fx", window.evaluate_js("""(() => {
                  const row=[...document.querySelectorAll('.setting')]
                    .find(e=>e.querySelector('label')?.textContent.includes('FXの強さ'));
                  return row?.querySelector('input[type=number]').value==='55';})()"""))
                window.evaluate_js("document.querySelector('header [data-pop=compare]').click()")
                wait_js(window, "document.querySelector('#dialog')?.open")
                check("compare_numbers_only", window.evaluate_js("""(() =>
                  [...document.querySelectorAll('#dialog [data-layout]')]
                    .map(b=>b.textContent.trim()).join(',')==='候補8,候補9,候補10')()"""))
                window.evaluate_js("document.querySelector('#dialog [data-layout=flow]').click()")
                wait_js(window, "document.querySelector('#variant')?.textContent==='候補9'")
                check("candidate9_keeps_theme", window.evaluate_js(
                    "document.documentElement.dataset.theme==='dark'"))
                window.evaluate_js("""[...document.querySelectorAll('button')]
                  .find(b=>b.textContent.trim()==='詳細編集へ進む').click()""")
                wait_js(window, "new URLSearchParams(location.search).get('view')==='detail'")
                check("candidate9_detail_camera", window.evaluate_js(
                    "!!document.querySelector('#right input[type=number]')"))
                window.evaluate_js("""(() => {
                  const row=[...document.querySelectorAll('.setting')]
                    .find(e=>e.querySelector('label')?.textContent==='距離');
                  const n=row.querySelector('input[type=number]');
                  n.value='1000';n.dispatchEvent(new Event('input',{bubbles:true}));
                })()""")
                window.evaluate_js("document.querySelector('header [data-pop=compare]').click()")
                wait_js(window, "document.querySelector('#dialog')?.open")
                window.evaluate_js("document.querySelector('#dialog [data-layout=library]').click()")
                wait_js(window, "document.querySelector('#variant')?.textContent==='候補10'")
                window.evaluate_js("document.querySelector('[data-view=detail]').click()")
                wait_js(window, "new URLSearchParams(location.search).get('view')==='detail'")
                check("candidate10_keeps_camera_value", window.evaluate_js("""(() => {
                  const row=[...document.querySelectorAll('.setting')]
                    .find(e=>e.querySelector('label')?.textContent==='距離');
                  return row?.querySelector('input[type=number]').value==='1000';})()"""))
                window.evaluate_js("document.querySelector('header [data-pop=output]').click()")
                wait_js(window, "document.querySelector('#dialog')?.open")
                check("output_is_mock", window.evaluate_js(
                    "document.querySelector('#dialog').innerText.includes('実際の録画は開始しません')"))
                window.evaluate_js("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
                check("escape_closes_dialog", wait_js(window,
                    "!document.querySelector('#dialog')?.open"))
            except Exception:
                errors.append(traceback.format_exc())
            finally:
                window.destroy()

        webview.start(worker, gui="edgechromium", private_mode=True, debug=False)
    finally:
        server.shutdown()
        server.server_close()
    report = {"kind": "STANDALONE_WORK_UI_INTERACTION_MOCK", "passed": checks,
              "errors": errors, "real_lol_connection": "NOT_IMPLEMENTED"}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(checks)} passed; {len(errors)} errors")
    if errors:
        print(errors[0])
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
