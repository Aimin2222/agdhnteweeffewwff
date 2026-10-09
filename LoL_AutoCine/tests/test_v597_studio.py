# -*- coding: utf-8 -*-
"""v5.9.7 visual structure, language roundtrips and montage FX regression."""
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace
import pytest
from core.effects import Template
from core.montage_fx import cut_points, montage_filter, render_montage
from ui.studio_localization import SHOT_PROFILE_JA, FOG_LABEL_JA, reverse_label, convert_label
from legacy_app import App


def test_localizations_keep_machine_keys():
    for values in (SHOT_PROFILE_JA, FOG_LABEL_JA):
        for key, label in values.items():
            assert convert_label(key,values)==label
            assert reverse_label(label,values)==key


def test_montage_filter_has_exact_boundaries():
    assert cut_points(['a','b','c'],probe=lambda p: {'a':3,'b':2,'c':8}[p.name]) == [3,5]
    assert montage_filter('cut',[3]) == 'null'
    assert '3.0000' in montage_filter('flash',[3])
    assert '3.0000' in montage_filter('dark',[3])
    with pytest.raises(ValueError): montage_filter('invalid',[3])


def test_fullwidth_editor_and_preserved_settings():
    root=tk.Tk()
    try:
        root.geometry('1540x900')
        app=App(root)
        root.update()
        assert app.center_edit_host.winfo_rooty()>app.center_preview_host.winfo_rooty()
        # Lower section now extends beneath the three upper columns.
        assert app.center_edit_host.winfo_width()>app.center_preview_host.winfo_width()+220
        app.var_edit_mode.set('advanced')
        app._apply_edit_mode(log=False)
        app.var_editor_zone.set('scene')
        app._apply_editor_zone()
        app.var_shot_profile.set(SHOT_PROFILE_JA['dynamic'])
        app.var_shot_intensity.set('強め')
        shot=app._scene_shot_from_ui()
        assert (shot.profile,shot.intensity)==('dynamic','strong')
        app.var_montage_fx.set('光るカット（白い閃光）')
        t=app.current_template()
        assert t.montage_fx=='flash'
        app.apply_template(t.name)  # selected template should still be loadable
        app.var_montage_fx.set('暗転カット（シネマ）')
        assert app.current_template().montage_fx=='dark'
    finally:
        root.destroy()


def test_montage_cut_calls_existing_joiner(tmp_path):
    one=tmp_path/'one.mp4';one.write_bytes(b'1')
    two=tmp_path/'two.mp4';two.write_bytes(b'2')
    output=tmp_path/'montage.mp4'
    calls=[]
    def concatenate(clips, dst):
        calls.append(list(clips));Path(dst).write_bytes(b'joined')
    assert render_montage([one,two],output,'cut',concat=concatenate)=='cut'
    assert output.read_bytes()==b'joined'
    assert calls==[[one,two]]
