# -*- coding: utf-8 -*-
"""LoLゲーム音の単体診断。リプレイを再生してから実行する。"""
from __future__ import annotations
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audio import PreferredGameAudio, AudioError  # noqa: E402

out = ROOT / "diagnostics" / "lol_audio_test.wav"
out.parent.mkdir(parents=True, exist_ok=True)
try:
    rec = PreferredGameAudio(out)
    print("[1/3] LoL音声録音を開始します…")
    rec.start()
    print("[2/3] 5秒待機中。LoLの音が鳴る場面で実行してください。")
    time.sleep(5.0)
    dur = rec.stop()
    print(f"録音時間: {dur:.2f}s")
    with wave.open(str(out), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        channels = wf.getnchannels()
        raw = wf.readframes(frames)
    nonzero = any(b != 0 for b in raw)
    print(f"WAV: {out}")
    print(f"format: PCM / {rate}Hz / {channels}ch / {frames} frames")
    if not nonzero:
        print("[FAIL] WAVは完全な無音です。LoLの出力デバイス/音量を確認してください。")
        raise SystemExit(2)
    print("[OK] LoL音声の信号を検出しました。")
except AudioError as e:
    print(f"[FAIL] {e}")
    raise SystemExit(3)
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    raise SystemExit(4)
