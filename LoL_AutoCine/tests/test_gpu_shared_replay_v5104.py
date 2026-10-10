"""Real HTTP transport checks for shared UI/camera keep-alive integration."""
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from core.replay_api import ReplayAPI, ReplayApiError


@pytest.fixture
def replay_server():
    counts={'connections':0,'posts':0,'requests':0}
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.1'
        def setup(self):
            super().setup()
            counts['connections']+=1
        def log_message(self,*args): pass
        def do_GET(self):
            self.respond()
        def do_POST(self):
            counts['posts']+=1
            self.rfile.read(int(self.headers.get('Content-Length',0)))
            self.respond()
        def respond(self):
            counts['requests']+=1
            if self.path.endswith('/broken'):
                # A POST reached the server but its response was lost.
                self.close_connection=True
                return
            value=json.dumps({'path':self.path,'time':10}).encode()
            self.send_response(500 if self.path.endswith('/error') else 200)
            self.send_header('Content-Length',str(len(value)))
            if self.path.endswith('/close'):
                self.send_header('Connection','close')
                self.close_connection=True
            self.end_headers()
            self.wfile.write(value)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    api=ReplayAPI(f'http://127.0.0.1:{server.server_port}/replay',timeout=1)
    try:
        yield api,counts
    finally:
        api.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_keepalive_close_and_http_error_leave_next_request_usable(replay_server):
    api,counts=replay_server
    assert api.get('/close')['path']=='/replay/close'
    assert api.get('/next')['path']=='/replay/next'
    assert counts['connections']==2
    with pytest.raises(ReplayApiError,match='HTTP 500'):
        api.get('/error')
    assert api.get('/after_error')['path']=='/replay/after_error'
    assert counts['connections']==2


def test_broken_post_is_not_retried_and_connection_recovers(replay_server):
    api,counts=replay_server
    with pytest.raises(ReplayApiError):
        api.post('/broken',{'fieldOfView':60})
    assert counts['posts']==1, 'A lost response must not duplicate a camera command'
    assert api.get('/after_break')['time']==10
    assert counts['posts']==1 and counts['connections']==2


def test_concurrent_camera_queries_share_one_serialized_connection(replay_server):
    api,counts=replay_server
    with ThreadPoolExecutor(max_workers=4) as pool:
        values=list(pool.map(lambda i: api.get(f'/request/{i}'),range(12)))
    assert [v['path'] for v in values]==[f'/replay/request/{i}' for i in range(12)]
    assert counts['requests']==12 and counts['connections']==1
