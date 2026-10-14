"""Candidate provenance, measured catalog, edge cleanup and review coverage."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import pytest
from core.kill_frame_themes import THEMES, source_path

APP = Path(__file__).resolve().parents[1]
ROOT = APP/'assets/kill_frames'
MANIFEST = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
MAPPING = json.loads((ROOT/'source_mapping.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('theme', ('winter_festival', 'project', 'elderwood'))
def test_catalog_matches_real_files_and_measured_pixels(theme):
    item = MAPPING['themes'][theme]
    registered = THEMES[theme]
    assert registered.source_file == item['source_file']
    assert source_path(APP/'assets/kill_concepts', theme).is_file()
    assert registered.source_size == tuple(item['source_dimensions'])
    assert np.allclose(registered.motif_centers, item['motif_centers_normalized'])
    for name, box in registered.measured_regions:
        assert box == tuple(item['assets'][name]['crop_box'])
        assert 0 <= box[0] < box[2] <= registered.source_size[0]
        assert 0 <= box[1] < box[3] <= registered.source_size[1]


@pytest.mark.parametrize('entry', MANIFEST['assets'], ids=lambda a: a['file'])
def test_candidate_changes_alpha_without_erasing_art(entry):
    name = Path(entry['file']).stem
    old = np.asarray(Image.open(ROOT/'qa/pilot_masks'/entry['theme']/(name+'.alpha.png'))).astype(float)
    alpha = np.asarray(Image.open(ROOT/entry['mask_file'])).astype(float)
    assert np.count_nonzero(old != alpha) > 20
    # Tightening matte must leave a substantial frame/motif, not pass by
    # replacing the whole asset with transparency.
    assert alpha.sum() > old.sum() * .55
    assert np.count_nonzero(alpha >= 240) > 100
    assert MANIFEST['status'] == 'candidate_pending_visual_approval'


@pytest.mark.parametrize('theme', ('winter_festival', 'project', 'elderwood'))
def test_review_covers_original_size_before_after_and_portrait_variants(theme):
    assert Image.open(ROOT/f'qa/{theme}_before_after.png').size == (2400, 2355)
    assert Image.open(ROOT/f'qa/{theme}_portraits.png').size == (2400, 1895)
    for name in ('Akali', 'Mordekaiser'):
        icon = Image.open(ROOT/f'qa/reference_icons/{name}.png')
        assert icon.size == (128, 128)
    assert MANIFEST['portrait_preview']['sample_only'] is True


def test_all_89_originals_remain_exact_and_old_37_are_present():
    source = APP/'assets/kill_concepts'
    data = json.loads((source/'source_import_manifest.json').read_text(encoding='utf-8-sig'))
    assert len(data['assets']) == 89
    for entry in data['assets']:
        raw = (source/entry['stored_file']).read_bytes()
        assert len(raw) == entry['bytes']
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
    assert len(list((APP/'assets/kill_badges').glob('*.png'))) == 37


def test_old_pilot_builder_cannot_overwrite_candidate(tmp_path):
    from tools.extract_killframe_original_alpha_pilot import build
    destination = tmp_path/'assets/kill_frames'
    destination.mkdir(parents=True)
    marker = destination/'manifest.json'
    marker.write_text('{"status":"candidate_pending_visual_approval"}', encoding='utf-8')
    original = marker.read_bytes()
    with pytest.raises(RuntimeError, match='Refusing to overwrite'):
        build(tmp_path)
    assert marker.read_bytes() == original
