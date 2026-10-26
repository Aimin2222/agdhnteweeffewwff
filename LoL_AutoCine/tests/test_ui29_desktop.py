"""The portable window must select an included WebView2 Fixed Version."""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui.audit29_desktop import _configure_webview2_runtime


class FixedRuntimeTests(unittest.TestCase):
    def test_bundled_runtime_is_selected_by_pywebview(self):
        with TemporaryDirectory(dir=ROOT) as temp:
            root = Path(temp)
            runtime = root / "WebView2Fixed"
            runtime.mkdir()
            (runtime / "msedgewebview2.exe").write_bytes(b"test executable marker")
            webview = SimpleNamespace(settings={})
            with patch.object(sys, "frozen", True, create=True), patch.object(
                    sys, "executable", str(root / "LoL_AutoCine_UI29.exe")):
                self.assertEqual(_configure_webview2_runtime(webview), runtime)
            self.assertEqual(webview.settings["WEBVIEW2_RUNTIME_PATH"], str(runtime))

    def test_system_runtime_setting_is_not_overridden_without_bundle(self):
        with TemporaryDirectory(dir=ROOT) as temp:
            webview = SimpleNamespace(settings={"WEBVIEW2_RUNTIME_PATH": None})
            with patch.object(sys, "frozen", True, create=True), patch.object(
                    sys, "executable", str(Path(temp) / "LoL_AutoCine_UI29.exe")):
                self.assertIsNone(_configure_webview2_runtime(webview))
            self.assertIsNone(webview.settings["WEBVIEW2_RUNTIME_PATH"])


if __name__ == "__main__":
    unittest.main()
