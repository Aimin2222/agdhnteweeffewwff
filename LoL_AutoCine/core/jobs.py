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
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from .audio import AudioCapture, AudioError
from .audio_log import log as audio_log
from .camera import CameraPlan, CameraDirector, RigInfo, attach_to_player
from .capture import FrameSource, CaptureError, WGCWindowSource
from .effects import Template, apply_effects, concat_clips
from .hud import hide_hud, restore_hud
from .render_fx import apply_fx, restore_fx
from .players import Player
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
    min_speed = 0.35 if tpl.style in ("cinema", "cinema_top", "third_cinema", "lolnam_cinema") else 1.0
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
    try:
        _await_capture_refresh(source, source.frame_count, stop=stop)
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
    _await_capture_refresh(source, baseline, stop=stop)
    log('映像入力の復旧を確認、指定の開始時刻から録画します')
    return plan, rig


def _setup_clip(api: ReplayAPI, player: Player, tpl: Template, start: float, kills: list,
                log: Callable) -> tuple:
    api.set_playback(paused=True, speed=1.0)
    actual = api.seek(start)
    if actual is not None and abs(float(actual) - float(start)) > 0.80:
        actual = api.seek(start)
    if actual is not None and abs(float(actual) - float(start)) > 0.80:
        raise ReplayApiError(f'リプレイのシーク位置が確定しません ({actual:.2f}s / 目標 {start:.2f}s)')
    rig = attach_to_player(api, player, tpl.style, dist_scale=tpl.dist_scale, height=tpl.cam_height,
                           third_elev=getattr(tpl, "third_elev", 28.0), third_dist=getattr(tpl, "third_dist", 950.0), log=log)
    time.sleep(0.35)
    plan = CameraPlan(style=tpl.style, intensity=tpl.amp(), kill_time=kills[0].time,
                      kill_times=tuple(k.time for k in kills), dist_scale=tpl.dist_scale, height=tpl.cam_height,
                      third_elev=getattr(tpl, "third_elev", 28.0), third_dist=getattr(tpl, "third_dist", 950.0),
                       third_yaw=getattr(tpl, "third_yaw", 0.0),
                      motion_arc=getattr(tpl, "motion_arc", 0.0), motion_dolly=getattr(tpl, "motion_dolly", 0.0),
                      motion_profile=getattr(tpl, "motion_profile", "cinematic"),
                      scene_keyframes=tuple(getattr(tpl, 'scene_keyframes', ()) or ()),
                       smart_composition=bool(getattr(tpl, 'smart_composition', False)),
                       smart_impact=(float(getattr(tpl, 'highlight_pulse', 0.0))
                                     if getattr(tpl, 'smart_highlight_enabled', False) else 0.0), rig=rig,
                      sel_name=player.selection_name or player.champion)
    if rig.mode == "top" and tpl.style in ("cinema", "follow"):
        plan.style = "cinema_top" if tpl.style == "cinema" else "top"   # 実際に使えるモードに合わせる
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


def record_one_clip(api: ReplayAPI, source: FrameSource, player: Player, tpl: Template,
                    start: float, end: float, kills: list, raw_path: Path, stop=None,
                    log: Callable = lambda m: None,
                    audio_factory: Optional[Callable] = None) -> ClipTake:
    """1クリップ録画。HUD非表示は呼び出し側 (run_auto_edit) が行う。"""
    plan, rig = _prepare_clip_capture(api, source, player, tpl, start, kills, stop, log)
    take = ClipTake(rig=rig)
    saved_hud = {}
    if tpl.hide_hud:
        saved_hud = hide_hud(api, tpl.keep_champion_bars)
    fx_saved = {}
    try:
        cam_dist = getattr(tpl, "third_dist", 950.0) if getattr(rig, "third", False) else None
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
            # ゲーム音ONなのに無音MP4を成功扱いしない。初心者でも原因が分かるよう明示して停止。
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
        try:
            api.set_playback(paused=True, speed=1.0)
            api.set_render(fieldOfView=plan.base_fov, selectionOffset={"x": 0, "y": 0, "z": 0})
        except ReplayApiError:
            pass
        restore_hud(api, saved_hud)
        restore_fx(api, fx_saved)
    if recorder_error is not None:
        raise recorder_error
    return take


def preview_clip(api: ReplayAPI, player: Player, tpl: Template, start: float, end: float, kills: list,
                 stop=None, log: Callable = lambda m: None) -> RigInfo:
    """録画せずに、テンプレートのカメラ演出(追従/ズーム/スロー/HUD非表示)をLoL上で再生して確認する。"""
    plan, rig = _setup_clip(api, player, tpl, start, kills, log)
    director = CameraDirector(api, plan)
    cam_dist = getattr(tpl, "third_dist", 950.0) if getattr(rig, "third", False) else None
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
        try:
            api.set_playback(paused=True, speed=1.0)
            api.set_render(fieldOfView=plan.base_fov, selectionOffset={"x": 0, "y": 0, "z": 0})
        except ReplayApiError:
            pass
        restore_hud(api, saved_hud)
        restore_fx(api, fx_saved)
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
