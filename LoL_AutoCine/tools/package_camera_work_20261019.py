"""Build source Windows test ZIP + code delta, with immutable asset integrity manifest."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

APP=Path(__file__).resolve().parents[1]
REPO=APP.parent
BASE='de453046c2e2a7f522571e4d45d804947b05a150'


def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    names=git('ls-files','-z','--','LoL_AutoCine').decode('utf-8').split('\0')
    files=[n for n in names if n and (REPO/n).is_file() and
           not any(p in {'diagnostics','.venv','__pycache__','.pytest_cache','projects','output','outputs'} for p in Path(n).parts)
           and Path(n).name!='settings.json' and Path(n).suffix.lower() not in {'.log','.mp4','.mkv','.wav','.pyc'}]
    changed=set(git('diff','--name-only',BASE,'HEAD','--','LoL_AutoCine').decode('utf-8').splitlines())
    version=dict(base=BASE,commit=git('rev-parse','HEAD').decode().strip(),
                 branch=git('branch','--show-current').decode().strip(),
                 distribution='source Windows test build; Python and C++ tools not bundled',
                 real_lol_visual_qa='not_performed')
    manifest=[]
    full=output/'LoL_AutoCine_20261020_GPU_Work_Full.zip'
    delta=output/'LoL_AutoCine_CameraWork_20261019_Codex_Code_Delta.zip'
    for target,selected in ((full,files),(delta,[n for n in files if n in changed and Path(n).suffix.lower()!='.png'])):
        with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=4) as archive:
            for name in sorted(selected):
                path=REPO/name
                data=path.read_bytes()
                archive.writestr(name,data,compress_type=ZIP_STORED if path.suffix.lower()=='.png' else ZIP_DEFLATED)
                if target==full: manifest.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            archive.writestr('BUILD_INFO.json',json.dumps(version,indent=2))
            archive.writestr('README_TEST_JA.txt',
                '2026-10-20の修正を含むWindowsテスト版です。新しいフォルダに展開してください。\n'
                '起動: LoL_AutoCine/START.bat\n'
                'テスト順: LoL_AutoCine/docs/QA_GPU_WORK_20261020_JA.md\n'
                'Python 3.12 x64を自動検出して初回セットアップします。pyは必須ではありません。Native Audio Helper構築フローは既存通りです。\n'
                'このFull版には現在のコードとWork素材を同梱しています。\n'
                'ミラー映像はOpenCL GPU優先。非対応効果はCPUへ自動復帰します。\n'
                '652候補・35演出案は確認可能ですが、正式合格はNo.083 Aのみです。\n')
        with ZipFile(target) as archive:
            assert archive.testzip() is None
        print(target.name,target.stat().st_size,flush=True)
    (output/'PACKAGE_MANIFEST.json').write_text(json.dumps(dict(build=version,files=manifest),indent=2),'utf-8')
    sums=[]
    for path in (full,delta):
        digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
        sums.append(f'{digest}  {path.name}')
    (output/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n','utf-8')


if __name__=='__main__': main()
