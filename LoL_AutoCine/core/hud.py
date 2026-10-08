# -*- coding: utf-8 -*-
"""HUD関連ヘルパー。

v2.2では安全性優先のため、通常処理からReplay APIのHUD変更を行わない。

フラグ名は Replay API の render プロパティ (Lolnam Editor の UI が操作している項目と同じ)。
録画前に現在値を保存し、終了時に必ず復元する。
"""
from __future__ import annotations
from typing import Optional

from .replay_api import ReplayAPI, ReplayApiError

INTERFACE_FLAGS = [
    "interfaceAll", "interfaceReplay", "interfaceScore", "interfaceScoreboard", "interfaceFrames",
    "interfaceMinimap", "interfaceTimeline", "interfaceChat", "interfaceTarget", "interfaceQuests",
    "interfaceAnnounce", "interfaceKillCallouts", "interfaceNeutralTimers",
]
BAR_FLAGS = ["healthBarChampions", "healthBarStructures", "healthBarWards", "healthBarPets", "healthBarMinions"]
OTHER_FLAGS = ["floatingText", "outlineSelect", "outlineHover"]


def hide_values(keep_champion_bars: bool = False) -> dict:
    vals = {k: False for k in INTERFACE_FLAGS + BAR_FLAGS + OTHER_FLAGS}
    if keep_champion_bars:
        vals["healthBarChampions"] = True
    return vals


def hide_hud(api: ReplayAPI, keep_champion_bars: bool = False) -> dict:
    """HUDを隠し、変更前の値(戻す用)を返す。"""
    # 1クリップにつき1回だけ送信する。毎フレーム変更しないことでReplay API負荷を抑える。
    try:
        before = api.render()
    except ReplayApiError:
        before = {}
    vals = hide_values(keep_champion_bars)
    saved = {k: before[k] for k in vals if k in before}
    try:
        api.set_render(**vals)
    except ReplayApiError:
        # HUD非表示に失敗しても録画自体は継続できるよう安全側に倒す。
        return {}
    return saved


def restore_hud(api: ReplayAPI, saved: Optional[dict]) -> None:
    if not saved:
        return
    try:
        api.set_render(**saved)
    except ReplayApiError:
        pass
