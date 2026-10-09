# -*- coding: utf-8 -*-
"""LoLのインストール先 / game.cfg / lockfile / リプレイ保存先の自動検出。

APIキーの入力は不要。game.cfg の [General] に EnableReplayApi=1 を書くだけで
Replay API (https://127.0.0.1:2999) が有効になる。
"""
from __future__ import annotations
import os
import shutil
import time
from pathlib import Path
from typing import Optional

COMMON_DIRS = [
    r"C:\Riot Games\League of Legends",
    r"D:\Riot Games\League of Legends",
    r"E:\Riot Games\League of Legends",
    r"C:\Program Files\Riot Games\League of Legends",
    r"C:\Program Files (x86)\Riot Games\League of Legends",
]


def _registry_candidates() -> list[str]:
    out: list[str] = []
    try:
        import winreg  # type: ignore
    except ImportError:
        return out
    keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Riot Games\League of Legends"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Riot Games, Inc\League of Legends"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Riot Games, Inc\League of Legends"),
    ]
    for hive, sub in keys:
        try:
            with winreg.OpenKey(hive, sub) as k:
                for name in ("Location", "InstallLocation", "Path"):
                    try:
                        v, _ = winreg.QueryValueEx(k, name)
                        out.append(str(v))
                    except OSError:
                        pass
        except OSError:
            pass
    return out


def find_lol_dir(override: Optional[str] = None) -> Optional[Path]:
    cands = []
    if override:
        cands.append(override)
    env = os.environ.get("LOL_DIR")
    if env:
        cands.append(env)
    cands += _registry_candidates() + COMMON_DIRS
    for c in cands:
        p = Path(c)
        if (p / "Config").is_dir() or (p / "lockfile").exists():
            return p
    return None


def game_cfg_path(lol_dir: Path) -> Path:
    return lol_dir / "Config" / "game.cfg"


def replay_api_enabled(cfg: Path) -> bool:
    if not cfg.exists():
        return False
    txt = cfg.read_text(encoding="utf-8", errors="ignore")
    for line in txt.splitlines():
        s = line.strip().replace(" ", "")
        if s.lower() == "enablereplayapi=1":
            return True
    return False


def enable_replay_api(cfg: Path) -> str:
    """game.cfg に EnableReplayApi=1 を書く (バックアップ付き)。戻り値は結果メッセージ。"""
    cfg.parent.mkdir(parents=True, exist_ok=True)
    if not cfg.exists():
        cfg.write_text("[General]\nEnableReplayApi=1\n", encoding="utf-8")
        return "game.cfg を新規作成して EnableReplayApi=1 を設定しました。LoLを再起動してください。"
    if replay_api_enabled(cfg):
        return "すでに有効です (EnableReplayApi=1)。"
    bak = cfg.with_name(f"game.cfg.bak_{time.strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(cfg, bak)
    raw = cfg.read_text(encoding="utf-8", errors="ignore")
    out, in_general, done = [], False, False
    for ln in raw.splitlines():
        st = ln.strip()
        if st.startswith("["):
            if in_general and not done:
                out.append("EnableReplayApi=1")
                done = True
            in_general = st.lower() == "[general]"
        if in_general and st.replace(" ", "").lower().startswith("enablereplayapi="):
            out.append("EnableReplayApi=1")
            done = True
            continue
        out.append(ln)
    if not done:
        if any(l.strip().lower() == "[general]" for l in out):
            out.append("EnableReplayApi=1")  # [General] が末尾セクション
        else:
            out = ["[General]", "EnableReplayApi=1", ""] + out
    cfg.write_text("\n".join(out) + "\n", encoding="utf-8")
    return f"EnableReplayApi=1 を書き込みました (バックアップ: {bak.name})。LoLを再起動してください。"


def read_lockfile(lol_dir: Path) -> Optional[dict]:
    """LCU の lockfile (name:pid:port:password:protocol)。"""
    lf = lol_dir / "lockfile"
    if not lf.exists():
        return None
    try:
        parts = lf.read_text(encoding="utf-8", errors="ignore").strip().split(":")
        return {"pid": int(parts[1]), "port": int(parts[2]), "password": parts[3], "protocol": parts[4]}
    except Exception:
        return None


def replays_dir() -> Path:
    return Path(os.path.expanduser("~")) / "Documents" / "League of Legends" / "Replays"


def list_replays() -> list[Path]:
    d = replays_dir()
    if not d.is_dir():
        return []
    return sorted(d.glob("*.rofl"), key=lambda p: p.stat().st_mtime, reverse=True)
