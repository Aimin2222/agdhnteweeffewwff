# -*- coding: utf-8 -*-
"""全編スキャン: リプレイを倍速で最後まで流し、固定プレイヤーのキルだけを集める。

Replay中の /liveclientdata/eventdata は「現在の再生時刻までのイベント」しか返さない。
そのため手動操作なしで終端まで自動再生しながらイベントを回収し、最後に終端で最終取得する。
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional

from .players import Player, is_player_name
from .replay_api import ReplayAPI, ReplayApiError


@dataclass
class Kill:
    event_id: int
    time: float
    killer: str
    victim: str
    assisters: list
    multikill: int = 1      # 連続キル数 (グルーピング後)
    role: str = "kill"     # kill / assist / both

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScanResult:
    total_events: int
    kills: list
    length: float
    complete: bool


def _norm_event(e: dict) -> Optional[dict]:
    if e.get("EventName") != "ChampionKill":
        return None
    return {
        "event_id": int(e.get("EventID", -1)),
        "time": float(e.get("EventTime", 0.0)),
        "killer": str(e.get("KillerName", "")),
        "victim": str(e.get("VictimName", "")),
        "assisters": list(e.get("Assisters", []) or []),
    }


def scan_kills(
    api: ReplayAPI,
    player: Player,
    progress: Optional[Callable] = None,
    stop=None,
    scan_speed: float = 8.0,
    poll: float = 0.4,
    stall_limit: float = 10.0,
    diag_dir: Optional[Path] = None,
    event_mode: str = "kill",  # kill / assist / both
) -> ScanResult:
    """progress(pct, cur_time, length, n_events, n_kills) を随時呼ぶ。"""
    pb = api.playback()
    length = float(pb.get("length", 0.0))
    if length <= 0:
        raise ReplayApiError("リプレイの長さを取得できません。リプレイが再生中か確認してください。")

    api.set_playback(paused=True)
    api.seek(0.0)
    api.set_playback(speed=scan_speed, paused=False)

    seen: dict = {}      # EventID -> raw event
    all_events: list = []
    last_t, last_move = -1.0, time.time()
    complete = False

    def collect() -> None:
        for e in api.events():
            key = int(e.get("EventID", len(all_events)))
            if key not in seen:
                seen[key] = e
                all_events.append(e)
            elif len(e.get("Assisters", []) or []) > len(seen[key].get("Assisters", []) or []):
                # Some replay events acquire their full assister list after
                # the first poll. Refresh an existing event without duplicating it.
                seen[key].update(e)

    mode = event_mode if event_mode in ("kill", "assist", "both") else "kill"

    def _is_target(ne: dict) -> tuple[bool, str]:
        if is_player_name(ne["killer"], player):
            return True, "kill"
        if any(is_player_name(a, player) for a in ne.get("assisters", [])):
            return True, "assist"
        return False, ""

    def count_kills() -> int:
        n = 0
        for e in all_events:
            ne = _norm_event(e)
            if ne:
                hit, role = _is_target(ne)
                if hit and (mode == "both" or role == mode):
                    n += 1
        return n

    try:
        while True:
            if stop is not None and stop.is_set():
                break
            pb = api.playback()
            t = float(pb.get("time", 0.0))
            collect()
            if progress:
                progress(min(100.0, 100.0 * t / length), t, length, len(all_events), count_kills())
            if t >= length - 1.0:
                complete = True
                break
            # 停止検知 (同じ画面で止まる問題の対策)
            if t > last_t + 0.05:
                last_t, last_move = t, time.time()
            elif time.time() - last_move > 2.0:
                api.set_playback(paused=False, speed=scan_speed)
                if time.time() - last_move > stall_limit:
                    raise ReplayApiError("再生が進みません (スキャン中に停止)。LoLが前面で動作しているか確認してください。")
            time.sleep(poll)

        if complete:
            api.seek(max(0.0, length - 0.5))   # 終端到達後に最終イベント取得
            time.sleep(0.3)
            collect()
    finally:
        try:
            api.set_playback(paused=True, speed=1.0)
        except ReplayApiError:
            pass

    raw_kills = []
    for e in all_events:
        ne = _norm_event(e)
        if ne:
            hit, role = _is_target(ne)
            if hit and (mode == "both" or role == mode):
                raw_kills.append(Kill(ne["event_id"], ne["time"], ne["killer"], ne["victim"], ne["assisters"], role=role))
    raw_kills.sort(key=lambda k: k.time)
    kills = _dedupe_kills(raw_kills)
    _mark_multikills(kills)

    if progress:
        progress(100.0 if complete else 0.0, length, length, len(all_events), len(kills))
    if diag_dir is not None:
        diag_dir.mkdir(parents=True, exist_ok=True)
        (diag_dir / "last_scan_events.json").write_text(
            json.dumps(
                {"player": player.to_dict(), "length": length, "complete": complete,
                 "total_events": len(all_events), "target_kills": len(kills), "event_mode": mode,
                 "kills": [k.to_dict() for k in kills], "events": all_events},
                ensure_ascii=False, indent=2),
            encoding="utf-8")
    return ScanResult(len(all_events), kills, length, complete)



def _dedupe_kills(kills: list, same_victim_window: float = 1.5) -> list:
    """Replay API が同じ ChampionKill を別 EventID で重複返却するケースを除去する。

    EventID だけをキーにすると重複を通してしまうため、実際のキル内容
    (killer/victim) と時刻の近さでも判定する。同一キラーが同一犠牲者を
    1.5秒以内に再度倒すことは通常ないので、安全側で最初のイベントを残す。
    """
    out = []
    last_by_pair = {}
    for k in kills:
        killer = k.killer.strip().casefold()
        victim = k.victim.strip().casefold()
        pair = (killer, victim)
        prev = last_by_pair.get(pair)
        if prev is not None and abs(k.time - prev.time) <= same_victim_window:
            continue
        # 時刻だけが同じで EventID だけ違う重複も除去。
        if out and abs(k.time - out[-1].time) <= 0.35 and killer == out[-1].killer.strip().casefold() and victim == out[-1].victim.strip().casefold():
            continue
        out.append(k)
        last_by_pair[pair] = k
    return out


def _mark_multikills(kills: list, window: float = 10.0) -> None:
    """10秒以内の連続キルに multikill 数を付与 (ダブル/トリプル…)。"""
    run = 0
    prev = None
    for k in kills:
        if prev is not None and k.time - prev.time <= window:
            run += 1
        else:
            run = 1
        k.multikill = run
        prev = k


def group_clips(kills: list, pre: float, post: float, merge: bool = True) -> list:
    """キル → クリップ区間 [(start, end, [kills])]。連続キルは1本にまとめる(merge)。"""
    clips: list = []
    for k in kills:
        s, e = max(0.0, k.time - pre), k.time + post
        if merge and clips and s <= clips[-1][1]:
            clips[-1][1] = max(clips[-1][1], e)
            clips[-1][2].append(k)
        else:
            clips.append([s, e, [k]])
    return [(s, e, ks) for s, e, ks in clips]
