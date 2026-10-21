"""Local-only browser presentation of audited HTML, backed by one Tk App.

This is an opt-in implementation slice for the new research screens. Old
screens have no HTML source and are not silently mapped to these layouts.
"""
from __future__ import annotations

from concurrent.futures import Future
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import mimetypes
from pathlib import Path
import queue
import secrets
import threading
from urllib.parse import unquote, urlparse

from ui.audit29_runtime import Audit29Runtime, DEFAULT_SCREEN, SCREENS


DESIGN = Path(__file__).resolve().parents[1] / "design" / "ui" / "ui_rethink_20261021"
CLIENT = Path(__file__).with_name("audit29_client.js")


class TkDispatcher:
    def __init__(self, root):
        self.root = root
        self.queue = queue.Queue()
        self.running = True
        root.after(20, self._drain)

    def _drain(self):
        if not self.running:
            return
        for _ in range(32):
            try:
                fn, future = self.queue.get_nowait()
            except queue.Empty:
                break
            try:
                future.set_result(fn())
            except Exception as exc:
                future.set_exception(exc)
        self.root.after(20, self._drain)

    def call(self, fn):
        future = Future()
        self.queue.put((fn, future))
        return future.result(timeout=30)


class UI29Server:
    def __init__(self, app):
        self.app = app
        self.runtime = Audit29Runtime(app)
        if "html" not in SCREENS[self.runtime.screen_id]:
            # Keep the last explicit choice on disk while the raster-only
            # candidate is still being reconstructed in the browser UI.
            self.runtime.screen_id = DEFAULT_SCREEN
        self.token = secrets.token_urlsafe(24)
        self.dispatcher = TkDispatcher(app.root)
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), self._handler_type())
        self.thread = threading.Thread(target=self.http.serve_forever, name="ui29-http", daemon=True)
        self.thread.start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.http.server_port}/ui/{self.runtime.screen_id}?token={self.token}"

    def close(self):
        self.http.shutdown()
        self.dispatcher.running = False

    def _handler_type(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, _format, *_args):
                pass

            def _authorized(self):
                from urllib.parse import parse_qs
                parsed = urlparse(self.path)
                return parse_qs(parsed.query).get("token", [None])[0] == owner.token

            def _send(self, code, data: bytes, content_type="application/json; charset=utf-8"):
                self.send_response(code)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _json(self, code, data):
                self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"))

            def do_GET(self):
                path = unquote(urlparse(self.path).path)
                if not self._authorized() and not path.startswith("/static/"):
                    return self._json(403, {"error": "forbidden"})
                if path == "/api/state":
                    try:
                        return self._json(200, owner.dispatcher.call(owner.runtime.snapshot))
                    except Exception as exc:
                        return self._json(500, {"error": str(exc)})
                if path == "/api/frame.jpg":
                    def get_frame():
                        result = getattr(owner.app, "_preview_presented", None)
                        if result is None or not owner.app.var_mirror.get():
                            return None
                        image = result[1][0]
                        stream = io.BytesIO()
                        image.convert("RGB").save(stream, format="JPEG", quality=86)
                        return stream.getvalue()
                    try:
                        content = owner.dispatcher.call(get_frame)
                    except Exception:
                        content = None
                    return self._send(200, content, "image/jpeg") if content else self._send(404, b"")
                if path == "/runtime/client.js":
                    return self._send(200, CLIENT.read_bytes(), "text/javascript; charset=utf-8")
                if path.startswith("/ui/"):
                    screen_id = path[4:]
                    screen = SCREENS.get(screen_id)
                    if screen is None:
                        return self._json(404, {"error": "unknown screen"})
                    if "html" not in screen:
                        return self._json(501, {"error": "旧画面の編集可能なHTMLは監査資料にありません。再構成は未完了です", "screen_id": screen_id})
                    source = DESIGN / screen["html"]
                    html = source.read_text(encoding="utf-8")
                    html = html.replace('<script src="ui.js"></script>',
                        f'<script>window.AUTOCINE_TOKEN={json.dumps(owner.token)};'
                        f'window.AUTOCINE_SCREEN={json.dumps(screen_id)};</script>'
                        '<script src="/runtime/client.js?token=' + owner.token + '"></script>')
                    html = html.replace('href="ui.css"', f'href="/static/ui.css?token={owner.token}"')
                    html = html.replace('src="assets/', f'src="/static/assets/')
                    return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
                if path.startswith("/static/"):
                    source = (DESIGN / path[len("/static/"):]).resolve()
                    if not source.is_relative_to(DESIGN.resolve()) or not source.is_file():
                        return self._json(404, {"error": "missing asset"})
                    mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
                    return self._send(200, source.read_bytes(), mime)
                return self._json(404, {"error": "not found"})

            def do_POST(self):
                if not self._authorized() or urlparse(self.path).path != "/api/action":
                    return self._json(403, {"error": "forbidden"})
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length > 8192:
                        raise ValueError("request too large")
                    body = json.loads(self.rfile.read(length))
                    action = str(body["action"])
                    payload = body.get("data") or {}
                    result = owner.dispatcher.call(lambda: owner.runtime.perform(action, payload))
                    return self._json(200, result)
                except (ValueError, KeyError, NotImplementedError) as exc:
                    return self._json(422, {"error": str(exc)})
                except Exception as exc:
                    return self._json(500, {"error": str(exc)})

        return Handler
