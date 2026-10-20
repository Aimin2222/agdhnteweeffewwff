"""Paged visual catalog for immutable Work frames and effect drafts."""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from functools import lru_cache
from tkinter import ttk

from PIL import Image, ImageTk

from core.work_kill_assets import file_signature, list_assets, paired_effect_for_frame, resolve_asset

PAGE_SIZE = 6
KINDS = {'キルフレーム': 'frames', 'エフェクト': 'effects'}
REGION_THEMES = {
    'bandle_city', 'bilgewater', 'demacia', 'freljord', 'ionia', 'ixtal',
    'noxus', 'piltover', 'shadow_isles', 'shurima', 'targon', 'void', 'zaun',
}
CATEGORIES = ('すべて', 'スキンテーマ', '地域モチーフ', '基本案・その他')


def page_layout(width, height):
    """Keep each card legible at the current pane size."""
    columns = 3 if width >= 660 else 2 if width >= 330 else 1
    rows = 2 if height >= 485 else 1
    return columns, columns * rows


def thumbnail_width(width, columns):
    card_width = (width - 16 - 8 * columns) // columns
    return max(96, min(205, ((card_width - 12) // 16) * 16))


def theme_category(theme):
    if theme in REGION_THEMES:
        return '地域モチーフ'
    if theme.startswith(('a_', 'a1_', 'a2_', 'b_', 'b1_', 'b2_', 'c_', 'c1_', 'c2_')) or theme in {
        'abcd_palette_reference', 'unlabeled_s005',
    }:
        return '基本案・その他'
    return 'スキンテーマ'


def centered_preview(image, bounds):
    """Center visible pixels for catalog display only; never alter source PNGs."""
    alpha_bounds = image.getchannel('A').getbbox()
    content = image.crop(alpha_bounds) if alpha_bounds else image
    content.thumbnail(bounds, Image.Resampling.LANCZOS)
    tile = Image.new('RGBA', bounds)
    tile.alpha_composite(content, ((bounds[0] - content.width) // 2,
                                   (bounds[1] - content.height) // 2))
    return tile


@lru_cache(maxsize=64)
def thumbnail(signature, width=205):
    with Image.open(signature[0]) as source:
        return centered_preview(source.convert('RGBA'), (width, round(width * 108 / 205)))


def matching(items, text, status, category='すべて', theme='すべて'):
    needle = text.strip().casefold()
    return [item for item in items
            if (status == 'すべて' or (item['status'] == 'approved') == (status == '正式合格'))
            and (category == 'すべて' or theme_category(item.get('theme', '')) == category)
            and (theme == 'すべて' or item.get('theme') == theme)
            and (not needle or needle in (item['id']+' '+item.get('label', '')).casefold())]


class WorkGallery:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title('LoL AutoCine｜Work素材図鑑')
        self.win.geometry('1090x720')
        self.win.minsize(770, 520)
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.items = {kind: list_assets(kind, review=True) for kind in KINDS.values()}
        self.kind = tk.StringVar(value='キルフレーム')
        self.search = tk.StringVar()
        self.status = tk.StringVar(value='すべて')
        self.category = tk.StringVar(value='すべて')
        self.theme = tk.StringVar(value='すべて')
        self.page = 0
        self.columns = 2
        self.page_size = 4
        self.thumb_width = 205
        self.selected = None
        self.generation = 0
        self.preview_generation = 0
        self.ready = queue.Queue()
        self.photos = []
        self._layout_job = None

        heading = ttk.Frame(self.win, padding=(10, 8, 10, 0))
        heading.pack(fill='x')
        ttk.Label(heading, text='Work素材図鑑', font=('Meiryo UI', 15, 'bold')).pack(side='left')
        ttk.Label(heading, text='正式合格と仮素材を区別して表示').pack(side='right')
        top = ttk.Frame(self.win, padding=(10, 6, 10, 2))
        top.pack(fill='x')
        top.columnconfigure(3, weight=1)
        ttk.Label(top, text='種類').grid(row=0, column=0, sticky='w')
        ttk.Combobox(top, textvariable=self.kind, values=list(KINDS),
                     state='readonly', width=16).grid(row=0, column=1, sticky='ew', padx=(6, 16))
        ttk.Label(top, text='検索').grid(row=0, column=2, sticky='w')
        ttk.Entry(top, textvariable=self.search).grid(row=0, column=3, sticky='ew', padx=(6, 12))
        ttk.Combobox(top, textvariable=self.status, values=('すべて', '正式合格', '仮素材'),
                     state='readonly', width=12).grid(row=0, column=4, sticky='e')
        filters = ttk.Frame(self.win, padding=(10, 0, 10, 8))
        filters.pack(fill='x')
        ttk.Label(filters, text='素材の系統').grid(row=0, column=0, sticky='w')
        self.category_box = ttk.Combobox(filters, textvariable=self.category, values=CATEGORIES,
                                         state='readonly', width=16)
        self.category_box.grid(row=0, column=1, sticky='ew', padx=(6, 16))
        ttk.Label(filters, text='テーマ').grid(row=0, column=2, sticky='w')
        self.theme_box = ttk.Combobox(filters, textvariable=self.theme, state='readonly', width=24)
        self.theme_box.grid(row=0, column=3, sticky='ew', padx=(6, 0))
        ttk.Label(filters, text='地域は素材のモチーフ分類です').grid(row=1, column=0,
                                                   columnspan=4, sticky='w', pady=(4, 0))

        main = ttk.PanedWindow(self.win, orient='horizontal')
        main.pack(fill='both', expand=True)
        left = ttk.Frame(main, padding=8)
        right = ttk.Frame(main, padding=12)
        self.left = left
        main.add(left, weight=3)
        main.add(right, weight=2)
        pager = ttk.Frame(left)
        pager.pack(fill='x', pady=(0, 7))
        self.prev_button = ttk.Button(pager, text='◀ 前へ', command=lambda: self.turn(-1))
        self.prev_button.pack(side='left')
        self.page_label = ttk.Label(pager, text='')
        self.page_label.pack(side='left', expand=True)
        self.next_button = ttk.Button(pager, text='次へ ▶', command=lambda: self.turn(1))
        self.next_button.pack(side='right')
        self.grid = ttk.Frame(left)
        self.grid.pack(fill='both', expand=True)
        for column in range(3):
            self.grid.columnconfigure(column, weight=1 if column < self.columns else 0)

        self.preview = ttk.Label(right, text='素材を選択してください', anchor='center')
        self.preview.pack(fill='both', expand=True)
        self.info = ttk.Label(right, text='', wraplength=370)
        self.info.pack(fill='x', pady=8)
        self.apply_button = ttk.Button(right, text='この枠と同名のエフェクトを適用', command=self.apply)
        self.apply_button.pack(fill='x', pady=5)
        ttk.Button(right, text='閉じる', command=self.close).pack(fill='x')
        ttk.Label(right, text='仮素材を適用すると試作動画にも出せます。品質台帳の合格数は変わりません。',
                  wraplength=370).pack(anchor='w', pady=8)
        for variable in (self.kind, self.category):
            variable.trace_add('write', lambda *_: self._update_theme_choices())
        for variable in (self.kind, self.search, self.status, self.category, self.theme):
            variable.trace_add('write', lambda *_: self.refresh(reset=True))
        self._update_theme_choices()
        self.refresh(reset=True)
        left.bind('<Configure>', lambda _event: self._queue_layout(), add='+')
        self.win.after_idle(self._sync_layout)
        self._poll_id = self.win.after(50, self.poll)

    def filtered(self):
        if self.kind.get() == 'エフェクト':
            return matching(self.items['effects'], self.search.get(), self.status.get())
        return matching(self.items['frames'], self.search.get(), self.status.get(),
                        self.category.get(), self.theme.get())

    def _update_theme_choices(self):
        frames = self.kind.get() == 'キルフレーム'
        self.category_box.configure(state='readonly' if frames else 'disabled')
        self.theme_box.configure(state='readonly' if frames else 'disabled')
        choices = sorted({item.get('theme', '') for item in self.items['frames']
                          if item.get('theme') and (self.category.get() == 'すべて' or
                          theme_category(item['theme']) == self.category.get())})
        self.theme_box.configure(values=('すべて', *choices))
        if self.theme.get() not in choices:
            self.theme.set('すべて')

    def _sync_layout(self):
        if not self.win.winfo_exists():
            return
        width, height = self.left.winfo_width(), self.left.winfo_height()
        if width < 200 or height < 200:
            return  # Ignore Tk's initial 1x1 geometry before the pane settles.
        columns, page_size = page_layout(width, height)
        thumb_width = thumbnail_width(width, columns)
        if (columns, page_size, thumb_width) == (self.columns, self.page_size, self.thumb_width):
            return
        first_visible = self.page * self.page_size
        self.columns, self.page_size, self.thumb_width = columns, page_size, thumb_width
        self.page = first_visible // page_size
        for column in range(3):
            self.grid.columnconfigure(column, weight=1 if column < columns else 0)
        self.refresh()

    def _queue_layout(self):
        if self._layout_job is not None:
            self.win.after_cancel(self._layout_job)
        self._layout_job = self.win.after(100, self._apply_queued_layout)

    def _apply_queued_layout(self):
        self._layout_job = None
        self._sync_layout()

    def refresh(self, *, reset=False):
        if reset:
            self.page = 0
            self.selected = None
            self.info.configure(text='')
            self.preview.configure(image='', text='素材を選択してください')
            self.preview_generation += 1
        self.generation += 1
        generation = self.generation
        rows = self.filtered()
        page_count = max(1, (len(rows)+self.page_size-1)//self.page_size)
        self.page = min(self.page, page_count-1)
        self.page_label.configure(text=f'{len(rows)}件  /  {self.page+1} / {page_count}')
        self.prev_button.configure(state='normal' if self.page else 'disabled')
        self.next_button.configure(state='normal' if self.page+1 < page_count else 'disabled')
        self.apply_button.configure(text=('この枠と同名のエフェクトを適用' if self.kind.get() == 'キルフレーム'
                                          else 'このエフェクトだけ変更（詳細）'))
        for widget in self.grid.winfo_children():
            widget.destroy()
        self.photos.clear()
        shown = rows[self.page*self.page_size:(self.page+1)*self.page_size]
        self.cards = []
        for index, item in enumerate(shown):
            cell = ttk.Frame(self.grid, padding=4, relief='solid', borderwidth=1)
            cell.grid(row=index//self.columns, column=index%self.columns,
                      sticky='nsew', padx=4, pady=4)
            image = ttk.Label(cell, text='画像を読込中', anchor='center')
            image.pack(fill='both', expand=True)
            status = '正式合格' if item['status'] == 'approved' else '仮素材・未合格'
            ttk.Label(cell, text=item['id'], wraplength=self.thumb_width).pack(fill='x')
            ttk.Label(cell, text=status).pack(fill='x')
            ttk.Button(cell, text='選択', command=lambda row=item: self.select(row)).pack(fill='x')
            self.cards.append(image)
        kind = KINDS[self.kind.get()]
        threading.Thread(target=self._load_page, args=(generation, kind, shown, self.thumb_width),
                         name='AutoCine-WorkGallery', daemon=True).start()

    def _load_page(self, generation, kind, shown, width):
        for index, item in enumerate(shown):
            if generation != self.generation:
                return
            try:
                _, path = resolve_asset(item['id'], kind, review=True)
                image = thumbnail(file_signature(path), width)
                self.ready.put((generation, index, image, ''))
            except Exception as exc:
                self.ready.put((generation, index, None, f'{type(exc).__name__}: {exc}'))

    def poll(self):
        if not self.win.winfo_exists():
            return
        for _ in range(8):
            try:
                generation, index, image, error = self.ready.get_nowait()
            except queue.Empty:
                break
            if index == -1:
                if generation != self.preview_generation:
                    continue
            elif generation != self.generation or index >= len(self.cards):
                continue
            if index == -1:
                if image is None:
                    self.preview.configure(text=error[:100], image='')
                else:
                    self.preview_photo = ImageTk.PhotoImage(image)
                    self.preview.configure(image=self.preview_photo, text='')
                continue
            if image is None:
                self.cards[index].configure(text=error[:70])
            else:
                photo = ImageTk.PhotoImage(image)
                self.photos.append(photo)
                self.cards[index].configure(image=photo, text='')
        self._poll_id = self.win.after(50, self.poll)

    def turn(self, offset):
        count = len(self.filtered())
        page_count = max(1, (count+self.page_size-1)//self.page_size)
        next_page = max(0, min(page_count-1, self.page+offset))
        if next_page != self.page:
            self.page = next_page
            self.refresh()

    def select(self, item):
        self.selected = (KINDS[self.kind.get()], item)
        status = '正式合格' if item['status'] == 'approved' else '仮素材・品質未合格'
        layout = ('検証済み肖像穴' if item.get('portrait_boxes') else
                  '肖像は仮位置。合格品と差し替えるまで構図は暫定')
        effect = paired_effect_for_frame(item['id']) if self.selected[0] == 'frames' else None
        pairing = (f"\n連動エフェクト: {effect['label']}（仮素材）" if effect else
                   '\n連動エフェクト: なし') if self.selected[0] == 'frames' else ''
        self.info.configure(text=f"{item.get('label', item['id'])}\n{item['id']} / {status}\n{layout}{pairing}")
        self.preview_generation += 1
        generation = self.preview_generation
        kind = self.selected[0]
        # A separate load keeps the full-size preview off the Tk thread.
        def load():
            try:
                _, path = resolve_asset(item['id'], kind, review=True)
                with Image.open(path) as source:
                    image = centered_preview(source.convert('RGBA'), (320, 215))
                self.ready.put((generation, -1, image, ''))
            except Exception as exc:
                self.ready.put((generation, -1, None, str(exc)))
        threading.Thread(target=load, daemon=True).start()

    def apply(self):
        if self.selected is None:
            return
        kind, item = self.selected
        if kind == 'frames':
            from ui.director_work_controls import select_frame_with_effect
            effect = select_frame_with_effect(self.app, item['id'])
        else:
            self.app.var_work_effect.set(item['id'])
            effect = item
            if not self.app.var_work_frame.get():
                self.app.var_work_frame.set('083/a_simple_main')
        if item['status'] != 'approved' or (effect and effect['status'] != 'approved'):
            self.app.var_work_review.set(True)
        refresh = getattr(self.app, '_work_settings_refresh', None)
        if callable(refresh):
            refresh()
        self.app._invalidate_preview_snapshot()
        self.app._save_settings()
        self.app.log(f"Work素材を選択: {item['id']} / 品質状態 {item['status']}"
                     + (f" / 連動エフェクト {effect['id']}（仮素材）" if kind == 'frames' and effect else ''))
        self.close()

    def close(self):
        if self._layout_job is not None:
            self.win.after_cancel(self._layout_job)
            self._layout_job = None
        if getattr(self, '_poll_id', None):
            self.win.after_cancel(self._poll_id)
            self._poll_id = None
        self.win.destroy()


def open_gallery(app):
    gallery = getattr(app, '_work_gallery', None)
    if gallery is not None and gallery.win.winfo_exists():
        gallery.win.lift()
        return gallery.win
    gallery = app._work_gallery = WorkGallery(app)
    return gallery.win
