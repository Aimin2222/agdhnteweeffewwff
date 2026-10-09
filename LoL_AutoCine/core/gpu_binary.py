"""Select the verified optional Windows OpenCL build, preserving explicit overrides."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from functools import lru_cache

GPU_BUILD_URL = ('https://github.com/BtbN/FFmpeg-Builds/releases/download/'
                 'autobuild-2026-10-08-13-05/ffmpeg-n8.1.3-14-g330caae0c1-win64-gpl-8.1.zip')
GPU_ARCHIVE_SHA256 = '6e63b4f8aae35949f4a5b471784f97a51b29b2466038769e3f8ecf513316ec6c'
GPU_CACHE = Path(__file__).resolve().parent.parent/'tools'/'bin'/'ffmpeg_gpu'


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verified_gpu_binary(cache=GPU_CACHE):
    try:
        info = json.loads((Path(cache)/'installed.json').read_text(encoding='utf-8'))
        binary = Path(cache)/GPU_ARCHIVE_SHA256/'ffmpeg.exe'
        if info.get('archive_sha256') == GPU_ARCHIVE_SHA256 and sha256_file(binary) == info.get('exe_sha256'):
            return str(binary)
    except (OSError, ValueError, TypeError):
        pass
    return None


@lru_cache(maxsize=1)
def ffmpeg_exe():
    # IMAGEIO_FFMPEG_EXE remains an explicit user choice.
    if not os.environ.get('IMAGEIO_FFMPEG_EXE') and sys.platform == 'win32':
        binary = verified_gpu_binary()
        if binary:
            return binary
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return shutil.which('ffmpeg') or shutil.which('ffmpeg.exe') or 'ffmpeg'
