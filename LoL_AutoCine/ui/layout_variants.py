"""Nine presentation shells over one AutoCine App and one set of Tk variables."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.smart_camera_director import CONTROL_MODES
from core.work_kill_assets import list_assets
from ui.director_work_controls import select_frame_with_effect


LAYOUT_NAMES = (
    "1 ワンクリック・ホーム型",
    "2 動画編集ソフト標準型",
    "3 ハイブリッド固定プレビュー型",
    "4 OBS風ドック型",
    "5 ステップウィザード型",
    "6 ライブラリ＋編集分離型",
    "7 現行UI整理型",
    "8 カメラ・エフェクトテスト特化型",
    "9 初心者向けカード型",
)
OLD_NAMES = {"現行配置 A": LAYOUT_NAMES[6], "テスト配置 B": LAYOUT_NAMES[7]}
SCENE_LEFT = {3, 5, 8}


def _card(parent, title, note):
    frame = ttk.Frame(parent, style="Card.TFrame", padding=(12, 10))
    ttk.Label(frame, text=title, style="Section.TLabel").pack(anchor="w")
    ttk.Label(frame, text=note, style="CardMuted.TLabel", wraplength=260).pack(
        anchor="w", fill="x", pady=(3, 8))
    return frame


def _button(frame, title, command, accent=False):
    ttk.Button(frame, text=title, command=command,
               style="Accent.TButton" if accent else "TButton").pack(fill="x", pady=3)


class InlineWorkLibrary:
    """A compact real catalog pane; the existing full gallery remains available."""

    def __init__(self, app, parent):
        self.app = app
        self.frame = _card(parent, "Work素材ライブラリ", "画像を選ぶと同名FXも既存設定へ適用")
        tabs = ttk.Frame(self.frame)
        tabs.pack(fill="x")
        ttk.Button(tabs, text="素材を探す", command=lambda: self.show("library")).pack(side="left", expand=True, fill="x")
        ttk.Button(tabs, text="編集する", command=lambda: self.show("edit")).pack(side="left", expand=True, fill="x")
        self.browse = ttk.Frame(self.frame)
        self.edit = ttk.Frame(self.frame)
        self.query = tk.StringVar()
        ttk.Entry(self.browse, textvariable=self.query).pack(fill="x")
        self.listbox = tk.Listbox(self.browse, height=6, exportselection=False)
        self.listbox.pack(fill="x", pady=5)
        self.rows = []
        self.query.trace_add("write", lambda *_: self.refresh())
        self.listbox.bind("<<ListboxSelect>>", self._preview)
        self.image = ttk.Label(self.browse, text="素材を選択", anchor="center")
        self.image.pack(fill="x")
        self._photo = None
        self.status = ttk.Label(self.browse, text="", style="CardMuted.TLabel", wraplength=260)
        self.status.pack(fill="x", pady=4)
        _button(self.browse, "選択した枠＋同名FXを適用", self.apply)
        _button(self.browse, "全画面の画像図鑑", app._open_work_gallery)
        _button(self.edit, "シーンを選ぶ", lambda: app._focus_editor_zone("scene"))
        _button(self.edit, "カメラを調整", lambda: app._focus_editor_zone("camera"))
        _button(self.edit, "キル演出を調整", lambda: app._focus_editor_zone("fx"))
        _button(self.edit, "選択シーンを書き出す", app.on_make_checked)
        self.refresh()
        self.show("library")

    def show(self, page):
        self.browse.pack_forget()
        self.edit.pack_forget()
        (self.browse if page == "library" else self.edit).pack(fill="x", pady=(8, 0))

    def activate(self):
        if self.rows and not self.listbox.curselection():
            self.listbox.selection_set(0)
            self._preview()

    def refresh(self):
        needle = self.query.get().strip().casefold()
        self.rows = [row for row in list_assets("frames", review=True)
                     if needle in (row["id"] + " " + row.get("label", "")).casefold()]
        self.rows.sort(key=lambda row: (row["status"] != "approved", row["id"]))
        self.rows = self.rows[:80]
        self.listbox.delete(0, "end")
        for row in self.rows:
            state = "合格" if row["status"] == "approved" else "確認用"
            self.listbox.insert("end", f"{row['id']}  [{state}]")

    def _preview(self, _event=None):
        selected = self.listbox.curselection()
        if not selected:
            return
        row = self.rows[selected[0]]
        try:
            from PIL import ImageTk
            from core.work_kill_assets import file_signature, resolve_asset
            from ui.work_gallery import thumbnail
            _, path = resolve_asset(row["id"], "frames", review=True)
            self._photo = ImageTk.PhotoImage(thumbnail(file_signature(path), 205))
            self.image.configure(image=self._photo, text="")
        except Exception as exc:
            self._photo = None
            self.image.configure(image="", text=f"プレビュー不可: {type(exc).__name__}")
        state = "正式合格" if row["status"] == "approved" else "確認用・未合格"
        self.status.configure(text=f"{row['id']} — {state}")

    def apply(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        row = self.rows[selected[0]]
        effect = select_frame_with_effect(self.app, row["id"])
        refresh = getattr(self.app, "_work_settings_refresh", None)
        if callable(refresh):
            refresh()
        self.app._invalidate_preview_snapshot()
        self.app._save_settings()
        self.status.configure(text=f"適用: {row['id']} / FX: {effect['id'] if effect else 'なし'}"
                              + ("（確認用）" if row["status"] != "approved" else ""))


def install(app, left, right, root, body):
    """Create the presentation controls once, bound only to existing handlers."""
    cards = {}
    home = _card(right, "ワンクリック・ホーム", "準備→スキャン→見どころ→動画作成")
    _button(home, "① リプレイ準備", app.on_quick_prepare)
    _button(home, "② 試合全体をスキャン", app.on_scan)
    _button(home, "③ おすすめ設定で自動作成", app.on_smart_one_click, True)
    _button(home, "詳細編集", lambda: app._focus_editor_zone("camera"))
    cards[1] = home

    editor = _card(left, "編集ソフト型・素材", "素材・プレビュー・設定の3列と広いタイムライン")
    _button(editor, "Work画像ライブラリ", app._open_work_gallery)
    _button(editor, "カメラ編集", lambda: app._focus_editor_zone("camera"))
    _button(editor, "キル演出編集", lambda: app._focus_editor_zone("fx"))
    _button(editor, "選択シーンを書き出す", app.on_make_checked, True)
    cards[2] = editor

    hybrid = _card(left, "ハイブリッド・クイック選択", "映像を見ながら少数の設定を選択")
    ttk.Combobox(hybrid, state="readonly", textvariable=app.var_camera_control_mode,
                 values=list(CONTROL_MODES.values())).pack(fill="x", pady=3)
    _button(hybrid, "WorkフレームとFX", app._open_work_gallery)
    _button(hybrid, "詳細設定を開く", lambda: app._focus_editor_zone("camera"))
    cards[3] = hybrid

    dock = _card(right, "ドック操作", "カメラ／素材／音声／出力を個別に開く")
    for title, zone in (("カメラドック", "camera"), ("FXドック", "fx"),
                        ("音声・出力ドック", "output")):
        _button(dock, title, lambda z=zone: app._focus_editor_zone(z))
    _button(dock, "素材ドック", app._open_work_gallery)
    _button(dock, "シーン編集に戻す", lambda: app._focus_editor_zone("scene"))
    cards[4] = dock

    guide = _card(left, "4ステップで動画作成", "戻っても選択シーン・設定は残ります")
    for title, action in (("1 準備", app.on_quick_prepare), ("2 試合スキャン", app.on_scan),
                          ("3 カメラ・素材", lambda: app._focus_editor_zone("camera")),
                          ("4 書き出し", app.on_make_checked)):
        _button(guide, title, action)
    cards[5] = guide

    library = InlineWorkLibrary(app, left)
    cards[6] = library.frame
    app._ui_inline_library = library

    beginner = _card(right, "初心者向け選択カード", "大きい操作から順番に選べます")
    _button(beginner, "リプレイを準備", app.on_quick_prepare)
    _button(beginner, "シーンを探す", app.on_scan)
    _button(beginner, "カメラを選ぶ", lambda: app._focus_editor_zone("camera"))
    _button(beginner, "キルフレームを画像で選ぶ", app._open_work_gallery)
    _button(beginner, "動画を作る", app.on_make_checked, True)
    cards[9] = beginner

    wizard = ttk.Frame(root, padding=(12, 4))
    ttk.Label(wizard, text="制作ステップ", style="Muted.TLabel").pack(side="left", padx=(0, 8))
    for title, action in (("① 準備", app.on_quick_prepare), ("② スキャン", app.on_scan),
                          ("③ 編集", lambda: app._focus_editor_zone("camera")),
                          ("④ 出力", app.on_make_checked)):
        ttk.Button(wizard, text=title, command=action).pack(side="left", padx=3)
    return cards, wizard


def configure(app, index):
    for frame in app._ui_variant_cards.values():
        frame.pack_forget()
    app._ui_wizard_strip.pack_forget()
    if index in app._ui_variant_cards:
        frame = app._ui_variant_cards[index]
        before = app._nav_home_card if frame.master is app.left_scroll.inner else app._ui_scene_card
        frame.pack(before=before, fill="x", pady=(0, 8))
    if index == 5:
        app._ui_wizard_strip.pack(before=app._ui_body, fill="x")
    if index == 6:
        app._ui_inline_library.activate()
