# -*- coding: utf-8 -*-
"""High contrast blue ✓ indicator for multi-selection checkboxes.

Radio buttons retain their native single-choice indicators.
"""
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk


def install(root, style):
    try:
        def pic(selected=False, disabled=False):
            im=Image.new('RGBA',(21,21),(0,0,0,0))
            d=ImageDraw.Draw(im)
            d.rounded_rectangle((1,1,19,19),radius=4,outline=(115,129,150,255),width=2,
                                fill=(45,110,218,255) if selected else (255,255,255,255))
            if selected:
                d.line([(5,10),(9,14),(16,6)],fill=(255,255,255,255),width=3,joint='curve')
            if disabled:
                im.putalpha(im.getchannel('A').point(lambda a:int(a*.42)))
            return ImageTk.PhotoImage(im,master=root)
        unchecked=pic();checked=pic(True);disabled=pic(False,True)
        root._autocine_check_images=(unchecked,checked,disabled)
        style.element_create('AutoCine.Check', 'image', unchecked,
                             ('selected',checked),('disabled',disabled),sticky='w')
        style.layout('TCheckbutton', [('Checkbutton.padding', {'sticky':'nswe','children':[
            ('AutoCine.Check', {'side':'left','sticky':'w'}),
            ('Checkbutton.label', {'side':'left','sticky':'w'})]})])
        style.configure('TCheckbutton',padding=(2,3))
        return True
    except Exception:
        return False
