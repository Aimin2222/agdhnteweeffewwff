"""Write portable numeric QA; numerical passes never grant visual approval."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

APP = Path(__file__).resolve().parents[1]
ROOT = APP/'assets/kill_frames'


def verify():
    manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    pilot = json.loads((ROOT/'qa/pilot_manifest.json').read_text(encoding='utf-8'))
    old = {(a['theme'], Path(a['file']).stem): a for a in pilot['assets']}
    source_manifest = json.loads((APP/'assets/kill_concepts/source_import_manifest.json').read_text(encoding='utf-8-sig'))
    for entry in source_manifest['assets']:
        raw = (APP/'assets/kill_concepts'/entry['stored_file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
        assert len(raw) == entry['bytes']
    result = {'schema_version': 1, 'status': 'candidate_pending_visual_approval',
              'visual_approval': False, 'original_source_sha_matches': len(source_manifest['assets']),
              'old_badge_png_count': len(list((APP/'assets/kill_badges').glob('*.png'))),
              'rgba_assets': len(manifest['assets']), 'alpha_masks': len(manifest['assets']),
              'themes': ['winter_festival', 'project', 'elderwood'], 'assets': [],
              'preview_matrix': {'single_assets_x_backgrounds': [15, 4],
                                 'portrait_base_frames_x_backgrounds': [6, 4],
                                 'weak_strong_x_motifs_x_themes_x_backgrounds': [2, 3, 3, 4]},
              'limitations': ['Flattened source RGB/matte cannot be unmixed without RGB changes.',
                              'Occluded ornament cannot be reconstructed without repainting.',
                              'Alpha area retention is an integrity gate, not a visual quality score.']}
    for entry in manifest['assets']:
        source = APP/'assets/kill_concepts'/entry['source_file']
        pixels = np.asarray(Image.open(ROOT/entry['file']))
        expected = np.asarray(Image.open(source).convert('RGB').crop(entry['crop_box']))
        assert np.array_equal(pixels[:, :, :3], expected)
        alpha = pixels[:, :, 3]
        mask = np.asarray(Image.open(ROOT/entry['mask_file']))
        assert np.array_equal(mask, alpha)
        for key, hash_key in (('file', 'sha256'), ('mask_file', 'mask_sha256')):
            assert hashlib.sha256((ROOT/entry[key]).read_bytes()).hexdigest() == entry[hash_key]
        name = Path(entry['file']).stem
        before = np.asarray(Image.open(ROOT/'qa/pilot_masks'/entry['theme']/(name+'.alpha.png')))
        previous = old[(entry['theme'], name)]
        assert hashlib.sha256((ROOT/'qa/pilot_masks'/entry['theme']/(name+'.alpha.png')).read_bytes()).hexdigest() == previous['mask_sha256']
        result['assets'].append({'file': entry['file'], 'rgb_source_exact': True, 'mask_matches': True,
                                 'sha_matches': True, 'dimensions': [pixels.shape[1], pixels.shape[0]],
                                 'alpha_changed_pixels': int(np.count_nonzero(alpha != before)),
                                 'alpha_revealed_pixels': int(np.count_nonzero(alpha > before)),
                                 'alpha_suppressed_pixels': int(np.count_nonzero(alpha < before)),
                                 'alpha_mass_retained_ratio': round(float(alpha.astype(float).sum()/before.astype(float).sum()), 5),
                                 'single_pixel_noise_removed': entry['alpha_model']['tiny_noise_pixels_removed']})
    result['rgb_modified_assets'] = 0
    (ROOT/'qa/candidate_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    data = verify()
    print(json.dumps({k: data[k] for k in ('rgba_assets', 'original_source_sha_matches', 'rgb_modified_assets', 'visual_approval')}))
