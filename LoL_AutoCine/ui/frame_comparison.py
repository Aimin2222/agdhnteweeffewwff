"""Small real-frame comparisons: pixel work in a bounded worker, Tk upload only."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
import numpy as np
from core.effects import Template
from core.preview import grade_rgb,apply_video_effect_preview
from ui.live_preview import LatestPreview


def _render_comparison(request):
    source,settings,width,height,with_effects=request
    if source is None or not source.running:return None,'LoLミラーを開始すると実フレームを比較できます。'
    raw=source.latest()
    if raw is None:return None,'ミラーのフレーム取得を待っています。'
    original=Image.fromarray(np.asarray(raw)[..., [2,1,0]].astype(np.uint8))
    original.thumbnail((width,height),Image.Resampling.LANCZOS)
    template=Template(**settings)
    graded=grade_rgb(np.asarray(original),template)
    after=apply_video_effect_preview(graded,template) if with_effects else graded
    combined=Image.new('RGB',(original.width*2,original.height))
    combined.paste(original,(0,0));combined.paste(Image.fromarray(after.astype(np.uint8)),(original.width,0))
    return combined,''



def render_comparison(request):
    try:return _render_comparison(request)
    except Exception as error:return None,'比較画像を生成できません：'+str(error)


def open_comparison(parent,source,template,*,title='',width=240,height=135,with_effects=False,hover=False,footer='',presets=None):
    popup=tk.Toplevel(parent)
    popup.title(title)
    if hover:
        popup.overrideredirect(True);popup.attributes('-topmost',True)
        popup.geometry(f'+{parent.winfo_rootx()}+{parent.winfo_rooty()+parent.winfo_height()+5}')
    buttons=ttk.Frame(popup)
    if presets:
        popup.geometry('1020x690');popup.transient(parent)
        buttons.pack(fill='x',padx=8,pady=8)
    label=ttk.Label(popup,text='比較画像を準備中…');label.pack(padx=9,pady=9)
    ttk.Label(popup,text='左：元の試合 ／ 右：適用後（静止画の近似）').pack(padx=9)
    if footer:ttk.Label(popup,text=footer,wraplength=width*2).pack(padx=9,pady=9)
    worker=popup._comparison_worker=LatestPreview(render_comparison)
    state={'closed':False,'after':None,'generation':0}
    def dispose(event):
        if event.widget is popup:
            state['closed']=True;worker.close()
            if state['after'] is not None:
                try:popup.after_cancel(state['after'])
                except tk.TclError:pass
    popup.bind('<Destroy>',dispose,add='+')
    def poll():
        if state['closed']:return
        result=worker.result(state['generation'])
        if result is None:
            state['after']=popup.after(30,poll);return
        picture,reason=result[1]
        if picture is None:label.configure(text=reason)
        else:
            popup._photo=ImageTk.PhotoImage(picture,master=popup)
            label.configure(image=popup._photo,text='')
        state['after']=None
    def select(selected):
        if state['closed']:return
        if state['after'] is not None:popup.after_cancel(state['after'])
        state['generation']+=1
        popup._selected_template=selected.name
        label.configure(image='',text='比較画像を準備中…')
        worker.submit(state['generation'],(source,selected.to_dict(),width,height,with_effects))
        state['after']=popup.after(30,poll)
    for caption,preset in presets or ():
        ttk.Button(buttons,text=caption,command=lambda p=preset:select(p)).pack(side='left',fill='x',expand=True,padx=4)
    if presets:ttk.Button(popup,text='閉じる',command=popup.destroy).pack(pady=8)
    select(presets[0][1] if presets else template)
    return popup
