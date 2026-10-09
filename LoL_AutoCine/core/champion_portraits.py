# -*- coding: utf-8 -*-
"""Resolve actual LoL champion portraits from a replay's player list.

Data source: Riot's public Data Dragon PNG icon service. No API key.
- Only fixed Riot CDN endpoints are used; never accept a remote URL from a clip.
- Cache files per champion so a second video does not need an internet request.
- If a real champion cannot be identified/resolved, return None instead of
  inventing a portrait or showing the wrong character.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from .players import Player, norm

BASE = "https://ddragon.leagueoflegends.com"
_VERSIONS_URL = BASE + "/api/versions.json"
_LOCAL_VERSION = "versions.json"
_MANIFESTS = ("en_US", "ja_JP")
_MEM_MANIFEST: dict[str, str] | None = None
_MEM_VERSION: str | None = None

# Data Dragon's IDs are not always the champion's display name.
_ALIASES = {
    "wukong": "MonkeyKing",
    "monkeyking": "MonkeyKing",
    "nunuandwillump": "Nunu",
    "nunu": "Nunu",
    "renataglasc": "Renata",
    "drmundo": "DrMundo",
    "belveth": "Belveth",
    "khazix": "Khazix",
    "kogmaw": "KogMaw",
    "kaisa": "Kaisa",
    "velkoz": "Velkoz",
    "chogath": "Chogath",
    "reksai": "RekSai",
    "missfortune": "MissFortune",
    "jarvaniv": "JarvanIV",
    "aurelionsol": "AurelionSol",
    "tahmkench": "TahmKench",
    "masteryi": "MasterYi",
    "twistedfate": "TwistedFate",
    "xinzhao": "XinZhao",
    "leesin": "LeeSin",
    "ksante": "KSante",
    "smolder": "Smolder",
}


def _key(s: str) -> str:
    text = unicodedata.normalize("NFKC", str(s or "")).casefold()
    return "".join(ch for ch in text if ch.isalnum())


def _cache_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    return Path(base) / "LoL_AutoCine" / "champion_icons" if base else Path.home() / ".cache" / "lol_autocine" / "champion_icons"


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def _fetch(url: str, timeout: float = 4.0) -> bytes:
    if not url.startswith(BASE + "/"):
        raise ValueError("Unexpected champion asset host")
    request = urllib.request.Request(url, headers={"User-Agent": "LoL-AutoCine/5.9.9.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(4_000_000)


def _version(cache: Path) -> str:
    global _MEM_VERSION
    if _MEM_VERSION:
        return _MEM_VERSION
    path = cache / _LOCAL_VERSION
    try:
        versions = json.loads(_fetch(_VERSIONS_URL))
        if not isinstance(versions, list) or not versions:
            raise ValueError("No Data Dragon version")
        version = str(versions[0])
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise ValueError("Invalid Data Dragon version")
        path.write_text(json.dumps(versions[:8]), encoding="utf-8")
    except (OSError, ValueError, TimeoutError, urllib.error.URLError):
        versions = _load_json(path)
        version = str(versions[0]) if isinstance(versions, list) and versions else ""
    _MEM_VERSION = version
    return version


def _manifest(cache: Path) -> dict[str, str]:
    global _MEM_MANIFEST
    if _MEM_MANIFEST is not None:
        return _MEM_MANIFEST
    version = _version(cache)
    lookup = dict(_ALIASES)
    if not version:
        _MEM_MANIFEST = lookup
        return lookup
    for locale in _MANIFESTS:
        path = cache / f"champions_{version}_{locale}.json"
        manifest = _load_json(path)
        if manifest is None:
            try:
                manifest = json.loads(_fetch(f"{BASE}/cdn/{version}/data/{locale}/champion.json"))
                path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            except (OSError, ValueError, TimeoutError, urllib.error.URLError):
                manifest = None
        if not isinstance(manifest, dict):
            continue
        data = manifest.get("data", {})
        if not isinstance(data, dict):
            continue
        for champ in data.values():
            if not isinstance(champ, dict):
                continue
            champ_id = champ.get("id", "")
            if not re.fullmatch(r"[a-zA-Z0-9]{2,36}", champ_id):
                continue
            for alias in (champ.get("id"), champ.get("name"), champ.get("key")):
                if alias:
                    lookup[_key(alias)] = champ_id
    _MEM_MANIFEST = lookup
    return lookup


def identify_champion(event_name: str, roster: list[Player] | None) -> Optional[str]:
    """Return the replay player's champion; no guessing between ambiguous IDs."""
    candidates = [p for p in roster or [] if norm(event_name) in p.aliases()]
    unique = {(_key(p.raw_champion.replace("game_character_displayname_", "")),
               _key(p.champion or p.selection_name)): p for p in candidates}
    if len(unique) == 1:
        p = next(iter(unique.values()))
        return (p.selection_name or p.champion or p.raw_champion) or None
    if not candidates:
        # Some event versions contain champion name instead of summoner name.
        return event_name
    return None


def portrait_for_event(event_name: str, roster: list[Player] | None,
                       cache_dir: Optional[Path] = None) -> Optional[Path]:
    champion_name = identify_champion(event_name, roster)
    if not champion_name:
        return None
    cache = Path(cache_dir) if cache_dir else _cache_dir()
    try:
        cache.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    manifest = _manifest(cache)
    champion_id = manifest.get(_key(champion_name))
    if not champion_id:
        return None
    stored = cache / f"{champion_id}.png"
    if stored.is_file() and stored.stat().st_size > 400:
        return stored
    version = _version(cache)
    if not version:
        return None
    try:
        raw = _fetch(f"{BASE}/cdn/{version}/img/champion/{champion_id}.png", timeout=5.0)
        # Verify PNG signature, then write atomically.
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            return None
        fd, tmp = tempfile.mkstemp(prefix="champ_", suffix=".png", dir=cache)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
            os.replace(tmp, stored)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return stored
    except (OSError, ValueError, TimeoutError, urllib.error.URLError):
        return None
