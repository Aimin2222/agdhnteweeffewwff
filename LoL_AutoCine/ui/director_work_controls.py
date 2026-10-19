"""Additional controls; legacy camera/badge controls remain available."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.smart_camera_director import CONTROL_MODES, SUPPORTED_STYLES

MODE_LABELS = {None: '既存プロジェクトの設定を維持', **CONTROL_MODES}
KEYS = ('camera_control_mode', 'camera_auto_excluded', 'camera_auto_qa_approved',
        'work_kill_frame_id', 'work_kill_effect_id', 'work_kill_review', 'work_kill_strength')


def initialize(app):
    app.var_camera_control_mode = tk.StringVar(value=MODE_LABELS[None])
    app.var_work_frame = tk.StringVar(value='')
    app.var_work_effect = tk.StringVar(value='')
    app.var_work_review = tk.BooleanVar(value=False)
    app.var_work_strength = tk.StringVar(value='strong')
    app.camera_auto_excluded = []
    app.camera_auto_qa_approved = {}


def values(app):
    if not hasattr(app, 'var_camera_control_mode'): return {}
    return dict(camera_control_mode=next((k for k, v in MODE_LABELS.items()
                                         if v == app.var_camera_control_mode.get()), None),
                camera_auto_excluded=list(app.camera_auto_excluded),
                camera_auto_qa_approved={k: list(v) for k, v in app.camera_auto_qa_approved.items()},
                work_kill_frame_id=app.var_work_frame.get(),
                work_kill_effect_id=app.var_work_effect.get(),
                work_kill_review=bool(app.var_work_review.get()),
                work_kill_strength=app.var_work_strength.get())


def restore(app, data):
    if not isinstance(data, dict) or not hasattr(app, 'var_camera_control_mode'): return
    app.var_camera_control_mode.set(MODE_LABELS.get(data.get('camera_control_mode'), MODE_LABELS[None]))
    app.camera_auto_excluded = list(data.get('camera_auto_excluded') or [])
    qa = data.get('camera_auto_qa_approved') or {}
    app.camera_auto_qa_approved = {k: list(v) for k, v in qa.items()
                                   if k in ('BLUE', 'RED') and isinstance(v, list)} if isinstance(qa, dict) else {}
    app.var_work_frame.set(str(data.get('work_kill_frame_id') or ''))
    app.var_work_effect.set(str(data.get('work_kill_effect_id') or ''))
    app.var_work_review.set(bool(data.get('work_kill_review', False)))
    app.var_work_strength.set('weak' if data.get('work_kill_strength') == 'weak' else 'strong')


def apply(app, template):
    for key, value in values(app).items(): setattr(template, key, value)
    return template


def build(app, parent):
    row = ttk.Frame(parent, style='Card.TFrame')
    row.pack(fill='x', pady=(6, 4))
    ttk.Label(row, text='カメラ制御', style='Card.TLabel', width=16).pack(side='left')
    ttk.Combobox(row, state='readonly', textvariable=app.var_camera_control_mode,
                 values=list(CONTROL_MODES.values()), width=30).pack(side='left', fill='x', expand=True)
    ttk.Button(parent, text='Workキル素材・アニメーション／カメラ自動選択を設定',
               command=lambda: open_settings(app)).pack(fill='x', pady=(2, 4))


def open_settings(app):
    from core.work_kill_assets import list_assets
    from core.kill_icons import MOTION_STYLES
    win = tk.Toplevel(app.root)
    win.title('カメラ・Workキル素材')
    win.geometry('840x660')
    footer = ttk.Frame(win, padding=(16, 4, 16, 10))
    footer.pack(side='bottom', fill='x')
    viewport = ttk.Frame(win)
    viewport.pack(fill='both', expand=True)
    canvas = tk.Canvas(viewport, highlightthickness=0, bg='#FFFFFF')
    scroll = ttk.Scrollbar(viewport, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scroll.set)
    scroll.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    body = ttk.Frame(canvas, padding=16)
    window_id = canvas.create_window((0, 0), window=body, anchor='nw')
    body.bind('<Configure>', lambda _event: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>', lambda event: canvas.itemconfigure(window_id, width=event.width))
    win.bind('<MouseWheel>', lambda event: canvas.yview_scroll(-int(event.delta / 120), 'units'))
    frames = list_assets('frames', review=True)
    effects = list_assets('effects', review=True)
    approved_frames = sum(item['status'] == 'approved' for item in frames)
    approved_effects = sum(item['status'] == 'approved' for item in effects)
    ttk.Label(body, text=f'キルフレーム {len(frames)}候補（正式合格{approved_frames}）／'
                         f'エフェクト {len(effects)}案（正式合格{approved_effects}）。',
              wraplength=790).pack(anchor='w')
    ttk.Label(body, text='未合格素材は確認用の明示選択のみ。肖像穴が未検証の候補は原画確認に限定します。',
              wraplength=790).pack(anchor='w')
    ttk.Label(body, text='Work素材を選ぶと既存37キルバッジに代わって表示します。オフで既存設定へ戻ります。', wraplength=790).pack(anchor='w')
    ttk.Label(body, text='選択したWork素材はキル時にミラーへ表示します。動画全体のFX表示は別スイッチです。', wraplength=790).pack(anchor='w')
    ttk.Label(body, text='肖像穴が未検証の候補は原画確認のみ。合成出力は穴の検証完了後に使用できます。', wraplength=790).pack(anchor='w')
    frame_choice, effect_choice = tk.StringVar(), tk.StringVar()
    frame_box = ttk.Combobox(body, state='readonly', textvariable=frame_choice, width=100)
    effect_box = ttk.Combobox(body, state='readonly', textvariable=effect_choice, width=100)
    mappings = {}

    def refresh():
        try:
            for kind, var, widget, selected in (
                    ('frames', frame_choice, frame_box, app.var_work_frame),
                    ('effects', effect_choice, effect_box, app.var_work_effect)):
                items = list_assets(kind, review=app.var_work_review.get())
                mapping = {'オフ': ''}
                for item in items:
                    label = f"{item.get('label', item['id'])} [{ '正式合格' if item['status']=='approved' else '未合格・確認用' }]"
                    mapping[label] = item['id']
                mappings[kind] = mapping
                widget['values'] = list(mapping)
                if selected.get() not in mapping.values(): selected.set('')
                var.set(next((k for k, v in mapping.items() if v == selected.get()), 'オフ'))
        except (OSError, ValueError) as exc:
            app.log(f'Work素材台帳を開けません: {exc}')

    def select_approved():
        app.var_work_frame.set('083/a_simple_main')
        refresh()

    ttk.Button(body, text='正式合格 No.083 A を選択', command=select_approved).pack(fill='x', pady=(8, 2))

    ttk.Checkbutton(body, text='未合格素材を確認・テスト用に表示する（品質合格にはなりません）',
                    variable=app.var_work_review, command=refresh).pack(anchor='w', pady=8)
    ttk.Label(body, text='キルフレーム').pack(anchor='w')
    frame_box.pack(fill='x', pady=4)
    frame_box.bind('<<ComboboxSelected>>', lambda _: app.var_work_frame.set(mappings['frames'][frame_choice.get()]))
    ttk.Label(body, text='A/B/C/D・D31テーマ演出（すべて未合格、確認許可が必要）').pack(anchor='w')
    effect_box.pack(fill='x', pady=4)
    effect_box.bind('<<ComboboxSelected>>', lambda _: app.var_work_effect.set(mappings['effects'][effect_choice.get()]))
    ttk.Label(body, text='登場アニメーション（既存6種類）').pack(anchor='w')
    ttk.Combobox(body, state='readonly', textvariable=app.var_kill_icon_motion,
                 values=list(MOTION_STYLES.values())).pack(fill='x', pady=4)
    strength = ttk.Frame(body)
    strength.pack(fill='x')
    for label, key in [('弱', 'weak'), ('強', 'strong')]:
        ttk.Radiobutton(strength, text=label, value=key, variable=app.var_work_strength).pack(side='left', padx=8)
    ttk.Button(body, text='選択素材の配置・アニメーションを確認', command=lambda: open_demo(app)).pack(fill='x', pady=8)
    ttk.Separator(body).pack(fill='x', pady=8)
    ttk.Label(body, text='フルオートの候補：実機確認を終えた視点だけチェックしてください。', wraplength=790).pack(anchor='w')
    ttk.Label(body, text='初期状態は未登録のため選択中の固定視点へ戻ります。映像品質の合格を自動で付けません。', wraplength=790).pack(anchor='w')
    from core.camera import STYLES
    for side in ('BLUE', 'RED'):
        group = ttk.LabelFrame(body, text=side)
        group.pack(fill='x', pady=4)
        for index, style in enumerate(SUPPORTED_STYLES):
            variable = tk.BooleanVar(value=style in app.camera_auto_qa_approved.get(side, []))
            def change(s=side, k=style, v=variable):
                approved = set(app.camera_auto_qa_approved.get(s, []))
                if v.get(): approved.add(k)
                else: approved.discard(k)
                app.camera_auto_qa_approved[s] = sorted(approved)
                app._invalidate_preview_snapshot()
            ttk.Checkbutton(group, text=STYLES.get(style, style), variable=variable,
                            command=change).grid(row=index // 5, column=index % 5, sticky='w')
    def close():
        app._save_settings()
        win.destroy()
    ttk.Button(footer, text='保存して閉じる', command=close).pack(fill='x')
    win.protocol('WM_DELETE_WINDOW', close)
    refresh()
    return win


def open_demo(app):
    """Placement demo uses marked dummy portraits; never presents them as champions."""
    import tempfile
    import threading
    import queue
    from pathlib import Path
    from PIL import Image, ImageDraw, ImageTk
    from core.work_kill_assets import render_preview_pair
    template = app.current_template()
    win = tk.Toplevel(app.root)
    win.title('配置確認・仮の肖像（実際のチャンピオン画像ではありません）')
    label = ttk.Label(win, text='確認画像を準備中…')
    label.pack()
    results = queue.Queue()
    def render():
        try:
            from core.work_kill_assets import resolve_asset
            item, path = resolve_asset(template.work_kill_frame_id, review=template.work_kill_review)
            if not item.get('portrait_boxes'):
                with Image.open(path) as source:
                    raw = source.convert('RGBA')
                    raw.thumbnail((960, 480), Image.Resampling.LANCZOS)
                    base = Image.new('RGBA', (960, 540), '#c7ced6')
                    base.alpha_composite(raw, ((960-raw.width)//2, (480-raw.height)//2))
                    ImageDraw.Draw(base).text((20, 510), 'REVIEW ONLY - portrait layout unverified', fill='black')
                    results.put([base.convert('RGB')])
                return
            with tempfile.TemporaryDirectory(prefix='ac-work-preview-') as folder:
                icons = []
                for i, color in enumerate(('#326fcb', '#b83e4d')):
                    path = Path(folder) / f'{i}.png'
                    im = Image.new('RGBA', (128, 128), color)
                    ImageDraw.Draw(im).text((40, 56), 'DEMO', fill='white')
                    im.save(path)
                    icons.append(path)
                images = []
                for i in range(72):
                    overlay = render_preview_pair(template, *icons, i / 60., size=(960, 540))
                    base = Image.new('RGBA', overlay.size, '#c7ced6')
                    base.alpha_composite(overlay)
                    images.append(base.convert('RGB'))
                results.put(images)
        except Exception as exc: results.put(exc)
    threading.Thread(target=render, daemon=True).start()
    def poll():
        if not win.winfo_exists(): return
        try: result = results.get_nowait()
        except queue.Empty:
            win.after(50, poll)
            return
        if isinstance(result, Exception):
            label.configure(text=f'確認できません: {result}')
            return
        def show(index=0):
            if not win.winfo_exists(): return
            label.image = ImageTk.PhotoImage(result[index % len(result)])
            label.configure(image=label.image, text='')
            win.after(17, show, index + 1)
        show()
    win.after(50, poll)
    return win


def mirror_event_rows(kills, now, duration):
    """Use export's stable three-slot feed; new kills never move older portraits."""
    from core.kill_icons import badge_plan
    if not kills: return []
    plan = badge_plan([(None, k['time']+.1) for k in kills],
                      max(now+.1, max(k['time'] for k in kills)+.1), duration-.1)
    return [(kills[p['index']], p['row']) for p in plan if p['start'] <= now < p['end']]


def composite_mirror(image, template, context):
    """Worker-only Replay API sampling. Uses genuine cached portraits, no Tk."""
    if not context or not getattr(template, 'work_kill_frame_id', ''): return image
    from core.kill_icons import _player_for_name, champion_icon
    from core.work_kill_assets import render_preview_pair
    api, kills, roster = context
    try:
        now = float(api.playback().get('time', -1))
        duration = float(template.kill_icon_duration)
        active = mirror_event_rows(kills, now, duration)
        output = image.convert('RGBA')
        for kill, row in active:
            pair = [_player_for_name(kill[key], roster) for key in ('killer', 'victim')]
            icons = [champion_icon(p, download=False) if p else None for p in pair]
            if all(icons):
                output.alpha_composite(render_preview_pair(template, *icons, now-kill['time'], size=output.size, row=row))
        return output.convert('RGB')
    except Exception:
        return image
