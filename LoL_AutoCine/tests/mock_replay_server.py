# -*- coding: utf-8 -*-
"""Replay API のモック。実機の挙動(特に eventdata が"現在時刻までのイベントのみ"を返す点)を再現する。"""
from __future__ import annotations
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CHAMPS = ["Ahri", "Jinx", "Thresh", "Lee Sin", "Garen", "Zed", "Lux", "Ezreal", "Leona", "Yasuo"]
NAMES = ["Taki", "Bob", "Cat", "Dan", "Eve", "Fay", "Gus", "Hal", "Ivy", "Jun"]


def make_players():
    out = []
    for i in range(10):
        out.append({
            "championName": CHAMPS[i], "rawChampionName": f"game_character_displayname_{CHAMPS[i].replace(' ', '')}",
            "isBot": False, "riotId": f"{NAMES[i]}#JP{i}", "riotIdGameName": NAMES[i], "riotIdTagLine": f"JP{i}",
            "summonerName": f"{NAMES[i]}#JP{i}", "team": "ORDER" if i < 5 else "CHAOS", "level": 10,
        })
    return out


def make_events():
    ev, eid = [{"EventID": 0, "EventName": "GameStart", "EventTime": 0.0}], 1

    def kill(t, killer, victim):
        nonlocal eid
        ev.append({"EventID": eid, "EventName": "ChampionKill", "EventTime": float(t),
                   "KillerName": killer, "VictimName": victim, "Assisters": []})
        eid += 1
    kill(10, "Taki#JP0", "Hal#JP7")
    kill(13, "Taki#JP0", "Ivy#JP8")     # ダブル
    kill(20, "Bob#JP1", "Jun#JP9")      # 他人のキル (混ざってはいけない)
    kill(30, "Taki", "Fay#JP5")         # 名前表記ゆれ (タグ無し)
    kill(40, "Gus#JP6", "Cat#JP2")      # 敵のキル
    kill(50, "Taki#JP0", "Gus#JP6")
    return ev


TOP_V = (0.0, 1800.0, -1300.0)           # 標準(俯瞰)カメラ: キャラ位置からの相対
TOP_ROT = {"x": 0.0, "y": -54.0, "z": 0.0}
HUD_KEYS = ["interfaceAll", "interfaceReplay", "interfaceScore", "interfaceScoreboard", "interfaceFrames",
            "interfaceMinimap", "interfaceTimeline", "interfaceChat", "interfaceTarget", "interfaceQuests",
            "interfaceAnnounce", "interfaceKillCallouts", "interfaceNeutralTimers", "healthBarChampions",
            "healthBarStructures", "healthBarWards", "healthBarPets", "healthBarMinions", "floatingText",
            "outlineSelect", "outlineHover"]


def champ_pos(sel: str):
    """selectionName -> キャラのワールド座標 (y=地面の高さ 60)。"""
    names = [c.replace(" ", "") for c in CHAMPS]
    i = names.index(sel) if sel in names else 0
    return (3000.0 + 500 * i, 60.0, 2000.0 + 300 * i)


class MockState:
    def __init__(self, length=60.0, stuck=False, fps_broken=False):
        self.length, self.stuck, self.fps_broken = length, stuck, fps_broken
        self.hud_log = []          # (time, interfaceAll) など HUD フラグの変化履歴
        self.cam_log = []          # 実効カメラ位置の履歴 (地面チェック用)
        self.time, self.speed, self.paused, self.seeking = 0.0, 1.0, True, False
        self.render = {"cameraMode": "top", "cameraAttached": False, "fieldOfView": 60.0,
                       "selectionName": "", "selectionOffset": {"x": 0, "y": 0, "z": 0},
                       "cameraRotation": dict(TOP_ROT), "cameraPosition": {"x": 0, "y": 0, "z": 0}}
        for k in HUD_KEYS:
            self.render[k] = True
        self.events = make_events()
        self.players = make_players()
        self.render_log = []
        self.speed_log = []
        self.lock = threading.Lock()
        self._stop = False
        self._th = threading.Thread(target=self._tick, daemon=True)

    def _tick(self):
        last = time.time()
        while not self._stop:
            time.sleep(0.01)
            now = time.time()
            with self.lock:
                if not self.paused and not self.stuck:
                    self.time = min(self.length, self.time + (now - last) * self.speed)
            last = now


def make_handler(st: MockState):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, obj, code=200):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            with st.lock:
                if self.path == "/replay/playback":
                    return self._send({"length": st.length, "paused": st.paused, "seeking": st.seeking,
                                       "speed": st.speed, "time": st.time})
                if self.path == "/replay/render":
                    r = dict(st.render)
                    if r.get("cameraAttached") and r.get("selectionName"):
                        P = champ_pos(r["selectionName"])
                        if r["cameraMode"] == "top":
                            pos = (P[0] + TOP_V[0], P[1] + TOP_V[1], P[2] + TOP_V[2])
                            r["cameraRotation"] = dict(TOP_ROT)
                        else:
                            o = r.get("selectionOffset") or {"x": 0, "y": 0, "z": 0}
                            if st.fps_broken:      # オフセットを無視してキャラの足元に置く(=地面に埋まる環境)
                                pos = P
                            else:
                                pos = (P[0] + o["x"], P[1] + o["y"], P[2] + o["z"])
                        r["cameraPosition"] = {"x": pos[0], "y": pos[1], "z": pos[2]}
                        st.cam_log.append((r["cameraMode"], pos[1] - P[1]))
                    return self._send(r)
                if self.path == "/liveclientdata/playerlist":
                    return self._send(st.players)
                if self.path == "/liveclientdata/eventdata":
                    return self._send({"Events": [e for e in st.events if e["EventTime"] <= st.time]})
            self._send({"error": "nf"}, 404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            with st.lock:
                if self.path == "/replay/playback":
                    if "time" in body:
                        st.time = float(body["time"])
                    if "speed" in body:
                        st.speed = float(body["speed"])
                        st.speed_log.append(st.speed)
                    if "paused" in body:
                        st.paused = bool(body["paused"])
                    return self._send({})
                if self.path == "/replay/render":
                    st.render.update(body)
                    st.render_log.append(dict(body))
                    if any(k in body for k in HUD_KEYS):
                        st.hud_log.append({k: st.render[k] for k in HUD_KEYS})
                    return self._send({})
            self._send({"error": "nf"}, 404)
    return H


def start_mock(length=60.0, stuck=False, fps_broken=False):
    st = MockState(length, stuck, fps_broken)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(st))
    st._th.start()
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def shutdown():
        st._stop = True
        srv.shutdown()
    return st, f"http://127.0.0.1:{srv.server_address[1]}", shutdown
