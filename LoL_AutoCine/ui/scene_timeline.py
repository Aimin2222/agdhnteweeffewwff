# -*- coding: utf-8 -*-
"""Timeline for trim pre/post seconds. UI only, no GPU/render engine dependency.

Both the editor and the basic-panel spinboxes share two Tk DoubleVars.
Changing either one changes the exact same Template.pre / Template.post fields.
"""
from __future__ import annotations
import tkinter as tk

MIN_SECONDS = 1.0
MAX_SECONDS = 15.0


def clamp_seconds(value) -> float:
    """Keep the timeline within the current Template UI-supported boundaries."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 4.0
    if not (number == number and abs(number) != float('inf')):
        return 4.0
    return max(MIN_SECONDS, min(MAX_SECONDS, round(number * 2) / 2))


class SceneTimeline(tk.Canvas):
    """Dragging left and right handles updates the real clip length controls.

    This controls *clip trimming* only; it does not pretend to edit camera
    animation keyframes. The camera motion engine remains unchanged.
    """
    def __init__(self, master, pre_var: tk.DoubleVar, post_var: tk.DoubleVar, **kwargs):
        options = dict(height=110, background='#F8FAFC', highlightthickness=1,
                       highlightbackground='#CBD5E1', cursor='hand2')
        options.update(kwargs)
        super().__init__(master, **options)
        self.pre_var, self.post_var = pre_var, post_var
        self._drag = None
        self._left_px, self._right_px, self._kill_px = 0.0, 0.0, 0.0
        self.bind('<Configure>', lambda _e: self.redraw())
        self.bind('<Button-1>', self._down)
        self.bind('<B1-Motion>', self._move)
        self.bind('<ButtonRelease-1>', self._up)
        self.pre_var.trace_add('write', lambda *_: self.redraw())
        self.post_var.trace_add('write', lambda *_: self.redraw())
        self.redraw()

    @staticmethod
    def _num(variable, default):
        try:
            return clamp_seconds(variable.get())
        except (tk.TclError, ValueError):
            return default

    def redraw(self):
        self.delete('all')
        w=max(320,self.winfo_width())
        h=max(100,self.winfo_height())
        left,right=24,w-24
        kill=(left+right)/2
        pre=self._num(self.pre_var,4.0)
        post=self._num(self.post_var,3.0)
        unit=(right-left)/(2*MAX_SECONDS)
        start,end=kill-unit*pre,kill+unit*post
        self._left_px,self._right_px,self._kill_px=start,end,kill
        self.create_text(left,13,text='ドラッグでキル前・キル後の長さを調整',anchor='w',fill='#475569',font=('Meiryo UI',9))
        self.create_rectangle(left,38,right,65,fill='#E2E8F0',outline='')
        self.create_rectangle(start,38,kill,65,fill='#BFDBFE',outline='')
        self.create_rectangle(kill,38,end,65,fill='#FDE68A',outline='')
        self.create_line(kill,31,kill,76,fill='#F97316',width=2)
        for x,txt,color in ((start,f'-{pre:g}秒','#2563EB'),(kill,'キル','#C2410C'),(end,f'+{post:g}秒','#9A6700')):
            self.create_line(x,34,x,71,fill=color,width=3)
            self.create_text(x,83,text=txt,fill=color,font=('Meiryo UI',9,'bold'))
        self.create_oval(start-6,44,start+6,58,fill='white',outline='#2563EB',width=2)
        self.create_oval(end-6,44,end+6,58,fill='white',outline='#D97706',width=2)
        self.create_text(left,103,text='青: キル前',anchor='w',fill='#475569',font=('Meiryo UI',8))
        self.create_text(right,103,text='黄: キル後',anchor='e',fill='#475569',font=('Meiryo UI',8))

    def _down(self,event):
        if event.y < 30 or event.y > 76:
            return
        # Pick nearest side even when clicked inside a segment.
        self._drag='pre' if abs(event.x-self._left_px)<=abs(event.x-self._right_px) else 'post'
        self._move(event)

    def _move(self,event):
        if self._drag not in ('pre','post'):
            return
        w=max(320,self.winfo_width())
        px_per_sec=(w-48)/(2*MAX_SECONDS)
        value=clamp_seconds(abs(event.x-self._kill_px)/px_per_sec)
        if self._drag=='pre':
            self.pre_var.set(value)
        else:
            self.post_var.set(value)

    def _up(self,_event):
        self._drag=None
