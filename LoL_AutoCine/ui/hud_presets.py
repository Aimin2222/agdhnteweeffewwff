# -*- coding: utf-8 -*-
"""Stable HUD presets; never claim to change the in-game name display setting.

LoL name display is controlled by the game UI. Keep only proven Replay API
render flags here; do not guess additional unsupported `set_render` properties.
"""

HUD_MODES = {
    "hidden": "すべて非表示（シネマ）",
    "health": "体力バー中心（名前はLoL設定）",
    "full": "通常HUD（ゲーム内表示のまま）",
}


def hud_flags(mode: str) -> tuple[bool, bool]:
    """Return (hide_interface, keep_champion_health_bars)."""
    if mode == "full":
        return False, False
    if mode == "health":
        return True, True
    if mode == "hidden":
        return True, False
    raise ValueError(f"Unknown HUD mode: {mode}")


def hud_mode_from_flags(hide_hud: bool, keep_champion_bars: bool) -> str:
    # Legacy saved templates represent HUD with two independent flags.
    if not hide_hud:
        return "full"
    return "health" if keep_champion_bars else "hidden"


def hud_summary(mode: str) -> str:
    if mode == "health":
        return "体力バーを残す設定です。名前を消すにはLoL側の名前表示を『なし』にしてください（録画前にミラーで確認）。"
    if mode == "full":
        return "LoLが表示しているHUDを維持します。名前・体力バーもLoL側の設定に従います。"
    return "HUD・HPバーを非表示にするシネマ向け設定です。"
