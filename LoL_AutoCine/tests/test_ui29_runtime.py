"""Candidate and theme switches cannot reset the shared AutoCine model."""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui.audit29_runtime import Audit29Runtime, SCREENS, default_preferences_path
from ui.audit29_server import UI29Server
from ui.comparison_detail import DERIVED_DETAILS, render_detail, render_material
from ui.legacy_reconstruct import render_legacy


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Listbox:
    def __init__(self):
        self.selected = (1,)

    def curselection(self):
        return self.selected

    def selection_clear(self, _start, _end):
        self.selected = ()

    def selection_set(self, index):
        self.selected = (index,)


class App:
    def __init__(self):
        self.root = type("Root", (), {"after": lambda self, _delay, _fn: None})()
        self.kills = [type("Scene", (), {"time": x, "side": "BLUE", "victim": "A", "multikill": 1})()
                      for x in (10, 20)]
        self.lb_kills = Listbox()
        self.checked_kills = {0}
        self.players = [object()] * 10
        self.locked = None
        self.var_event_mode = Variable("キル")
        self.var_edit_mode = Variable("easy")
        self.source = None
        self.var_camera_control_mode = Variable("固定視点＋自動構図補正")
        self.var_camera_side = Variable("BLUE")
        self.var_style = Variable("Cinematic")
        self.sl = {"third_dist": Variable(900)}
        self.var_work_frame = Variable("No.083")
        self.var_work_effect = Variable("FX")
        self.var_work_review = Variable(False)
        self.var_work_strength = Variable("strong")
        self.var_kill_icon_motion = Variable("一気に表示")
        self.var_mirror = Variable(True)
        self.var_live = Variable(True)
        self.var_preview_hz = Variable("144 Hz")
        self._mirror_present_rate = type("Rate", (), {"fps": lambda self: 96.5})()
        self.busy = False
        self.out_root = Path("out")
        self.var_fps_ui = Variable("60 FPS")
        self.var_encoder_policy = Variable("自動（NVENC優先・失敗時CPU）")
        self.var_gaudio = Variable(True)
        self.var_hud_mode = Variable("hidden")


class Audit29RuntimeTests(unittest.TestCase):
    def test_missing_detail_references_have_explicit_derived_views(self):
        self.assertEqual(set(DERIVED_DETAILS), {"testA", "legacy02", "legacy05"})
        self.assertEqual(len(SCREENS), 16)
        for family, (_, _, main_id, _) in DERIVED_DETAILS.items():
            html = render_detail(family, "test-token")
            self.assertIn("原画像未提供・比較用派生詳細", html)
            self.assertIn(f"window.AUTOCINE_SCREEN='{main_id}'", html)
            for action in ("scan", "camera_mode", "frame", "effect_strength",
                           "motion", "native_editor_zone", "export_menu"):
                if action == "frame":
                    self.assertIn('data-ui="material-card-0"', html)
                else:
                    self.assertIn(f'data-action="{action}"', html)
            self.assertIn('data-compare="main"', html)
            self.assertIn('data-compare="material"', html)
        for family in ("legacy02", "legacy03", "legacy05", "testA"):
            material = render_material(family, "test-token")
            self.assertIn('data-ui="material-card-0"', material)
            self.assertIn('data-compare="detail"', material)

    def test_derived_detail_route_reuses_runtime_client_and_requires_token(self):
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            server = UI29Server(App(), Path(directory) / "workspace.json")
            root = f"http://127.0.0.1:{server.http.server_port}"
            try:
                for family in DERIVED_DETAILS:
                    with urlopen(f"{root}/compare/detail/{family}?token={server.token}", timeout=5) as response:
                        html = response.read().decode("utf-8")
                    self.assertIn(f"window.AUTOCINE_DERIVED_DETAIL='{family}'", html)
                    self.assertIn("/runtime/client.js", html)
                for family in ("legacy02", "legacy03", "legacy05", "testA"):
                    with urlopen(f"{root}/compare/material/{family}?token={server.token}", timeout=5) as response:
                        self.assertIn("素材を選択", response.read().decode("utf-8"))
                with self.assertRaises(HTTPError) as denied:
                    urlopen(f"{root}/compare/detail/legacy02", timeout=5)
                self.assertEqual(denied.exception.code, 403)
                for route in ("/compare/detail/researchB", "/compare/material/researchB",
                              "/ui/R-A-main", "/static/A_main.png"):
                    with self.assertRaises(HTTPError) as excluded:
                        urlopen(f"{root}{route}?token={server.token}", timeout=5)
                    self.assertEqual(excluded.exception.code, 404)
            finally:
                server.close()

    def test_all_candidates_remain_distinct(self):
        self.assertEqual(len(SCREENS), 16)
        self.assertEqual(len({screen["family"] for screen in SCREENS.values()}), 7)

    def test_gui_qa_uses_isolated_comparison_preference_file(self):
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            isolated = Path(directory) / "qa_preferences.json"
            with patch.dict("os.environ", {"AUTOCINE_UI_COMPARE_PREFS": str(isolated)}):
                self.assertEqual(default_preferences_path(), isolated)

    def test_compact_test_b_screen_keeps_real_controls(self):
        html = render_legacy(SCREENS["T-B-S"])
        self.assertEqual(html.count('class="testb-compact-frame"'), 4)
        self.assertIn('data-action="camera_mode" data-action-value="fixed_auto"', html)
        self.assertIn('data-setting="third_yaw" type="number"', html)
        self.assertIn('data-action="screen" data-action-value="T-B-F"', html)
        self.assertIn('キル選択タイムライン', html)

    def test_hybrid_detail_frame_tab_opens_same_candidate_material(self):
        html = render_legacy(SCREENS["L03-D"])
        self.assertIn('<button data-compare="material">フレーム</button>', html)

    def test_switch_and_theme_preserve_model(self):
        app = App()
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            path = Path(directory) / "workspace.json"
            runtime = Audit29Runtime(app, path)
            for screen_id in SCREENS:
                runtime.perform("screen", {"id": screen_id})
            runtime.perform("theme", {"value": "dark"})
            self.assertEqual(app.lb_kills.curselection(), (1,))
            self.assertEqual(app.checked_kills, {0})
            self.assertEqual(app.sl["third_dist"].get(), 900)
            self.assertTrue(app.var_mirror.get())
            self.assertEqual(Audit29Runtime(app, path).screen_id, screen_id)
            self.assertEqual(Audit29Runtime(app, path).theme, "dark")

    def test_unimplemented_engage_is_explicit(self):
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(App(), Path(directory) / "workspace.json")
            with self.assertRaises(NotImplementedError):
                runtime.perform("engage")
            self.assertFalse(runtime.snapshot()["capabilities"]["engage"])

    def test_camera_side_and_motion_use_existing_labels(self):
        app = App()
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(app, Path(directory) / "workspace.json")
            runtime.perform("camera_side", {"value": "RED"})
            runtime.perform("motion", {"value": "slide_left"})
            self.assertEqual(app.var_camera_side.get(), "レッド側基準")
            self.assertEqual(app.var_kill_icon_motion.get(), "左から登場")

    def test_legacy_library_uses_real_catalog_and_shared_frame_action(self):
        app = App()
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(app, Path(directory) / "workspace.json")
            frame = runtime.snapshot()["frame"]
            self.assertEqual(len(frame["cards"]), 4)
            self.assertEqual(len(frame["library_cards"]), 6)
            self.assertEqual(len({card["id"] for card in frame["library_cards"]}), 6)
            self.assertEqual({card["status"] for card in frame["library_cards"]},
                             {"review", "approved"})
            chosen = frame["library_cards"][1]["id"]
            with patch("ui.audit29_runtime.select_frame_with_effect") as select:
                runtime.perform("frame", {"id": chosen})
            select.assert_called_once_with(app, chosen)

    def test_scene_edit_buttons_dispatch_to_existing_project(self):
        app = App()
        called = []
        app.on_save_scene = lambda: called.append("save")
        app.on_scene_undo = lambda: called.append("undo")
        app.on_scene_redo = lambda: called.append("redo")
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(app, Path(directory) / "workspace.json")
            for action in ("scene_save", "scene_undo", "scene_redo"):
                runtime.perform(action)
            self.assertEqual(called, ["save", "undo", "redo"])
            app.lb_kills.selected = ()
            with self.assertRaisesRegex(ValueError, "シーンを選択"):
                runtime.perform("scene_save")
            self.assertEqual(called, ["save", "undo", "redo"])

    def test_edit_mode_reuses_native_workspace_state(self):
        app = App()
        called = []
        app.root.deiconify = lambda: called.append("show")
        app.root.lift = lambda: called.append("raise")
        app._apply_edit_mode = lambda **_kwargs: called.append(app.var_edit_mode.get())
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(app, Path(directory) / "workspace.json")
            runtime.perform("edit_mode", {"value": "advanced"})
            self.assertEqual(runtime.snapshot()["edit_mode"], "advanced")
            runtime.perform("edit_mode", {"value": "easy"})
            self.assertEqual(called, ["advanced", "show", "raise", "easy"])
            with self.assertRaises(ValueError):
                runtime.perform("edit_mode", {"value": "unknown"})

    def test_comparison_navigation_does_not_raise_native_window(self):
        app = App()
        called = []
        app.root.deiconify = lambda: called.append("show")
        app.root.lift = lambda: called.append("raise")
        app._apply_edit_mode = lambda **_kwargs: called.append(app.var_edit_mode.get())
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            runtime = Audit29Runtime(app, Path(directory) / "workspace.json")
            runtime.perform("comparison_edit_mode", {"value": "advanced"})
            runtime.perform("comparison_edit_mode", {"value": "easy"})
        self.assertEqual(called, ["advanced", "easy"])

    def test_connect_uses_existing_replay_handler(self):
        app = App()
        called = []
        app.on_connect = lambda: called.append("connect")
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            Audit29Runtime(app, Path(directory) / "workspace.json").perform("connect")
        self.assertEqual(called, ["connect"])

    def test_mirror_route_reuses_jpeg_and_reports_new_frames(self):
        app = App()
        app._preview_presented = (1, (Image.new("RGB", (16, 9), "red"), None))
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            server = UI29Server(app, Path(directory) / "workspace.json")
            # This fake App has no Tk event loop. The route's read-only image
            # callback can be dispatched directly for a deterministic test.
            server.dispatcher.call = lambda fn, **_kwargs: fn()
            url = f"http://127.0.0.1:{server.http.server_port}/api/frame.jpg?token={server.token}"
            try:
                with urlopen(url, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers["Content-Type"], "image/jpeg")
                    first_tag = response.headers["ETag"]
                    self.assertTrue(response.read().startswith(b"\xff\xd8"))
                with self.assertRaises(HTTPError) as unchanged:
                    urlopen(Request(url, headers={"If-None-Match": first_tag}), timeout=5)
                self.assertEqual(unchanged.exception.code, 304)
                app._preview_presented = (2, (Image.new("RGB", (16, 9), "blue"), None))
                with urlopen(Request(url, headers={"If-None-Match": first_tag}), timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertNotEqual(response.headers["ETag"], first_tag)
            finally:
                server.close()

    def test_local_server_uses_editable_source_and_reconstructs_old_screens(self):
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            server = UI29Server(App(), Path(directory) / "workspace.json")
            try:
                with urlopen(server.url, timeout=5) as response:
                    chooser = response.read().decode("utf-8")
                self.assertIn('比較対象は7案です', chooser)
                self.assertLess(chooser.index('T-B-M'), chooser.index('L02-M'))
                self.assertNotIn('R-A-main', chooser)
                server.runtime.select_screen("R-E-main")
                with urlopen(server.url, timeout=5) as response:
                    html = response.read().decode("utf-8")
                self.assertIn('data-ui="preview-panel"', html)
                self.assertIn('/runtime/client.js', html)
                self.assertNotIn('<script src="ui.js"></script>', html)
                server.runtime.select_screen("T-A-M")
                with urlopen(server.url, timeout=5) as response:
                    legacy_html = response.read().decode("utf-8")
                self.assertIn('data-ui="prepare"', legacy_html)
                self.assertIn('data-ui="scene-list"', legacy_html)
                self.assertIn('/static/legacy/legacy.css', legacy_html)
                screen_rows = server.runtime.snapshot()["workspace"]["screens"]
                self.assertTrue(next(row for row in screen_rows if row["id"] == "T-A-M")["implemented"])
                for old_id in ("L02-M", "L03-N", "L03-D", "L05-M", "L06-L", "L06-E",
                               "T-B-M", "T-B-S", "T-B-C", "T-B-F"):
                    server.runtime.select_screen(old_id)
                    with urlopen(server.url, timeout=5) as response:
                        reconstructed = response.read().decode("utf-8")
                    self.assertIn('data-ui="preview-stage"', reconstructed)
                    self.assertIn('data-ui="timeline"', reconstructed)
                    self.assertIn('/static/legacy/reconstructed.css', reconstructed)
                    self.assertIn('/runtime/client.js', reconstructed)
                    self.assertNotIn('<script src="ui.js"></script>', reconstructed)
                    if old_id in {"L03-N", "L03-D"}:
                        self.assertIn('data-action-value="L03-N"', reconstructed)
                        self.assertIn('data-action-value="L03-D"', reconstructed)
                    if old_id == "T-B-M":
                        self.assertEqual(reconstructed.count('data-ui="scene-card-'), 6)
                        self.assertIn('data-action-value="fixed_auto"', reconstructed)
                        self.assertIn('data-action-value="third_cinema"', reconstructed)
                        self.assertIn('data-action-value="BLUE"', reconstructed)
                        self.assertIn('data-action-value="RED"', reconstructed)
                        self.assertIn('class="film-placeholder"', reconstructed)
                    if old_id == "T-B-C":
                        self.assertEqual(reconstructed.count('data-ui="scene-card-'), 6)
                        self.assertEqual(reconstructed.count('data-action="camera_style"'), 10)
                        for key in ("third_dist", "cam_height", "third_yaw",
                                    "motion_arc", "motion_dolly"):
                            self.assertIn(f'data-setting="{key}"', reconstructed)
                        self.assertIn('data-action="camera_qa"', reconstructed)
                        self.assertIn('data-action-value="auto"', reconstructed)
                    if old_id == "T-B-F":
                        self.assertEqual(reconstructed.count('data-ui="scene-card-'), 6)
                        self.assertEqual(reconstructed.count('data-ui="material-card-'), 3)
                        self.assertEqual(reconstructed.count('class="motion"'), 6)
                        self.assertIn('data-action="apply_selected_frame"', reconstructed)
                        self.assertIn('data-action-value="T-B-C"', reconstructed)
                    if old_id.startswith("T-B-"):
                        for target in ("T-B-M", "T-B-S", "T-B-C", "T-B-F"):
                            self.assertIn(f'data-action-value="{target}"', reconstructed)
                    self.assertTrue(next(row for row in server.runtime.snapshot()["workspace"]["screens"]
                                         if row["id"] == old_id)["implemented"])
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
