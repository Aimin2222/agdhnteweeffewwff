"""Work catalog stays usable with 652 candidates without 652 Tk cards."""
import tkinter as tk
from types import SimpleNamespace
from PIL import Image

from ui.work_gallery import (WorkGallery, matching, PAGE_SIZE, centered_preview,
                             page_layout, theme_category, thumbnail_width)


def test_filter_preserves_quality_labels():
    rows = [dict(id='083/a_simple_main', label='No.083 A', status='approved'),
            dict(id='001/a', label='Draft', status='review')]
    assert [x['id'] for x in matching(rows, '083', 'すべて')] == ['083/a_simple_main']
    assert [x['id'] for x in matching(rows, '', '仮素材')] == ['001/a']


def test_region_and_skin_filters_use_catalog_theme_without_reclassifying_quality():
    rows = [dict(id='001/demacia_weak', label='Demacia', theme='demacia', status='review'),
            dict(id='002/elderwood_weak', label='Elderwood', theme='elderwood', status='review'),
            dict(id='083/a_simple_main', label='No.083 A', theme='a_simple', status='approved')]
    assert theme_category('demacia') == '地域モチーフ'
    assert theme_category('elderwood') == 'スキンテーマ'
    assert [x['id'] for x in matching(rows, '', 'すべて', '地域モチーフ')] == ['001/demacia_weak']
    assert [x['id'] for x in matching(rows, '', '仮素材', 'スキンテーマ', 'elderwood')] == ['002/elderwood_weak']
    assert [x['id'] for x in matching(rows, '', '正式合格', '基本案・その他')] == ['083/a_simple_main']


def test_gallery_only_centers_alpha_content_without_upscaling_or_editing_source():
    source = Image.new('RGBA', (100, 50))
    source.paste((255, 0, 0, 255), (10, 10, 30, 30))
    output = centered_preview(source, (100, 50))
    assert output.getchannel('A').getbbox() == (40, 15, 60, 35)
    assert source.getchannel('A').getbbox() == (10, 10, 30, 30)


def test_responsive_catalog_page_layout_keeps_cards_legible():
    assert page_layout(800, 600) == (3, PAGE_SIZE)
    assert page_layout(620, 600) == (2, 4)  # Normal 1090px window.
    assert page_layout(345, 400) == (2, 2)  # Minimum window, smaller thumbnails.
    assert thumbnail_width(345, 2) < thumbnail_width(620, 2)
    assert page_layout(300, 600) == (1, 2)
    assert page_layout(300, 350) == (1, 1)


def test_gallery_pages_assets_and_explicitly_marks_draft_selection(monkeypatch):
    root = tk.Tk()
    root.withdraw()
    app = SimpleNamespace(root=root, var_work_frame=tk.StringVar(value=''),
                          var_work_effect=tk.StringVar(value=''),
                          var_work_review=tk.BooleanVar(value=False),
                          _invalidate_preview_snapshot=lambda: None,
                          _save_settings=lambda: None, log=lambda _msg: None)
    gallery = WorkGallery(app)
    gallery.win.withdraw()
    try:
        assert len(gallery.items['frames']) == 652
        assert len(gallery.items['effects']) == 35
        assert len(gallery.cards) == 4
        monkeypatch.setattr(gallery.left, 'winfo_width', lambda: 800)
        monkeypatch.setattr(gallery.left, 'winfo_height', lambda: 600)
        gallery._sync_layout()
        assert len(gallery.cards) == PAGE_SIZE
        monkeypatch.setattr(gallery.left, 'winfo_width', lambda: 300)
        gallery._sync_layout()
        assert len(gallery.cards) == 2
        gallery.kind.set('エフェクト')
        assert len(gallery.cards) == 2
        gallery.status.set('正式合格')
        assert len(gallery.cards) == 0
        gallery.status.set('すべて')
        item = gallery.filtered()[0]
        gallery.select(item)
        gallery.apply()
        assert app.var_work_effect.get() == item['id']
        assert app.var_work_frame.get() == '083/a_simple_main'
        assert app.var_work_review.get()
    finally:
        if gallery.win.winfo_exists():
            gallery.close()
        root.destroy()
