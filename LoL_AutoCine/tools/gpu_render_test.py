"""Batch actual recorded footage through GPU/CPU paths without replay recapture.

Results remain local (may contain source paths). Audio/camera/LoL-only capture
must additionally be checked in the real application; this is a pixel test.
"""
from pathlib import Path
import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main(stage=lambda _name: None):
    parser=argparse.ArgumentParser(description='同じ録画でGPU/CPU映像加工をまとめて比較')
    parser.add_argument('source',nargs='?',help='録画済みraw MP4。省略するとファイル選択')
    parser.add_argument('--seconds',type=float,default=6)
    args=parser.parse_args()
    source=args.source
    if not source:
        stage('selecting_source')
        print('録画済みraw MP4を選択してください。キャンセルすると加工せず終了します。', flush=True)
        import tkinter as tk
        from tkinter import filedialog
        root=tk.Tk();root.withdraw()
        try:
            source=filedialog.askopenfilename(title='比較する同じraw MP4を選択',filetypes=[('MP4','*.mp4')])
        finally:root.destroy()
    if not source:
        stage('cancelled')
        print('ファイル選択をキャンセルしました。', flush=True)
        return 2
    source=Path(source).resolve()
    if not source.is_file(): parser.error('MP4が見つかりません')
    if not 0<args.seconds<=30: parser.error('--seconds は0より大きく30以下')
    stage('loading_engine')
    print('GPU比較テストを準備しています…', flush=True)
    from core.effects import Template,apply_effects,FFMPEG
    from core.gpu_pipeline import detect
    from core.montage_fx import get_duration
    duration=min(args.seconds,get_duration(source,ffmpeg=FFMPEG))
    folder=ROOT/'output'/'gpu_render_tests'/dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True)
    base=dict(fps=60,game_audio=False,kill_icon_style='off',encoder_policy='gpu')
    clean=dict(grade='standard',grade_strength=0,vignette=0,grain=0,bloom=0,transition='cut')
    standard=dict(grade='sunset',grade_strength=.8,temperature=.3,vibrance=.52,
                  dof_enabled=True,dof_blur=5,bloom=.25,vignette=.4,grain=.15,
                  video_effects={'sphere_blur':.18,'vignette_fx':.3})
    cases=[('01_clean_gpu','full',clean),('02_standard_gpu','full',standard),
           ('03_standard_cpu','cpu',standard),
           ('04_curve_title_band_gpu','full',standard|dict(curve_enabled=True,dof_shape='band',title_text='GPU TEST 日本語',bars=.06)),
           ('05_temporal_transform_gpu','full',clean|dict(video_effects={'radial_blur':.3,'zoom_blur':.2,'camera_shake':.1,'mirror':1,'chroma_leak':.2,'flash':.2})),
           ('06_fog_grain_glint_gpu','full',clean|dict(fog_enabled=True,fog_strength=.3,grain=.35,bpm=120,highlight_pulse=.5,video_effects={'glint':.2,'glitch':.1,'vr_light_leak':.2}))]
    old_mode=os.environ.get('AUTOCINE_GPU_EFFECTS')
    result={'source':str(source),'duration_s':duration,'output_fps':60,'audio_tested':False,
            'camera_tested':False,'physical_gpu_verified_by_user':False,'cases':[]}
    events=[(duration/2,min(duration,duration/2+.42))]
    stage('running_cases')
    try:
        for name,mode,options in cases:
            print(f'[{name}] {mode} / {duration:.2f}s / 60fps',flush=True)
            os.environ['AUTOCINE_GPU_EFFECTS']=mode
            detect.cache_clear()
            started=time.monotonic();status='success';error=None
            try:
                apply_effects(source,folder/(name+'.mp4'),Template(**(base|options)),duration,[],effect_events=events)
            except Exception as exc:
                status='failed';error=str(exc)[-1500:]
            records=[]
            for p in sorted((ROOT/'diagnostics'/'performance').glob('render_*.json')):
                data=json.loads(p.read_text(encoding='utf-8'))
                if data.get('output')==str(folder/(name+'.mp4')): records.append(data)
            result['cases'].append({'name':name,'requested_mode':mode,'status':status,'error':error,
                                    'wall_time_s':round(time.monotonic()-started,3),
                                    'gpu_effects_confirmed':bool(records and records[-1].get('gpu_effects_confirmed') and records[-1].get('pipeline',{}).get('full_gpu_pipeline')),
                                    'actual_encoder':records[-1].get('encoder') if records else None,
                                    'renders':records})
            (folder/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            (ROOT/'diagnostics'/('gpu_batch_'+folder.name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            confirmed=result['cases'][-1]['gpu_effects_confirmed']
            print(f'  {status} / {result["cases"][-1]["wall_time_s"]}s / effects={"GPU confirmed" if confirmed else "CPU/hybrid fallback"}',flush=True)
    finally:
        if old_mode is None: os.environ.pop('AUTOCINE_GPU_EFFECTS',None)
        else: os.environ['AUTOCINE_GPU_EFFECTS']=old_mode
        detect.cache_clear()
    print(f'結果: {folder}\n映像を確認後 COLLECT_DIAGNOSTICS.bat で診断ZIPを作成してください。',flush=True)
    return int(any(c['status']!='success' for c in result['cases']))


class _Tee:
    def __init__(self, console, log):
        self.console, self.log = console, log

    def write(self, text):
        self.log.write(text)
        self.log.flush()
        if self.console is not None:
            self.console.write(text)
        return len(text)

    def flush(self):
        self.log.flush()
        if self.console is not None:
            self.console.flush()


def entrypoint(runner=None):
    """Record startup before importing engine dependencies or opening Tk."""
    folder = ROOT / 'diagnostics'
    folder.mkdir(parents=True, exist_ok=True)
    name = 'gpu_test_startup_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    record_path, log_path = folder / (name+'.json'), folder / (name+'.log')
    record = {'python': sys.executable, 'python_version': sys.version,
              'app_version': (ROOT/'VERSION.txt').read_text(encoding='utf-8').strip(),
              'status': 'starting', 'exit_code': None}
    def stage(status):
        record['status'] = status
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    stage('starting')
    with log_path.open('w', encoding='utf-8') as log:
        with redirect_stdout(_Tee(sys.stdout, log)), redirect_stderr(_Tee(sys.stderr, log)):
            print('GPUテストの起動ログ: '+str(log_path), flush=True)
            try:
                code = (runner or main)(stage) or 0
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                if exc.code is not None and not isinstance(exc.code, int):
                    print(str(exc.code), file=sys.stderr, flush=True)
            except Exception:
                traceback.print_exc()
                code = 1
            except KeyboardInterrupt:
                print('GPUテストを中断しました。', flush=True)
                code = 130
            record['exit_code'] = code
            stage('completed' if code == 0 else ('cancelled' if record['status']=='cancelled' else 'failed'))
            print(f'終了コード: {code} / 診断ログを保存しました。', flush=True)
    return code


if __name__=='__main__': raise SystemExit(entrypoint())
