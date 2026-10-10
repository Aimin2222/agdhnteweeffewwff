"""v5.10.4: tab scrolling, live DOF during camera playback and slow-API camera safety."""
from types import SimpleNamespace
import numpy as np
import pytest
import tkinter as tk

from core.camera import limit_camera_post


@pytest.fixture
def gui(tmp_path, monkeypatch):
    import legacy_app
    monkeypatch.setattr(legacy_app, 'SETTINGS', tmp_path / 'settings.json')
    root=tk.Tk(); root.geometry('1480x980')
    app=legacy_app.App(root)
    app.var_edit_mode.set('advanced')
    app._apply_edit_mode(log=False)
    app.var_editor_zone.set('color')
    app._apply_editor_zone()
    root.update()
    yield app, root
    root.destroy()


def test_advanced_notebook_wheel_does_not_switch_tab(gui):
    app, root = gui
    nb=app._editor_advanced_tabs
    assert nb.winfo_class() == 'TNotebook'
    assert root.bind_class('TNotebook', '<MouseWheel>')
    nb.select(1)  # Color FX
    root.update()
    before=nb.select()
    for key, kw in [('<MouseWheel>', {'delta': -120}), ('<MouseWheel>', {'delta': 120}),
                    ('<Button-4>',{}),('<Button-5>',{})]:
        nb.event_generate(key, **kw)
        root.update()
        assert nb.select() == before, f'wheeling switched {key}'
    nb.select(2)  # Clicking the intended tab (select API) is still allowed.
    assert nb.index('current') == 2


def test_live_fx_draw_during_camera_preview_only(gui, monkeypatch):
    import legacy_app
    app, root=gui
    requests=[]
    app.source=SimpleNamespace(running=True)
    monkeypatch.setattr(app._live_preview, 'submit', lambda key, request: requests.append(request))
    app.var_live.set(True)
    app.busy=True
    app._preview_fx_during_camera=True
    app._preview_tick()
    assert requests[-1][3] is not None
    app._preview_fx_during_camera=False
    app._preview_tick()
    assert requests[-1][3] is None, 'No expensive FX should be requested during export'
    app.busy=False
    app._preview_tick()
    assert requests[-1][3] is not None
    app.var_live.set(False)
    app._preview_tick()
    assert requests[-1][3] is None


def test_render_rate_limiter_only_when_api_slow():
    prev={'fieldOfView': 60.0, 'selectionOffset': {'x':0,'y':446,'z':0},
          'cameraRotation': {'x':0,'y':170,'z':0}, 'selectionName':'Hero'}
    goal={'fieldOfView': 30.0, 'selectionOffset': {'x':100,'y':446,'z':900},
          'cameraRotation': {'x':0,'y':-165,'z':0}, 'selectionName':'Hero'}
    assert limit_camera_post(goal,prev,.1,slow_api=False) is goal
    assert limit_camera_post(goal,None,.1,slow_api=True) is goal
    value=limit_camera_post(goal,prev,.1,slow_api=True)
    assert value['fieldOfView']==pytest.approx(57.8)
    assert value['selectionOffset']['y']==pytest.approx(446)
    assert np.linalg.norm([value['selectionOffset']['x'],value['selectionOffset']['z']])<=42.01
    assert value['cameraRotation']['y'] == pytest.approx(174.2) # wrap +25 degrees
    assert value['selectionName']=='Hero'
    assert goal['selectionOffset']['z']==900  # no mutation


def test_render_limiter_bounds_both_directions_and_no_coordinate_changes():
    prev={'cameraRotation':{'y':-179.0},'selectionOffset':{'x':0,'y':446,'z':100},'fieldOfView':45}
    goal={'cameraRotation':{'y':179.0},'selectionOffset':{'x':0,'y':446,'z':0},'fieldOfView':60}
    limited=limit_camera_post(goal,prev,.05,slow_api=True)
    assert limited['cameraRotation']['y']==pytest.approx(-181.0)
    assert limited['selectionOffset']['z']==pytest.approx(79.0)
    assert limited['fieldOfView']==pytest.approx(46.1)


def test_replay_http11_connection_reused_for_camera_requests():
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from core.replay_api import ReplayAPI
    counts={'connections':0, 'requests':0}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        def log_message(self, *args): pass
        def setup(self):
            super().setup()
            counts['connections']+=1
        def do_GET(self):
            self.respond({'time':10.0,'paused':True})
        def do_POST(self):
            length=int(self.headers.get('Content-Length', '0'))
            if length:
                self.rfile.read(length)
            self.respond({})
        def respond(self, item):
            counts['requests']+=1
            blob=json.dumps(item).encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)
    srv=ThreadingHTTPServer(('127.0.0.1',0), Handler)
    thread=threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    api=ReplayAPI(f'http://127.0.0.1:{srv.server_address[1]}')
    try:
        assert api.playback()['time']==10.0
        api.set_render(fieldOfView=63)
        api.set_render(fieldOfView=65)
        assert api.playback()['time']==10.0
        assert counts['requests']==4
        assert counts['connections']==1, 'Camera stream should reuse a single HTTP/TCP socket'
    finally:
        api.close()
        srv.shutdown()
        srv.server_close()
