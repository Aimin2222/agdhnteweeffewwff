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
from io import BytesIO
import time

import numpy as np
from PIL import Image, ImageDraw

# Older offline extraction tools use sibling imports. Keep the application
# import graph unchanged while allowing this utility to be tested as a module.
TOOLS = str(Path(__file__).resolve().parent)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

try:
    from build_killframe_candidates import components, font
    from extract_killframe_original_alpha_pilot import checker, shape_mask
except ImportError:
    from tools.build_killframe_candidates import components, font
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


def save_image(image, path, **options):
    """Encode fully before writing; use wb (not PIL's w+b) on OneDrive.

    Only new candidate output paths are writable. Bounded retries handle
    transient Windows sync errors, and verification subsequently rereads bytes.
    """
    path = Path(path)
    if OUT.resolve() not in path.resolve().parents:
        raise ValueError('Candidate writer cannot overwrite original or protected assets')
    data = BytesIO()
    image.save(data, format='PNG' if path.suffix.lower() == '.png' else 'JPEG', **options)
    for attempt in range(5):
        try:
            path.write_bytes(data.getvalue())
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(.2 * (attempt + 1))


def candidate(source, config):
    """Fit the matte without using any portrait pixels as background samples.

    The board cover's light/dark appearance is irrelevant: each selected part
    has its own border/support samples. Artwork RGB is never unmatted/edited.
    """
    crop = source.crop(config['crop_box']).convert('RGB')
    rgb = np.asarray(crop)
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[:h, :w]
    design = np.stack([np.ones_like(xx), xx / max(w - 1, 1), yy / max(h - 1, 1)], -1).astype(float)
    holes = shape_mask(crop.size, config['portrait_holes'], config['crop_box'])
    support = shape_mask(crop.size, config['roi_regions'], config['crop_box']) if config['roi_regions'] else np.ones((h, w))
    edge = (xx < max(3, w // 20)) | (xx >= w - max(3, w // 20)) | (yy < max(3, h // 20)) | (yy >= h - max(3, h // 20))
    eligible = ((support < .05) | edge) & (holes < .01)
    if eligible.sum() < 24:
        eligible = holes < .01
    values = rgb.reshape(-1, 3).astype(float)
    matrix = design.reshape(-1, 3)
    sample = eligible.ravel()
    # A robust plane of border/page background, with portraits excluded.
    brightness = float(np.median(values[sample].mean(-1)))
    light = brightness > 155
    luma = values.mean(-1)
    selected = sample & (luma >= np.percentile(luma[sample], 35) if light else luma <= np.percentile(luma[sample], 65))
    for _ in range(5):
        coefficients = np.linalg.lstsq(matrix[selected], values[selected], rcond=None)[0]
        residual = np.linalg.norm(values - matrix @ coefficients, axis=-1)
        selected = sample & (residual <= np.percentile(residual[sample], 50))
    background = (matrix @ coefficients).reshape(h, w, 3)
    distance = np.linalg.norm(rgb.astype(float) - background, axis=-1)
    low, high = config['candidate_thresholds']
    t = np.clip((distance - low) / (high - low), 0, 1)
    alpha = t * t * (3 - 2 * t)
    if light:
        alpha *= np.clip((255 - rgb.min(-1).astype(float) - 18) / 70, 0, 1)
    alpha *= support * (1 - holes)
    for key in ('exclude_regions', 'candidate_exclusions'):
        if config.get(key):
            alpha *= 1 - shape_mask(crop.size, config[key], config['crop_box'])
    removed = 0
    for group in components(alpha > .035):
        if len(group) < config.get('min_component_pixels', 3):
            for y, x in group:
                alpha[y, x] = 0
                removed += 1
    alpha[alpha < 1 / 255] = 0
    result = Image.fromarray(np.dstack([rgb, np.rint(alpha * 255).astype('uint8')]))
    return result, {'model': 'robust_border_or_outside_support_rgb_plane', 'coefficients': coefficients.tolist(),
                    'sampling': 'portrait pixels excluded; each component samples its own board background',
                    'sample_pixels': int(sample.sum()), 'background_median_luma': brightness,
                    'light_matte': light, 'candidate_thresholds': [low, high],
                    'tiny_noise_pixels_removed': removed, 'rgb_modified': False}


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
        save_image(canvas, path, quality=94, subsampling=0)
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
    save_image(canvas, path, quality=94, subsampling=0)
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
                save_image(image, sprite)
                save_image(image.getchannel('A'), mask)
                a['file'], a['mask_file'] = sprite.relative_to(ROOT).as_posix(), mask.relative_to(ROOT).as_posix()
            a['sha256'], a['mask_sha256'] = sha(ROOT / a['file']), sha(ROOT / a['mask_file'])
            alpha = np.asarray(image.getchannel('A'))
            edge = np.concatenate([alpha[0], alpha[-1], alpha[1:-1, 0], alpha[1:-1, -1]])
            a['quality_metrics'] = {'edge_pixels_above_32': int((edge > 32).sum()),
                                    'visible_pixels': int((alpha > 0).sum()),
                                    'opaque_pixels': int((alpha >= 240).sum())}
            if not a.get('reused_unchanged') and (edge > 32).sum() >= 20:
                a['quality_flags'] = list(a['quality_flags']) + ['切り出し端に不透明な画素が接する。装飾の欠け/隣接部品/罫線をsource_regions.jpgで確認。']
            a['status'] = 'needs_visual_review' if not a.get('quality_flags') else 'needs_mask_or_source_review'
            manifest['assets'].append(a)
            items.append((a, image))
            draw.rectangle(config['crop_box'], outline='cyan', width=2)
            draw.text(tuple(config['crop_box'][:2]), config['id'], fill='cyan', font=font(11))
            for hole in config['portrait_holes']:
                kind, box = next(iter(hole.items()))
                getattr(draw, kind)(box, outline='red', width=2)
        overlay.thumbnail((1448, 1086))
        save_image(overlay, target / 'source_regions.jpg', quality=94, subsampling=0)
    manifest['review_pages'] = review_pages(items, target, game, icons)
    manifest['combinations'] = combinations(items, target, game, icons)
    manifest['verification'] = verify_source(entry, manifest)
    write_json(target / 'manifest.json', manifest)
    return {'source_index': entry['index'], 'assets': len(items), 'new_assets': sum(not a.get('reused_unchanged') for a in manifest['assets']),
            'combinations': manifest['combinations']['count'], 'checks_passed': True,
            'manifest': (target / 'manifest.json').relative_to(ROOT).as_posix()}


def make_review_contacts(batch):
    """All components in a batch, black/white contact pages for quick triage."""
    sources = [s for s in read_json(OUT / 'source_inventory.json')['sources'] if s['batch'] == batch]
    tiles, pages = [], []
    for s in sources:
        m = read_json(OUT / f's{s["index"]:03}/manifest.json')
        for start, path in enumerate(m['review_pages']):
            with Image.open(ROOT / path) as review:
                for j, a in enumerate(m['assets'][start * 8:start * 8 + 8]):
                    tile = review.crop((300, 72 + j * 160, 900, 200 + j * 160)).resize((400, 86), Image.Resampling.LANCZOS)
                    tiles.append((f's{s["index"]:03} / {a["theme"]} / {a["id"]}', tile))
                    if len(tiles) == 40:
                        pages.append(save_contact_page(tiles, batch, len(pages) + 1))
                        tiles.clear()
    if tiles:
        pages.append(save_contact_page(tiles, batch, len(pages) + 1))
    return pages


def save_contact_page(tiles, batch, page):
    canvas = Image.new('RGB', (2000, 38 + ((len(tiles) + 4) // 5) * 120), '#252933')
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 9), f'BATCH {batch:02} / EVERY COMPONENT / BLACK + WHITE / UNAPPROVED / SEE FULL REVIEW PAGES', fill='white', font=font(16))
    for j, (label, tile) in enumerate(tiles):
        x, y = j % 5 * 400, 38 + j // 5 * 120
        draw.text((x + 5, y + 6), label, fill='white', font=font(11))
        canvas.paste(tile, (x, y + 29))
    path = OUT / 'batches' / f'batch_{batch:02}_contact_{page:02}.jpg'
    save_image(canvas, path, quality=94, subsampling=0)
    return path.relative_to(ROOT).as_posix()


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
                'human_approval': False, 'decoded_sources_at_once': 1, 'sources': results,
                'black_white_contacts': make_review_contacts(args.batch)})
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
