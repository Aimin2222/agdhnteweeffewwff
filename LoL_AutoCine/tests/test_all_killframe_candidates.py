"""Source-pixel preservation checks for the offline all-89 candidate archive.

Run during a batch with AUTOCINE_KILLFRAME_BATCH=<1..12>. The final run omits
the variable and requires every registered source to have been processed.
"""
from pathlib import Path
import hashlib
import json
import os

import numpy as np
import pytest
from PIL import Image

from tools.build_all_killframe_candidates import verify_source
from tools.build_all_killframe_candidates import candidate

APP = Path(__file__).resolve().parents[1]
ROOT = APP / 'assets/kill_frames'
OUT = ROOT / 'all_sources'
INVENTORY = json.loads((OUT / 'source_inventory.json').read_text(encoding='utf-8'))
BATCH = os.environ.get('AUTOCINE_KILLFRAME_BATCH')
SOURCES = [e for e in INVENTORY['sources'] if not BATCH or e['batch'] == int(BATCH)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inventory_covers_exactly_all_originals_and_no_invented_sources():
    originals = json.loads((APP / 'assets/kill_concepts/source_import_manifest.json').read_text(encoding='utf-8-sig'))['assets']
    assert len(INVENTORY['sources']) == len(originals) == 89
    assert {s['source_file']: s['sha256'] for s in INVENTORY['sources']} == {s['stored_file']: s['sha256'] for s in originals}
    for batch in range(1, 13):
        assert 1 <= len([s for s in INVENTORY['sources'] if s['batch'] == batch]) <= 8
    assert not (OUT / 'source_inventory.json').read_text(encoding='utf-8').count('C:\\Users')


@pytest.mark.parametrize('source', SOURCES, ids=lambda s: f's{s["index"]:03}')
def test_every_original_is_accounted_for_with_source_pixels_and_real_holes(source):
    path = OUT / f's{source["index"]:03}/manifest.json'
    assert path.is_file(), 'No silent skips: every registered source needs a result manifest'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    assert len(manifest['assets']) == len(source['components']) > 0
    assert manifest['source_sha256'] == source['sha256']
    assert len(verify_source(source, manifest)) == source['component_count']
    assert not manifest['rgb_modified'] and not manifest['generated_or_inpainted']
    assert manifest['status'] == 'unapproved_candidates'
    assert len(manifest['review_pages']) == (source['component_count'] + 7) // 8
    for review in manifest['review_pages']:
        with Image.open(ROOT / review) as image:
            assert image.width == 1800
    for entry in manifest['assets']:
        definition = next(c for c in source['components'] if c['id'] == entry['id'])
        for key in ('crop_box', 'portrait_holes', 'theme', 'role', 'intensity'):
            assert entry[key] == definition[key]
        with Image.open(ROOT / entry['file']) as asset:
            alpha = np.asarray(asset)[:, :, 3]
            assert np.count_nonzero(alpha > 0) >= 40, entry['id']
            assert np.count_nonzero(alpha >= 200) >= 12, entry['id']
        assert entry['component'] != 'frame' or entry['portrait_holes'], entry['id']
        assert entry['role'] in ('melee', 'ranged', 'hybrid', 'unspecified')
        assert entry['intensity'] in ('weak', 'strong', 'unspecified')


def test_protected_original_badges_and_three_theme_candidates_remain_byte_identical():
    protected = json.loads((OUT / 'protected_sha256.json').read_text(encoding='utf-8'))
    assert protected['base_commit'] == '22861a90c585c8b6b91263241d7437ccf956acc2'
    assert len(list((APP / 'assets/kill_badges').glob('*.png'))) == 37
    assert sum(p.startswith('assets/kill_badges/') for p in protected['files']) == 37
    for path, expected in protected['files'].items():
        assert digest(APP / path) == expected, path


def test_all_31_catalog_names_have_observed_source_mappings_without_runtime_changes():
    from core.kill_frame_themes import THEMES
    table = json.loads((OUT / 'theme_correspondence.json').read_text(encoding='utf-8'))
    registered = {row['theme']: row for row in table['registered_themes']}
    assert set(registered) == set(THEMES)
    sources = {s['index']: s for s in INVENTORY['sources']}
    for theme, row in registered.items():
        assert theme in sources[row['primary_source_index']]['themes']
        assert row['actual_source_file'] == sources[row['primary_source_index']]['source_file']
        assert row['old_catalog_source_file'] == THEMES[theme].source_file
        assert row['observed_source_indices']
    assert table['runtime_catalog_modified'] is False


@pytest.mark.parametrize('background', [(37, 56, 81), (236, 243, 249)])
def test_portraits_covering_most_of_a_board_do_not_become_background_samples(background):
    # Dark hair fills 2/3 of this otherwise uniform plate. Fitting all crop
    # pixels would incorrectly use the hair as the matte and retain the plate.
    rgb = np.empty((100, 300, 3), dtype='uint8')
    rgb[:] = background
    rgb[4:96, 4:109] = (3, 7, 11)
    rgb[4:96, 192:297] = (5, 9, 13)
    rgb[25:75, 147:153] = (200, 151, 24)
    config = {'crop_box': [0, 0, 300, 100], 'roi_regions': [],
              'portrait_holes': [{'rectangle': [4, 4, 108, 95]}, {'rectangle': [192, 4, 296, 95]}],
              'candidate_thresholds': [16, 78], 'min_component_pixels': 3,
              'exclude_regions': [], 'candidate_exclusions': []}
    result, model = candidate(Image.fromarray(rgb), config)
    pixels = np.asarray(result)
    assert np.array_equal(pixels[:, :, :3], rgb)
    assert not pixels[0, :, 3].any()  # The actual plate background is transparent.
    assert not pixels[10:90, 10:100, 3].any()  # Portrait interiors are transparent.
    assert np.all(pixels[25:75, 147:153, 3] >= 240)  # Gold detail survives.
    assert model['sample_pixels'] > 100
