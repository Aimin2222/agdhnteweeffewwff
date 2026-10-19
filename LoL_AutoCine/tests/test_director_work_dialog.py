"""Run in an isolated GUI case; exercise real selection/quality gates."""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
from ui.director_work_controls import initialize, open_settings, apply
from core.effects import Template


def test_work_dialog_defaults_to_only_approved_and_explicit_review_toggle():
    root = tk.Tk()
    root.withdraw()
    logs = []
    app = SimpleNamespace(root=root, var_kill_icon_motion=tk.StringVar(value='一気に表示'),
                          log=logs.append, _invalidate_preview_snapshot=lambda:None,
                          _save_settings=lambda:None)
    initialize(app)
    window = open_settings(app)
    window.withdraw()
    try:
        root.update()
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        widgets = list(descendants(window))
        combos = [w for w in widgets if isinstance(w,ttk.Combobox)]
        frames,effects,_ = combos
        assert len(frames['values']) == 2  # off + approved083
        assert len(effects['values']) == 1
        frames.current(1)
        frames.event_generate('<<ComboboxSelected>>')
        root.update()
        assert apply(app,Template()).work_kill_frame_id == '083/a_simple_main'
        review = next(w for w in widgets if isinstance(w,ttk.Checkbutton))
        review.invoke()
        assert app.var_work_review.get()
        assert len(frames['values']) == 653 and len(effects['values']) == 36
        effects.current(1)
        effects.event_generate('<<ComboboxSelected>>')
        root.update()
        assert app.var_work_effect.get()
        review.invoke()
        assert not app.var_work_effect.get()
        assert not logs and app.camera_auto_qa_approved == {}
    finally:
        window.destroy()
        root.destroy()
