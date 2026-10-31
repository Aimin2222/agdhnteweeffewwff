"""Standalone Windows UI study for candidates 8–10.

This process serves only its bundled mock files to an embedded WebView2
window. It never imports or starts the AutoCine replay, capture or GPU code.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading


HERE = Path(__file__).resolve().parent
WEB = (Path(sys._MEIPASS) / "work_ui_web") if getattr(sys, "frozen", False) else HERE / "web"


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        pass

    def end_headers(self) -> None:
        # The research data must remain a self-contained local experience.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


def start_local_server() -> tuple[ThreadingHTTPServer, str]:
    if not (WEB / "index.html").is_file():
        raise FileNotFoundError(f"Standalone UI files are missing: {WEB}")
    handler = partial(QuietStaticHandler, directory=str(WEB))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, name="work-ui-local", daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/index.html?layout=hybrid"


def configure_fixed_runtime(webview: object) -> None:
    if not getattr(sys, "frozen", False):
        return
    fixed = Path(sys.executable).resolve().parent / "WebView2Fixed"
    if (fixed / "msedgewebview2.exe").is_file():
        webview.settings["WEBVIEW2_RUNTIME_PATH"] = str(fixed)


def main() -> int:
    if "--capture-all" in sys.argv:
        from qa_capture import main as capture_main
        return capture_main(sys.argv[sys.argv.index("--capture-all") + 1:])
    if "--qa-interaction" in sys.argv:
        from qa_interaction import main as interaction_main
        return interaction_main(sys.argv[sys.argv.index("--qa-interaction") + 1:])

    import webview

    configure_fixed_runtime(webview)
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    server, url = start_local_server()
    try:
        webview.create_window("LoL AutoCine — 候補8〜10", url,
                              width=1600, height=900, min_size=(1100, 700),
                              resizable=True)
        webview.start(gui="edgechromium", private_mode=True, debug=False)
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
