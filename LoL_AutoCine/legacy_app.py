# -*- coding: utf-8 -*-
"""LoL AutoCine - リプレイからキルクリップを自動でMP4にするアプリ (Windows / 個人利用)。"""
from __future__ import annotations
import json
import os
import queue
import sys
import threading
import time
import traceback
import faulthandler
import hashlib
import tkinter as tk
from dataclasses import fields
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import numpy as np
from PIL import Image, ImageTk

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core import paths                                             # noqa: E402
from core.camera import INTENSITY_JP, STYLES                       # noqa: E402
from core.capture import CaptureError, SyntheticSource, WGCWindowSource   # noqa: E402
from core.effects import (FOG_PRESETS, GRADE_JP, TRANSITIONS, Template, one_click_templates, gpu_encoder_available, gpu_pipeline_status,
                            VIDEO_EFFECT_CATEGORIES, VIDEO_EFFECT_DEFAULTS, VIDEO_EFFECT_LABELS)   # noqa: E402
from core.reference_safe import make_remixes, save_template as save_reference_template, load_template as load_reference_template, template_from_references  # noqa: E402
from core.audio import PreferredGameAudio, SyntheticAudio               # noqa: E402
from core.jobs import preview_clip, run_auto_edit                  # noqa: E402
from core.preview import apply_camera_preview, apply_video_effect_preview, compose_compare, preview_title, render_exact_still   # noqa: E402
from core.launcher import watch_replay                             # noqa: E402
from core.players import Player, parse_players                     # noqa: E402
from core.replay_api import ReplayAPI                              # noqa: E402
from core.scanner import scan_kills                                # noqa: E402
from ui.scene_timeline import SceneTimeline                     # noqa: E402
from ui.scene_project import SceneProject, Shot, scene_key, recommend, apply_shot  # noqa: E402
from ui.scene_batch import render_scenes                      # noqa: E402
from ui.motion_graph import ShotMotionGraph                  # noqa: E402

APP = "LoL AutoCine"
FONT = ("Meiryo UI", 10)
SETTINGS = ROOT / "settings.json"
API_BASE = os.environ.get("AUTOCINE_API_BASE", "https://127.0.0.1:2999")
FAKE_CAPTURE = os.environ.get("AUTOCINE_FAKE_CAPTURE") == "1"      # テスト用

# ---- crash-safe diagnostics -----------------------------------------
DIAG_DIR = ROOT / "diagnostics"
DIAG_DIR.mkdir(parents=True, exist_ok=True)
CRASH_LOG = DIAG_DIR / "crash.log"
RUN_LOG = DIAG_DIR / "runtime.log"
FATAL_LOG = DIAG_DIR / "fatal_python.log"
try:
    _fatal_fp = FATAL_LOG.open("a", encoding="utf-8", errors="replace", buffering=1)
    faulthandler.enable(_fatal_fp, all_threads=True)
except Exception:
    _fatal_fp = None

def _diag_write(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", errors="replace") as f:
            f.write(text.rstrip() + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass

def _uncaught_exception(exc_type, exc_value, exc_tb) -> None:
    detail = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _diag_write(CRASH_LOG, "\n===== UNCAUGHT EXCEPTION %s =====\n%s" % (time.strftime("%Y-%m-%d %H:%M:%S"), detail))
    try:
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    except Exception:
        pass

def _thread_exception(args) -> None:
    detail = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    _diag_write(CRASH_LOG, "\n===== THREAD EXCEPTION %s [%s] =====\n%s" % (time.strftime("%Y-%m-%d %H:%M:%S"), getattr(args.thread, "name", "unknown"), detail))
    try:
        threading.__excepthook__(args)
    except Exception:
        pass

sys.excepthook = _uncaught_exception
if hasattr(threading, "excepthook"):
    threading.excepthook = _thread_exception


def rev(d: dict) -> dict:
    return {v: k for k, v in d.items()}


class ScrollFrame(ttk.Frame):
    """縦スクロールできるパネル。子ウィジェット/Scale/Scrollbar上でもホイールを奪わずパネルをスクロールする。"""

    def __init__(self, parent, width: int):
        super().__init__(parent, width=width)
        self._panel_width = int(width)
        self.pack_propagate(False)
        self.canvas = tk.Canvas(self, width=width, highlightthickness=0, borderwidth=0, bg="#F6F7F9")
        self.sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>", self._update_scrollregion)
        self._window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw", width=width)
        self.canvas.bind("<Configure>", self._fit_inner_width)
        self.canvas.configure(yscrollcommand=self.sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.sb.pack(side="right", fill="y")
        self._wheel_bind_id = self.winfo_toplevel().bind_all("<MouseWheel>", self._global_wheel, add="+")
        self.winfo_toplevel().bind_all("<Button-4>", self._global_wheel, add="+")
        self.winfo_toplevel().bind_all("<Button-5>", self._global_wheel, add="+")

    def _update_scrollregion(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_inner_width(self, event) -> None:
        self.canvas.itemconfigure(self._window_id, width=max(1, event.width))
        self._update_scrollregion()

    def _pointer_inside(self, e) -> bool:
        try:
            x, y = e.x_root, e.y_root
            rx, ry = self.winfo_rootx(), self.winfo_rooty()
            return rx <= x < rx + self.winfo_width() and ry <= y < ry + self.winfo_height()
        except tk.TclError:
            return False

    def _global_wheel(self, e) -> None:
        if not self._pointer_inside(e):
            return
        delta = getattr(e, "delta", 0)
        if delta:
            units = -max(-8, min(8, int(delta / 120)))
        elif getattr(e, "num", None) == 4:
            units = -3
        else:
            units = 3
        self.canvas.yview_scroll(units, "units")

    def set_width(self, width: int) -> None:
        width = max(260, min(620, int(width)))
        self._panel_width = width
        self.configure(width=width)
        self.canvas.configure(width=width)
        self.canvas.itemconfigure(self._window_id, width=width)
        self.update_idletasks()
        self._update_scrollregion()


class CurveEditor(tk.Canvas):
    """LoLnam風の大きめトーンカーブ。ドラッグと数値入力を同じ値へ同期する。"""
    def __init__(self, master, var, points="0/0 0.25/0.20 0.50/0.50 0.75/0.80 1/1", **kw):
        canvas_kw = dict(kw)
        canvas_kw.setdefault("height", 230)
        canvas_kw.setdefault("bg", "#111827")
        canvas_kw.setdefault("highlightthickness", 1)
        canvas_kw.setdefault("highlightbackground", "#334155")
        super().__init__(master, **canvas_kw)
        self.var = var
        self.points = self._parse(points)
        self.drag = None
        self.hist = None
        self.var.trace_add("write", lambda *_: self._sync_from_var())
        self.bind("<Configure>", lambda _e: self.draw())
        self.bind("<Button-1>", self._down)
        self.bind("<B1-Motion>", self._move)
        self.bind("<ButtonRelease-1>", self._up)
        self.draw()

    def _parse(self, text):
        pts=[]
        for token in str(text).replace(';',' ').split():
            try:
                x,y=token.split('/')[:2]
                pts.append([max(0,min(1,float(x))),max(0,min(1,float(y)))])
            except Exception:
                pass
        return sorted(pts or [[0,0],[1,1]])

    def _sync_from_var(self):
        self.points=self._parse(self.var.get())
        self.draw()

    def set_histogram(self, rgb):
        """現在のミラー映像の輝度ヒストグラムを背景に表示。"""
        try:
            a=np.asarray(rgb)
            if a.ndim == 3 and a.shape[2] >= 3:
                lum=(0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]).astype(np.uint8)
                self.hist=np.histogram(lum,bins=64,range=(0,255))[0].astype(float)
                mx=max(1.0,float(self.hist.max()))
                self.hist/=mx
                self.draw()
        except Exception:
            pass

    def reset(self):
        self.var.set("0/0 1/1")

    def _bounds(self):
        w=max(300,self.winfo_width() or 520)
        h=max(180,self.winfo_height() or 230)
        return 18, w-18, 12, h-28

    def _xy(self,x,y):
        l,r,t,b=self._bounds()
        return l+x*(r-l), b-y*(b-t)

    def _down(self,e):
        best=None; bd=14
        for i,(x,y) in enumerate(self.points):
            px,py=self._xy(x,y)
            d=((e.x-px)**2+(e.y-py)**2)**0.5
            if d<bd:
                best=i; bd=d
        if best is not None:
            self.drag=best
            return
        # クリックで新しい制御点を追加（両端は固定）
        l,r,t,b=self._bounds()
        x=max(0,min(1,(e.x-l)/max(1,r-l)))
        y=max(0,min(1,(b-e.y)/max(1,b-t)))
        if 0.02 < x < 0.98:
            self.points.append([x,y])
            self.points.sort(key=lambda p:p[0])
            self.drag=min(range(len(self.points)),key=lambda i:abs(self.points[i][0]-x))
            self.var.set(' '.join(f'{x:.3f}/{y:.3f}' for x,y in self.points))

    def _move(self,e):
        if self.drag is None:
            return
        l,r,t,b=self._bounds()
        x=max(0,min(1,(e.x-l)/max(1,r-l)))
        y=max(0,min(1,(b-e.y)/max(1,b-t)))
        if self.drag==0: x=0
        if self.drag==len(self.points)-1: x=1
        self.points[self.drag]=[x,y]
        self.points.sort(key=lambda p:p[0])
        self.drag=min(self.drag,len(self.points)-1)
        self.var.set(' '.join(f'{x:.3f}/{y:.3f}' for x,y in self.points))
        self.draw()

    def _up(self,e):
        self.drag=None

    def _delete_near(self,e):
        pass

    def draw(self):
        self.delete('all')
        l,r,t,b=self._bounds()
        # histogram
        if self.hist is not None:
            bw=(r-l)/len(self.hist)
            for i,v in enumerate(self.hist):
                hh=(b-t)*0.82*v
                x0=l+i*bw
                self.create_rectangle(x0,b-hh,x0+bw+1,b,fill="#475569",outline="")
        # grid
        for i in range(1,5):
            x=l+i*(r-l)/5
            y=t+i*(b-t)/5
            self.create_line(x,t,x,b,fill="#334155")
            self.create_line(l,y,r,y,fill="#334155")
        self.create_line(l,b,r,t,fill="#64748B",dash=(5,5))
        xy=[self._xy(x,y) for x,y in self.points]
        for a,bp in zip(xy,xy[1:]):
            self.create_line(*a,*bp,fill="#F8FAFC",width=3,smooth=True)
        for x,y in xy:
            self.create_oval(x-6,y-6,x+6,y+6,fill="#F8FAFC",outline="#CBD5E1",width=1)
        self.create_text(l+2,t+2,text="入力 → 出力",anchor="nw",fill="#94A3B8",font=("Meiryo UI",8))
        self.create_text(r-2,b+16,text="クリック: 点追加 / ドラッグ: 移動 / 両端は固定",
                         anchor="e",fill="#94A3B8",font=("Meiryo UI",8))

class FogViz(tk.Canvas):
    def __init__(self, master, strength_var, **kw):
        super().__init__(master, width=260, height=90, bg="#F8FAFC", highlightthickness=1, highlightbackground="#D0D5DD", **kw)
        self.var=strength_var; self.var.trace_add("write", lambda *_: self.draw()); self.draw()
    def draw(self):
        self.delete("all")
        try:v=max(0,min(1,float(self.var.get())))
        except Exception:return
        self.create_line(18,68,240,18,fill="#D0D5DD",dash=(3,3))
        # fog opacity curve: stronger fog toward the right/depth side
        pts=[]
        for i in range(21):
            x=i/20; y=(x*x)*v; pts.append((18+x*222,68-y*50))
        for a,b in zip(pts,pts[1:]):self.create_line(*a,*b,fill="#0EA5A4",width=3)
        self.create_text(12,8,text="FOG  深度 →",anchor="nw",fill="#667085",font=("Meiryo UI",8))
        self.create_text(240,78,text=f"強度 {v:.2f}",anchor="e",fill="#0F766E",font=("Meiryo UI",8,"bold"))

class DofViz(tk.Canvas):
    def __init__(self, master, blur_var, focus_var, near_var, far_var, **kw):
        super().__init__(master,width=260,height=90,bg='#F8FAFC',highlightthickness=1,highlightbackground='#D0D5DD',**kw)
        self.vars=(blur_var,focus_var,near_var,far_var)
        for v in self.vars:v.trace_add('write',lambda *_:self.draw())
        self.draw()
    def draw(self):
        self.delete('all'); w=int(self.winfo_width() or 260); h=90
        try:b=float(self.vars[0].get()); f=float(self.vars[1].get()); n=float(self.vars[2].get()); far=float(self.vars[3].get())
        except Exception:return
        span=max(1,n+f+far); fx=18+min(w-36,(f/span)*(w-36)); nx=18+min(w-36,((f-n)/span)*(w-36)); rx=18+min(w-36,((f+far)/span)*(w-36))
        self.create_rectangle(18,25,w-18,65,fill='#E5E7EB',outline='')
        self.create_rectangle(max(18,nx),25,min(w-18,fx),65,fill='#CBD5E1',outline='')
        self.create_rectangle(fx-3,20,fx+3,70,fill='#2563EB',outline='')
        self.create_text(fx,12,text='FOCUS',fill='#2563EB',font=('Meiryo UI',8,'bold'))
        self.create_text(18,78,text=f'近 {n:.0f}',anchor='w',fill='#667085',font=('Meiryo UI',8))
        self.create_text(w-18,78,text=f'遠 {far:.0f}',anchor='e',fill='#667085',font=('Meiryo UI',8))

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"{APP} v5.9.3 - シンプル / 詳細編集")
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{min(1560, sw - 40)}x{min(960, sh - 90)}+10+10")
        root.option_add("*Font", FONT)
        root.configure(bg="#F6F7F9")
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.api = ReplayAPI(API_BASE)
        self.lol_dir = paths.find_lol_dir()
        self.players: list = []
        self.locked: Player | None = None
        self.kills: list = []
        self.checked_kills: set[int] = set()
        self.var_event_mode = tk.StringVar(value="キル")
        self.source = None
        self.templates = one_click_templates()
        self.reference_videos: list[str] = []
        self.reference_template_dir = ROOT / "templates" / "reference"
        self.reference_template_dir.mkdir(parents=True, exist_ok=True)
        for _rp in sorted(self.reference_template_dir.glob("*.json")):
            try:
                _t = load_reference_template(_rp)
                self.templates[_t.name] = _t
            except Exception:
                pass
        self.q: queue.Queue = queue.Queue()
        self.stop_ev = threading.Event()
        self.busy = False
        self._photo = None
        self._checked_watchdog_active = False
        self.out_root = Path(os.path.expanduser("~")) / "Videos" / "LoL_AutoCine"
        self.var_left_width = tk.IntVar(value=310)
        self.var_right_width = tk.IntVar(value=390)
        self.var_format = tk.StringVar(value="MP4（1080p）")
        # UI再構成前から存在するテンプレート設定変数。_build() の複数パネルから共有するため先に初期化する。
        self.var_style = tk.StringVar(value=STYLES.get("cinema", "Cinematic"))
        # Shared by the draggable timeline and the existing basic editor controls.
        # Initialize before _build(); never replace these variables with new instances.
        self.var_pre = tk.DoubleVar(value=4.0)
        self.var_post = tk.DoubleVar(value=3.0)
        self.var_auto_director = tk.BooleanVar(value=False)  # preserve old one-click default
        self.var_scene_mode = tk.BooleanVar(value=False)    # opt-in per-scene rendering
        self.var_edit_mode = tk.StringVar(value="easy")  # view only: never silently change rendering state
        self.scene_project = SceneProject()
        self.scene_project_path = ROOT / 'projects' / 'scene_project.json'
        self._project_autosave_token = None
        self._scene_loading = False
        self._build()
        self._load_settings()
        try:
            if self.scene_project_path.exists():
                self.scene_project = SceneProject.load(self.scene_project_path)
        except Exception as e:
            self.log(f"シーンプロジェクトの復元をスキップ: {e}")
        self.root.after(80, self._pump)
        # UIプレビューはTkinter/PIL/NumpyのCPU合成。書き出し側はGPU Hybridを使用。
        # 144Hzで毎回フルフレーム加工するとUI操作まで重くなるため、プレビュー処理は最大60Hzに制限。
        self.root.after(16, self._preview_tick)
        self.log("起動しました。①から順に、または上部の『★ これで自動作成』を押してください。")
        self._refresh_status()

    # ------------------------------------------------------------ UI
    def _build(self) -> None:
        """白基調のLoLnam風3ペインUI。既存の処理・ハンドラはそのまま利用する。"""
        r = self.root
        bg = "#F4F7FB"
        panel = "#FFFFFF"
        panel2 = "#F8FAFC"
        fg = "#172033"
        muted = "#667085"
        line = "#D9E1EC"
        accent = "#1677FF"
        accent_dark = "#0B63D8"
        selected = "#EAF3FF"
        green = "#159A6B"

        r.configure(bg=bg)
        r.minsize(1280, 780)
        style = ttk.Style(r)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=bg, foreground=fg, font=("Meiryo UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("SubCard.TFrame", background=panel2)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("Card.TLabel", background=panel, foreground=fg)
        style.configure("Sub.TLabel", background=panel2, foreground=fg)
        style.configure("Muted.TLabel", background=bg, foreground=muted)
        style.configure("CardMuted.TLabel", background=panel, foreground=muted)
        style.configure("Section.TLabel", background=panel, foreground="#111827", font=("Meiryo UI", 11, "bold"))
        style.configure("BigTitle.TLabel", background=bg, foreground="#0F172A", font=("Meiryo UI", 18, "bold"))
        style.configure("SmallTitle.TLabel", background=bg, foreground=muted, font=("Meiryo UI", 9))
        style.configure("Mode.TRadiobutton", background="#EAF3FF", foreground="#174EA6", font=("Meiryo UI", 11, "bold"), padding=(12, 9))
        style.map("Mode.TRadiobutton", background=[("active", "#D9EAFE")])
        style.configure("Nav.TButton", background=bg, foreground="#596780", padding=(14, 11), borderwidth=0, font=("Meiryo UI", 10, "bold"))
        style.map("Nav.TButton", background=[("active", "#EAF3FF")], foreground=[("active", accent)])
        style.configure("TButton", background="#FFFFFF", foreground="#344054", padding=(10, 7), bordercolor=line, lightcolor=line, darkcolor=line)
        style.map("TButton", background=[("active", "#F2F6FB"), ("pressed", "#E6EEF8")], foreground=[("disabled", "#98A2B3")])
        style.configure("Accent.TButton", background=accent, foreground="#FFFFFF", padding=(13, 9), borderwidth=0, font=("Meiryo UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", accent_dark), ("pressed", accent_dark)])
        style.configure("OutlineAccent.TButton", background="#FFFFFF", foreground=accent, padding=(10, 7), bordercolor="#B8D5FF", lightcolor="#B8D5FF", darkcolor="#B8D5FF")
        style.map("OutlineAccent.TButton", background=[("active", "#EEF6FF")])
        style.configure("TCheckbutton", background=panel, foreground=fg)
        style.map("TCheckbutton", background=[("active", panel)])
        style.configure("TRadiobutton", background=panel, foreground=fg)
        style.map("TRadiobutton", background=[("active", panel)])
        style.configure("TCombobox", fieldbackground="#FFFFFF", background="#FFFFFF", foreground=fg, bordercolor=line, lightcolor=line, darkcolor=line, padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", "#FFFFFF")], foreground=[("readonly", fg)])
        style.configure("TEntry", fieldbackground="#FFFFFF", foreground=fg, bordercolor=line, lightcolor=line, darkcolor=line, padding=6)
        style.configure("TSpinbox", fieldbackground="#FFFFFF", foreground=fg, bordercolor=line, lightcolor=line, darkcolor=line, padding=5)
        style.configure("Horizontal.TScale", background=panel, troughcolor="#E3EAF3")
        style.configure("TProgressbar", troughcolor="#E6ECF3", background=accent, borderwidth=0)
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=fg, rowheight=30, borderwidth=0)
        style.map("Treeview", background=[("selected", selected)], foreground=[("selected", "#0F172A")])
        style.configure("Treeview.Heading", background="#F2F5F9", foreground="#475467", relief="flat", padding=(6, 6), font=("Meiryo UI", 9, "bold"))
        style.configure("Vertical.TScrollbar", background="#F2F4F7", troughcolor="#FAFBFC", bordercolor="#FAFBFC", arrowcolor="#98A2B3")

        # ---- top navigation -------------------------------------------------
        # 既存のクイック操作で使用していた変数を先に初期化し、
        # 上部ナビからも同じ設定・処理を操作できるようにする。
        self.var_tpl = tk.StringVar(value=list(self.templates)[0])
        self.var_int = tk.StringVar(value="standard")

        top = ttk.Frame(r, padding=(18, 7, 18, 6))
        top.pack(fill="x")
        brand_box = ttk.Frame(top)
        brand_box.pack(side="left")
        ttk.Label(brand_box, text="◈  LoL AutoCine v5.9.3", style="BigTitle.TLabel").pack(anchor="w")
        ttk.Label(brand_box, text="", style="SmallTitle.TLabel").pack(anchor="w", pady=(0, 1))

        nav = ttk.Frame(top)
        nav.pack(side="left", padx=(48, 0))
        ttk.Button(nav, text="⌂  ホーム", style="Nav.TButton", command=lambda: self._focus_home()).pack(side="left")
        ttk.Button(nav, text="▣  テンプレート", style="Nav.TButton", command=lambda: self._focus_template()).pack(side="left")
        ttk.Button(nav, text="▰  参考動画", style="Nav.TButton", command=lambda: self._focus_reference()).pack(side="left")
        ttk.Button(nav, text="⚙  設定", style="Nav.TButton", command=self.on_show_diagnostics).pack(side="left")

        right_top = ttk.Frame(top)
        right_top.pack(side="right")
        ttk.Label(right_top, text="出力FPS", style="Muted.TLabel").pack(side="left", padx=(0, 5))
        self.var_fps_ui = tk.StringVar(value="60 FPS")
        self.var_preview_hz = tk.StringVar(value="144 Hz")
        ttk.Label(right_top, text="プレビュー", style="Muted.TLabel").pack(side="left", padx=(0, 4))
        ttk.Combobox(right_top, state="readonly", width=9, textvariable=self.var_preview_hz,
                     values=["60 Hz", "144 Hz"]).pack(side="left", padx=(0, 6))
        ttk.Label(right_top, text="出力", style="Muted.TLabel").pack(side="left", padx=(0, 4))
        ttk.Combobox(right_top, state="readonly", width=9, textvariable=self.var_fps_ui,
                     values=["60 FPS", "144 FPS"]).pack(side="left")
        ttk.Button(right_top, text="＋", width=3, command=self.on_quick_prepare).pack(side="left", padx=5)
        ttk.Button(right_top, text="☼", width=3, command=lambda: None).pack(side="left")

        # View switch is UI-only. Project, checkmarks, templates and the render mode
        # are never reset when the user changes between easy/detailed views.
        mode_bar = ttk.Frame(r, padding=(20, 5, 20, 7))
        mode_bar.pack(fill="x")
        ttk.Label(mode_bar, text="編集モード", style="Muted.TLabel").pack(side="left", padx=(0, 12))
        for title, mode_id in (("★ かんたん編集", "easy"), ("⚙ 詳細編集", "advanced")):
            ttk.Radiobutton(mode_bar, text=title, value=mode_id,
                            variable=self.var_edit_mode, style="Mode.TRadiobutton",
                            command=self._apply_edit_mode).pack(side="left", padx=(0, 8))
        self.edit_mode_hint = ttk.Label(mode_bar, style="Muted.TLabel")
        self.edit_mode_hint.pack(side="left", padx=12)
        ttk.Separator(r).pack(fill="x")

        # ---- main three-pane layout ----------------------------------------
        body = ttk.Frame(r, padding=(10, 7, 10, 5))
        body.pack(fill="both", expand=True)

        self.left_scroll = ScrollFrame(body, 310)
        self.left_scroll.pack(side="left", fill="y")
        left = self.left_scroll.inner

        # 中央は「マルチ分割 + 上下リサイズ」。
        # 上段のLoLミラーと下段の編集エリアを境界ドラッグで上下に移動できる。
        # 編集エリアだけスクロールするため、設定を下へ送ってもミラーを見失わない。
        center = ttk.Frame(body, style="Card.TFrame")
        center.pack(side="left", fill="both", expand=True, padx=9)
        center_split = tk.PanedWindow(
            center, orient="vertical", sashwidth=8, sashrelief="raised",
            bd=0, relief="flat", bg="#E4E7EC", opaqueresize=True
        )
        center_split.pack(fill="both", expand=True)
        preview_host = ttk.Frame(center_split, style="Card.TFrame")
        edit_host = ttk.Frame(center_split, style="Card.TFrame")
        center_split.add(preview_host, minsize=360, stretch="always")
        center_split.add(edit_host, minsize=250, stretch="always")
        center_edit_scroll = ScrollFrame(edit_host, 0)
        center_edit_scroll.pack(fill="both", expand=True)
        center_edit = center_edit_scroll.inner
        self.center_split = center_split
        self.center_preview_host = preview_host
        self.center_edit_host = edit_host
        self._center_split_initialized = False

        def _init_center_split(_event=None):
            if self._center_split_initialized:
                return
            try:
                h = center_split.winfo_height()
                if h > 640:
                    center_split.sash_place(0, 0, max(360, min(h - 260, int(h * 0.56))))
                    self._center_split_initialized = True
            except tk.TclError:
                pass
        center_split.bind("<Configure>", _init_center_split)

        self.right_scroll = ScrollFrame(body, 390)
        self.right_scroll.pack(side="right", fill="y")
        right = self.right_scroll.inner

        # panel helper
        self._mode_sidecards = []
        def card(parent, title, subtitle=None):
            f = ttk.Frame(parent, style="Card.TFrame", padding=(12, 10))
            f.pack(fill="x", pady=(0, 8))
            self._mode_sidecards.append((f, parent, title))
            head = ttk.Frame(f, style="Card.TFrame")
            head.pack(fill="x", pady=(0, 7))
            ttk.Label(head, text=title, style="Section.TLabel").pack(side="left")
            if subtitle:
                ttk.Label(head, text=subtitle, style="CardMuted.TLabel").pack(side="right")
            return f

        # ---- left: references / workflow / templates ----------------------
        f = card(left, "▶  参考動画の追加")
        mode = ttk.Frame(f, style="Card.TFrame")
        mode.pack(fill="x", pady=(0, 7))
        ttk.Button(mode, text="X / YouTube / URLから追加", command=self.on_add_reference_url).pack(side="left", fill="x", expand=True)
        ttk.Button(mode, text="＋", width=3, command=self.on_add_reference_videos).pack(side="left", padx=(5, 0))
        self.ref_url_hint = tk.StringVar(value="https://www.youtube.com/watch?v=...")
        ttk.Entry(f, textvariable=self.ref_url_hint).pack(fill="x", pady=(0, 7))
        ttk.Button(f, text="動画を取得", style="Accent.TButton", command=self.on_add_reference_url).pack(fill="x")

        f = card(left, "◉  参考動画リスト")
        self.lb_reference = tk.Listbox(f, height=7, bg="#FFFFFF", fg="#344054", selectbackground=selected,
                                       selectforeground="#101828", relief="flat", highlightthickness=1,
                                       highlightbackground=line, activestyle="none")
        self.lb_reference.pack(fill="both", expand=True)
        rb = ttk.Frame(f, style="Card.TFrame")
        rb.pack(fill="x", pady=(7, 0))
        ttk.Button(rb, text="動画を追加…", command=self.on_add_reference_videos).pack(side="left", fill="x", expand=True)
        ttk.Button(rb, text="削除", command=self.on_remove_reference_video).pack(side="left", padx=(5, 0))
        ttk.Button(f, text="テンプレート生成", style="Accent.TButton", command=self.on_make_reference_template).pack(fill="x", pady=(7, 0))
        ttk.Button(f, text="✨ 参考演出から HERO / CLEAN / HYPE を生成",
                   command=self.on_reference_remix).pack(fill="x", pady=(5, 0))
        self.lbl_reference = ttk.Label(f, text="参考動画 0本 / 未解析", style="CardMuted.TLabel", wraplength=270)
        self.lbl_reference.pack(fill="x", pady=(5, 0))

        f = card(left, "▣  テンプレート")
        self.tpl_combo = ttk.Combobox(f, state="readonly", textvariable=self.var_tpl, values=list(self.templates))
        self.tpl_combo.pack(fill="x", pady=(0, 7))
        self.tpl_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_template(self.var_tpl.get()))
        for name, cmd in [
            ("標準シネマティック", lambda: self._select_template_by_text("標準")),
            ("LoLnam風シネマ", lambda: self._select_template_by_text("LoLnam")),
            ("自動カメラモーション", lambda: self._select_template_by_text("自動")),
            ("ダイナミックアクション", lambda: self._select_template_by_text("ダイナミック")),
            ("マルチキル向け", lambda: self._select_template_by_text("マルチ")),
        ]:
            ttk.Button(f, text="◆  " + name, command=cmd).pack(fill="x", pady=2)
        ttk.Button(f, text="＋  新しいテンプレート", command=self.on_make_reference_template).pack(fill="x", pady=(5, 0))

        f = card(left, "1  リプレイ準備")
        ttk.Button(f, text="① Replay APIを自動設定", command=self.on_fix_cfg).pack(fill="x", pady=2)
        ttk.Button(f, text="② リプレイ（.rofl）を開く", command=self.on_open_replay).pack(fill="x", pady=2)
        self.cb_recent = ttk.Combobox(f, state="readonly", values=[p.name for p in paths.list_replays()[:30]])
        self.cb_recent.pack(fill="x", pady=2)
        ttk.Button(f, text="最近のリプレイを再生", command=self.on_play_recent).pack(fill="x", pady=2)
        ttk.Label(f, text="APIキー不要。game.cfgを自動設定します。", style="CardMuted.TLabel", wraplength=270).pack(fill="x", pady=(4, 0))

        f = card(left, "2  対象プレイヤー")
        ttk.Button(f, text="接続して10人を取得", command=self.on_connect).pack(fill="x", pady=(0, 5))
        self.tree = ttk.Treeview(f, columns=("team", "champ", "name"), show="headings", height=8, selectmode="browse")
        for c, t, w in (("team", "チーム", 55), ("champ", "チャンピオン", 95), ("name", "プレイヤー", 125)):
            self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="w")
        self.tree.tag_configure("ORDER", background="#EFF6FF", foreground="#1E3A8A")
        self.tree.tag_configure("CHAOS", background="#FFF1F2", foreground="#9F1239")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.on_lock())
        ttk.Button(f, text="この人を対象にする", command=self.on_lock).pack(fill="x", pady=(5, 3))
        self.lbl_lock = ttk.Label(f, text="対象: 未選択", style="CardMuted.TLabel")
        self.lbl_lock.pack(fill="x")

        f = card(left, "3  キル・アシストを探す")
        ttk.Label(f, text="検出対象", style="CardMuted.TLabel").pack(anchor="w", pady=(0, 3))
        ttk.Combobox(f, state="readonly", textvariable=self.var_event_mode,
                     values=["キル", "アシスト", "キル＋アシスト"]).pack(fill="x", pady=(0, 5))
        ttk.Button(f, text="全編スキャン", command=self.on_scan).pack(fill="x")
        self.pb_scan = ttk.Progressbar(f, maximum=100); self.pb_scan.pack(fill="x", pady=6)
        self.lbl_scan = ttk.Label(f, text="まだスキャンしていません", style="CardMuted.TLabel", wraplength=270)
        self.lbl_scan.pack(fill="x")

        # ---- center: preview / timeline / camera --------------------------
        preview_card = ttk.Frame(preview_host, style="Card.TFrame", padding=(10, 10))
        preview_card.pack(fill="both", expand=True, pady=(0, 8))
        ph = ttk.Frame(preview_card, style="Card.TFrame")
        ph.pack(fill="x", pady=(0, 7))
        ttk.Label(ph, text="カメラプレビュー", style="Section.TLabel").pack(side="left")
        self.preview_badge = ttk.Label(ph, text="三人称カメラ（対象: 追従）", style="CardMuted.TLabel")
        self.preview_badge.pack(side="right")

        self.var_live = tk.BooleanVar(value=True)
        self.var_split = tk.DoubleVar(value=0.0)
        self.var_mirror = tk.BooleanVar(value=False)
        tools = ttk.Frame(preview_card, style="Card.TFrame")
        tools.pack(fill="x", pady=(0, 7))
        ttk.Button(tools, text="ミラー ON / OFF", command=self.on_mirror_toggle).pack(side="left")
        ttk.Checkbutton(tools, text="編集中の見た目を反映", variable=self.var_live).pack(side="left", padx=10)
        ttk.Button(tools, text="▶ 再生", style="Accent.TButton", command=self.on_preview_play).pack(side="right", padx=4)
        ttk.Button(tools, text="■ 停止", command=self.on_preview_stop).pack(side="right", padx=4)
        ttk.Button(tools, text="1枚だけ更新", command=self.on_exact_still).pack(side="right", padx=4)

        self.canvas = tk.Canvas(preview_card, bg="#111827", width=760, height=360, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        ttk.Label(preview_card, text="上：LoLミラー / 下：編集設定　　↕ 境界をドラッグして表示領域を上下調整",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(4,0))

        player_bar = ttk.Frame(preview_card, style="Card.TFrame", padding=(4, 5, 4, 0))
        player_bar.pack(fill="x")
        ttk.Label(player_bar, text="00:12.4 / 00:32.0", style="CardMuted.TLabel").pack(side="left")
        ttk.Label(player_bar, text="━━━━━━━━━━━━━━━━━━━━━━━━", style="CardMuted.TLabel").pack(side="left", padx=12)
        ttk.Label(player_bar, text="🔊 LoL音声のみ   144Hzプレビュー   ⛶   ⚙", style="CardMuted.TLabel").pack(side="right")

        split_hint = ttk.Frame(edit_host, style="Card.TFrame")
        split_hint.pack(fill="x", padx=8, pady=(5, 0))
        ttk.Label(split_hint, text="編集エリア　↕ 上下にドラッグして高さを変更　／　ミラーは上段に固定表示", style="CardMuted.TLabel").pack(anchor="center")

        easy = ttk.Frame(center_edit, style="Card.TFrame", padding=(12, 10))
        self._mode_easy_section = easy
        easy.pack(fill="x", pady=(5, 8))
        eh = ttk.Frame(easy, style="Card.TFrame"); eh.pack(fill="x")
        ttk.Label(eh, text="★ かんたん作成", style="Section.TLabel").pack(side="left")
        ttk.Label(eh, text="難しい設定は後から変更できます", style="CardMuted.TLabel").pack(side="right")
        ttk.Label(easy, text="① リプレイを開く → ② 対象プレイヤーを選ぶ → ③ ボタン1つでキル/アシストを検出して動画を作成", style="CardMuted.TLabel", wraplength=900).pack(anchor="w", pady=(4, 7))
        ttk.Button(easy, text="★ これで自動作成（おすすめ）", style="Accent.TButton", command=self.on_one_click).pack(fill="x", ipady=4)
        ttk.Button(easy, text="✨ スマート自動編集：全シーンに個別カメラ演出 → 作成", command=self.on_smart_one_click).pack(fill="x", pady=(4,0))
        quick_presets = ttk.Frame(easy, style="Card.TFrame")
        quick_presets.pack(fill="x", pady=(10, 3))
        ttk.Label(quick_presets, text="仕上がり", style="Card.TLabel").pack(side="left", padx=(0, 6))
        for title, key in (("自然", "三人称 自然め"),
                           ("シネマ", "Lolnam風スムーズ"),
                           ("ダイナミック", "Lolnam風ダイナミック")):
            ttk.Button(quick_presets, text=title,
                       command=lambda k=key: self._choose_easy_preset(k)).pack(side="left", padx=3, fill="x", expand=True)
        self.lbl_easy_preset = ttk.Label(easy, textvariable=self.var_tpl, style="CardMuted.TLabel")
        self.lbl_easy_preset.pack(anchor="w", pady=(0, 3))
        ttk.Checkbutton(easy, text="自動ディレクター：キル数に合わせてカメラ演出を自動調整（任意）",
                        variable=self.var_auto_director).pack(anchor="w", pady=(6, 1))
        ttk.Label(easy, text="ONなら自動作成前に既存のOrbit/ドリー設定を調整します。OFFでは以前の挙動のまま。",
                  style="CardMuted.TLabel").pack(anchor="w")

        self._mode_detail_sections = []
        timeline = ttk.Frame(center_edit, style="Card.TFrame", padding=(12, 10))
        self._mode_detail_sections.append(timeline)
        timeline.pack(fill="x", pady=(0, 8))
        ttk.Label(timeline, text="◈  カメラ動作タイムライン", style="Section.TLabel").pack(anchor="w")
        self.scene_timeline = SceneTimeline(timeline, self.var_pre, self.var_post)
        self.scene_timeline.pack(fill="x", pady=(5, 4))
        ttk.Label(timeline, text="左・右のハンドルをドラッグ。下の「基本」タブのキル前/後（秒）と連動します。", style="CardMuted.TLabel").pack(anchor="w")
        # Per-scene direction controls live in the center editor (GPU code unchanged).
        scene_card = ttk.Frame(center_edit, style="Card.TFrame", padding=(12, 10))
        self._mode_detail_sections.append(scene_card)
        scene_card.pack(fill="x", pady=(0, 8))
        ttk.Label(scene_card, text="◈ シーン別ディレクター / 編集プロジェクト", style="Section.TLabel").pack(anchor="w")
        ttk.Checkbutton(scene_card, text="シーン別演出を使用（各クリップにカメラ設定を反映）",
                        variable=self.var_scene_mode).pack(anchor="w", pady=(5, 2))
        ttk.Label(scene_card, text="右の検出シーンを選ぶ → 値を調整 →『このシーンに保存』。三人称はLolnam風カメラへ切替、FPS/俯瞰はそのまま。",
                  style="CardMuted.TLabel", wraplength=770).pack(anchor="w")
        self.scene_selected_label = ttk.Label(scene_card, text="シーン未選択（スキャン後に右の一覧を選択）", style="Card.TLabel")
        self.scene_selected_label.pack(anchor="w", pady=(6,3))
        thumbs = ttk.Frame(scene_card, style="Card.TFrame")
        thumbs.pack(fill="x", pady=(2,6))
        self.scene_thumbnail = ttk.Label(thumbs, text="サムネイル未保存", style="CardMuted.TLabel")
        self.scene_thumbnail.pack(side="left", padx=(0,8))
        thumb_buttons = ttk.Frame(thumbs, style="Card.TFrame")
        thumb_buttons.pack(side="left", fill="x", expand=True)
        ttk.Button(thumb_buttons, text="選択シーンへ移動", command=self.on_jump_selected).pack(anchor="w", pady=2)
        ttk.Button(thumb_buttons, text="ミラーの現在画面をサムネイルに保存", command=self.on_capture_scene_thumbnail).pack(anchor="w", pady=2)
        ttk.Label(thumb_buttons, text="移動後にミラーを確認して保存。自動で別の場面を撮影しません。",
                  style="CardMuted.TLabel", wraplength=480).pack(anchor="w")
        self._scene_thumbnail_photo = None
        sr = ttk.Frame(scene_card, style="Card.TFrame"); sr.pack(fill="x", pady=2)
        self.var_shot_profile = tk.StringVar(value="cinematic")
        ttk.Label(sr, text="動き", style="Card.TLabel").pack(side="left")
        ttk.Combobox(sr, textvariable=self.var_shot_profile, state="readonly", width=13,
                     values=["auto", "smooth", "cinematic", "dynamic"]).pack(side="left", padx=(4,10))
        self.var_shot_intensity = tk.StringVar(value="standard")
        ttk.Label(sr, text="演出強度", style="Card.TLabel").pack(side="left")
        ttk.Combobox(sr, textvariable=self.var_shot_intensity, state="readonly", width=12,
                     values=["natural", "standard", "strong"]).pack(side="left", padx=(4,10))
        self.scene_vars = {}
        for title,key,lo,hi,initial in (("Orbit°", "arc",0,75,10),("Dolly%","dolly",0,15,3),
                                         ("Yaw°","yaw",-180,180,0),("キル前s","pre",1,15,4),
                                         ("キル後s","post",1,15,3)):
            self.scene_vars[key] = tk.DoubleVar(value=initial)
            segment=ttk.Frame(scene_card, style="Card.TFrame");segment.pack(fill="x",pady=1)
            ttk.Label(segment, text=title, width=12, style="Card.TLabel").pack(side="left")
            ttk.Scale(segment, variable=self.scene_vars[key], from_=lo, to=hi).pack(side="left", fill="x", expand=True, padx=(0,6))
            ttk.Spinbox(segment, from_=lo,to=hi,increment=0.5,textvariable=self.scene_vars[key],width=7).pack(side="right")
        self.shot_motion_graph=ShotMotionGraph(scene_card, self._scene_shot_from_ui)
        self.shot_motion_graph.pack(fill="x",pady=(5,2))

        # v5.9.2: Optional camera keyframe lane, relative to the kill event.
        kf_head = ttk.Frame(scene_card, style="Card.TFrame"); kf_head.pack(fill="x", pady=(8,3))
        ttk.Label(kf_head, text="◈ カメラキーフレーム（キル瞬間 = 0秒）", style="Section.TLabel").pack(side="left")
        ttk.Label(scene_card, text="回転・寄り・FOVの補正値。空なら従来の自動カメラ。変更後は『このシーンに保存』で確定。",
                  style="CardMuted.TLabel", wraplength=760).pack(anchor="w")
        self._edit_keyframes = []
        self.kf_list = tk.Listbox(scene_card, height=4, exportselection=False,
                                  bg="#FFFFFF", fg="#172033", selectbackground="#BFDBFE", relief="flat")
        self.kf_list.pack(fill="x", pady=(3,3))
        self.kf_list.bind('<<ListboxSelect>>', self.on_keyframe_selection)
        kf_inputs = ttk.Frame(scene_card, style="Card.TFrame"); kf_inputs.pack(fill="x")
        self.kf_vars = {}
        for title, field_name, lo, hi, value in (("時刻s", "time", -15, 15, 0),
            ("回転°", "yaw", -70, 70, 0), ("寄り%", "zoom", -30, 30, 0),
            ("FOV°", "fov", -15, 15, 0)):
            ttk.Label(kf_inputs, text=title, style="Card.TLabel").pack(side="left", padx=(5,2))
            self.kf_vars[field_name] = tk.DoubleVar(value=value)
            ttk.Spinbox(kf_inputs, from_=lo, to=hi, increment=0.5,
                        textvariable=self.kf_vars[field_name], width=6).pack(side="left", padx=(0,5))
        kf_actions=ttk.Frame(scene_card,style="Card.TFrame"); kf_actions.pack(fill="x",pady=(4,4))
        ttk.Button(kf_actions,text="＋ 追加 / 選択を更新",command=self.on_keyframe_upsert).pack(side="left")
        ttk.Button(kf_actions,text="－ 選択を削除",command=self.on_keyframe_remove).pack(side="left",padx=5)
        ttk.Button(kf_actions,text="動きをプレビュー",command=self.on_keyframe_preview).pack(side="left")
        preset_actions = ttk.Frame(scene_card, style="Card.TFrame")
        preset_actions.pack(fill="x", pady=(4, 3))
        ttk.Label(preset_actions, text="キーフレームの型", style="Card.TLabel").pack(side="left", padx=(0, 6))
        for caption, pattern in (("自然な回り込み", "soft_orbit"),
                                 ("寄って戻る", "push_pull"),
                                 ("キル瞬間を強調", "impact")):
            ttk.Button(preset_actions, text=caption,
                       command=lambda p=pattern: self.on_keyframe_preset(p)).pack(side="left", padx=3)

        fx_head = ttk.Frame(scene_card,style="Card.TFrame"); fx_head.pack(fill="x",pady=(8,3))
        ttk.Label(fx_head,text="◈ シーンごとの色・エフェクト",style="Section.TLabel").pack(side="left")
        self.var_scene_fx_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(scene_card,text="このシーンだけ色・エフェクトを上書き（OFFは全体設定を引き継ぐ）",
                        variable=self.var_scene_fx_enabled).pack(anchor="w")
        self.scene_fx_vars={}
        for label,key,lo,hi,default in (("色温度", "temperature",-1,1,0),
                                       ("ブルーム", "bloom",0,1,0.25),
                                       ("Focus Blur", "focus_blur",0,1,0),
                                       ("DOFぼかし", "dof_blur",0,20,0)):
            fx_row=ttk.Frame(scene_card,style="Card.TFrame");fx_row.pack(fill="x",pady=1)
            ttk.Label(fx_row,text=label,width=14,style="Card.TLabel").pack(side="left")
            v=tk.DoubleVar(value=default);self.scene_fx_vars[key]=v
            ttk.Scale(fx_row,variable=v,from_=lo,to=hi).pack(side="left",fill="x",expand=True,padx=5)
            ttk.Spinbox(fx_row,from_=lo,to=hi,increment=0.05,textvariable=v,width=7).pack(side="left")

        for _variable in (self.var_shot_profile,self.var_shot_intensity,*self.scene_vars.values()):
            _variable.trace_add('write',lambda *_: self.shot_motion_graph.redraw())
        actions=ttk.Frame(scene_card,style="Card.TFrame");actions.pack(fill="x",pady=(7,2))
        ttk.Button(scene_card,text="全シーンの演出を自動推薦（現在のスキャン結果）", command=self.on_recommend_all).pack(fill="x",pady=3)
        for label,handler in (("このシーンに保存",self.on_save_scene),
                              ("自動演出を設定",self.on_recommend_scene),
                              ("上書きを解除",self.on_clear_scene),
                              ("元に戻す",self.on_scene_undo),
                              ("やり直す",self.on_scene_redo)):
            ttk.Button(actions,text=label,command=handler).pack(side="left",padx=(0,4))
        project_bar=ttk.Frame(scene_card,style="Card.TFrame");project_bar.pack(fill="x",pady=(3,0))
        ttk.Button(project_bar,text="編集プロジェクトを保存",command=self.on_scene_export).pack(side="left")
        ttk.Button(project_bar,text="読み込み",command=self.on_scene_import).pack(side="left",padx=5)
        ttk.Label(project_bar,text="自動保存 / Undo・Redo（最大100回） / ON時は1シーン1クリップ",style="CardMuted.TLabel").pack(side="right")
        order_header=ttk.Frame(scene_card,style="Card.TFrame")
        order_header.pack(fill="x",pady=(10,2))
        ttk.Label(order_header,text="◈ モンタージュの再生順",style="Section.TLabel").pack(side="left")
        ttk.Label(order_header,text="シーン別演出ONの場合のみ適用",style="CardMuted.TLabel").pack(side="right")
        order_body=ttk.Frame(scene_card,style="Card.TFrame");order_body.pack(fill="x")
        self.scene_order_list=tk.Listbox(order_body,height=5,exportselection=False,
                                         bg="#FFFFFF",fg="#172033",selectbackground="#BFDBFE",
                                         selectforeground="#172033",relief="flat",font=("Meiryo UI",9))
        self.scene_order_list.pack(side="left",fill="x",expand=True)
        self.scene_order_list.bind('<<ListboxSelect>>', self.on_order_selection)
        self._drag_order_index = None
        self.scene_order_list.bind('<ButtonPress-1>', self._on_order_drag_start, add='+')
        self.scene_order_list.bind('<ButtonRelease-1>', self._on_order_drag_end, add='+')
        order_buttons=ttk.Frame(order_body,style="Card.TFrame");order_buttons.pack(side="right",padx=(7,0))
        ttk.Button(order_buttons,text="▲ 上へ",command=lambda:self.on_move_scene(-1)).pack(fill="x",pady=(0,4))
        ttk.Button(order_buttons,text="▼ 下へ",command=lambda:self.on_move_scene(1)).pack(fill="x",pady=(0,4))
        ttk.Button(order_buttons,text="時刻順に戻す",command=self.on_reset_scene_order).pack(fill="x")
        ttk.Label(scene_card,text="ドラッグまたは▲▼で順序変更。プロジェクトJSONに保存され、Undo/Redoできます。",
                  style="CardMuted.TLabel",wraplength=760).pack(anchor="w",pady=(4,0))

        cam = ttk.Frame(center_edit, style="Card.TFrame", padding=(12, 10))
        self._mode_detail_sections.append(cam)
        cam.pack(fill="x", pady=(0, 8))
        ttk.Label(cam, text="◈  カメラ設定", style="Section.TLabel").pack(anchor="w", pady=(0, 7))
        mode_row = ttk.Frame(cam, style="Card.TFrame"); mode_row.pack(fill="x", pady=(0, 7))
        ttk.Label(mode_row, text="カメラモード", width=11, style="Card.TLabel").pack(side="left")
        self.mode_buttons = []
        # ここは見た目だけのモード切替ではなく、既存の var_style に直接接続する。
        camera_modes = (("♟ 三人称（通常）", "third"), ("♟ 三人称（シネマ）", "third_cinema"),
                        ("▣ FPS風", "fps"), ("◉ Lolnamシネマ", "lolnam_cinema"))
        for text, val in camera_modes:
            b = ttk.Button(mode_row, text=text,
                           command=lambda v=val: (self.var_style.set(STYLES[v]), self.log(f"カメラスタイル: {STYLES[v]}")))
            b.pack(side="left", padx=3, fill="x", expand=True)
            self.mode_buttons.append(b)
        ttk.Button(cam, text="↺ 追従カメラを安定設定に戻す（高さ・距離・Yawのみ）",
                   command=self.on_camera_safe_pose).pack(fill="x", pady=(1, 8))

        target_row = ttk.Frame(cam, style="Card.TFrame"); target_row.pack(fill="x", pady=3)
        ttk.Label(target_row, text="カメラの追従対象", width=11, style="Card.TLabel").pack(side="left")
        ttk.Button(target_row, text="◉  キル対象（自動）", command=lambda: self.log("追従対象: キル対象（自動）")).pack(side="left", fill="x", expand=True)
        ttk.Button(target_row, text="▶  対象を手動指定", command=self.on_lock).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # all existing camera sliders remain available in the center
        self.sl, self.sl_labels = {}, {}
        def _slider_range(key):
            return {
                "grade_strength": (0, 1.4), "temperature": (-1, 1), "contrast": (0.6, 1.6),
                "exposure": (-0.3, 0.3), "vibrance": (-1, 1.5), "vignette": (0, 1),
                "grain": (0, 1), "bloom": (0, 1), "bars": (0, 1), "fog_strength": (0, 1),
                "dist_scale": (0.3, 1.0), "cam_height": (0, 900), "third_elev": (10, 50),
                "third_dist": (500, 1400), "third_yaw": (-180, 180), "motion_arc": (0, 45),
                "motion_dolly": (0, 15), "game_volume": (0, 1.5), "bgm_volume": (0, 1.0),
                "dof_blur": (0, 12), "dof_focus_distance": (500, 12000),
                "dof_near_distance": (100, 20000), "dof_far_distance": (100, 20000),
            }.get(key, (0, 1))
        self._slider_range = _slider_range
        def slider(parent, key, label, lo, hi, compact=False):
            row = ttk.Frame(parent, style="Card.TFrame"); row.pack(fill="x", pady=3)
            ttk.Label(row, text=label, width=15 if not compact else 13, style="Card.TLabel").pack(side="left")
            v = tk.DoubleVar()
            sc = ttk.Scale(row, from_=lo, to=hi, variable=v)
            sc.pack(side="left", fill="x", expand=True, padx=4)
            ent = ttk.Entry(row, textvariable=v, width=8, justify="right")
            ent.pack(side="right")
            self.sl[key] = v; self.sl_labels[key] = ent

        cam_grid = ttk.Frame(cam, style="Card.TFrame")
        cam_grid.pack(fill="x")
        left_cam = ttk.Frame(cam_grid, style="Card.TFrame"); left_cam.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right_cam = ttk.Frame(cam_grid, style="Card.TFrame"); right_cam.pack(side="left", fill="both", expand=True)
        ttk.Label(left_cam, text="追従設定", style="Card.TLabel", font=("Meiryo UI", 10, "bold")).pack(anchor="w", pady=(0, 3))
        slider(left_cam, "dist_scale", "追従距離", 0.3, 1.0)
        slider(left_cam, "cam_height", "高さ", 0, 900)
        slider(left_cam, "third_elev", "仰角", 10, 50)
        ttk.Checkbutton(left_cam, text="常に対象を画面中央に表示", variable=tk.BooleanVar(value=True)).pack(anchor="w", pady=(4, 0))
        ttk.Label(right_cam, text="Orbit（横回転）", style="Card.TLabel", font=("Meiryo UI", 10, "bold")).pack(anchor="w", pady=(0, 3))
        slider(right_cam, "third_dist", "三人称 距離", 500, 1400)
        slider(right_cam, "third_yaw", "回転角", -180, 180)
        slider(right_cam, "motion_arc", "自動Orbit角", 0, 45)
        slider(right_cam, "motion_dolly", "自動ドリー", 0, 15)
        yawbar = ttk.Frame(right_cam, style="Card.TFrame"); yawbar.pack(fill="x", pady=2)
        ttk.Button(yawbar, text="↶ -90°", command=lambda: self.sl["third_yaw"].set(max(-180, self.sl["third_yaw"].get()-90))).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(yawbar, text="0°", command=lambda: self.sl["third_yaw"].set(0)).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(yawbar, text="+90° ↷", command=lambda: self.sl["third_yaw"].set(min(180, self.sl["third_yaw"].get()+90))).pack(side="left", expand=True, fill="x", padx=(2, 0))

        motion = ttk.Frame(cam, style="Card.TFrame", padding=(0, 8, 0, 0)); motion.pack(fill="x")
        ttk.Label(motion, text="自動カメラモーション", style="Card.TLabel", font=("Meiryo UI", 10, "bold")).pack(anchor="w")
        self.var_motion_profile = tk.StringVar(value="Cinematic（Lolnam風）")
        self.cb_motion_profile = ttk.Combobox(motion, state="readonly", textvariable=self.var_motion_profile,
                                               values=["Smooth（自然）", "Cinematic（Lolnam風）", "Dynamic（大きく動く）", "Auto（キル数で自動）"])
        self.cb_motion_profile.pack(fill="x", pady=4)
        self._motion_profile_jp = {"smooth":"Smooth（自然）", "cinematic":"Cinematic（Lolnam風）", "dynamic":"Dynamic（大きく動く）", "auto":"Auto（キル数で自動）"}
        self._motion_profile_rev = {v:k for k,v in self._motion_profile_jp.items()}
        ttk.Label(motion, text="キル前→瞬間→終了を自動補間。Lolnam風は水平Orbit＋ドリーを使用。", style="CardMuted.TLabel").pack(anchor="w")
        preset_row = ttk.Frame(motion, style="Card.TFrame"); preset_row.pack(fill="x", pady=(5, 0))
        for caption, profile, arc, dolly in (("自然", "smooth", 8.0, 2.0),
                                              ("シネマ", "cinematic", 14.0, 5.0),
                                              ("ダイナミック", "dynamic", 22.0, 8.0)):
            ttk.Button(preset_row, text=caption,
                       command=lambda p=profile,a=arc,d=dolly: self._set_camera_motion(p,a,d)).pack(side="left", fill="x", expand=True, padx=3)
        ttk.Label(motion, text="カメラの簡単設定：既存のOrbit/ドリー/モーションプロファイルに反映します。",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(3, 0))

        # Keep existing advanced controls reachable below the main camera card.
        advanced = ttk.Frame(center_edit, style="Card.TFrame", padding=(12, 10))
        self._mode_detail_sections.append(advanced)
        advanced.pack(fill="x", pady=(0, 8))
        ttk.Label(advanced, text="詳細編集", style="Section.TLabel").pack(anchor="w")
        nb = ttk.Notebook(advanced); nb.pack(fill="x", pady=(7, 0))
        basic = ttk.Frame(nb, padding=8, style="Card.TFrame")
        color = ttk.Frame(nb, padding=8, style="Card.TFrame")
        output = ttk.Frame(nb, padding=8, style="Card.TFrame")
        nb.add(basic, text="基本")
        nb.add(color, text="カラー・FX")
        nb.add(output, text="録画・出力")

        ttk.Label(basic, text="テンプレート", style="Card.TLabel").pack(anchor="w")
        self.cb_tpl_quick = ttk.Combobox(basic, state="readonly", textvariable=self.var_tpl, values=list(self.templates))
        self.cb_tpl_quick.pack(fill="x", pady=3)
        self.cb_tpl_quick.bind("<<ComboboxSelected>>", lambda _e: self.apply_template(self.var_tpl.get()))
        ttk.Label(basic, text="演出の強さ", style="Card.TLabel").pack(anchor="w", pady=(5, 2))
        int_row = ttk.Frame(basic, style="Card.TFrame"); int_row.pack(fill="x", pady=(0, 4))
        for key, label in INTENSITY_JP.items():
            ttk.Radiobutton(int_row, text=label, value=key, variable=self.var_int).pack(side="left", padx=(0, 12))
        ttk.Label(basic, text="カメラスタイル", style="Card.TLabel").pack(anchor="w", pady=(7, 2))
        # 実際のテンプレートに接続されたコンボだけを表示（見た目だけの重複UIは作らない）。
        style_cb = ttk.Combobox(basic, state="readonly", textvariable=self.var_style, values=list(STYLES.values()))
        style_cb.pack(fill="x", pady=(0, 4))
        ttk.Label(basic, text="タイトル（空欄なら表示なし）", style="Card.TLabel").pack(anchor="w", pady=(4, 2))
        self.var_title = tk.StringVar(); ttk.Entry(basic, textvariable=self.var_title).pack(fill="x")
        ttk.Label(basic, text="キル前 / キル後（秒）", style="Card.TLabel").pack(anchor="w", pady=(6, 2))
        pr=ttk.Frame(basic, style="Card.TFrame"); pr.pack(fill="x")
        ttk.Spinbox(pr, from_=1, to=15, increment=0.5, width=7, textvariable=self.var_pre).pack(side="left")
        ttk.Label(pr, text=" / ", style="Card.TLabel").pack(side="left")
        ttk.Spinbox(pr, from_=1, to=15, increment=0.5, width=7, textvariable=self.var_post).pack(side="left")
        self.var_merge=tk.BooleanVar(value=True)
        ttk.Checkbutton(basic, text="連続キルは1本にまとめる", variable=self.var_merge).pack(anchor="w", pady=6)
        ttk.Button(basic, text="★ この設定で全自動作成", style="Accent.TButton", command=self.on_one_click).pack(fill="x", pady=(4, 0))

        self.var_grade = tk.StringVar()
        ttk.Label(color, text="カラーグレード", style="Card.TLabel").pack(anchor="w")
        ttk.Combobox(color, state="readonly", textvariable=self.var_grade, values=list(GRADE_JP.values())).pack(fill="x", pady=3)
        for args in (("grade_strength","色の強さ",0,1.4),("temperature","色温度",-1,1),("contrast","コントラスト",0.6,1.6),("exposure","露出",-0.3,0.3),("vibrance","自然な彩度",-1,1.5),("vignette","ビネット",0,1),("grain","グレイン",0,1),("bloom","ブルーム",0,1),("bars","シネマ枠",0,1)):
            slider(color,*args)
        self.var_fog=tk.BooleanVar(value=False); ttk.Checkbutton(color, text="Fogを有効化", variable=self.var_fog).pack(anchor="w", pady=(6,2))
        self.var_fog_preset=tk.StringVar(value="Teal"); ttk.Combobox(color, state="readonly", textvariable=self.var_fog_preset, values=list(FOG_PRESETS.values())).pack(fill="x")
        slider(color,"fog_strength","Fog強度",0,1)
        self.fog_viz = FogViz(color, self.sl["fog_strength"])
        self.fog_viz.pack(fill="x", pady=(0,4))
        self.var_curve=tk.BooleanVar(value=False); ttk.Checkbutton(color, text="カーブ補正を有効化（lolnam系）", variable=self.var_curve).pack(anchor="w", pady=(6,2))
        self.var_curve_points=tk.StringVar(value="0/0 0.25/0.20 0.50/0.50 0.75/0.80 1/1")
        curve_head = ttk.Frame(color, style="Card.TFrame"); curve_head.pack(fill="x", pady=(4,2))
        ttk.Label(curve_head, text="トーンカーブ（LoLnam風）", style="CardMuted.TLabel").pack(side="left")
        ttk.Button(curve_head, text="Reset", command=lambda: self.curve_editor.reset()).pack(side="right")
        self.curve_editor = CurveEditor(color, self.var_curve_points, self.var_curve_points.get(), height=230)
        self.curve_editor.pack(fill="x", pady=(0,4))
        ttk.Label(color, text="点をクリックで追加 / ドラッグで移動。数値は x/y（0.000〜1.000）で入力できます。",
                  style="CardMuted.TLabel", wraplength=560).pack(anchor="w")
        ttk.Entry(color, textvariable=self.var_curve_points).pack(fill="x", pady=(4,0))
        self.var_dof=tk.BooleanVar(value=False); ttk.Checkbutton(color, text="被写界深度 DOF", variable=self.var_dof).pack(anchor="w", pady=5)
        slider(color,"dof_blur","DOFぼかし",0,12)
        slider(color,"dof_focus_distance","フォーカス距離",500,12000)
        slider(color,"dof_near_distance","近距離",100,20000)
        slider(color,"dof_far_distance","遠距離",100,20000)
        ttk.Label(color, text="DOFフォーカス範囲（概念プレビュー）", style="CardMuted.TLabel").pack(anchor="w", pady=(5,2))
        self.dof_viz = DofViz(color, self.sl["dof_blur"], self.sl["dof_focus_distance"], self.sl["dof_near_distance"], self.sl["dof_far_distance"])
        self.dof_viz.pack(fill="x", pady=(0,4))

        # Premiere/AE系の演出。難しい編集を覚えなくても、チェックを入れるだけで使える。
        fx_box = ttk.LabelFrame(color, text="映像演出（チェックするだけでOK）", padding=8)
        fx_box.pack(fill="x", pady=(8, 0))
        fx_top = ttk.Frame(fx_box, style="Card.TFrame"); fx_top.pack(fill="x", pady=(0, 5))
        ttk.Label(fx_top, text="演出プリセット", style="Card.TLabel").pack(side="left")
        self.var_effect_preset = tk.StringVar(value="なし")
        self.cb_effect_preset = ttk.Combobox(fx_top, state="readonly", textvariable=self.var_effect_preset,
                                              values=["なし", "キル瞬間", "カメラ演出", "VHS / Glitch", "シネマ", "全部控えめ"])
        self.cb_effect_preset.pack(side="left", fill="x", expand=True, padx=8)
        self.cb_effect_preset.bind("<<ComboboxSelected>>", lambda _e: self._apply_effect_preset(self.var_effect_preset.get()))
        ttk.Label(fx_box, text="各エフェクトはON/OFFと強さを個別に変更できます。迷ったらプリセットだけでOK。",
                  style="CardMuted.TLabel", wraplength=560).pack(anchor="w", pady=(0, 6))
        self.effect_vars = {}
        self.effect_strength_vars = {}
        for category, items in VIDEO_EFFECT_CATEGORIES.items():
            sec = ttk.LabelFrame(fx_box, text=category, padding=5)
            sec.pack(fill="x", pady=3)
            for col in range(2):
                sec.columnconfigure(col, weight=1)
            for i, (key, label) in enumerate(items):
                row_idx, col_idx = divmod(i, 2)
                cell = ttk.Frame(sec, style="Card.TFrame"); cell.grid(row=row_idx, column=col_idx, sticky="ew", padx=4, pady=2)
                var = tk.BooleanVar(value=False); sval = tk.DoubleVar(value=float(VIDEO_EFFECT_DEFAULTS.get(key, 0.25)))
                self.effect_vars[key] = var; self.effect_strength_vars[key] = sval
                ttk.Checkbutton(cell, text=label, variable=var).pack(side="left")
                ttk.Scale(cell, from_=0.05, to=1.0, variable=sval, length=70).pack(side="left", fill="x", expand=True, padx=4)
                ttk.Entry(cell, textvariable=sval, width=5, justify="right").pack(side="right")
        ttk.Button(fx_box, text="全エフェクトOFF", command=self._clear_video_effects).pack(fill="x", pady=(5, 0))

        self.var_tr=tk.StringVar(); ttk.Label(output, text="切替", style="Card.TLabel").pack(anchor="w")
        ttk.Combobox(output, state="readonly", textvariable=self.var_tr, values=list(TRANSITIONS.values())).pack(fill="x", pady=3)
        self.var_gaudio=tk.BooleanVar(value=True); ttk.Checkbutton(output, text="LoLの音だけを優先して録音", variable=self.var_gaudio).pack(anchor="w", pady=4)
        self.lbl_gpu = ttk.Label(output, text="GPU優先: NVIDIA / NVENC を確認中…", style="CardMuted.TLabel", wraplength=520)
        self.lbl_gpu.pack(anchor="w", pady=(2,4))
        self.root.after(200, self._refresh_gpu_status)
        ttk.Label(output, text="プレビュー/カメラ制御は最大144Hz。最終MP4は1080p・60fpsを標準。", style="CardMuted.TLabel", wraplength=520).pack(anchor="w", pady=(0,4))
        self.var_montage=tk.BooleanVar(value=True); ttk.Checkbutton(output, text="最後に全キルを1本へ連結", variable=self.var_montage).pack(anchor="w", pady=4)
        ttk.Label(output, text="BGM（任意）", style="Card.TLabel").pack(anchor="w", pady=(5,2))
        self.var_bgm=tk.StringVar(); rb=ttk.Frame(output, style="Card.TFrame"); rb.pack(fill="x")
        ttk.Button(rb, text="選択", command=lambda:self._pick(self.var_bgm,[('音声','*.mp3 *.wav *.m4a *.aac')])).pack(side="left")
        ttk.Label(rb, textvariable=self.var_bgm, style="CardMuted.TLabel").pack(side="left", padx=5)
        ttk.Label(output, text="LUT（任意）", style="Card.TLabel").pack(anchor="w", pady=(5,2))
        self.var_lut=tk.StringVar(); rl=ttk.Frame(output, style="Card.TFrame"); rl.pack(fill="x")
        ttk.Button(rl, text="選択", command=lambda:self._pick(self.var_lut,[('LUT','*.cube')])).pack(side="left")
        ttk.Label(rl, textvariable=self.var_lut, style="CardMuted.TLabel").pack(side="left", padx=5)
        slider(output,"game_volume","ゲーム音量",0,1.5)
        slider(output,"bgm_volume","BGM音量",0,1.0)
        ttk.Label(output, text="出力先", style="Card.TLabel").pack(anchor="w", pady=(5,2))
        self.lbl_out=ttk.Label(output, text=str(self.out_root), style="CardMuted.TLabel", wraplength=560); self.lbl_out.pack(fill="x")
        ttk.Button(output, text="出力フォルダを変更", command=self.on_pick_out).pack(fill="x", pady=3)
        ttk.Button(output, text="出力フォルダを開く", command=self.on_open_out).pack(fill="x")

        # right: cinematic settings / output / kill list --------------------
        # 右パネルにも元版の数値コントロールを常時表示する。
        # Notebook内だけに置くと、白UIでは「機能が消えた」ように見えるため、
        # 同じ DoubleVar を共有して、どちらから動かしても即時反映されるようにする。
        f = card(right, "◈  カラー・FX")
        ttk.Label(f, text="カラーグレード", style="Card.TLabel").pack(anchor="w")
        ttk.Combobox(f, state="readonly", textvariable=self.var_grade,
                     values=list(GRADE_JP.values())).pack(fill="x", pady=(3, 5))

        # 旧版に存在したカラー数値バーを復元
        for key, label in (("grade_strength", "色の強さ"), ("temperature", "色温度"),
                           ("contrast", "コントラスト"), ("exposure", "露出"),
                           ("vibrance", "自然な彩度"), ("vignette", "ビネット"),
                           ("grain", "グレイン"), ("bloom", "ブルーム"),
                           ("bars", "シネマ枠")):
            row = ttk.Frame(f, style="Card.TFrame"); row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=11, style="Card.TLabel").pack(side="left")
            ttk.Scale(row, from_=self._slider_range(key)[0], to=self._slider_range(key)[1],
                      variable=self.sl[key]).pack(side="left", fill="x", expand=True, padx=4)
            ttk.Entry(row, textvariable=self.sl[key], width=9, justify="right").pack(side="right")

        fx_row = ttk.Frame(f, style="Card.TFrame"); fx_row.pack(fill="x", pady=(4, 0))
        ttk.Checkbutton(fx_row, text="Fog", variable=self.var_fog).pack(side="left")
        ttk.Checkbutton(fx_row, text="カーブ", variable=self.var_curve).pack(side="left", padx=8)
        ttk.Checkbutton(fx_row, text="DOF", variable=self.var_dof).pack(side="left")
        ttk.Label(f, text="Fogプリセット", style="CardMuted.TLabel").pack(anchor="w", pady=(6, 2))
        ttk.Combobox(f, state="readonly", textvariable=self.var_fog_preset,
                     values=list(FOG_PRESETS.values())).pack(fill="x")
        row = ttk.Frame(f, style="Card.TFrame"); row.pack(fill="x", pady=2)
        ttk.Label(row, text="Fog強度", width=11, style="Card.TLabel").pack(side="left")
        ttk.Scale(row, from_=0, to=1, variable=self.sl["fog_strength"]).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Label(row, textvariable=self.sl_labels["fog_strength"], width=7, anchor="e", style="CardMuted.TLabel").pack(side="right")
        ttk.Label(f, text="カーブ補正ポイント", style="CardMuted.TLabel").pack(anchor="w", pady=(5, 2))
        ttk.Entry(f, textvariable=self.var_curve_points).pack(fill="x")
        ttk.Label(f, text="DOF詳細", style="CardMuted.TLabel").pack(anchor="w", pady=(6, 2))
        for key, label in (("dof_blur", "DOFぼかし"), ("dof_focus_distance", "フォーカス距離"),
                           ("dof_near_distance", "近距離"), ("dof_far_distance", "遠距離")):
            row = ttk.Frame(f, style="Card.TFrame"); row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=11, style="Card.TLabel").pack(side="left")
            lo, hi = self._slider_range(key)
            ttk.Scale(row, from_=lo, to=hi, variable=self.sl[key]).pack(side="left", fill="x", expand=True, padx=4)
            ttk.Entry(row, textvariable=self.sl[key], width=9, justify="right").pack(side="right")

        f = card(right, "◈  カメラ詳細")
        ttk.Label(f, text="カメラ距離 / 高さ / Orbit", style="Card.TLabel").pack(anchor="w")
        for key, label in (("dist_scale", "追従距離"), ("cam_height", "高さ"),
                           ("third_elev", "三人称 仰角"), ("third_dist", "三人称 距離"),
                           ("third_yaw", "Orbit回転"), ("motion_arc", "自動Orbit角"),
                           ("motion_dolly", "自動ドリー")):
            row = ttk.Frame(f, style="Card.TFrame"); row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=11, style="Card.TLabel").pack(side="left")
            lo, hi = self._slider_range(key)
            ttk.Scale(row, from_=lo, to=hi, variable=self.sl[key]).pack(side="left", fill="x", expand=True, padx=4)
            ttk.Entry(row, textvariable=self.sl[key], width=9, justify="right").pack(side="right")
        yawbar2 = ttk.Frame(f, style="Card.TFrame"); yawbar2.pack(fill="x", pady=(2, 0))
        ttk.Button(yawbar2, text="↶ -90°", command=lambda: self.sl["third_yaw"].set(max(-180, self.sl["third_yaw"].get()-90))).pack(side="left", expand=True, fill="x", padx=(0,2))
        ttk.Button(yawbar2, text="0°", command=lambda: self.sl["third_yaw"].set(0)).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(yawbar2, text="+90° ↷", command=lambda: self.sl["third_yaw"].set(min(180, self.sl["third_yaw"].get()+90))).pack(side="left", expand=True, fill="x", padx=(2,0))

        f = card(right, "◈  LoLnam風シネマ")
        top_switch = ttk.Frame(f, style="Card.TFrame"); top_switch.pack(fill="x")
        ttk.Label(top_switch, text="シネマティックテンプレート", style="Card.TLabel").pack(side="left")
        self.var_cinema = tk.BooleanVar(value=True)
        ttk.Checkbutton(top_switch, text="ON", variable=self.var_cinema).pack(side="right")
        ttk.Combobox(f, state="readonly", textvariable=self.var_tpl, values=list(self.templates)).pack(fill="x", pady=5)
        ttk.Label(f, text="カメラ演出", style="Card.TLabel", font=("Meiryo UI", 10, "bold")).pack(anchor="w", pady=(3,2))
        self.var_preback=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="キル前：少し戻る", variable=self.var_preback).pack(anchor="w")
        self.var_orbit=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="キル時：回り込み", variable=self.var_orbit).pack(anchor="w")
        self.var_pull=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="キル後：引く", variable=self.var_pull).pack(anchor="w")
        self.var_multi=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="マルチキル時：動きを強める", variable=self.var_multi).pack(anchor="w")
        ttk.Label(f, text="演出の強さ", style="Card.TLabel").pack(anchor="w", pady=(7,2))

        f = card(right, "✧  自動カメラモーション")
        self.var_auto_motion=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="自動カメラモーション", variable=self.var_auto_motion).pack(anchor="w")
        ttk.Label(f, text="モーションタイプ", style="Card.TLabel").pack(anchor="w", pady=(6,2))
        ttk.Combobox(f, state="readonly", textvariable=self.var_motion_profile, values=["Smooth（自然）","Cinematic（Lolnam風）","Dynamic（大きく動く）","Auto（キル数で自動）"]).pack(fill="x")
        for text in ("キル前のカメラ移動", "キル瞬間のズーム", "キル後の引き", "マルチキル時の演出強化"):
            ttk.Checkbutton(f, text=text, variable=tk.BooleanVar(value=True)).pack(anchor="w")

        f = card(right, "⚙  その他の設定")
        self.var_hud=tk.BooleanVar(value=True); ttk.Checkbutton(f, text="HUD非表示", variable=self.var_hud).pack(anchor="w", pady=2)
        self.var_bars=tk.BooleanVar(value=False); ttk.Checkbutton(f, text="チャンピオンHPバーだけ残す", variable=self.var_bars).pack(anchor="w", pady=2)
        self.var_dof_blur=tk.DoubleVar(value=0.0); self.var_dof_focus_distance=tk.DoubleVar(value=5510.0); self.var_dof_near_distance=tk.DoubleVar(value=10000.0); self.var_dof_far_distance=tk.DoubleVar(value=10000.0)
        ttk.Checkbutton(f, text="音声クラッシュ防止", variable=tk.BooleanVar(value=True)).pack(anchor="w", pady=2)
        ttk.Label(f, text="出力FPS", style="Card.TLabel").pack(anchor="w", pady=(7,2))
        ttk.Combobox(f, state="readonly", values=["60 FPS", "144 FPS"], textvariable=self.var_fps_ui).pack(fill="x")
        ttk.Label(f, text="出力形式", style="Card.TLabel").pack(anchor="w", pady=(7,2))
        ttk.Combobox(f, state="readonly", values=["MP4（1080p）"], textvariable=self.var_format).pack(fill="x")
        ttk.Label(f, text="出力先（1080p MP4）", style="Card.TLabel").pack(anchor="w", pady=(8,2))
        out_row = ttk.Frame(f, style="Card.TFrame"); out_row.pack(fill="x")
        self.var_out_right = tk.StringVar(value=str(self.out_root))
        self.lbl_out_right = ttk.Label(out_row, textvariable=self.var_out_right,
                                       style="CardMuted.TLabel", wraplength=230)
        self.lbl_out_right.pack(side="left", fill="x", expand=True)
        ttk.Button(out_row, text="選択", command=self.on_pick_out).pack(side="right", padx=(6,0))
        ttk.Button(f, text="▶  動画を生成", style="Accent.TButton", command=self.on_make_clips).pack(fill="x", pady=(8,0), ipady=5)

        f = card(right, "◉  検出シーン")
        ttk.Label(f, text="☑ = 作成対象 / ☐ = 除外。行を選んで「チェック切替」。", style="CardMuted.TLabel", wraplength=280).pack(anchor="w", pady=(0, 5))
        self.lb_kills = tk.Listbox(f, height=7, bg="#FFFFFF", fg=fg, selectbackground=selected, selectforeground="#111827", relief="flat", highlightthickness=1, highlightbackground=line, activestyle="none", font=("Meiryo UI", 9))
        kills_sb=ttk.Scrollbar(f, orient="vertical", command=self.lb_kills.yview); self.lb_kills.configure(yscrollcommand=kills_sb.set)
        self.lb_kills.pack(fill="x", expand=False, pady=(0, 2)); kills_sb.pack(side="right", fill="y")
        self.lb_kills.bind('<<ListboxSelect>>', self.on_scene_selection)
        kb=ttk.Frame(f, style="Card.TFrame"); kb.pack(fill="x", pady=(6,0))
        ttk.Button(kb, text="✓ チェック切替", command=self.on_toggle_checked).pack(side="left", fill="x", expand=True, padx=(0,3))
        ttk.Button(kb, text="↳ 選択シーンへ移動", command=self.on_jump_selected).pack(side="left", fill="x", expand=True, padx=(3,0))
        kb2=ttk.Frame(f, style="Card.TFrame"); kb2.pack(fill="x", pady=(5,0))
        ttk.Button(kb2, text="全選択", command=self.on_check_all).pack(side="left", fill="x", expand=True, padx=(0,3))
        ttk.Button(kb2, text="全解除", command=self.on_uncheck_all).pack(side="left", fill="x", expand=True, padx=(3,0))
        ttk.Button(f, text="▶ 選択シーンを作成", command=self.on_make_selected).pack(fill="x", pady=(5,0), ipady=3)
        ttk.Button(f, text="☑ チェックしたシーンだけ作成", style="Accent.TButton", command=self.on_make_checked).pack(fill="x", pady=(5,0))
        ttk.Button(f, text="▶ 全検出シーンを一括作成", command=self.on_make_clips).pack(fill="x", pady=(5,0))

        f = card(right, "☁  出力状況")
        self.pb_job=ttk.Progressbar(f, maximum=100); self.pb_job.pack(fill="x")
        self.lbl_job=ttk.Label(f, text="待機中", style="CardMuted.TLabel"); self.lbl_job.pack(fill="x", pady=3)
        ttk.Button(f, text="中止", command=self.on_stop).pack(side="left")
        ttk.Button(f, text="出力フォルダを開く", command=self.on_open_out).pack(side="right")

        # bottom status bar ---------------------------------------------------
        bottom = ttk.Frame(r, padding=(16, 7))
        bottom.pack(fill="x")
        self.lbl_status=ttk.Label(bottom, text="", style="Muted.TLabel")
        self.lbl_status.pack(side="left", fill="x", expand=True)
        ttk.Label(bottom, text="●  準備完了", foreground=green, background=bg, font=("Meiryo UI", 9, "bold")).pack(side="left", padx=12)
        ttk.Label(bottom, text="参考動画　　テンプレート　　動画編集　　♥ LoLで最高の瞬間を", style="Muted.TLabel").pack(side="right")

        # legacy width variables/settings compatibility
        self.var_mirror = tk.BooleanVar(value=False)
        log_card = ttk.Frame(right, style="Card.TFrame", padding=(12, 10))
        log_card.pack(fill="x", pady=(0, 8))
        ttk.Label(log_card, text="▤  ログ", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.txt = tk.Text(log_card, height=7, state="disabled", bg="#FBFCFD", fg="#475467",
                           insertbackground=fg, wrap="none", relief="flat", highlightthickness=1, highlightbackground=line)
        log_sb = ttk.Scrollbar(log_card, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=log_sb.set)
        self.txt.pack(side="left", fill="both", expand=True)
        log_sb.pack(side="right", fill="y")
        self._mode_sidecards.append((log_card, right, "log"))

        # Initialize all template-backed controls.
        self.apply_template(self.var_tpl.get())
        self._apply_edit_mode(log=False)

        # A compact log window is available from the settings/diagnostics button.
        self._build_log_dialog = None

    def _apply_edit_mode(self, log: bool = True) -> None:
        """Switch visible editor controls only; never alter underlying render settings.

        A complete pack rebuild is necessary: pack_forget() followed by pack()
        otherwise moves the restored card after the persistent log card.
        """
        mode = self.var_edit_mode.get()
        easy = mode != "advanced"
        if hasattr(self, "_mode_easy_section"):
            self._mode_easy_section.pack_forget()
            for panel in self._mode_detail_sections:
                panel.pack_forget()
            if easy:
                self._mode_easy_section.pack(fill="x", pady=(0, 8))
            else:
                for panel in self._mode_detail_sections:
                    panel.pack(fill="x", pady=(0, 8))
        if hasattr(self, "_mode_sidecards"):
            for panel, _, _ in self._mode_sidecards:
                panel.pack_forget()
            for panel, parent, title in self._mode_sidecards:
                # Keep replay/player/template and results accessible in easy mode;
                # hide specialist edit/FX blocks while keeping them instantiated.
                if easy and (title.startswith(("▶  参考", "◉  参考", "◈  カラー", "◈  カメラ詳細", "◈  LoLnam", "✧  自動"))):
                    continue
                panel.pack(in_=parent, fill="x", pady=(0, 8))
        if hasattr(self, "edit_mode_hint"):
            self.edit_mode_hint.configure(text=(
                "リプレイ→対象選択→自動作成。難しい設定は隠れています。" if easy else
                "シーン・タイムライン・キーフレーム・カラーまで調整できます。"))
        if log and hasattr(self, "txt"):
            self.log("編集画面を切替: " + ("かんたん編集" if easy else "詳細編集"))

    def on_camera_safe_pose(self) -> None:
        """Restore conservative 3rd-person framing without deleting shot edits."""
        self.var_style.set(STYLES["third_cinema"])
        for key, value in (("third_elev", 28.0), ("third_dist", 950.0),
                           ("third_yaw", 0.0), ("motion_arc", 10.0),
                           ("motion_dolly", 3.0), ("dist_scale", 0.8)):
            if key in self.sl:
                self.sl[key].set(value)
        self.log("三人称カメラの追従距離・仰角・Yawを安定設定へ戻しました。既存のシーン別設定は保持しています。")

    def _choose_easy_preset(self, name: str) -> None:
        if name not in self.templates:
            return
        self.var_tpl.set(name)
        self.apply_template(name)
        self.log("かんたん編集の仕上がり: " + name)

    def on_keyframe_preset(self, preset: str) -> None:
        """Editable motion starting points, never silently save/overwrite a scene."""
        from ui.scene_project import validate_keyframes
        patterns = {
            "soft_orbit": [(-2.5, -9, 0, 0), (-1.1, -3, 2, -1),
                           (0, 9, 7, -3), (1.5, 4, 3, -1), (2.8, 0, 0, 0)],
            "push_pull": [(-2.5, 0, -8, 3), (-1.0, 0, -2, 1),
                          (0, 0, 12, -4), (1.0, 0, 6, -2), (2.5, 0, 0, 0)],
            "impact": [(-2.2, -8, 0, 0), (-0.75, -2, 1, -1),
                        (0, 10, 9, -4), (0.8, 5, 5, -2), (2.4, 0, 0, 0)],
        }
        if preset not in patterns:
            return
        self._edit_keyframes = validate_keyframes([
            {"time": t, "yaw": y, "zoom": z, "fov": f}
            for t, y, z, f in patterns[preset]])
        self._refresh_keyframe_list()
        self.log(f"キーフレームの型を適用: {preset}（未保存。『このシーンに保存』で確定）")

    def _focus_home(self):
        self.canvas.focus_set()

    def _focus_template(self):
        self.tpl_combo.focus_set()

    def _focus_reference(self):
        self.lb_reference.focus_set()

    def _select_template_by_text(self, needle: str):
        for name in self.templates:
            if needle in name:
                self.var_tpl.set(name)
                self.apply_template(name)
                self.log(f"テンプレート選択: {name}")
                return
        messagebox.showinfo(APP, f"「{needle}」に一致するテンプレートがありません。")

    # ------------------------------------------------------------ quick / UI actions
    def on_quick_prepare(self) -> None:
        """初回設定→直近リプレイ起動までを1ボタンで行う。"""
        try:
            if not self.lol_dir:
                self.lol_dir = paths.find_lol_dir()
            if not self.lol_dir:
                p = filedialog.askdirectory(title="League of Legends フォルダを選択")
                if not p:
                    return
                self.lol_dir = Path(p)
            msg = paths.enable_replay_api(paths.game_cfg_path(self.lol_dir))
            self.log(msg)
            recent = paths.list_replays()
            if recent:
                self._play(recent[0])
            else:
                messagebox.showinfo(APP, "Replay APIを設定しました。\nリプレイ(.rofl)を開いて再生してください。")
            self._refresh_status()
        except Exception as e:
            self.log(f"準備に失敗: {e}")
            messagebox.showerror(APP, str(e))

    def on_show_diagnostics(self) -> None:
        d = ROOT / "diagnostics"
        d.mkdir(exist_ok=True)
        err = d / "last_error.txt"
        if err.exists():
            try:
                text = err.read_text(encoding="utf-8", errors="replace")
                messagebox.showinfo("診断情報", text[-5000:] or "エラー情報はありません。")
                return
            except Exception:
                pass
        if sys.platform == "win32":
            os.startfile(str(d))  # type: ignore[attr-defined]

    def on_mirror_toggle(self) -> None:
        if self.source is not None and getattr(self.source, "running", False):
            self.on_mirror_stop()
            self.var_mirror.set(False)
        else:
            self.on_mirror_start()
            self.var_mirror.set(self.source is not None)

    def on_jump_selected(self) -> None:
        if not self._need_lock():
            return
        idx = self.lb_kills.curselection()
        if not idx:
            messagebox.showinfo(APP, "キル一覧から移動したいキルを選んでください。")
            return
        if idx[0] >= len(self.kills):
            return
        self._run_bg(self._jump_to_kill, self.kills[idx[0]])

    def _jump_to_kill(self, kill) -> None:
        from core.camera import attach_to_player
        self.api.set_playback(paused=True, speed=1.0)
        self.api.seek(max(0.0, float(kill.time) - 3.0))
        attach_to_player(self.api, self.locked, "third_cinema", dist_scale=0.8, height=170, log=self.log)
        self.log(f"キルシーンへ移動: {kill.time:.1f}秒 / {kill.killer} → {kill.victim}")

    def on_make_selected(self) -> None:
        if not self._need_lock():
            return
        idx = self.lb_kills.curselection()
        if not idx:
            messagebox.showinfo(APP, "作成したいキルを選んでください。")
            return
        if idx[0] >= len(self.kills):
            return
        self._run_bg(self._make_selected, self.kills[idx[0]], self.current_template(), *self._scene_render_config())

    def _make_selected(self, kill, tpl: Template, scene_mode=False, shots=None, auto=False, order=None) -> None:
        p = self.locked
        if p is None:
            return
        src, own = self._ensure_source()
        try:
            factory = None
            if tpl.game_audio:
                factory = (lambda path: SyntheticAudio(path)) if FAKE_CAPTURE else (lambda path: PreferredGameAudio(path))
            res = self._render_with_optional_scene_mode(src, p, [kill], tpl, False, factory,
                                                        scene_mode, shots or {}, auto, order)
            self.log(f"選択キルの作成完了: {len(res.outputs)}本")
        finally:
            if own:
                src.stop()

    def on_close(self) -> None:
        """アプリ終了時に録画/ミラー用リソースを安全に止めてから終了する。"""
        try:
            self.stop_ev.set()
            if self.source is not None:
                try:
                    self.source.stop()
                except Exception as e:
                    _diag_write(CRASH_LOG, f"close source stop: {e}")
                self.source = None
            self._save_settings()
            self._autosave_project()
        finally:
            try:
                self.root.destroy()
            except Exception:
                pass

    # ------------------------------------------------------------ helpers
    def log(self, msg: str) -> None:
        # UIログと同時に常時ファイルへフラッシュ。クラッシュしても直前の記録を残す。
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        _diag_write(RUN_LOG, line)
        try:
            self.q.put(("log", line))
        except Exception:
            pass

    def _pump(self) -> None:
        try:
            while True:
                kind, *a = self.q.get_nowait()
                if kind == "log":
                    self.txt.configure(state="normal")
                    self.txt.insert("end", time.strftime("[%H:%M:%S] ") + a[0] + "\n")
                    self.txt.see("end")
                    self.txt.configure(state="disabled")
                elif kind == "scan":
                    pct, t, ln, ne, nk = a
                    self.pb_scan["value"] = pct
                    self.lbl_scan.configure(text=f"時刻 {t:.0f} / {ln:.0f} 秒 ({pct:.0f}%)  イベント {ne}  対象キル {nk}")
                elif kind == "job":
                    done, total, pct, msg = a
                    self.pb_job["value"] = pct
                    self.lbl_job.configure(text=f"{msg}  ({done}/{total}  {pct:.0f}%)")
                elif kind == "players":
                    self._fill_players()
                elif kind == "kills":
                    self._fill_kills()
                    if self.kills:
                        self.lb_kills.selection_set(0)
                        self.on_scene_selection()
                elif kind == "status":
                    self._refresh_status()
                elif kind == "busy":
                    self.busy = a[0]
                elif kind == "reference_url_done":
                    path, url = a[0], a[1]
                    if path not in self.reference_videos:
                        self.reference_videos.append(path)
                    self._refresh_reference_list()
                    self.log(f"参考動画URL取得完了: {Path(path).name} / {url}")
                    self.lbl_reference.configure(text=f"URL動画を追加: {Path(path).name}")
                elif kind == "reference_url_error":
                    messagebox.showerror(APP, "参考動画URLの取得に失敗しました。\n\n" + str(a[0])[-900:])

                elif kind == "reference_done":
                    t, errors = a
                    self.templates[t.name] = t
                    if hasattr(self, "tpl_combo"):
                        self.tpl_combo.configure(values=list(self.templates))
                    self.var_tpl.set(t.name)
                    self.apply_template(t.name)
                    self.lbl_reference.configure(text=f"解析完了: {len(t.reference_sources)}本 / 失敗 {len(errors)}本。カメラ設定は基準版の現在値を維持。")
                    self.log(f"参考テンプレート作成: {t.name} / 成功 {len(t.reference_sources)}本 / 失敗 {len(errors)}本")
                    if errors:
                        for p,e in errors: self.log(f"  スキップ: {Path(p).name} - {e}")
                elif kind == "reference_error":
                    self.lbl_reference.configure(text="解析失敗（追加動画は保持されています。別の動画で再試行できます）")
                    self.log("参考テンプレート解析エラー: " + a[0])
                elif kind == "reference_remix_done":
                    saved=a[0]
                    for t in saved:
                        self.templates[t.name]=t
                    if hasattr(self, "tpl_combo"):
                        self.tpl_combo.configure(values=list(self.templates))
                    if saved:
                        self.var_tpl.set(saved[0].name); self.apply_template(saved[0].name)
                    self.lbl_reference.configure(text=f"リミックス {len(saved)}種類を保存しました（カメラ設定は不変）")
                    self.log("参考演出リミックス保存: " + ", ".join(t.name for t in saved))
        except queue.Empty:
            pass
        except Exception:
            _diag_write(CRASH_LOG, "UI_PUMP_ERROR\n" + traceback.format_exc())
        self.root.after(80, self._pump)

    def _refresh_status(self) -> None:
        up = self.api.is_up()
        cfg_ok = False
        if self.lol_dir:
            cfg_ok = paths.replay_api_enabled(paths.game_cfg_path(self.lol_dir))
        self.lbl_status.configure(
            text=f"LoL: {self.lol_dir or '未検出'}   |   Replay API設定: {'OK' if cfg_ok else '未設定'}   |   "
                 f"接続: {'OK' if up else '待機中 (リプレイ再生で自動接続)'}   |   映像入力: LoLウィンドウのみ")
        self.root.after(5000, self._refresh_status_safe)

    def _refresh_status_safe(self) -> None:
        threading.Thread(target=lambda: self.q.put(("status",)), daemon=True).start()

    def _pick(self, var: tk.StringVar, ft: list) -> None:
        p = filedialog.askopenfilename(filetypes=ft)
        if p:
            var.set(p)

    def _fill_players(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for p in self.players:
            self.tree.insert("", "end", iid=str(p.slot), values=("BLUE" if p.team == "ORDER" else "RED", p.champion, p.name),
                             tags=(p.team,))

    def _fill_kills(self) -> None:
        self.lb_kills.delete(0, "end")
        ordered=self.scene_project.ordered_keys(scene_key(k) for k in self.kills)
        ranks={k:i+1 for i,k in enumerate(ordered)}
        for i, k in enumerate(self.kills):
            m = {1: "", 2: " DOUBLE", 3: " TRIPLE", 4: " QUADRA"}.get(k.multikill, " PENTA" if k.multikill >= 5 else "")
            role = "⚔ KILL" if getattr(k, "role", "kill") == "kill" else "＋ ASSIST"
            mark = "☑" if i in self.checked_kills else "☐"
            edited = " ✎" if scene_key(k) in self.scene_project.shots else ""
            self.lb_kills.insert("end", f"{mark}{edited}  #{ranks[scene_key(k)]:02d}  {int(k.time // 60):02d}:{k.time % 60:04.1f}  [{role}] {k.killer} → {k.victim}{m}")

        self._refresh_order_list()

    # ---------------- scene direction (UI thread only) --------------------
    def _refresh_order_list(self):
        if not hasattr(self, 'scene_order_list'):
            return
        selected_key=None
        selected=self.scene_order_list.curselection()
        current=getattr(self,'_ordered_scene_keys',[])
        if selected and selected[0]<len(current):
            selected_key=current[selected[0]]
        keys=self.scene_project.ordered_keys(scene_key(k) for k in self.kills)
        self._ordered_scene_keys=keys
        descriptions={scene_key(k):f"{k.time:.1f}s  {k.killer} → {k.victim}" for k in self.kills}
        self.scene_order_list.delete(0,'end')
        for index,key in enumerate(keys,1):
            self.scene_order_list.insert('end',f"{index:02d}. {descriptions.get(key,key)}")
        if selected_key in keys:
            self.scene_order_list.selection_set(keys.index(selected_key))

    def on_order_selection(self,_event=None):
        pos=self.scene_order_list.curselection()
        if not pos or pos[0] >= len(getattr(self,'_ordered_scene_keys',[])):
            return
        key=self._ordered_scene_keys[pos[0]]
        for index,kill in enumerate(self.kills):
            if scene_key(kill)==key:
                self.lb_kills.selection_clear(0,'end')
                self.lb_kills.selection_set(index)
                self.lb_kills.see(index)
                self.on_scene_selection()
                return

    def _on_order_drag_start(self,event):
        self._drag_order_index = (self.scene_order_list.nearest(event.y), event.y)

    def _on_order_drag_end(self,event):
        drag=self._drag_order_index
        self._drag_order_index=None
        if self.busy or drag is None or abs(event.y-drag[1]) < 8:
            return
        initial=self._ordered_scene_keys
        start=drag[0]
        if not 0 <= start < len(initial):
            return
        key=initial[start]
        target=self.scene_order_list.nearest(event.y)
        if self.scene_project.move_to(key,(scene_key(k) for k in self.kills),target):
            self.var_scene_mode.set(True)
            self._schedule_project_save()
            self._refresh_scene_list()
            pos=self._ordered_scene_keys.index(key)
            self.scene_order_list.selection_clear(0,'end')
            self.scene_order_list.selection_set(pos)
            self.scene_order_list.see(pos)
            self.log(f'シーンをドラッグ移動: {start+1}番目 → {pos+1}番目')

    def on_move_scene(self,step):
        if self.busy:
            self.log('作成中はシーンの順序を変更できません。')
            return
        kill=self._current_scene()
        if kill is None:
            messagebox.showinfo(APP,'先に右のシーン一覧、または再生順リストでシーンを選択してください。')
            return
        key=scene_key(kill)
        if self.scene_project.move(key,(scene_key(k) for k in self.kills),step):
            self.var_scene_mode.set(True)
            self._schedule_project_save()
            self._refresh_scene_list()
            keys=self._ordered_scene_keys
            if key in keys:
                self.scene_order_list.selection_clear(0,'end')
                self.scene_order_list.selection_set(keys.index(key))
                self.scene_order_list.see(keys.index(key))
            self.log(f'モンタージュ順序変更: {kill.time:.1f}秒 → {keys.index(key)+1}番目')

    def on_reset_scene_order(self):
        if self.busy:
            return
        if self.scene_project.reset_order(scene_key(k) for k in self.kills):
            self._schedule_project_save()
            self._refresh_scene_list()
            self.log('モンタージュ順序を検出時刻順へ戻しました。')

    def _current_scene(self):
        selection = self.lb_kills.curselection()
        if not selection or selection[0] >= len(self.kills):
            return None
        return self.kills[selection[0]]

    def _refresh_scene_list(self):
        selection=self.lb_kills.curselection()
        index=selection[0] if selection else None
        self._fill_kills()
        if index is not None and index<len(self.kills):
            self.lb_kills.selection_set(index)
        self.on_scene_selection()

    def on_scene_selection(self, _event=None):
        kill = self._current_scene()
        if kill is None:
            return
        key = scene_key(kill)
        shot = self.scene_project.shots.get(key) or recommend(kill, self.var_pre.get(), self.var_post.get())
        self._scene_loading = True
        try:
            self.var_shot_profile.set(shot.profile)
            self.var_shot_intensity.set(shot.intensity)
            for field, var in self.scene_vars.items():
                var.set(getattr(shot, field))
            self._edit_keyframes = [dict(frame) for frame in shot.keyframes]
            self._refresh_keyframe_list()
            self.var_scene_fx_enabled.set(shot.fx_override)
            for field, var in self.scene_fx_vars.items():
                var.set(getattr(shot, field))
            self.shot_motion_graph.redraw()
            self._show_scene_thumbnail(key)
            self.scene_selected_label.configure(text=(
                f"{kill.time:.1f}秒 / {kill.victim} / {'保存済み編集' if key in self.scene_project.shots else '自動推薦値（未保存）'}"))
        finally:
            self._scene_loading = False

    def _scene_thumbnail_path(self, key):
        digest = hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]
        return ROOT / 'projects' / 'thumbnails' / f'{digest}.png'

    def _show_scene_thumbnail(self, key):
        path=self._scene_thumbnail_path(key)
        if not path.is_file():
            self._scene_thumbnail_photo = None
            self.scene_thumbnail.configure(image='', text='サムネイル未保存')
            return
        try:
            with Image.open(path) as original:
                image=original.convert('RGB')
                image.thumbnail((220,124), Image.Resampling.LANCZOS)
                photo=ImageTk.PhotoImage(image)
            self._scene_thumbnail_photo=photo
            self.scene_thumbnail.configure(image=photo, text='')
        except Exception as exc:
            self._scene_thumbnail_photo=None
            self.scene_thumbnail.configure(image='', text='画像を開けません')
            self.log(f'サムネイル表示失敗: {exc}')

    def on_capture_scene_thumbnail(self):
        if self.busy:
            self.log('書き出し中はサムネイルを保存できません。')
            return
        kill=self._current_scene()
        if kill is None:
            messagebox.showinfo(APP,'保存先のシーンを選んでください。')
            return
        rgb, _=self._current_frame_rgb(480,270)
        if rgb is None:
            messagebox.showinfo(APP,'LoLミラーが映っている状態で実行してください。')
            return
        try:
            path=self._scene_thumbnail_path(scene_key(kill))
            path.parent.mkdir(parents=True,exist_ok=True)
            Image.fromarray(rgb).convert('RGB').save(path, format='PNG')
            self._show_scene_thumbnail(scene_key(kill))
            self.log(f'シーンサムネイルを保存: {kill.time:.1f}s / {path.name}')
        except Exception as exc:
            messagebox.showerror(APP,f'サムネイル保存失敗: {exc}')

    def _scene_shot_from_ui(self) -> Shot:
        raw = {'profile': self.var_shot_profile.get(), 'intensity': self.var_shot_intensity.get()}
        for key, variable in self.scene_vars.items():
            raw[key] = variable.get()
        raw['keyframes'] = [dict(f) for f in getattr(self, '_edit_keyframes', [])]
        raw['fx_override'] = self.var_scene_fx_enabled.get()
        for key, variable in self.scene_fx_vars.items():
            raw[key] = variable.get()
        return Shot.validated(raw)

    def _refresh_keyframe_list(self, select_time=None):
        if not hasattr(self, 'kf_list'):
            return
        self.kf_list.delete(0,'end')
        frames = getattr(self, '_edit_keyframes', [])
        for f in frames:
            self.kf_list.insert('end',f"{f['time']:+.1f}s   回転 {f['yaw']:+.1f}°  寄り {f['zoom']:+.1f}%  FOV {f['fov']:+.1f}°")
        if select_time is not None:
            for i, frame in enumerate(frames):
                if frame['time']==select_time:
                    self.kf_list.selection_set(i)
                    self.kf_list.see(i)
                    break
        self.shot_motion_graph.redraw()

    def on_keyframe_selection(self, _event=None):
        selection=self.kf_list.curselection()
        if not selection or selection[0]>=len(self._edit_keyframes):
            return
        for key, value in self._edit_keyframes[selection[0]].items():
            if key in self.kf_vars:
                self.kf_vars[key].set(value)

    def on_keyframe_upsert(self):
        if self.busy:
            return
        try:
            from ui.scene_project import validate_keyframes
            frame={key:var.get() for key,var in self.kf_vars.items()}
            selection=self.kf_list.curselection()
            frames=list(self._edit_keyframes)
            if selection and selection[0]<len(frames):
                frames.pop(selection[0])
            frames.append(frame)
            self._edit_keyframes=validate_keyframes(frames)
            self._refresh_keyframe_list(select_time=round(frame['time'],2))
        except Exception as exc:
            messagebox.showerror(APP,f'キーフレーム設定: {exc}')

    def on_keyframe_remove(self):
        if self.busy:
            return
        selection=self.kf_list.curselection()
        if selection and selection[0]<len(self._edit_keyframes):
            del self._edit_keyframes[selection[0]]
            self._refresh_keyframe_list()

    def on_keyframe_preview(self):
        """Replay the CURRENT editor values, including unsaved keyframes, in LoL.

        This button previously redrew only the graph; users rightly expected
        a camera-motion preview. Capture all Tk values on the UI thread before
        dispatching the Replay API work to the background worker.
        """
        self.shot_motion_graph.redraw()
        kill = self._current_scene()
        if kill is None:
            self.log('動きのプレビュー: 検出シーンを選択してください。')
            return
        if not self._need_lock():
            return
        if self.busy:
            self.log('動きのプレビュー: 別の処理を実行中です。')
            return
        try:
            shot = self._scene_shot_from_ui()
            tpl = apply_shot(self.current_template(), shot)
        except (ValueError, TypeError, tk.TclError) as exc:
            self.log(f'動きのプレビュー設定エラー: {exc}')
            return
        self.log(f'動きのプレビュー開始: {len(shot.keyframes)}キーフレーム / '
                 f'シーン {kill.time:.1f}s / 未保存の編集値も反映')
        self._run_bg(self._preview_play, tpl, kill)

    def _schedule_project_save(self):
        if self._project_autosave_token is not None:
            try: self.root.after_cancel(self._project_autosave_token)
            except tk.TclError: pass
        self._project_autosave_token = self.root.after(850, self._autosave_project)

    def _autosave_project(self):
        self._project_autosave_token = None
        try:
            self.scene_project.save(self.scene_project_path)
        except Exception as exc:
            self.log(f'編集プロジェクトの自動保存失敗: {exc}')

    def on_save_scene(self):
        kill = self._current_scene()
        if kill is None:
            messagebox.showinfo(APP, '右側の検出シーンを選択してください。')
            return
        try:
            shot=self._scene_shot_from_ui()
            self.scene_project.put(scene_key(kill), shot)
            self.var_scene_mode.set(True)
            self._schedule_project_save()
            self._refresh_scene_list()
            self.log(f'シーン個別設定を保存: {kill.time:.1f}秒 / {shot.profile} / Orbit {shot.arc}°')
        except Exception as exc:
            messagebox.showerror(APP, f'シーン設定を保存できません: {exc}')

    def on_recommend_scene(self):
        kill = self._current_scene()
        if kill is None:
            messagebox.showinfo(APP, 'シーンを選択してください。')
            return
        shot = recommend(kill, self.var_pre.get(), self.var_post.get())
        self.scene_project.put(scene_key(kill),shot)
        self.var_scene_mode.set(True)
        self._schedule_project_save()
        self._refresh_scene_list()
        self.log(f'シーン自動推薦: {kill.time:.1f}秒 / {shot.profile}')

    def on_recommend_all(self):
        if not self.kills:
            messagebox.showinfo(APP,'先にシーンをスキャンしてください。')
            return
        plan={scene_key(k):recommend(k,self.var_pre.get(),self.var_post.get()) for k in self.kills}
        self.scene_project.put_many(plan)
        self.var_scene_mode.set(True)
        self.var_auto_director.set(True)
        self._schedule_project_save()
        self._refresh_scene_list()
        self.log(f'全シーンにカメラ自動演出を設定: {len(plan)}件')

    def on_smart_one_click(self):
        """Explicit enhanced one-click path; normal one click remains unchanged."""
        self.var_scene_mode.set(True)
        self.var_auto_director.set(True)
        self.on_one_click(smart=True)

    def on_clear_scene(self):
        kill=self._current_scene()
        if kill is not None:
            self.scene_project.remove(scene_key(kill))
            self._schedule_project_save()
            self._refresh_scene_list()

    def on_scene_undo(self):
        if self.scene_project.undo():
            self._schedule_project_save()
            self._refresh_scene_list()

    def on_scene_redo(self):
        if self.scene_project.redo():
            self._schedule_project_save()
            self._refresh_scene_list()

    def on_scene_export(self):
        target = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('AutoCine project','*.json')],
                                             initialfile='autocine_scenes.json',title='シーン編集を保存')
        if target:
            try:
                self.scene_project.save(target)
                self.log(f'編集プロジェクトを書き出しました: {target}')
            except Exception as exc: messagebox.showerror(APP,str(exc))

    def on_scene_import(self):
        target=filedialog.askopenfilename(filetypes=[('AutoCine project','*.json')],title='シーン編集を読み込む')
        if target:
            try:
                self.scene_project = SceneProject.load(target)
                self.var_scene_mode.set(True)
                self._schedule_project_save()
                self._refresh_scene_list()
                self.log(f'編集プロジェクトを読み込みました: {len(self.scene_project.shots)} シーン')
            except Exception as exc: messagebox.showerror(APP,f'読み込み失敗: {exc}')

    def _scene_render_config(self):
        """Called in UI thread: worker receives only plain snapshots."""
        return bool(self.var_scene_mode.get()), self.scene_project.snapshot(), bool(self.var_auto_director.get()), list(self.scene_project.sequence)

    def _render_with_optional_scene_mode(self, src, player, kills, tpl, montage, factory,
                                         scene_mode: bool, shots: dict, auto: bool, order=None):
        if scene_mode:
            return render_scenes(self.api,src,player,kills,tpl,self.out_root,montage,shots,auto=auto,
                                 progress=lambda *a:self.q.put(('job',*a)),stop=self.stop_ev,
                                 log=self.log,audio_factory=factory,order=order)
        return run_auto_edit(self.api,src,player,kills,tpl,self.out_root,montage,
                             progress=lambda *a:self.q.put(('job',*a)),stop=self.stop_ev,
                             log=self.log,audio_factory=factory)

    def on_toggle_checked(self) -> None:
        idx = self.lb_kills.curselection()
        if not idx:
            return
        i = idx[0]
        if i in self.checked_kills:
            self.checked_kills.remove(i)
        else:
            self.checked_kills.add(i)
        self._fill_kills()
        self.lb_kills.selection_set(i)

    def on_check_all(self) -> None:
        self.checked_kills = set(range(len(self.kills)))
        self._fill_kills()

    def on_uncheck_all(self) -> None:
        self.checked_kills.clear()
        self._fill_kills()

    def on_make_checked(self) -> None:
        """UI thread captures all Tk state before a background render starts."""
        _diag_write(RUN_LOG, "CHECKED_STAGE click_enter")
        if not self._need_lock():
            _diag_write(RUN_LOG, "CHECKED_STAGE missing_player_lock")
            return
        if self.busy:
            _diag_write(RUN_LOG, "CHECKED_STAGE already_busy")
            messagebox.showinfo(APP, "別の処理を実行中です。")
            return
        selected = [self.kills[i] for i in sorted(self.checked_kills) if 0 <= i < len(self.kills)]
        if not selected:
            messagebox.showinfo(APP, "チェックされたシーンがありません。")
            return
        _diag_write(RUN_LOG, f"CHECKED_CLICK count={len(selected)}")
        try:
            _diag_write(RUN_LOG, "CHECKED_STAGE template_begin")
            tpl = self.current_template()    # Tk variables: main/UI thread ONLY
            _diag_write(RUN_LOG, "CHECKED_STAGE template_ready")
            montage = bool(self.var_montage.get())
            _diag_write(RUN_LOG, "CHECKED_STAGE enqueue_worker")
            if _fatal_fp is not None:
                try:
                    faulthandler.dump_traceback_later(35, repeat=True, file=_fatal_fp)
                    self._checked_watchdog_active = True
                except Exception:
                    pass
            self._run_bg(self._make_list, list(selected), tpl, montage, *self._scene_render_config())
            _diag_write(RUN_LOG, "CHECKED_STAGE queued")
        except Exception:
            _diag_write(CRASH_LOG, "CHECKED_CALLBACK_ERROR\n" + traceback.format_exc())
            self.log("チェック済みシーン開始時にエラーが発生しました。diagnostics/crash.log を確認してください。")

    def _make_list(self, selected, tpl: Template, montage: bool, scene_mode=False, shots=None, auto=False, order=None) -> None:
        """Worker only: never read Tk variables in this function."""
        _diag_write(RUN_LOG, "CHECKED_STAGE worker_enter")
        p = self.locked
        if p is None:
            _diag_write(RUN_LOG, "CHECKED_STAGE worker_missing_player")
            return
        src = None
        own = False
        try:
            _diag_write(RUN_LOG, "CHECKED_STAGE capture_start")
            src, own = self._ensure_source()
            _diag_write(RUN_LOG, f"CHECKED_STAGE capture_ready own={own}")
            factory = None
            if tpl.game_audio:
                factory = (lambda path: SyntheticAudio(path)) if FAKE_CAPTURE else (lambda path: PreferredGameAudio(path))
            _diag_write(RUN_LOG, "CHECKED_STAGE render_begin")
            res = self._render_with_optional_scene_mode(src, p, list(selected), tpl, montage, factory,
                                                        scene_mode, shots or {}, auto, order)
            _diag_write(RUN_LOG, f"CHECKED_STAGE render_complete outputs={len(res.outputs)} failed={len(res.failed)}")
            self.log(f"チェック済みシーンの作成完了: {len(res.outputs)}本" +
                     (f" / 失敗 {len(res.failed)}本" if res.failed else ""))
        except Exception:
            _diag_write(CRASH_LOG, "CHECKED_WORKER_ERROR\n" + traceback.format_exc())
            raise  # _run_bg catches and reports the error
        finally:
            if own and src is not None:
                _diag_write(RUN_LOG, "CHECKED_STAGE capture_stop")
                try:
                    src.stop()
                except Exception as e:
                    _diag_write(CRASH_LOG, f"CHECKED_CAPTURE_STOP_ERROR: {e}")
                _diag_write(RUN_LOG, "CHECKED_STAGE worker_exit")
            if self._checked_watchdog_active:
                try:
                    faulthandler.cancel_dump_traceback_later()
                except Exception:
                    pass
                self._checked_watchdog_active = False

    def _run_bg(self, fn, *a) -> None:
        if self.busy:
            messagebox.showinfo(APP, "別の処理を実行中です。")
            return
        self.stop_ev.clear()
        # Set this immediately so a rapid double-click cannot start two capture jobs.
        self.busy = True
        self.q.put(("busy", True))
        name = getattr(fn, "__name__", "worker")
        _diag_write(RUN_LOG, f"BG_STAGE start_requested fn={name}")

        def w():
            _diag_write(RUN_LOG, f"BG_STAGE worker_started fn={name}")
            try:
                fn(*a)
                _diag_write(RUN_LOG, f"BG_STAGE worker_finished fn={name}")
            except Exception as e:
                self.log(f"エラー: {e}")
                (ROOT / "diagnostics").mkdir(exist_ok=True)
                (ROOT / "diagnostics" / "last_error.txt").write_text(traceback.format_exc(), encoding="utf-8")
                _diag_write(RUN_LOG, f"BG_STAGE worker_error fn={name}: {type(e).__name__}: {e}")
            finally:
                _diag_write(RUN_LOG, f"BG_STAGE worker_finally fn={name}")
                self.q.put(("busy", False))
        try:
            threading.Thread(target=w, daemon=True, name=f"AutoCine-{name}").start()
        except Exception as e:
            self.busy = False
            self.q.put(("busy", False))
            _diag_write(CRASH_LOG, f"BG_THREAD_START_ERROR {name}: {e}")
            raise

    # ------------------------------------------------------------ video effects
    def _clear_video_effects(self) -> None:
        for v in getattr(self, "effect_vars", {}).values():
            v.set(False)

    def _apply_effect_preset(self, name: str) -> None:
        self._clear_video_effects()
        groups = {
            "キル瞬間": {"chroma_leak", "flash"},
            "カメラ演出": {"motion_camera", "zoom_blur", "camera_shake", "wiggle", "spin_motion"},
            "VHS / Glitch": {"glitch", "vhs_damage", "block_motion", "chroma_leak"},
            "シネマ": {"focus_blur", "vignette_fx", "glint", "vr_light_leak", "sphere_blur"},
            "全部控えめ": set(VIDEO_EFFECT_LABELS),
            "なし": set(),
        }
        keys = groups.get(name, set())
        for key, var in getattr(self, "effect_vars", {}).items():
            if key in keys:
                var.set(True)
                self.effect_strength_vars[key].set(min(0.35, float(VIDEO_EFFECT_DEFAULTS.get(key, 0.25))))

    def _get_video_effects(self) -> dict:
        out = {}
        for key, var in getattr(self, "effect_vars", {}).items():
            if bool(var.get()):
                try:
                    out[key] = max(0.05, min(1.0, float(self.effect_strength_vars[key].get())))
                except (TypeError, ValueError, tk.TclError):
                    out[key] = float(VIDEO_EFFECT_DEFAULTS.get(key, 0.25))
        return out

    # ------------------------------------------------------------ template <-> UI
    def apply_template(self, name: str) -> None:
        t = self.templates[name]
        self.var_int.set(t.intensity)
        self.var_style.set(STYLES.get(t.style, t.style))
        self.var_grade.set(GRADE_JP.get(t.grade, t.grade))
        if hasattr(self, "var_motion_profile"):
            mp = getattr(t, "motion_profile", "cinematic")
            self.var_motion_profile.set(getattr(self, "_motion_profile_jp", {}).get(mp, mp))
        for k, v in self.sl.items():
            v.set(getattr(t, k))
        self.var_tr.set(TRANSITIONS.get(t.transition, t.transition))
        self.var_pre.set(t.pre)
        self.var_post.set(t.post)
        self.var_merge.set(t.merge_multikill)
        self.var_hud.set(t.hide_hud)
        self.var_bars.set(t.keep_champion_bars)
        self.var_gaudio.set(t.game_audio)
        self.var_fog.set(t.fog_enabled)
        self.var_fog_preset.set(FOG_PRESETS.get(t.fog_preset, t.fog_preset))
        self.var_curve.set(t.curve_enabled)
        self.var_curve_points.set(t.curve_points)
        self.var_dof.set(t.dof_enabled)
        for key in ("dof_blur", "dof_focus_distance", "dof_near_distance", "dof_far_distance"):
            if key in self.sl:
                self.sl[key].set(float(getattr(t, key)))
        saved_fx = getattr(t, "video_effects", {}) or {}
        for key, var in getattr(self, "effect_vars", {}).items():
            val = float(saved_fx.get(key, 0.0))
            var.set(val > 0.001)
            if key in self.effect_strength_vars:
                self.effect_strength_vars[key].set(val if val > 0.001 else float(VIDEO_EFFECT_DEFAULTS.get(key, 0.25)))
        if hasattr(self, "var_effect_preset"):
            self.var_effect_preset.set(getattr(t, "effect_preset", "なし") or "なし")

    def current_template(self) -> Template:
        t = Template(name=self.var_tpl.get())
        t.intensity = self.var_int.get()
        t.style = rev(STYLES).get(self.var_style.get(), "cinema")
        t.grade = rev(GRADE_JP).get(self.var_grade.get(), "standard")
        if hasattr(self, "var_motion_profile"):
            t.motion_profile = getattr(self, "_motion_profile_rev", {}).get(self.var_motion_profile.get(), self.var_motion_profile.get())
        for k, v in self.sl.items():
            setattr(t, k, float(v.get()))
        t.transition = rev(TRANSITIONS).get(self.var_tr.get(), "fade")
        t.pre, t.post = float(self.var_pre.get()), float(self.var_post.get())
        t.merge_multikill = bool(self.var_merge.get())
        t.title_text = self.var_title.get().strip()
        t.bgm_path, t.lut_path = self.var_bgm.get(), self.var_lut.get()
        # 空欄ならタイトルを一切表示しない。自動KILL文字は生成しない。
        t.title_auto = False
        t.hide_hud, t.keep_champion_bars = bool(self.var_hud.get()), bool(self.var_bars.get())
        t.game_audio = bool(self.var_gaudio.get())
        t.fog_enabled = bool(self.var_fog.get())
        t.fog_preset = rev(FOG_PRESETS).get(self.var_fog_preset.get(), "teal")
        t.curve_enabled = bool(self.var_curve.get())
        t.curve_points = self.var_curve_points.get().strip()
        t.dof_enabled = bool(self.var_dof.get())
        t.dof_blur = float(self.sl.get("dof_blur", tk.DoubleVar(value=t.dof_blur)).get())
        t.dof_focus_distance = float(self.sl.get("dof_focus_distance", tk.DoubleVar(value=t.dof_focus_distance)).get())
        t.dof_near_distance = float(self.sl.get("dof_near_distance", tk.DoubleVar(value=t.dof_near_distance)).get())
        t.dof_far_distance = float(self.sl.get("dof_far_distance", tk.DoubleVar(value=t.dof_far_distance)).get())
        t.video_effects = self._get_video_effects()
        t.effect_preset = self.var_effect_preset.get() if hasattr(self, "var_effect_preset") else "なし"
        # LoLミラー/カメラは144Hzで内部サンプリングし、最終出力FPSだけUI選択値へ合わせる。
        # これで60fps書き出しでも、カメラ演出の元データを144Hzで保持できる。
        t.capture_fps = 144
        try:
            fps = int(str(self.var_fps_ui.get()).split()[0])
            if fps in (30, 60, 120, 144):
                t.fps = fps
        except Exception:
            pass
        return t

    def _refresh_gpu_status(self) -> None:
        try:
            ok = bool(gpu_encoder_available())
            if hasattr(self, "lbl_gpu"):
                self.lbl_gpu.configure(text=(gpu_pipeline_status() + " / UIプレビューはCPU合成" if ok else gpu_pipeline_status() + " / UIプレビューはCPU合成"))
        except Exception as e:
            if hasattr(self, "lbl_gpu"):
                self.lbl_gpu.configure(text=f"GPU状態: 判定できません ({type(e).__name__})")

    def _apply_panel_widths(self) -> None:
        try:
            lw = max(260, min(520, int(self.var_left_width.get())))
            rw = max(300, min(620, int(self.var_right_width.get())))
        except (TypeError, ValueError, tk.TclError):
            return
        self.var_left_width.set(lw)
        self.var_right_width.set(rw)
        if hasattr(self, "left_scroll"):
            self.left_scroll.set_width(lw)
        if hasattr(self, "right_scroll"):
            self.right_scroll.set_width(rw)
        self.root.update_idletasks()
        self._save_settings()

    def _load_settings(self) -> None:
        try:
            d = json.loads(SETTINGS.read_text(encoding="utf-8"))
            if d.get("out_root"):
                self.out_root = Path(d["out_root"])
                self.lbl_out.configure(text=str(self.out_root))
                if hasattr(self, "var_out_right"):
                    self.var_out_right.set(str(self.out_root))
            if d.get("left_width"):
                self.var_left_width.set(int(d["left_width"]))
            if d.get("right_width"):
                self.var_right_width.set(int(d["right_width"]))
            self._apply_panel_widths()
            restored_mode = d.get("edit_mode", "easy")
            if restored_mode in ("easy", "advanced"):
                self.var_edit_mode.set(restored_mode)
                self._apply_edit_mode(log=False)
        except Exception:
            pass

    def _save_settings(self) -> None:
        try:
            SETTINGS.write_text(json.dumps({"out_root": str(self.out_root),
                                             "left_width": int(self.var_left_width.get()),
                                             "right_width": int(self.var_right_width.get()),
                                             "edit_mode": self.var_edit_mode.get()}, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    # ------------------------------------------------------------ reference templates
    def on_add_reference_videos(self) -> None:
        files = filedialog.askopenfilenames(
            title="参考動画を追加（複数可・追加だけでは解析しません）",
            filetypes=[("動画", "*.mp4 *.mov *.mkv *.webm *.avi *.m4v"), ("すべて", "*.*")])
        if not files:
            return
        existing = set(self.reference_videos)
        for p in files:
            if p not in existing:
                self.reference_videos.append(p); existing.add(p)
        self._refresh_reference_list()
        self.log(f"参考動画を追加: {len(files)}本 / 合計 {len(self.reference_videos)}本（まだ解析していません）")

    def on_add_reference_url(self) -> None:
        url = simpledialog.askstring("参考動画URL", "X / Twitter / YouTube などの動画URLを貼り付けてください。\nyt-dlp対応サイトから動画を取得して参考動画に追加します:")
        if not url:
            return
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showerror(APP, "http:// または https:// で始まるURLを指定してください。")
            return
        self._run_bg(self._download_reference_url, url)

    def _download_reference_url(self, url: str) -> None:
        try:
            import subprocess, sys
            out_dir = self.reference_template_dir / "downloads"
            out_dir.mkdir(parents=True, exist_ok=True)
            before = {p.resolve() for p in out_dir.glob("*.*") if p.is_file()}
            cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "-f", "bv*+ba/b",
                   "--merge-output-format", "mp4", "-o", str(out_dir / "ref_%(id)s.%(ext)s"), url]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            if r.returncode != 0:
                raise RuntimeError((r.stderr or r.stdout)[-1200:])
            candidates = [p for p in out_dir.glob("ref_*.*") if p.is_file() and p.resolve() not in before]
            if not candidates:
                candidates = sorted(out_dir.glob("ref_*.*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates:
                raise RuntimeError("動画ファイルを取得できませんでした。公開動画か、yt-dlpが対応するURLか確認してください。")
            path = str(candidates[0])
            self.q.put(("reference_url_done", path, url))
        except Exception as e:
            self.log(f"参考動画URL取得失敗: {e}")
            self.q.put(("reference_url_error", str(e)))

    def on_remove_reference_video(self) -> None:
        if not hasattr(self, "lb_reference"):
            return
        idx = list(self.lb_reference.curselection())
        if not idx:
            return
        for i in reversed(idx):
            if 0 <= i < len(self.reference_videos):
                self.reference_videos.pop(i)
        self._refresh_reference_list()

    def _refresh_reference_list(self) -> None:
        if not hasattr(self, "lb_reference"): return
        self.lb_reference.delete(0, "end")
        for p in self.reference_videos:
            self.lb_reference.insert("end", Path(p).name)
        self.lbl_reference.configure(text=f"参考動画 {len(self.reference_videos)}本 / 追加済み（未解析）")

    def _add_template_to_ui(self, t: Template) -> None:
        self.templates[t.name] = t
        if hasattr(self, "tpl_combo"):
            self.tpl_combo.configure(values=list(self.templates))
        self.var_tpl.set(t.name)
        self.apply_template(t.name)

    def on_make_reference_template(self) -> None:
        if not self.reference_videos:
            messagebox.showinfo(APP, "先に参考動画を追加してください。")
            return
        camera_base = self.current_template()
        paths = list(self.reference_videos)
        name = "参考_" + Path(paths[0]).stem[:24]
        self._run_bg(self._learn_reference, paths, name, camera_base)

    def _learn_reference(self, paths: list[str], name: str, camera_base: Template) -> None:
        try:
            t, errors = template_from_references(paths, name, camera_base)
            save_reference_template(t, self.reference_template_dir / (name + ".json"))
            # UI更新はキュー経由。Tk変数をワーカースレッドから触らない。
            self.q.put(("reference_done", t, errors))
        except Exception as e:
            self.log(f"参考動画テンプレート作成失敗: {e}")
            self.q.put(("reference_error", str(e)))

    def on_reference_remix(self) -> None:
        # 現在選択中のテンプレを基に派生。参考動画を再解析する必要はない。
        t = self.current_template()
        if not t.reference_dna:
            messagebox.showinfo(APP, "先に『参考動画 → テンプレート作成』を実行してください。")
            return
        self._run_bg(self._save_reference_remixes, t)

    def _save_reference_remixes(self, t: Template) -> None:
        saved=[]
        for x in make_remixes(t):
            save_reference_template(x, self.reference_template_dir / (x.name + ".json"))
            saved.append(x)
        self.q.put(("reference_remix_done", saved))

    # ------------------------------------------------------------ actions
    def on_fix_cfg(self) -> None:
        if not self.lol_dir:
            p = filedialog.askdirectory(title="League of Legends フォルダを選択 (Config が入っている場所)")
            if not p:
                return
            self.lol_dir = Path(p)
        msg = paths.enable_replay_api(paths.game_cfg_path(self.lol_dir))
        self.log(msg)
        messagebox.showinfo(APP, msg)
        self._refresh_status()

    def on_open_replay(self) -> None:
        p = filedialog.askopenfilename(initialdir=str(paths.replays_dir()), filetypes=[("LoL Replay", "*.rofl")])
        if p:
            self._play(Path(p))

    def on_play_recent(self) -> None:
        n = self.cb_recent.get()
        if n:
            self._play(paths.replays_dir() / n)

    def _play(self, p: Path) -> None:
        try:
            how = watch_replay(self.lol_dir, p)
            self.log(f"リプレイを起動 ({how}): {p.name}  → 読み込み完了後『接続してプレイヤー取得』")
        except Exception as e:
            self.log(f"起動失敗: {e}")
            messagebox.showerror(APP, str(e))

    def on_connect(self) -> None:
        self._run_bg(self._connect)

    def _connect(self) -> None:
        self.log("Replay API に接続中… (リプレイの読み込み完了まで待ちます)")
        if not self.api.wait_ready(timeout=90, stop=self.stop_ev):
            self.log("接続できません。game.cfg設定→LoL再起動→リプレイ再生を確認してください。")
            return
        for _ in range(20):                       # プレイヤー一覧が揃うまで待つ
            raw = self.api.playerlist()
            if len(raw) >= 2:
                break
            time.sleep(1.0)
        self.players = parse_players(raw)
        self.q.put(("players",))
        self.log(f"プレイヤー {len(self.players)} 人を取得しました。対象を選んで『固定』を押してください。")
        if len(self.players) < 10:
            self.log("※10人未満です (カスタム/ボット戦の可能性)。")

    def on_lock(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo(APP, "プレイヤーを選んでください。")
            return
        self.locked = next(p for p in self.players if str(p.slot) == sel[0])
        self.lbl_lock.configure(text=f"対象: {self.locked.label()}", foreground="#15803d")
        self.log(f"対象を固定: {self.locked.label()} (slot {self.locked.slot})")
        self.kills = []
        self.checked_kills = set()
        self._fill_kills()

    def on_scan(self) -> None:
        if not self._need_lock():
            return
        self._run_bg(self._scan)

    def _need_lock(self) -> bool:
        if self.locked is None:
            messagebox.showinfo(APP, "先にプレイヤーを選び『このプレイヤーを対象に固定』を押してください。")
            return False
        return True

    def _scan(self, event_mode: str | None = None) -> None:
        p = self.locked
        self.log(f"全編スキャン開始: {p.label()}")
        # Tk変数はバックグラウンドスレッドから読まない。UI側でsnapshotした値を渡す。
        # この関数はバックグラウンドスレッドからも呼ばれるため、Tk変数を読まない。
        selected_mode = event_mode if event_mode is not None else "キル"
        mode = {"キル": "kill", "アシスト": "assist", "キル＋アシスト": "both"}.get(selected_mode, "kill")
        res = scan_kills(self.api, p, progress=lambda *a: self.q.put(("scan", *a)), stop=self.stop_ev,
                         diag_dir=ROOT / "diagnostics", event_mode=mode)
        self.kills = res.kills
        self.checked_kills = set(range(len(self.kills)))
        self.q.put(("kills",))
        self.log(f"スキャン完了: イベント {res.total_events} 件 / 対象シーン {len(res.kills)} 件 / モード {selected_mode}"
                 + ("" if res.complete else " (途中で中断)"))

    def _ensure_source(self):
        if self.source is not None and self.source.running:
            return self.source, False
        if FAKE_CAPTURE:
            src = SyntheticSource(time_fn=lambda: float(self.api.playback().get("time", 0.0)))
        else:
            src = WGCWindowSource()
        src.start()
        return src, True

    def on_make_clips(self) -> None:
        if not self._need_lock():
            return
        if not self.kills:
            messagebox.showinfo(APP, "先に全編スキャンを実行してください。")
            return
        self._run_bg(self._make, False, self.current_template(), bool(self.var_montage.get()), "キル", *self._scene_render_config())

    def _set_camera_motion(self, profile: str, arc: float, dolly: float) -> None:
        """UI-only: set the existing camera engine parameters, never overwrite target lock."""
        if profile not in self._motion_profile_jp:
            return
        self.var_motion_profile.set(self._motion_profile_jp[profile])
        self.sl["motion_arc"].set(arc)
        self.sl["motion_dolly"].set(dolly)
        self.log(f"カメラ簡単設定: {profile}, Orbit={arc:g}°, Dolly={dolly:g}%")

    def _apply_auto_director(self) -> None:
        """Select a conservative camera preset before reading UI settings.

        Without scanned kills we use the existing 'auto' camera motion logic.
        No GPU/render API is called here and no camera coordinate logic is changed.
        """
        multikill = max((int(getattr(k, 'multikill', 1)) for k in self.kills), default=1)
        if multikill >= 3:
            profile, arc, dolly = "dynamic", 20.0, 7.0
        elif multikill >= 2:
            profile, arc, dolly = "cinematic", 14.0, 5.0
        else:
            profile, arc, dolly = "auto", 10.0, 3.0
        self._set_camera_motion(profile, arc, dolly)

    def on_one_click(self, smart: bool = False) -> None:
        if not self._need_lock():
            return
        if self.var_auto_director.get():
            self._apply_auto_director()
        scene_cfg = self._scene_render_config()
        # Basic auto-create uses a plain template unless the explicitly named
        # smart action is used. This does not discard advanced saved edits.
        if self.var_edit_mode.get() == "easy" and not smart:
            scene_cfg = (False, scene_cfg[1], False, scene_cfg[3])
        self._run_bg(self._make, True, self.current_template(), bool(self.var_montage.get()), self.var_event_mode.get(), *scene_cfg)

    def _make(self, scan_first: bool, tpl: Template, montage: bool, event_mode: str = "キル",
              scene_mode=False, shots=None, auto=False, order=None) -> None:
        # Tk変数はUIスレッドで読み取り済み (tpl/montage は引数で受け取る)
        _diag_write(RUN_LOG, f"\n===== ALL_KILL_BEGIN {time.strftime('%Y-%m-%d %H:%M:%S')} player={getattr(self.locked, 'name', '?')} =====")
        p = self.locked                      # ジョブ開始時に固定 (UI選択が変わっても影響しない)
        if scan_first:
            self._scan(event_mode)
        if not self.kills:
            self.log("対象プレイヤーのキルがありません。")
            return
        try:
            src, own = self._ensure_source()
        except CaptureError as e:
            self.log(f"映像入力エラー: {e}")
            return
        res = None
        try:
            factory = None
            if tpl.game_audio:
                factory = (lambda path: SyntheticAudio(path)) if FAKE_CAPTURE else (lambda path: PreferredGameAudio(path))
            try:
                res = self._render_with_optional_scene_mode(src, p, list(self.kills), tpl, montage, factory,
                                                            scene_mode, shots or {}, auto, order)
            except Exception as e:
                # 全キル処理全体の例外をUI/プロセスへ漏らさず、診断情報を残す。
                self.log(f"全キル作成を安全停止: {type(e).__name__}: {e}")
                (ROOT / "diagnostics").mkdir(exist_ok=True)
                (ROOT / "diagnostics" / "last_error.txt").write_text(traceback.format_exc(), encoding="utf-8")
                return
        finally:
            if own:
                try:
                    src.stop()
                except Exception as e:
                    self.log(f"映像入力の停止処理をスキップ: {e}")
        if res is not None:
            self.log(f"完了: {len(res.outputs)} 本" + (f" / 失敗 {len(res.failed)}" if res.failed else ""))
            _diag_write(RUN_LOG, f"===== ALL_KILL_END outputs={len(res.outputs)} failed={len(res.failed)} =====")

    def on_stop(self) -> None:
        self.stop_ev.set()
        self.log("中止を要求しました…")

    def on_pick_out(self) -> None:
        p = filedialog.askdirectory(initialdir=str(self.out_root))
        if p:
            self.out_root = Path(p)
            self.lbl_out.configure(text=p)
            if hasattr(self, "var_out_right"):
                self.var_out_right.set(str(p))
            self._save_settings()

    def on_open_out(self) -> None:
        self.out_root.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(self.out_root))  # type: ignore[attr-defined]

    # ミラー (LoLウィンドウのみ)
    def on_mirror_start(self) -> None:
        try:
            if FAKE_CAPTURE:
                self.source = SyntheticSource(time_fn=lambda: time.time() % 600)
            else:
                self.source = WGCWindowSource()
            self.source.start()
            self.log("ミラー開始 (LoLウィンドウのみ)。")
        except CaptureError as e:
            self.source = None
            self.log(f"ミラー開始失敗: {e}")

    def on_mirror_stop(self) -> None:
        if self.source:
            self.source.stop()
            self.source = None
            self.canvas.delete("all")
        if hasattr(self, "var_mirror"):
            self.var_mirror.set(False)

    def _current_frame_rgb(self, cw: int, ch: int):
        """LoLミラー映像だけをプレビューに使用する。サンプル画像は表示しない。"""
        if self.source is not None and self.source.running:
            fr = self.source.latest()
            if fr is not None:
                img = Image.fromarray(fr[..., [2, 1, 0]])
                img.thumbnail((cw, ch), Image.Resampling.LANCZOS)
                return np.asarray(img), "mirror"
        return None, "empty"

    def _selected_multikill(self) -> int:
        sel = self.lb_kills.curselection()
        if sel and sel[0] < len(self.kills):
            return self.kills[sel[0]].multikill
        return 1

    def _preview_tick(self) -> None:
        try:
            cw, ch = max(160, self.canvas.winfo_width()), max(90, self.canvas.winfo_height())
            live = bool(self.var_live.get())
            mirror_on = self.source is not None and self.source.running
            self.canvas.delete("all")
            rgb, kind = self._current_frame_rgb(cw, ch)
            if rgb is not None:
                if live and not self.busy:
                    t = self.current_template()
                    if hasattr(self, "curve_editor"):
                        self.curve_editor.set_histogram(rgb)
                    # ミラー表示はReplay APIへHUD/camera設定を送らず、画面上だけテンプレートを近似適用する。
                    rgb = apply_camera_preview(rgb, t)
                    rgb = apply_video_effect_preview(rgb, t, phase=0.5)
                    rgb = compose_compare(rgb, t, preview_title(t, self._selected_multikill()), float(self.var_split.get()))
                self._photo = ImageTk.PhotoImage(Image.fromarray(rgb))
                self.canvas.create_image(cw // 2, ch // 2, image=self._photo)
                if live and not self.busy:
                    cam = STYLES.get(t.style, t.style)
                    hud = "HUD安全モード" if t.hide_hud else "HUDそのまま"
                    self.canvas.create_text(8, 8, anchor="nw", fill="#a7f3d0",
                                            text=f"テンプレ反映 / カメラ: {cam} / {hud}")
            else:
                self.canvas.create_text(cw // 2, ch // 2, anchor="center",
                                        fill="#94A3B8", font=("Meiryo UI", 12, "bold"),
                                        text="LoLミラーを開始するとここに実映像が表示されます")
        except Exception:
            pass
        # During encoding, don't run costly Tk/PIL CPU preview effects at 60 Hz.
        # Mirror remains visible; update it at ~10 Hz while a job is running.
        self.root.after(100 if self.busy else 16, self._preview_tick)

    def on_exact_still(self) -> None:
        try:
            cw, ch = 960, 540
            rgb, _ = self._current_frame_rgb(cw, ch)
            if rgb is None:
                raise RuntimeError("LoLミラーを開始してから「1枚だけ更新」を実行してください。")
            out = Path(self.out_root) / "preview_exact.png"
            render_exact_still(rgb, self.current_template(), out)
            self.log(f"正確なプレビューを保存: {out} (最終出力と同じフィルタ。タイトル/切替演出は除く)")
            if sys.platform == "win32":
                os.startfile(str(out))  # type: ignore[attr-defined]
        except Exception as e:
            self.log(f"正確なプレビュー失敗: {e}")

    def on_preview_stop(self) -> None:
        """カメラ演出プレビューだけを停止する。録画ジョブと同じ停止イベントを安全に使う。"""
        self.stop_ev.set()
        try:
            if self.api is not None:
                self.api.set_playback(paused=True, speed=1.0)
        except Exception:
            pass
        self.log("カメラ演出プレビューを停止しました。")

    def on_preview_play(self) -> None:
        """LoL上で、テンプレートのカメラ演出(追従/ズーム/スロー/HUD非表示)を録画せずに再生して確認。"""
        if not self._need_lock():
            return
        tpl = self.current_template()
        sel = self.lb_kills.curselection()
        kill = self.kills[sel[0]] if (sel and sel[0] < len(self.kills)) else (self.kills[0] if self.kills else None)
        if kill is not None and self.var_scene_mode.get():
            shot = self.scene_project.shots.get(scene_key(kill))
            if shot is None and self.var_auto_director.get():
                shot = recommend(kill, tpl.pre, tpl.post)
            if shot is not None:
                tpl = apply_shot(tpl, shot)
        self._run_bg(self._preview_play, tpl, kill)

    def _preview_play(self, tpl, kill) -> None:
        from core.scanner import Kill
        if kill is None:           # スキャン前は「今の再生位置 + 3秒」をキル扱いにして演出だけ確認
            now = float(self.api.playback().get("time", 0.0))
            kill = Kill(-1, now + 3.0, self.locked.name, "-", [])
        start, end = max(0.0, kill.time - tpl.pre), kill.time + tpl.post
        self.log(f"カメラ演出プレビュー: {int(kill.time // 60):02d}:{kill.time % 60:04.1f} 付近 (録画はしません。ミラーを開始すると見やすい)")
        rig = preview_clip(self.api, self.locked, tpl, start, end, [kill], stop=self.stop_ev, log=self.log)
        self.log("カメラ: " + (rig.note or rig.mode) + f" / 横回転 {getattr(tpl, 'third_yaw', 0.0):+.0f}°")


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
