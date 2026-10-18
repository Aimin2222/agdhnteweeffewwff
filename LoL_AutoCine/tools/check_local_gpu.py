"""Validate the explicitly selected FFmpeg without installing anything."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.gpu_pipeline import FFMPEG, detect, backend_name

if __name__ == '__main__':
    caps = detect()
    print('FFmpeg:', FFMPEG)
    print('Backend:', backend_name(caps))
    if not caps.full_gpu_runtime_ok:
        print('Reason:', caps.full_probe_reason)
    raise SystemExit(0 if caps.full_gpu_runtime_ok else 1)
