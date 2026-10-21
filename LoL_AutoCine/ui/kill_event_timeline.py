"""Read-only match event overview; selecting a marker selects the real scene."""
from __future__ import annotations

import tkinter as tk


class KillEventTimeline(tk.Canvas):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, height=70, background="#F8FAFC",
                         highlightthickness=1, highlightbackground="#CBD5E1", **kwargs)
        self.on_select = on_select
        self.events = []
        self.checked = set()
        self.selected = None
        self.duration = 0.0
        self.markers = []
        self.bind("<Configure>", lambda _event: self.redraw())
        self.bind("<Button-1>", self._select)

    def set_events(self, events, checked, duration=None, selected=None):
        self.events = list(events)
        self.checked = set(checked)
        self.duration = max(float(duration or 0),
                            max((float(event.time) for event in self.events), default=0) + 1)
        self.selected = selected
        self.redraw()

    def redraw(self):
        self.delete("all")
        width = max(self.winfo_width(), 100)
        left, right = 18, width - 18
        self.create_text(left, 10, anchor="w", text="試合イベント：マークをクリックしてシーンを選択",
                         fill="#475569", font=("Meiryo UI", 9))
        self.create_line(left, 38, right, 38, fill="#CBD5E1", width=3)
        self.markers = []
        if not self.events:
            self.create_text(width / 2, 48, text="スキャン後にキル・アシストを表示",
                             fill="#64748B", font=("Meiryo UI", 9))
            return
        for index, event in enumerate(self.events):
            x = left + (right - left) * max(0.0, min(1.0, float(event.time) / self.duration))
            color = ("#94A3B8" if index not in self.checked else
                     "#2563EB" if getattr(event, "role", "kill") == "assist" else "#DC2626")
            radius = 7 if index == self.selected else 5
            self.create_oval(x-radius, 38-radius, x+radius, 38+radius,
                             fill=color, outline="#0F172A" if index == self.selected else "white",
                             width=2)
            self.markers.append((x, index))
        self.create_text(left, 60, text="0:00", anchor="w", fill="#64748B", font=("Meiryo UI", 8))
        seconds = int(self.duration)
        self.create_text(right, 60, text=f"{seconds // 60}:{seconds % 60:02d}",
                         anchor="e", fill="#64748B", font=("Meiryo UI", 8))

    def _select(self, event):
        if not self.markers:
            return
        x, index = min(self.markers, key=lambda pair: abs(pair[0] - event.x))
        if abs(x - event.x) <= 14:
            self.selected = index
            self.redraw()
            self.on_select(index)
