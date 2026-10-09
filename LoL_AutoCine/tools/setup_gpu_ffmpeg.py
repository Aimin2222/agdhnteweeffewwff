"""Install one checksum-pinned BtbN Windows FFmpeg build, leaving bundled FFmpeg intact."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from core.gpu_binary import (GPU_BUILD_URL, GPU_ARCHIVE_SHA256, GPU_CACHE,
                             sha256_file, verified_gpu_binary)


def install_archive(archive, cache=GPU_CACHE):
    archive, cache = Path(archive), Path(cache)
    if sha256_file(archive) != GPU_ARCHIVE_SHA256:
        raise RuntimeError('GPU FFmpeg archive checksum mismatch; nothing installed')
    target = cache/GPU_ARCHIVE_SHA256
    if target.exists():
        raise RuntimeError('Existing GPU build directory is preserved; use its verified installation or a new folder')
    with zipfile.ZipFile(archive) as z:
        matches = [i for i in z.infolist() if i.filename.endswith('/bin/ffmpeg.exe')]
        if len(matches) != 1 or not 0 < matches[0].file_size < 250*1024*1024:
            raise RuntimeError('Archive has no unique bounded ffmpeg.exe')
        cache.mkdir(parents=True,exist_ok=True)
        # Only copy the exact binary and license text, never arbitrary archive paths.
        with tempfile.TemporaryDirectory(prefix='install-',dir=cache) as folder:
            stage = Path(folder)
            binary = stage/'ffmpeg.exe'
            with z.open(matches[0]) as source, binary.open('wb') as out:
                shutil.copyfileobj(source,out)
            with binary.open('rb') as executable:
                header = executable.read(2)
            if header != b'MZ':
                raise RuntimeError('Not a Windows executable')
            licenses = [i for i in z.infolist() if i.filename.rsplit('/',1)[-1] in ('LICENSE.txt','LICENSE','COPYING.GPLv3')]
            for i, item in enumerate(licenses):
                if item.file_size < 1024*1024:
                    (stage/f'LICENSE_{i}.txt').write_bytes(z.read(item))
            binary_hash = sha256_file(binary)
            # Validate required filters and encoder registrations before activation.
            result = subprocess.run([str(binary),'-hide_banner','-filters'],capture_output=True,text=True,timeout=20)
            if result.returncode or 'program_opencl' not in result.stdout or 'avgblur_opencl' not in result.stdout:
                raise RuntimeError('This FFmpeg cannot run the required OpenCL filters')
            enc = subprocess.run([str(binary),'-hide_banner','-encoders'],capture_output=True,text=True,timeout=20)
            if enc.returncode or 'h264_nvenc' not in enc.stdout or 'libx264' not in enc.stdout:
                raise RuntimeError('Required NVENC/CPU encoders are missing')
            stage.rename(target)
        info = {'archive_sha256':GPU_ARCHIVE_SHA256,'exe_sha256':binary_hash,'source':GPU_BUILD_URL}
        marker = cache/'installed.json.tmp'
        marker.write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
        marker.replace(cache/'installed.json')
    return target/'ffmpeg.exe'


def setup():
    if sys.platform != 'win32':
        raise RuntimeError('GPU FFmpeg setup is for Windows; the current bundled FFmpeg is unchanged')
    existing = verified_gpu_binary()
    if existing:
        print('[GPU] Verified OpenCL FFmpeg ready:', existing)
        return
    print('[GPU] Downloading a checksum-pinned BtbN OpenCL FFmpeg build (~200 MB).',flush=True)
    with tempfile.TemporaryDirectory(prefix='autocine-ffmpeg-download-') as folder:
        archive = Path(folder)/'ffmpeg.zip'
        request = urllib.request.Request(GPU_BUILD_URL,headers={'User-Agent':'LoL-AutoCine-GPU-Setup'})
        total = 0
        with urllib.request.urlopen(request,timeout=60) as response, archive.open('wb') as out:
            for chunk in iter(lambda: response.read(1024*1024), b''):
                total += len(chunk)
                if total > 350*1024*1024:
                    raise RuntimeError('Unexpectedly large GPU FFmpeg download')
                out.write(chunk)
                if total % (10*1024*1024) < len(chunk):
                    print(f'[GPU] {total//1048576} MB downloaded',flush=True)
        binary = install_archive(archive)
    print('[GPU] Installed verified FFmpeg:',binary)
    print('[GPU] Hardware execution is checked by the app. CPU fallback remains available.')


if __name__ == '__main__':
    try:
        setup()
    except Exception as e:
        print('[GPU] Setup failed:',e,file=sys.stderr)
        print('[GPU] Original START.bat and bundled FFmpeg remain available.',file=sys.stderr)
        sys.exit(1)
