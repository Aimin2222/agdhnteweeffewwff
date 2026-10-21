"""Candidate and theme switches cannot reset the shared AutoCine model."""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
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

    def test_local_server_uses_editable_source_and_rejects_old_placeholder(self):
        server = UI29Server(App())
        try:
            with urlopen(server.url, timeout=5) as response:
                html = response.read().decode("utf-8")
            self.assertIn('data-ui="preview-panel"', html)
            self.assertIn('/runtime/client.js', html)
            self.assertNotIn('<script src="ui.js"></script>', html)
            with self.assertRaises(HTTPError) as error:
                urlopen(server.url.replace("R-A-main", "L02-M"), timeout=5)
            self.assertEqual(error.exception.code, 501)
        finally:
            server.close()


if __name__ == "__main__":
    unittest.main()
