# -*- coding: utf-8 -*-
"""10人のプレイヤー取得と、キル判定用の名前照合。"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import re


def norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).casefold()


@dataclass(frozen=True)
class Player:
    slot: int            # playerlist 内の並び (0-9)
    name: str            # 表示名 (riotIdGameName 優先)
    riot_id: str         # name#tag
    summoner: str        # 旧 summonerName
    champion: str        # 表示用チャンピオン名
    team: str            # ORDER / CHAOS
    raw_champion: str = ""
    selection_name: str = ""   # Replay API の selectionName 用

    def aliases(self) -> set:
        al = {self.name, self.riot_id, self.summoner, self.champion, self.selection_name}
        al |= {a.split("#")[0] for a in list(al) if a and "#" in a}
        return {norm(a) for a in al if a}

    def label(self) -> str:
        side = "BLUE" if self.team == "ORDER" else "RED"
        return f"[{side}] {self.champion}  -  {self.name}"

    def to_dict(self) -> dict:
        return asdict(self)


def parse_players(raw: list) -> list:
    out = []
    for i, p in enumerate(raw):
        game = p.get("riotIdGameName") or ""
        tag = p.get("riotIdTagLine") or ""
        summ = p.get("summonerName") or p.get("riotId") or ""
        riot = p.get("riotId") or (f"{game}#{tag}" if game and tag else summ)
        name = game or (summ.split("#")[0] if summ else f"Player{i + 1}")
        champ = p.get("championName") or ""
        raw_ch = p.get("rawChampionName", "") or ""
        sel = raw_ch.replace("game_character_displayname_", "") or champ
        out.append(Player(i, name, riot, summ, champ, p.get("team", "ORDER"), raw_ch, sel))
    out.sort(key=lambda x: (0 if x.team == "ORDER" else 1, x.slot))
    return out


def is_player_name(event_name: str, p: Player) -> bool:
    return norm(event_name) in p.aliases()
