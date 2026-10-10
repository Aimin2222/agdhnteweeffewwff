# -*- coding: utf-8 -*-
"""Return LoL's live mirror to a safe, attached camera after a cinematic job.

This changes only the Replay API view AFTER capture has stopped.  It does not
touch FFmpeg, the audio capture path, TargetLock math, or the exported frames.
"""
from __future__ import annotations

from typing import Callable

from .replay_api import ReplayApiError


def restore_mirror_camera(api, player, field_of_view: float = 65.0,
                          log: Callable[[str], None] = lambda _msg: None) -> bool:
    """Park the attached camera above the selected champion, never at FPS offset 0.

    The previous cleanup sent selectionOffset=0 while leaving cameraMode=fps,
    which can embed the live mirror in the model/ground.  The safe top view is
    intentionally used only *after* recording/preview, not in any captured shot.
    """
    try:
        api.set_playback(paused=True, speed=1.0)
        selection = getattr(player, 'selection_name', '') or getattr(player, 'champion', '')
        if not selection:
            raise ValueError("選択チャンピオンが不明です")
        api.set_render(
            selectionName=selection,
            cameraMode="top",
            cameraAttached=True,
            selectionOffset={"x": 0, "y": 0, "z": 0},
            fieldOfView=float(field_of_view),
        )
        log("ミラー視点を復帰: 対象の安全な俯瞰追従カメラ")
        return True
    except (ReplayApiError, ValueError, TypeError) as exc:
        log(f"ミラー視点を復帰できませんでした: {exc}")
        return False
