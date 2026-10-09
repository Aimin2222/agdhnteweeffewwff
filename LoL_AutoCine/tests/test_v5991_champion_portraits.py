# -*- coding: utf-8 -*-
"""Offline tests for text-free original champion × champion kill-feed decorations."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image
from core.players import Player
from core import champion_portraits as cp
from core.kill_icons import make_champion_badge, with_portrait_badges


def player(name, champion, slot=0):
    return Player(slot, name, name+"#JP1", name, champion, "ORDER")


def make_icon(path, color):
    Image.new("RGBA", (120, 120), color).save(path)
    return path


def test_event_alias_mapping_has_no_killer_victim_confusion():
    roster = [player("BlueUser", "Ahri"), player("RedUser", "Yasuo", 1)]
    assert cp.identify_champion("BlueUser", roster) == "Ahri"
    assert cp.identify_champion("RedUser#JP1", roster) == "Yasuo"
    assert cp.identify_champion("Ahri", roster) == "Ahri"
    # Unknown summoner cannot be guessed to be a champion.
    assert cp.identify_champion("DefinitelyUnknownPlayer", roster) == "DefinitelyUnknownPlayer"


def test_data_dragon_manifest_and_portrait_cache_offline(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "_MEM_MANIFEST", None)
    monkeypatch.setattr(cp, "_MEM_VERSION", None)
    manifest = {"data":{"Ahri":{"id":"Ahri","name":"Ahri","key":"103"},
                        "Yasuo":{"id":"Yasuo","name":"Yasuo","key":"157"}}}
    data = {}
    for champion in ("Ahri", "Yasuo"):
        buf = BytesIO()
        Image.new("RGBA", (120, 120), "purple").save(buf, format="PNG")
        data[f"/{champion}.png"] = buf.getvalue()
    calls=[]
    def fake_fetch(url, timeout=4):
        calls.append(url)
        if url.endswith("/versions.json"):
            return b'["16.20.1"]'
        if url.endswith("/champion.json"):
            import json
            return json.dumps(manifest).encode()
        for suffix, raw in data.items():
            if url.endswith(suffix):
                return raw
        raise ValueError(url)
    monkeypatch.setattr(cp, "_fetch", fake_fetch)
    roster = [player("BlueUser", "Ahri"), player("RedUser", "Yasuo", 1)]
    a = cp.portrait_for_event("BlueUser", roster, tmp_path)
    b = cp.portrait_for_event("RedUser", roster, tmp_path)
    assert a and b and a.is_file() and b.is_file() and a != b
    assert a.name == "Ahri.png" and b.name == "Yasuo.png"
    before=len(calls)
    assert cp.portrait_for_event("BlueUser", roster, tmp_path) == a
    assert len(calls) == before, "Cached icons must be reused"


@pytest.mark.parametrize("style", ["simple", "cinema", "neon", "impact"])
def test_badge_only_has_two_real_portraits_and_no_text(tmp_path, monkeypatch, style):
    left = make_icon(tmp_path/"Ahri.png", (218, 40, 70, 255))
    right = make_icon(tmp_path/"Yasuo.png", (40, 84, 220, 255))
    from PIL import ImageDraw
    def forbidden_text(*args, **kwargs):
        raise AssertionError("Decorations must not draw KILL, x1, or any other text")
    monkeypatch.setattr(ImageDraw.ImageDraw, "text", forbidden_text)
    result = make_champion_badge(tmp_path / "badge.png", left, right, style)
    with Image.open(result) as im:
        assert im.size == (260, 112) and im.mode == "RGBA"
        assert im.getpixel((47, 54))[0] > 180   # left (Ahri)
        assert im.getpixel((200, 54))[2] > 180  # right (Yasuo)


def test_two_events_make_distinct_overlay_inputs_and_kill_times():
    graph = with_portrait_badges("[0:v]format=yuv420p[vout]", [(1, 1.5), (2, 2.1)],
                                 duration=5, scale=1.0, seconds=1.55, style="simple")
    assert graph.endswith("[vout]")
    assert "[1:v]" in graph and "[2:v]" in graph
    assert "between(t,1.400,3.050)" in graph
    assert "between(t,2.000,3.650)" in graph
    assert "62+115" in graph  # Nearby kills are displayed on separate rows
    assert "KILL" not in graph and "x1" not in graph


def test_badge_not_rendered_without_known_events():
    s="[0:v]format=yuv420p[vout]"
    assert with_portrait_badges(s, [], duration=7) == s
    assert with_portrait_badges(s, [(1, 50)], duration=7) == s


def test_actual_ffmpeg_two_kill_icons_uses_real_video_pipeline(tmp_path):
    import shutil
    import subprocess
    exe = shutil.which("ffmpeg")
    if not exe:
        pytest.skip("System FFmpeg unavailable")
    paths=[]
    for n,(lc,rc) in enumerate([("red","blue"),("green","yellow")]):
        lp=make_icon(tmp_path/f"left{n}.png",lc)
        rp=make_icon(tmp_path/f"right{n}.png",rc)
        paths.append(make_champion_badge(tmp_path/f"badge{n}.png",lp,rp,"cinema"))
    graph=with_portrait_badges("[0:v]format=yuv420p[vout]",[(1,1.0),(2,2.3)],
                               duration=4.0,position="right-top")
    dst=tmp_path/"pair_overlay.mp4"
    args=[exe,"-y","-hide_banner","-loglevel","error",
          "-f","lavfi","-i","color=c=black:s=640x360:r=24:d=4",
          "-loop","1","-t","4","-i",str(paths[0]),
          "-loop","1","-t","4","-i",str(paths[1]),
          "-filter_complex",graph,"-map","[vout]","-c:v","libx264","-preset","ultrafast",
          "-t","4",str(dst)]
    p=subprocess.run(args,capture_output=True,text=True,timeout=75)
    assert p.returncode==0,p.stderr[-1200:]
    assert dst.stat().st_size > 1024
