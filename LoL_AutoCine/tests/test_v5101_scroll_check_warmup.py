"""UI-owned v5.10.1 wheel guard and scene list scroll tests."""
from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk
import pytest

@pytest.fixture
def gui(tmp_path, monkeypatch):
    import legacy_app
    monkeypatch.setattr(legacy_app, 'SETTINGS', tmp_path/'settings.json')
    root = tk.Tk()
    root.geometry('1450x900')
    app = legacy_app.App(root)
    root.update()
    yield app, root
    root.destroy()


def _all_combos(parent):
    for w in parent.winfo_children():
        if isinstance(w, ttk.Combobox):
            yield w
        yield from _all_combos(w)


def test_color_fx_grade_fog_and_export_combos_ignore_wheel(gui):
    app, root = gui
    targets = (app.var_grade, app.var_fog_preset, app.var_tr,
               app.var_encoder_policy, app.var_kill_mark_style)
    for var in targets:
        widgets = [w for w in _all_combos(root) if str(w.cget('textvariable')) == str(var)]
        assert widgets, str(var)
        before = var.get()
        for w in widgets:
            w.event_generate('<MouseWheel>', delta=-120)
            w.event_generate('<MouseWheel>', delta=120)
            w.event_generate('<Button-4>')
            w.event_generate('<Button-5>')
            root.update()
        assert var.get() == before, f'{var}: wheel changed value'


def test_dynamically_added_combobox_uses_wheel_guard(gui):
    app, root=gui
    v=tk.StringVar(value='one')
    late=ttk.Combobox(app.center_edit_scroll.inner, state='readonly',
                      values=('one','two','three'), textvariable=v)
    late.pack()
    root.update()
    late.event_generate('<MouseWheel>',delta=-120)
    root.update()
    assert v.get() == 'one'
    assert root.bind_class('TCombobox','<MouseWheel>')


def test_late_control_scrolls_panel_and_keeps_keyboard_selection(gui):
    app, root = gui
    panel = app.left_scroll
    value = tk.StringVar(value='one')
    late = ttk.Combobox(panel.inner, state='readonly',
                       values=('one', 'two', 'three'), textvariable=value)
    late.pack()
    root.update()
    panel.canvas.yview_moveto(0)
    root.update()
    before = panel.canvas.yview()[0]
    # Dispatch through the actual class binding with the pointer inside its panel.
    late.event_generate('<MouseWheel>', delta=-120,
                        rootx=panel.winfo_rootx()+10, rooty=panel.winfo_rooty()+10)
    root.update()
    assert panel.canvas.yview()[0] > before
    assert value.get() == 'one'
    panel.scroll_to(late)
    late.focus_force()
    root.update()
    late.event_generate('<Down>')  # Native readonly control opens its dropdown.
    root.update()
    popup = late.tk.call('ttk::combobox::PopdownWindow', str(late))
    assert root.tk.call('winfo', 'ismapped', popup)
    root.tk.call('event', 'generate', popup+'.f.l', '<Down>')
    root.tk.call('event', 'generate', popup+'.f.l', '<Return>')
    root.update()
    assert value.get() == 'two'


def test_scene_check_and_bulk_toggles_keep_vertical_scroll(gui):
    app, root = gui
    app.kills = [SimpleNamespace(event_id=i+1,time=float(i*12+10),killer='Alpha',
                    victim=f'Bravo{i}',multikill=1,role='kill') for i in range(40)]
    app.checked_kills = set(range(40))
    app.on_scene_selection = lambda *_: None
    app._fill_kills()
    root.update()
    app.lb_kills.yview_scroll(18, 'units')
    app.lb_kills.selection_clear(0,'end')
    app.lb_kills.selection_set(22)
    root.update()
    before = app.lb_kills.nearest(0)
    assert before >= 8
    app.on_toggle_checked()
    root.update()
    assert 22 not in app.checked_kills
    assert abs(app.lb_kills.nearest(0) - before) <= 1
    assert app.lb_kills.curselection() == (22,)
    app.on_toggle_checked()
    root.update()
    assert 22 in app.checked_kills
    assert abs(app.lb_kills.nearest(0) - before) <= 1
    app.on_uncheck_all()
    root.update()
    assert abs(app.lb_kills.nearest(0) - before) <= 1
    app.on_check_all()
    root.update()
    assert abs(app.lb_kills.nearest(0) - before) <= 1


def test_bracket_click_keeps_scroll_location(gui):
    app, root = gui
    app.kills = [SimpleNamespace(event_id=i+1,time=float(i+1),killer='A',
                    victim=f'B{i}',multikill=1,role='kill') for i in range(35)]
    app.checked_kills=set(range(35))
    app.on_scene_selection=lambda *_:None
    app._fill_kills()
    root.update()
    app.lb_kills.yview_scroll(15,'units')
    root.update()
    top = app.lb_kills.nearest(0)
    bbox=app.lb_kills.bbox(top+1)
    assert bbox
    e=SimpleNamespace(x=6,y=bbox[1]+bbox[3]//2)
    assert app._on_kill_list_click(e)=='break'
    root.update()
    assert abs(app.lb_kills.nearest(0)-top)<=1


def test_new_replay_and_reconnect_reset_recording_warmup(gui, monkeypatch, tmp_path):
    app, root = gui
    import legacy_app
    app.api._autocine_record_primed = True
    monkeypatch.setattr(legacy_app, 'watch_replay', lambda *a: 'mock launch')
    app._play(tmp_path/'mock.rofl')
    assert app.api._autocine_record_primed is False
    app.api._autocine_record_primed = True
    monkeypatch.setattr(app.api, 'wait_ready', lambda **kw: False)
    app._connect()
    assert app.api._autocine_record_primed is False
