"""Offline, bounded source-pixel extraction. Never imported by the application.

Measured annotations are independent of the production theme catalog. This
builder writes ONLY all_sources/; the original boards and three-theme assets
are read-only inputs. A batch contains at most eight sources, opened serially.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from PIL import Image, ImageDraw

# Older offline extraction tools use sibling imports. Keep the application
# import graph unchanged while allowing this utility to be tested as a module.
TOOLS = str(Path(__file__).resolve().parent)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

try:
    from build_killframe_candidates import candidate, font
    from extract_killframe_original_alpha_pilot import checker, shape_mask
except ImportError:
    from tools.build_killframe_candidates import candidate, font
    from tools.extract_killframe_original_alpha_pilot import checker, shape_mask

APP = Path(__file__).resolve().parents[1]
ROOT = APP / 'assets/kill_frames'
OUT = ROOT / 'all_sources'
BASE = '22861a90c585c8b6b91263241d7437ccf956acc2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify_source(entry, manifest):
    """Decode only one source and its crops, including all invisible RGB."""
    path = APP / 'assets/kill_concepts' / entry['source_file']
    assert sha(path) == entry['sha256'], entry['source_file']
    checks = []
    with Image.open(path) as raw:
        source = raw.convert('RGB')
        assert list(source.size) == entry['dimensions']
        for a in manifest['assets']:
            with Image.open(ROOT / a['file']) as asset, Image.open(ROOT / a['mask_file']) as mask:
                crop = np.asarray(source.crop(a['crop_box']))
                rgba = np.asarray(asset)
                alpha = np.asarray(mask)
                assert asset.mode == 'RGBA' and mask.mode == 'L'
                assert np.array_equal(rgba[:, :, :3], crop), a['id']
                assert np.array_equal(alpha, rgba[:, :, 3]), a['id']
                assert sha(ROOT / a['file']) == a['sha256']
                assert sha(ROOT / a['mask_file']) == a['mask_sha256']
                assert np.any(alpha == 0) and np.any(alpha > 0), a['id']
                holes = shape_mask(asset.size, a['portrait_holes'], a['crop_box'])
                if holes.any():
                    assert not np.any(alpha[holes == 1]), a['id']
                checks.append({'id': a['id'], 'rgb_exact': True, 'independent_mask_exact': True,
                               'portrait_hole_pixels_zero': int((holes == 1).sum()),
                               'transparent_pixels': int((alpha == 0).sum()),
                               'partial_pixels': int(((alpha > 0) & (alpha < 255)).sum()),
                               'visible_pixels': int((alpha > 0).sum())})
    return checks


def fit_preview(image, size):
    im = image.copy()
    im.thumbnail(size, Image.Resampling.LANCZOS)
    return im


def demo(image, config, icons):
    """Portrait-only demonstration, including measured beveled polygons."""
    result = Image.new('RGBA', image.size)
    crop_box = config['crop_box']
    for shape, icon in zip(config['portrait_holes'], icons):
        kind, values = next(iter(shape.items()))
        if kind == 'polygon':
            xs, ys = zip(*values)
            box = [min(xs), min(ys), max(xs), max(ys)]
        else:
            box = values
        local = [round(v - crop_box[i % 2]) for i, v in enumerate(box)]
        width, height = local[2] - local[0] + 1, local[3] - local[1] + 1
        portrait = icon.resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')
        mask = shape_mask((width, height), [shape], box)
        portrait.putalpha(Image.fromarray(np.rint(mask * 255).astype('uint8')))
        result.alpha_composite(portrait, tuple(local[:2]))
    result.alpha_composite(image)
    return result


def review_pages(items, target, game, icons):
    """Every sprite on four backgrounds, two portrait samples and small size.

    Labels are outside the preview tiles. They are NEVER written to sprites.
    Review resampling is explicitly separate from unscaled source-pixel assets.
    """
    pages = []
    cw, ch = 300, 160
    for start in range(0, len(items), 8):
        selected = items[start:start + 8]
        canvas = Image.new('RGB', (cw * 6, 42 + ch * len(selected)), '#252933')
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 9), 'UNAPPROVED | CHECKER / BLACK / WHITE / LoL / AKALI x MORDEKAISER / SMALL 160px', fill='white', font=font(14))
        for row, (entry, image) in enumerate(selected):
            for col in range(6):
                size = (cw, ch - 32)
                bg = checker(size) if col == 0 else Image.new('RGBA', size, 'black' if col == 1 else 'white') if col < 3 else game.resize(size, Image.Resampling.LANCZOS)
                shown = demo(image, entry, icons) if col >= 4 else image
                shown = fit_preview(shown, (160 if col == 5 else cw - 14, ch - 38))
                bg.alpha_composite(shown, ((cw - shown.width) // 2, (size[1] - shown.height) // 2))
                canvas.paste(bg.convert('RGB'), (col * cw, 42 + row * ch + 30))
                draw.text((col * cw + 6, 42 + row * ch + 6), entry['id'], fill='white', font=font(11))
        path = target / f'review_{start // 8 + 1:02}.jpg'
        canvas.save(path, quality=94, subsampling=0)
        pages.append(path.relative_to(ROOT).as_posix())
    return pages


def combinations(items, target, game, icons):
    """All present frames x every explicitly labeled role motif, by theme.

    Demo uses the source frame center, not a production-engine anchor. Unknown
    motifs never silently become melee/ranged/hybrid. No video or UI hooks.
    """
    count, pages = 0, []
    by_theme = {}
    for item in items:
        by_theme.setdefault(item[0]['theme'], []).append(item)
    tiles = []
    for theme, entries in by_theme.items():
        frames = [e for e in entries if e[0]['component'] == 'frame']
        motifs = [e for e in entries if e[0]['component'] == 'center' and e[0]['role'] in ('melee', 'ranged', 'hybrid')]
        for frame, image in frames:
            for center, motif in motifs:
                combined = demo(image, frame, icons)
                # UI integration/FX are outside scope: illustrative center placement.
                combined.alpha_composite(motif, ((image.width - motif.width) // 2, (image.height - motif.height) // 2))
                tiles.append((frame['id'] + ' / ' + center['id'], combined))
                count += 1
                if len(tiles) == 24:
                    pages.append(save_combinations(tiles, target, game, len(pages) + 1))
                    tiles.clear()
    if tiles:
        pages.append(save_combinations(tiles, target, game, len(pages) + 1))
    return {'count': count, 'files': pages, 'anchor': 'illustrative frame crop center; no runtime integration'}


def save_combinations(tiles, target, game, number):
    canvas = Image.new('RGB', (1600, 35 + 150 * ((len(tiles) + 3) // 4)), '#252933')
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), 'UNAPPROVED / DEMO PORTRAITS / ALL PRESENT FRAME x LABELED ROLE VARIANTS', fill='white', font=font(14))
    for index, (label, image) in enumerate(tiles):
        x, y = index % 4 * 400, 35 + index // 4 * 150
        bg = game.resize((400, 124), Image.Resampling.LANCZOS)
        shown = fit_preview(image, (390, 115))
        bg.alpha_composite(shown, ((400 - shown.width) // 2, (124 - shown.height) // 2))
        canvas.paste(bg.convert('RGB'), (x, y + 26))
        draw.text((x + 4, y + 5), label, fill='white', font=font(10))
    path = target / f'combinations_{number:02}.jpg'
    canvas.save(path, quality=94, subsampling=0)
    return path.relative_to(ROOT).as_posix()


def build_source(entry):
    path = APP / 'assets/kill_concepts' / entry['source_file']
    if sha(path) != entry['sha256']:
        raise ValueError('Source SHA mismatch: ' + entry['source_file'])
    target = OUT / f's{entry["index"]:03}'
    target.mkdir(parents=True, exist_ok=True)
    game = Image.open(ROOT / 'qa/lol_background.png').convert('RGBA')
    icons = [Image.open(ROOT / f'qa/reference_icons/{n}.png').convert('RGBA') for n in ('Akali', 'Mordekaiser')]
    manifest = {'source_index': entry['index'], 'source_file': entry['source_file'], 'source_sha256': entry['sha256'],
                'base_commit': BASE, 'rgb_modified': False, 'generated_or_inpainted': False,
                'status': 'unapproved_candidates', 'assets': [], 'quality_notes': entry['quality_notes'],
                'excluded_content': entry['excluded_content'], 'unsupported': entry['unsupported']}
    items = []
    with Image.open(path) as raw:
        source = raw.convert('RGB')
        overlay = source.copy()
        draw = ImageDraw.Draw(overlay)
        for config in entry['components']:
            a = dict(config)
            if config.get('reuse_file'):
                a['file'], a['mask_file'] = config['reuse_file'], config['reuse_mask']
                image = Image.open(ROOT / a['file']).convert('RGBA')
                a['reused_unchanged'] = True
            else:
                image, model = candidate(source, config)
                a['alpha_model'] = model
                sprite = target / (config['id'] + '.png')
                mask = target / (config['id'] + '.alpha.png')
                image.save(sprite)
                image.getchannel('A').save(mask)
                a['file'], a['mask_file'] = sprite.relative_to(ROOT).as_posix(), mask.relative_to(ROOT).as_posix()
            a['sha256'], a['mask_sha256'] = sha(ROOT / a['file']), sha(ROOT / a['mask_file'])
            a['status'] = 'needs_visual_review' if not config.get('quality_flags') else 'needs_mask_or_source_review'
            manifest['assets'].append(a)
            items.append((a, image))
            draw.rectangle(config['crop_box'], outline='cyan', width=2)
            draw.text(tuple(config['crop_box'][:2]), config['id'], fill='cyan', font=font(11))
            for hole in config['portrait_holes']:
                kind, box = next(iter(hole.items()))
                getattr(draw, kind)(box, outline='red', width=2)
        overlay.thumbnail((1448, 1086))
        overlay.save(target / 'source_regions.jpg', quality=94, subsampling=0)
    manifest['review_pages'] = review_pages(items, target, game, icons)
    manifest['combinations'] = combinations(items, target, game, icons)
    manifest['verification'] = verify_source(entry, manifest)
    write_json(target / 'manifest.json', manifest)
    return {'source_index': entry['index'], 'assets': len(items), 'new_assets': sum(not a.get('reused_unchanged') for a in manifest['assets']),
            'combinations': manifest['combinations']['count'], 'checks_passed': True,
            'manifest': (target / 'manifest.json').relative_to(ROOT).as_posix()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=int, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    sources = read_json(OUT / 'source_inventory.json')['sources']
    selected = [s for s in sources if s['batch'] == args.batch]
    if not selected or len(selected) > 8:
        parser.error('Batch must contain one to eight registered sources')
    results = []
    for entry in selected:
        if args.verify_only:
            m = read_json(OUT / f's{entry["index"]:03}/manifest.json')
            result = {'source_index': entry['index'], 'verified_assets': len(verify_source(entry, m))}
        else:
            result = build_source(entry)
        results.append(result)
        print(json.dumps(result), flush=True)
    write_json(OUT / 'batches' / f'batch_{args.batch:02}_verification.json',
               {'batch': args.batch, 'base_commit': BASE, 'all_numeric_checks_passed': True,
                'human_approval': False, 'decoded_sources_at_once': 1, 'sources': results})
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
