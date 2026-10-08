# -*- coding: utf-8 -*-
"""LoL AutoCine - Phase 1 UI prototype.

The original application remains in legacy_app.py and core/ untouched.
This phase intentionally focuses on reproducing the supplied white UI first.
Function wiring is added incrementally in later phases.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

ROOT = Path(__file__).resolve().parent
APP = "LoL AutoCine v4.1"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP)
        self.root.geometry("1536x980+30+20")
        self.root.minsize(1200, 760)
        self.root.configure(bg="#F5F8FC")
        self.vars = {}
        self._setup_style()
        self._build()

    def _setup_style(self):
        s = ttk.Style(self.root)
        try: s.theme_use("clam")
        except tk.TclError: pass
        bg="#F5F8FC"; white="#FFFFFF"; text="#172033"; muted="#6B7890"; line="#DCE4EF"; blue="#1677FF"; blue2="#0B63D8"; pale="#EEF6FF"
        s.configure("TFrame", background=bg)
        s.configure("Card.TFrame", background=white)
        s.configure("TLabel", background=bg, foreground=text, font=("Meiryo UI",10))
        s.configure("Card.TLabel", background=white, foreground=text, font=("Meiryo UI",10))
        s.configure("Muted.TLabel", background=white, foreground=muted, font=("Meiryo UI",9))
        s.configure("Title.TLabel", background=bg, foreground="#12213A", font=("Meiryo UI",18,"bold"))
        s.configure("SubTitle.TLabel", background=bg, foreground=muted, font=("Meiryo UI",9))
        s.configure("Section.TLabel", background=white, foreground="#14213D", font=("Meiryo UI",11,"bold"))
        s.configure("TButton", background=white, foreground="#344054", bordercolor=line, padding=(10,7), font=("Meiryo UI",9))
        s.map("TButton", background=[("active", "#F0F6FF")])
        s.configure("Blue.TButton", background=blue, foreground=white, borderwidth=0, padding=(12,9), font=("Meiryo UI",10,"bold"))
        s.map("Blue.TButton", background=[("active",blue2)])
        s.configure("Nav.TButton", background=bg, foreground="#53627A", borderwidth=0, padding=(15,12), font=("Meiryo UI",10,"bold"))
        s.map("Nav.TButton", background=[("active",pale)], foreground=[("active",blue)])
        s.configure("TCombobox", fieldbackground=white, background=white, foreground=text, bordercolor=line, padding=5)
        s.configure("TEntry", fieldbackground=white, foreground=text, bordercolor=line, padding=5)
        s.configure("Horizontal.TScale", background=white, troughcolor="#E2E9F2")
        s.configure("TCheckbutton", background=white, foreground=text)
        s.configure("TRadiobutton", background=white, foreground=text)

    def card(self, parent, title=None, pad=10):
        f=ttk.Frame(parent, style="Card.TFrame", padding=pad)
        if title:
            ttk.Label(f,text=title,style="Section.TLabel").pack(fill="x",pady=(0,8))
        return f

    def _build(self):
        root=self.root
        # Header
        header=ttk.Frame(root,padding=(18,10,18,7)); header.pack(fill="x")
        brand=ttk.Frame(header); brand.pack(side="left")
        ttk.Label(brand,text="◈  LoL AutoCine v4.1",style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand,text="最高の瞬間を、映像に。",style="SubTitle.TLabel").pack(anchor="w")
        nav=ttk.Frame(header); nav.pack(side="left",padx=(55,0))
        for txt in ["⌂  ホーム","▣  テンプレート","▣  参考動画","⚙  設定"]:
            ttk.Button(nav,text=txt,style="Nav.TButton",command=lambda t=txt:self._nav(t)).pack(side="left")
        top_right=ttk.Frame(header); top_right.pack(side="right")
        ttk.Label(top_right,text="出力FPS",style="SubTitle.TLabel").pack(side="left",padx=(0,5))
        fps=ttk.Combobox(top_right,values=["30 FPS","60 FPS","120 FPS"],state="readonly",width=9); fps.set("60 FPS"); fps.pack(side="left")
        ttk.Button(top_right,text="＋",width=3,command=lambda:self._toast("追加設定")).pack(side="left",padx=4)
        ttk.Button(top_right,text="⚙",width=3,command=lambda:self._toast("設定")).pack(side="left")

        # Main grid
        body=ttk.Frame(root,padding=(10,0,10,6)); body.pack(fill="both",expand=True)
        body.columnconfigure(0,weight=0,minsize=310); body.columnconfigure(1,weight=1,minsize=600); body.columnconfigure(2,weight=0,minsize=320); body.rowconfigure(0,weight=1)
        self._build_left(body)
        self._build_center(body)
        self._build_right(body)

        footer=ttk.Frame(root,padding=(15,6,15,7)); footer.pack(fill="x")
        ttk.Label(footer,text="●  準備完了",foreground="#159A6B").pack(side="left")
        ttk.Label(footer,text="▣  参考動画",foreground="#5D6A80").pack(side="right",padx=18)
        ttk.Label(footer,text="▣  テンプレート",foreground="#5D6A80").pack(side="right",padx=18)
        ttk.Label(footer,text="◆  自動編集",foreground="#5D6A80").pack(side="right",padx=18)
        ttk.Label(footer,text="♥  LoLで最高の瞬間を",foreground="#EF5B78").pack(side="right",padx=18)

    def _build_left(self,parent):
        left=ttk.Frame(parent); left.grid(row=0,column=0,sticky="nsew",padx=(0,8)); left.rowconfigure(1,weight=1); left.rowconfigure(2,weight=1)
        add=self.card(left,"◉  参考動画の追加",8); add.grid(row=0,column=0,sticky="ew",pady=(0,8))
        mode=ttk.Combobox(add,values=["X / YouTube / URLから追加","ローカル動画から追加"],state="readonly"); mode.set("X / YouTube / URLから追加"); mode.pack(fill="x",pady=(0,7))
        row=ttk.Frame(add,style="Card.TFrame"); row.pack(fill="x")
        ttk.Button(row,text="▶  YouTube").pack(side="left",fill="x",expand=True,padx=(0,4)); ttk.Button(row,text="𝕏  X (Twitter)").pack(side="left",fill="x",expand=True,padx=(4,0))
        e=ttk.Entry(add); e.insert(0,"https://www.youtube.com/watch?v=..."); e.pack(fill="x",pady=7)
        ttk.Button(add,text="↓  動画を取得",style="Blue.TButton",command=lambda:self._toast("動画取得はPhase 2で接続します")).pack(fill="x")

        refs=self.card(left,"◉  参考動画リスト",8); refs.grid(row=1,column=0,sticky="nsew",pady=(0,8)); refs.rowconfigure(1,weight=1)
        items=[("League of Legends Montage","2025-05-17 14:32"),("Faker - Best Moments","2025-05-16 21:10"),("Zed One Shot","2025-05-15 18:45"),("Katarina Montage","2025-05-14 12:20")]
        for name,date in items:
            row=ttk.Frame(refs,style="Card.TFrame",padding=(0,5)); row.pack(fill="x")
            thumb=tk.Frame(row,bg="#24314B",width=68,height=48); thumb.pack(side="left",padx=(0,8)); thumb.pack_propagate(False); tk.Label(thumb,text="LoL",fg="white",bg="#24314B",font=("Arial",12,"bold")).pack(expand=True)
            info=ttk.Frame(row,style="Card.TFrame"); info.pack(side="left",fill="x",expand=True); ttk.Label(info,text=name,style="Card.TLabel").pack(anchor="w"); ttk.Label(info,text=date,style="Muted.TLabel").pack(anchor="w")
            ttk.Button(row,text="♜",width=3,command=lambda n=name:self._toast(f"削除: {n}")).pack(side="right")
        ttk.Button(refs,text="テンプレート生成",style="Blue.TButton",command=lambda:self._toast("テンプレート生成はPhase 2で接続します")).pack(fill="x",pady=(7,0))

        tpl=self.card(left,"▣  テンプレート",8); tpl.grid(row=2,column=0,sticky="nsew")
        for i,name in enumerate(["標準シネマティック","LoLnam風シネマ","自動カメラモーション","ダイナミックアクション","マルチキル向け"]):
            b=ttk.Button(tpl,text=("◆  " if i==1 else "◇  ")+name+"   ›",anchor="w",style="TButton",command=lambda n=name:self._toast(f"テンプレート: {n}")); b.pack(fill="x",pady=2)
            if i==1: b.configure(style="Blue.TButton")

    def _build_center(self,parent):
        center=ttk.Frame(parent); center.grid(row=0,column=1,sticky="nsew"); center.rowconfigure(0,weight=0); center.rowconfigure(1,weight=0); center.rowconfigure(2,weight=1); center.columnconfigure(0,weight=1)
        # Preview
        card=self.card(center,"カメラプレビュー",0); card.grid(row=0,column=0,sticky="ew",pady=(0,8)); card.configure(padding=0)
        preview_frame=tk.Frame(card,bg="#101722",height=470); preview_frame.pack(fill="x"); preview_frame.pack_propagate(False)
        img_path=ROOT/"preview_mock.png"
        if img_path.exists():
            im=Image.open(img_path).resize((850,484),Image.LANCZOS); self.preview_img=ImageTk.PhotoImage(im); tk.Label(preview_frame,image=self.preview_img,bg="#101722").pack(fill="both",expand=True)
        else: tk.Label(preview_frame,text="CAMERA PREVIEW",fg="white",bg="#101722",font=("Arial",20,"bold")).pack(expand=True)
        # overlay controls
        overlay=tk.Frame(preview_frame,bg="#101722"); overlay.place(x=14,y=10)
        tk.Label(overlay,text="カメラプレビュー",fg="white",bg="#101722",font=("Meiryo UI",10,"bold")).pack()
        bottom=tk.Frame(card,bg="#101722",height=38); bottom.pack(fill="x")
        tk.Label(bottom,text="00:12.4 / 00:32.0",fg="white",bg="#101722").pack(side="left",padx=14)
        self.preview_scale=tk.Scale(bottom,from_=0,to=32,orient="horizontal",showvalue=False,highlightthickness=0,bg="#101722",fg="white",troughcolor="#34445E",activebackground="#1677FF"); self.preview_scale.set(12.4); self.preview_scale.pack(side="left",fill="x",expand=True)
        tk.Label(bottom,text="🔊  1.0x  ⛶  ⚙",fg="white",bg="#101722").pack(side="right",padx=12)

        # Timeline
        tl=self.card(center,"♟  カメラ動作タイムライン",10); tl.grid(row=1,column=0,sticky="ew",pady=(0,8))
        c=tk.Canvas(tl,height=58,bg="#FFFFFF",highlightthickness=0); c.pack(fill="x")
        c.create_line(18,30,850,30,fill="#2B9DFF",width=3)
        for x,color in [(120,"#377DFF"),(150,"#2EB67D"),(330,"#E24B6D"),(415,"#E24B6D"),(625,"#377DFF"),(845,"#377DFF")]: c.create_oval(x-4,26,x+4,34,fill=color,outline="")
        c.create_text(120,12,text="キル前",fill="#52627A"); c.create_text(400,12,text="キル瞬間",fill="#52627A"); c.create_text(625,12,text="キル後",fill="#52627A")
        c.create_text(18,50,text="0s",fill="#52627A",anchor="w"); c.create_text(225,50,text="8s",fill="#52627A"); c.create_text(430,50,text="16s",fill="#52627A"); c.create_text(635,50,text="24s",fill="#52627A"); c.create_text(850,50,text="32s",fill="#52627A",anchor="e")

        # Camera settings
        cam=self.card(center,"♟  カメラ設定",10); cam.grid(row=2,column=0,sticky="nsew")
        cam.columnconfigure(1,weight=1); cam.columnconfigure(3,weight=1)
        ttk.Label(cam,text="カメラモード",style="Card.TLabel").grid(row=0,column=0,sticky="w",pady=4)
        modes=["👤 三人称（通常）","👥 三人称（シネマ）","▣ FPS風","▣ 固定カメラ"]
        for j,m in enumerate(modes):
            ttk.Button(cam,text=m,style="Blue.TButton" if j==0 else "TButton",command=lambda n=m:self._toast(n)).grid(row=0,column=j+1,sticky="ew",padx=3)
        ttk.Label(cam,text="カメラの追従対象",style="Card.TLabel").grid(row=1,column=0,sticky="w",pady=8)
        cb=ttk.Combobox(cam,values=["🎯 キル対象（自動）","プレイヤー","手動指定"],state="readonly"); cb.set("🎯 キル対象（自動）"); cb.grid(row=1,column=1,columnspan=2,sticky="ew",padx=3)
        ttk.Button(cam,text="対象を手動指定").grid(row=1,column=3,sticky="ew",padx=3)
        # sliders left
        self._slider(cam,2,"追従距離",0,12,6.0,"follow_distance")
        self._slider(cam,3,"高さ",0,6,2.5,"height")
        self._slider(cam,4,"追従スムーズ",0,1,0.7,"smooth")
        ttk.Checkbutton(cam,text="常に対象を画面中央に表示").grid(row=5,column=0,columnspan=2,sticky="w",pady=6)
        orbit=ttk.Frame(cam,style="Card.TFrame",padding=(10,0)); orbit.grid(row=2,column=2,rowspan=4,columnspan=2,sticky="nsew")
        ttk.Label(orbit,text="Orbit（横回転）",style="Section.TLabel").pack(anchor="w")
        ttk.Checkbutton(orbit,text="有効").pack(anchor="w")
        self._slider(orbit,1,"回転速度",0,5,2.0,"orbit_speed",pack=True)
        ttk.Label(orbit,text="回転角度",style="Card.TLabel").pack(anchor="w",pady=(7,2)); ttk.Combobox(orbit,values=["-90° ～ +90°","-180° ～ +180°","自由設定"],state="readonly").pack(fill="x")
        ttk.Label(orbit,text="自動カメラモーション",style="Card.TLabel").pack(anchor="w",pady=(7,2)); ttk.Combobox(orbit,values=["Cinematic（LoLnam風）","Natural","Dynamic","Custom"],state="readonly").pack(fill="x")

    def _slider(self,parent,row,label,a,b,val,key,pack=False):
        var=tk.DoubleVar(value=val); self.vars[key]=var
        box=ttk.Frame(parent,style="Card.TFrame")
        if pack:
            box.pack(fill="x",pady=2)
            ttk.Label(box,text=label,style="Card.TLabel").pack(anchor="w")
            inner=ttk.Frame(box,style="Card.TFrame"); inner.pack(fill="x")
            ttk.Scale(inner,from_=a,to=b,variable=var,orient="horizontal").pack(side="left",fill="x",expand=True)
            value=ttk.Label(inner,text=f"{val:.1f}",style="Card.TLabel",width=5); value.pack(side="right")
            var.trace_add("write",lambda *_:value.config(text=f"{var.get():.1f}"))
        else:
            box.grid(row=row,column=0,columnspan=2,sticky="ew",pady=2)
            box.columnconfigure(1,weight=1)
            ttk.Label(box,text=label,style="Card.TLabel").grid(row=0,column=0,sticky="w")
            ttk.Scale(box,from_=a,to=b,variable=var,orient="horizontal").grid(row=0,column=1,sticky="ew",padx=8)
            value=ttk.Label(box,text=f"{val:.1f}",style="Card.TLabel",width=5); value.grid(row=0,column=2)
            var.trace_add("write",lambda *_:value.config(text=f"{var.get():.1f}"))

    def _build_right(self,parent):
        right=ttk.Frame(parent); right.grid(row=0,column=2,sticky="nsew",padx=(8,0))
        canvas=tk.Canvas(right,bg="#F5F8FC",highlightthickness=0,width=330); sb=ttk.Scrollbar(right,orient="vertical",command=canvas.yview); canvas.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y"); canvas.configure(yscrollcommand=sb.set)
        inner=ttk.Frame(canvas); win=canvas.create_window((0,0),window=inner,anchor="nw",width=320)
        inner.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all"))); canvas.bind("<Configure>",lambda e:canvas.itemconfigure(win,width=e.width))
        def wheel(e): canvas.yview_scroll(int(-e.delta/120),"units")
        canvas.bind_all("<MouseWheel>",wheel,add="+")

        c=self.card(inner,"⚙  LoLnam風シネマ",10); c.pack(fill="x",pady=(0,8)); self._switch(c)
        ttk.Label(c,text="シネマンティックテンプレート",style="Card.TLabel").pack(anchor="w"); ttk.Combobox(c,values=["LoLnam風シネマ","Standard Cinematic","HERO","HYPE"],state="readonly").pack(fill="x",pady=4)
        for x in ["キル前：少し戻る","キル時：回り込み","キル後：引く","マルチキル時：動きを強める"]: ttk.Checkbutton(c,text=x).pack(anchor="w",pady=2)
        self._slider_pack(c,"演出の強さ",0,2,1.0,"drama")

        c2=self.card(inner,"♞  自動カメラモーション",10); c2.pack(fill="x",pady=(0,8)); self._switch(c2)
        ttk.Label(c2,text="モーションタイプ",style="Card.TLabel").pack(anchor="w"); ttk.Combobox(c2,values=["Cinematic","Natural","Dynamic","Custom"],state="readonly").pack(fill="x",pady=4)
        for x in ["キル前のカメラ移動","キル瞬間のズーム","キル後の引き","マルチキル時の演出強化"]: ttk.Checkbutton(c2,text=x).pack(anchor="w",pady=2)

        c3=self.card(inner,"🎨 カラー / FX",10); c3.pack(fill="x",pady=(0,8))
        ttk.Label(c3,text="カラーグレード",style="Card.TLabel").pack(anchor="w"); ttk.Combobox(c3,values=["標準","フィルム","ノワール","ダーク","夕日","深夜青","ティール＆オレンジ","ネオン","紫霧"],state="readonly").pack(fill="x",pady=4)
        for label,a,b,v,key in [("色温度",-1,1,0,"temp"),("露出",-2,2,0,"exposure"),("コントラスト",0,2,1,"contrast"),("彩度",0,2,1,"sat"),("ビネット",0,1,0.2,"vignette"),("グレイン",0,1,0,"grain"),("ブルーム",0,1,0.15,"bloom"),("Fog",0,1,0.0,"fog")]: self._slider_pack(c3,label,a,b,v,key)
        for x in ["DOF","シネマ枠","カーブ補正"]: ttk.Checkbutton(c3,text=x).pack(anchor="w",pady=2)

        c4=self.card(inner,"⚙  その他の設定",10); c4.pack(fill="x",pady=(0,8))
        ttk.Checkbutton(c4,text="HUD非表示").pack(anchor="w"); ttk.Checkbutton(c4,text="音声クラッシュ防止").pack(anchor="w")
        ttk.Label(c4,text="出力FPS",style="Card.TLabel").pack(anchor="w",pady=(8,2)); ttk.Combobox(c4,values=["30 FPS","60 FPS","120 FPS"],state="readonly").pack(fill="x")
        ttk.Label(c4,text="出力形式",style="Card.TLabel").pack(anchor="w",pady=(8,2)); ttk.Combobox(c4,values=["MP4（高品質）","MP4（軽量）","PNG連番"],state="readonly").pack(fill="x")
        ttk.Button(c4,text="▶  動画を生成",style="Blue.TButton",command=lambda:self._toast("動画生成はPhase 3で接続します")).pack(fill="x",pady=(10,0))

    def _switch(self,parent):
        ttk.Checkbutton(parent,text="有効").pack(anchor="e")
    def _slider_pack(self,parent,label,a,b,val,key):
        var=tk.DoubleVar(value=val); self.vars[key]=var
        row=ttk.Frame(parent,style="Card.TFrame"); row.pack(fill="x",pady=3); row.columnconfigure(1,weight=1)
        ttk.Label(row,text=label,style="Card.TLabel").grid(row=0,column=0,sticky="w")
        ttk.Scale(row,from_=a,to=b,variable=var,orient="horizontal").grid(row=0,column=1,sticky="ew",padx=7)
        value=ttk.Label(row,text=f"{val:.2f}",style="Card.TLabel",width=5); value.grid(row=0,column=2)
        var.trace_add("write",lambda *_:value.config(text=f"{var.get():.2f}"))
    def _toast(self,text):
        messagebox.showinfo("LoL AutoCine",text)
    def _nav(self,text): self._toast(f"UIナビゲーション: {text}\n\nPhase 1ではUIを先に完成させています。")

def main():
    root=tk.Tk(); App(root); root.mainloop()

if __name__ == "__main__": main()
