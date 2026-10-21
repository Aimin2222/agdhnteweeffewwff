"""Nine reference-led Tk workspaces over the existing AutoCine controller.

This module owns presentation only. Every command and Tk variable belongs to
legacy_app.App; camera, scan, mirror, render and audio code stay in that app.
An explicitly labelled mock still is shown only while the replay is offline.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ui.layout_variants import LAYOUT_NAMES

BG = "#F2F6FB"
WHITE = "#FFFFFF"
INK = "#12213C"
MUTED = "#63748F"
BLUE = "#0875F9"
LINE = "#DCE6F2"


class ReferenceStudio:
    """Real comparison window sharing one live App and one project state."""

    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("LoL AutoCine — UI比較版")
        sw, sh = app.root.winfo_screenwidth(), app.root.winfo_screenheight()
        self.window.geometry(f"{min(1660, sw)}x{min(940, sh)}+0+0")
        self.window.minsize(1020, 650)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", app.on_close)
        self.layout_var = app.var_ui_layout
        self.library_page = tk.StringVar(value="ライブラリ")
        self.inspector_page = tk.StringVar(value="カメラ")
        self._scene_signature = None
        self._asset_photos = []
        self._scene_photos = []
        self._library_page_num = 0
        self._camera_mode_cards = []
        self._camera_style_cards = []
        self._scene_widgets = []
        self._offline_photo = None
        self._offline_photo_size = None
        self.window.bind("<Configure>", self._responsive, add="+")
        self.window.bind("<MouseWheel>", self._wheel, add="+")
        self._build()
        app.root.withdraw()
        self._sync()

    def _label(self, parent, text, *, size=10, bold=False, color=INK, bg=WHITE, **kw):
        return tk.Label(parent, text=text, bg=bg, fg=color,
                        font=("Meiryo UI", size, "bold" if bold else "normal"), **kw)

    def _button(self, parent, text, command, *, primary=False, small=False):
        b = tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                      bg=BLUE if primary else WHITE, fg=WHITE if primary else BLUE,
                      activebackground="#075FCC" if primary else "#EAF3FF",
                      activeforeground=WHITE if primary else BLUE,
                      highlightbackground=LINE, font=("Meiryo UI", 9 if small else 10, "bold"),
                      padx=9, pady=5 if small else 8, cursor="hand2")
        return b

    def _panel(self, parent, title=None):
        f = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=LINE)
        if title:
            self._label(f, title, size=12, bold=True).pack(anchor="w", padx=12, pady=(10, 6))
        return f

    def _scroll(self, parent, width):
        outer = tk.Frame(parent, bg=WHITE, width=width, highlightthickness=1,
                         highlightbackground=LINE)
        outer.pack_propagate(False)
        canvas = tk.Canvas(outer, bg=WHITE, highlightthickness=0, bd=0)
        bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=WHITE)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=bar.set)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        outer._scroll_canvas = canvas
        def wheel(e):
            canvas.yview_scroll(-int(e.delta / 120), "units")
            return "break"
        canvas.bind("<MouseWheel>", wheel)
        inner.bind("<MouseWheel>", wheel)
        return outer, inner

    def _wheel(self, event):
        for box in (getattr(self, "left_box", None), getattr(self, "right_box", None)):
            if box is None or not box.winfo_exists():
                continue
            x, y = box.winfo_rootx(), box.winfo_rooty()
            if x <= event.x_root < x + box.winfo_width() and y <= event.y_root < y + box.winfo_height():
                box._scroll_canvas.yview_scroll(-int(event.delta / 120), "units")
                return "break"

    def _build(self):
        for child in self.window.winfo_children():
            child.destroy()
        self._asset_photos = []
        self._camera_mode_cards = []
        self._camera_style_cards = []
        try:
            index = LAYOUT_NAMES.index(self.layout_var.get()) + 1
        except ValueError:
            index = 3
            self.layout_var.set(LAYOUT_NAMES[2])
        self.index = index
        self._header(index)
        if index == 5:
            self._steps()
        if index == 9:
            self._steps(beginner=True)
        # Claim the fixed timeline height before the expanding workspace.
        self._timeline()
        body = tk.Frame(self.window, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=5)
        # The editor is intentionally wider on plan 2, the library on plan 6.
        left_w = 385 if index in (2, 6) else (315 if index in (1, 3, 5, 9) else 340)
        right_w = 405 if index in (4, 8) else 340
        if index == 7:
            left_w, right_w = 320, 390
        left_box, left = self._scroll(body, left_w)
        right_box, right = self._scroll(body, right_w)
        center = tk.Frame(body, bg=BG)
        left_box.pack(side="left", fill="y", padx=(0, 7))
        right_box.pack(side="right", fill="y", padx=(7, 0))
        center.pack(side="left", fill="both", expand=True)
        self.left_box, self.right_box = left_box, right_box
        if index == 7:
            self._replay_prep(left)
            self._scene_list(right)
            self._test_summary(right)
        elif index == 6 and self.library_page.get() == "ライブラリ":
            self._library(left)
            self._asset_detail(right)
        elif index == 2:
            self._editor_sources(left)
            self._inspector(right, detailed=True)
        elif index == 1:
            self._home_scenes(left)
            self._recommendations(right)
        elif index == 5:
            self._scene_list(left)
            self._wizard_guide(right)
        elif index == 9:
            self._beginner_scenes(left)
            self._beginner_cards(right)
        else:
            self._scene_list(left)
            if index == 4:
                self._dock_inspector(right)
            elif index == 8:
                self._test_inspector(right)
            else:
                self._inspector(right, detailed=(self.app.var_edit_mode.get() == "advanced"))
        if index in (1, 3, 4, 5, 6):
            self._quick_strip(center)
        self._preview(center)
        if index == 5:
            self._button(self.window, "次へ：書き出し  →", self.app.on_make_checked,
                         primary=True).pack(side="bottom", anchor="e", padx=14, pady=3)
        self.window.after_idle(lambda: self.window.lift())

    def _responsive(self, event):
        if event.widget is not self.window or not hasattr(self, "timeline"):
            return
        if not self.timeline.winfo_exists():
            return
        short = event.height < 820
        wanted = 112 if short else (175 if self.index == 2 else 142)
        if int(self.timeline.cget("height")) != wanted:
            self.timeline.configure(height=wanted)
        row = getattr(self, "quick_row", None)
        if row is not None and row.winfo_exists():
            if short and row.winfo_manager():
                row.pack_forget()
            elif not short and not row.winfo_manager():
                row.pack(side="bottom", fill="x", pady=(6, 0))

    def _header(self, index):
        bar = tk.Frame(self.window, bg=WHITE, height=48,
                       highlightthickness=1, highlightbackground=LINE)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self._label(bar, "LoL AutoCine", size=14, bold=True).pack(side="left", padx=(16, 12))
        self._label(bar, LAYOUT_NAMES[index - 1], size=10, color=MUTED).pack(side="left")
        self._button(bar, "書き出し", self.app.on_make_checked, primary=True, small=True).pack(side="right", padx=7, pady=5)
        self._button(bar, "基本設定", self._show_legacy_settings, small=True).pack(side="right", padx=3)
        self._button(bar, "ログ", self.app.on_show_diagnostics, small=True).pack(side="right", padx=3)
        self._button(bar, "リプレイを開く", self.app.on_open_replay, small=True).pack(side="right", padx=3)
        chooser = ttk.Combobox(bar, textvariable=self.layout_var, values=LAYOUT_NAMES,
                               state="readonly", width=30)
        chooser.pack(side="right", padx=8)
        chooser.bind("<<ComboboxSelected>>", lambda _e: self._change_layout())
        mode = tk.Frame(self.window, bg=WHITE)
        mode.pack(fill="x", padx=10, pady=(4, 0))
        for text, value in (("簡単編集", "easy"), ("詳細編集", "advanced")):
            tk.Radiobutton(mode, text=text, variable=self.app.var_edit_mode, value=value,
                           command=lambda: (self.app._apply_edit_mode(), self._build()),
                           indicatoron=0, relief="flat", bg=WHITE, fg=BLUE,
                           selectcolor="#E9F2FF", padx=14, pady=3,
                           font=("Meiryo UI", 10, "bold")).pack(side="left", padx=3)
        self._label(mode, "GPU / 音声 / HUD / TargetLock は基本設定で調整", size=9,
                    color=MUTED).pack(side="right", padx=5)

    def _change_layout(self):
        self.app._apply_ui_layout()
        self._build()

    def _show_legacy_settings(self):
        self.app.root.deiconify()
        self.app.root.lift()
        self.app._focus_settings()

    def _steps(self, beginner=False):
        f = tk.Frame(self.window, bg=WHITE, height=46)
        f.pack(fill="x", padx=10, pady=(4, 0))
        f.pack_propagate(False)
        labels = ("1  リプレイと対象", "2  試合をスキャン", "3  見た目を整える", "4  書き出す")
        actions = (self.app.on_quick_prepare, self.app.on_scan,
                   lambda: self._show_legacy_settings(), self.app.on_make_checked)
        for i, (label, action) in enumerate(zip(labels, actions)):
            self._button(f, label, action, primary=i == 2, small=True).pack(side="left", expand=True, fill="x", padx=5, pady=5)

    def _section(self, parent, title):
        f = tk.Frame(parent, bg=WHITE)
        f.pack(fill="x", padx=11, pady=(7, 6))
        self._label(f, title, size=11, bold=True).pack(anchor="w", pady=(0, 5))
        return f

    def _scene_list(self, parent):
        f = self._section(parent, "検出シーン")
        self._button(f, "⌕  試合全体スキャン", self.app.on_scan, primary=True).pack(fill="x", pady=3)
        self._label(f, "実リプレイを解析してシーンを表示", color=MUTED, size=9).pack(anchor="w")
        self._label(f, "キル・アシスト", size=9, bold=True).pack(anchor="w", pady=(10, 2))
        for label in ("キル", "アシスト", "キル＋アシスト"):
            ttk.Radiobutton(f, text=label, variable=self.app.var_event_mode,
                            value=label).pack(side="left")
        f2 = self._section(parent, "検出されたシーン")
        self.scene_count = self._label(f2, "未スキャン", size=9, color=MUTED)
        self.scene_count.pack(anchor="w")
        self.scene_items = tk.Frame(f2, bg=WHITE)
        self.scene_items.pack(fill="x")
        row = tk.Frame(f2, bg=WHITE)
        row.pack(fill="x", pady=5)
        self._button(row, "全選択", lambda: self._scene_action(self.app.on_check_all), small=True).pack(side="left", expand=True, fill="x")
        self._button(row, "全解除", lambda: self._scene_action(self.app.on_uncheck_all), small=True).pack(side="left", expand=True, fill="x")
        self._button(f2, "選択シーンへ移動", self.app.on_jump_selected, small=True).pack(fill="x")
        self._button(f2, "チェック分を書き出す", self.app.on_make_checked, primary=True, small=True).pack(fill="x", pady=3)
        self._render_scenes()

    def _scene_action(self, fn):
        fn()
        self._render_scenes()

    def _render_scenes(self):
        if not hasattr(self, "scene_items") or not self.scene_items.winfo_exists():
            return
        for widget in self.scene_items.winfo_children():
            widget.destroy()
        self._scene_photos = []
        kills = self.app.kills
        self.scene_count.configure(text=f"{len(kills)}件" if kills else "未スキャン / 検出0件")
        selected = self.app.lb_kills.curselection()
        for i, kill in enumerate(kills):
            row = tk.Frame(self.scene_items, bg="#ECF4FF" if selected and selected[0] == i else WHITE,
                           highlightthickness=1, highlightbackground=LINE)
            row.pack(fill="x", pady=3)
            check = tk.BooleanVar(value=i in self.app.checked_kills)
            ttk.Checkbutton(row, variable=check,
                            command=lambda n=i: self._toggle_scene(n)).pack(side="left", padx=3)
            try:
                from PIL import Image, ImageTk
                from ui.scene_project import scene_key
                path = self.app._scene_thumbnail_path(scene_key(kill))
                if path.is_file():
                    with Image.open(path) as source:
                        source.thumbnail((76, 46))
                        photo = ImageTk.PhotoImage(source.copy())
                    self._scene_photos.append(photo)
                    tk.Label(row, image=photo, bg=row.cget("bg")).pack(side="left", padx=2)
            except (ImportError, OSError, ValueError):
                pass
            role = "キル" if getattr(kill, "role", "kill") == "kill" else "アシスト"
            title = f"{int(kill.time//60):02d}:{int(kill.time%60):02d}  {role}"
            if getattr(kill, "multikill", 1) > 1:
                title += f" ×{kill.multikill}"
            b = self._button(row, title, lambda n=i: self._select_scene(n), small=True)
            b.configure(anchor="w", bg=row.cget("bg"), fg=INK)
            b.pack(side="left", fill="x", expand=True)
            self._label(row, "BLUE" if getattr(kill, "team", "") == "ORDER" else "RED",
                        size=8, color=BLUE if getattr(kill, "team", "") == "ORDER" else "#DF3A50",
                        bg=row.cget("bg")).pack(side="right", padx=5)

    def _select_scene(self, index):
        self.app._select_timeline_event(index)
        self._render_scenes()
        self._draw_timeline()

    def _toggle_scene(self, index):
        self.app.lb_kills.selection_clear(0, "end")
        self.app.lb_kills.selection_set(index)
        self.app.on_toggle_checked()
        self.app.on_scene_selection()
        self._render_scenes()
        self._draw_timeline()

    def _replay_prep(self, parent):
        f = self._section(parent, "1. リプレイ準備")
        self._button(f, "リプレイを開く", self.app.on_open_replay, primary=True).pack(fill="x", pady=3)
        self._button(f, "準備", self.app.on_quick_prepare).pack(fill="x")
        self._label(f, "対象プレイヤー / TargetLock", bold=True).pack(anchor="w", pady=(10, 3))
        self._button(f, "プレイヤー一覧を開く", self._show_legacy_settings).pack(fill="x")

    def _home_scenes(self, parent):
        f = self._section(parent, "試合から動画を作る")
        self._label(f, "見どころを自動で探します", color=MUTED).pack(anchor="w")
        self._button(f, "⌕  試合全体スキャン", self.app.on_scan, primary=True).pack(fill="x", pady=5)
        self._scene_list(parent)

    def _beginner_scenes(self, parent):
        self._replay_prep(parent)
        self._scene_list(parent)

    def _editor_sources(self, parent):
        f = self._section(parent, "素材 / シーン")
        for title, command in (("シーン", lambda: None), ("キルフレーム", self.app._open_work_gallery),
                               ("エフェクト", self.app._open_work_gallery)):
            self._button(f, title, command, small=True).pack(side="left", expand=True, fill="x", padx=2)
        self._scene_list(parent)
        self._library(parent, compact=True)

    def _library(self, parent, compact=False):
        f = self._section(parent, "ライブラリ" if not compact else "キルフレーム素材")
        if not compact:
            self._button(f, "試合全体スキャン", self.app.on_scan, primary=True).pack(fill="x", pady=3)
            tabs = tk.Frame(f, bg=WHITE)
            tabs.pack(fill="x")
            for label in ("ライブラリ", "編集"):
                self._button(tabs, label, lambda value=label: self._set_library_page(value),
                             primary=self.library_page.get() == label, small=True).pack(side="left", fill="x", expand=True)
        from core.work_kill_assets import list_assets, file_signature, resolve_asset
        assets_all = list_assets("frames", review=True)
        search = tk.StringVar()
        filter_theme = tk.StringVar(value="すべてのテーマ")
        filter_status = tk.StringVar(value="すべて")
        ttk.Entry(f, textvariable=search).pack(fill="x", pady=4)
        filters = tk.Frame(f, bg=WHITE)
        filters.pack(fill="x", pady=3)
        ttk.Combobox(filters, textvariable=filter_theme, state="readonly", width=17,
                     values=["すべてのテーマ", *sorted({a.get("theme", "") for a in assets_all if a.get("theme")})]).pack(side="left", fill="x", expand=True)
        ttk.Combobox(filters, textvariable=filter_status, state="readonly", width=10,
                     values=("すべて", "正式合格", "確認用")).pack(side="left", padx=(4, 0))
        page_status = self._label(f, "", size=9, color=MUTED)
        page_status.pack(anchor="w", pady=3)
        grid = tk.Frame(f, bg=WHITE)
        grid.pack(fill="x")
        def populate(*_):
            for child in grid.winfo_children():
                child.destroy()
            self._asset_photos.clear()
            from ui.work_gallery import thumbnail
            from PIL import ImageTk
            needle = search.get().strip().casefold()
            assets = [a for a in assets_all
                      if needle in (a["id"] + " " + a.get("label", "")).casefold()
                      and (filter_theme.get() == "すべてのテーマ" or a.get("theme") == filter_theme.get())
                      and (filter_status.get() == "すべて" or
                           (filter_status.get() == "正式合格") == (a["status"] == "approved"))]
            page_size = 4 if compact else 10
            page_count = max(1, (len(assets) + page_size - 1) // page_size)
            self._library_page_num = min(self._library_page_num, page_count - 1)
            page_status.configure(text=f"{len(assets)}件   /   {self._library_page_num + 1} / {page_count} ページ")
            start = self._library_page_num * page_size
            for n, asset in enumerate(assets[start:start + page_size]):
                tile = tk.Frame(grid, bg=WHITE, highlightthickness=1, highlightbackground=LINE)
                tile.grid(row=n // 2, column=n % 2, sticky="ew", padx=2, pady=3)
                try:
                    _, path = resolve_asset(asset["id"], "frames", review=True)
                    photo = ImageTk.PhotoImage(thumbnail(file_signature(path), 145))
                    self._asset_photos.append(photo)
                    button = tk.Button(tile, image=photo, command=lambda a=asset: self._apply_asset(a),
                                       relief="flat", bg=WHITE, bd=0)
                    button.pack(fill="x")
                except Exception:
                    pass
                status = "正式合格" if asset["status"] == "approved" else "確認用"
                self._button(tile, f"{asset['id'][:15]}\n{status}",
                             lambda a=asset: self._apply_asset(a), small=True).pack(fill="x")
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)
        search.trace_add("write", populate)
        filter_theme.trace_add("write", lambda *_: (setattr(self, "_library_page_num", 0), populate()))
        filter_status.trace_add("write", lambda *_: (setattr(self, "_library_page_num", 0), populate()))
        nav = tk.Frame(f, bg=WHITE)
        nav.pack(fill="x", pady=3)
        self._button(nav, "◀ 前のページ", lambda: self._library_turn(-1, populate),
                     small=True).pack(side="left", fill="x", expand=True)
        self._button(nav, "次のページ ▶", lambda: self._library_turn(1, populate),
                     small=True).pack(side="left", fill="x", expand=True)
        populate()
        self._button(f, "全素材を画像図鑑で見る", self.app._open_work_gallery,
                     small=True).pack(fill="x", pady=5)

    def _set_library_page(self, page):
        self.library_page.set(page)
        self._build()

    def _library_turn(self, direction, populate):
        self._library_page_num = max(0, self._library_page_num + direction)
        populate()

    def _apply_asset(self, asset):
        from ui.director_work_controls import select_frame_with_effect
        select_frame_with_effect(self.app, asset["id"])
        self.app._invalidate_preview_snapshot()
        self.app._save_settings()
        self._build()

    def _asset_detail(self, parent):
        f = self._section(parent, "選択中の素材")
        self._label(f, self.app.var_work_frame.get() or "素材を選択してください",
                    size=10, color=MUTED).pack(anchor="w", pady=8)
        self._button(f, "プレビューに適用", self.app.on_exact_still, primary=True).pack(fill="x")
        self._camera_choices(parent)
        self._fx_choices(parent)
        self._output_summary(parent)

    def _preview(self, parent):
        host = self._panel(parent)
        host.pack(fill="both", expand=True)
        heading = tk.Frame(host, bg=WHITE)
        heading.pack(fill="x", padx=8, pady=5)
        self._label(heading, "ミラープレビュー", size=12, bold=True).pack(side="left")
        self.preview_status = self._label(heading, "● 接続待ち", color=MUTED, size=9)
        self.preview_status.pack(side="left", padx=10)
        self._label(heading, "16:9", color=MUTED, size=9).pack(side="right")
        controls = tk.Frame(host, bg="#172437")
        controls.pack(side="bottom", fill="x", padx=7, pady=(0, 7))
        self._button(controls, "▶ ミラー", self.app.on_mirror_start, small=True).pack(side="left", padx=2)
        self._button(controls, "■ 停止", lambda: self.app.on_mirror_stop(reason="UI停止"), small=True).pack(side="left", padx=2)
        self._button(controls, "▶ 演出確認", self.app.on_preview_play, small=True).pack(side="left", padx=2)
        self._button(controls, "■ 停止", self.app.on_preview_stop, small=True).pack(side="left", padx=2)
        ttk.Checkbutton(controls, text="FX反映", variable=self.app.var_live).pack(side="left", padx=3)
        self._label(controls, "映像は実LoL接続時に表示", bg="#172437",
                    color="#C8D7E9", size=8).pack(side="right", padx=8)
        canvas = tk.Canvas(host, bg="#101826", highlightthickness=0, width=700, height=395)
        canvas.pack(fill="both", expand=True, padx=7)
        self.app.canvas = canvas
        self.app._preview_image_item = None
        self.app._preview_text_item = None
        self._offline_photo_size = None
        canvas.bind("<Configure>", self.app._recenter_preview_placeholder, add="+")

    def _offline_reference(self):
        """Show the supplied visual reference without presenting it as live LoL."""
        canvas = self.app.canvas
        if self.app.var_mirror.get():
            canvas.delete("offline_reference")
            self._offline_photo = None
            self._offline_photo_size = None
            return
        source = Path(__file__).resolve().parent.parent / "assets" / "ui_reference" / "mock_preview_offline.jpg"
        if not source.is_file():
            return
        width, height = max(1, canvas.winfo_width()), max(1, canvas.winfo_height())
        size = (width, height)
        if size != self._offline_photo_size or not canvas.find_withtag("offline_reference"):
            from PIL import Image, ImageTk
            with Image.open(source) as original:
                image = original.copy()
            image.thumbnail(size, Image.Resampling.LANCZOS)
            self._offline_photo = ImageTk.PhotoImage(image, master=canvas)
            canvas.delete("offline_reference")
            canvas.create_image(width // 2, height // 2, image=self._offline_photo,
                                tags="offline_reference")
            canvas.create_rectangle(8, 8, 303, 35, fill="#10243D", outline="",
                                    tags="offline_reference")
            canvas.create_text(15, 21, text="UI参考静止画  |  LoL未接続・実映像ではありません",
                               fill="#FFFFFF", anchor="w", font=("Meiryo UI", 8, "bold"),
                               tags="offline_reference")
            canvas.tag_lower("offline_reference")
            self._offline_photo_size = size
        text_item = getattr(self.app, "_preview_text_item", None)
        if text_item is not None:
            canvas.itemconfigure(text_item, text="")

    def _quick_strip(self, parent):
        row = tk.Frame(parent, bg=BG)
        self.quick_row = row
        row.pack(side="bottom", fill="x", pady=(6, 0))
        for title, builder in (("カメラ", self._camera_choices),
                               ("キルフレーム", self._frame_choices),
                               ("エフェクト", self._fx_choices)):
            pane = self._panel(row, title)
            pane.pack(side="left", fill="both", expand=True, padx=2)
            builder(pane, compact=True)

    def _camera_choices(self, parent, compact=False):
        if compact:
            f = tk.Frame(parent, bg=WHITE)
            f.pack(fill="x", padx=7, pady=3)
        else:
            f = self._section(parent, "カメラ")
        from core.smart_camera_director import CONTROL_MODES
        modes = (("手動", "manual", "プレイヤー操作に近いカメラワーク"),
                 ("固定視点＋自動構図補正", "fixed_auto", "戦況に応じて見やすい構図へ補正"),
                 ("フルオートシネマ", "full_auto", "承認済み候補から選択。候補なしは固定視点"))
        if compact:
            for title, key, _ in modes:
                value = CONTROL_MODES[key]
                self._button(f, title, lambda v=value: self._set_camera_mode(v),
                             primary=self.app.var_camera_control_mode.get() == value,
                             small=True).pack(side="left", expand=True, fill="x", padx=1)
            self._camera_style_tiles(parent)
        else:
            for title, key, description in modes:
                value = CONTROL_MODES[key]
                selected = self.app.var_camera_control_mode.get() == value
                card = tk.Frame(f, bg="#EBF4FF" if selected else WHITE,
                                highlightthickness=2 if selected else 1,
                                highlightbackground=BLUE if selected else LINE)
                card.pack(fill="x", pady=3)
                button = self._button(card, ("◉ " if selected else "○ ") + title,
                                      lambda v=value: self._set_camera_mode(v), small=True)
                button.configure(anchor="w", bg=card.cget("bg"), fg=INK)
                button.pack(fill="x")
                self._label(card, description, size=8, color=MUTED,
                            bg=card.cget("bg"), anchor="w").pack(fill="x", padx=10, pady=(0, 5))
                self._camera_mode_cards.append((card, button, value, title))
        if not compact:
            row = tk.Frame(parent, bg=WHITE)
            row.pack(fill="x", padx=10, pady=3)
            from core.camera import CAMERA_SIDE_CHOICES
            for code, side in CAMERA_SIDE_CHOICES.items():
                title = {"auto": "自動", "blue": "BLUE", "red": "RED"}[code]
                self._button(row, title, lambda v=side: self.app.var_camera_side.set(v),
                             primary=self.app.var_camera_side.get() == side,
                             small=True).pack(side="left", expand=True, fill="x", padx=2)
            self._label(parent, "視点スタイル", size=9, bold=True).pack(anchor="w", padx=12, pady=(6, 2))
            from core.camera import STYLES
            ttk.Combobox(parent, textvariable=self.app.var_style,
                         values=list(STYLES.values()), state="readonly").pack(fill="x", padx=12)
            self._camera_style_tiles(parent)
            for title, key in (("距離", "third_dist"), ("高さ", "cam_height"),
                               ("角度", "third_yaw"), ("回り込み", "motion_arc")):
                self._number_slider(parent, title, key)
            self._button(parent, "BLUE/RED カメラQA", self.app.on_dev_camera_qa,
                         small=True).pack(fill="x", padx=12, pady=6)

    def _set_camera_mode(self, value):
        self.app.var_camera_control_mode.set(value)
        for card, button, mode, title in self._camera_mode_cards:
            if not card.winfo_exists():
                continue
            selected = mode == value
            bg = "#EBF4FF" if selected else WHITE
            card.configure(bg=bg, highlightthickness=2 if selected else 1,
                           highlightbackground=BLUE if selected else LINE)
            button.configure(text=("◉ " if selected else "○ ") + title, bg=bg)

    def _camera_style_tiles(self, parent):
        """Real, earlier CameraQA stills: reference thumbnails, never live video."""
        source_path = Path(__file__).resolve().parents[1] / "assets" / "ui_reference" / "camera_comparison_20261020.jpg"
        if not source_path.is_file():
            return
        from PIL import Image, ImageTk
        from core.camera import STYLES
        self._label(parent, "過去のカメラQA参考画像", size=8, color=MUTED).pack(anchor="w", padx=10, pady=(5, 2))
        strip = tk.Frame(parent, bg=WHITE)
        strip.pack(fill="x", padx=8)
        with Image.open(source_path) as original:
            for n, (key, label) in enumerate((("third", "三人称"),
                                               ("third_cinema", "シネマ"),
                                               ("fps", "FPS"))):
                value = STYLES[key]
                selected = self.app.var_style.get() == value
                tile = tk.Frame(strip, bg=WHITE, highlightthickness=2 if selected else 1,
                                highlightbackground=BLUE if selected else LINE)
                tile.pack(side="left", fill="x", expand=True, padx=2)
                frame = original.crop((n * 320, 26, (n + 1) * 320, 206))
                frame.thumbnail((100, 58), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self._asset_photos.append(photo)
                tk.Button(tile, image=photo, command=lambda v=value: self._set_camera_style(v),
                          bd=0, relief="flat", bg=WHITE).pack(fill="x")
                self._button(tile, label, lambda v=value: self._set_camera_style(v),
                             small=True).pack(fill="x")
                self._camera_style_cards.append((tile, value))

    def _set_camera_style(self, value):
        self.app.var_style.set(value)
        for tile, choice in self._camera_style_cards:
            if tile.winfo_exists():
                selected = choice == value
                tile.configure(highlightthickness=2 if selected else 1,
                               highlightbackground=BLUE if selected else LINE)

    def _number_slider(self, parent, title, key):
        f = tk.Frame(parent, bg=WHITE)
        f.pack(fill="x", padx=12, pady=2)
        self._label(f, title, size=9).pack(side="left")
        lo, hi = self.app._slider_range(key)
        ttk.Scale(f, from_=lo, to=hi, variable=self.app.sl[key]).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Entry(f, textvariable=self.app.sl[key], width=7).pack(side="right")

    def _frame_choices(self, parent, compact=False):
        f = tk.Frame(parent, bg=WHITE)
        f.pack(fill="x", padx=7, pady=3) if compact else f.pack(fill="x", padx=12)
        self._label(f, self.app.var_work_frame.get() or "枠未選択", size=9,
                    color=MUTED).pack(anchor="w")
        self._button(f, "画像で選ぶ", self.app._open_work_gallery,
                     small=True).pack(fill="x", pady=3)
        if not compact:
            self._asset_tiles(f, "frames")
            self._label(f, "正式合格と確認用は図鑑で区別", color=MUTED, size=8).pack(anchor="w")
            self._button(f, "既存37バッジ", self.app._open_kill_frame_gallery,
                         small=True).pack(fill="x")
            ttk.Combobox(f, textvariable=self.app.var_kill_icon_motion,
                         values=list(__import__("core.kill_icons", fromlist=["MOTION_STYLES"]).MOTION_STYLES.values()),
                         state="readonly").pack(fill="x", pady=4)

    def _fx_choices(self, parent, compact=False):
        f = tk.Frame(parent, bg=WHITE)
        f.pack(fill="x", padx=7, pady=3) if compact else f.pack(fill="x", padx=12)
        self._label(f, self.app.var_work_effect.get() or "同名FX / 未選択", size=9,
                    color=MUTED).pack(anchor="w")
        self._button(f, "エフェクト図鑑", self.app._open_work_gallery,
                     small=True).pack(fill="x", pady=3)
        if not compact:
            self._asset_tiles(f, "effects")
            for label, value in (("弱", "weak"), ("強", "strong")):
                ttk.Radiobutton(f, text=label, variable=self.app.var_work_strength,
                                value=value).pack(side="left", padx=5)

    def _asset_tiles(self, parent, kind):
        """Show audited, real catalog thumbnails rather than mock artwork."""
        from core.work_kill_assets import list_assets, file_signature, resolve_asset
        from ui.work_gallery import thumbnail
        from PIL import ImageTk
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill="x", pady=3)
        assets = sorted(list_assets(kind, review=True),
                        key=lambda a: (a["status"] != "approved", a["id"]))
        selected = self.app.var_work_frame.get() if kind == "frames" else self.app.var_work_effect.get()
        if selected:
            selected_row = next((a for a in assets if a["id"] == selected), None)
            if selected_row is not None:
                assets.remove(selected_row)
                assets.insert(0, selected_row)
        for asset in assets[:3]:
            tile = tk.Frame(row, bg=WHITE, highlightthickness=1,
                            highlightbackground=BLUE if asset["id"] == selected else LINE)
            tile.pack(side="left", fill="x", expand=True, padx=1)
            action = ((lambda a=asset: self._apply_asset(a)) if kind == "frames" else
                      (lambda a=asset: self._apply_effect(a)))
            try:
                _, path = resolve_asset(asset["id"], kind, review=True)
                photo = ImageTk.PhotoImage(thumbnail(file_signature(path), 88))
                self._asset_photos.append(photo)
                tk.Button(tile, image=photo, command=action, relief="flat",
                          bd=0, bg=WHITE).pack(fill="x")
            except (OSError, ValueError):
                pass
            label = "合格" if asset["status"] == "approved" else "確認用"
            self._button(tile, f"{asset['id'][:9]}\n{label}", action,
                         small=True).pack(fill="x")

    def _apply_effect(self, asset):
        self.app.var_work_effect.set(asset["id"])
        if asset["status"] != "approved":
            self.app.var_work_review.set(True)
        self.app._invalidate_preview_snapshot()
        self.app._save_settings()
        self._build()

    def _inspector(self, parent, detailed=False):
        self._label(parent, "かんたん設定" if not detailed else "詳細編集",
                    size=12, bold=True).pack(anchor="w", padx=12, pady=8)
        self._camera_choices(parent)
        self._frame_choices(parent)
        self._fx_choices(parent)
        self._output_summary(parent)
        if detailed:
            self._button(parent, "全ての詳細設定を開く", self._show_legacy_settings,
                         small=True).pack(fill="x", padx=12, pady=5)

    def _dock_inspector(self, parent):
        self._label(parent, "ドック", size=12, bold=True).pack(anchor="w", padx=12, pady=8)
        self._camera_choices(parent)
        self._frame_choices(parent)
        self._fx_choices(parent)
        self._output_summary(parent)
        self._button(parent, "レイアウトを戻す", self._build, small=True).pack(fill="x", padx=12)

    def _test_inspector(self, parent):
        tabs = tk.Frame(parent, bg=WHITE)
        tabs.pack(fill="x", padx=6, pady=7)
        for label in ("カメラ", "キル演出"):
            self._button(tabs, label, lambda x=label: self._set_inspector(x),
                         primary=self.inspector_page.get() == label,
                         small=True).pack(side="left", fill="x", expand=True)
        if self.inspector_page.get() == "カメラ":
            self._camera_choices(parent)
            self._button(parent, "カメラ一括QA", self.app.on_dev_camera_qa,
                         primary=True, small=True).pack(fill="x", padx=12, pady=5)
        else:
            self._frame_choices(parent)
            self._fx_choices(parent)
            self._button(parent, "Work素材の設定", self.app._open_work_kill_settings,
                         primary=True, small=True).pack(fill="x", padx=12, pady=5)
        self._test_summary(parent)

    def _set_inspector(self, name):
        self.inspector_page.set(name)
        self._build()

    def _test_summary(self, parent):
        f = self._section(parent, "テスト結果")
        self._label(f, "未実行：一括QAの結果は診断ログで確認", color=MUTED,
                    size=9, wraplength=300, justify="left").pack(anchor="w")
        self._button(f, "診断ログ", self.app.on_show_diagnostics, small=True).pack(fill="x", pady=4)

    def _recommendations(self, parent):
        f = self._section(parent, "おすすめ設定")
        self._button(f, "おすすめ", self.app.on_smart_one_click, primary=True).pack(fill="x", pady=5)
        self._button(f, "詳細編集へ", self._show_legacy_settings).pack(fill="x")
        self._camera_choices(parent)
        self._fx_choices(parent)
        self._output_summary(parent)
        self._button(parent, "おすすめで書き出す", self.app.on_smart_one_click,
                     primary=True).pack(fill="x", padx=12, pady=8)

    def _wizard_guide(self, parent):
        f = self._section(parent, "見た目を整える")
        self._label(f, "おすすめ設定から始めましょう", color=MUTED).pack(anchor="w")
        self._button(f, "おすすめ", self.app.on_smart_one_click, primary=True).pack(fill="x", pady=5)
        self._camera_choices(parent)
        self._frame_choices(parent)
        self._fx_choices(parent)
        self._output_summary(parent)

    def _beginner_cards(self, parent):
        self._label(parent, "見た目で選ぶ", size=12, bold=True).pack(anchor="w", padx=12, pady=7)
        self._camera_choices(parent)
        self._frame_choices(parent)
        self._fx_choices(parent)
        self._button(parent, "登場アニメーションを選ぶ", self.app._open_work_kill_settings,
                     small=True).pack(fill="x", padx=12, pady=5)

    def _output_summary(self, parent):
        f = self._section(parent, "出力設定")
        self._label(f, f"1920 × 1080   /   {self.app.var_fps_ui.get()}   /   MP4",
                    size=9).pack(anchor="w")
        self._button(f, "出力先・GPU・音声を開く", self._show_legacy_settings,
                     small=True).pack(fill="x", pady=4)

    def _timeline(self):
        dock = self._panel(self.window)
        dock.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
        head = tk.Frame(dock, bg=WHITE)
        head.pack(fill="x", padx=8, pady=(5, 2))
        self._label(head, "タイムライン", size=11, bold=True).pack(side="left")
        self._label(head, "検出シーン / カメラ / キルフレーム / エフェクト",
                    size=8, color=MUTED).pack(side="right")
        self.timeline = tk.Canvas(dock, height=142 if self.index != 2 else 175,
                                  bg=WHITE, highlightthickness=0)
        self.timeline.pack(fill="x", padx=8, pady=(0, 4))
        self.timeline.bind("<Configure>", lambda _e: self._draw_timeline())
        foot = tk.Frame(dock, bg=WHITE)
        foot.pack(fill="x", padx=10, pady=(0, 6))
        self._label(foot, "キル前", size=9).pack(side="left")
        ttk.Spinbox(foot, from_=1, to=15, increment=.5, width=5,
                    textvariable=self.app.var_pre).pack(side="left", padx=4)
        self._label(foot, "秒   キル後", size=9).pack(side="left")
        ttk.Spinbox(foot, from_=1, to=15, increment=.5, width=5,
                    textvariable=self.app.var_post).pack(side="left", padx=4)
        self._label(foot, "秒", size=9).pack(side="left")
        self._button(foot, "選択範囲を確認", self.app.on_preview_play,
                     small=True).pack(side="right")
        self._draw_timeline()

    def _draw_timeline(self):
        if not hasattr(self, "timeline") or not self.timeline.winfo_exists():
            return
        c = self.timeline
        c.delete("all")
        width = max(600, c.winfo_width())
        labels = ("検出シーン", "カメラ", "キルフレーム", "エフェクト")
        colors = ("#D5E8FF", "#BBD9FD", "#FFE4A7", "#F8C8DF")
        scan = getattr(self.app, "_match_scan_cache", None)
        duration = float(getattr(scan, "length", 0) or max([k.time for k in self.app.kills], default=30) + 30)
        duration = max(duration, 1)
        left, right = 116, width - 10
        selected = self.app.lb_kills.curselection()
        short = int(c.cget("height")) < 130
        row_height = 23 if short else 31
        bar_height = 17 if short else 24
        for row, (label, color) in enumerate(zip(labels, colors)):
            y = 17 + row * row_height
            c.create_text(5, y + bar_height // 2, text=label, fill=INK, anchor="w",
                          font=("Meiryo UI", 8 if short else 9, "bold"))
            c.create_rectangle(left, y, right, y + bar_height, fill="#F5F8FC", outline=LINE)
            for i, kill in enumerate(self.app.kills):
                if row == 2 and not (self.app.var_work_frame.get() or self.app.var_kill_icon_style.get()):
                    continue
                if row == 3 and not self.app.var_work_effect.get():
                    continue
                x = left + (right - left) * (kill.time / duration)
                span = max(8, (right - left) * ((self.app.var_pre.get() + self.app.var_post.get()) / duration))
                x1, x2 = max(left, x - span * .55), min(right, x + span * .45)
                if row == 0:
                    use = i in self.app.checked_kills
                    fill = BLUE if selected and selected[0] == i else (color if use else "#EBEFF5")
                else:
                    fill = color if i in self.app.checked_kills else "#EBEFF5"
                tag = f"scene_{i}"
                c.create_rectangle(x1, y + 1, x2, y + bar_height - 1,
                                   fill=fill, outline=WHITE, tags=tag)
                c.tag_bind(tag, "<Button-1>", lambda _e, n=i: self._select_scene(n))
        for i in range(7):
            x = left + (right - left) * i / 6
            seconds = duration * i / 6
            c.create_text(x, 13, text=f"{int(seconds // 60):02d}:{int(seconds % 60):02d}",
                          anchor="s", fill=MUTED, font=("Meiryo UI", 7))

    def _sync(self):
        if not self.window.winfo_exists():
            return
        signature = (len(self.app.kills), tuple(sorted(self.app.checked_kills)),
                     tuple(self.app.lb_kills.curselection()))
        if signature != self._scene_signature:
            self._scene_signature = signature
            self._render_scenes()
            self._draw_timeline()
        if hasattr(self, "preview_status") and self.preview_status.winfo_exists():
            connected = bool(self.app.var_mirror.get())
            self.preview_status.configure(text="● 接続中" if connected else "● 接続待ち",
                                          fg="#13A66A" if connected else MUTED)
        self._offline_reference()
        self.window.after(350, self._sync)
