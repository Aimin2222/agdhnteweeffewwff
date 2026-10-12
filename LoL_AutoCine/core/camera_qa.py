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
from .kill_icons import MOTION_STYLES, make_badge, normalize
from .gpu_badge_qa import render_badge_motion
from .montage_fx import get_duration
from .gpu_binary import ffmpeg_exe
from .qa_package import split_test_results
from .qa_plan import validate_plan
from .qa_support import collect_qa_support
from .camera_geometry import inspect_rig
from .qa_visual import make_qa_contact_sheets
from .qa_reels import assemble_side_reels
from .qa_true_transitions import TRANSITION_PREVIEWS, render_true_transition

QA_MODES = (
    ("third", "通常三人称"),
    ("third_cinema", "三人称シネマ"),
    ("fps", "FPS"),
    ("lolnam_cinema", "Lolnam風シネマ"),
)

EXPERIMENTAL_QA_MODES = (("geo_aim", "座標追従カメラ（実験）"),)

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
        selected_modes = QA_MODES + (EXPERIMENTAL_QA_MODES if modes is not None and "geo_aim" in modes else ())
        for mode, label in selected_modes:
            if modes is None or mode in modes:
                result.append((side, player, chosen, mode, label))
    return result

def run_camera_record_test(api, source, players, events, preferred, template, destination,
                           *, stop=None, log=lambda _m: None, audio_factory=None, progress=None,
                           plan=None, plan_source="bundled"):
    """Record four modes per side, returning the report path.

    Only one clip per style is created; capture and game audio use exactly the
    same production pipeline as ordinary montage exports. No 8 simultaneous
    recorders, no Tk widget access from the worker.
    """
    config = validate_plan(plan) if plan is not None else None
    scenarios = (plan_eight_cases(players, events, preferred, modes=config["camera_modes"])
                 if config else plan_eight_cases(players, events, preferred))
    folder = Path(destination) / ("CameraQA_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {
        "version": (Path(__file__).resolve().parents[1] / "VERSION.txt").read_text(encoding="utf-8").strip(),
        "kind": "live_replay_camera_test",
        "expected_clips": len(scenarios),
        "test_plan": config,
        "test_plan_source": plan_source,
        "qa_archives": [],
        "outputs": [],
        "montage_tests": [],
        "badge_motion_tests": [],
        "spatial_transition_tests": [],
        "side_review_reels": {},
        "limitations": "Framing must be judged visually on Windows. Audio/codec need playback or ffprobe.",
    }
    def flush():
        (folder / "results.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    flush()
    for index, (side, player, scene, mode, label) in enumerate(scenarios, 1):
        if stop is not None and stop.is_set():
            log("カメラテスト: ユーザー操作により中止しました。")
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
            if str(message).startswith("CAMERA_QA_POSE "):
                try:
                    evidence = json.loads(str(message).split(" ", 1)[1])
                    if isinstance(evidence, dict):
                        evidence["geometry_validation"] = inspect_rig(evidence)
                        current["camera_diagnostics"].append(evidence)
                except (ValueError, IndexError, TypeError):
                    pass
            log(message)
        log(f"カメラテスト [{index}/{len(scenarios)}]: {side} / {label} / {player.label()} / {scene.time:.1f}s")
        if progress:
            progress(index-1, len(scenarios), round(100*(index-1)/len(scenarios),1), f"{side} {label} を録画中")
        try:
            (folder / side).mkdir(exist_ok=True)
            result = run_auto_edit(
                api, source, player, [scene], clip_template, folder / side / f"{index:02d}_{mode}",
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
    if not (stop is not None and stop.is_set()):
        manifest["side_review_reels"] = assemble_side_reels(folder, manifest["outputs"], log=log)
        flush()
    generated = [Path(p) for row in manifest["outputs"] for p in row["outputs"]]
    ready = [p for p in generated if p.is_file()]
    quality = [Path(p) for side in ("RED", "BLUE") for row in manifest["outputs"]
               if row["side"] == side and row["mode"] == "third_cinema"
               for p in row["outputs"] if Path(p).is_file()]
    join_sources = quality if len(quality) == 2 else ready[:2]
    if len(ready) >= 2 and not (stop is not None and stop.is_set()):
        from .montage_fx import MONTAGE_LABELS, render_montage
        for style in MONTAGE_LABELS:
            if config is not None and style not in config["montage_styles"]:
                continue
            if stop is not None and stop.is_set():
                break
            (folder / "Transitions").mkdir(exist_ok=True)
            dest = folder / "Transitions" / f"transition_{style}.mp4"
            outcome = {"style": style, "label": MONTAGE_LABELS[style],
                       "outputs": [], "failed": []}
            try:
                applied = render_montage(join_sources, dest, style=style, logger=log, encoder_policy=template.encoder_policy)
                outcome["applied_style"] = applied
                if applied != style:
                    outcome["failed"].append(f"Requested {style}, applied {applied}")
                if dest.is_file():
                    outcome["outputs"] = [str(dest)]
                else:
                    outcome["failed"] = ["MP4 was not created"]
            except Exception as exc:
                outcome["failed"] = [f"{type(exc).__name__}: {exc}"]
                log(f"つなぎ演出テスト {style}: {exc}")
            manifest["montage_tests"].append(outcome)
            flush()
    if config is not None and len(join_sources) >= 2 and not (stop is not None and stop.is_set()):
        for style in config["spatial_transition_previews"]:
            if stop is not None and stop.is_set():
                break
            row = {"style": style, "label": TRANSITION_PREVIEWS[style], "outputs": [],
                   "failed": [], "qa_only": True, "no_audio": True}
            try:
                dest = folder / "Transitions" / "SpatialPreviews" / f"spatial_{style}.mp4"
                render_true_transition(join_sources[0], join_sources[1], dest, style,
                                       log=log, encoder_policy=template.encoder_policy)
                row["outputs"] = [str(dest)]
                row["render"] = json.loads(dest.with_suffix(".render.json").read_text())
            except Exception as exc:
                row["failed"].append(f"{type(exc).__name__}: {exc}")
                log(f"空間切替 {style} の確認動画を作成できません: {exc}")
            manifest["spatial_transition_tests"].append(row)
            flush()
    # Reuse the recorded clip, including its LoL audio, for motion QA.
    # Only the test badge is added: do not apply the clip's color/DOF twice.
    if ready and not (stop is not None and stop.is_set()):
        theme = normalize(template.kill_icon_style)
        if theme == "off":
            theme = "cinema"
        (folder / "KillFrames").mkdir(exist_ok=True)
        badge = folder / "KillFrames" / "badge_motion_qa_image.png"
        try:
            duration = min(3.0, get_duration(ready[0], ffmpeg=str(ffmpeg_exe())))
            if duration <= 0:
                raise ValueError("録画素材の長さを取得できません")
            make_badge(badge, theme)
            for motion, label in MOTION_STYLES.items():
                if config is not None and motion not in config["badge_motions"]:
                    continue
                if stop is not None and stop.is_set():
                    break
                dest = folder / "KillFrames" / f"badge_motion_{motion}.mp4"
                entry = {"motion": motion, "label": label, "outputs": [], "failed": []}
                try:
                    entry["render"] = render_badge_motion(
                        ready[0], dest, badge, theme, motion, duration,
                        encoder_policy=template.encoder_policy, log=log)
                    if not dest.is_file() or not dest.stat().st_size:
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
    # Cancellation skips optional frame extraction and packaging, preserving files.
    if not (stop is not None and stop.is_set()) and (config is None or config["include_visual_comparison"]):
        try:
            manifest["visual_qa"] = make_qa_contact_sheets(folder, manifest["outputs"], manifest["montage_tests"] +
                [dict(row, style="spatial_"+row["style"]) for row in manifest["spatial_transition_tests"]],
                log=log, transition_inputs=join_sources)
        except Exception as exc:
            manifest["visual_qa_error"] = str(exc)
            log(f"比較画像生成失敗（録画結果は保持）: {exc}")
    manifest["completed_clips"] = sum(bool(row["outputs"]) for row in manifest["outputs"])
    manifest["canceled"] = bool(stop is not None and stop.is_set())
    flush()
    if not manifest["canceled"]:
        manifest["qa_support"] = collect_qa_support(folder, log=log)
        flush()
        try:
            def update_archives(paths):
                manifest["qa_archives"] = [str(p) for p in paths]
                flush()
            split_test_results(folder, max_bytes=(config["max_zip_mb"] if config else 500)*1_000_000,
                               log=log, report_update=update_archives)
        except Exception as exc:
            manifest["qa_archives"] = []
            manifest["qa_packaging_error"] = f"{type(exc).__name__}: {exc}"
            log(f"テストZIP化に失敗。元MP4とJSONは保持: {exc}")
            flush()
    return folder / "results.json"
