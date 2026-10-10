# -*- coding: utf-8 -*-
"""LoL のプロセス音だけを録る (Windows 10 2004+ の WASAPI プロセスループバック)。

「デスクトップ全体の音」ではなく「League of Legends の音だけ」を録るための実装。
AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK を ctypes で直接叩く。

設計方針 (実機未検証のため安全側)
  - available() は「実際に IAudioClient を取得できるか」まで確認する。
  - 少しでも失敗したら False を返し、呼び出し側 (audio.py) がデスクトップ全体の
    ループバックへ自動フォールバックして、その旨をログに出す。
  - 出力は 16bit PCM / 48kHz / ステレオ固定。

参考: Microsoft "Application loopback" (ActivateAudioInterfaceAsync + VAD\\Process_Loopback)
"""
from __future__ import annotations

import ctypes
import sys
import threading
import time
from ctypes import POINTER, byref, c_void_p
from pathlib import Path
from typing import Optional

# Windows 専用の型 (非 Windows では import できないのでフォールバックする)
try:
    from ctypes import WINFUNCTYPE                     # type: ignore[attr-defined]
    from ctypes.wintypes import DWORD, HANDLE, LPCWSTR, WORD
except ImportError:                                    # Linux/macOS: 型定義だけ用意
    WINFUNCTYPE = None                                 # type: ignore[assignment]
    DWORD = ctypes.c_uint32
    HANDLE = ctypes.c_void_p
    WORD = ctypes.c_uint16
    LPCWSTR = ctypes.c_wchar_p

# ------------------------------------------------------------------ 定数
AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
AUDCLNT_STREAMFLAGS_EVENTCALLBACK = 0x00040000
AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM = 0x80000000
AUDCLNT_BUFFERFLAGS_SILENT = 0x00000002

AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK = 1
PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE = 0

VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK = "VAD\\Process_Loopback"

CLSID_MMDeviceEnumerator = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"
IID_IMMDeviceEnumerator = "{A95664D2-9614-4F35-A746-DE8DB63617E6}"
IID_IAudioClient = "{1CB9AD4C-DBFA-4c32-B178-C2F568A703B2}"
IID_IAudioCaptureClient = "{C8ADBD64-E71E-48a0-A4DE-185C395CD317}"
IID_IActivateAudioInterfaceCompletionHandler = "{41D949AB-9862-444A-80F6-C261334DA5EB}"

WAVE_FORMAT_PCM = 1
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

S_OK = 0
AUDCLNT_S_BUFFER_EMPTY = 0x08890001
AUDCLNT_E_DEVICE_INVALIDATED = -2004287480


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_uint32), ("Data2", ctypes.c_uint16),
                ("Data3", ctypes.c_uint16), ("Data4", ctypes.c_ubyte * 8)]


class _WAVEFORMATEX(ctypes.Structure):
    _fields_ = [("wFormatTag", WORD), ("nChannels", WORD), ("nSamplesPerSec", DWORD),
                ("nAvgBytesPerSec", DWORD), ("nBlockAlign", WORD), ("wBitsPerSample", WORD),
                ("cbSize", WORD)]


class _WAVEFORMATEXTENSIBLE(ctypes.Structure):
    _fields_ = [("Format", _WAVEFORMATEX), ("wValidBitsPerSample", WORD),
                ("dwChannelMask", DWORD), ("SubFormat", ctypes.c_ubyte * 16)]


class _AUDIOCLIENT_ACTIVATION_PARAMS(ctypes.Structure):
    _fields_ = [("ActivationType", ctypes.c_int), ("ProcessLoopbackMode", ctypes.c_int),
                ("TargetProcessId", DWORD)]


class _PROPVARIANT_BLOB(ctypes.Structure):
    _fields_ = [("vt", ctypes.c_ushort), ("wReserved1", ctypes.c_ushort),
                ("wReserved2", ctypes.c_ushort), ("wReserved3", ctypes.c_ushort),
                ("cbSize", ctypes.c_ulong), ("pBlobData", c_void_p)]


def _guid(s: str) -> _GUID:
    import uuid
    u = uuid.UUID(s.strip("{}"))
    return _GUID(u.time_low, u.time_mid, u.time_hi_version,
                 (ctypes.c_ubyte * 8)(*u.bytes[8:]))


def _vcall(ptr, index: int, restype, *argtypes):
    """COM オブジェクトの vtable[index] を呼ぶ関数を返す。"""
    vtbl = ctypes.cast(ptr, POINTER(POINTER(c_void_p))).contents[0]
    arr = ctypes.cast(vtbl, POINTER(c_void_p))
    proto = WINFUNCTYPE(restype, c_void_p, *argtypes)
    fn = proto(arr[index])

    def call(this, *args):
        return fn(this, *args)
    return call


def lol_pid() -> Optional[int]:
    """League of Legends の PID。ウィンドウ → プロセス名 の順で探す。"""
    if sys.platform != "win32":
        return None
    try:
        import ctypes as C
        from ctypes import wintypes
        user32 = C.windll.user32
        for title in ("League of Legends (TM) Client", "League of Legends"):
            hwnd = user32.FindWindowW(None, title)
            if hwnd:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, C.byref(pid))
                if pid.value:
                    return int(pid.value)
    except Exception:
        pass
    try:
        import ctypes as C

        class PROCESSENTRY32(C.Structure):
            _fields_ = [("dwSize", DWORD), ("cntUsage", DWORD), ("th32ProcessID", DWORD),
                        ("th32DefaultHeapID", c_void_p), ("th32ModuleID", DWORD),
                        ("cntThreads", DWORD), ("th32ParentProcessID", DWORD),
                        ("pcPriClassBase", ctypes.c_long), ("dwFlags", DWORD),
                        ("szExeFile", ctypes.c_char * 260)]

        k32 = C.windll.kernel32
        snap = k32.CreateToolhelp32Snapshot(0x00000002, 0)
        if snap == -1:
            return None
        e = PROCESSENTRY32()
        e.dwSize = C.sizeof(PROCESSENTRY32)
        try:
            if not k32.Process32First(snap, C.byref(e)):
                return None
            while True:
                if e.szExeFile.decode("mbcs", "ignore").lower() == "league of legends.exe":
                    return int(e.th32ProcessID)
                if not k32.Process32Next(snap, C.byref(e)):
                    break
        finally:
            k32.CloseHandle(snap)
    except Exception:
        return None
    return None


def _pcm_format(rate: int = 48000, channels: int = 2, bits: int = 16) -> _WAVEFORMATEXTENSIBLE:
    f = _WAVEFORMATEXTENSIBLE()
    f.Format.wFormatTag = WAVE_FORMAT_EXTENSIBLE
    f.Format.nChannels = channels
    f.Format.nSamplesPerSec = rate
    f.Format.wBitsPerSample = bits
    f.Format.nBlockAlign = channels * bits // 8
    f.Format.nAvgBytesPerSec = rate * f.Format.nBlockAlign
    f.Format.cbSize = ctypes.sizeof(_WAVEFORMATEXTENSIBLE) - ctypes.sizeof(_WAVEFORMATEX)
    f.wValidBitsPerSample = bits
    f.dwChannelMask = 3 if channels == 2 else 4
    import uuid
    sub = uuid.UUID("00000001-0000-0010-8000-00aa00389b71").bytes_le
    for i, b in enumerate(sub):
        f.SubFormat[i] = b
    return f


class _HandlerVtbl:
    """IActivateAudioInterfaceCompletionHandler の最小実装 (Python 側 COM オブジェクト)。"""

    def __init__(self, on_done):
        self.on_done = on_done
        self.event = threading.Event()
        self.activated = None
        self.result = None
        self._keep = []
        self._refcount = 1
        self._fn_qi = self._fn_addref = self._fn_release = self._fn_activated = None
        self._vtable = None
        self.ptr = None

    # QueryInterface / AddRef / Release
    def _qi(self, this, riid, ppv):
        ctypes.cast(ppv, POINTER(c_void_p))[0] = this
        return S_OK

    def _addref(self, this):
        self._refcount += 1
        return self._refcount

    def _release(self, this):
        self._refcount -= 1
        return self._refcount

    def _activate_completed(self, this, operation):
        try:
            res = ctypes.c_long(0)
            ptr = c_void_p()
            op_get = _vcall(operation, 3, ctypes.c_long, POINTER(ctypes.c_long), POINTER(c_void_p))
            hr = op_get(operation, byref(res), byref(ptr))
            self.result = hr
            self.activated = ptr.value
        except Exception as e:                       # noqa: BLE001
            self.result = f"exception: {e}"
        finally:
            self.event.set()
        return S_OK


def _make_handler():
    if WINFUNCTYPE is None:
        raise RuntimeError("Windows 以外ではプロセスループバックを使えません")
    h = _HandlerVtbl(lambda: None)
    # ctypes のコールバックはインスタンス生成後に束縛する
    QI = WINFUNCTYPE(ctypes.c_long, c_void_p, c_void_p, c_void_p)
    AR = WINFUNCTYPE(ctypes.c_ulong, c_void_p)
    AC = WINFUNCTYPE(ctypes.c_long, c_void_p, c_void_p)
    h._fn_qi = QI(h._qi)
    h._fn_addref = AR(h._addref)
    h._fn_release = AR(h._release)
    h._fn_activated = AC(h._activate_completed)
    h._keep = [h._fn_qi, h._fn_addref, h._fn_release, h._fn_activated]
    h._vtable = (c_void_p * 4)(
        ctypes.cast(h._fn_qi, c_void_p), ctypes.cast(h._fn_addref, c_void_p),
        ctypes.cast(h._fn_release, c_void_p), ctypes.cast(h._fn_activated, c_void_p),
    )
    h.ptr = ctypes.cast(ctypes.pointer(h._vtable), c_void_p)
    return h


class ProcessLoopbackClient:
    """LoL プロセスの音を取る IAudioClient / IAudioCaptureClient のラッパ。"""

    def __init__(self, pid: int, rate: int = 48000, channels: int = 2):
        self.pid, self.rate, self.channels = pid, rate, channels
        self.client: Optional[int] = None
        self.capture = None
        self.event = None
        self.buffer_frames = 0

    def open(self) -> None:
        import ctypes as C
        ole32 = C.windll.ole32
        ole32.CoInitializeEx(None, 0x2)      # APARTMENTTHREADED
        mmdev = C.WinDLL("Mmdevapi.dll")

        act_async = mmdev.ActivateAudioInterfaceAsync
        act_async.restype = ctypes.c_long
        act_async.argtypes = [LPCWSTR, c_void_p, c_void_p, c_void_p, POINTER(c_void_p)]

        params = _AUDIOCLIENT_ACTIVATION_PARAMS()
        params.ActivationType = AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK
        params.ProcessLoopbackMode = PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE
        params.TargetProcessId = self.pid

        pv = _PROPVARIANT_BLOB()
        pv.vt = 65                                            # VT_BLOB
        pv.cbSize = C.sizeof(params)
        pv.pBlobData = C.cast(C.pointer(params), c_void_p)

        handler = _make_handler()
        op = c_void_p()
        iid = _guid(IID_IAudioClient)
        hr = act_async(VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK, ctypes.cast(C.pointer(iid), c_void_p),
                       ctypes.cast(C.pointer(pv), c_void_p), handler.ptr, byref(op))
        if hr != S_OK:
            raise RuntimeError(f"ActivateAudioInterfaceAsync 失敗 hr=0x{hr & 0xFFFFFFFF:08x}")
        if not handler.event.wait(3.0):
            raise RuntimeError("プロセスループバックの有効化がタイムアウトしました")
        if not handler.activated:
            raise RuntimeError(f"IAudioClient を取得できません (hr={handler.result})")
        self.client = handler.activated

        fmt = _pcm_format(self.rate, self.channels)
        init = _vcall(self.client, 3, ctypes.c_long, ctypes.c_int, DWORD, ctypes.c_longlong,
                      ctypes.c_longlong, c_void_p, c_void_p)
        flags = (AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_EVENTCALLBACK |
                 AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM)
        # Process loopback is event-driven; use the endpoint default period rather than
        # forcing a 200 ms/2 s-style duration. This matches the Windows sample.
        hr = init(self.client, AUDCLNT_SHAREMODE_SHARED, flags, 0, 0,
                  ctypes.cast(byref(fmt), c_void_p), None)
        if hr != S_OK:
            raise RuntimeError(f"IAudioClient::Initialize 失敗 hr=0x{hr & 0xFFFFFFFF:08x}")

        self.event = C.windll.kernel32.CreateEventW(None, False, False, None)
        set_evt = _vcall(self.client, 13, ctypes.c_long, HANDLE)
        if set_evt(self.client, HANDLE(self.event)) != S_OK:
            raise RuntimeError("SetEventHandle に失敗しました")

        svc = _vcall(self.client, 14, ctypes.c_long, c_void_p, c_void_p)
        cap = c_void_p()
        iid_cap = _guid(IID_IAudioCaptureClient)
        if svc(self.client, ctypes.cast(C.pointer(iid_cap), c_void_p),
               ctypes.cast(byref(cap), c_void_p)) != S_OK:
            raise RuntimeError("IAudioCaptureClient を取得できません")
        self.capture = cap

        get_buf = _vcall(self.client, 4, ctypes.c_long, POINTER(ctypes.c_uint32))
        n = ctypes.c_uint32(0)
        if get_buf(self.client, byref(n)) == S_OK:
            self.buffer_frames = int(n.value)

    def start(self) -> None:
        start = _vcall(self.client, 10, ctypes.c_long)
        start(self.client)

    def read(self, timeout_ms: int = 200) -> Optional[bytes]:
        """1ブロック読む。データが無ければ None。"""
        import ctypes as C
        if C.windll.kernel32.WaitForSingleObject(HANDLE(self.event), timeout_ms) != 0:
            return None
        out = bytearray()
        get_buffer = _vcall(self.capture, 3, ctypes.c_long, POINTER(c_void_p),
                            POINTER(ctypes.c_uint32), POINTER(DWORD), POINTER(ctypes.c_uint64),
                            POINTER(ctypes.c_uint64))
        release = _vcall(self.capture, 4, ctypes.c_long, ctypes.c_uint32)
        next_pkt = _vcall(self.capture, 5, ctypes.c_long, POINTER(ctypes.c_uint32))
        while True:
            data = c_void_p()
            frames = ctypes.c_uint32(0)
            flags = DWORD(0)
            devpos = ctypes.c_uint64(0)
            qpc = ctypes.c_uint64(0)
            if get_buffer(self.capture, byref(data), byref(frames), byref(flags),
                          byref(devpos), byref(qpc)) != S_OK:
                break
            if frames.value and data.value:
                size = frames.value * self.channels * 2
                if flags.value & AUDCLNT_BUFFERFLAGS_SILENT:
                    out += b"\x00" * size
                else:
                    out += C.string_at(data.value, size)
            release(self.capture, frames)
            n = ctypes.c_uint32(0)
            if next_pkt(self.capture, byref(n)) != S_OK or n.value == 0:
                break
        return bytes(out) if out else None

    def close(self) -> None:
        try:
            if self.client is not None:
                _vcall(self.client, 11, ctypes.c_long)(self.client)      # Stop
        except Exception:
            pass
        for p in (self.capture, self.client):
            try:
                if p:
                    _vcall(p, 2, ctypes.c_ulong)(p)                      # Release
            except Exception:
                pass
        self.capture = self.client = None


def available() -> tuple:
    """使えるかどうかと理由を返す。PID が取れなければ False。"""
    if sys.platform != "win32":
        return False, "Windows 以外ではプロセス音声を録音できません"
    if sys.getwindowsversion().build < 20348:                # noqa: SIM105
        return False, "Windows 10 build 20348 以降が必要です"
    pid = lol_pid()
    if not pid:
        return False, "LoL のプロセスが見つかりません (リプレイを再生してから録画してください)"
    try:
        c = ProcessLoopbackClient(pid)
        c.open()
        c.close()
    except Exception as e:                                   # noqa: BLE001
        return False, f"プロセスループバックを使えません: {e}"
    return True, ""


class ProcessLoopbackRecorder:
    """LoL の音だけを WAV に録る (16bit / 48kHz / stereo)。start() が失敗したら例外。"""

    def __init__(self, wav_path: Path, rate: int = 48000, channels: int = 2):
        self.path = Path(wav_path)
        self.rate, self.channels = rate, channels
        self.t0 = 0.0
        self.error: Optional[str] = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._client: Optional[ProcessLoopbackClient] = None
        self._frames = 0
        self._wav = None

    def start(self) -> None:
        pid = lol_pid()
        if not pid:
            raise RuntimeError("LoL のプロセスが見つかりません")
        self._client = ProcessLoopbackClient(pid, self.rate, self.channels)
        self._client.open()
        import wave
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._wav = wave.open(str(self.path), "wb")
        self._wav.setnchannels(self.channels)
        self._wav.setsampwidth(2)
        self._wav.setframerate(self.rate)
        self.t0 = time.perf_counter()
        self._client.start()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            while not self._stop.is_set():
                chunk = self._client.read(200)
                if chunk:
                    n = len(chunk) // (self.channels * 2)
                    self._frames += n
                    self._wav.writeframes(chunk)
                    if (self._frames // self.rate) != ((self._frames - n) // self.rate):
                        try:
                            self._wav._file.flush()
                        except Exception:
                            pass
        except Exception as e:                                # noqa: BLE001
            self.error = str(e)

    def stop(self) -> float:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        dur = self._frames / float(self.rate)
        try:
            if self._client is not None:
                self._client.close()
        except Exception:
            pass
        try:
            if self._wav is not None:
                self._wav.close()
        except Exception:
            pass
        self._client = None
        self._wav = None
        return dur
