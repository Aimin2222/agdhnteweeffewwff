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
from urllib.parse import parse_qs, unquote, urlparse

from ui.audit29_runtime import Audit29Runtime, SCREENS, LEGACY_RECONSTRUCTIONS


DESIGN = Path(__file__).resolve().parents[1] / "design" / "ui" / "ui_rethink_20261021"
LEGACY_DESIGN = Path(__file__).resolve().parents[1] / "design" / "ui" / "ui29_legacy"
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

    def call(self, fn, *, timeout=30):
        future = Future()
        self.queue.put((fn, future))
        return future.result(timeout=timeout)


class UI29Server:
    def __init__(self, app, preferences_path: Path | None = None):
        self.app = app
        self.runtime = Audit29Runtime(app, preferences_path)
        self.token = secrets.token_urlsafe(24)
        self.dispatcher = TkDispatcher(app.root)
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), self._handler_type())
        self.thread = threading.Thread(target=self.http.serve_forever, name="ui29-http", daemon=True)
        self.thread.start()

    @property
    def url(self):
        route = (f"/ui/{self.runtime.screen_id}"
                 if self.runtime.screen_id and ("html" in SCREENS[self.runtime.screen_id]
                                                or self.runtime.screen_id in LEGACY_RECONSTRUCTIONS)
                 else "/choose")
        return f"http://127.0.0.1:{self.http.server_port}{route}?token={self.token}"

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
                if path == "/choose":
                    families = {}
                    for row in SCREENS.values():
                        families.setdefault(row["family"], row)
                    buttons = "".join(
                        f'<button data-id="{row["id"]}" {"" if "html" in row or row["id"] in LEGACY_RECONSTRUCTIONS else "disabled"}>'
                        f'{row["family_name"]} <small>{row["id"]}</small>'
                        f'{"" if "html" in row or row["id"] in LEGACY_RECONSTRUCTIONS else " — 再構成中"}</button>'
                        for row in families.values())
                    html = '''<!doctype html><html lang="ja"><meta charset="utf-8">
<title>AutoCine UI候補を選ぶ</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font:16px "Yu Gothic UI",Meiryo,sans-serif;background:#eef1f4;color:#172b3e;margin:0}
main{max-width:980px;margin:5vh auto;padding:26px;background:#f8fafc;border-radius:12px}
h1{margin:0 0 8px}p{color:#465a6f}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:22px}
button{min-height:72px;padding:14px;border:1px solid #6c7d90;border-radius:8px;background:#fff;text-align:left;font:inherit;cursor:pointer}
button:hover:not(:disabled){border:2px solid #245fab;background:#d7e6fc}button:disabled{opacity:.6;cursor:not-allowed}
small{display:block;color:#465a6f}#status{min-height:24px;color:#a33}</style>
<main><h1>LoL AutoCine — UI比較候補</h1><p>12候補・29画面は未採用です。選択してもシーンやカメラ設定を初期化しません。</p>
<p>旧11画面は順次再構成中。旧テストAと新A〜Fは共通Appへ接続し、未接続機能を明示します。</p>
<section>''' + buttons + '''</section><p id="status"></p></main><script>
const token=''' + json.dumps(owner.token) + ''';
document.querySelectorAll('button[data-id]:not(:disabled)').forEach(button=>button.onclick=async()=>{
 const id=button.dataset.id;
 try{const r=await fetch('/api/action?token='+encodeURIComponent(token),{method:'POST',
 headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'screen',data:{id}})});
 if(!r.ok)throw new Error((await r.json()).error||'画面切替失敗');
 location.assign('/ui/'+encodeURIComponent(id)+'?token='+encodeURIComponent(token));
 }catch(e){document.querySelector('#status').textContent=e.message}
});</script></html>'''
                    return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
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
                if path.startswith("/api/asset/"):
                    try:
                        from core.work_kill_assets import resolve_asset
                        _, source = resolve_asset(path[len("/api/asset/"):], kind="frames", review=True)
                        return self._send(200, source.read_bytes(), "image/png")
                    except (ValueError, OSError):
                        return self._json(404, {"error": "unknown audited asset"})
                if path == "/runtime/client.js":
                    return self._send(200, CLIENT.read_bytes(), "text/javascript; charset=utf-8")
                if path.startswith("/ui/"):
                    screen_id = path[4:]
                    screen = SCREENS.get(screen_id)
                    if screen is None:
                        return self._json(404, {"error": "unknown screen"})
                    if "html" not in screen and screen_id not in LEGACY_RECONSTRUCTIONS:
                        return self._json(501, {"error": "旧画面の編集可能なHTMLは監査資料にありません。再構成は未完了です", "screen_id": screen_id})
                    source = ((LEGACY_DESIGN / LEGACY_RECONSTRUCTIONS[screen_id])
                              if screen_id in LEGACY_RECONSTRUCTIONS else DESIGN / screen["html"])
                    html = source.read_text(encoding="utf-8")
                    html = html.replace('<script src="ui.js"></script>',
                        f'<script>window.AUTOCINE_TOKEN={json.dumps(owner.token)};'
                        f'window.AUTOCINE_SCREEN={json.dumps(screen_id)};</script>'
                        '<script src="/runtime/client.js?token=' + owner.token + '"></script>')
                    html = html.replace('href="ui.css"', f'href="/static/ui.css?token={owner.token}"')
                    html = html.replace('href="legacy.css"', f'href="/static/legacy/legacy.css?token={owner.token}"')
                    html = html.replace('src="assets/', f'src="/static/assets/')
                    if parse_qs(urlparse(self.path).query).get("measure") == ["1"]:
                        # Read-only DOM bounds for reproducible offline layout QA.
                        measurement = '''<script>setTimeout(() => {
const boxes = {};
document.querySelectorAll('[data-ui]').forEach(element => {
 const rect = element.getBoundingClientRect();
 boxes[element.dataset.ui] = [rect.x, rect.y, rect.width, rect.height];
});
const footer = document.querySelector('footer');
if (footer) {
 const rect = footer.getBoundingClientRect();
 boxes['footer-' + Object.keys(boxes).length] = [rect.x, rect.y, rect.width, rect.height];
}
const result = document.createElement('script');
result.type = 'application/json'; result.id = 'ui29-bounds';
result.textContent = JSON.stringify(boxes); document.body.append(result);
}, 900);</script>'''
                        html = html.replace("</body>", measurement + "</body>")
                    return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
                if path.startswith("/static/"):
                    static_path = path[len("/static/"):]
                    base = LEGACY_DESIGN if static_path.startswith("legacy/") else DESIGN
                    relative = static_path[len("legacy/"):] if base == LEGACY_DESIGN else static_path
                    source = (base / relative).resolve()
                    if not source.is_relative_to(base.resolve()) or not source.is_file():
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
                    # Native file dialogs legitimately stay open while a user chooses a path.
                    # Do not report a false HTTP failure after the default 30-second wait.
                    dialog_actions = {"open_replay", "project_export", "project_import", "output_folder"}
                    result = owner.dispatcher.call(lambda: owner.runtime.perform(action, payload),
                                                   timeout=None if action in dialog_actions else 30)
                    return self._json(200, result)
                except (ValueError, KeyError, NotImplementedError) as exc:
                    return self._json(422, {"error": str(exc)})
                except Exception as exc:
                    return self._json(500, {"error": str(exc)})

        return Handler
