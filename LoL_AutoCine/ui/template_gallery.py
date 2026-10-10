# -*- coding: utf-8 -*-
"""Real LoL kill/assist scene previews, using AutoCine's live mirror snapshots.

No fake gameplay thumbnails: until a real frame is saved for a selected scene,
show instructions rather than an unrelated image. Preview does not send camera
commands and never touches the export/GPU/TargetLock pipelines.
"""
from __future__ import annotations

from typing import Any

from PIL import Image
import numpy as np

GRADE_APPEARANCE = {
    "default": ("補正なし", "#748472", "#A4A993", "#D4C6A3", "元のLoLの色をそのまま使う"),
    "standard": ("自然な色", "#718B74", "#87A7A6", "#DECC93", "自然な明るさと彩度"),
    "film": ("柔らかいフィルム", "#766C67", "#B19B87", "#D9C5A1", "落ち着いた映画色"),
    "lolnam": ("映画風ティール＆金", "#355F70", "#9B9F8D", "#EAC189", "青緑の影と暖かいハイライト"),
    "tealorange": ("青緑 × オレンジ", "#2D6170", "#A47863", "#F6A659", "映画風の強い色の対比"),
    "golden": ("温かいゴールド", "#735632", "#C69A56", "#FFDC87", "暖かい金色"),
    "iceblue": ("アイスブルー", "#263F6A", "#648CAF", "#BBDCF7", "冷たい青の色調"),
    "neon": ("ネオン", "#48256B", "#9E4BAA", "#65DDE1", "鮮やかな色"),
    "purple": ("紫", "#35325C", "#8F5A9F", "#C5ABDA", "幻想的な紫"),
    "noir": ("モノクロ", "#28292F", "#888A90", "#CFD0D0", "モノクロ風"),
    "dark": ("暗め", "#232A34", "#596274", "#A59A8A", "陰影の強調"),
    "sunset": ("夕焼け", "#6E3432", "#C27854", "#FAC68B", "赤とオレンジ"),
    "midnight": ("深夜青", "#1D284B", "#496588", "#A5BDCD", "濃い寒色"),
    "drama": ("ドラマ", "#3E4057", "#9B847F", "#E0C4AC", "彩度控えめ"),
    "fade": ("フェード", "#687F86", "#A8AFA5", "#E0D6BE", "淡い色"),
    "highcontrast": ("高コントラスト", "#182D41", "#879999", "#F3CF7A", "陰影を強調"),
}


def appearance(grade: str):
    return GRADE_APPEARANCE.get(str(grade), GRADE_APPEARANCE['standard'])


def template_info(template: Any) -> dict:
    tone, a, b, c, description = appearance(getattr(template, 'grade', 'standard'))
    style = getattr(template, 'style', 'follow')
    cameras = {'third':'三人称・自然', 'third_cinema':'三人称・シネマ',
               'lolnam_cinema':'Lolnam風Orbit', 'cinema_top':'俯瞰シネマ',
               'cinema':'シネマ', 'orbit':'Orbit', 'follow':'追従'}
    fx = getattr(template, 'video_effects', {}) or {}
    enabled = [k for k, v in fx.items() if float(v or 0) > .01]
    return dict(tone=tone, colors=(a,b,c), description=description,
                camera=cameras.get(style,style), effects=', '.join(enabled[:3]) or '追加FXなし',
                use='集団戦向け' if 'チーム' in template.name or 'マルチ' in template.name
                else 'キル／アシスト編集向け')


def render_template_preview(template, width=280, height=158):
    """Compatibility method for legacy callers; gallery itself requires a real frame."""
    from core.preview import sample_scene, grade_rgb
    return Image.fromarray(grade_rgb(sample_scene(width,height), template))


def draw_color_bars(canvas, colors, y0=1, bar_width=38, bar_height=20):
    canvas.delete('all')
    for i, col in enumerate(colors):
        x = i * (bar_width+3)+2
        canvas.create_rectangle(x,y0,x+bar_width,y0+bar_height,fill=col,outline='#D5DDE7')


def render_scene_comparison(real_frame: Image.Image, template: Any,
                            width: int=150, height: int=85) -> Image.Image:
    """Same *real* source frame on both sides; grade/2D effects on right.

    Camera and temporal effects cannot be reconstructed from a single frame.
    Only the explicitly supported single-frame grade/video FX are displayed.
    """
    from core.preview import grade_rgb, apply_video_effect_preview
    if width < 8 or height < 8:
        raise ValueError('Preview too small')
    before = real_frame.convert('RGB').resize((width,height),Image.Resampling.LANCZOS)
    rgb = np.asarray(before)
    after = grade_rgb(rgb,template)
    after = apply_video_effect_preview(after,template,phase=.5)
    compared = Image.new('RGB',(width*2+3,height),(19,28,42))
    compared.paste(before,(0,0))
    compared.paste(Image.fromarray(after),(width+3,0))
    return compared


def scene_labels(kills):
    from ui.scene_project import scene_key
    names = []
    for i, kill in enumerate(kills):
        role = 'アシスト' if getattr(kill, 'role', 'kill') == 'assist' else 'キル'
        names.append((f'{i+1:03d}｜{role}｜{float(kill.time):.1f}s｜'
                      f'{str(kill.killer)} → {str(kill.victim)}', scene_key(kill), kill))
    return names



def _render_real_scene_request(request):
    """Read and process real frames off Tk; requests contain paths/plain settings."""
    from core.effects import Template
    path, settings = request
    try:
        with Image.open(path) as im:
            image = im.convert('RGB').copy()
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return (None, [])
    comparisons = []
    for values in settings:
        try:
            tpl = Template(**values)
            comparisons.append((render_scene_comparison(image,tpl,150,85), None))
        except Exception as exc:
            comparisons.append((None, str(exc)[:65]))
    return (True, comparisons)

def open_gallery(app):
    """Option B: searchable real-frame gallery, with capture per selected event."""
    import tkinter as tk
    from tkinter import ttk, messagebox
    from PIL import ImageTk

    from ui.live_preview import LatestPreview
    scenes = scene_labels(getattr(app, 'kills', []))
    signature = tuple((label, key) for label, key, _ in scenes)
    previous = getattr(app, '_template_gallery_window', None)
    if previous is not None:
        try:
            if previous.winfo_exists():
                if getattr(previous, '_scene_signature', None) == signature:
                    previous.lift()
                    previous.refresh_real_scene()
                    return previous
                previous.destroy()  # Scanning again may change selectable events.
        except tk.TclError:
            pass

    win = tk.Toplevel(app.root)
    win.title('LoL AutoCine｜実シーンでテンプレート比較')
    win.geometry('930x700')
    win.minsize(730, 490)
    app._template_gallery_window = win
    win._previews = []
    win._generation = 0
    win._scene_signature = signature
    worker = win._comparison_worker = LatestPreview(_render_real_scene_request)
    win.bind('<Destroy>', lambda event: worker.close() if event.widget is win else None, add='+')

    head = ttk.Frame(win,padding=(12,10))
    head.pack(fill='x')
    ttk.Label(head,text='テンプレートを実際のキル／アシスト映像で比較',
              font=('Meiryo UI',14,'bold')).pack(anchor='w')
    ttk.Label(head,text='同じシーンの 左：元映像 ／ 右：色・2D FX適用後 を比較します。'
              'カメラの位置や時間演出は静止画では再現されません。',
              wraplength=860).pack(anchor='w',pady=(2,4))
    scene_var = tk.StringVar(value=scenes[0][0] if scenes else '')
    top = ttk.Frame(head);top.pack(fill='x',pady=(4,2))
    ttk.Label(top,text='プレビュー元シーン').pack(side='left')
    select = ttk.Combobox(top, textvariable=scene_var, state='readonly',
                          values=[item[0] for item in scenes],width=67)
    select.pack(side='left',padx=8,fill='x',expand=True)
    status = tk.StringVar(value='キル／アシストをスキャンしてシーンを選んでください。'
                          if not scenes else '保存済みの実シーン画像を読み込みます。')
    ttk.Label(head,textvariable=status,wraplength=880).pack(anchor='w',pady=(3,3))
    act = ttk.Frame(head);act.pack(fill='x',pady=(3,4))
    search_var = tk.StringVar()
    ttk.Entry(head,textvariable=search_var).pack(fill='x',pady=(4,1))
    ttk.Label(head,text='↑ テンプレートの名前・色・カメラで検索',font=('Meiryo UI',9)).pack(anchor='w')

    body = ttk.Frame(win);body.pack(fill='both',expand=True)
    canvas = tk.Canvas(body,bg='#F4F7FB',highlightthickness=0)
    scrollbar = ttk.Scrollbar(body,orient='vertical',command=canvas.yview)
    inner = ttk.Frame(canvas)
    inner.bind('<Configure>',lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
    window_id = canvas.create_window((0,0),window=inner,anchor='nw')
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window_id,width=max(1,e.width)))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side='left',fill='both',expand=True)
    scrollbar.pack(side='right',fill='y')
    inner.columnconfigure(0,weight=1)
    inner.columnconfigure(1,weight=1)

    cards = []
    for i,(name,tpl) in enumerate(app.templates.items()):
        info=template_info(tpl)
        panel=ttk.Frame(inner,padding=7)
        panel.grid(row=i//2,column=i%2,sticky='nsew',padx=7,pady=6)
        ttk.Label(panel,text=name,font=('Meiryo UI',10,'bold'),wraplength=360).pack(anchor='w')
        preview=ttk.Label(panel,text='シーン画像を保存すると、ここに比較が出ます。',
                          wraplength=330)
        preview.pack(pady=(5,4))
        bar=tk.Canvas(panel,width=130,height=23,highlightthickness=0,bg='#FFFFFF')
        bar.pack(anchor='w')
        draw_color_bars(bar,info['colors'])
        ttk.Label(panel,text=f'色：{info["tone"]}｜{info["description"]}',
                  wraplength=350).pack(anchor='w')
        ttk.Label(panel,text=f'カメラ：{info["camera"]}｜{info["effects"]}',
                  wraplength=350).pack(anchor='w')
        def apply(n=name):
            app.var_tpl.set(n)
            app.apply_template(n)
            app.var_live.set(True)
            app._invalidate_preview_snapshot()
            status.set(f'適用：{n}（ミラーにも反映）')
        ttk.Button(panel,text='このテンプレートを適用',command=apply).pack(fill='x',pady=(6,0))
        query=' '.join((name,info['tone'],info['camera'],info['description'])).casefold()
        cards.append((panel,preview,tpl,query))

    def chosen():
        return next(((key,kill) for label,key,kill in scenes
                     if label==scene_var.get()),(None,None))

    def refresh():
        win._generation += 1
        token = win._generation
        key, _ = chosen()
        path = str(app._scene_thumbnail_path(key)) if key is not None else None
        # Take snapshots on Tk. The worker must never read Tk variables/widgets.
        settings = [tpl.to_dict() for _, _, tpl, _ in cards]
        for _, preview, _, _ in cards:
            preview.configure(image='', text='比較画像を準備中…')
        win._previews = []
        status.set('保存した実シーンから比較画像を準備しています。')
        worker.submit(token, (path, settings))

        def poll():
            if not win.winfo_exists() or token != win._generation:
                return
            result = worker.result(token)
            if result is None:
                win.after(20, poll)
                return
            exists, comparisons = result[1]
            if exists is None:
                for _, preview, _, _ in cards:
                    preview.configure(image='', text='実フレーム未保存：先にシーンへ移動して撮影')
                status.set('実シーンの画像がありません。①移動 → ミラーで場面確認 → ②保存 の順で操作してください。')
                return
            status.set('保存した実シーンを使用中。各カード：左が元映像、右がテンプレ適用後。')

            def present(index):
                if not win.winfo_exists() or token != win._generation or index >= len(cards):
                    return
                _, preview, _, _ = cards[index]
                comparison, error = comparisons[index]
                if comparison is None:
                    preview.configure(image='', text=f'この設定の表示に失敗：{error}')
                else:
                    photo = ImageTk.PhotoImage(comparison, master=win)
                    win._previews.append(photo)
                    preview.configure(image=photo, text='')
                win.after(4, lambda: present(index + 1))
            present(0)
        win.after(20, poll)

    def jump():
        _,kill=chosen()
        if kill is None:
            return
        if not app._need_lock():
            return
        if app.busy:
            status.set('録画／処理中です。終了後にシーンへ移動できます。')
            return
        app._run_bg(app._jump_to_kill,kill)
        status.set('選択シーンへ移動中。ミラーに正しいキル／アシストが映ったら②を押してください。')

    def capture():
        key,kill=chosen()
        if key is None:
            status.set('先にスキャンして、プレビュー元シーンを選んでください。')
            return
        if app.busy or app.source is None or not app.source.running:
            status.set('録画中は撮影できません。LoLミラーをONにしてから試してください。')
            return
        rgb,where=app._current_frame_rgb(960,540)
        if rgb is None or where != 'mirror':
            status.set('ミラーに有効なゲーム画面がありません。')
            return
        path=app._scene_thumbnail_path(key)
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            Image.fromarray(rgb).convert('RGB').save(path,'PNG')
            if app._current_scene() is not None and chosen()[0] == __import__('ui.scene_project',fromlist=['scene_key']).scene_key(app._current_scene()):
                app._show_scene_thumbnail(key)
        except Exception as exc:
            status.set(f'実シーン画像の保存失敗：{exc}')
            return
        refresh()
        app.log(f'テンプレ比較用の実フレーム保存: {kill.time:.1f}s / {path.name}')

    ttk.Button(act,text='① 選択シーンへ移動',command=jump).pack(side='left',padx=(0,8))
    ttk.Button(act,text='② ミラーの今の実フレームを保存・比較',command=capture).pack(side='left',padx=(0,8))
    ttk.Button(act,text='再表示',command=refresh).pack(side='left')
    select.bind('<<ComboboxSelected>>',lambda _:refresh())

    def filter_cards(*_):
        q=search_var.get().strip().casefold()
        ix=0
        for panel,_,_,name in cards:
            if not q or q in name:
                panel.grid(row=ix//2,column=ix%2,sticky='nsew',padx=7,pady=6)
                ix+=1
            else:
                panel.grid_remove()
        canvas.yview_moveto(0)
    search_var.trace_add('write',filter_cards)

    def wheel(event):
        app._preview_input(event)
        if event.delta:
            units=-max(-8,min(8,round(event.delta/120)))
        else:
            units=-3 if event.num==4 else 3
        canvas.yview_scroll(units,'units')
        return 'break'

    def bind_wheel(widget):
        if isinstance(widget,(ttk.Combobox,ttk.Spinbox,ttk.Entry)):
            return
        for seq in ('<MouseWheel>','<Button-4>','<Button-5>'):
            widget.bind(seq,wheel,add='+')
        for child in widget.winfo_children():
            bind_wheel(child)
    bind_wheel(inner)
    win.refresh_real_scene=refresh
    refresh()
    return win
