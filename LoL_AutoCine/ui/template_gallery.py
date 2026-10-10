# -*- coding: utf-8 -*-
"""Shared template color previews for quick cards and the full gallery.

Both formats use the same per-template source data; the thumbnails use
AutoCine's existing grade_rgb calculation, not hand-painted mock thumbnails.
"""
from __future__ import annotations

from typing import Any

GRADE_APPEARANCE = {
    "default": ("補正なし", "#748472", "#A4A993", "#D4C6A3", "元のLoLの色をそのまま使う"),
    "standard": ("自然な色", "#718B74", "#87A7A6", "#DECC93", "自然な明るさと彩度"),
    "film": ("柔らかいフィルム", "#766C67", "#B19B87", "#D9C5A1", "少し落ち着いた映画色"),
    "lolnam": ("映画風ティール＆金", "#355F70", "#9B9F8D", "#EAC189", "青緑の影と暖かいハイライト"),
    "tealorange": ("青緑 × オレンジ", "#2D6170", "#A47863", "#F6A659", "シネマティックな強い色の対比"),
    "golden": ("温かいゴールド", "#735632", "#C69A56", "#FFDC87", "キル瞬間の暖色を印象的に"),
    "iceblue": ("アイスブルー", "#263F6A", "#648CAF", "#BBDCF7", "涼しい青の映像"),
    "neon": ("ネオン", "#48256B", "#9E4BAA", "#65DDE1", "鮮やかな夜光・色の強調"),
    "purple": ("紫", "#35325C", "#8F5A9F", "#C5ABDA", "紫寄りの幻想的な色"),
    "noir": ("モノクロ", "#28292F", "#888A90", "#CFD0D0", "白黒に近い強い映画色"),
    "dark": ("暗め", "#232A34", "#596274", "#A59A8A", "暗い場所の臨場感"),
    "sunset": ("夕焼け", "#6E3432", "#C27854", "#FAC68B", "赤とオレンジの暖かい色"),
    "midnight": ("深夜青", "#1D284B", "#496588", "#A5BDCD", "寒色のミステリアスな色"),
    "drama": ("ドラマ", "#3E4057", "#9B847F", "#E0C4AC", "彩度控えめで人物が引き立つ"),
    "fade": ("フェード", "#687F86", "#A8AFA5", "#E0D6BE", "コントラストが柔らかい淡い色"),
    "highcontrast": ("高コントラスト", "#182D41", "#879999", "#F3CF7A", "陰影の差が強いパンチある色"),
}


def appearance(grade: str):
    return GRADE_APPEARANCE.get(str(grade), GRADE_APPEARANCE["standard"])


def template_info(template: Any) -> dict:
    tone, a, b, c, description = appearance(getattr(template, "grade", "standard"))
    style = getattr(template, "style", "follow")
    camera = {
        "third": "三人称・自然", "third_cinema": "三人称・シネマ",
        "lolnam_cinema": "Lolnam風Orbit", "cinema_top": "俯瞰シネマ",
        "cinema": "シネマ", "orbit": "Orbit", "follow": "追従"
    }.get(style, style)
    fx = getattr(template, "video_effects", {}) or {}
    enabled = [k for k, value in fx.items() if float(value or 0) > 0.01]
    return dict(tone=tone, colors=(a, b, c), description=description,
                camera=camera, effects=", ".join(enabled[:3]) or "追加FXなし",
                use="集団戦・複数キル向け" if "チーム" in template.name or "マルチ" in template.name
                    else "ワンクリック・キル編集向け")


def render_template_preview(template, width=280, height=158):
    """Use real grade pipeline for the color comparison (not a canned image)."""
    from PIL import Image
    from core.preview import sample_scene, grade_rgb
    rgb = sample_scene(width, height)
    return Image.fromarray(grade_rgb(rgb, template))


def draw_color_bars(canvas, colors, y0=1, bar_width=38, bar_height=20):
    canvas.delete("all")
    for i, color in enumerate(colors):
        x = i * (bar_width + 3) + 2
        canvas.create_rectangle(x, y0, x + bar_width, y0 + bar_height,
                                fill=color, outline="#D5DDE7")


def open_gallery(app):
    """Option B: dedicated browseable two-column template window.

    The existing inline quick-view swatch remains available as option A.
    Both call App.apply_template, so they can be A/B tested safely.
    """
    import tkinter as tk
    from tkinter import ttk
    from PIL import ImageTk

    active = getattr(app, "_template_gallery_window", None)
    if active is not None:
        try:
            if active.winfo_exists():
                active.lift()
                active.focus_force()
                return active
        except tk.TclError:
            pass

    win = tk.Toplevel(app.root)
    app._template_gallery_window = win
    win.title("LoL AutoCine｜テンプレート図鑑・色味比較")
    win.geometry("880x660")
    win.minsize(660, 480)
    win.configure(bg="#F4F7FB")
    win._previews = []
    head = ttk.Frame(win, padding=(14, 10))
    head.pack(fill="x")
    ttk.Label(head, text="テンプレート図鑑", font=("Meiryo UI", 15, "bold")).pack(anchor="w")
    ttk.Label(head, text="色見本とカメラ・エフェクトを比較。サンプルはAutoCineのカラー補正から生成しています。",
              wraplength=830).pack(anchor="w")
    ttk.Label(head, text="適用すると通常のかんたん編集・詳細編集とミラーに同じテンプレート設定が反映されます。",
              wraplength=830).pack(anchor="w")
    search_var = tk.StringVar()
    ttk.Entry(head, textvariable=search_var).pack(fill="x", pady=(6,0))
    ttk.Label(head, text="↑ 名前・色・カメラ名で検索", font=("Meiryo UI", 9)).pack(anchor="w")

    body = ttk.Frame(win)
    body.pack(fill="both", expand=True)
    scroll = tk.Canvas(body, bg="#F4F7FB", highlightthickness=0)
    sb = ttk.Scrollbar(body, orient="vertical", command=scroll.yview)
    inner = ttk.Frame(scroll)
    inner.bind("<Configure>", lambda _e: scroll.configure(scrollregion=scroll.bbox("all")))
    window_id = scroll.create_window((0,0), window=inner, anchor="nw")
    scroll.bind("<Configure>", lambda e: scroll.itemconfigure(window_id, width=max(1,e.width)))
    scroll.configure(yscrollcommand=sb.set)
    scroll.pack(side="left",fill="both",expand=True)
    sb.pack(side="right",fill="y")
    cards = []
    for i,(name, tpl) in enumerate(app.templates.items()):
        info = template_info(tpl)
        panel = ttk.Frame(inner, style="Card.TFrame",padding=8)
        panel.grid(row=i//2,column=i%2,sticky="nsew",padx=8,pady=7)
        ttk.Label(panel,text=name,style="Section.TLabel",wraplength=340).pack(anchor="w")
        try:
            photo = ImageTk.PhotoImage(render_template_preview(tpl, 320, 180),master=win)
            win._previews.append(photo)
            ttk.Label(panel, image=photo).pack(anchor="center",pady=4)
        except Exception:
            # A missing optional graphics package must not hide the controls.
            ttk.Label(panel, text="色サンプルを取得できません",style="CardMuted.TLabel").pack()
        bar=tk.Canvas(panel,width=130,height=23,background="#FFFFFF",highlightthickness=0)
        bar.pack(anchor="w")
        draw_color_bars(bar,info["colors"])
        ttk.Label(panel,text=f'色：{info["tone"]}｜{info["description"]}',
                  style="CardMuted.TLabel",wraplength=350).pack(anchor="w")
        ttk.Label(panel,text=f'カメラ：{info["camera"]}｜{info["effects"]}',
                  style="CardMuted.TLabel",wraplength=350).pack(anchor="w")
        ttk.Label(panel,text=f'おすすめ：{info["use"]}',style="CardMuted.TLabel").pack(anchor="w")

        def apply(name=name):
            app.var_tpl.set(name)
            app.apply_template(name)
            app.var_live.set(True)
            if hasattr(app,"_invalidate_preview_snapshot"):
                app._invalidate_preview_snapshot()
            app.log("テンプレート図鑑から適用: "+name)

        ttk.Button(panel,text="このテンプレートを適用",command=apply).pack(fill="x",pady=(5,0))
        cards.append((panel,(name+" "+info["tone"]+" "+info["camera"]+" "+info["description"]).casefold()))

    inner.columnconfigure(0, weight=1)
    inner.columnconfigure(1, weight=1)

    def filter_cards(*_):
        query=search_var.get().strip().casefold()
        index=0
        for frame,label in cards:
            if not query or query in label:
                frame.grid(row=index//2,column=index%2,sticky="nsew",padx=8,pady=7)
                index+=1
            else:
                frame.grid_remove()
        scroll.yview_moveto(0)

    search_var.trace_add("write",filter_cards)

    def wheel(event):
        if getattr(event,"delta",0):
            scroll.yview_scroll(-max(-8,min(8,int(event.delta/120))),"units")
        elif getattr(event,"num",0)==4:
            scroll.yview_scroll(-3,"units")
        else:
            scroll.yview_scroll(3,"units")
        return "break"

    # Bind in this window only; the main editor's combobox wheel protection stays intact.
    def bind_children(widget):
        widget.bind("<MouseWheel>",wheel,add="+")
        widget.bind("<Button-4>",wheel,add="+")
        widget.bind("<Button-5>",wheel,add="+")
        for child in widget.winfo_children():
            bind_children(child)

    bind_children(win)
    return win
