"""UI-owned circular focus controls and preset explanations."""
import pytest
from ui.studio_localization import TEMPLATE_HELP_JA, EFFECT_HELP_JA

@pytest.fixture
def gui(monkeypatch,tmp_path):
    import tkinter as tk
    import legacy_app
    monkeypatch.setattr(legacy_app,'SETTINGS',tmp_path/'settings.json')
    root=tk.Tk();root.geometry('1450x900')
    app=legacy_app.App(root);root.update()
    yield app,root
    root.destroy()


def test_gui_focus_controls_and_preset(gui):
    app,root=gui
    assert app.var_dof_shape.get()=='円形（おすすめ）'
    assert not app._legacy_dof_panel.winfo_manager()
    app._apply_focus_preset()
    tpl=app.current_template()
    assert tpl.dof_enabled and tpl.dof_shape=='circle'
    assert tpl.dof_blur==pytest.approx(4.5)
    app.var_dof_shape.set('従来の上下ぼかし')
    root.update()
    assert app._legacy_dof_panel.winfo_manager()
    assert app.current_template().dof_shape=='band'


def test_gui_selected_template_explains_intended_look(gui):
    app,_=gui
    app.apply_template('アイスブルー・シネマ')
    assert app.var_grade.get()=='アイスブルー'
    assert app.template_hint.cget('text')==TEMPLATE_HELP_JA['アイスブルー・シネマ']
    app.apply_template('エピック・チームファイト')
    assert app.current_template().style=='cinema_top'


def test_all_effects_have_japanese_help_and_retired_mosaic_is_absent(gui):
    app, root = gui
    from core.effects import VIDEO_EFFECT_LABELS
    assert not set(VIDEO_EFFECT_LABELS) - set(EFFECT_HELP_JA)
    assert 'center_mosaic' not in EFFECT_HELP_JA and 'center_mosaic' not in app.effect_vars


def test_custom_circle_template_roundtrip_preserves_other_settings(gui):
    app, root = gui
    from core.effects import Template
    custom = Template(dof_enabled=True, dof_center_x=.4, dof_center_y=.6,
                      dof_radius=.2, dof_feather=.08, encoder_policy='cpu',
                      kill_frame_color='#22AA44', game_audio=True)
    app.templates['custom-test'] = Template(**custom.to_dict())
    app.apply_template('custom-test')
    result = app.current_template()
    assert (result.dof_center_x, result.dof_center_y, result.dof_radius, result.dof_feather) == (.4, .6, .2, .08)
    assert result.encoder_policy == 'cpu' and result.game_audio
    assert result.kill_frame_color == '#22AA44'
