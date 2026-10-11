# -*- coding: utf-8 -*-
"""Anti-aliased blue check marks for the Tk/ttk white UI.

The check mark is rasterized at 4x resolution then LANCZOS downsampled,
rather than using a platform-dependent small bitmap/glyph. This modifies
only the presentation of TCheckbutton; variable/command semantics remain
the native ttk implementation. Falls back gracefully when a theme refuses
a custom indicator element.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageTk

def _picture(checked: bool, disabled: bool):
    ratio, side = 4, 20
    size = side*ratio
    im = Image.new("RGBA",(size,size),(0,0,0,0))
    d = ImageDraw.Draw(im)
    xy=(3*ratio,3*ratio,(side-3)*ratio,(side-3)*ratio)
    fill=("#E8EEF5" if disabled else "#1677FF") if checked else "#FFFFFF"
    border="#AAB8C9" if disabled else ("#1677FF" if checked else "#8191A8")
    d.rounded_rectangle(xy,radius=4*ratio,fill=fill,outline=border,width=ratio*2)
    if checked:
        color="#FFFFFF" if not disabled else "#A0AEC2"
        d.line([(5*ratio,10*ratio),(9*ratio,14*ratio),(15*ratio,7*ratio)],
               fill=color,width=ratio*2+2,joint="curve")
    return im.resize((side,side),Image.Resampling.LANCZOS)

def install(root, style):
    try:
        pics=[ImageTk.PhotoImage(_picture(check,disable),master=root)
              for check,disable in ((False,False),(True,False),(False,True),(True,True))]
        # Keep references alive for the lifetime of Tk.
        root._autocine_checkbox_pictures=pics
        element="AutoCine.CrispCheck.indicator"
        if element not in style.element_names():
            style.element_create(element,"image",pics[0],
                ("disabled","selected",pics[3]),("selected",pics[1]),("disabled",pics[2]))
        def override(nodes):
            new=[]
            for name,opts in nodes:
                opts=dict(opts)
                if "children" in opts:
                    opts["children"]=override(opts["children"])
                new.append((element if name.endswith(".indicator") else name,opts))
            return new
        layout=style.layout("TCheckbutton")
        if layout:
            style.layout("TCheckbutton", override(layout))
        return True
    except Exception:
        # Never sacrifice application startup or audio/capture for UI polish.
        return False
