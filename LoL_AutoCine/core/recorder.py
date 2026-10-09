# -*- coding: utf-8 -*-
"""FrameSource の最新フレームを一定FPSで固定で ffmpeg に流して MP4 化する。

WGC のフレーム到着は不定間隔なので、一定間隔ごとに「最新の1枚」を書き出して一定fpsにする
(到着が遅ければ前フレームを複製)。フレームサイズは開始時に固定し、変わったら最近傍で合わせる。
"""
from __future__ import annotations
import subprocess
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

from .capture import FrameSource, CaptureError
from .effects import FFMPEG, gpu_encoder_available, encoder_args


@lru_cache(maxsize=8)
def _nvenc_capture_probe(ffmpeg, fps):
    """Validate the encoder before capture; restarting a partial clip would lose frames."""
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-f','lavfi','-i',
         f'color=s=1920x1080:r={fps}:d=0.1','-frames:v','1','-an',
         '-c:v','h264_nvenc','-preset','p5','-pix_fmt','yuv420p','-f','null','-']
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=8)
        return result.returncode==0, (result.stderr or '')[-450:]
    except (OSError, subprocess.TimeoutExpired) as e:
        return False,str(e)


def _fit(frame: np.ndarray, w: int, h: int) -> np.ndarray:
    if frame.shape[1] == w and frame.shape[0] == h:
        return frame
    ys = (np.arange(h) * frame.shape[0] // h).astype(np.int32)
    xs = (np.arange(w) * frame.shape[1] // w).astype(np.int32)
    return frame[ys][:, xs]


class ClipRecorder:
    def __init__(self, source: FrameSource, out_path: Path, fps: int = 60, crf: int = 14,
                 encoder_policy: str = 'auto'):
        self.src, self.out, self.fps, self.crf = source, Path(out_path), fps, crf
        self.encoder_policy = encoder_policy
        self._proc: Optional[subprocess.Popen] = None
        self._th: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self.frames = 0
        self.fresh_frames = 0        # 実際に新規到着したフレーム数 (固まり検知用)
        self.error: Optional[str] = None
        self.started_at = 0.0
        self.started_perf = 0.0
        self.wall_duration = 0.0
        self._stderr_tail = ""
        self.encoder_fallback_reason = None
        self._command = []

    def start(self) -> None:
        fr = self.src.latest()
        if fr is None:
            raise CaptureError("映像フレームがありません。録画を開始できません。")
        h, w = fr.shape[:2]
        w, h = w - (w % 2), h - (h % 2)
        self.w, self.h = w, h
        self.out.parent.mkdir(parents=True, exist_ok=True)
        use_nvenc = self.encoder_policy != 'cpu' and gpu_encoder_available()
        if use_nvenc:
            use_nvenc, reason = _nvenc_capture_probe(FFMPEG, self.fps)
            if not use_nvenc:
                self.encoder_fallback_reason = 'NVENC録画プローブ失敗 → CPUで録画: ' + reason
                import logging
                logging.getLogger(__name__).warning(self.encoder_fallback_reason)
        if use_nvenc:
            enc = ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr",
                   "-cq", "18", "-b:v", "0"]
        else:
            enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", str(self.crf)]
        # 録画中も最終サイズを1080pへ固定。LoLウィンドウが1440p/4Kでも
        # 後段で解像度が変わらず、編集アプリと同じ安定した出力サイズになる。
        cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{w}x{h}", "-framerate", str(self.fps), "-i", "-",
               "-vf", "scale=1920:1080:flags=lanczos",
               *enc, "-pix_fmt", "yuv420p", "-r", str(self.fps), "-vsync", "cfr", str(self.out)]
        self._command = cmd
        try:
            self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as e:
            raise CaptureError(f"FFmpegを起動できません: {e}") from e
        if self._proc.stdin is None:
            raise CaptureError("FFmpegの入力パイプを開けませんでした。")
        self._stop.clear()
        self.started_at = time.time()
        self.started_perf = time.perf_counter()
        self._th = threading.Thread(target=self._run, daemon=True)
        self._th.start()

    def _run(self) -> None:
        dt = 1.0 / self.fps
        nxt = time.perf_counter()
        last_count = self.src.frame_count
        try:
            while not self._stop.is_set():
                fr = self.src.latest()
                if fr is not None:
                    c = self.src.frame_count
                    if c != last_count:
                        self.fresh_frames += 1
                        last_count = c
                    self._proc.stdin.write(_fit(fr, self.w, self.h).tobytes())
                    self.frames += 1
                nxt += dt
                sl = nxt - time.perf_counter()
                if sl > 0:
                    time.sleep(sl)
                elif sl < -0.25:       # 大幅遅延: 取り戻そうとせず基準時刻を再設定
                    nxt = time.perf_counter()
        except (BrokenPipeError, OSError, ValueError) as e:
            self.error = f"ffmpeg への書き込み失敗: {e}"
        except Exception as e:  # 録画スレッドの例外をUIスレッドへ漏らさない
            self.error = f"録画スレッド異常: {type(e).__name__}: {e}"

    @property
    def elapsed(self) -> float:
        return self.frames / float(self.fps)

    def _probe_duration(self) -> float:
        """FFmpegが実際に書き出した動画長を取得する。"""
        import re
        try:
            r = subprocess.run([FFMPEG, "-hide_banner", "-i", str(self.out)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
            if not m:
                return 0.0
            return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
        except Exception:
            return 0.0

    def _normalize_duration(self, target: float) -> None:
        """録画中の実時間を基準にMP4の再生速度を正規化する。

        WGC/FFmpeg/Windowsの負荷で入力フレームと実時間がずれる場合でも、
        完成クリップが8倍速/極端なスローにならないようにする。
        """
        if target <= 0.5 or not self.out.exists():
            return
        actual = self._probe_duration()
        if actual <= 0.5:
            return
        ratio = actual / target
        if 0.97 <= ratio <= 1.03:
            return
        tmp = self.out.with_name(self.out.stem + "__timingfix.mp4")
        # setpts=PTS/ratio: actual/target が 8 なら 8倍長くして正しい実時間へ戻す。
        cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", str(self.out),
               "-vf", f"setpts=PTS/{ratio:.9f}", "-an",
               *encoder_args(self.fps, self.crf, policy=self.encoder_policy), str(tmp)]
        from .performance_diagnostics import run_render
        r = run_render(cmd,output=tmp,gpu_effects=[],effect_values={},timeout=120,
                       pipeline_info={'stage':'timing_normalization','encoder_policy':self.encoder_policy,
                                      'output_fps':self.fps,'duration_s':target})
        if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            tmp.replace(self.out)
            self._timing_fixed = True
        else:
            try:
                tmp.unlink()
            except OSError:
                pass
            raise CaptureError('録画時間の補正に失敗しました: ' + (r.stderr or '')[-500:])

    def stop(self) -> float:
        """録画停止。戻り値は録画秒数。"""
        self.wall_duration = max(0.0, time.perf_counter() - self.started_perf) if self.started_perf else 0.0
        self._stop.set()
        if self._th:
            self._th.join(timeout=3.0)
        if self._proc:
            try:
                self._proc.stdin.close()
            except Exception:
                pass
            try:
                self._proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
                self.error = self.error or '録画FFmpegの終了がタイムアウトしました。'
            if self._proc.returncode not in (0, None) and not self.error:
                err = self._proc.stderr.read().decode("utf-8", "replace")[-800:] if self._proc.stderr else ""
                self.error = f"ffmpeg 異常終了: {err}"
        from .performance_diagnostics import record_encoding_result
        record_encoding_result(self._command,output=self.out,
                               returncode=getattr(self._proc,'returncode',None),
                               error=self.error or ('録画フレームなし' if self.frames<=0 else None),
                               fallback_reason=self.encoder_fallback_reason,
                               pipeline_info={'stage':'capture','encoder_policy':self.encoder_policy,
                                              'cpu_video_effects':['scale'],'output_fps':self.fps,
                                              'duration_s':self.wall_duration})
        if self.error:
            raise CaptureError(self.error)
        if self.frames <= 0:
            raise CaptureError("録画フレームが1枚も生成されませんでした。")
        self._timing_fixed = False
        self._normalize_duration(self.wall_duration)
        # 完成動画の時間を優先。以降のFX/音声合成も同じ時間軸を使う。
        return self.wall_duration if self.wall_duration > 0.5 else self.elapsed
