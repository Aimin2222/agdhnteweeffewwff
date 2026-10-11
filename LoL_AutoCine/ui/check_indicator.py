# -*- coding: utf-8 -*-
"""High contrast blue ✓ indicator for multi-selection checkboxes.

Radio buttons retain their native single-choice indicators.
"""
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk


def _rounded(draw, xy, radius, *, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def install(root, style):
    try:
        def pic(selected=False, disabled=False, pressed=False):
            size=26
            scale=4
            canvas=size*scale
            im=Image.new('RGBA',(canvas,canvas),(0,0,0,0))
            d=ImageDraw.Draw(im)
            border=(149,163,184,255)
            fill=(255,255,255,255)
            if selected:
                fill=(46,111,219,255) if not pressed else (38,95,195,255)
                border=(46,111,219,255)
            elif pressed:
                fill=(244,247,251,255)
                border=(119,133,155,255)
            _rounded(d,(3*scale,3*scale,(size-3)*scale,(size-3)*scale),6*scale,
                     fill=fill,outline=border,width=2*scale)
            if selected:
                pts=[(6.5,13.2),(11.0,17.3),(19.0,8.2)]
                pts=[(x*scale,y*scale) for x,y in pts]
                d.line(pts,fill=(255,255,255,255),width=3*scale,joint='curve')
            im=im.resize((size,size),Image.Resampling.LANCZOS)
            if disabled:
                alpha=im.getchannel('A').point(lambda a:int(a*0.45))
                im.putalpha(alpha)
            return ImageTk.PhotoImage(im,master=root)
        unchecked=pic();checked=pic(True);pressed=pic(False,False,True)
        checked_pressed=pic(True,False,True);disabled=pic(False,True);checked_disabled=pic(True,True)
        root._autocine_check_images=(unchecked,checked,pressed,checked_pressed,disabled,checked_disabled)
        try:
            style.element_delete('AutoCine.Check')
        except Exception:
            pass
        style.element_create('AutoCine.Check', 'image', unchecked,
                             ('disabled', 'selected', checked_disabled),
                             ('disabled', disabled),
                             ('active', 'selected', checked_pressed),
                             ('selected', checked),
                             ('active', pressed),
                             sticky='w')
        style.layout('TCheckbutton', [('Checkbutton.padding', {'sticky':'nswe','children':[
            ('AutoCine.Check', {'side':'left','sticky':'w'}),
            ('Checkbutton.label', {'side':'left','sticky':'w'})]})])
        style.configure('TCheckbutton',padding=(2,3))
        return True
    except Exception:
        return False
