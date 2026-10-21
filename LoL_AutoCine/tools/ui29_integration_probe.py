"""Exercise the local UI HTTP bridge with the actual AutoCine App.

This probe deliberately does not start LoL, capture, recording, or export.
It validates screen/theme changes and camera/animation variable wiring only.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import threading
import tkinter as tk
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from legacy_app import App
from ui.audit29_runtime import SCREENS
from ui.audit29_server import UI29Server


OUTPUT = ROOT / "qa" / "ui29" / "local_bridge_probe.json"


def main():
    root = tk.Tk()
    app = App(root)
    root.withdraw()
    appearance = ROOT / "qa" / "ui29" / "probe_appearance.json"
    appearance.unlink(missing_ok=True)  # test-only file from the prior probe
    server = UI29Server(app, appearance)
    outcome = {"kind": "LOCAL_BRIDGE_ONLY", "lol_replay": "NOT_RUN",
               "gpu_record_audio_export": "NOT_RUN"}
    completed = threading.Event()

    def request(action, data):
        address = f"http://127.0.0.1:{server.http.server_port}/api/action?token={server.token}"
        body = json.dumps({"action": action, "data": data}).encode("utf-8")
        with urlopen(Request(address, data=body, headers={"Content-Type": "application/json"}), timeout=35) as response:
            return json.load(response)

    def worker():
        try:
            with urlopen(server.url, timeout=5) as response:
                chooser = response.read().decode("utf-8")
            assert "12候補・29画面は未採用" in chooser
            request("screen", {"id": "R-A-main"})
            request("camera_side", {"value": "BLUE"})
            request("camera_number", {"key": "third_dist", "value": 925})
            request("motion", {"value": "slide_left"})
            request("frame", {"id": "083/a_simple_main"})
            asset_url = (f"http://127.0.0.1:{server.http.server_port}"
                         f"/api/asset/083/a_simple_main?token={server.token}")
            with urlopen(asset_url, timeout=15) as response:
                assert response.read(8) == b"\x89PNG\r\n\x1a\n"
            checked_screens = []
            for candidate_id in SCREENS:
                current = request("screen", {"id": candidate_id})
                assert current["workspace"]["screen_id"] == candidate_id
                page_url = (f"http://127.0.0.1:{server.http.server_port}"
                            f"/ui/{candidate_id}?token={server.token}")
                with urlopen(page_url, timeout=5) as response:
                    page = response.read()
                assert b'/runtime/client.js' in page
                assert b'data-ui="preview-stage"' in page
                checked_screens.append(candidate_id)
            request("screen", {"id": "R-A-main"})
            state = request("theme", {"value": "dark"})
            assert state["workspace"]["screen_id"] == "R-A-main"
            assert state["workspace"]["theme"] == "dark"
            assert state["camera"]["side"] == "ブルー側基準"
            assert state["camera"]["values"]["third_dist"] == 925
            assert state["frame"]["motion"] == "左から登場"
            assert state["frame"]["id"] == "083/a_simple_main"
            assert len(state["frame"]["cards"]) == 4
            assert not state["capabilities"]["engage"]
            assert next(row for row in state["workspace"]["screens"]
                        if row["id"] == "T-A-M")["implemented"]
            outcome["result"] = "PASS"
            outcome["screen"] = state["workspace"]["screen_id"]
            outcome["candidate_roundtrip"] = checked_screens
            outcome["candidate_roundtrip_count"] = len(checked_screens)
            outcome["tested"] = ["neutral_chooser", "candidate_state", "theme_state",
                                 "camera_side", "camera_number", "entrance_motion",
                                 "audited_frame_pair", "catalog_asset_route",
                                 "all_29_screen_routes_preserve_state"]
        except Exception as exc:
            outcome["result"] = "FAIL"
            outcome["error"] = repr(exc)
        finally:
            completed.set()

    threading.Thread(target=worker, daemon=True, name="ui29-probe").start()
    def poll_completion():
        if completed.is_set():
            root.quit()
        else:
            root.after(20, poll_completion)
    root.after(20, poll_completion)
    root.after(45000, root.quit)
    root.mainloop()
    server.close()
    app.on_close()
    appearance.unlink(missing_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False))
    return 0 if outcome.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
