# -*- coding: utf-8 -*-
"""Full kill-frame gallery independent of the current LoL replay.

Keeps game/video thread untouched. UI thumbnails are generated in small batches
from the same core.kill_icons.make_badge renderer used for exported videos.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw

from core.kill_icons import STYLES, make_badge, ASSET_STYLES


def sample_portrait(rgb, name: str):
    """Neutral sample portrait; never impersonates a LoL champion or a live scene."""
    canvas = Image.new("RGB", (180, 180), rgb)
    d = ImageDraw.Draw(canvas)
    d.ellipse((30, 20, 150, 140), fill=tuple(min(255,x+40) for x in rgb))
    d.rounded_rectangle((42, 120, 138, 185), radius=22, fill=tuple(max(0,x-25) for x in rgb))
    d.text((9, 8), name, fill=(245, 245, 250))
    return canvas


def display_name(style):
    return STYLES.get(style, style)


class KillFrameGallery:
    """Searchable scrollable 2-column gallery with a right-side large preview."""
    def __init__(self, app):
        self.app=app
        self.win=tk.Toplevel(app.root)
        self.win.title("LoL AutoCine｜キルフレーム図鑑")
        self.win.geometry("1080x740")
        self.win.minsize(740, 500)
        self.win._kill_gallery=self
        self._photos=[]
        self._rendered={}
        self._queue=list(STYLES)
        self._preview_after=None
        self._chosen='premium_gold' if 'premium_gold' in STYLES else 'cinema'
        self._workdir=TemporaryDirectory(prefix="autocine_kill_gallery_")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        tmp=Path(self._workdir.name)
        a=tmp/"sample_left.png";b=tmp/"sample_right.png"
        sample_portrait((57,109,191),"A").save(a)
        sample_portrait((177,65,97),"B").save(b)
        self._icons=(a,b)

        heading=ttk.Frame(self.win,padding=10)
        heading.pack(fill="x")
        ttk.Label(heading,text="キルフレーム図鑑",font=("Meiryo UI",15,"bold")).pack(side="left")
        ttk.Label(heading,text="試合の撮影は不要。選択後はかんたん編集・詳細編集の両方に反映。",
                  wraplength=460).pack(side="left",padx=(18,4))
        self.search=tk.StringVar()
        ttk.Entry(heading,textvariable=self.search,width=22).pack(side="right")
        ttk.Label(heading,text="検索：",style="CardMuted.TLabel").pack(side="right")
        main=ttk.PanedWindow(self.win,orient="horizontal")
        main.pack(fill="both",expand=True)
        left=ttk.Frame(main)
        right=ttk.Frame(main,padding=12)
        main.add(left,weight=3);main.add(right,weight=2)
        self.canvas=tk.Canvas(left,background="#F6F7F9",highlightthickness=0)
        bar=ttk.Scrollbar(left,orient="vertical",command=self.canvas.yview)
        self.grid_parent=ttk.Frame(self.canvas)
        self.grid_parent.bind("<Configure>",lambda _e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.grid_id=self.canvas.create_window((0,0),window=self.grid_parent,anchor="nw")
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(self.grid_id,width=e.width))
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side="left",fill="both",expand=True)
        bar.pack(side="right",fill="y")
        self.cards=[]
        for idx,(style,title) in enumerate(STYLES.items()):
            panel=ttk.Frame(self.grid_parent,padding=7,style="Card.TFrame")
            panel.grid(row=idx//2,column=idx%2,sticky="nsew",padx=4,pady=4)
            ttk.Label(panel,text=title,wraplength=290).pack(anchor="w")
            image=ttk.Label(panel,text="プレビュー準備中…",cursor="hand2")
            image.pack(fill="x")
            image.bind("<Button-1>",lambda _e,s=style:self.select(s))
            ttk.Button(panel,text="選択・適用",command=lambda s=style:self.select(s,apply=True)).pack(fill="x",pady=(3,0))
            self.cards.append((style,title,panel,image))
        self.grid_parent.columnconfigure(0,weight=1)
        self.grid_parent.columnconfigure(1,weight=1)
        self.search.trace_add("write",self.filter_cards)
        self.canvas.bind("<MouseWheel>",self._wheel)
        self.grid_parent.bind("<MouseWheel>",self._wheel)
        for _,_,panel,im in self.cards:
            panel.bind("<MouseWheel>",self._wheel)
            im.bind("<MouseWheel>",self._wheel)
        ttk.Label(right,text="大きく確認",font=("Meiryo UI",12,"bold")).pack(anchor="w")
        self.title=ttk.Label(right,text="",wraplength=440)
        self.title.pack(anchor="w",pady=(4,8))
        self.preview=ttk.Label(right,text="読み込み中…")
        self.preview.pack(fill="x",pady=(6,8))
        ttk.Label(right,text="青／赤は見本の肖像です。実際の書き出しでは試合のチャンピオンアイコンになります。",
                  wraplength=410).pack(anchor="w")
        self.strength=tk.DoubleVar(value=float(app.var_kill_glow_strength.get()))
        ttk.Label(right,text="発光量（0〜2）").pack(anchor="w",pady=(12,1))
        ttk.Scale(right,variable=self.strength,from_=0,to=2,command=lambda _s:self._queue_preview()).pack(fill="x")
        self.glow_enabled=tk.BooleanVar(value=app.var_kill_glow_enabled.get())
        ttk.Checkbutton(right,text="追加発光をON",variable=self.glow_enabled,command=self._queue_preview).pack(anchor="w")
        ttk.Button(right,text="このフレームを適用",style="Accent.TButton",
                   command=lambda:self.select(self._chosen,apply=True)).pack(fill="x",pady=(10,5))
        ttk.Button(right,text="閉じる",command=self.close).pack(fill="x")
        self.status=ttk.Label(right,text="37種類以上を順に読み込んでいます。",wraplength=430)
        self.status.pack(anchor="w",pady=7)
        self.select(self._chosen)
        self.win.after(10,self._fill_batch)

    def _render(self,style,glow_strength=1.,glow_enabled=True):
        tmp=Path(self._workdir.name)/f"badge_{style}_{int(glow_strength*100)}_{int(glow_enabled)}.png"
        if not tmp.is_file():
            make_badge(tmp,style,killer_icon=self._icons[0],victim_icon=self._icons[1],
                       glow_strength=glow_strength,glow_enabled=glow_enabled)
        with Image.open(tmp) as im: return im.convert("RGBA").copy()

    def _fill_batch(self):
        if not self.win.winfo_exists(): return
        for _ in range(min(2,len(self._queue))):
            style=self._queue.pop(0)
            try:
                im=self._render(style,1.)
                im.thumbnail((280,92),Image.Resampling.LANCZOS)
                photo=ImageTk.PhotoImage(im,master=self.win)
                self._photos.append(photo)
                for key,_,_,label in self.cards:
                    if key==style:
                        label.configure(image=photo,text="")
                        break
            except Exception as error:
                for key,_,_,label in self.cards:
                    if key==style:
                        label.configure(text=f"プレビュー不可: {error}")
                        break
        self.status.configure(text=f"読み込み：{len(STYLES)-len(self._queue)} / {len(STYLES)}")
        if self._queue:self.win.after(40,self._fill_batch)

    def _queue_preview(self):
        if self._preview_after:
            self.win.after_cancel(self._preview_after)
        self._preview_after=self.win.after(180,self._refresh_preview)

    def _refresh_preview(self):
        self._preview_after=None
        if not self.win.winfo_exists(): return
        try:
            image=self._render(self._chosen,float(self.strength.get()),bool(self.glow_enabled.get()))
            image.thumbnail((460,175),Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(image,master=self.win)
            self.preview.configure(image=photo,text="")
            self._main_photo=photo
        except Exception as error:
            self.preview.configure(image="",text=str(error))

    def select(self,style,apply=False):
        if style not in STYLES:return
        self._chosen=style
        self.title.configure(text=f"{STYLES[style]} — {'素材型・高画質' if style in ASSET_STYLES else '描画型'}")
        self._queue_preview()
        if apply:
            self.app.var_kill_icon_style.set(STYLES[style])
            self.app.var_kill_glow_strength.set(float(self.strength.get()))
            self.app.var_kill_glow_enabled.set(bool(self.glow_enabled.get()))
            self.app._save_settings()
            self.app.log("キルフレーム図鑑から適用: "+STYLES[style])

    def filter_cards(self,*_):
        token=self.search.get().strip().casefold()
        idx=0
        for style,title,panel,_ in self.cards:
            if not token or token in title.casefold() or token in style.casefold():
                panel.grid(row=idx//2,column=idx%2,sticky="nsew",padx=4,pady=4)
                idx+=1
            else:panel.grid_remove()
        self.canvas.yview_moveto(0)

    def _wheel(self,e):
        d=getattr(e,'delta',0)
        n=-int(d/120) if d else (-3 if getattr(e,'num',0)==4 else 3)
        self.canvas.yview_scroll(n,"units")
        return "break"

    def close(self):
        if self._preview_after:
            try:self.win.after_cancel(self._preview_after)
            except tk.TclError:pass
        self._workdir.cleanup()
        self.win.destroy()


def open_gallery(app):
    previous=getattr(app,'_kill_frame_gallery',None)
    if previous and previous.win.winfo_exists():
        previous.win.lift()
        return previous.win
    app._kill_frame_gallery=KillFrameGallery(app)
    return app._kill_frame_gallery.win
