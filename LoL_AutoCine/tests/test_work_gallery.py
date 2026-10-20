"""Work catalog stays usable with 652 candidates without 652 Tk cards."""
import tkinter as tk
from types import SimpleNamespace

from ui.work_gallery import WorkGallery, matching, PAGE_SIZE


def test_filter_preserves_quality_labels():
    rows = [dict(id='083/a_simple_main', label='No.083 A', status='approved'),
            dict(id='001/a', label='Draft', status='review')]
    assert [x['id'] for x in matching(rows, '083', 'すべて')] == ['083/a_simple_main']
    assert [x['id'] for x in matching(rows, '', '仮素材')] == ['001/a']


def test_gallery_pages_assets_and_explicitly_marks_draft_selection():
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
        assert len(gallery.cards) == PAGE_SIZE
        gallery.kind.set('エフェクト')
        assert len(gallery.cards) == PAGE_SIZE
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
