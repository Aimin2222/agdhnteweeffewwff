# -*- coding: utf-8 -*-
"""Champion-portrait kill feed regression: authentic pair mapping and time-specific overlays."""
from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess

import pytest
from PIL import Image
from core.kill_icons import (make_badge, make_event_badges, with_badges, champion_icon,
                             _player_for_name, _icon_id, STYLES)
from core.effects import Template


def roster():
    return [
        {'name':'Aimin', 'summoner':'Aimin#カワウソ','riot_id':'Aimin#カワウソ', 'selection_name':'LeeSin'},
        {'name':'Enemy', 'summoner':'Enemy#JP1','riot_id':'Enemy#JP1', 'selection_name':'Ahri'},
        {'name':'Another', 'summoner':'Another#JP1','riot_id':'Another#JP1', 'selection_name':'Yasuo'},
    ]


def demo_icons(tmp):
    for name,color in [('LeeSin',(220,40,40)), ('Ahri',(30,80,235)), ('Yasuo',(40,230,60))]:
        Image.new('RGB',(128,128),color).save(tmp / (name+'.png'))
    return {name:tmp/(name+'.png') for name in ('LeeSin','Ahri','Yasuo')}


def test_template_keeps_roster_for_each_scene():
    t=Template(kill_icon_style='cinema',kill_icon_players=roster())
    from ui.scene_project import Shot,apply_shot
    after=apply_shot(t,Shot())
    assert after.kill_icon_players==roster()
    assert t.kill_icon_players==roster()


def test_exact_event_champion_mapping_and_no_guess():
    assert _player_for_name('Aimin',roster())['selection_name']=='LeeSin'
    assert _player_for_name('Enemy#JP1',roster())['selection_name']=='Ahri'
    assert _player_for_name('NotThisPlayer',roster()) is None
    assert _icon_id(roster()[0])=='LeeSin'
    assert _icon_id({'selection_name':'../../invalid.png'}) is None
    assert _icon_id({'selection_name':'Wukong'})=='MonkeyKing'


def test_local_icons_resolved_without_network(tmp_path):
    icons=demo_icons(tmp_path)
    for p in roster():
        assert champion_icon(p,cache_dir=tmp_path,download=False)==icons[p['selection_name']]


@pytest.mark.parametrize('style',['simple','cinema','neon','impact'])
def test_real_portraits_in_all_templates(tmp_path,style):
    icons=demo_icons(tmp_path)
    p=make_badge(tmp_path/(style+'.png'),style,99,killer_icon=icons['LeeSin'],victim_icon=icons['Ahri'])
    with Image.open(p) as im:
        assert im.mode=='RGBA'
        assert im.size==(385,116)
        # Actual portrait colors in left and right slots: no title, count or placeholder.
        assert im.getpixel((77,55))[:3]==(220,40,40)
        assert im.getpixel((306,55))[:3]==(30,80,235)
        assert im.getpixel((192,58))[3]>0  # slash / clash art


def test_each_kill_uses_real_different_victim(tmp_path):
    icons=demo_icons(tmp_path)
    lookup=lambda p:icons[p['selection_name']]
    kills=[SimpleNamespace(killer='Aimin',victim='Enemy'),SimpleNamespace(killer='Aimin',victim='Another')]
    entries=make_event_badges(tmp_path/'scene.mp4','neon',kills,[(.7,1), (1.7,2)],roster(),icon_lookup=lookup)
    assert len(entries)==2
    assert [e[1] for e in entries]==[.7,1.7]
    a,b=[Image.open(e[0]) for e in entries]
    try:
        assert a.getpixel((306,55))[:3]==(30,80,235)
        assert b.getpixel((306,55))[:3]==(40,230,60)
    finally:
        a.close();b.close()


def test_missing_players_or_icons_omit_instead_of_faking(tmp_path):
    events=[(.8,1.1)]
    k=[SimpleNamespace(killer='Aimin',victim='Ghost')]
    assert make_event_badges(tmp_path/'out.mp4','simple',k,events,roster(),icon_lookup=lambda p:None)==[]
    k[0].victim='Enemy'
    assert make_event_badges(tmp_path/'out.mp4','simple',k,events,roster(),icon_lookup=lambda p:None)==[]


def test_time_specific_pair_overlays_encode_to_mp4(tmp_path):
    ff=shutil.which('ffmpeg')
    if not ff:pytest.skip('no ffmpeg')
    icons=demo_icons(tmp_path)
    k=[SimpleNamespace(killer='Aimin',victim='Enemy'),SimpleNamespace(killer='Aimin',victim='Another')]
    entries=make_event_badges(tmp_path/'scene.mp4','simple',k,[(.65,1),(1.7,2)],roster(),icon_lookup=lambda p:icons[p['selection_name']])
    graph=with_badges('[0:v]format=yuv420p[vout]',1,entries,duration=2.5,scale=.65,seconds=.65)
    cmd=[ff,'-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=black:s=640x360:r=24:d=2.5']
    for p,_ in entries:
        cmd+=['-loop','1','-t','2.5','-i',str(p)]
    dst=tmp_path/'out.mp4'
    cmd+=['-filter_complex',graph,'-map','[vout]','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-t','2.5',str(dst)]
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=50)
    assert run.returncode==0,run.stderr[-1400:]
    assert dst.stat().st_size>1500
    def frame(ts):
        result=subprocess.run([ff,'-hide_banner','-loglevel','error','-ss',str(ts),'-i',str(dst),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,timeout=20)
        assert result.returncode==0
        return result.stdout
    empty,redgreen,after=frame(.2),frame(.9),frame(1.95)
    assert sum(a!=b for a,b in zip(empty,redgreen))>1000
    assert sum(a!=b for a,b in zip(redgreen,after))>1000


def test_nearly_simultaneous_kills_do_not_break_filter_graph():
    entries=[(Path("first.png"),1.001),(Path("next.png"),1.005)]
    g=with_badges("null[vout]",1,entries,duration=2,seconds=1.0)
    assert g.endswith("[vout]")
    assert "[pair_src_0]" in g
    assert "[2:v]" in g
