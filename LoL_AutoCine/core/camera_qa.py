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
    project_root = Path(__file__).resolve().parents[1]
    installed_version = (project_root / "VERSION.txt").read_text(
        encoding="utf-8").strip()
    import hashlib
    camera_fingerprint = hashlib.sha256(
        (project_root / "core" / "camera.py").read_bytes() +
        (project_root / "core" / "camera_tuning.py").read_bytes()
    ).hexdigest()[:16]
    manifest = {
        "version": "5.10.26-test",
        "installed_version": installed_version,
        "camera_code_fingerprint": camera_fingerprint,
        "version_mismatch": installed_version != "5.10.26-test",
        "kind": "live_replay_camera_test",
        "expected_clips": len(scenarios),
        "test_plan": config,
        "test_plan_source": plan_source,
        "qa_archives": [],
        "outputs": [],
        "montage_tests": [],
        "spatial_transition_tests": [],
        "side_review_reels": {},
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
                    pose = json.loads(str(message).split(" ", 1)[1])
                    pose["geometry_validation"] = inspect_rig(pose)
                    current["camera_diagnostics"].append(pose)
                except (ValueError, IndexError, TypeError):
                    pass
            log(message)
        log(f"カメラテスト [{index}/{len(scenarios)}]: {side} / {label} / {player.label()} / {scene.time:.1f}s")
        if progress:
            progress(index-1, len(scenarios), round(100*(index-1)/len(scenarios),1), f"{side} {label} を録画中")
        try:
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
    # All RED and BLUE source videos are organized together, including a
    # single chronological review reel per side for one-click playback.
    manifest["side_review_reels"] = assemble_side_reels(folder, manifest["outputs"], log=log)
    flush()
    generated = [Path(p) for row in manifest["outputs"] for p in row["outputs"]]
    ready = [p for p in generated if p.is_file()]
    # Avoid basing transition QA on inverted camera #1: select good approved
    # cinematic footage from RED and BLUE where available.
    quality = [Path(p) for side in ("RED", "BLUE")
               for row in manifest["outputs"]
               if row["side"] == side and row["mode"] == "third_cinema"
               for p in row["outputs"] if Path(p).is_file()]
    join_sources = quality if len(quality) == 2 else ready[:2]
    if len(ready) >= 2 and not (stop is not None and stop.is_set()):
        from .montage_fx import MONTAGE_LABELS, render_montage
        for style in MONTAGE_LABELS:
            if config is not None and style not in config['montage_styles']:
                continue
            if stop is not None and stop.is_set():
                break
            fx_folder = folder / "Transitions"
            fx_folder.mkdir(parents=True, exist_ok=True)
            dest = fx_folder / f"transition_{style}.mp4"
            outcome = {"style": style, "label": MONTAGE_LABELS[style],
                       "outputs": [], "failed": []}
            try:
                applied = render_montage(join_sources, dest, style=style, logger=log)
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
    # True spatial transitions are QA-only examples, visually different from
    # the legacy ten brightness-based montage styles. Reuse saved MP4s.
    if len(join_sources) >= 2 and not (stop is not None and stop.is_set()):
        requested = (config or {}).get("spatial_transition_previews", list(TRANSITION_PREVIEWS))
        preview_dir = folder / "Transitions" / "SpatialPreviews"
        for style in requested:
            if stop is not None and stop.is_set():
                break
            row = {"style":style,"label":TRANSITION_PREVIEWS[style],
                   "outputs":[],"failed":[],"qa_only":True,"no_audio":True}
            try:
                dest = preview_dir / f"spatial_{style}.mp4"
                render_true_transition(join_sources[0],join_sources[1],dest,style,log=log)
                row["outputs"]=[str(dest)]
            except Exception as exc:
                row["failed"].append(f"{type(exc).__name__}: {exc}")
                log(f"空間切替 {style} の比較動画を作成できません: {exc}")
            manifest["spatial_transition_tests"].append(row)
            flush()
    # The eight camera QA clips intentionally disable kill badges so camera
    # geometry is unobstructed. Render six *separate* badge-motion clips from
    # an already-recorded MP4; otherwise the user cannot check entrance FX.
    if ready and not (stop is not None and stop.is_set()):
        from .kill_icons import STYLES
        theme = template.kill_icon_style if template.kill_icon_style in STYLES and template.kill_icon_style != "off" else "cinema"
        frame_folder = folder / "KillFrames"
        frame_folder.mkdir(parents=True, exist_ok=True)
        badge = frame_folder / "badge_motion_qa_image.png"
        try:
            make_badge(badge, theme)
            for motion, label in MOTION_STYLES.items():
                if config is not None and motion not in config['badge_motions']:
                    continue
                if stop is not None and stop.is_set():
                    break
                dest = frame_folder / f"badge_motion_{motion}.mp4"
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
    if config is None or config.get("include_visual_comparison", True):
        try:
            manifest["visual_qa"] = make_qa_contact_sheets(
                folder,manifest["outputs"],
                manifest["montage_tests"] +
                    [dict(entry, style="spatial_"+entry["style"])
                     for entry in manifest.get("spatial_transition_tests",[])],
                log=log, transition_inputs=join_sources)
        except Exception as visual_error:
            manifest["visual_qa_error"] = str(visual_error)
            log("比較画像生成失敗（録画・ZIP作成は継続）: " + str(visual_error))
    manifest["completed_clips"] = sum(bool(row["outputs"]) for row in manifest["outputs"])
    manifest["canceled"] = bool(stop is not None and stop.is_set())
    flush()
    # Always include an upload-ready, human-readable report and bounded
    # diagnostics, together with the MP4s and image contact sheets. Copying
    # diagnostics is best-effort and never invalidates a successful render.
    support_dir = folder / "QA_Support"
    support_dir.mkdir(parents=True, exist_ok=True)
    notes = (
        "# AutoCine 一括テスト結果\\n\\n"
        "このフォルダーを個別に開かず、作成されたpart ZIPをすべてアップロードしてください。\\n"
        "results.json：撮影・切替・キルフレーム・計画ID・失敗の一覧。\\n"
        "RED_camera_3frames.jpg / BLUE_camera_3frames.jpg：キル前・瞬間・後の比較。\\n"
        "RED/BLUE各フォルダーの*_camera_review_all.mp4：カメラごとの連続比較。\\n"
        "Transitions：場面切替の比較動画。 KillFrames：登場動作。\\n"
        "QA_Support：最新の診断ログ断片。\\n"
        f"実行版：{installed_version}（カメラコードID：{camera_fingerprint}）。\\n"
        "古いresults.json（例：5.10.23-test）の映像と混同しないでください。\\n"
        "flat_upper_background_ratioは空・マップ外の可能性を示す目安であり、キル検出ではありません。\\n"
        "映像内の対象の位置が適切かはWindows実機で目視確認が必要です。\\n"
    ).replace("\\n", "\n")
    (support_dir / "READ_ME_FIRST_JA.md").write_text(notes, encoding="utf-8")
    origin = Path(__file__).resolve().parents[1] / "diagnostics"
    for filename in ("runtime.log", "crash.log", "last_error.txt", "audio.log",
                     "capture.log", "selftest_latest.json"):
        source = origin / filename
        if not source.is_file():
            continue
        try:
            # Prevent a multi-GB lifetime log from inflating every QA archive.
            with source.open("rb") as handle:
                handle.seek(max(0, source.stat().st_size - 1_000_000))
                content = handle.read()
            (support_dir / filename).write_text(
                content.decode("utf-8", errors="replace"), encoding="utf-8")
        except OSError as exc:
            log("診断ログの追加をスキップ: " + str(exc))
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
