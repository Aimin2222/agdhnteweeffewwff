"""Launch real Windows PowerShell without py; do not install global Python."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import pytest

pytestmark=pytest.mark.skipif(sys.platform!='win32',reason='Windows launcher integration')
ROOT=Path(__file__).resolve().parents[1]
POWERSHELL=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'


def setup_folder(tmp_path):
    app=tmp_path/'App with spaces'
    (app/'tools').mkdir(parents=True)
    shutil.copy2(ROOT/'tools/bootstrap_python.ps1',app/'tools/bootstrap_python.ps1')
    env=dict(os.environ)
    env.pop('AUTOCINE_PYTHON',None)
    env['SYSTEMROOT']=os.environ.get('SystemRoot','C:/Windows')
    env['PATH']=str(Path(env['SYSTEMROOT'])/'System32')
    return app,env


def run(app,env,*args):
    return subprocess.run([str(POWERSHELL),'-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(app/'tools/bootstrap_python.ps1'),*args],env=env,capture_output=True,timeout=25)


def test_no_py_uses_real_bundled_runtime(tmp_path):
    app,env=setup_folder(tmp_path)
    # No PATH Python or py. A real runtime can be located without invoking Store aliases.
    env['AUTOCINE_PYTHON']=sys.executable
    result=run(app,env,'-Mode','Probe')
    assert result.returncode==0,result.stdout+result.stderr
    assert b'[Python] Found:' in result.stdout


def test_missing_python_reports_actionable_error_instead_of_9009(tmp_path):
    app,env=setup_folder(tmp_path)
    for key in ('USERPROFILE','LOCALAPPDATA','PROGRAMFILES'):
        env[key]=str(tmp_path/'empty')
    result=run(app,env,'-Mode','Probe')
    assert result.returncode==2
    assert b'64-bit' in result.stdout and b'not found' in result.stdout


def test_incomplete_environment_is_kept_and_not_overwritten(tmp_path):
    app,env=setup_folder(tmp_path)
    env['AUTOCINE_PYTHON']=sys.executable
    (app/'.venv').mkdir()
    marker=app/'.venv/keep.txt';marker.write_text('existing user data')
    result=run(app,env,'-Mode','Setup')
    assert result.returncode==3,result.stdout+result.stderr
    assert marker.read_text()=='existing user data'


def test_start_bat_preserves_audio_helper_and_app_exit_code_without_py(tmp_path):
    app,env=setup_folder(tmp_path)
    shutil.copy2(ROOT/'START.bat',app/'START.bat')
    subprocess.run([sys.executable,'-m','venv','--without-pip',str(app/'.venv')],check=True,timeout=30)
    packages=app/'.venv/Lib/site-packages';packages.mkdir(parents=True,exist_ok=True)
    for name in ('numpy','PIL','imageio_ffmpeg','windows_capture','yt_dlp','pycaw','pyaudiowpatch','psutil'):
        (packages/(name+'.py')).write_text('# launcher-only fixture\n')
    (app/'.venv/autocine-ready.txt').write_text('launcher fixture; actual dependency installation tested separately')
    (app/'tools/bin').mkdir()
    helper=app/'tools/bin/lol_audio_helper.exe';helper.write_bytes(b'launcher fixture; never executed')
    (app/'app.py').write_text("import sys\nprint('BOOTSTRAP_APP_STARTED')\nsys.exit(23)\n")
    result=subprocess.run([str(Path(env['SYSTEMROOT'])/'System32/cmd.exe'),'/d','/c','START.bat'],
        cwd=app,env=env,input=b'\n',capture_output=True,timeout=30)
    assert result.returncode==23,result.stdout+result.stderr
    assert b'BOOTSTRAP_APP_STARTED' in result.stdout and b'exited with code 23' in result.stdout
    assert helper.read_bytes()==b'launcher fixture; never executed'


def test_diagnostics_without_py_or_dependencies_creates_zip(tmp_path):
    app,env=setup_folder(tmp_path)
    env['AUTOCINE_PYTHON']=sys.executable
    shutil.copy2(ROOT/'COLLECT_DIAGNOSTICS.bat',app/'COLLECT_DIAGNOSTICS.bat')
    shutil.copy2(ROOT/'tools/collect_diagnostics.py',app/'tools/collect_diagnostics.py')
    (app/'diagnostics').mkdir()
    (app/'diagnostics/runtime.log').write_text('mirror evidence')
    result=subprocess.run([str(Path(env['SYSTEMROOT'])/'System32/cmd.exe'),'/d','/c','COLLECT_DIAGNOSTICS.bat'],
        cwd=app,env=env,input=b'\n',capture_output=True,timeout=30)
    assert result.returncode==0,result.stdout+result.stderr
    from zipfile import ZipFile
    with ZipFile(app/'AutoCine_Diagnostics.zip') as archive:
        assert archive.read('diagnostics/runtime.log')==b'mirror evidence'
        assert 'diagnostics/collector_environment.json' in archive.namelist()
    assert not (app/'.venv').exists()  # collection must not install app dependencies
