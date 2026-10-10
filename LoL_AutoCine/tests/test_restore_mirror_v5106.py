# -*- coding: utf-8 -*-
"""Regression tests for the mirror camera being left underground after export."""
from __future__ import annotations
import unittest
from types import SimpleNamespace

from core.jobs import restore_mirror_camera
from core.replay_api import ReplayApiError


class DummyReplay:
    def __init__(self, fail_first=False):
        self.calls = []
        self.fail_first = fail_first

    def set_playback(self, **kwargs):
        self.calls.append(("playback", kwargs))

    def set_render(self, **kwargs):
        self.calls.append(("render", kwargs))
        if self.fail_first:
            self.fail_first = False
            raise ReplayApiError("temporary error")


class TestSafeCameraReset(unittest.TestCase):
    def test_restores_top_mode_and_attached_target_together(self):
        api = DummyReplay()
        player = SimpleNamespace(selection_name="LeeSin", champion="リー・シン")
        messages = []
        restore_mirror_camera(api, player, 45, messages.append)
        self.assertEqual(api.calls[0], ("playback", {"paused": True, "speed": 1.0}))
        payload = api.calls[1][1]
        self.assertEqual(payload["cameraMode"], "top")
        self.assertTrue(payload["cameraAttached"])
        self.assertEqual(payload["selectionName"], "LeeSin")
        self.assertEqual(payload["selectionOffset"], {"x": 0, "y": 0, "z": 0})
        self.assertEqual(payload["fieldOfView"], 45)
        self.assertTrue(any("ミラー復帰" in m for m in messages))

    def test_fallback_still_switches_to_top(self):
        api = DummyReplay(fail_first=True)
        restore_mirror_camera(api, SimpleNamespace(selection_name="", champion="Ahri"), 50)
        self.assertEqual(api.calls[-1][1], {"cameraMode": "top", "cameraAttached": True})

    def test_export_code_releases_camera_before_audio_check(self):
        import inspect
        import core.jobs as jobs
        body = inspect.getsource(jobs.record_one_clip)
        self.assertLess(body.index("restore_mirror_camera(api, player"),
                        body.index('if audio is not None:', body.index("director.stop()")))
        self.assertNotIn('api.set_render(fieldOfView=plan.base_fov, selectionOffset=', body)

    def test_preview_has_restore_in_finally(self):
        import inspect
        import core.jobs as jobs
        body = inspect.getsource(jobs.preview_clip)
        self.assertIn('restore_mirror_camera(api, player, plan.base_fov, log)', body)


if __name__ == "__main__":
    unittest.main()
