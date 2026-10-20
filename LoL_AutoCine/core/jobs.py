# -*- coding: utf-8 -*-
"""全自動編集ジョブ: 固定プレイヤーのキルだけを 1 クリップずつ録画 -> エフェクト -> MP4。

ポイント
- ジョブ開始時にプレイヤー(slot/名前/チャンピオン)を固定。途中でUI選択が変わっても影響しない
- 各クリップ録画前に毎回同じプレイヤーをカメラ対象にする (地面に埋まる配置は検証して回避)
- 録画中は HUD をすべて隠し、終了時に元へ戻す
- ゲーム音を同時に録音して MP4 に合成 (取れない場合は警告して無音で続行)
- 再生が進まない(同じ画面を録画し続ける)状態を検知して復旧 / 中止する
"""
from __future__ import annotations
from copy import deepcopy
import re
import time
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from .audio import AudioCapture, AudioError
from .audio_log import log as audio_log
from .camera import CameraPlan, side_yaw_for, live_side_profile, CameraDirector, RigInfo, attach_to_player
from .capture import FrameSource, CaptureError, WGCWindowSource
from .effects import Template, apply_effects, concat_clips
from .hud import hide_hud, restore_hud
from .render_fx import apply_fx, restore_fx
from .players import Player, norm
from .recorder import ClipRecorder
from .replay_api import ReplayAPI, ReplayApiError
from .scanner import group_clips


class StallError(Exception):
    pass


def safe_name(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", s).strip("_") or "player"

def unique_path(path: Path) -> Path:
    """既存ファイルを上書きせず空き名を返す。"""
    path=Path(path)
    if not path.exists():
        return path
    for i in range(1,10000):
        q=path.with_name(f"{path.stem}_{i:03d}{path.suffix}")
        if not q.exists():
            return q
    raise RuntimeError(f"出力ファイル名を確保できません: {path}")


@dataclass
class ClipTake:
    duration: float = 0.0
    audio_path: Optional[Path] = None
    audio_offset: float = 0.0
    rig: Optional[RigInfo] = None
    cam_errors: int = 0
    effect_events: Optional[list] = None  # optional recording-time event coordinates
    qa_event_times: Optional[list] = None  # QA-only observations; never enables video effects


@dataclass
class JobResult:
    outputs: list = field(default_factory=list)
    montage: Optional[Path] = None
    failed: list = field(default_factory=list)


def _play_until(api: ReplayAPI, end: float, start: float, tpl: Template, rec: Optional[ClipRecorder], stop,
                limit_extra: float = 25.0, observe=None) -> None:
    """end まで再生しつつ、停止検知 (同じ画面を録り続けない) を行う。"""
    t_begin = time.time()
    last_t, last_move = -1.0, time.time()
    min_speed = 0.35 if (tpl.style in ("cinema", "cinema_top", "third_cinema", "lolnam_cinema", "geo_aim")
                         or getattr(tpl, "camera_control_mode", None) == "full_auto") else 1.0
    wall_limit = (end - start) / min_speed + limit_extra
    while True:
        if stop is not None and stop.is_set():
            return
        t = float(api.playback().get("time", 0.0))
        if observe is not None:
            observe(t, time.perf_counter())
        if t >= end:
            return
        if t > last_t + 0.02:
            last_t, last_move = t, time.time()
        else:
            idle = time.time() - last_move
            if idle > 1.5:
                api.set_playback(paused=False)
            if idle > 8.0:
                raise StallError("再生が止まっています (同じ画面を録画しないよう中止しました)。")
        if rec is not None and rec.error:
            raise CaptureError(rec.error)
        if time.time() - t_begin > wall_limit:
            raise StallError("録画がタイムアウトしました。")
        time.sleep(0.05)


def _prime_live_replay_once(api: ReplayAPI, source: FrameSource, start: float,
                            stop=None, log: Callable = lambda m: None) -> None:
    """Initialize the LoL 3D replay renderer before the first Windows recording.

    When Replay API is responsive but playback has never actually run, a seek
    can report the requested time while WGC still shows the initial Nexus.
    A short *automatic* play of the pre-roll initializes the game scene.
    `_setup_clip` then seeks back to the exact requested start time.
    Never restart WGC or capture the desktop; reuse the existing session.
    """
    if not isinstance(source, WGCWindowSource) or getattr(api, '_autocine_record_primed', False):
        return
    if stop is not None and stop.is_set():
        raise StallError('開始前に停止されました')
    log('初回クリップ: リプレイ映像を自動準備中（手動再生は不要）…')
    api.set_playback(paused=True, speed=1.0)
    # Starting a little before the clip leaves room for the warming animation;
    # never prime at 0 unless this really is a near-zero-time clip.
    api.seek(max(0.0, float(start) - 1.5))
    first_time = float(api.playback().get('time', 0.0))
    base_frames = source.frame_count
    advanced = False
    fresh = False
    try:
        for attempt in range(2):
            api.set_playback(paused=False, speed=1.0)
            deadline = time.monotonic() + 1.25
            while time.monotonic() < deadline:
                if stop is not None and stop.is_set():
                    raise StallError('開始前に停止されました')
                time.sleep(0.09)
                state = api.playback()
                advanced |= float(state.get('time', first_time)) > first_time + 0.18
                fresh |= source.frame_count > base_frames
                if advanced and fresh:
                    # Allow the renderer to draw a gameplay frame, not the old
                    # static Nexus still cached by Windows Graphics Capture.
                    time.sleep(0.35)
                    break
            if advanced and fresh:
                break
    finally:
        api.set_playback(paused=True, speed=1.0)
    if stop is not None and stop.is_set():
        raise StallError('開始前に停止されました')
    if not advanced or not fresh:
        raise CaptureError('初回リプレイ画面の準備が完了しませんでした。LoLのリプレイ画面を表示し、再試行してください。')
    # Flag only when verified; failures can retry on the next attempt.
    api._autocine_record_primed = True
    log('初回クリップ: 再生・ゲーム映像フレームを確認、正確な開始時刻へ戻します')


def _await_capture_refresh(source: FrameSource, after_count: int, timeout: float = 1.5,
                           stop=None) -> None:
    """Do not record the pre-seek frame cached by WGC after moving the camera."""
    if not isinstance(source, WGCWindowSource):
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if stop is not None and stop.is_set():
            raise StallError('開始前に停止されました')
        frame = source.latest()  # Propagate a dead worker's actual error promptly.
        if source.frame_count > after_count and frame is not None:
            return
        time.sleep(0.05)
    if stop is not None and stop.is_set():
        raise StallError('開始前に停止されました')
    raise CaptureError('シーク後にLoL映像が更新されませんでした。古いネクサス映像の録画を防ぐため中止します。')


def _prepare_clip_capture(api, source, player, tpl, start, kills, stop, log):
    """Recover one stalled seek without recording old frames or shifting a clip."""
    _prime_live_replay_once(api, source, start, stop=stop, log=log)
    plan, rig = _setup_clip(api, player, tpl, start, kills, log)
    pose_frame_baseline = source.frame_count if getattr(plan, "_prepare_pose_before_capture", False) else None
    _apply_initial_camera_pose(api, plan, start, stop, log)
    try:
        _await_capture_refresh(source, source.frame_count if pose_frame_baseline is None else pose_frame_baseline, stop=stop)
        return plan, rig
    except CaptureError as exc:
        if not isinstance(source, WGCWindowSource):
            raise
        if stop is not None and stop.is_set():
            raise StallError('開始前に停止されました') from exc
        log(f'映像入力を1回だけ復旧します（録画はまだ開始しません）: {exc}')
    # Reuse a healthy mirror; restart only a terminated capture session.
    if not source.running:
        source.stop()
        source.start()
    api._autocine_record_primed = False
    _prime_live_replay_once(api, source, start, stop=stop, log=log)
    # Playing the pre-roll produced verified, moving frames. Seek back to the
    # exact requested time and require another frame after this new setup began.
    # A paused replay may deliver it DURING setup, then stop emitting frames.
    baseline = source.frame_count
    plan, rig = _setup_clip(api, player, tpl, start, kills, log)
    if getattr(plan, "_prepare_pose_before_capture", False):
        baseline = source.frame_count
    _apply_initial_camera_pose(api, plan, start, stop, log)
    _await_capture_refresh(source, baseline, stop=stop)
    log('映像入力の復旧を確認、指定の開始時刻から録画します')
    return plan, rig


def _apply_initial_camera_pose(api, plan, start, stop, log):
    """Confirm repaired presets' final pose BEFORE recorder/audio clocks start.

    Previously attach validated a provisional pose, but the first director
    POST replaced it after capture started. The accepted RED #3/#5 path is
    deliberately untouched. Invalid acknowledgements abort, never record an
    unverified stale camera while reporting success.
    """
    if not getattr(plan, "_prepare_pose_before_capture", False) or plan.rig.mode != "fps":
        return
    offset = plan.offset_at(start)
    rotation = plan.rotation_at(start)
    if rotation is None:
        raise ReplayApiError("録画前のカメラ視線を構成できません")
    body = {"selectionName": plan.sel_name, "cameraMode": "fps", "cameraAttached": True,
            "selectionOffset": dict(zip(("x", "y", "z"), offset)),
            "cameraRotation": rotation, "fieldOfView": plan.fov_at(start)}
    for attempt in range(3):
        if stop is not None and stop.is_set():
            raise StallError("録画前のカメラ確認を中止しました")
        if attempt in (0, 2):
            api.set_render(**body)
        time.sleep(.08)
        state = api.render()
        try:
            off = state["selectionOffset"]
            rot = state["cameraRotation"]
            valid = (state.get("cameraMode") == "fps"
                     and state.get("cameraAttached") is True
                     and norm(state.get("selectionName", "")) in plan._target_aliases
                     and all(abs(float(off[k])-float(body["selectionOffset"][k])) <= 2.0 for k in ("x","y","z"))
                     and all(abs((float(rot[k])-float(rotation[k])+180.0)%360.0-180.0) <= .5 for k in ("x","y","z"))
                     and abs(float(state["fieldOfView"])-float(body["fieldOfView"])) <= .5)
        except (KeyError, TypeError, ValueError, OverflowError):
            valid = False
        log("CAMERA_QA_INITIAL_POSE " + json.dumps({
            "attempt": attempt+1, "verified": valid, "requested_offset": body["selectionOffset"],
            "requested_rotation": rotation, "observed_offset": state.get("selectionOffset"),
            "observed_rotation": state.get("cameraRotation"), "observed_mode": state.get("cameraMode"),
            "selection_verified": norm(state.get("selectionName", "")) in plan._target_aliases,
        }, ensure_ascii=False))
        if valid:
            return
    raise ReplayApiError("録画前のカメラ姿勢が反映されません。元映像の取り違えを防ぐため中止します")


def _setup_clip(api: ReplayAPI, player: Player, tpl: Template, start: float, kills: list,
                log: Callable) -> tuple:
    api.set_playback(paused=True, speed=1.0)
    actual = api.seek(start)
    if actual is not None and abs(float(actual) - float(start)) > 0.80:
        actual = api.seek(start)
    if actual is not None and abs(float(actual) - float(start)) > 0.80:
        raise ReplayApiError(f'リプレイのシーク位置が確定しません ({actual:.2f}s / 目標 {start:.2f}s)')
    from .smart_camera_director import decide_camera
    side_choice = getattr(tpl, 'camera_side', 'auto')
    decision_side = {'blue': 'BLUE', 'red': 'RED'}.get(side_choice, getattr(player, 'team', 'ORDER'))
    try:
        decision = decide_camera(getattr(tpl, "camera_control_mode", None),
                                 decision_side, tpl.style,
                                 (k.time for k in kills),
                                 approved=getattr(tpl, "camera_auto_qa_approved", None),
                                 excluded=getattr(tpl, "camera_auto_excluded", ()))
    except ValueError as error:
        log("SMART_CAMERA_FALLBACK " + json.dumps({"reason":str(error), "capture_refused":True, "visual_qa_pass":False}))
        raise ReplayApiError("使用可能なカメラ候補がありません。サイド別の除外設定を確認してください。") from error
    log("SMART_CAMERA_DECISION " + json.dumps(decision.to_dict(), ensure_ascii=False))
    if decision.mode is not None:
        tpl = deepcopy(tpl)  # runtime selection never modifies the project/UI
        tpl.style = decision.style
        tpl.smart_composition = decision.mode in ("fixed_auto", "full_auto")
        if decision.mode == "manual":
            tpl.auto_director_strength = 0.0
    auto_camera = decision.mode in ("fixed_auto", "full_auto")
    side_choice = getattr(tpl, 'camera_side', 'auto')
    profile = live_side_profile(getattr(player, 'team', 'ORDER'), side_choice, style=tpl.style)
    live_third = tpl.style in ('third', 'third_cinema', 'lolnam_cinema', 'geo_aim')
    elev = max(float(getattr(tpl, 'third_elev', 28.0)), profile['elevation']) if live_third else float(getattr(tpl, 'third_elev', 28.0))
    dist = max(float(getattr(tpl, 'third_dist', 950.0)), profile['distance']) if live_third else float(getattr(tpl, 'third_dist', 950.0))
    attach_options = {"safe_axes": True} if auto_camera else {}
    rig = attach_to_player(api, player, tpl.style, dist_scale=tpl.dist_scale, height=tpl.cam_height,
                           third_elev=elev, third_dist=dist, log=log, **attach_options)
    time.sleep(0.35)
    plan = CameraPlan(style=tpl.style, intensity=tpl.amp(), kill_time=kills[0].time,
                      kill_times=tuple(k.time for k in kills), dist_scale=tpl.dist_scale, height=tpl.cam_height,
                      third_elev=elev, third_dist=dist,
                       third_yaw=getattr(tpl, "third_yaw", 0.0),
                      motion_arc=getattr(tpl, "motion_arc", 0.0), motion_dolly=getattr(tpl, "motion_dolly", 0.0),
                      motion_profile=getattr(tpl, "motion_profile", "cinematic"),
                      scene_keyframes=tuple(deepcopy(getattr(tpl, 'scene_keyframes', ()) or ())),
                       smart_composition=bool(getattr(tpl, 'smart_composition', False)),
                       smart_impact=(float(getattr(tpl, 'highlight_pulse', 0.0))
                                     if getattr(tpl, 'smart_highlight_enabled', False) else 0.0), rig=rig,
                       side_yaw=((profile['yaw'] - 8.0 if tpl.style == 'third' and side_choice == 'auto' and str(getattr(player, 'team', '')).upper() in ('CHAOS', 'RED') else profile['yaw']) if live_third else 0.0),
                       team=getattr(player, 'team', 'ORDER'),
                      sel_name=player.selection_name or player.champion)
    plan.camera_control_mode = decision.mode
    plan._camera_decision = decision.to_dict()
    plan._decision_log = log
    plan._auto_director_strength = getattr(tpl, "auto_director_strength", None)
    plan._target_aliases = frozenset(player.aliases() if hasattr(player, "aliases") else
                                     {norm(player.selection_name), norm(player.champion)})
    plan._camera_axis_safety = tpl.style in ('third', 'geo_aim')
    # Mode-specific composition and axis policy. The accepted RED3/5 retain
    # their numeric behavior; repaired modes share only the measured API math.
    from .camera_tuning import shot_tuning, target_center_rotation, live_framing_policy
    shot = shot_tuning(getattr(player, "team", "ORDER"), tpl.style)
    framing = live_framing_policy(getattr(player, "team", "ORDER"), tpl.style)
    plan._live_dist_factor = shot["distance"]
    plan._live_fps_back = shot["fps_back"]
    plan._live_angle_bias = ({} if tpl.style == "fps" and side_choice != "auto" else shot["angles"])
    plan._live_red_target_center = (
        str(getattr(player, "team", "")).upper() in ("CHAOS", "RED")
        and tpl.style in ("third", "fps") and side_choice == "auto"
    )
    # Explicit manual third headings retain the previous small correction.
    if (str(getattr(player, "team", "")).upper() in ("CHAOS", "RED")
            and tpl.style == "third" and side_choice != "auto"):
        plan._live_angle_bias = {"x": 4.0}
    # Keep older flags for direct callers. The measured engine target-lock
    # policy below supersedes the rejected BLUE/RED2/RED4 rotation layouts.
    blue = str(getattr(player, 'team', '')).upper() in ('ORDER', 'BLUE')
    plan._live_blue_geo_look = blue and tpl.style in ('third', 'third_cinema', 'lolnam_cinema')
    plan._live_blue_pulled_back = blue and tpl.style == 'third'
    plan._live_fps_recenter = tpl.style == 'fps'
    if plan._live_fps_recenter:
        # RED FPS #3: target-relative position must use the same ~192-degree
        # RED side heading as cameraRotation; previously position used yaw=0
        # while rotation aimed backwards at yaw=192, showing empty terrain.
        plan._live_fps_side_heading = profile["yaw"]
    plan._live_red_normal_reframe = (not blue and tpl.style == 'third' and side_choice == 'auto')
    plan._live_engine_target_lock = framing["target_lock"]
    if framing["target_lock"]:
        # Old biases compensated a swapped axis; applying them to correct
        # Replay axes would turn the lens away from the attached target again.
        plan._live_angle_bias = {}
    red_normal_pullback = not blue and tpl.style == 'third' and side_choice == 'auto'
    if red_normal_pullback:
        plan._live_dist_factor *= framing["distance_extra"]
    plan._prepare_pose_before_capture = framing["target_lock"] or red_normal_pullback
    if auto_camera:
        plan._live_engine_target_lock = rig.mode == "fps"
        plan._live_angle_bias = {}
        plan._prepare_pose_before_capture = rig.mode == "fps"
        if rig.fell_back:
            log("SMART_CAMERA_FALLBACK " + json.dumps({"reason": rig.note,
                "requested_style": decision.style, "actual_mode": rig.mode,
                "visual_qa_pass": False}, ensure_ascii=False))
    # QA-only readout: compare RED/BLUE rotations and positions numerically.
    # Logging itself adds no Replay API writes.
    if str(getattr(tpl, "name", "")).startswith("CameraQA "):
        try:
            log("CAMERA_QA_POSE " + json.dumps({
                "side": str(getattr(player, "team", "?")),
                "style": str(tpl.style),
                "time": float(start),
                "camera_mode": str(rig.mode),
                "third_person_enabled": bool(rig.third),
                "pitch_axis": str(rig.pitch_axis),
                "pitch_sign": float(rig.pitch_sign),
                "pitch_complement": bool(rig.pitch_complement),
                "baseline_rotation": rig.rot,
                "baseline_player_position": rig.P,
                "baseline_horizontal_direction": rig.h,
                "baseline_offset": rig.v,
                "rig_fell_back": bool(rig.fell_back),
                "rig_note": str(rig.note),
                "planned_fov_degrees": float(plan.fov_at(start)),
                "side_heading_degrees": float(plan.side_yaw),
                "initial_camera_offset": plan.offset_at(start),
                "initial_camera_rotation": plan.rotation_at(start),
                "shot_tuning": shot,
                "applied_angle_bias": dict(plan._live_angle_bias),
                "red_target_center_enabled": bool(plan._live_red_target_center),
                "target_center_rotation": (target_center_rotation(plan.offset_at(start))
                                           if plan._live_red_target_center else None),
                "fps_target_relative": bool(tpl.style == "fps" and getattr(plan, "_live_fps_recenter", False)),
                "engine_target_lock_enabled": bool(plan._live_engine_target_lock),
                "framing_policy": framing,
                "rotation_contract": ("X_yaw_Y_downward_pitch_Z_zero" if plan._live_engine_target_lock else "protected_legacy_mode"),
            }, ensure_ascii=False, default=str))
        except Exception as diagnostic_error:
            log(f"カメラQA数値ログ取得失敗（録画は継続）: {diagnostic_error}")
    if rig.mode == "top" and tpl.style in ("cinema", "follow"):
        plan.style = "cinema_top" if tpl.style == "cinema" else "top"   # 実際に使えるモードに合わせる
    if plan.style in ("third", "third_cinema", "lolnam_cinema", "geo_aim"):
        log(f"カメラサイド基準: 所属={getattr(player, 'team', 'ORDER')} / "
            f"設定={side_choice} / 校正済み水平補正={plan.side_yaw:.0f}° "
            f"/ 高さ角={elev:.0f}° / 距離={dist:.0f} (世界座標を二重反転しない)")
    return plan, rig


def _recording_event_observer(kills, replay_start, wall_start, events):
    """Interpolate existing playback observations onto the normalized video clock."""
    pending = sorted(float(k.time) for k in kills)
    previous = [float(replay_start), float(wall_start)]
    def observe(replay_time, wall_time):
        old_replay, old_wall = previous
        if replay_time <= old_replay:
            return
        while pending and pending[0] <= replay_time:
            target = pending.pop(0)
            if target >= old_replay:
                fraction = (target - old_replay) / (replay_time - old_replay)
                center = max(0.0, old_wall + fraction * (wall_time - old_wall) - wall_start)
                events.append((center, center + .42))
        previous[:] = [float(replay_time), float(wall_time)]
    return observe



def restore_mirror_camera(api: ReplayAPI, player: Player, fov: float,
                          log: Callable = lambda m: None) -> None:
    """Restore a *safe visible* replay view after a cinematic job.

    A zero selectionOffset with cameraMode='fps' keeps the camera attached to
    the champion and can place the camera inside the character/terrain. Reset
    the camera mode and its attachment together. This changes only the live
    Replay API view; the already-rendered MP4 is untouched.
    """
    try:
        api.set_playback(paused=True, speed=1.0)
    except ReplayApiError as exc:
        log(f"ミラー復帰: 再生停止を確認できません: {exc}")
    sel = getattr(player, 'selection_name', '') or getattr(player, 'champion', '')
    try:
        api.set_render(selectionName=sel, cameraMode="top", cameraAttached=True,
                       selectionOffset={"x": 0, "y": 0, "z": 0}, fieldOfView=fov)
        log("ミラー復帰: 対象チャンピオンの安全な俯瞰追従カメラに戻しました")
    except ReplayApiError as exc:
        log(f"ミラー復帰: カメラ切替失敗: {exc}")
        try:
            api.set_render(cameraMode="top", cameraAttached=True)
        except ReplayApiError as retry:
            log(f"ミラー復帰: 再試行失敗（リプレイの接続を確認）: {retry}")


def record_one_clip(api: ReplayAPI, source: FrameSource, player: Player, tpl: Template,
                    start: float, end: float, kills: list, raw_path: Path, stop=None,
                    log: Callable = lambda m: None,
                    audio_factory: Optional[Callable] = None) -> ClipTake:
    """1クリップ録画。HUD非表示は呼び出し側 (run_auto_edit) が行う。"""
    try:
        plan, rig = _prepare_clip_capture(api, source, player, tpl, start, kills, stop, log)
    except Exception:
        try:
            if player is not None:
                restore_mirror_camera(api, player, 65.0, log)
        except Exception as restore_error:
            log(f"準備失敗後のミラー復帰をスキップ: {restore_error}")
        raise
    take = ClipTake(rig=rig)
    saved_hud = {}
    if tpl.hide_hud:
        saved_hud = hide_hud(api, tpl.keep_champion_bars)
    fx_saved = {}
    try:
        cam_dist = plan.third_dist if getattr(rig, "third", False) else None
        if cam_dist is None and rig is not None and rig.v is not None:
            cam_dist = sum(float(x) * float(x) for x in rig.v) ** 0.5
        fx_saved = apply_fx(api, tpl, cam_dist=cam_dist)
    except ReplayApiError as e:
        log(f"ゲーム内エフェクトを適用できません (録画は継続): {e}")
    audio: Optional[AudioCapture] = None
    if audio_factory is not None and tpl.game_audio:
        try:
            audio_path = raw_path.with_suffix(".wav")
            audio_log(f"clip audio start path={audio_path}")
            log("音声: LoLゲーム音の録音を開始します")
            audio = audio_factory(audio_path)
            audio.start()
            log("音声: 録音開始OK")
        except AudioError as e:
            audio_log(f"clip audio start failed: {type(e).__name__}: {e}", "ERROR")
            log(f"音声: 録音開始失敗 → {e}")
            # Start can fail after camera setup. Never leave the LoL mirror inside the rig.
            restore_hud(api, saved_hud)
            restore_fx(api, fx_saved)
            restore_mirror_camera(api, player, plan.base_fov, log)
            raise AudioError(f"LoLゲーム音の準備に失敗しました: {e}") from e
    director = CameraDirector(api, plan)
    # CameraDirector has its own 144Hz motion clock. Do not encode and then
    # normalize a 144fps intermediate when the requested video is only 60fps.
    recording_fps = min(tpl.capture_fps, tpl.fps)
    log(f"動画: 録画 {recording_fps}fps / 加工・出力 {tpl.fps}fps")
    rec = ClipRecorder(source, raw_path, fps=recording_fps)
    rec.encoder_policy = getattr(tpl, 'encoder_policy', 'auto')
    try:
        rec.start()
        director.start()
        api.set_playback(paused=False, speed=1.0)
        observe = None
        if (getattr(tpl, "kill_icon_style", "off") != "off"
                or getattr(tpl, "smart_composition", False)):
            take.effect_events = []
            observe = _recording_event_observer(kills, start, rec.started_perf, take.effect_events)
        if str(getattr(tpl, "name", "")).startswith("CameraQA "):
            take.qa_event_times = []
            qa_observe = _recording_event_observer(kills, start, rec.started_perf, take.qa_event_times)
            prior_observe = observe
            def observe(replay_time, wall_time):
                qa_observe(replay_time, wall_time)
                if prior_observe is not None:
                    prior_observe(replay_time, wall_time)
        _play_until(api, end, start, tpl, rec, stop, observe=observe)
    finally:
        director.stop()
        # Stop replay/game rendering before waiting for FFmpeg finalization and
        # timing normalization. It otherwise keeps running during that work.
        try:
            api.set_playback(paused=True, speed=1.0)
        except ReplayApiError as exc:
            log(f'録画後の一時停止を再試行します: {exc}')
        recorder_error = None
        try:
            take.duration = rec.stop()
        except CaptureError as e:
            # 復元処理を完了してからクリップ単位の失敗として返す。
            take.duration = rec.elapsed
            recorder_error = e
        # Recorder is stopped: release the temporary 3rd-person camera now,
        # even if LoL audio validation below raises an exception.
        restore_hud(api, saved_hud)
        restore_fx(api, fx_saved)
        restore_mirror_camera(api, player, plan.base_fov, log)
        if take.qa_event_times is not None:
            log("CAMERA_QA_TIMING " + json.dumps({
                "replay_start": float(start), "event_replay_times": [float(k.time) for k in kills],
                "event_video_seconds": [float(v[0]) for v in take.qa_event_times],
                "recording_duration": float(take.duration),
                "basis": "recording_wall_clock_interpolated_replay_observations",
            }))
        take.cam_errors = director.errors
        log(f"カメラ動作診断: API送信 {director.api_calls}回 / 25ms超 {director.api_slow_calls}回 / "
            f"最大API待ち {director.max_api_latency_ms:.1f}ms / 最大時刻ずれ {director.max_clock_drift:.3f}s")
        if audio is not None:
            try:
                stopped_dur = audio.stop()
                audio_log(f"clip audio stop duration={stopped_dur:.3f}s path={audio.path}")
                if not audio.path.exists() or audio.path.stat().st_size < 1024:
                    raise AudioError("LoL音声WAVが空です")
                # WAVヘッダ上の実時間も確認。短すぎる録音は最終MP4へ混ぜず原因を明示する。
                import wave
                with wave.open(str(audio.path), "rb") as wf:
                    wav_rate = int(wf.getframerate())
                    wav_channels = int(wf.getnchannels())
                    wav_frames = int(wf.getnframes())
                    wav_dur = wav_frames / float(max(1, wav_rate))
                    # 完全無音WAVを「録音成功」と扱わない。先頭から数秒をサンプリングして
                    # 少なくとも1サンプルに非ゼロ信号があるか確認する。ゲームが静かな瞬間
                    # だけなら後段で正常に扱えるよう、全体を数秒ずつ確認する。
                    nonzero = False
                    remaining = wf.getnframes()
                    while remaining > 0 and not nonzero:
                        chunk = wf.readframes(min(wf.getframerate(), remaining))
                        if any(b != 0 for b in chunk):
                            nonzero = True
                        remaining -= min(wf.getframerate(), remaining)
                if wav_dur < max(0.25, min(1.0, take.duration * 0.25)):
                    raise AudioError(f"LoL音声の録音時間が短すぎます ({wav_dur:.2f}s / 映像 {take.duration:.2f}s)")
                if not nonzero:
                    raise AudioError("LoL音声WAVが完全な無音です。Windowsの出力デバイス/LoL音量を確認してください")
                take.audio_path = audio.path
                take.audio_offset = max(0.0, rec.started_perf - audio.t0)
                log(f"LoL音声OK: {wav_dur:.2f}s / offset {take.audio_offset:.3f}s")
                audio_log(f"WAV validated duration={wav_dur:.3f}s rate={wav_rate} channels={wav_channels} frames={wav_frames} size={audio.path.stat().st_size}")
            except Exception as e:  # noqa: BLE001
                audio_log(f"WAV validation failed: {type(e).__name__}: {e}", "ERROR")
                if tpl.game_audio:
                    raise AudioError(f"LoLゲーム音を確実に収録できません: {e}") from e
                log(f"音声の停止処理でエラー: {e}")
        # The temporary camera was already released immediately after rec.stop().
    if recorder_error is not None:
        raise recorder_error
    return take


def preview_clip(api: ReplayAPI, player: Player, tpl: Template, start: float, end: float, kills: list,
                 stop=None, log: Callable = lambda m: None) -> RigInfo:
    """録画せずに、テンプレートのカメラ演出(追従/ズーム/スロー/HUD非表示)をLoL上で再生して確認する。"""
    try:
        plan, rig = _setup_clip(api, player, tpl, start, kills, log)
        if plan.camera_control_mode in ("fixed_auto", "full_auto"):
            _apply_initial_camera_pose(api, plan, start, stop, log)
    except Exception:
        try:
            if player is not None:
                restore_mirror_camera(api, player, 65.0, log)
        except Exception as restore_error:
            log(f"準備失敗後のミラー復帰をスキップ: {restore_error}")
        raise
    director = CameraDirector(api, plan)
    cam_dist = plan.third_dist if getattr(rig, "third", False) else None
    if cam_dist is None and rig is not None and rig.v is not None:
        cam_dist = sum(float(x) * float(x) for x in rig.v) ** 0.5
    fx_saved = apply_fx(api, tpl, cam_dist=cam_dist)
    saved_hud = hide_hud(api, tpl.keep_champion_bars) if tpl.hide_hud else {}
    try:
        director.start()
        api.set_playback(paused=False, speed=1.0)
        _play_until(api, end, start, tpl, None, stop)
    finally:
        director.stop()
        log(f"プレビューカメラ診断: API送信 {director.api_calls}回 / "
            f"25ms超 {director.api_slow_calls}回 / "
            f"最大API待ち {director.max_api_latency_ms:.1f}ms / "
            f"最大時刻ずれ {director.max_clock_drift:.3f}s")
        restore_hud(api, saved_hud)
        restore_fx(api, fx_saved)
        restore_mirror_camera(api, player, plan.base_fov, log)
    return rig


def run_auto_edit(api: ReplayAPI, source: FrameSource, player: Player, kills: list, tpl: Template,
                  out_root: Path, make_montage: bool = True,
                  progress: Optional[Callable] = None, stop=None,
                  log: Callable = lambda m: None,
                  audio_factory: Optional[Callable] = None) -> JobResult:
    """progress(done, total, pct, message)"""
    res = JobResult()
    out_dir = Path(out_root) / f"{safe_name(player.name)}_{safe_name(player.champion)}"
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    clips = group_clips(kills, tpl.pre, tpl.post, tpl.merge_multikill)
    total = len(clips)
    if total == 0:
        log("対象プレイヤーのキルがありません。")
        return res
    hud_desc = ("体力バー中心（名前表示はLoL側設定）" if tpl.hide_hud and tpl.keep_champion_bars
                else "HUD非表示" if tpl.hide_hud else "通常HUD")
    log(f"対象: {player.label()} / {total} クリップを作成します"
        + f" / HUD: {hud_desc}" + (" / ゲーム音あり" if audio_factory and tpl.game_audio else ""))
    # HUD flags are applied once per clip by record_one_clip(), not on every frame.
    # Name visibility is deliberately left to LoL settings; no unsupported API property is sent.
    try:
        for i, (s, e, ks) in enumerate(clips, 1):
            if stop is not None and stop.is_set():
                log("中断しました。")
                break
            raw = unique_path(raw_dir / f"raw_{i:03d}.mp4")
            final = unique_path(out_dir / f"kill_{i:03d}.mp4")
            if progress:
                progress(i - 1, total, 100.0 * (i - 1) / total, f"クリップ {i}/{total} を録画中…")
            try:
                take = record_one_clip(api, source, player, tpl, s, e, ks, raw, stop, log, audio_factory)
                if take.rig is not None and i == 1:
                    log("カメラ: " + (take.rig.note or take.rig.mode))
                if progress:
                    progress(i - 1, total, 100.0 * (i - 0.5) / total, f"クリップ {i}/{total} にエフェクト適用中…")
                timing = {"effect_events": take.effect_events} if take.effect_events is not None else {}
                apply_effects(raw, final, tpl, take.duration, ks, game_wav=take.audio_path,
                              audio_trim=take.audio_offset, **timing)
                res.outputs.append(final)
                log(f"保存: {final.name} ({take.duration:.1f}s, {len(ks)}キル"
                    + (", 音声あり" if take.audio_path else "") + ")")
            except Exception as ex:  # 1クリップの異常でUI/後続処理を落とさない
                res.failed.append((i, f"{type(ex).__name__}: {ex}"))
                log(f"クリップ {i} 失敗: {type(ex).__name__}: {ex}")
                try:
                    import traceback
                    log(traceback.format_exc().strip()[-1200:])
                except Exception:
                    pass
                # Replay APIが落ちた場合、後続クリップを無理に叩かない。
                # 接続が復帰していれば次へ進めるが、拒否された状態なら安全停止。
                msg = str(ex).lower()
                if "winerror 10061" in msg or "connection refused" in msg or "接続できません" in str(ex):
                    log("Replay APIとの接続が切れたため、後続クリップを安全のため中止します。リプレイを再起動してから再実行してください。")
                    break
                if isinstance(ex, StallError):
                    try:
                        api.set_playback(paused=False)
                    except ReplayApiError:
                        pass
            if progress:
                progress(i, total, 100.0 * i / total, f"{i}/{total} 完了")
    finally:
        pass
    if make_montage and len(res.outputs) >= 2:
        try:
            m = unique_path(out_dir / "montage.mp4")
            if getattr(tpl, "montage_fx", "cut") == "cut":
                concat_clips(res.outputs, m)
            else:
                from .montage_fx import render_montage
                render_montage(res.outputs, m, tpl.montage_fx, logger=log,
                               encoder_policy=getattr(tpl, 'encoder_policy', 'auto'))
            res.montage = m
            log(f"モンタージュ保存: {m.name}")
        except Exception as ex:
            # モンタージュ失敗は完成済みクリップを巻き戻さない。
            res.failed.append((0, f"montage: {type(ex).__name__}: {ex}"))
            log(f"モンタージュ作成をスキップ: {type(ex).__name__}: {ex}")
    return res
