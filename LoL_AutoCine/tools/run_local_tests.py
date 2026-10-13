"""Run existing tests in a disposable source copy; keep reports local.

Separate pytest processes follow the existing CI's twelve-file batches to
avoid accumulating destroyed Tk roots. Run with the LoL game process closed;
the existing suite's integration cases use synthetic sources.
"""
from pathlib import Path
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def copy_source(destination):
    excluded = {'.venv', 'venv', '.git', '__pycache__', '.pytest_cache',
                'diagnostics', 'output', 'outputs', 'clips', 'settings.json',
                'bin', '.env', '.env.*', '*.rofl', '*.wav', '*.mp4', '*.log'}
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(*excluded))
    (destination / 'diagnostics').mkdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pytest-only', action='store_true')
    parser.add_argument('--test-file', action='append', help='Existing tests/test_*.py path; repeatable')
    args = parser.parse_args()
    try:
        import pytest  # noqa: F401
        import psutil
    except ImportError:
        print('pytest is missing. Run SETUP_DEV_ENV.bat.', file=sys.stderr)
        return 2
    if any((process.info.get('name') or '').lower() == 'league of legends.exe'
           for process in psutil.process_iter(['name'], ad_value='')):
        print('Close the LoL game/replay before running synthetic tests.', file=sys.stderr)
        return 2
    report_dir = ROOT / 'diagnostics' / 'local_dev' / dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    report_dir.mkdir(parents=True)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
               PYTHONDONTWRITEBYTECODE='1')
    results = []
    with tempfile.TemporaryDirectory(prefix='autocine-local-tests-') as temporary:
        workspace = Path(temporary) / 'LoL_AutoCine'
        copy_source(workspace)
        # Keep the same verified optional FFmpeg when installed; never install it here.
        sys.path.insert(0, str(ROOT))
        from core.gpu_binary import ffmpeg_exe
        env['IMAGEIO_FFMPEG_EXE'] = ffmpeg_exe()
        files = sorted(workspace.joinpath('tests').rglob('test_*.py'))
        if args.test_file:
            requested = {Path(name).as_posix() for name in args.test_file}
            available = {p.relative_to(workspace).as_posix(): p for p in files}
            if not requested <= available.keys():
                parser.error('Only existing tests/test_*.py paths are accepted')
            files = sorted(available[name] for name in requested)
        if not files:
            raise RuntimeError('No existing test files found')
        commands = []
        for start in range(0, len(files), 12):
            commands.append((f'pytest_{start // 12 + 1:02}',
                             ['-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                              '--basetemp', str(workspace / f'_pytest_tmp_{start // 12 + 1:02}'),
                              *[str(p.relative_to(workspace)) for p in files[start:start + 12]]]))
        if not args.pytest_only:
            commands.append(('legacy', ['tests/run_tests.py']))
        for label, command in commands:
            print(f'Running {label}...', flush=True)
            result = subprocess.run([sys.executable, '-B', *command], cwd=workspace,
                                    env=env, capture_output=True, text=True,
                                    encoding='utf-8', errors='replace', timeout=1200)
            output = result.stdout + result.stderr
            (report_dir / f'{label}.log').write_text(output, encoding='utf-8')
            print(output, flush=True)
            results.append({'suite': label, 'returncode': result.returncode})
        shutil.copytree(workspace / 'diagnostics', report_dir / 'test_diagnostics')
    summary = {'python': sys.version, 'ffmpeg': env['IMAGEIO_FFMPEG_EXE'],
               'test_files': len(files), 'results': results,
               'real_lol_validation': 'not_performed'}
    (report_dir / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'Local reports: {report_dir}', flush=True)
    return 0 if all(item['returncode'] == 0 for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
