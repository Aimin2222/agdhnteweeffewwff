# -*- coding: utf-8 -*-
"""Accessible checkmark indicators for AutoCine's light ttk/clam UI.

Classic Tk/clam themes render a selected checkbox as a tiny X on Windows.
Draw a genuine white checkmark on a high-contrast blue tile without changing
ttk.Checkbutton variables, callbacks, keyboard bindings or checked state.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageTk
from tkinter import ttk, TclError


def install(root, style=None):
    style = style or ttk.Style(root)
    # Pixel-perfect 2x raster then Lanczos reduction for 100% Windows DPI.
    def picture(checked, disabled=False):
        w=40
        im=Image.new("RGBA", (w,w), (0,0,0,0))
        d=ImageDraw.Draw(im)
        bg=(34,104,205,255) if checked else (250,251,254,255)
        line=(151,161,177,255) if disabled else (53,87,130,255)
        d.rounded_rectangle((2,2,w-3,w-3), radius=7, fill=bg, outline=line, width=3)
        if checked:
            d.line([(9,20),(17,27),(31,12)],fill=(255,255,255,255),width=6,joint="curve")
        return ImageTk.PhotoImage(im.resize((20,20),Image.Resampling.LANCZOS),master=root)
    try:
        unchecked=picture(False)
        checked=picture(True)
        disabled=picture(False,True)
        style.element_create("AutoCine.Checkmark", "image", unchecked,
                             ("disabled",disabled), ("selected",checked),
                             sticky="w")
        def convert(items):
            output=[]
            for name,options in items:
                if name == "Checkbutton.indicator":
                    name="AutoCine.Checkmark"
                options=dict(options)
                if "children" in options:
                    options["children"]=convert(options["children"])
                output.append((name,options))
            return output
        style.layout("TCheckbutton", convert(style.layout("TCheckbutton")))
        root._autocine_checkbox_images=(unchecked,checked,disabled)
        return True
    except TclError:
        return False
