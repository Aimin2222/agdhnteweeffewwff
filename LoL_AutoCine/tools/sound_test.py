# -*- coding: utf-8 -*-
"""LoL AutoCine 起動前サウンド診断。

LoLリプレイを再生した状態で実行し、
1) Python/依存関係
2) LoL PID
3) プロセスループバック
4) WAVの実信号
を順番に確認する。
"""
from __future__ import annotations

import json
import os
import sys
import time
import wave
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audio import PreferredGameAudio, AudioError  # noqa: E402
from core.audio_log import log as audio_log, reset as reset_audio_log  # noqa: E402
from core.procloop import lol_pid  # noqa: E402

OUT = ROOT / "diagnostics" / "lol_audio_test.wav"
REPORT = ROOT / "diagnostics" / "audio_test_result.json"


def result(status: str, **extra):
    data = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": status,
        **extra,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def main() -> int:
    reset_audio_log()
    audio_log("=== SOUND TEST BEGIN ===")
    print("============================================")
    print(" LoL AutoCine - サウンドテスト")
    print("============================================")
    print()
    print("[準備] LoLのリプレイを再生し、ゲーム音が鳴る状態にしてください。")
    print("       できれば戦闘/効果音が鳴る場面でテストしてください。")
    input("準備できたら Enter を押してください... ")

    pid = lol_pid()
    print(f"[1/4] LoL PID: {pid or '見つかりません'}")
    audio_log(f"preflight LoL PID={pid}")
    if not pid:
        print("[FAIL] League of Legends.exe が見つかりません。")
        result("FAIL", reason="LoL process not found")
        return 2

    try:
        import pyaudiowpatch as pyaudio  # type: ignore
        print("[2/4] PyAudioWPatch: OK")
        audio_log("PyAudioWPatch import OK")
        p = pyaudio.PyAudio()
        try:
            wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_dev = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
            print(f"       出力デバイス: {default_dev.get('name', '?')}")
            audio_log(f"default WASAPI output={default_dev.get('name')} index={default_dev.get('index')}")
            loopbacks = []
            for dev in p.get_loopback_device_info_generator():
                loopbacks.append(dev.get("name", "?"))
            print(f"       ループバック候補: {len(loopbacks)}")
            for name in loopbacks[:8]:
                print(f"         - {name}")
            audio_log(f"loopback devices={loopbacks[:8]}")
        finally:
            p.terminate()
    except Exception as e:
        print(f"[FAIL] PyAudioWPatch: {e}")
        audio_log(f"PyAudioWPatch preflight failed: {type(e).__name__}: {e}", "ERROR")
        result("FAIL", reason="PyAudioWPatch unavailable", error=str(e), pid=pid)
        return 3

    try:
        print("[3/4] LoLプロセス音声の録音テストを開始します（5秒）...")
        rec = PreferredGameAudio(OUT)
        rec.start()
        print("       録音開始: OK")
        time.sleep(5.0)
        dur = rec.stop()
        print(f"       録音停止: OK ({dur:.2f}s)")
    except AudioError as e:
        print(f"[FAIL] 録音開始/停止: {e}")
        audio_log(f"recording failed: {type(e).__name__}: {e}", "ERROR")
        result("FAIL", reason="recording failed", error=str(e), pid=pid)
        return 4
    except Exception as e:
        print(f"[FAIL] 予期しないエラー: {type(e).__name__}: {e}")
        audio_log(f"unexpected recording error: {type(e).__name__}: {e}", "ERROR")
        result("FAIL", reason="unexpected error", error=str(e), pid=pid)
        return 5

    try:
        with wave.open(str(OUT), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            raw = wf.readframes(frames)
        nonzero = any(b != 0 for b in raw)
        size = OUT.stat().st_size
        print(f"[4/4] WAV検証: {rate}Hz / {channels}ch / {width * 8}bit / {frames} frames / {size} bytes")
        audio_log(f"WAV verify rate={rate} channels={channels} bits={width*8} frames={frames} size={size} nonzero={nonzero}")
        if not nonzero:
            print("[FAIL] WAVは完全な無音です。Windows出力デバイスとLoL音量を確認してください。")
            result("FAIL", reason="silent WAV", pid=pid, wav=str(OUT), rate=rate, channels=channels, frames=frames)
            return 6
    except Exception as e:
        print(f"[FAIL] WAV検証: {type(e).__name__}: {e}")
        audio_log(f"WAV verify failed: {type(e).__name__}: {e}", "ERROR")
        result("FAIL", reason="wav verify failed", error=str(e), pid=pid)
        return 7

    result("PASS", pid=pid, wav=str(OUT), duration=dur, rate=rate, channels=channels, frames=frames)
    audio_log("=== SOUND TEST PASS ===")
    print()
    print("[PASS] LoLゲーム音を録音できました。")
    print(f"       WAV: {OUT}")
    print(f"       ログ: {ROOT / 'diagnostics' / 'audio.log'}")
    print(f"       結果: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
