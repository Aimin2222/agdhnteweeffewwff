# -*- coding: utf-8 -*-
"""Opt-in development-only replay QA. Never starts by itself.

Reuses the ordinary AutoCine capture/export path. A person must start the
replay first and click the QA button. Abort is controlled by the same stop
event as the regular recorder. Can be removed without touching release jobs.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
import json
import subprocess
import time

from .scanner import filter_scanned_events

CAMERA_CASES = (
    ("third", "通常三人称"),
    ("third_cinema", "三人称シネマ"),
    ("fps", "FPS風"),
    ("lolnam_cinema", "Lolnam風シネマ"),
)
TEAM_NAME = {"ORDER": "BLUE", "CHAOS": "RED"}


def build_matrix(players, events, *, events_per_team=1):
    """One or two real kill events on each side across four camera styles.

    Deliberately avoids an all-player 20-clip run by default. Events are
    scanned/cached once; no extra full-replay scans are performed.
    """
    events_per_team = max(1, min(2, int(events_per_team)))
    tests = []
    for team in ("ORDER", "CHAOS"):
        choices = []
        for player in players:
            if player.team != team:
                continue
            kills = filter_scanned_events(events, player, "kill")
            for kill in kills:
                choices.append((player, kill))
        # Prefer a single well-covered subject; preserve all killer names.
        choices.sort(key=lambda item: (item[1].time, item[0].slot))
        selected = choices[:events_per_team]
        for player, kill in selected:
            for style, title in CAMERA_CASES:
                tests.append({"side": TEAM_NAME[team], "player": player, "kill": kill,
                              "camera": style, "camera_title": title})
    return tests


def run_replay_qa(api, source, players, events, template, destination, *,
                  audio_factory=None, stop=None, progress=None, log=None,
                  events_per_team=1):
    """Record up to 8 (or 16) short actual replay clips, without changing UI vars.

    Outputs are isolated in diagnostics/replay_qa_<timestamp>. No montage is
    built, minimizing temporary files and preserving the user's own output.
    Existing record_one_clip restores camera/HUD through its finally blocks.
    """
    from .jobs import run_auto_edit
    log = log or (lambda _message: None)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(destination) / ("replay_qa_" + stamp)
    root.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix(players, events, events_per_team=events_per_team)
    report = {
        "version": "5.10.15", "timestamp": stamp, "format": "developer opt-in",
        "reason": "RED/BLUE camera and output regression checks",
        "cases_requested": len(matrix), "cases": [], "cancelled": False,
        "outputs_root": str(root), "notes": [
            "This records real LoL replay video only after the user clicks the test button.",
            "Visual subject framing and camera inversion still need human review.",
            "GPU availability and audio can vary; inspect generated media.",
        ],
    }
    for i, case in enumerate(matrix):
        if stop is not None and stop.is_set():
            report["cancelled"] = True
            break
        title = case["camera_title"]
        player, kill = case["player"], case["kill"]
        side = case["side"]
        group = root / side / case["camera"]
        local_tpl = replace(template, style=case["camera"], name="QA_" + title,
                            pre=2.0, post=2.0, merge_multikill=False,
                            smart_highlight_enabled=False, smart_montage=False,
                            montage_fx="cut", motion_arc=0.0, motion_dolly=0.0)
        local_tpl.bgm_path = ""
        local_tpl.bgm_volume = 0.0
        case_result = {"side": side, "camera": case["camera"],
                       "camera_title": title, "player": player.name,
                       "champion": player.champion, "time": float(kill.time),
                       "status": "pending", "outputs": [], "error": ""}
        try:
            if progress:
                progress(i, len(matrix), (100.0*i/max(1,len(matrix))),
                         f"自動実機テスト {i+1}/{len(matrix)}: {side} {title}")
            log(f"QA {i+1}/{len(matrix)}: {side} / {title} / {player.champion}")
            result = run_auto_edit(api, source, player, [kill], local_tpl, group,
                                   make_montage=False, stop=stop,
                                   log=log, audio_factory=audio_factory)
            case_result["outputs"] = [str(p) for p in result.outputs]
            case_result["status"] = "pass" if result.outputs and not result.failed else "fail"
            if result.failed:
                case_result["error"] = "; ".join(str(item) for item in result.failed)
        except Exception as exc:
            case_result["status"] = "fail"
            case_result["error"] = type(exc).__name__ + ": " + str(exc)
            log(f"QA error {side}/{title}: {exc}")
        report["cases"].append(case_result)
        (root / "replay_qa_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["passed"] = sum(c["status"] == "pass" for c in report["cases"])
    report["failed"] = sum(c["status"] == "fail" for c in report["cases"])
    report["finished"] = datetime.now().isoformat()
    (root / "replay_qa_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if progress:
        progress(len(report["cases"]), len(matrix), 100., "リプレイ自動テスト完了")
    return report
