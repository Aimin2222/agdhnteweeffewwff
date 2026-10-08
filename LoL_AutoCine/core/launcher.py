# -*- coding: utf-8 -*-
"""クライアント(LCU)経由で .rofl を再生する。lockfile から自動認証するのでAPIキー入力は不要。"""
from __future__ import annotations
import base64
import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional

from .paths import read_lockfile


def _lcu(lol_dir: Path, method: str, path: str, body: Optional[dict] = None):
    lf = read_lockfile(lol_dir)
    if not lf:
        raise RuntimeError("LoLクライアントが起動していません (lockfile が見つかりません)。")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    auth = base64.b64encode(f"riot:{lf['password']}".encode()).decode()
    req = urllib.request.Request(
        f"https://127.0.0.1:{lf['port']}{path}", method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
    with opener.open(req, timeout=5) as r:
        raw = r.read()
    return json.loads(raw) if raw else None


def watch_replay(lol_dir: Optional[Path], rofl: Path) -> str:
    """LCU で再生。失敗したら Windows の関連付けで開く。戻り値は使った方法。"""
    rofl = Path(rofl)
    if not rofl.exists():
        raise FileNotFoundError(f"リプレイファイルが見つかりません: {rofl}")
    if lol_dir is not None:
        try:
            _lcu(lol_dir, "POST", f"/lol-replays/v1/rofls/{rofl.stem}/watch", {"componentType": "replay-button"})
            return "LCU"
        except Exception:
            pass
    if sys.platform == "win32":
        os.startfile(str(rofl))  # type: ignore[attr-defined]
        return "関連付け起動"
    raise RuntimeError("リプレイを起動できませんでした。")
