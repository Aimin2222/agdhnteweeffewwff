from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
import pytest

from core.effects import Template
from core.kill_icons import MOTION_STYLES
from ui.director_work_controls import apply, restore, values, MODE_LABELS, mirror_event_rows, composite_mirror, select_frame_with_effect


class Variable:
    def __init__(self, value): self.value = value
    def get(self): return self.value
    def set(self, value): self.value = value


def application():
    return SimpleNamespace(var_camera_control_mode=Variable(MODE_LABELS[None]),
        var_work_frame=Variable(''), var_work_effect=Variable(''),
        var_work_review=Variable(False), var_work_strength=Variable('strong'),
        camera_auto_excluded=[], camera_auto_qa_approved={})


def test_existing_settings_keep_legacy_camera_and_badges():
    app = application()
    restore(app, {'out_root': 'previous'})
    template = apply(app, Template())
    assert template.camera_control_mode is None
    assert template.work_kill_frame_id == template.work_kill_effect_id == ''
    assert not template.work_kill_review
    assert template.camera_auto_qa_approved == {}


def test_frame_selection_pairs_only_the_same_theme_effect_and_preserves_quality_state():
    app = application()
    effect = select_frame_with_effect(app, '001/elderwood_weak')
    assert effect['id'] == 'D_elderwood'
    assert (app.var_work_frame.get(), app.var_work_effect.get()) == ('001/elderwood_weak', 'D_elderwood')
    assert app.var_work_review.get()  # Neither asset has passed source comparison.
    assert app.var_work_strength.get() == 'weak'
    effect = select_frame_with_effect(app, '083/a_simple_main')
    assert effect['id'] == 'A'
    assert app.var_work_review.get()  # The approved frame's paired effect is still a draft.
    select_frame_with_effect(app, '001/elderwood_weak')
    effect = select_frame_with_effect(app, '003/project_variant_1')
    assert effect['id'] == 'D_project'
    # A theme without a matching effect must not retain the old skin's effect.
    from core.work_kill_assets import list_assets
    unmatched = next(row['id'] for row in list_assets('frames', review=True)
                     if row.get('theme') == 'demacia')
    assert select_frame_with_effect(app, unmatched) is None
    assert app.var_work_effect.get() == ''


@pytest.mark.parametrize('mode', ('manual', 'fixed_auto', 'full_auto'))
def test_settings_template_roundtrip(mode):
    app = application()
    data = dict(camera_control_mode=mode, camera_auto_qa_approved={'BLUE':['third'], 'RED':['cinema_top']},
                camera_auto_excluded=['RED:fps'], work_kill_frame_id='083/a_simple_main',
                work_kill_effect_id='A', work_kill_review=True, work_kill_strength='weak')
    restore(app, data)
    assert values(app) == data
    template = apply(app, Template())
    assert {k: template.to_dict()[k] for k in data} == data


def test_feed_slots_stay_stable_and_match_export_boundaries():
    kills = [dict(time=t) for t in (1., 1.2, 1.4, 1.6)]
    assert mirror_event_rows(kills, .99, 1.55) == []
    assert mirror_event_rows(kills, 1., 1.55) == [(kills[0], 0)]
    assert mirror_event_rows(kills, 1.3, 1.55) == [(kills[0], 0), (kills[1], 1)]
    assert mirror_event_rows(kills, 1.61, 1.55) == [(kills[1], 1), (kills[2], 2), (kills[3], 0)]
    assert mirror_event_rows(kills, 4., 1.55) == []


@pytest.mark.parametrize('motion', MOTION_STYLES)
def test_mirror_event_uses_replay_clock_and_cached_real_icons(tmp_path, motion):
    icons = []
    for n, color in enumerate(('blue', 'red')):
        path = tmp_path/f'{n}.png'
        Image.new('RGBA',(64,64),color).save(path)
        icons.append(path)
    template = Template(work_kill_frame_id='083/a_simple_main', kill_icon_motion=motion)
    api = SimpleNamespace(playback=lambda: {'time': 12.4})
    kills = [dict(time=12., killer='A', victim='B')]
    roster = [dict(name='A', selection_name='Ashe'), dict(name='B', selection_name='Lux')]
    image = Image.new('RGB',(960,540),'gray')
    with patch('core.kill_icons.champion_icon', side_effect=icons) as resolve:
        result = composite_mirror(image, template, (api, kills, roster))
    assert result.tobytes() != image.tobytes()
    assert all(call.kwargs == {'download':False} for call in resolve.call_args_list)
    api.playback = lambda: {'time': 11.99}
    assert composite_mirror(image, template, (api,kills,roster)).tobytes() == image.tobytes()


def test_missing_replay_or_icons_does_not_fabricate_portraits():
    image=Image.new('RGB',(320,180),'gray')
    template=Template(work_kill_frame_id='083/a_simple_main')
    api=SimpleNamespace(playback=lambda: {'time': 1.1})
    assert composite_mirror(image,template,(api,[dict(time=1.,killer='A',victim='B')],[])).tobytes()==image.tobytes()
