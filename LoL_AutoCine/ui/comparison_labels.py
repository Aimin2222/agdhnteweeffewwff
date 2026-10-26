"""Neutral, friend-facing labels for the seven UI comparison candidates.

Internal family IDs and the audited design sources retain their original names.
Only the presentation served by the Windows comparison EXE uses these labels.
"""
from __future__ import annotations

import re


CANDIDATE_ORDER = (
    ("testB", "T-B-M"),
    ("legacy03", "L03-N"),
    ("testA", "T-A-M"),
    ("legacy06", "L06-L"),
    ("researchE", "R-E-main"),
    ("legacy02", "L02-M"),
    ("legacy05", "L05-M"),
)
CANDIDATE_LABELS = {family: f"候補{index}" for index, (family, _) in enumerate(CANDIDATE_ORDER, 1)}


def public_label(family: str) -> str:
    return CANDIDATE_LABELS[family]


def neutralize_reference_html(screen_id: str, html: str) -> str:
    """Remove candidate identities from served originals without editing the originals."""
    if screen_id == "T-A-M":
        html = html.replace("A案｜現行UI整理型", public_label("testA"))
        html = html.replace("A案 現行UI整理型", public_label("testA"))
    elif screen_id.startswith("R-E-"):
        label = public_label("researchE")
        html = re.sub(r"<title>.*?</title>", f"<title>LoL AutoCine — {label}</title>", html, count=1)
        html = html.replace('<span class="appname">Flow</span>', f'<span class="appname">{label}</span>')
        html = html.replace("E案 / かんたん作成＋Studio・独自案", "")
        for original, replacement in (
            (">Studioへ<", ">詳細編集へ<"),
            (">Studio編集<", ">詳細編集<"),
            (">Studioで細かく編集<", ">詳細編集で細かく調整<"),
            (">Studio・シーン詳細<", ">詳細編集・シーン詳細<"),
        ):
            html = html.replace(original, replacement)
    return html
