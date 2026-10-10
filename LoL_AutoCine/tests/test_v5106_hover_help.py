"""The incoming hover patch retains v5.10.5 click help and responsive Tk."""
import time
import tkinter as tk
from tkinter import ttk
from legacy_app import bind_effect_hover_tip


def pump(root,predicate):
    deadline=time.monotonic()+1
    while not predicate() and time.monotonic()<deadline:
        root.update();time.sleep(.005)
    assert predicate()


def test_hover_opens_then_leave_destroys_without_replacing_click():
    root=tk.Tk();clicked=[]
    button=ttk.Button(root,text='?',command=lambda:clicked.append(True));button.pack();root.update()
    try:
        bind_effect_hover_tip(button,'日本語の説明',delay_ms=10)
        button.event_generate('<Enter>')
        pump(root,lambda:any(isinstance(w,tk.Toplevel) for w in button.winfo_children()))
        tip=next(w for w in button.winfo_children() if isinstance(w,tk.Toplevel))
        assert tip.winfo_children()[0]['text']=='日本語の説明'
        button.invoke();assert clicked==[True]
        button.event_generate('<Leave>');root.update()
        assert not tip.winfo_exists()
    finally:root.destroy()


def test_pending_hover_is_cancelled_on_destroy():
    root=tk.Tk();errors=[]
    root.report_callback_exception=lambda *a:errors.append(a)
    button=ttk.Button(root,text='?');button.pack();root.update()
    bind_effect_hover_tip(button,'説明',delay_ms=15)
    button.event_generate('<Enter>');button.destroy()
    try:
        started=time.monotonic()
        pump(root,lambda:time.monotonic()-started>.03)
        root.update();assert not errors
    finally:root.destroy()
