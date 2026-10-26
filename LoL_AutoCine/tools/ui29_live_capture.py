"""Capture implemented audited screens through the real App bridge.

No replay, capture, recording, or export is started. The resulting screenshots
are offline UI evidence, never a functional acceptance of those subsystems.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import re
from urllib.request import Request, urlopen

from ui29_review import ROOT, load_inventory
from ui29_source_baseline import EDGE_PATHS

sys.path.insert(0, str(ROOT))
from legacy_app import App
from ui.audit29_server import UI29Server
from ui.legacy_reconstruct import SCREEN_IDS as RECONSTRUCTED_SCREEN_IDS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, default=next((p for p in EDGE_PATHS if p.is_file()), None))
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "ui29" / "live_offline")
    parser.add_argument("--screen", help="capture one implemented audited screen for a quick check")
    parser.add_argument("--legacy-only", action="store_true", help="capture the ten raster reconstructions")
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    if not args.edge or not args.edge.is_file():
        parser.error("Microsoft Edge executable was not found")
    args.output.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    app = App(root)
    root.withdraw()
    appearance = args.output / "capture_appearance.json"
    appearance.unlink(missing_ok=True)
    server = UI29Server(app, appearance)
    completed = threading.Event()
    results = []
    implemented = [screen for screen in load_inventory()
                   if not args.legacy_only or screen["id"] in RECONSTRUCTED_SCREEN_IDS]

    def activate(action, data):
        url = f"http://127.0.0.1:{server.http.server_port}/api/action?token={server.token}"
        body = json.dumps({"action": action, "data": data}).encode("utf-8")
        with urlopen(Request(url, data=body, headers={"Content-Type": "application/json"}), timeout=35) as response:
            return json.load(response)

    def worker():
        try:
            for screen in implemented:
                if args.screen and screen["id"] != args.screen:
                    continue
                sid = screen["id"]
                try:
                    state = activate("screen", {"id": sid})
                    assert state["workspace"]["screen_id"] == sid
                    state = activate("theme", {"value": screen["theme"]})
                    assert state["workspace"]["theme"] == screen["theme"]
                    width, height = screen["resolution"]
                    capture = args.output / f"{sid}.png"
                    url = f"http://127.0.0.1:{server.http.server_port}/ui/{sid}?token={server.token}"
                    with tempfile.TemporaryDirectory(dir=args.output) as profile:
                        command = [str(args.edge), "--headless", "--disable-gpu", "--no-first-run",
                                   "--no-default-browser-check", "--hide-scrollbars",
                                   "--virtual-time-budget=2500", f"--user-data-dir={profile}",
                                   f"--window-size={width},{height}", f"--screenshot={capture}", url]
                        run = subprocess.run(command, timeout=60, capture_output=True, text=True,
                                             encoding="utf-8", errors="replace")
                    if not capture.is_file() or capture.stat().st_size == 0:
                        raise RuntimeError(f"Edge capture failed ({run.returncode}): {run.stderr[-400:]}")
                    # Use the same live route for a separate, read-only DOM measurement.
                    measured_url = url + "&measure=1"
                    with tempfile.TemporaryDirectory(dir=args.output) as profile:
                        command = [str(args.edge), "--headless", "--disable-gpu", "--no-first-run",
                                   "--no-default-browser-check", "--virtual-time-budget=2500",
                                   f"--user-data-dir={profile}", f"--window-size={width + 24},{height + 92}",
                                   "--dump-dom", measured_url]
                        dom_run = subprocess.run(command, timeout=60, capture_output=True, text=True,
                                                 encoding="utf-8", errors="replace")
                    match = re.search(r'<script[^>]*id="ui29-bounds"[^>]*>(.*?)</script>',
                                      dom_run.stdout, flags=re.DOTALL)
                    if not match:
                        raise RuntimeError(f"DOM measurement missing ({dom_run.returncode}); "
                                           f"marker={dom_run.stdout.find('ui29-bounds')}, "
                                           f"tail={dom_run.stdout[-200:]!r}")
                    bounds = json.loads(html.unescape(match.group(1)))
                    bounds_path = args.output / "bounds"
                    bounds_path.mkdir(exist_ok=True)
                    (bounds_path / f"{sid}.json").write_text(
                        json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
                    results.append({"id": sid, "result": "CAPTURED_OFFLINE", "capture": capture.name,
                                    "bounds": f"bounds/{sid}.json"})
                except Exception as exc:
                    results.append({"id": sid, "result": "FAIL", "error": repr(exc)})
                print(sid, results[-1]["result"], flush=True)
        finally:
            completed.set()

    threading.Thread(target=worker, daemon=True, name="ui29-live-capture").start()
    def poll():
        if completed.is_set():
            root.quit()
        else:
            root.after(50, poll)
    root.after(50, poll)
    root.mainloop()
    server.close()
    app.on_close()
    appearance.unlink(missing_ok=True)
    report = {"kind": "LIVE_APP_BRIDGE_OFFLINE", "lol_replay": "NOT_RUN",
              "gpu_record_audio_export": "NOT_RUN", "screens": results}
    (args.output / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    expected_count = 1 if args.screen else len(implemented)
    return 0 if len(results) == expected_count and all(row["result"] == "CAPTURED_OFFLINE" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
