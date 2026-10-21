"""Candidate and theme switches cannot reset the shared AutoCine model."""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui.audit29_runtime import Audit29Runtime, SCREENS
from ui.audit29_server import UI29Server


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
    def test_all_candidates_remain_distinct(self):
        self.assertEqual(len(SCREENS), 29)
        self.assertEqual(len({screen["family"] for screen in SCREENS.values()}), 12)

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

    def test_connect_uses_existing_replay_handler(self):
        app = App()
        called = []
        app.on_connect = lambda: called.append("connect")
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            Audit29Runtime(app, Path(directory) / "workspace.json").perform("connect")
        self.assertEqual(called, ["connect"])

    def test_local_server_uses_editable_source_and_reconstructs_old_screens(self):
        with TemporaryDirectory(dir=ROOT / "qa") as directory:
            server = UI29Server(App(), Path(directory) / "workspace.json")
            try:
                with urlopen(server.url, timeout=5) as response:
                    chooser = response.read().decode("utf-8")
                self.assertIn('12候補・29画面は未採用', chooser)
                server.runtime.select_screen("R-A-main")
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
                    if old_id.startswith("T-B-"):
                        for target in ("T-B-M", "T-B-S", "T-B-C", "T-B-F"):
                            self.assertIn(f'data-action-value="{target}"', reconstructed)
                    self.assertTrue(next(row for row in server.runtime.snapshot()["workspace"]["screens"]
                                         if row["id"] == old_id)["implemented"])
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
