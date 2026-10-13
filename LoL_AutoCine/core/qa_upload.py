"""Temporary developer-only CameraQA upload copies; never alters recordings.

Remove this adapter and its CameraQA call when shipping the consumer app.
Ordinary recording, effects and process-specific audio do not import it.
"""
from pathlib import Path
import math
import subprocess
import time

from .gpu_binary import ffmpeg_exe
from .montage_fx import get_duration
from .performance_diagnostics import record_encoding_result

MAX_ZIP_BYTES = 30_000_000  # Decimal MB: below the executor's 32 MiB limit.
MAX_VIDEO_BYTES = 24_000_000
UPLOAD_DIR = ".qa_upload"
EXCLUDE_DIRS = ("raw", UPLOAD_DIR)


class QAUploadCanceled(RuntimeError):
    pass


def _check_stop(stop):
    if stop is not None and stop.is_set():
        raise QAUploadCanceled("QA送信用コピーの作成を中止しました。元映像は保持しています。")


def _run(command, stop):
    """Drain pipes and promptly reap FFmpeg on cancel or timeout."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    deadline = time.monotonic() + 180
    try:
        while True:
            _check_stop(stop)
            if time.monotonic() > deadline:
                raise TimeoutError("QA送信用FFmpegが制限時間を超えました")
            try:
                _out, error = process.communicate(timeout=.2)
                return process.returncode, error.decode("utf-8", errors="replace")
            except subprocess.TimeoutExpired:
                continue
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()


def make_upload_video(source, destination, *, encoder_policy="auto", stop=None, log=lambda _m: None):
    """540p60 H.264, AAC stream copy, bounded bitrate and actual size check.

    Frames retain their original timestamps. No trim, speed change, frame
    interpolation, new audio capture or second application of video effects.
    NVENC is preferred; its failure is reported and a bounded CPU retry is used.
    """
    from .effects import encoder_args
    source, destination = Path(source), Path(destination)
    _check_stop(stop)
    duration = get_duration(source, ffmpeg=str(ffmpeg_exe()))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("QA動画の再生時間が不正です")
    # Reserve generous room for the existing AAC stream and MP4 headers.
    bitrate = min(3_000_000, int(MAX_VIDEO_BYTES * .86 * 8 / duration) - 512_000)
    if bitrate < 128_000:
        raise ValueError("QA動画が長すぎます。元動画を分割してZIPへ保存します")
    preferred = encoder_args(60, policy=encoder_policy)
    encoder = "h264_nvenc" if "h264_nvenc" in preferred else "libx264"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    temporary = destination.with_name(destination.stem + ".encoding.mp4")
    if temporary.exists():
        raise FileExistsError(temporary)
    retry_reason = None
    try:
        for attempt in range(3):
            _check_stop(stop)
            encoding = (["-c:v", encoder, "-preset", "p4", "-rc", "vbr"]
                        if encoder == "h264_nvenc" else
                        ["-c:v", encoder, "-preset", "veryfast"])
            command = [str(ffmpeg_exe()), "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                       "-i", str(source), "-map", "0:v:0", "-map", "0:a:0?",
                       "-vf", "scale=960:540:flags=bilinear:force_original_aspect_ratio=decrease,"
                       "pad=960:540:(ow-iw)/2:(oh-ih)/2,setsar=1",
                       *encoding, "-b:v", str(bitrate), "-maxrate", str(bitrate),
                       "-bufsize", str(bitrate * 2), "-pix_fmt", "yuv420p",
                       "-fps_mode", "passthrough", "-enc_time_base", "demux",
                       "-c:a", "copy", "-movflags", "+faststart", str(temporary)]
            code, error = _run(command, stop)
            record_encoding_result(command, output=destination, returncode=code,
                                   error=error[-800:] if code else None, fallback_reason=retry_reason,
                                   pipeline_info={"qa_only": True, "upload_copy": True,
                                                  "output_size": [960, 540], "output_fps": 60,
                                                  "duration_s": duration, "audio": "stream_copy",
                                                  "scale": "software_bilinear", "video_bitrate": bitrate})
            if code:
                if encoder == "h264_nvenc":
                    retry_reason = "QA送信用NVENC失敗 → 制限ビットレートのCPU再試行: " + error[-300:]
                    log(retry_reason)
                    encoder = "libx264"
                    continue
                raise RuntimeError("QA送信用FFmpegに失敗: " + error[-800:])
            size = temporary.stat().st_size
            if 0 < size <= MAX_VIDEO_BYTES:
                _check_stop(stop)
                temporary.replace(destination)
                return {"duration_seconds": duration, "bytes": size, "encoder": encoder,
                        "encoder_retry_reason": retry_reason, "resolution": [960, 540],
                        "fps": 60, "frame_timing": "passthrough", "audio": "stream_copy"}
            bitrate = max(128_000, int(bitrate * .7))
        raise RuntimeError("送信用動画が24MB以下になりません。元映像は保持しています")
    finally:
        temporary.unlink(missing_ok=True)


def prepare_upload_copies(folder, *, encoder_policy="auto", stop=None, log=lambda _m: None):
    """Mirror just final MP4s; failures fall back to lossless archive parts."""
    folder = Path(folder).resolve()
    report = {"qa_only": True, "profile": "dev-30mb-540p60", "max_zip_bytes": MAX_ZIP_BYTES,
              "originals_preserved": True, "excluded_archive_dirs": list(EXCLUDE_DIRS),
              "files": [], "limitations": "Upload copies are for framing/motion review, not final image-quality approval."}
    overrides = {}
    generation = 1
    while (folder / UPLOAD_DIR / f"export{generation:03d}").exists():
        generation += 1
    copy_root = folder / UPLOAD_DIR / f"export{generation:03d}"
    copy_root.mkdir(parents=True, exist_ok=False)
    for source in sorted(folder.rglob("*.mp4")):
        _check_stop(stop)
        relative = source.relative_to(folder)
        if any(part in EXCLUDE_DIRS for part in relative.parts[:-1]):
            continue
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(folder):
            continue
        row = {"path": relative.as_posix(), "original_bytes": source.stat().st_size}
        try:
            destination = copy_root / relative
            row.update(make_upload_video(source, destination, encoder_policy=encoder_policy, stop=stop, log=log))
            overrides[relative.as_posix()] = destination
            log(f"QA送信用540p60: {relative.as_posix()} / {row['bytes']/1_000_000:.2f}MB（元映像保持）")
        except QAUploadCanceled:
            raise
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["archive_fallback"] = "original_or_numbered_binary_parts"
            log(f"QA送信用の軽量化失敗: {relative.as_posix()}。元映像を30MB以下のZIPへ分割保存: {exc}")
        report["files"].append(row)
    return overrides, report
