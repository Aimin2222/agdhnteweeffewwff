# -*- coding: utf-8 -*-
"""ゲーム音の録音 (WASAPI ループバック)。映像と同じ区間をWAVで録り、後で MP4 に合成する。

注意: ループバックは「既定の出力デバイスで鳴っている音すべて」を録る (LoL以外の音も入る)。
      録画中は Discord や音楽などを止める/ミュートすること。
無音の間 WASAPI はデータを送ってこないため、時刻に合わせて無音を詰めて映像と長さを揃える。
"""
from __future__ import annotations
import math
import os
import struct
import threading
import time
import wave
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .procloop import ProcessLoopbackRecorder
from .audio_log import log as audio_log


class AudioError(Exception):
    pass


class PaddedWavWriter:
    """時刻に合わせて無音を挿入しながら WAV を書く (テスト可能な純ロジック)。"""

    def __init__(self, path: Path, rate: int, channels: int, t0: float):
        self.rate, self.ch, self.t0 = rate, channels, t0
        self.frames = 0
        self._w = wave.open(str(path), "wb")
        self._w.setnchannels(channels)
        self._w.setsampwidth(2)
        self._w.setframerate(rate)

    def _pad_to(self, target_frames: int) -> None:
        missing = target_frames - self.frames
        if missing > 0:
            self._w.writeframes(b"\x00" * (missing * self.ch * 2))
            self.frames += missing

    def write(self, data: bytes, now: float) -> None:
        n = len(data) // (self.ch * 2)
        expected_end = int((now - self.t0) * self.rate)
        gap = (expected_end - n) - self.frames
        if gap > int(self.rate * 0.04):          # 40ms以上の欠落は無音で埋める
            self._pad_to(self.frames + gap)
        self._w.writeframes(data)
        self.frames += n

    def finish(self, now: float) -> float:
        self._pad_to(int((now - self.t0) * self.rate))
        self._w.close()
        return self.frames / float(self.rate)


class AudioCapture:
    path: Path
    t0: float = 0.0           # perf_counter 基準の録音開始時刻

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> float:
        raise NotImplementedError


class LoopbackAudio(AudioCapture):
    """Windows: PyAudioWPatch で既定出力のループバックを録音。"""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._p = None
        self._stream = None
        self._wr: Optional[PaddedWavWriter] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        audio_log(f"LoopbackAudio.start path={self.path}")
        try:
            import pyaudiowpatch as pyaudio  # type: ignore
        except ImportError as e:
            audio_log("PyAudioWPatch import failed", "ERROR")
            raise AudioError("PyAudioWPatch が未インストールです。SOUND_TEST.bat または START.bat を実行してください。") from e
        try:
            p = pyaudio.PyAudio()
            wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            dev = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
            if not dev.get("isLoopbackDevice"):
                for lb in p.get_loopback_device_info_generator():
                    if dev["name"] in lb["name"]:
                        dev = lb
                        break
                else:
                    raise AudioError("ループバックデバイスが見つかりません。")
            rate, ch = int(dev["defaultSampleRate"]), int(dev["maxInputChannels"])
            audio_log(f"WASAPI loopback device={dev.get('name', '?')} index={dev.get('index')} rate={rate} channels={ch}")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.t0 = time.perf_counter()
            self._wr = PaddedWavWriter(self.path, rate, ch, self.t0)

            def cb(in_data, frame_count, time_info, status):  # noqa: ANN001
                with self._lock:
                    if self._wr is not None:
                        self._wr.write(in_data, time.perf_counter())
                return (None, pyaudio.paContinue)

            self._stream = p.open(format=pyaudio.paInt16, channels=ch, rate=rate, frames_per_buffer=1024,
                                  input=True, input_device_index=dev["index"], stream_callback=cb)
            self._p = p
        except AudioError:
            raise
        except Exception as e:
            audio_log(f"LoopbackAudio.start failed: {type(e).__name__}: {e}", "ERROR")
            raise AudioError(f"ゲーム音の録音を開始できません: {e}") from e

    def stop(self) -> float:
        dur = 0.0
        try:
            if self._stream is not None:
                self._stream.stop_stream()
                self._stream.close()
            if self._p is not None:
                self._p.terminate()
        except Exception:
            pass
        with self._lock:
            if self._wr is not None:
                dur = self._wr.finish(time.perf_counter())
                self._wr = None
        audio_log(f"LoopbackAudio.stop duration={dur:.3f}s")
        return dur



class SessionIsolatedLoopbackAudio(AudioCapture):
    """Process-loopback が使えない場合の診断用フォールバック。

    重要: デスクトップ全体のWASAPIループバックをLoL専用音声として
    扱うことはできないため、他アプリをミュートして録音する方式は廃止。
    Process Loopback に失敗した場合は PreferredGameAudio 側で明示的に失敗させ、
    BGM/他アプリの音を勝手に消したり混ぜたりしない。
    """
    def __init__(self, path: Path):
        self.path = Path(path)
        self._inner: Optional[LoopbackAudio] = None
        self._pid = 0
        self.t0 = 0.0

    def start(self) -> None:
        raise AudioError(
            "LoL専用Process Loopbackが利用できないため、デスクトップ全体音声へのフォールバックは安全上使用しません。WindowsのProcess Loopbackを有効にしてください。"
        )

    def stop(self) -> float:
        return 0.0


class PreferredGameAudio(AudioCapture):
    """LoLプロセスだけを録音するネイティブWindows Process Loopback。"""
    def __init__(self, path: Path):
        self.path = Path(path)
        self._proc: Optional[subprocess.Popen] = None
        self.t0 = 0.0

    @staticmethod
    def _helper_path() -> Path:
        return Path(__file__).resolve().parent.parent / "tools" / "bin" / "lol_audio_helper.exe"

    def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        audio_log(f"PreferredGameAudio.native start path={self.path}")
        helper = self._helper_path()
        if not helper.exists():
            raise AudioError(f"ネイティブ音声ヘルパーがありません: {helper}. BUILD_AUDIO_HELPER.bat を実行してヘルパーを作成してください。")
        try:
            from .procloop import lol_pid
            pid = int(lol_pid() or 0)
        except Exception:
            pid = 0
        if not pid:
            raise AudioError("LoLプロセスが見つかりません。リプレイを起動してから録音してください。")

        cmd = [str(helper), str(pid), str(self.path), "3600"]
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                      errors="replace", bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW)
        if self._proc.stdout is None:
            raise AudioError("ネイティブ音声ヘルパーの標準出力を開けません。")
        deadline = time.monotonic() + 10.0
        lines = []
        while time.monotonic() < deadline:
            line = self._proc.stdout.readline().strip()
            if line:
                lines.append(line)
                audio_log(f"native helper: {line}")
                if line.startswith("START"):
                    self.t0 = time.perf_counter()
                    return
            if self._proc.poll() is not None:
                break
        code = self._proc.poll()
        detail = " | ".join(lines[-5:])
        self._proc = None
        raise AudioError(f"ネイティブProcess Loopbackの開始に失敗しました (code={code}) {detail}")

    def stop(self) -> float:
        proc = self._proc
        self._proc = None
        if proc is None:
            return 0.0
        started = self.t0 or time.perf_counter()
        try:
            if proc.stdin:
                proc.stdin.write("STOP\n")
                proc.stdin.flush()
                proc.stdin.close()
            proc.wait(timeout=15)
            out = proc.stdout.read() if proc.stdout else ""
            dur = max(0.0, time.perf_counter() - started)
            if proc.returncode != 0:
                audio_log(f"native helper exit code={proc.returncode} output={out[-1000:]}", "ERROR")
                raise AudioError(f"ネイティブLoL音声ヘルパーが終了しました (code={proc.returncode}): {out[-1000:]}")
            audio_log(f"native process loopback stopped duration={dur:.3f}s")
            return dur
        except subprocess.TimeoutExpired as e:
            try: proc.kill()
            except Exception: pass
            raise AudioError("ネイティブLoL音声の録音停止がタイムアウトしました") from e


class SyntheticAudio(AudioCapture):
    """テスト用: 440Hz のサイン波を実時間で書き出す。"""

    def __init__(self, path: Path, rate: int = 48000):
        self.path, self.rate = Path(path), rate
        self._stop = threading.Event()
        self._th: Optional[threading.Thread] = None
        self._wr: Optional[PaddedWavWriter] = None

    def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.t0 = time.perf_counter()
        self._wr = PaddedWavWriter(self.path, self.rate, 2, self.t0)
        self._stop.clear()
        self._th = threading.Thread(target=self._run, daemon=True)
        self._th.start()

    def _run(self) -> None:
        n, chunk = 0, int(self.rate * 0.02)
        while not self._stop.is_set():
            samples = []
            for i in range(chunk):
                v = int(9000 * math.sin(2 * math.pi * 440 * (n + i) / self.rate))
                samples.append(struct.pack("<hh", v, v))
            n += chunk
            self._wr.write(b"".join(samples), time.perf_counter())
            time.sleep(0.02)

    def stop(self) -> float:
        self._stop.set()
        if self._th:
            self._th.join(timeout=1.0)
        return self._wr.finish(time.perf_counter()) if self._wr else 0.0
