# -*- coding: utf-8 -*-
"""Non-destructive offline/online diagnostics. Does not record or move LoL's camera.

A replay application cannot verify shot framing visually without game footage and a
human or validated target oracle. We explicitly distinguish such live checks.
"""
from __future__ import annotations
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def run_checks(root, *, report_file=None, api=None):
    from PIL import Image
    from .camera import CameraPlan, RigInfo, side_yaw_for
    from .effects import Template, GRADE_JP
    from .kill_icons import ASSET_STYLES, STYLES, make_badge
    root = Path(root)
    outcomes=[]

    def check(label, action, *, optional=False):
        try:
            evidence = action()
            if evidence is False:
                raise RuntimeError('期待した結果を確認できませんでした')
            outcomes.append(dict(name=label, status='pass', info=str(evidence or 'OK')[:260]))
        except Exception as e:
            outcomes.append(dict(name=label, status='warn' if optional else 'fail',
                                 info=f'{type(e).__name__}: {e}'[:340]))

    def all_png():
        invalid=[]
        for code,filename in ASSET_STYLES.items():
            path=root/'assets'/'kill_badges'/filename
            with Image.open(path) as image:
                if image.size[0] < 300 or image.size[1] < 100 or image.mode != 'RGBA':
                    invalid.append(code)
        if invalid: raise ValueError('不正なPNG: '+','.join(invalid))
        return f'{len(ASSET_STYLES)}種類の透過PNGを確認'

    check('キルフレーム素材の存在・透過',all_png)
    def composites():
        with tempfile.TemporaryDirectory(prefix='autocine_selftest_') as temp:
            icon=Path(temp)/'portrait.png'
            Image.new('RGB',(96,96),(70,130,220)).save(icon)
            for code in ASSET_STYLES:
                result=Path(temp)/(code+'.png')
                make_badge(result,code,killer_icon=icon,victim_icon=icon)
                with Image.open(result) as png:
                    assert png.mode=='RGBA' and png.size==(385,116),code
        return f'{len(ASSET_STYLES)}スタイルを385×116で合成'

    check('すべてのキル素材にキャラ肖像を合成',composites)
    def camera_math():
        import math
        rig=RigInfo(mode='fps',third=True,h=(0,-1),pitch_axis='x',pitch_sign=-1,
                    rot={'x':-32,'y':0,'z':0})
        blue=CameraPlan(style='third',rig=rig,side_yaw=side_yaw_for('ORDER'))
        red=CameraPlan(style='third',rig=rig,side_yaw=side_yaw_for('CHAOS'))
        a,b=blue.offset_at(0),red.offset_at(0)
        assert abs(a[0]+b[0])<1e-4 and abs(a[2]+b[2])<1e-4
        assert abs(a[1]-b[1])<1e-4 and a[1]>250
        return 'ブルー/レッドの追従位置180°対称を検証（数学テスト）'
    check('サイド別カメラの計算',camera_math)

    check('テンプレートカラー定義',lambda: f'{len(GRADE_JP)}グレードを確認' if 'default' in GRADE_JP else False)
    check('カメラ・音声・GPU関連モジュール',lambda: all(
        __import__(n) for n in ('core.camera','core.jobs','core.audio','core.gpu_full','core.scanner')))

    def ffmpeg():
        from .effects import FFMPEG
        exe = str(FFMPEG)
        result=subprocess.run([exe,'-version'],capture_output=True,text=True,timeout=10)
        assert result.returncode==0
        return result.stdout.splitlines()[0][:100]
    check('FFmpeg実行',ffmpeg)

    def ffmpeg_gpu():
        from .effects import FFMPEG
        exe = str(FFMPEG)
        result=subprocess.run([exe,'-encoders'],capture_output=True,text=True,timeout=10)
        if 'h264_nvenc' not in result.stdout:
            raise RuntimeError('このFFmpegではNVENCが列挙されません')
        return 'h264_nvencの存在を確認。GPU実機稼働は別途要検証'
    check('NVENCエンコーダ定義',ffmpeg_gpu,optional=True)

    def writable():
        with tempfile.TemporaryDirectory(prefix='autocine_write_',dir=root) as d:
            p=Path(d)/'test';p.write_text('ok','utf-8');assert p.read_text('utf-8')=='ok'
        return 'アプリフォルダの一時書込みOK'
    check('出力先の書込権限',writable)

    def preview_libs():
        import numpy
        from PIL import ImageTk
        from ui.template_gallery import render_scene_comparison
        test_image=Image.new('RGB',(360,202),(76,81,114))
        output=render_scene_comparison(test_image,Template(grade='default'),200,113)
        assert output.size==(403,113)
        return '比較サムネイル生成可能'
    check('実シーン比較エンジン',preview_libs)

    if api is not None:
        def live_api():
            playback=api.playback()
            assert isinstance(playback,dict)
            return f'LoL Replay API応答OK, time={playback.get("time", "unknown")}s'
        check('LoL Replay APIへの読取り接続',live_api,optional=True)
        def events_readonly():
            snapshot=api.events()
            if isinstance(snapshot, dict):
                snapshot=snapshot.get('Events',snapshot.get('events',[]))
            if not isinstance(snapshot,list):
                raise ValueError('Replay APIからイベント一覧を取得できません')
            killed=[e for e in snapshot if str(e.get('EventName','')).lower() == 'championkill']
            assists=sum(bool(e.get('Assisters')) for e in killed)
            return f'イベント{len(snapshot)}件 / ChampionKill {len(killed)}件 / アシスト参加の記録 {assists}件'
        check('LoLイベント一覧の読取り（ゲームを動かさない）',events_readonly,optional=True)

    version = (root/'VERSION.txt').read_text(encoding='utf-8').strip()
    result=dict(version=version, timestamp=datetime.datetime.now().astimezone().isoformat(),
                passed=sum(x['status']=='pass' for x in outcomes),
                warnings=sum(x['status']=='warn' for x in outcomes),
                failed=sum(x['status']=='fail' for x in outcomes),
                checks=outcomes,
                notes=['自動テストはローカル環境の安全な検査です。LoLの3D構図/ゲーム音の品質まで自動判定しません。',
                       'GPUエンコーダの表示は実GPUを使ったエンコードの成功を保証しません。',
                       'LoLの自動操作・リプレイ移動・録画・設定変更は行いません。'])
    if report_file:
        target=Path(report_file)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def main():
    result=run_checks(Path(__file__).resolve().parent.parent,
                      report_file=Path(__file__).resolve().parent.parent/'diagnostics'/'selftest_latest.json')
    for item in result['checks']:
        print(f"[{item['status'].upper()}] {item['name']} — {item['info']}")
    print('結果:',result['passed'],'成功',result['warnings'],'注意',result['failed'],'失敗')
    return 1 if result['failed'] else 0


if __name__=='__main__':
    sys.exit(main())
