"""Run with xvfb-run -a python -m pytest tests/test_editor_ui_contract.py -q."""
import tkinter as tk
from pathlib import Path

from ui.scene_timeline import SceneTimeline, clamp_seconds


def test_clamp():
    assert clamp_seconds(0) == 1.0
    assert clamp_seconds(16) == 15.0
    assert clamp_seconds(3.6) == 3.5
    assert clamp_seconds('nan') == 4.0


def test_timeline_sync():
    root = tk.Tk()
    root.geometry('700x300')
    a = tk.DoubleVar(root,value=4.0)
    b = tk.DoubleVar(root,value=3.0)
    timeline = SceneTimeline(root,a,b)
    timeline.pack(fill='x')
    root.update()
    a.set(8.0)
    assert timeline._num(a,0) == 8.0
    # Simulate real dragging; changes propagate to shared actual UI variables.
    class Event:
        pass
    event = Event()
    event.y = 50
    event.x = timeline._left_px
    timeline._down(event)
    event.x = timeline._kill_px - ((timeline.winfo_width()-48)/(2*15))*6
    timeline._move(event)
    timeline._up(event)
    assert a.get() == 6.0
    b.set(7.0)
    root.update()
    assert timeline._num(b,0) == 7.0
    root.destroy()


def test_default_one_click_preserved():
    # No requirement that the auto-director ever modifies a normal one click.
    from legacy_app import App
    root=tk.Tk()
    app=App(root)
    assert app.var_auto_director.get() is False
    assert app.current_template().pre == app.var_pre.get()
    assert app.current_template().post == app.var_post.get()
    app._set_camera_motion('dynamic',22.0,8.0)
    tpl=app.current_template()
    assert tpl.motion_arc == 22.0 and tpl.motion_dolly == 8.0
    assert tpl.motion_profile == 'dynamic'
    # Existing no-scan behavior: safe automatic camera preset, no rendering call.
    app._apply_auto_director()
    assert app.current_template().motion_profile == 'auto'
    root.destroy()
