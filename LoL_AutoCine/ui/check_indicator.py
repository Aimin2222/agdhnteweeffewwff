# -*- coding: utf-8 -*-
"""Antialiased high-DPI blue ✓ checkbox images for the white UI."""
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk


def install(root, style):
    try:
        size, oversample = 26, 4
        def icon(checked=False, disabled=False):
            S=oversample
            im=Image.new("RGBA",(size*S,size*S),(0,0,0,0))
            pen=ImageDraw.Draw(im)
            fill=(38,110,215,255) if checked else (255,255,255,255)
            border=(34,91,184,255) if checked else (124,139,163,255)
            pen.rounded_rectangle((3*S,3*S,23*S,23*S),radius=5*S,
                                  fill=fill,outline=border,width=2*S)
            if checked:
                pen.line([(7*S,13*S),(11*S,17*S),(19*S,8*S)],
                         fill=(255,255,255,255),width=3*S,joint="curve")
            im=im.resize((size,size),Image.Resampling.LANCZOS)
            if disabled:
                im.putalpha(im.getchannel("A").point(lambda alpha:int(alpha*0.4)))
            return ImageTk.PhotoImage(im,master=root)
        unchecked,checked,disabled_unchecked,disabled_checked=(
            icon(),icon(True),icon(False,True),icon(True,True))
        root._autocine_check_images=(unchecked,checked,disabled_unchecked,disabled_checked)
        style.element_create("AutoCine.Check","image",unchecked,
                             ("disabled","selected",disabled_checked),
                             ("disabled",disabled_unchecked),
                             ("selected",checked),sticky="w")
        style.layout("TCheckbutton",[("Checkbutton.padding",{"sticky":"nswe","children":[
            ("AutoCine.Check",{"side":"left","sticky":"w"}),
            ("Checkbutton.label",{"side":"left","sticky":"w"})]})])
        style.configure("TCheckbutton",padding=(2,3))
        return True
    except Exception:
        return False
