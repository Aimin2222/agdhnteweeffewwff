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
            request("screen", {"id": "L03-N"})
            preset_state = request("easy_preset", {"value": "Lolnam風スムーズ"})
            assert preset_state["easy_preset"] == "Lolnam風スムーズ"
            detail_state = request("screen", {"id": "L03-D"})
            assert detail_state["easy_preset"] == preset_state["easy_preset"]
            assert detail_state["workspace"]["screen_id"] == "L03-D"
            outcome["stage"] = "legacy06_library"
            library = request("screen", {"id": "L06-L"})
            assert len(library["frame"]["library_cards"]) == 6
            assert {item["status"] for item in library["frame"]["library_cards"]} == {"approved", "review"}
            frame_id = "004/freljord_frame"
            assert frame_id in {item["id"] for item in library["frame"]["library_cards"]}
            outcome["stage"] = "legacy06_frame"
            applied = request("frame", {"id": frame_id})
            assert applied["frame"]["id"] == frame_id
            assert applied["frame"]["effect_id"] == ""
            outcome["stage"] = "legacy06_editor"
            editor = request("screen", {"id": "L06-E"})
            assert editor["frame"]["id"] == frame_id
            assert editor["camera"]["values"]["third_dist"] == detail_state["camera"]["values"]["third_dist"]
            outcome["stage"] = "testb_camera_controls"
            request("screen", {"id": "T-B-M"})
            request("camera_mode", {"value": "full_auto"})
            request("camera_style", {"value": "third_cinema"})
            request("camera_side", {"value": "RED"})
            testb_settings = request("screen", {"id": "T-B-C"})
            assert testb_settings["camera"]["side"] == "レッド側基準"
            assert "三人称シネマ" in testb_settings["camera"]["style"]
            assert "フルオート" in testb_settings["camera"]["mode"]
            for style in ("third_cinema", "third", "geo_aim", "cinema", "fps",
                          "orbit", "lolnam_cinema", "follow", "cinema_top", "top"):
                style_state = request("camera_style", {"value": style})
                assert style_state["camera"]["style"]
            request("camera_number", {"key": "motion_arc", "value": 14})
            request("camera_number", {"key": "motion_dolly", "value": 5})
            request("screen", {"id": "T-B-F"})
            camera_again = request("screen", {"id": "T-B-C"})
            assert camera_again["camera"]["values"]["motion_arc"] == 14
            assert camera_again["camera"]["values"]["motion_dolly"] == 5
            assert "俯瞰 追従のみ" in camera_again["camera"]["style"]
            outcome["stage"] = "testb_frame_motion_controls"
            effects = request("screen", {"id": "T-B-F"})
            assert len(effects["frame"]["testb_cards"]) == 3, effects["frame"]["testb_cards"]
            assert {item["id"] for item in effects["frame"]["testb_cards"]} == {
                "083/a_simple_main", "004/freljord_frame", "063/weak_01"}
            selected = request("frame", {"id": "063/weak_01"})
            assert selected["frame"]["id"] == "063/weak_01"
            for motion in ("instant", "slide_left", "slide_right", "slide_up", "slide_down", "pop"):
                motion_state = request("motion", {"value": motion})
                from core.kill_icons import MOTION_STYLES
                assert motion_state["frame"]["motion"] == MOTION_STYLES[motion], motion_state["frame"]["motion"]
            effects_again = request("screen", {"id": "T-B-C"})
            assert effects_again["frame"]["id"] == "063/weak_01"
            assert effects_again["frame"]["motion"] == MOTION_STYLES["pop"]
            outcome["result"] = "PASS"
            outcome["screen"] = state["workspace"]["screen_id"]
            outcome["candidate_roundtrip"] = checked_screens
            outcome["candidate_roundtrip_count"] = len(checked_screens)
            outcome["tested"] = ["neutral_chooser", "candidate_state", "theme_state",
                                 "camera_side", "camera_number", "entrance_motion",
                                 "audited_frame_pair", "catalog_asset_route",
                                 "all_29_screen_routes_preserve_state",
                                 "legacy03_easy_preset_and_detail_switch",
                                 "legacy06_real_catalog_and_editor_state",
                                 "testb_camera_mode_style_side_roundtrip",
                                 "testb_all_10_styles_and_numeric_roundtrip",
                                 "testb_real_frame_and_six_motion_roundtrip"]
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
