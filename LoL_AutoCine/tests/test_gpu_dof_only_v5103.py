# -*- coding: utf-8 -*-
"""v5.10.3 removes unwanted circular pixelation, keeping all DOF controls."""
from dataclasses import fields
from pathlib import Path

import numpy as np

from core.effects import Template, VIDEO_EFFECT_LABELS, VIDEO_EFFECT_DEFAULTS, build_graph
from core.focus_fx import circular_dof_filter
from core.preview import grade_rgb


def test_circle_dof_remains_in_template_and_effect_pipeline():
    t = Template(dof_enabled=True, dof_blur=8, dof_center_x=.45,
                 dof_center_y=.51, dof_radius=.25, dof_feather=.10)
    assert all(field in {f.name for f in fields(Template)} for field in
               ('dof_enabled', 'dof_shape', 'dof_blur', 'dof_center_x',
                'dof_center_y', 'dof_radius', 'dof_feather'))
    assert t.dof_shape == 'circle'
    assert 'cdofalpha' in build_graph(t, 1, False)
    assert 'maskedmerge' in circular_dof_filter(t)


def test_retired_mosaic_not_in_ui_or_defaults():
    assert 'center_mosaic' not in VIDEO_EFFECT_DEFAULTS
    assert 'center_mosaic' not in VIDEO_EFFECT_LABELS


def test_old_templates_with_mosaic_are_silently_migrated():
    older = Template(video_effects={'center_mosaic': .75, 'vignette_fx': .3})
    assert older.video_effects == {'vignette_fx': .3}
    assert older.to_dict()['video_effects'] == {'vignette_fx': .3}
    # Old in-memory project settings can't put retired effect back into exports.
    older.video_effects['center_mosaic'] = .9
    assert 'center_mosaic' not in older.to_dict()['video_effects']
    assert 'pixelize' not in build_graph(older, 1, False)
    assert 'cmosa' not in build_graph(older, 1, False)


def test_template_migration_does_not_mutate_caller_settings():
    data = {'center_mosaic': .75, 'flash': .3}
    template = Template(video_effects=data)
    assert data == {'center_mosaic': .75, 'flash': .3}
    assert template.video_effects == {'flash': .3}


def test_all_v5101_template_positions_are_preserved():
    original = Template(encoder_policy='cpu', kill_icon_players=[{'name': 'One'}],
                        kill_frame_color='#22AA44', kill_mark_style='swords')
    added = {'dof_shape', 'dof_center_x', 'dof_center_y', 'dof_radius', 'dof_feather'}
    restored = Template(*(getattr(original, f.name) for f in fields(Template) if f.name not in added))
    assert restored.encoder_policy == 'cpu'
    assert restored.kill_icon_players == original.kill_icon_players
    assert restored.kill_frame_color == '#22AA44' and restored.kill_mark_style == 'swords'


def test_old_mosaic_does_not_change_lightweight_preview():
    a = np.random.default_rng(7).integers(0, 256, (80, 144, 3), dtype=np.uint8)
    original = Template(grade='standard', grade_strength=0, bloom=0,
                        grain=0, vignette=0)
    legacy = Template(**{**original.to_dict(),
                         'video_effects': {'center_mosaic': .9}})
    assert np.array_equal(grade_rgb(a, original), grade_rgb(a, legacy))


def test_program_source_has_no_active_mosaic_renderers():
    root = Path(__file__).resolve().parents[1]
    for relative in ('core/preview.py', 'core/focus_fx.py'):
        s = (root / relative).read_text(encoding='utf-8')
        assert 'center_mosaic' not in s, relative
