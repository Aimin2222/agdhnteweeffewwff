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
ROOT_BATS={'START.bat','START_GPU.bat','START_LOCAL_GPU.bat',
           'BUILD_AUDIO_HELPER.bat','ENSURE_CPP_BUILD_TOOLS.bat',
           'COLLECT_DIAGNOSTICS.bat'}


def packaged_file(name, data):
    """Keep all launchers, but put secondary ones in one clearly named folder.

    Source BAT files stay in their original paths for developer workflows.
    The package copies secondary launchers one level down and re-bases only
    their %~dp0 references; each script still changes to the app root first.
    """
    path=Path(name)
    if len(path.parts)==2 and path.suffix.lower()=='.bat' and path.name not in ROOT_BATS:
        return f'LoL_AutoCine/Developer_Tools/{path.name}',data.replace(b'%~dp0',b'%~dp0..\\')
    return name,data


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
    full=output/'LoL_AutoCine_20261020_Responsive_Gallery_Full.zip'
    delta=output/'LoL_AutoCine_20261020_Responsive_Gallery_Code_Delta.zip'
    for target,selected in ((full,files),(delta,[n for n in files if n in changed and Path(n).suffix.lower()!='.png'])):
        with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=4) as archive:
            for name in sorted(selected):
                path=REPO/name
                data=path.read_bytes()
                packaged_name,packaged_data=packaged_file(name,data) if target==full else (name,data)
                archive.writestr(packaged_name,packaged_data,
                                 compress_type=ZIP_STORED if path.suffix.lower()=='.png' else ZIP_DEFLATED)
                if target==full:
                    manifest.append(dict(path=packaged_name,bytes=len(packaged_data),
                                         sha256=hashlib.sha256(packaged_data).hexdigest()))
            if target==full:
                archive.writestr('LoL_AutoCine/Developer_Tools/README_JA.txt',
                    '通常起動は1階層上のSTART.bat、診断収集はCOLLECT_DIAGNOSTICS.batを使います。\n'
                    'このフォルダには音声・GPU・参考動画・旧QAの補助起動ファイルをまとめています。\n'
                    '機能は残してあります。アプリの開発用一括QAは画面内のボタンから実行できます。\n')
            archive.writestr('BUILD_INFO.json',json.dumps(version,indent=2))
            archive.writestr('README_TEST_JA.txt',
                'v5.10.32-testのWindowsテスト版です。新しいフォルダに展開してください。\n'
                '起動: LoL_AutoCine/START.bat\n'
                'テスト順: LoL_AutoCine/docs/QA_CAMERA_WORK_AUTOMATION_20261020_JA.md\n'
                'Python 3.12 x64を自動検出して初回セットアップします。pyは必須ではありません。Native Audio Helper構築フローは既存通りです。\n'
                'このFull版には現在のコードとWork素材を同梱しています。補助BATはDeveloper_Toolsへ整理しました。\n'
                'ミラー映像はOpenCL GPU優先。非対応効果はCPUへ自動復帰します。\n'
                'プレビューの余白埋め拡大は撤去し、16:9の全体表示と元フレーム以上に拡大しない画質を優先します。\n'
                'Workの枠を選ぶと同名テーマの仮エフェクトも選択します。図鑑は6件ずつ、系統・テーマで絞り込めます。\n'
                'ミラーは60 Hz目標で更新し、実際に表示できたfpsを画面とログへ表示します。144 Hzは任意の目標値で、実測値やMP4のFPSとは別です。\n'
                '図鑑はウィンドウ幅と高さに合わせてカード列数・ページ件数・サムネイルを調整します。原本画像は変更しません。\n'
                'ミラーの粒状ノイズはOpenCLで合成します。録画とTk転送は別経路です。\n'
                '652候補・35演出案は仮素材として明示選択できます。正式合格はNo.083 Aのみです。\n')
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
