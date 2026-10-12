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
import subprocess

from .gpu_binary import ffmpeg_exe
from .kill_icons import MOTION_STYLES, make_badge, with_badges

from .jobs import run_auto_edit
from .scanner import filter_scanned_events
from .qa_package import split_test_results
from .qa_plan import validate_plan

QA_MODES = (
    ("third", "通常三人称"),
    ("third_cinema", "三人称シネマ"),
    ("fps", "FPS"),
    ("lolnam_cinema", "Lolnam風シネマ"),
)

def plan_eight_cases(players, events, preferred=None, modes=None):
    """Return 8 ordered scenarios; empty event sets make testing impossible."""
    result = []
    for team, side in (("CHAOS", "RED"), ("ORDER", "BLUE")):
        candidates = []
        for p in players:
            if getattr(p, "team", None) != team:
                continue
            # A kill is a better QA target than an assist: the selected
            # champion must actually be present at the important moment.
            kills = filter_scanned_events(events, p, "kill")
            scenes = kills or filter_scanned_events(events, p, "both")
            if scenes:
                preference = 1 if p is preferred or getattr(p, "slot", None) == getattr(preferred, "slot", None) else 0
                candidates.append((bool(kills), len(kills), preference, p, scenes))
        if not candidates:
            raise ValueError(f"{side}側に録画できるキル/アシストが見つかりません。全体スキャンを確認してください。")
        candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        _, _, _, player, scenes = candidates[0]
        # A representative middle event avoids replay opening/closing edges.
        chosen = scenes[len(scenes)//2]
        for mode, label in QA_MODES:
            if modes is None or mode in modes:
                result.append((side, player, chosen, mode, label))
    return result

def run_camera_record_test(api, source, players, events, preferred, template, destination,
                           *, stop=None, log=lambda _m: None, audio_factory=None, progress=None,
                           plan=None, plan_source='bundled'):
    """Record four modes per side, returning the report path.

    Only one clip per style is created; capture and game audio use exactly the
    same production pipeline as ordinary montage exports. No 8 simultaneous
    recorders, no Tk widget access from the worker.
    """
    config = validate_plan(plan) if plan is not None else None
    scenarios = plan_eight_cases(players, events, preferred,
                                modes=config['camera_modes'] if config else None)
    folder = Path(destination) / ("CameraQA_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "5.10.17-test",
        "kind": "live_replay_camera_test",
        "expected_clips": len(scenarios),
        "test_plan": config,
        "test_plan_source": plan_source,
        "qa_archives": [],
        "outputs": [],
        "montage_tests": [],
        "badge_motion_tests": [],
        "limitations": "Framing must be judged visually on Windows. Audio/codec need playback or ffprobe.",
    }
    def flush():
        (folder / "results.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    flush()
    for index, (side, player, scene, mode, label) in enumerate(scenarios, 1):
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
                   "failed": [], "camera_diagnostics": []}
        def capture_camera_log(message):
            # Numeric camera setup data from the normal production path.
            if str(message).startswith("CAMERA_QA_POSE "):
                try:
                    current["camera_diagnostics"].append(json.loads(str(message).split(" ", 1)[1]))
                except (ValueError, IndexError, TypeError):
                    pass
            log(message)
        log(f"カメラテスト [{index}/{len(scenarios)}]: {side} / {label} / {player.label()} / {scene.time:.1f}s")
        if progress:
            progress(index-1, len(scenarios), round(100*(index-1)/len(scenarios),1), f"{side} {label} を録画中")
        try:
            result = run_auto_edit(
                api, source, player, [scene], clip_template, folder / f"{index:02d}_{side}_{mode}",
                False, progress=None, stop=stop, log=capture_camera_log, audio_factory=audio_factory)
            current["outputs"] = [str(p) for p in result.outputs]
            current["failed"] = [[int(i), str(msg)] for i,msg in result.failed]
            if not result.outputs and not result.failed:
                current["failed"].append([0, "録画結果がありません"])
        except Exception as exc:
            current["failed"].append([0, f"{type(exc).__name__}: {exc}"])
            log(f"カメラテスト [{index}/{len(scenarios)}] 失敗: {exc}")
        manifest["outputs"].append(current)
        flush()
        if progress:
            progress(index, len(scenarios), round(100*index/len(scenarios),1), f"{side} {label} 完了")
    # Reuse recorded MP4s for every transition: do not spend another LoL
    # capture/audio session on identical footage. Keep the outputs separate.
    generated = [Path(p) for row in manifest["outputs"] for p in row["outputs"]]
    ready = [p for p in generated if p.is_file()]
    if len(ready) >= 2 and not (stop is not None and stop.is_set()):
        from .montage_fx import MONTAGE_LABELS, render_montage
        for style in MONTAGE_LABELS:
            if config is not None and style not in config['montage_styles']:
                continue
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
    # The eight camera QA clips intentionally disable kill badges so camera
    # geometry is unobstructed. Render six *separate* badge-motion clips from
    # an already-recorded MP4; otherwise the user cannot check entrance FX.
    if ready and not (stop is not None and stop.is_set()):
        from .kill_icons import STYLES
        theme = template.kill_icon_style if template.kill_icon_style in STYLES and template.kill_icon_style != "off" else "cinema"
        badge = folder / "badge_motion_qa_image.png"
        try:
            make_badge(badge, theme)
            for motion, label in MOTION_STYLES.items():
                if config is not None and motion not in config['badge_motions']:
                    continue
                if stop is not None and stop.is_set():
                    break
                dest = folder / f"badge_motion_{motion}.mp4"
                entry = {"motion": motion, "label": label, "outputs": [], "failed": []}
                try:
                    # FFmpeg filter used by production, not a Python mock;
                    # no additional game capture or sound recording.
                    duration = 3.0
                    graph = with_badges("[0:v]format=yuv420p[vout]", 1,
                                        [(badge, 0.45)], duration=duration,
                                        position="right-top", scale=1.0,
                                        seconds=2.1, style=theme, motion=motion)
                    cmd = [str(ffmpeg_exe()), "-hide_banner", "-loglevel", "error", "-y",
                           "-i", str(ready[0]),
                           "-loop", "1", "-framerate", "60", "-i", str(badge),
                           "-filter_complex", graph,
                           "-map", "[vout]", "-map", "0:a?",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                           "-pix_fmt", "yuv420p", "-c:a", "copy",
                           "-t", str(duration), str(dest)]
                    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
                    if not dest.is_file() or dest.stat().st_size == 0:
                        raise RuntimeError("テスト動画が生成されませんでした")
                    entry["outputs"] = [str(dest)]
                except Exception as exc:
                    entry["failed"].append(f"{type(exc).__name__}: {exc}")
                    log(f"キルフレーム登場 {label} のテスト失敗: {exc}")
                manifest["badge_motion_tests"].append(entry)
                flush()
        except Exception as exc:
            manifest["badge_motion_tests"].append({"motion": "setup", "outputs": [],
                                                    "failed": [str(exc)]})
            flush()
    manifest["completed_clips"] = sum(bool(row["outputs"]) for row in manifest["outputs"])
    manifest["canceled"] = bool(stop is not None and stop.is_set())
    flush()
    # Export results directly as <=500MB ZIPs, while leaving loose MP4s intact.
    try:
        max_mb = config["max_zip_mb"] if config else 500
        archives = split_test_results(folder, max_bytes=max_mb * 1_000_000, log=log)
        manifest["qa_archives"] = [str(item) for item in archives]
        log(f"テスト結果をZIP {len(archives)} 個に分割（各最大{max_mb}MB）")
    except Exception as exc:
        manifest["qa_packaging_error"] = f"{type(exc).__name__}: {exc}"
        log("テストZIP化に失敗。元MP4とJSONは保持されます: " + str(exc))
    flush()
    return folder / "results.json"
