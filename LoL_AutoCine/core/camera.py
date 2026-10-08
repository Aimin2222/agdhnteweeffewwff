# -*- coding: utf-8 -*-
"""カメラ演出 v1.2。選択プレイヤーを追従し、キル周辺で 再生速度・FOV・距離・角度 を滑らかに動かす。

スタイル
  third_cinema / third : 三人称視点 (キャラの斜め上後方・低めの角度)。キル周辺で寄り+ローアングル+スロー
  cinema / follow      : FPS風 (標準カメラと同じ視線のまま距離だけ調整)
  cinema_top / top     : 俯瞰 (LoL標準カメラ。FOVでズーム)。最も安全
どのスタイルも「最初に固定したプレイヤー」を追従し、1秒ごとに追従設定を再送して外れを防ぐ。

座標系を推測しない設計:
  1. 俯瞰(top)で追従させ、標準カメラ位置 C と回転 R を読む  2. fps(オフセット0)でキャラ位置 P を読む
  3. v = C - P (キャラ→標準カメラ)。FPS風は offset = v x 係数、回転は R のまま
  4. 三人称は「R の俯角成分(= v の仰角と一致する成分)」だけを差し替える。水平方向は v と同じ向き。
  5. 読み戻して検証 (位置が想定通りか / 地面より十分上か)。ダメなら俯瞰へ自動フォールバック
曲線は純関数 (テスト可能)。急変を避けるため smoothstep のみ使用。
"""
from __future__ import annotations
import math
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

from .players import Player
from .replay_api import ReplayAPI, ReplayApiError
from .camera_clock import SmoothReplayClock

INTENSITY = {"natural": 0.6, "standard": 1.0, "strong": 1.4}
INTENSITY_JP = {"natural": "自然め", "standard": "標準", "strong": "強め"}

STYLES = {
    "third_cinema": "三人称シネマ (斜め後ろ・寄り＋ローアングル＋スロー)",
    "third": "三人称 追従のみ",
    "cinema": "FPS風シネマ (標準視点でドリーイン＋スロー)",
    "fps": "FPS視点 (高さ補正)",
    "orbit": "オービット (実験的)",
    "lolnam_cinema": "Lolnam風シネマ (自動カメラ移動)",
    "follow": "FPS風 追従のみ",
    "cinema_top": "俯瞰シネマ (ズーム＋スロー・安全)",
    "top": "俯瞰 追従のみ (安全)",
}
THIRD_STYLES = ("third_cinema", "third", "lolnam_cinema")
FPS_STYLES = ("cinema", "follow", "fps", "lolnam_cinema") + THIRD_STYLES
CINEMA_STYLES = ("cinema", "cinema_top", "third_cinema", "lolnam_cinema")

BASE_FOV = 60.0
ZERO = {"x": 0.0, "y": 0.0, "z": 0.0}


def _hermite(a: float, b: float, ta: float, tb: float, u: float) -> float:
    """2点間を滑らかにつなぐHermite補間。"""
    u = max(0.0, min(1.0, u))
    u2, u3 = u * u, u * u * u
    h00 = 2*u3 - 3*u2 + 1
    h10 = u3 - 2*u2 + u
    h01 = -2*u3 + 3*u2
    h11 = u3 - u2
    return h00*a + h10*ta + h01*b + h11*tb


def _ease5(x: float) -> float:
    """開始/終了を滑らかにするquintic ease-in/out。"""
    x = max(0.0, min(1.0, x))
    return x*x*x*(x*(x*6.0 - 15.0) + 10.0)


def _motion_params(profile: str, intensity: float, multi: int) -> tuple[float, float, float]:
    """Lolnam風自動カメラの (回り込み角, ドリー%, ローアングル角) を返す。"""
    p = profile or "cinematic"
    if p == "auto":
        p = "dynamic" if multi >= 2 else "cinematic"
    base = {
        "smooth": (8.0, 2.0, 5.0),
        "cinematic": (16.0, 5.0, 8.0),
        "dynamic": (25.0, 8.0, 11.0),
    }.get(p, (16.0, 5.0, 8.0))
    gain = max(0.75, min(1.35, 0.75 + 0.25 * max(0.0, intensity)))
    if multi >= 3:
        gain *= 1.08
    return base[0] * gain, base[1] * gain, base[2] * gain
MIN_CLEARANCE = 350.0     # FPS風: 地面(キャラ位置)よりカメラが最低これだけ上
MIN_CAM_HEIGHT = 300.0    # 三人称: 常にこの高さ以上
HEARTBEAT = 1.0           # 追従設定の再送間隔(秒)
TRY_TPS = __import__("os").environ.get("AUTOCINE_TRY_TPS", "0") == "1"

# 一度成功した三人称リグの「回転軸」をプロセス内で保持する。
# Replay API は seek/再生直後に cameraRotation の返却が不安定な場合があり、
# プレビューでは成功したのに録画開始時だけ FPS 判定へ落ちることがあるため。
_TPS_CALIBRATION = {}


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def window(t: float, a: float, b: float, c: float, d: float) -> float:
    """a->b で 0->1、b->c は 1 維持、c->d で 1->0 の台形(smoothstep)。"""
    if t <= a or t >= d:
        return 0.0
    if t < b:
        return smoothstep((t - a) / (b - a))
    if t <= c:
        return 1.0
    return 1.0 - smoothstep((t - c) / (d - c))


def _vec(d) -> Optional[tuple]:
    try:
        return (float(d["x"]), float(d["y"]), float(d["z"]))
    except Exception:
        return None


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _len(a) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def _pitch_axis(rot: dict, phi_top: float) -> Optional[str]:
    """回転 dict のうち、標準カメラの俯角(=vの仰角)と大きさが一致する成分名。無ければ None。"""
    best, best_d = None, 8.0
    for k in ("x", "y", "z"):
        try:
            d = abs(abs(float(rot[k])) - phi_top)
        except Exception:
            continue
        if d < best_d:
            best, best_d = k, d
    return best


@dataclass
class RigInfo:
    mode: str = "top"                 # 実際に使われたモード (fps / top)
    P: Optional[tuple] = None
    v: Optional[tuple] = None
    rot: Optional[dict] = None
    note: str = ""
    fell_back: bool = False
    third: bool = False               # 三人称リグが有効
    pitch_axis: str = ""
    pitch_sign: float = -1.0
    h: tuple = (0.0, -1.0)            # 水平方向の単位ベクトル (x, z): キャラ→カメラ


@dataclass
class CameraPlan:
    style: str = "cinema"
    intensity: float = 1.0
    kill_time: float = 0.0
    kill_times: tuple = ()              # マルチキルの各イベント時刻
    base_fov: float = BASE_FOV
    dist_scale: float = 0.8
    rig: Optional[RigInfo] = None
    third_elev: float = 28.0          # 三人称の仰角(度)
    third_dist: float = 950.0         # 三人称のキャラまでの距離
    third_yaw: float = 0.0            # 三人称の水平回転角。0=現在の基準方向、+右回り/-左回り
    motion_arc: float = 0.0           # Lolnam風の自動回り込み最大角
    motion_dolly: float = 0.0          # Lolnam風の追加ドリー量(%)
    motion_profile: str = "cinematic" # smooth / cinematic / dynamic / auto
    height: float = 0.0                # FPS系の安全高さ補正
    sel_name: str = ""
    scene_keyframes: tuple = ()       # append to preserve legacy positional fields

    @staticmethod
    def _keyframe_channel(frames, left_idx: int, key: str, local_t: float) -> float:
        """Shape-preserving cubic for three or more keyframes (continuous velocity).

        Smoothstep at each pair used to set the velocity to zero at *every*
        marker. This produced visible stops in an otherwise continuous orbit.
        Interior slopes use harmonic interpolation, avoiding overshoot.
        """
        def slope(i):
            if i <= 0 or i >= len(frames) - 1:
                return 0.0   # ease at shot boundaries
            a, b, c = frames[i-1], frames[i], frames[i+1]
            d0 = (b[key] - a[key]) / max(0.001, b['time'] - a['time'])
            d1 = (c[key] - b[key]) / max(0.001, c['time'] - b['time'])
            if d0 * d1 <= 0.0:
                return 0.0
            h0, h1 = b['time'] - a['time'], c['time'] - b['time']
            w0, w1 = 2.0*h1 + h0, h1 + 2.0*h0
            return (w0 + w1) / (w0/d0 + w1/d1)

        a, b = frames[left_idx], frames[left_idx + 1]
        h = b['time'] - a['time']
        u = max(0.0, min(1.0, (local_t - a['time']) / max(0.001, h)))
        if len(frames) == 2:
            return a[key] + (b[key] - a[key]) * smoothstep(u)
        return _hermite(a[key], b[key], h*slope(left_idx), h*slope(left_idx + 1), u)

    def keyframe_values(self, t: float) -> tuple[float, float, float]:
        """Get smooth (yaw degrees, zoom %, FOV degrees) from validated shot markers."""
        frames = self.scene_keyframes
        if not frames or self.style not in THIRD_STYLES:
            return (0.0, 0.0, 0.0)
        local_t = t - self.kill_time
        if local_t <= frames[0]['time']:
            mark = frames[0]
            return (mark['yaw'], mark['zoom'], mark['fov'])
        if local_t >= frames[-1]['time']:
            mark = frames[-1]
            return (mark['yaw'], mark['zoom'], mark['fov'])
        for i, (left, right) in enumerate(zip(frames, frames[1:])):
            if left['time'] <= local_t <= right['time']:
                return tuple(self._keyframe_channel(frames, i, ch, local_t)
                             for ch in ('yaw', 'zoom', 'fov'))
        return (0.0, 0.0, 0.0)

    def _cue(self, t: float, span=(-2.0, -0.4, 0.4, 1.8)) -> float:
        ks = tuple(self.kill_times) or (self.kill_time,)
        a, b, c, d = span
        return max((window(t, k+a, k+b, k+c, k+d) for k in ks), default=0.0)

    def speed_at(self, t: float) -> float:
        if self.style not in CINEMA_STYLES:
            return 1.0
        w = self._cue(t, (-1.6, -0.5, 0.3, 1.8))
        slow = 1.0 - 0.5 * min(1.0, self.intensity)
        slow = max(0.35, slow - 0.1 * max(0.0, self.intensity - 1.0))
        return 1.0 + (slow - 1.0) * w

    def fov_at(self, t: float) -> float:
        base = self._base_fov_at(t)
        if not self.scene_keyframes or self.style not in THIRD_STYLES:
            return base
        return max(32.0, min(100.0, base + self.keyframe_values(t)[2]))

    def _base_fov_at(self, t: float) -> float:
        w = self._cue(t, (-2.0, -0.4, 0.4, 1.8))
        if self.style == "cinema_top":
            return self.base_fov - 7.0 * self.intensity * w
        if self.style == "cinema":
            return self.base_fov - 3.0 * self.intensity * w
        if self.style == "third_cinema":
            return self.base_fov - 4.0 * self.intensity * w
        if self.style == "lolnam_cinema":
            ks = tuple(self.kill_times) or (self.kill_time,)
            impact = max((_ease5(max(0.0, min(1.0, 1.0 - abs(t-k) / 0.65))) for k in ks), default=0.0)
            multi_wide = 2.5 * max(0, len(ks)-1) * w
            return self.base_fov - 4.0 * self.intensity * w + 1.5 * impact + multi_wide
        return self.base_fov

    def scale_at(self, t: float) -> float:
        s0 = self.dist_scale
        if self.style != "cinema":
            return s0
        w = self._cue(t, (-2.0, -0.4, 0.4, 1.8))
        return max(0.22, s0 * (1.0 - 0.42 * min(1.3, self.intensity) * w))

    def third_pose_at(self, t: float) -> tuple:
        """確定版Orbitの三人称カメラ。キャラクターを中心に水平公転。"""
        if self.style in ("third", "third_cinema"):
            """三人称: (オフセット, 仰角deg)。シネマではキル周辺で寄りつつローアングル。常に MIN_CAM_HEIGHT 以上。"""
            w = 0.0
            if self.style == "third_cinema":
                k = self.kill_time
                w = window(t, k - 2.0, k - 0.4, k + 0.4, k + 1.8)
            a = min(1.3, self.intensity)
            elev = self.third_elev - 9.0 * a * w
            dist = self.third_dist * (1.0 - 0.30 * a * w)
            sin_e = max(math.sin(math.radians(max(10.0, elev))), MIN_CAM_HEIGHT / max(dist, 1.0))
            sin_e = min(0.98, sin_e)
            e = math.asin(sin_e)
            hx, hz = self.rig.h if self.rig else (0.0, -1.0)
            # TRUE ORBIT: キャラクターを中心に「キャラ→カメラ」の水平位置ベクトルを
            # x-z平面で回転させる。これはカメラ自身をその場で回すのではなく、
            # カメラがキャラの周囲を公転する動き。Yは高さとして固定する。
            extra_yaw, zoom, _ = self.keyframe_values(t)
            dist *= max(0.7, min(1.3, 1.0 - zoom / 100.0))
            sin_e = max(math.sin(e), MIN_CAM_HEIGHT / max(dist, 1.0))
            sin_e = min(0.98, sin_e)
            e = math.asin(sin_e)
            orbit = math.radians(float(self.third_yaw) + extra_yaw)
            c, s = math.cos(orbit), math.sin(orbit)
            rhx = hx * c - hz * s
            rhz = hx * s + hz * c
            return ((rhx * dist * math.cos(e), dist * sin_e, rhz * dist * math.cos(e)), math.degrees(e))
        return self._lolnam_pose_at(t)

    def _lolnam_pose_at(self, t: float) -> tuple:
        """三人称の位置オフセットと仰角。Lolnam風ではキャラ中心Orbitを自動化する。"""
        ks = tuple(self.kill_times) or (self.kill_time,)
        multi = max(1, len(ks))
        cue = max((window(t, k-2.0, k-0.4, k+0.4, k+1.8) for k in ks), default=0.0)
        impact = max((_ease5(max(0.0, min(1.0, 1.0 - abs(t-k) / 0.70))) for k in ks), default=0.0)
        a = min(1.3, self.intensity)

        if self.style == "lolnam_cinema":
            auto_arc, dolly, low = _motion_params(self.motion_profile, self.intensity, multi)
            arc = float(self.motion_arc or auto_arc)
            # キル前に開始→インパクトで最大→終了で基準へ戻る。
            u = max(0.0, min(1.0, (t - (min(ks)-2.0)) / 4.0))
            arc_wave = math.sin(math.pi * _ease5(u))
            orbit_delta = arc * arc_wave
            close_amount = (0.30 * a + dolly / 100.0) * impact
            wide_amount = (0.045 * max(0, multi-1)) * cue
            dist_factor = max(0.52, 1.0 - close_amount + min(0.16, wide_amount))
            dist = self.third_dist * dist_factor
            low_total = 9.0 * a + low * 0.55
            elev = self.third_elev - low_total * max(cue, impact * 0.9)
            if multi >= 2:
                elev += 4.0 * cue
        else:
            w = cue if self.style == "third_cinema" else 0.0
            elev = self.third_elev - 9.0 * a * w
            dist = self.third_dist * (1.0 - 0.30 * a * w)
            orbit_delta = 0.0

        extra_yaw, zoom, _ = self.keyframe_values(t)
        dist *= max(0.7, min(1.3, 1.0 - zoom / 100.0))
        elev = max(12.0, min(58.0, elev))
        sin_e = max(math.sin(math.radians(elev)), MIN_CAM_HEIGHT / max(dist, 1.0))
        sin_e = min(0.98, sin_e)
        eang = math.asin(sin_e)
        hx, hz = self.rig.h if self.rig else (0.0, -1.0)
        yaw = math.radians(float(self.third_yaw) + orbit_delta + extra_yaw)
        rhx = hx * math.cos(yaw) - hz * math.sin(yaw)
        rhz = hx * math.sin(yaw) + hz * math.cos(yaw)
        return ((rhx * dist * math.cos(eang), dist * sin_e, rhz * dist * math.cos(eang)), math.degrees(eang))

    def offset_at(self, t: float) -> tuple:
        if self.style == "orbit":
            ks = tuple(self.kill_times) or (self.kill_time,)
            k = min(ks, key=lambda kk: abs(t - kk))
            w = window(t, k - 2.5, k - 1.0, k + 1.0, k + 2.5)
            a = smoothstep((t - (k - 2.5)) / 5.0)
            ang = math.radians(150.0 * min(1.3, self.intensity)) * a
            r = 450.0 * w
            return (r * math.cos(ang), self.height, r * math.sin(ang))
        if self.rig is None or self.rig.mode != "fps":
            return (0.0, self.height, 0.0)
        if self.rig.third:
            return self.third_pose_at(t)[0]
        if self.rig.v is None:
            return (0.0, self.height, 0.0)
        s = self.scale_at(t)
        return (self.rig.v[0] * s, self.rig.v[1] * s + self.height, self.rig.v[2] * s)

    def rotation_at(self, t: float) -> Optional[dict]:
        """確定版Orbitの三人称視線。カメラ位置の公転と同じ基準。"""
        if self.style in ("third", "third_cinema"):
            if self.rig is None or not self.rig.third or not self.rig.rot or not self.rig.pitch_axis:
                return None
            rot = dict(self.rig.rot)
            elev = self.third_pose_at(t)[1]
            rot[self.rig.pitch_axis] = self.rig.pitch_sign * elev

            # TRUE ORBITの視線。カメラ位置を回しただけでは横を向くため、
            # 同じ軌道角だけ水平Yawも回して、常にキャラクター中心へ向ける。
            # pitch軸以外の水平回転軸はReplay APIの既存キャリブレーション規則を使用。
            yaw_axis = {"x": "z", "y": "x", "z": "y"}.get(self.rig.pitch_axis, "x")
            try:
                base_yaw = float(self.rig.rot.get(yaw_axis, 0.0))
            except Exception:
                base_yaw = 0.0
            yaw_delta = -(float(self.third_yaw) + self.keyframe_values(t)[0])
            rot[yaw_axis] = base_yaw + yaw_delta
            return rot
        return self._lolnam_rotation_at(t)

    def _lolnam_rotation_at(self, t: float) -> Optional[dict]:
        if self.rig is None or not self.rig.third or not self.rig.rot or not self.rig.pitch_axis:
            return None
        rot = dict(self.rig.rot)
        rot[self.rig.pitch_axis] = self.rig.pitch_sign * self.third_pose_at(t)[1]

        # Orbitは「カメラを回す」のではなく「キャラを中心にカメラが回る」。
        # そのためカメラ位置を回した分だけ水平Yawも同じだけ回し、
        # 常に被写体を中心へ向ける。pitch軸以外のうち、従来の水平回転に
        # 使う軸を固定対応させる。
        yaw_axis = {"x": "z", "y": "x", "z": "y"}.get(self.rig.pitch_axis, "x")
        try:
            base_yaw = float(rot.get(yaw_axis, 0.0))
        except Exception:
            base_yaw = 0.0
        yaw_delta = float(self.third_yaw) + self.keyframe_values(t)[0]
        if self.style == "lolnam_cinema":
            ks = tuple(self.kill_times) or (self.kill_time,)
            multi = max(1, len(ks))
            auto_arc, _, _ = _motion_params(self.motion_profile, self.intensity, multi)
            arc = float(self.motion_arc or auto_arc)
            u = max(0.0, min(1.0, (t - (min(ks)-2.0)) / 4.0))
            yaw_delta += arc * math.sin(math.pi * _ease5(u))
        rot[yaw_axis] = base_yaw - yaw_delta
        return rot


class CameraDirector:
    """録画/プレビュー中のカメラを滑らかに制御するDirector。

    重要なのは「144Hzで計算すること」と「Replay APIへ144回/秒HTTPを投げること」を分離すること。
    Replay APIはHTTPなので、毎フレーム playback GET + render POST を行うとネットワーク待ちで
    キル付近ほどガクつく。そこで内部モーションは144Hz、Replay APIへの書き込みは60Hzに制限し、
    再生時刻はローカルのmonotonic時計で補間しながら0.25秒ごとに実時間へ同期する。
    """

    def __init__(self, api: ReplayAPI, plan: CameraPlan, hz: float = 144.0, api_hz: float = 60.0):
        self.api, self.plan = api, plan
        self.hz = max(60.0, float(hz))
        self.api_hz = max(30.0, min(60.0, float(api_hz)))
        self.dt = 1.0 / self.hz
        self.api_dt = 1.0 / self.api_hz
        self._smooth_fov = None
        self._smooth_offset = None
        self._smooth_rot = None
        self._stop = threading.Event()
        self._th: Optional[threading.Thread] = None
        self.errors = 0
        self.min_cam_height: Optional[float] = None
        self.heartbeats = 0
        self.max_clock_drift = 0.0
        self.max_api_latency_ms = 0.0
        self.api_slow_calls = 0
        self.api_calls = 0
        self._playback_t0 = 0.0
        self._wall_t0 = 0.0
        self._last_sync = 0.0
        self._last_api_send = 0.0
        self._last_speed = None
        self._sent_speed = None
        self._last_heartbeat = 0.0

    def start(self) -> None:
        try:
            pb = self.api.playback()
            self._playback_t0 = float(pb.get("time", 0.0))
        except ReplayApiError:
            self._playback_t0 = float(self.plan.kill_time) - 0.001
        self._clock = SmoothReplayClock(self._playback_t0)
        self._wall_t0 = time.perf_counter()
        self._last_sync = self._wall_t0
        self._last_api_send = 0.0
        self._last_heartbeat = 0.0
        self._th = threading.Thread(target=self._run, daemon=True)
        self._th.start()

    def stop(self) -> None:
        self._stop.set()
        if self._th:
            self._th.join(timeout=2.0)

    def _estimate_time(self, now: float) -> float:
        return self._playback_t0 + (now - self._wall_t0) * (self._last_speed if self._last_speed not in (None, 0) else 1.0)

    def _run(self) -> None:
        next_tick = time.perf_counter()
        last_now = next_tick
        current_speed = 1.0
        clock = self._clock
        while not self._stop.is_set():
            now = time.perf_counter()
            try:
                # HTTPS playback observations never modify camera time in steps.
                # Only a real external seek resets the continuous clock.
                if self._last_sync <= 0.0 or now - self._last_sync >= 0.25:
                    try:
                        pb = self.api.playback()
                        if clock.observe(pb.get("time", clock.time)):
                            # A seek is exceptional: avoid interpolating across a cut.
                            self._smooth_fov = self._smooth_offset = self._smooth_rot = None
                        self.max_clock_drift = max(self.max_clock_drift, abs(clock.drift))
                    except ReplayApiError:
                        self.errors += 1
                    self._last_sync = time.perf_counter()
                # Include HTTP latency rather than dropping it from the clock.
                now = time.perf_counter()
                real_dt = max(0.0, min(0.25, now - last_now))
                last_now = now
                t = clock.advance(real_dt, current_speed)
                plan, rig = self.plan, self.plan.rig
                target_speed = float(plan.speed_at(t))
                speed_alpha = 1.0 - math.exp(-real_dt / 0.12)
                current_speed += (target_speed - current_speed) * speed_alpha
                self._last_speed = current_speed

                body = {}
                if plan.style in CINEMA_STYLES:
                    target_fov = float(plan.fov_at(t))
                    alpha = 1.0 - math.exp(-real_dt / 0.075) if self._smooth_fov is not None else 1.0
                    self._smooth_fov = target_fov if self._smooth_fov is None else self._smooth_fov + (target_fov - self._smooth_fov) * alpha
                    body["fieldOfView"] = round(self._smooth_fov, 3)
                if rig is not None and rig.mode == "fps":
                    target_offset = tuple(float(v) for v in plan.offset_at(t))
                    alpha = 1.0 - math.exp(-real_dt / 0.095) if self._smooth_offset is not None else 1.0
                    self._smooth_offset = target_offset if self._smooth_offset is None else tuple(a + (b - a) * alpha for a, b in zip(self._smooth_offset, target_offset))
                    x, y, z = self._smooth_offset
                    body["selectionOffset"] = {"x": x, "y": y, "z": z}
                    self.min_cam_height = y if self.min_cam_height is None else min(self.min_cam_height, y)
                    rot = plan.rotation_at(t)
                    if rot is not None:
                        alpha_r = 1.0 - math.exp(-real_dt / 0.085) if self._smooth_rot is not None else 1.0
                        if self._smooth_rot is None:
                            self._smooth_rot = {k: float(v) for k, v in rot.items()}
                        else:
                            for k, target in rot.items():
                                prev = self._smooth_rot.get(k, float(target))
                                delta = (float(target) - prev + 180.0) % 360.0 - 180.0
                                self._smooth_rot[k] = prev + delta * alpha_r
                        body["cameraRotation"] = dict(self._smooth_rot)

                # 60Hz API write cadence. This avoids saturating the local HTTPS Replay API.
                if plan.sel_name and now - self._last_heartbeat >= HEARTBEAT:
                    body.update(selectionName=plan.sel_name, cameraAttached=True,
                                cameraMode="fps" if (rig is not None and rig.mode == "fps") else "top")
                    self._last_heartbeat = now
                    self.heartbeats += 1

                if body and (now - self._last_api_send >= self.api_dt):
                    api_t0 = time.perf_counter()
                    self.api.set_render(**body)
                    api_ms = (time.perf_counter() - api_t0) * 1000.0
                    self.api_calls += 1
                    self.max_api_latency_ms = max(self.max_api_latency_ms, api_ms)
                    if api_ms >= 25.0:
                        self.api_slow_calls += 1
                    self._last_api_send = time.perf_counter()

                # Speed is also smoothed; only send meaningful changes.
                if self._sent_speed is None or abs(current_speed - self._sent_speed) > 0.01:
                    self.api.set_playback(speed=round(current_speed, 3))
                    self._sent_speed = current_speed
            except ReplayApiError:
                self.errors += 1
            next_tick += self.dt
            sleep_for = next_tick - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            elif sleep_for < -0.05:
                next_tick = time.perf_counter()


def _fallback_top(api: ReplayAPI, sel: str, base_fov: float, why: str) -> RigInfo:
    api.set_render(selectionName=sel, cameraMode="top", cameraAttached=True,
                   fieldOfView=base_fov, selectionOffset=ZERO)
    return RigInfo(mode="top", note=why, fell_back=True)


def attach_to_player(api: ReplayAPI, p: Player, style: str, dist_scale: float = 0.8,
                     base_fov: float = BASE_FOV, settle: float = 0.25,
                     log: Callable = lambda m: None,
                     third_elev: float = 28.0, third_dist: float = 950.0, height: float = 0.0) -> RigInfo:
    """固定プレイヤーをカメラ対象にして追従させる。

    三人称については、プレビュー/録画をまたいで成功したリグを再利用する。
    Replay API は seek 直後や地形・遮蔽物付近で cameraRotation の返却が一時的に
    不安定になることがあるため、毎回「軸を再推定して失敗したらFPSへ変更」しない。
    現在値で軸を取れない場合は、同じ対象の直近の成功キャリブレーションを使う。
    """
    sel = p.selection_name or p.champion
    cache_key = (sel, style)
    cached = _TPS_CALIBRATION.get(cache_key)

    api.set_render(selectionName=sel, cameraMode="top", cameraAttached=True,
                   fieldOfView=base_fov, selectionOffset=ZERO)
    if style not in FPS_STYLES and style != "orbit":
        return RigInfo(mode="top", note="俯瞰追従")

    time.sleep(settle)
    r_top = api.render()
    C, rot = _vec(r_top.get("cameraPosition")), r_top.get("cameraRotation")

    api.set_render(selectionName=sel, cameraMode="fps", cameraAttached=True, selectionOffset=ZERO)
    time.sleep(settle)
    r_fps = api.render()
    P = _vec(r_fps.get("cameraPosition"))

    # 現在のAPI値が正常なら、それを優先してキャリブレーションする。
    current_v = _sub(C, P) if C is not None and P is not None else None
    current_h = None
    current_phi = None
    if current_v is not None:
        hl = math.hypot(current_v[0], current_v[2])
        if hl > 50:
            current_h = (current_v[0] / hl, current_v[2] / hl)
            current_phi = math.degrees(math.atan2(current_v[1], hl))

    axis = None
    sign = -1.0
    if isinstance(rot, dict) and current_phi is not None:
        axis = _pitch_axis(rot, current_phi)
        if axis:
            try:
                sign = 1.0 if float(rot[axis]) >= 0 else -1.0
            except Exception:
                axis = None

    # ここが重要: 現在の cameraRotation だけで軸を決められなくても、
    # 過去に成功した三人称リグがあれば、それを録画時にも再利用する。
    if style in THIRD_STYLES and cached:
        cached_axis = cached.get("axis", "")
        cached_sign = float(cached.get("sign", -1.0))
        if not axis and cached_axis:
            axis = cached_axis
            sign = cached_sign
            log(f"カメラ: 保存済み三人称リグを再利用 (軸 {axis}, 符号 {sign:+.0f})")
        elif axis:
            # 現在値が取れた場合でも、符号は成功済みキャリブレーションを優先。
            # seek直後に符号だけ反転するケースを避ける。
            sign = cached_sign if cached_axis == axis else sign

    # 座標が一時的に欠けた場合も、成功済みキャリブレーションの水平方向を使う。
    h = current_h
    if h is None and cached and cached.get("h"):
        h = tuple(cached["h"])
        log("カメラ: 保存済み三人称の水平方向を再利用")

    v = current_v
    if v is None and cached and cached.get("v"):
        v = tuple(cached["v"])
        log("カメラ: 保存済み三人称の基準オフセットを再利用")

    # P が取れない場合だけ、過去のPを使う。これは一時的なAPI欠落への保険。
    if P is None and cached and cached.get("P"):
        P = tuple(cached["P"])
        log("カメラ: 保存済み三人称の基準位置を再利用")

    # 通常のFPS/三人称の基準値が作れない場合は従来通り安全に俯瞰へ。
    if P is None or v is None or _len(v) < 300 or v[1] < MIN_CLEARANCE:
        info = _fallback_top(api, sel, base_fov, "カメラ位置が安定せず三人称/FPSを構成できないため俯瞰に切替")
        log("カメラ: " + info.note)
        return info

    if h is None:
        hl = math.hypot(v[0], v[2])
        h = (v[0] / hl, v[2] / hl) if hl > 50 else (0.0, -1.0)

    # 三人称は「現在軸」または「保存軸」のどちらかがあれば維持する。
    third = style in THIRD_STYLES and bool(axis)
    note_extra = ""
    rot_use = dict(rot) if isinstance(rot, dict) else None

    if third:
        e = math.radians(third_elev)
        off = (
            h[0] * third_dist * math.cos(e),
            third_dist * math.sin(e),
            h[1] * third_dist * math.cos(e),
        )
        if rot_use is None:
            # 現在回転が欠けた場合は保存済み回転を使う。
            rot_use = dict(cached.get("rot", {})) if cached else {}
        if not rot_use:
            # 軸だけ分かって回転全体が取れないケースは、他軸を壊さないため
            # 最小限の回転を作る。Replay側が補正できるよう三人称を維持する。
            rot_use = {"x": 0.0, "y": 0.0, "z": 0.0}
        rot_use[axis] = sign * third_elev
    else:
        if style in THIRD_STYLES:
            note_extra = " (保存済み三人称リグもなく、方向を特定できないためFPS風)"
        off = (v[0] * dist_scale, v[1] * dist_scale, v[2] * dist_scale)

    api.set_render(cameraMode="fps", cameraAttached=True,
                   selectionOffset={"x": off[0], "y": off[1], "z": off[2]},
                   cameraRotation=rot_use, fieldOfView=base_fov)
    time.sleep(settle)
    Q = _vec(api.render().get("cameraPosition"))
    if Q is None:
        info = _fallback_top(api, sel, base_fov, "カメラ位置を検証できないため俯瞰に切替")
        log("カメラ: " + info.note)
        return info

    expected = (P[0] + off[0], P[1] + off[1], P[2] + off[2])
    err = _len(_sub(Q, expected))
    clearance = Q[1] - P[1]

    # 三人称では地形/遮蔽物によるReplay側の補正をある程度許容する。
    # 「少し位置がずれた」だけでFPS/俯瞰へ切り替えない。
    if third:
        max_err = max(260.0, 0.42 * _len(off) + 90.0)
        min_clearance = max(120.0, MIN_CAM_HEIGHT * 0.55)
    else:
        max_err = 0.25 * _len(off) + 50
        min_clearance = MIN_CLEARANCE * 0.6

    if err > max_err or clearance < min_clearance or clearance < max(0.0, off[1] * 0.35):
        # 三人称なら、検証値が一時的に地形補正されただけの可能性が高い。
        # 保存済みリグがある場合は1回だけ同じ三人称設定を再送して再検証する。
        if third and cached:
            log(f"カメラ: 三人称の初回検証が不安定 (誤差{err:.0f}, 高さ{clearance:.0f})。同じリグを再送します")
            api.set_render(cameraMode="fps", cameraAttached=True,
                           selectionOffset={"x": off[0], "y": off[1], "z": off[2]},
                           cameraRotation=rot_use, fieldOfView=base_fov)
            time.sleep(max(0.15, settle * 0.6))
            Q2 = _vec(api.render().get("cameraPosition"))
            if Q2 is not None:
                Q, clearance = Q2, Q2[1] - P[1]
                err = _len(_sub(Q2, expected))
                if err <= max_err * 1.25 and clearance >= min_clearance:
                    note = f"三人称カメラ OK (地面からの高さ {clearance:.0f}) (保存済みリグ再利用)"
                    return _cache_success(cache_key, P, v, rot_use, h, axis, sign, log, note)

        info = _fallback_top(api, sel, base_fov,
                             f"カメラが想定位置になりません(誤差{err:.0f}, 高さ{clearance:.0f})。俯瞰に切替")
        log("カメラ: " + info.note)
        return info

    kind = "三人称" if third else "FPS風"
    note = f"{kind}カメラ OK (地面からの高さ {clearance:.0f}){note_extra}"
    if third:
        return _cache_success(cache_key, P, v, rot_use, h, axis, sign, log, note)
    return RigInfo(mode="fps", P=P, v=v, rot=rot_use, third=False,
                   pitch_axis="", pitch_sign=sign, h=h, note=note)


def _cache_success(cache_key, P, v, rot, h, axis, sign, log, note) -> RigInfo:
    """成功した三人称リグを次の seek/録画でも再利用できる形で保存する。"""
    _TPS_CALIBRATION[cache_key] = {
        "P": tuple(P) if P is not None else None,
        "v": tuple(v) if v is not None else None,
        "h": tuple(h) if h is not None else (0.0, -1.0),
        "rot": dict(rot or {}),
        "axis": axis or "",
        "sign": float(sign),
    }
    log("カメラ: " + note)
    return RigInfo(mode="fps", P=P, v=v, rot=dict(rot or {}), third=True,
                   pitch_axis=axis or "", pitch_sign=float(sign), h=tuple(h), note=note)

