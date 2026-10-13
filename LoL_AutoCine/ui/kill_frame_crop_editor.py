# -*- coding: utf-8 -*-
"""Visual placement tool for extracting real decoration art from concept sheets.

Different generated board layouts can move the X motifs. This editor makes
source selection explicit instead of guessing and using substitute assets.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
from core.kill_frame_abcd import BY_CODE, boards_dir, load_board_regions, save_board_regions

REGION_NAMES={
    "weak":"装飾弱め（画像左側）",
    "strong":"装飾強め（画像右側）",
    "melee":"中央モチーフ：近接",
    "ranged":"中央モチーフ：遠隔",
    "hybrid":"中央モチーフ：ハイブリッド",
}

def open_crop_editor(parent,theme_code):
    if theme_code not in BY_CODE:
        messagebox.showwarning("切り出し位置","Dテーマを選んでください",parent=parent)
        return False
    file=boards_dir()/(theme_code+".png")
    if not file.is_file():
        messagebox.showwarning("元画像がありません",str(file),parent=parent)
        return False
    with Image.open(file) as loaded:
        origin=loaded.convert("RGBA")
    settings={key:list(value) for key,value in load_board_regions(theme_code).items()}
    preview=origin.copy()
    preview.thumbnail((900,620),Image.Resampling.LANCZOS)
    w,h=preview.size
    popup=tk.Toplevel(parent)
    popup.title("実画像の切り出し位置｜"+BY_CODE[theme_code].name)
    popup.geometry(f"{min(1240,w+280)}x{max(510,h+100)}")
    popup.transient(parent)
    panel=ttk.Frame(popup,padding=10);panel.pack(fill="both",expand=True)
    ttk.Label(panel,text="このチャットで作成した元画像を使用。四角をクリックして中央装飾を合わせてください。",wraplength=920).pack(anchor="w")
    body=ttk.Frame(panel);body.pack(fill="both",expand=True,pady=5)
    canvas=tk.Canvas(body,width=w,height=h,highlightthickness=1,highlightbackground="#9CA3AF")
    canvas.pack(side="left",anchor="n")
    preview_photo=ImageTk.PhotoImage(preview,master=popup)
    canvas.create_image(0,0,image=preview_photo,anchor="nw")
    canvas.image=preview_photo
    sidebar=ttk.Frame(body,padding=(12,0,0,0));sidebar.pack(side="left",fill="both",expand=True)
    which=tk.StringVar(value="weak")
    ttk.Label(sidebar,text="調整する装飾").pack(anchor="w")
    chooser=ttk.Combobox(sidebar,textvariable=which,values=list(REGION_NAMES),state="readonly")
    chooser.pack(fill="x",pady=4)
    ttk.Label(sidebar,text="weak/strong：上段の中央×\nmelee/ranged/hybrid：下段のモチーフ",wraplength=245).pack(anchor="w",pady=4)
    width_var=tk.DoubleVar(value=settings["weak"][2])
    height_var=tk.DoubleVar(value=settings["weak"][3])
    ttk.Label(sidebar,text="切り出し幅（比率）").pack(anchor="w")
    width_spin=ttk.Spinbox(sidebar,from_=.02,to=.35,increment=.005,textvariable=width_var,width=10)
    width_spin.pack(anchor="w",pady=4)
    ttk.Label(sidebar,text="切り出し高さ（比率）").pack(anchor="w")
    height_spin=ttk.Spinbox(sidebar,from_=.02,to=.35,increment=.005,textvariable=height_var,width=10)
    height_spin.pack(anchor="w",pady=4)
    status=ttk.Label(sidebar,text="",wraplength=240);status.pack(anchor="w",pady=5)
    outline=canvas.create_rectangle(0,0,1,1,outline="#FFE26B",width=3)
    small=ttk.Label(sidebar,text="元画像の切り出しを表示します",wraplength=230)
    small.pack(fill="x",pady=7)
    crop_photo=[None]

    def sync(_=None):
        code=which.get()
        width_var.set(settings[code][2]);height_var.set(settings[code][3])
        redraw()
    def redraw(*_):
        code=which.get();x,y,a,b=settings[code]
        canvas.coords(outline,(x-a/2)*w,(y-b/2)*h,(x+a/2)*w,(y+b/2)*h)
        try:
            box=((x-a/2)*origin.width,(y-b/2)*origin.height,(x+a/2)*origin.width,(y+b/2)*origin.height)
            clip=origin.crop(tuple(round(v) for v in box))
            clip.thumbnail((220,170),Image.Resampling.LANCZOS)
            crop_photo[0]=ImageTk.PhotoImage(clip,master=popup)
            small.configure(image=crop_photo[0],text="")
        except Exception as exc:status.configure(text=str(exc))
        status.configure(text="対象："+REGION_NAMES[code])
    def change_size(_=None):
        code=which.get()
        try:
            a=float(width_var.get());b=float(height_var.get())
            if .02<=a<=.35 and .02<=b<=.35:
                settings[code][2]=a;settings[code][3]=b
                redraw()
        except (ValueError,TypeError,tk.TclError):pass
    def place(event):
        code=which.get()
        settings[code][0]=max(.05,min(.95,event.x/w))
        settings[code][1]=max(.05,min(.95,event.y/h))
        redraw()
    chooser.bind("<<ComboboxSelected>>",sync)
    width_var.trace_add("write",change_size)
    height_var.trace_add("write",change_size)
    canvas.bind("<Button-1>",place)
    def save():
        try:
            save_board_regions(theme_code,settings)
            messagebox.showinfo("保存しました","切り出し位置を保存しました。図鑑のプレビューに反映されます。",parent=popup)
            popup.destroy()
        except Exception as exc:messagebox.showerror("保存に失敗しました",str(exc),parent=popup)
    ttk.Button(sidebar,text="この5か所を保存",command=save).pack(fill="x",pady=(10,4))
    ttk.Button(sidebar,text="閉じる",command=popup.destroy).pack(fill="x")
    redraw()
    return True
