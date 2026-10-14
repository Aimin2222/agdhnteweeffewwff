"""Reproducible alpha-only candidates and review sheets; no application hooks.

Uses the original crop RGB verbatim, including RGB behind alpha=0. Cached Riot
portraits appear only in labeled demonstration previews, never in sprites.
"""
from collections import deque
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from extract_killframe_original_alpha_pilot import extract, shape_mask, checker

APP = Path(__file__).resolve().parents[1]
ROOT = APP / 'assets/kill_frames'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(binary):
    """8-connected pixels, preserving narrow connected decoration branches."""
    seen = np.zeros(binary.shape, bool)
    height, width = binary.shape
    for y, x in zip(*np.nonzero(binary)):
        if seen[y, x]:
            continue
        queue = deque([(y, x)])
        seen[y, x] = True
        group = []
        while queue:
            row, col = queue.popleft()
            group.append((row, col))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = row + dy, col + dx
                    if (0 <= yy < height and 0 <= xx < width and
                            binary[yy, xx] and not seen[yy, xx]):
                        seen[yy, xx] = True
                        queue.append((yy, xx))
        yield group


def candidate(source, config):
    old, model = extract(source, config)
    rgb = np.asarray(old)[:, :, :3]
    height, width = rgb.shape[:2]
    yy, xx = np.mgrid[:height, :width]
    design = np.stack([np.ones_like(xx), xx / max(width-1, 1),
                       yy / max(height-1, 1)], -1)
    background = design @ np.asarray(model['coefficients'])
    distance = np.linalg.norm(rgb.astype(float) - background, axis=-1)
    low, high = config['candidate_thresholds']
    strength = np.clip((distance-low)/(high-low), 0, 1)
    alpha = strength * strength * (3-2*strength)
    if config['background_kind'] == 'light':
        # Reduce almost-neutral paper fringes. Original RGB is never unmatted.
        matte = np.clip((255-rgb.min(-1).astype(float)-18)/70, 0, 1)
        alpha *= matte
    if config['roi_regions']:
        alpha *= shape_mask(old.size, config['roi_regions'], config['crop_box'])
    for key in ('portrait_holes', 'exclude_regions', 'candidate_exclusions'):
        if config.get(key):
            alpha *= 1-shape_mask(old.size, config[key], config['crop_box'])
    # Remove only disconnected single/two-pixel noise. Retain connected leaves,
    # sparks and branches; no global erosion/blur that shrinks the artwork.
    removed = 0
    for group in components(alpha > .035):
        if len(group) < config.get('min_component_pixels', 3):
            for y, x in group:
                alpha[y, x] = 0
                removed += 1
    alpha[alpha < 1/255] = 0
    pixels = np.dstack([rgb, np.rint(alpha*255).astype(np.uint8)])
    return Image.fromarray(pixels), dict(model, candidate_thresholds=[low, high],
                                        paper_fringe_suppression=config['background_kind']=='light',
                                        tiny_noise_pixels_removed=removed)


def font(size=15):
    return ImageFont.truetype(str(APP/'tools'/'review_font.ttf'), size) if (APP/'tools/review_font.ttf').exists() else ImageFont.load_default(size=size)


def backgrounds(size, game):
    return [checker(size), Image.new('RGBA', size, 'black'),
            Image.new('RGBA', size, 'white'), game.resize(size, Image.Resampling.LANCZOS)]


def demo(image, config, icons):
    """Place true champion icons BEHIND transparent portrait holes."""
    result = Image.new('RGBA', image.size)
    for shape, icon in zip(config['portrait_holes'], icons):
        kind, box = next(iter(shape.items()))
        local = [round(v-config['crop_box'][i%2]) for i, v in enumerate(box)]
        width, height = local[2]-local[0]+1, local[3]-local[1]+1
        portrait = icon.resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        if kind == 'ellipse':
            draw.ellipse((0, 0, width-1, height-1), fill=255)
        else:
            draw.rectangle((0, 0, width-1, height-1), fill=255)
        portrait.putalpha(mask)
        result.alpha_composite(portrait, tuple(local[:2]))
    result.alpha_composite(image)
    return result


def review_sheet(items, game, label):
    cell_w, cell_h = 600, 230
    canvas = Image.new('RGB', (cell_w*4, 55+len(items)*cell_h), '#252933')
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 12), label, font=font(18), fill='white')
    for row, (name, image) in enumerate(items):
        for col, (kind, bg) in enumerate(zip(['checker / transparent', 'black', 'white', 'LoL'], backgrounds((cell_w, cell_h-30), game))):
            bg.alpha_composite(image, ((cell_w-image.width)//2, (cell_h-30-image.height)//2))
            canvas.paste(bg.convert('RGB'), (col*cell_w, 55+row*cell_h+30))
            draw.text((col*cell_w+8, 55+row*cell_h+7), f'{name} | {kind}', font=font(), fill='white')
    return canvas


def build(app=APP):
    root = app/'assets/kill_frames'
    spec = json.loads((root/'candidate_extraction_spec.json').read_text(encoding='utf-8'))
    previous = json.loads((root/'qa/pilot_manifest.json').read_text(encoding='utf-8'))
    previous = {(a['theme'], Path(a['file']).stem): a for a in previous['assets']}
    game = Image.open(root/'qa/lol_background.png').convert('RGBA')
    icons = [Image.open(root/f'qa/reference_icons/{n}.png').convert('RGBA') for n in ('Akali', 'Mordekaiser')]
    overview = Image.new('RGB', (1800, 1450), '#252933')
    overview_draw = ImageDraw.Draw(overview)
    overview_draw.text((14, 14), '3 THEMES | 18 COMBINATIONS | AKALI x MORDEKAISER | CANDIDATE / NOT APPROVED', font=font(18), fill='white')
    manifest = {'schema_version': 2, 'status': 'candidate_pending_visual_approval',
                'source_base_commit': spec['base_commit'], 'generated_or_inpainted': False,
                'rgb_policy': 'exact original crop RGB, alpha-only edits',
                'assets': [], 'game_background': 'qa/lol_background.png',
                'portrait_preview': {'killer': 'Akali', 'victim': 'Mordekaiser',
                                     'sample_only': True, 'official_cache_version': spec['icon_version']},
                'limitations': ['No RGB unmatting, hidden-art reconstruction or visual approval by numeric tests.']}
    for theme_index, (theme, data) in enumerate(spec['themes'].items()):
        sourcepath = app/'assets/kill_concepts'/data['source_file']
        source = Image.open(sourcepath).convert('RGB')
        items, before_after, portraits = [], [], []
        frames, centers = {}, {}
        for name, config in data['assets'].items():
            image, model = candidate(source, config)
            target = root/'themes'/theme
            target.mkdir(parents=True, exist_ok=True)
            path, mask = target/(name+'.png'), target/(name+'.alpha.png')
            image.save(path)
            image.getchannel('A').save(mask)
            pilot = Image.open(root/'qa/pilot_masks'/theme/(name+'.alpha.png'))
            old = source.crop(config['crop_box']).convert('RGBA')
            old.putalpha(pilot)
            before_after += [(name+' BEFORE', old), (name+' CANDIDATE', image)]
            items.append((name, image))
            a = np.asarray(image.getchannel('A'))
            entry = dict(previous[(theme, name)])
            entry.update(source_sha256=sha(sourcepath), sha256=sha(path), mask_sha256=sha(mask),
                         roi_regions=config['roi_regions'], portrait_holes=config['portrait_holes'],
                         alpha_model=model, candidate_exclusions=config.get('candidate_exclusions', []),
                         status='candidate_pending_visual_approval',
                         visual_review_notes=['Alpha-only candidate, human approval required; immutable flattened RGB may retain matte color.'],
                         alpha_counts={'zero': int((a==0).sum()), 'partial': int(((a>0)&(a<255)).sum()), 'opaque': int((a==255).sum())})
            manifest['assets'].append(entry)
            if name.startswith('frame_'):
                frames[name] = demo(image, config, icons)
            else:
                centers[name] = image
        # Review all 2 x 3 combinations; center marks are separate measured
        # artwork placed over the frame center ONLY for the demo, no resampling.
        for frame_index, (frame_name, frame) in enumerate(frames.items()):
            portraits.append((frame_name+' | Akali x Mordekaiser', frame))
            for center_index, (center_name, center) in enumerate(centers.items()):
                pair = Image.new('RGBA', (600, 200))
                pair.alpha_composite(frame, ((600-frame.width)//2, (200-frame.height)//2))
                pair.alpha_composite(center, ((600-center.width)//2, (200-center.height)//2))
                portraits.append((frame_name+'/'+center_name, pair))
                backdrop = game.resize((600, 200), Image.Resampling.LANCZOS)
                backdrop.alpha_composite(pair)
                y = 50 + (theme_index*2+frame_index)*230
                overview.paste(backdrop.convert('RGB'), (center_index*600, y+25))
                overview_draw.text((center_index*600+8, y+4), f'{theme} | {frame_name} / {center_name}', font=font(), fill='white')
        review_sheet(items, game, f'{theme} | ALPHA CANDIDATE - NOT APPROVED').save(root/f'qa/{theme}_comparison.png')
        review_sheet(before_after, game, f'{theme} | BEFORE / CANDIDATE').save(root/f'qa/{theme}_before_after.png')
        review_sheet(portraits, game, f'{theme} | DEMO: AKALI x MORDEKAISER - NOT MATCH EVENTS').save(root/f'qa/{theme}_portraits.png')
    (root/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    overview.save(root/'qa/three_theme_overview.png')
    return manifest


if __name__ == '__main__':
    print(json.dumps({'assets': len(build()['assets']), 'rgb_modified': False}))
