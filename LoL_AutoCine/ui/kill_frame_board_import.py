# -*- coding: utf-8 -*-
"""Attach the ACTUAL concept-board files created in this ChatGPT conversation."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from core.kill_frame_abcd import BY_CODE, installed_theme_styles, install_concept_board, recognize_board
from core.kill_icons import register_original_board_styles

def choose_and_import(parent):
    paths=filedialog.askopenfilenames(
        parent=parent,
        title="このチャットで作成した完成ボード画像を選択（複数可）",
        filetypes=[("デザイン画像","*.png *.jpg *.jpeg *.webp"),("すべてのファイル","*.*")])
    if not paths:return False
    success=[];failures=[]
    for path in paths:
        try:
            slug=recognize_board(path)
            if slug is None:
                slug=simpledialog.askstring(
                    "テーマを選択",
                    "名前から判定できませんでした。\n以下のようにテーマIDを入力してください。\n"
                    "例: elderwood, project, star_guardian\n"
                    "未登録の画像はキャンセルできます。",
                    parent=parent)
            if slug not in BY_CODE:
                failures.append(f"{path}: テーマ未選択またはIDが不明")
                continue
            code,dst=install_concept_board(path,slug)
            success.append(f"{BY_CODE[code].name} ← {path}")
        except Exception as exc:
            failures.append(f"{path}: {exc}")
    if success:
        register_original_board_styles()
    notice=(f"元画像を取り込みました：{len(success)}テーマ\n"
            f"Dテンプレート追加：{len(success)*2}種類（弱め／強め）\n"
            "元のボード画像をPNGのまま保存し、中央の装飾部分を切り出して利用します。\n"
            "左右のチャンピオンは試合データの本物のアイコンに差し替えます。\n"
            "プレビューを確認し、切り出し位置が合わなければ採用前に調整してください。")
    if failures:
        notice+="\n\n取り込めなかった画像：\n"+"\n".join(failures[:9])
        messagebox.showwarning("キルフレーム素材取り込み",notice,parent=parent)
    elif success:
        messagebox.showinfo("キルフレーム素材取り込み",notice,parent=parent)
    return bool(success)
