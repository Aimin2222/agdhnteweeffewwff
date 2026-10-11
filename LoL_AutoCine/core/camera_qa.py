# -*- coding: utf-8 -*-
"""Opt-in, eight-clip RED/BLUE camera and audio QA for live LoL replays.

The user must click the button. Never starts automatically in the background.
All heavyweight recording uses existing jobs.run_auto_edit and restores the
game camera/HUD via the same production cleanup paths.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import json
from pathlib import Path

from .jobs import run_auto_edit
from .scanner import filter_scanned_events

QA_MODES = (
    ("third", "通常三人称"),
    ("third_cinema", "三人称シネマ"),
    ("fps", "FPS"),
    ("lolnam_cinema", "Lolnam風シネマ"),
)

def plan_eight_cases(players, events, preferred=None):
    """Return 8 ordered scenarios; empty event sets make testing impossible."""
    result = []
    for team, side in (("CHAOS", "RED"), ("ORDER", "BLUE")):
        candidates = []
        for p in players:
            if getattr(p, "team", None) != team:
                continue
            scenes = filter_scanned_events(events, p, "both")
            if scenes:
                # Prefer the currently selected player if that side has one.
                preference = 1 if p is preferred or getattr(p, "slot", None) == getattr(preferred, "slot", None) else 0
                candidates.append((preference, len(scenes), p, scenes))
        if not candidates:
            raise ValueError(f"{side}側に録画できるキル/アシストが見つかりません。全体スキャンを確認してください。")
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        _, _, player, scenes = candidates[0]
        # A representative middle event avoids replay opening/closing edges.
        chosen = scenes[len(scenes)//2]
        for mode, label in QA_MODES:
            result.append((side, player, chosen, mode, label))
    return result

def run_camera_record_test(api, source, players, events, preferred, template, destination,
                           *, stop=None, log=lambda _m: None, audio_factory=None, progress=None):
    """Record four modes per side, returning the report path.

    Only one clip per style is created; capture and game audio use exactly the
    same production pipeline as ordinary montage exports. No 8 simultaneous
    recorders, no Tk widget access from the worker.
    """
    plan = plan_eight_cases(players, events, preferred)
    folder = Path(destination) / ("CameraQA_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "5.10.15",
        "kind": "live_replay_camera_test",
        "expected_clips": len(plan),
        "outputs": [],
        "montage_tests": [],
        "limitations": "Framing must be judged visually on Windows. Audio/codec need playback or ffprobe.",
    }
    def flush():
        (folder / "results.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    flush()
    for index, (side, player, scene, mode, label) in enumerate(plan, 1):
        if stop is not None and stop.is_set():
            log("8本テスト: ユーザー操作により中止しました。")
            break
        clip_template = replace(template)
        clip_template.name = f"CameraQA {side} {label}"
        clip_template.style = mode
        clip_template.camera_side = "auto"
        clip_template.merge_multikill = False
        clip_template.smart_highlight_enabled = False
        clip_template.smart_composition = False
        clip_template.smart_montage = False
        clip_template.kill_icon_style = "off"
        clip_template.fps = 60
        clip_template.capture_fps = 60
        clip_template.pre = min(3.0, max(1.0, float(template.pre)))
        clip_template.post = min(3.0, max(1.0, float(template.post)))
        current = {"number": index, "side": side, "mode": mode, "label": label,
                   "player": player.label(), "event_time": float(scene.time), "outputs": [],
                   "failed": []}
        log(f"8本テスト [{index}/8]: {side} / {label} / {player.label()} / {scene.time:.1f}s")
        if progress:
            progress(index-1, 8, round(100*(index-1)/8,1), f"{side} {label} を録画中")
        try:
            result = run_auto_edit(
                api, source, player, [scene], clip_template, folder / f"{index:02d}_{side}_{mode}",
                False, progress=None, stop=stop, log=log, audio_factory=audio_factory)
            current["outputs"] = [str(p) for p in result.outputs]
            current["failed"] = [[int(i), str(msg)] for i,msg in result.failed]
            if not result.outputs and not result.failed:
                current["failed"].append([0, "録画結果がありません"])
        except Exception as exc:
            current["failed"].append([0, f"{type(exc).__name__}: {exc}"])
            log(f"8本テスト [{index}/8] 失敗: {exc}")
        manifest["outputs"].append(current)
        flush()
        if progress:
            progress(index, 8, round(100*index/8,1), f"{side} {label} 完了")
    # Reuse recorded MP4s for every transition: do not spend another LoL
    # capture/audio session on identical footage. Keep the outputs separate.
    generated = [Path(p) for row in manifest["outputs"] for p in row["outputs"]]
    ready = [p for p in generated if p.is_file()]
    if len(ready) >= 2 and not (stop is not None and stop.is_set()):
        from .montage_fx import MONTAGE_LABELS, render_montage
        for style in MONTAGE_LABELS:
            if stop is not None and stop.is_set():
                break
            dest = folder / f"transition_{style}.mp4"
            outcome = {"style": style, "label": MONTAGE_LABELS[style],
                       "outputs": [], "failed": []}
            try:
                applied = render_montage(ready[:2], dest, style=style, logger=log)
                outcome["applied_style"] = applied
                if dest.is_file():
                    outcome["outputs"] = [str(dest)]
                else:
                    outcome["failed"] = ["MP4 was not created"]
            except Exception as exc:
                outcome["failed"] = [f"{type(exc).__name__}: {exc}"]
                log(f"つなぎ演出テスト {style}: {exc}")
            manifest["montage_tests"].append(outcome)
            flush()
    manifest["completed_clips"] = sum(bool(row["outputs"]) for row in manifest["outputs"])
    manifest["canceled"] = bool(stop is not None and stop.is_set())
    flush()
    return folder / "results.json"
