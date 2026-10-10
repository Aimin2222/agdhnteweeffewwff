"""Keep the reviewed event clock, roster identity and failure behavior intact."""
from dataclasses import fields
from types import SimpleNamespace

from PIL import Image

from core.effects import Template
from core.kill_icons import _player_for_name, _icon_id, make_event_badges, with_badges


def test_previous_template_positions_and_roster_isolation():
    old = Template(smart_composition=True, kill_icon_style='neon')
    appended={'kill_icon_players','encoder_policy','kill_frame_color','kill_glow_color',
              'kill_glow_enabled','kill_glow_strength','kill_frame_width','kill_mark_style'}
    values = [getattr(old, f.name) for f in fields(Template) if f.name not in appended | {'dof_shape', 'dof_center_x', 'dof_center_y', 'dof_radius', 'dof_feather', 'camera_side'}]
    copy = Template(*values)
    assert copy.smart_composition and copy.kill_icon_style == 'neon'
    copy.kill_icon_players.append({'name': 'Test'})
    assert old.kill_icon_players == Template().kill_icon_players == []


def test_tagged_names_are_exact_and_ambiguous_bare_names_are_omitted():
    roster = [{'name': 'Same', 'riot_id': 'Same#JP1', 'selection_name': 'Ahri'},
              {'name': 'Same', 'riot_id': 'Same#JP2', 'selection_name': 'Yasuo'}]
    assert _player_for_name('Same#JP2', roster) is roster[1]
    assert _player_for_name('Same', roster) is None
    assert _player_for_name('Ahri', roster) is None
    assert _icon_id({'selection_name': 'FiddleSticks'}) == 'Fiddlesticks'
    assert _icon_id({'selection_name': 'Fiddlesticks'}) == 'Fiddlesticks'


def test_unavailable_icons_are_looked_up_once_per_clip(tmp_path):
    calls = []
    roster = [{'name': 'A', 'selection_name': 'Ahri'},
              {'name': 'B', 'selection_name': 'Yasuo'}]
    kills = [SimpleNamespace(killer='A', victim='B')]*3
    entries = make_event_badges(tmp_path/'out.mp4', 'simple', kills,
                               [(1, 1.4), (2, 2.4), (3, 3.4)], roster,
                               icon_lookup=lambda p: calls.append(p['selection_name']))
    assert entries == []
    assert calls == ['Ahri', 'Yasuo']


def test_wrong_event_count_omits_pairs_without_icon_requests(tmp_path):
    def unexpected(_):
        raise AssertionError('No reliable event-to-kill mapping')
    assert make_event_badges(tmp_path/'out.mp4', 'simple',
                             [SimpleNamespace(killer='A', victim='B')], [], [],
                             icon_lookup=unexpected) == []


def test_simultaneous_kills_keep_both_actual_pairs_on_separate_rows():
    graph = with_badges('null[vout]', 1, [('a.png', 1), ('b.png', 1)], duration=3)
    assert '[2:v]' in graph and '[1:v]' in graph
    assert "y='62+0'" in graph and "y='62+120'" in graph
    assert graph.count("between(t,0.900,2.550)") == 2
    assert 'shortest=0:eof_action=repeat' in graph
    assert graph.count('overlay=') == 2


def test_download_uses_verified_cache_offline(monkeypatch, tmp_path):
    import io
    import urllib.request
    from core.kill_icons import champion_icon
    png = io.BytesIO()
    Image.new('RGB', (128,128), (80,100,220)).save(png, 'PNG')
    urls = []
    def response(request, timeout):
        url = getattr(request, 'full_url', request)
        urls.append(url)
        return io.BytesIO(b'["16.20.1"]' if url.endswith('versions.json') else png.getvalue())
    monkeypatch.setattr(urllib.request, 'urlopen', response)
    player = {'selection_name': 'ChampionPairTest'}
    icon = champion_icon(player, cache_dir=tmp_path)
    assert icon and Image.open(icon).size == (128,128)
    assert urls == ['https://ddragon.leagueoflegends.com/api/versions.json',
                    'https://ddragon.leagueoflegends.com/cdn/16.20.1/img/champion/ChampionPairTest.png']
    def unexpected(*args, **kwargs):
        raise AssertionError('Cached PNG must work offline')
    monkeypatch.setattr(urllib.request, 'urlopen', unexpected)
    assert champion_icon(player, cache_dir=tmp_path, download=False) == icon
