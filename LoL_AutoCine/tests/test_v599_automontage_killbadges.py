# -*- coding: utf-8 -*-
"""v5.9.9 overlay, preset, camera, montage and opt-in regression tests."""
from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path

import pytest

from core.effects import Template, _effect_events, build_graph
from core.camera import CameraPlan, RigInfo
from core.kill_icons import STYLES, POSITIONS, make_badge, normalize_options, with_badge
from ui.smart_montage import choose_scenes, score
from ui.scene_project import SceneProject, Shot, apply_shot, scene_key
from ui.scene_batch import build_scene_templates, order_scenes


def kill(n=1, t=10.0, multi=1, role="kill"):
    return SimpleNamespace(event_id=n, time=t, killer="Test", victim=f"Enemy{n}",
                           multikill=multi, role=role)


def test_four_visual_styles_are_explicit_and_legacy_off():
    assert set(STYLES) == {"off", "simple", "cinema", "neon", "impact"}
    assert Template().kill_icon_style == "off"
    assert Template().kill_icon_position == "right-top"
    assert len(POSITIONS) == 4


@pytest.mark.parametrize("style", ["simple", "cinema", "neon", "impact"])
def test_badge_is_real_transparent_png(tmp_path, style):
    from PIL import Image
    dest = make_badge(tmp_path / f"{style}.png", style, 2)
    with Image.open(dest) as img:
        assert img.mode == "RGBA" and img.size == (385, 116)
        # Blurred neon/gold glow can leave a barely visible edge pixel.
        assert img.getpixel((0, 0))[3] <= 3
        assert img.getpixel((50, 40))[3] > 0


def test_badge_does_not_mutate_legacy_graph_when_absent():
    src = "testsrc,format=yuv420p[vout]"
    assert with_badge(src, 1, [], duration=6) == src
    assert with_badge(src, 1, [(22, 23)], duration=6) == src
    with pytest.raises(ValueError):
        with_badge("null[xyz]", 1, [(2, 3)], duration=6)


@pytest.mark.parametrize("position", list(POSITIONS))
def test_badge_position_duration_size_and_format(position):
    graph = with_badge("null[vout]", 2, [(4.0, 4.4)], duration=7.0,
                       position=position, scale=1.4, seconds=2.0,
                       opacity=0.7, style="impact")
    assert graph.endswith("[vout]")
    assert "overlay=" in graph and "format=yuv420p[vout]" in graph
    assert "2:v" in graph and "iw*1.400" in graph
    assert "aa=0.700" in graph and "between(t,3.900,6.000)" in graph
    assert "W-w-32" in graph if position.startswith("right") else "x='32" in graph
    assert "H-h-62" in graph if position.endswith("bottom") else "y='62'" in graph


def test_badge_validation_bounds_nonfinite_values():
    assert normalize_options("no", -10, float("nan"), float("inf")) == ("right-top", .5, 1.55, 1.0)
    assert normalize_options("right-bottom", 2, 20, -1) == ("right-bottom", 1.8, 4.0, .25)


def test_events_drive_badges_not_wall_clock():
    tpl = Template(pre=4.0)
    events = _effect_events([kill(1, 35)], tpl, 7.0)
    assert events[0][0] == 4.0
    output = with_badge(build_graph(tpl, 7.0, False, effect_events=events),
                        1, events, duration=7.0)
    assert "between(t,3.900,5.550)" in output


def test_individual_scene_preset_inherits_or_overrides():
    base = Template(kill_icon_style="cinema", kill_icon_scale=1.25)
    inherited = apply_shot(base, Shot())
    assert inherited.kill_icon_style == "cinema"
    assert inherited.kill_icon_scale == 1.25
    forced_off = apply_shot(base, Shot(kill_icon_style="off"))
    assert forced_off.kill_icon_style == "off"
    neon = apply_shot(base, Shot(kill_icon_style="neon"))
    assert neon.kill_icon_style == "neon"
    assert base.kill_icon_style == "cinema"


def test_project_json_roundtrips_style_and_legacy():
    k = kill()
    key = scene_key(k)
    p = SceneProject()
    p.put(key, Shot(kill_icon_style="impact"))
    copy = SceneProject.from_dict(p.to_dict())
    assert copy.shots[key].kill_icon_style == "impact"
    assert SceneProject.from_dict({"schema_version": 3, "application": "LoL AutoCine",
                                    "shots": {key: {"arc": 10}}}).shots[key].kill_icon_style == "inherit"


def test_smart_montage_preserves_short_set_and_paces_climax():
    a = [kill(n=i, t=i * 6, multi=(3 if i==2 else 1)) for i in range(1, 8)]
    result = choose_scenes([(k, None) for k in a])
    assert len(result) == len(a)
    assert result[-1][0].multikill == 3


def test_smart_montage_selects_highlights_and_diversifies_timing():
    a = [kill(n=i, t=i*5, multi=(5 if i==15 else 3 if i%4==0 else 1),
              role="assist" if i%5==0 else "kill") for i in range(20)]
    result = choose_scenes([(k, None) for k in a])
    assert len(result) == 12
    assert a[15] in [p[0] for p in result]
    assert result[-1][0].multikill == 5


def test_manual_sequence_remains_authoritative():
    a, b = kill(n=1), kill(n=2)
    assert order_scenes([a, b], [scene_key(b), scene_key(a)]) == [b, a]


def test_smart_composition_maintains_high_safe_angle():
    rig = RigInfo(mode="fps", h=(0.0, -1.0))
    p = CameraPlan(style="lolnam_cinema", kill_time=10, smart_composition=True,
                   third_elev=18, third_dist=950, rig=rig)
    for t in (7.0, 9.5, 10.0, 10.5, 13.0):
        offset, elev = p.third_pose_at(t)
        assert elev >= 30.99
        assert offset[1] >= 400


def test_slow_motion_and_pulse_align_to_same_kill_timestamp():
    p = CameraPlan(style="lolnam_cinema", kill_time=10, smart_impact=.8)
    assert p.speed_at(10) < p.speed_at(5)
    event = (4.0, 4.4)
    from core.highlight_pulse import pulse_filters
    assert "t-4.000" in " ".join(pulse_filters([event], .8))


def test_easy_controls_create_valid_template():
    import tkinter as tk
    from legacy_app import App
    root = tk.Tk()
    try:
        app = App(root)
        app.var_kill_icon_style.set(STYLES["neon"])
        app.var_kill_icon_position.set(POSITIONS["left-bottom"])
        app.var_kill_icon_scale.set(1.2)
        app.var_kill_icon_duration.set(2.5)
        app.var_kill_icon_opacity.set(.6)
        template = app.current_template()
        assert (template.kill_icon_style, template.kill_icon_position) == ("neon", "left-bottom")
        assert (template.kill_icon_scale, template.kill_icon_duration, template.kill_icon_opacity) == (1.2, 2.5, .6)
        selected = []
        app.on_one_click = lambda smart=False: selected.append(smart)
        app.on_smart_one_click()
        assert selected == [True]
        assert app.current_template().smart_composition
    finally:
        root.destroy()


def test_ffmpeg_can_render_kill_badge_into_real_mp4(tmp_path):
    import shutil
    import subprocess
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        pytest.skip("System ffmpeg is not available")
    badge = make_badge(tmp_path / "badge.png", "neon", 1)
    graph = with_badge("[0:v]format=yuv420p[vout]", 1, [(1.0, 1.4)],
                       duration=2.0, position="right-top", scale=.7)
    dst = tmp_path / "badge_smoke.mp4"
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "lavfi", "-i", "color=c=blue:s=640x360:r=24:d=2",
           "-loop", "1", "-t", "2", "-i", str(badge),
           "-filter_complex", graph, "-map", "[vout]",
           "-c:v", "libx264", "-preset", "ultrafast",
           "-t", "2", "-pix_fmt", "yuv420p", str(dst)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    assert p.returncode == 0, p.stderr[-1600:]
    assert dst.stat().st_size > 1000
    # Ensure the icon actually changed output pixels during the kill window,
    # rather than just producing a video file without compositing.
    def frame(ts):
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", str(ts),
             "-i", str(dst), "-frames:v", "1", "-f", "rawvideo",
             "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        assert result.returncode == 0, result.stderr[-300:]
        return result.stdout
    before = frame(.4)
    decorated = frame(1.2)
    assert len(before) == len(decorated) == 640*360*3
    assert sum(a != b for a, b in zip(before, decorated)) > 400


def test_ui_snapshots_full_roster_as_isolated_plain_data():
    import tkinter as tk
    from legacy_app import App
    from core.players import parse_players
    root = tk.Tk()
    try:
        app = App(root)
        app.players = parse_players([
            {'riotIdGameName': 'One', 'riotIdTagLine': 'JP1',
             'rawChampionName': 'game_character_displayname_LeeSin'},
            {'riotIdGameName': 'Two', 'riotIdTagLine': 'JP2',
             'rawChampionName': 'game_character_displayname_Ahri'}])
        template = app.current_template()
        assert template.kill_icon_players == [p.to_dict() for p in app.players]
        assert template.kill_icon_players[1]['selection_name'] == 'Ahri'
        template.kill_icon_players[0]['name'] = 'Changed'
        app.players.clear()
        assert template.kill_icon_players[1]['name'] == 'Two'
        assert app.current_template().kill_icon_players == []
        from pathlib import Path
        version = (Path(__file__).resolve().parents[1] / 'VERSION.txt').read_text().strip()
        assert 'v' + version in root.title()
    finally:
        root.destroy()
