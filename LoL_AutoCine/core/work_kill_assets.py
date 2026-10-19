"""Audited Work materials. Source PNGs stay immutable; only temporary pairs render.

Review opt-in is explicit and never promotes an asset's quality status.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'assets/work_kill_assets/catalog.json'


def file_signature(path):
    path = Path(path)
    stat = path.stat()
    return str(path.resolve()), stat.st_size, stat.st_mtime_ns


@lru_cache(maxsize=4)
def _read_catalog(signature):
    return json.loads(Path(signature[0]).read_text(encoding='utf-8'))


def catalog():
    return _read_catalog(file_signature(CATALOG))


@lru_cache(maxsize=128)
def _verified(signature, expected):
    return hashlib.sha256(Path(signature[0]).read_bytes()).hexdigest() == expected


@lru_cache(maxsize=4)
def _rgba_cached(signature):
    from PIL import Image
    with Image.open(signature[0]) as image: return image.convert('RGBA')


def list_assets(kind='frames', review=False):
    return [dict(x) for x in catalog().get(kind, [])
            if review or x.get('status') == 'approved']


def resolve_asset(identifier, kind='frames', review=False):
    item = next((x for x in list_assets(kind, review) if x['id'] == identifier), None)
    if item is None:
        raise ValueError('Work material missing or not approved: ' + str(identifier))
    path = (ROOT / item['path']).resolve()
    if not path.is_relative_to((ROOT / 'assets/work_kill_assets').resolve()):
        raise ValueError('Work material outside immutable asset directory')
    if not _verified(file_signature(path), item['sha256']):
        raise ValueError('Work material SHA256 mismatch: ' + identifier)
    return item, path


def strength(value):
    return .45 if value == 'weak' else 1.


def peak_opacity(elapsed, end=.8):
    if elapsed < 0 or elapsed >= end:
        return 0.
    knots = ((0., 0.), (.04, .8), (.08, 1.), (.20, .65), (end, 0.))
    for (a, av), (b, bv) in zip(knots, knots[1:]):
        if elapsed <= b:
            return av + (bv-av) * (elapsed-a)/(b-a)
    return 0.


def peak_expression(start, end=.8, backend='ffmpeg'):
    x = f'(t-{start:.6f})'
    body = f'if(lt({x},0),0,if(lt({x},.04),20*{x},if(lt({x},.08),.8+5*({x}-.04),if(lt({x},.20),1-2.9166666667*({x}-.08),max(0,.65*(1-({x}-.20)/{end-.20:.6f}))))))'
    if backend == 'opencl':
        x = f'(time-{start:.6f}f)'
        return f'({x}<0?0:({x}<.04f?20*{x}:({x}<.08f?.8f+5*({x}-.04f):({x}<.20f?1-2.9166667f*({x}-.08f):fmax(0.0f,.65f*(1-({x}-.20f)/{end-.20:.6f}f))))))'
    return body


def render_pair(frame_id, icon_a, icon_b, *, review=False, include_ornament=True):
    # Eight native 2520x1050 RGBA pairs cost about 80 MB; bounded and immutable.
    _, source = resolve_asset(frame_id, review=review)
    return _pair_cached(frame_id, file_signature(icon_a), file_signature(icon_b),
                        file_signature(CATALOG), file_signature(source), review, include_ornament).copy()


@lru_cache(maxsize=8)
def _pair_cached(frame_id, icon_a, icon_b, catalog_signature, source_signature, review, include_ornament):
    """Verified circular portraits; optional ornament for the no-peak path."""
    from PIL import Image, ImageOps, ImageDraw, ImageChops
    item, path = resolve_asset(frame_id, review=review)
    if not item.get('portrait_boxes'):
        raise ValueError('Portrait layout not verified for Work material: ' + frame_id)
    with Image.open(path) as image:
        frame = image.convert('RGBA')
    base = Image.new('RGBA', frame.size)
    for portrait, box in zip((icon_a[0], icon_b[0]), item['portrait_boxes']):
        x, y, w, h = map(int, box)
        with Image.open(portrait) as image:
            fitted = ImageOps.fit(image.convert('RGBA'), (w, h), method=Image.Resampling.LANCZOS)
        mask = Image.new('L', (w, h))
        ImageDraw.Draw(mask).ellipse((0, 0, w-1, h-1), fill=255)
        fitted.putalpha(ImageChops.multiply(fitted.getchannel('A'), mask))
        base.alpha_composite(fitted, (x, y))
    if include_ornament: base.alpha_composite(frame)
    return base


def render_peak(frame, effect, path):
    return _peak_cached(json.dumps(frame, sort_keys=True), json.dumps(effect, sort_keys=True),
                        file_signature(path)).copy()


@lru_cache(maxsize=4)
def _peak_cached(frame_json, effect_json, signature):
    """Bake the declared placement into frame space; preserve portrait cut-outs."""
    from PIL import Image, ImageDraw
    frame, effect = json.loads(frame_json), json.loads(effect_json)
    placement = effect.get('placement', {})
    width, height = frame['width'], frame['height']
    with Image.open(signature[0]) as source: image = source.convert('RGBA')
    factor = min(width*float(placement.get('width_relative_to_frame', .35))/image.width,
                 height*float(placement.get('max_height_relative_to_frame', 1.4))/image.height)
    image = image.resize((max(1, round(image.width*factor)), max(1, round(image.height*factor))), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (width, height))
    anchor = placement.get('anchor', [.5, .5])
    canvas.alpha_composite(image, (round(width*anchor[0]-image.width/2), round(height*anchor[1]-image.height/2)))
    alpha = canvas.getchannel('A')
    draw = ImageDraw.Draw(alpha)
    for x,y,w,h in frame['portrait_boxes']:
        draw.ellipse((round(x),round(y),round(x+w),round(y+h)),fill=0)
    canvas.putalpha(alpha)
    return canvas


class WorkEntries(list):
    """Legacy list-of-path/time input contract plus Work layer metadata."""
    def __init__(self):
        super().__init__()
        self.layers = []
        self.strength = 1.


def make_event_work_badges(output, template, kills, events, roster, *, icon_lookup=None, log=None):
    from .kill_icons import _player_for_name, champion_icon
    entries = WorkEntries()
    entries.strength = strength(getattr(template, 'work_kill_strength', 'strong'))
    if len(kills) != len(events):
        if log: log('Work: event count mismatch; omitted')
        return entries
    frame_id = getattr(template, 'work_kill_frame_id', '')
    effect_id = getattr(template, 'work_kill_effect_id', '')
    review = bool(getattr(template, 'work_kill_review', False))
    # Validate before any downloads or temporary rendering.
    frame, _ = resolve_asset(frame_id, review=review)
    effect = resolve_asset(effect_id, 'effects', review) if effect_id else None
    lookup = icon_lookup or champion_icon
    cache = {}
    for index, (kill, event) in enumerate(zip(kills, events)):
        at = float(event[0])
        if not math.isfinite(at): continue
        players = [_player_for_name(getattr(kill, key, None), roster) for key in ('killer', 'victim')]
        if not all(players):
            if log: log('Work: real champion pair unavailable; omitted')
            continue
        icons = []
        for player in players:
            key = str(player)
            if key not in cache: cache[key] = lookup(player)
            icons.append(cache[key])
        if not all(icons):
            if log: log('Work: real champion icons unavailable; omitted')
            continue
        path = Path(output).with_name(Path(output).stem + f'.work_pair_{index:03d}.png')
        render_pair(frame_id, *icons, review=review, include_ornament=not bool(effect)).save(path)
        row_id = len(entries.layers)
        layers = []
        if effect:
            item, peak = effect
            # Source handoff order: original ornament, masked peak, portraits.
            _, ornament_path = resolve_asset(frame_id, review=review)
            from shutil import copyfile
            ornament_tmp = path.with_name(path.stem + '.ornament.png')
            copyfile(ornament_path, ornament_tmp)
            entries.append((ornament_tmp, at))
            layers.append(dict(index=len(entries)-1, kind='frame', width=frame['width'], height=frame['height']))
            peak_tmp = path.with_name(path.stem + '.peak.png')
            render_peak(frame, item, peak).save(peak_tmp)
            entries.append((peak_tmp, at))
            layers.append(dict(index=len(entries)-1, kind='peak', width=frame['width'],
                               height=frame['height'], duration=float(item.get('duration', .8))))
        entries.append((path, at))
        layers.append(dict(index=len(entries)-1, kind='frame', width=frame['width'], height=frame['height']))
        entries.layers.append(dict(time=at, layers=layers, event=row_id))
    return entries


def layer_plan(entries, duration, seconds):
    """At-kill start, deterministic max-three feed with no pre-kill flash."""
    from .kill_icons import badge_plan
    placeholders = [(None, x['time']+.1) for x in entries.layers]
    plan = badge_plan(placeholders, duration+.1, seconds-.1)
    result = []
    for item in plan:
        item['end'] = min(duration, item['end'])
        for layer in entries.layers[item['index']]['layers']:
            x = dict(item, **layer)
            x['time'] = entries.layers[item['index']]['time']
            if x['kind'] == 'peak': x['end'] = min(x['end'], x['time']+x['duration'])
            if x['end'] > x['start']: result.append(x)
    return result


def with_work_badges(graph, badge_input, entries, *, duration, position='right-top', scale=1.,
                     seconds=1.55, opacity=1., motion='instant', stack_gap=4, **unused):
    from .kill_icons import badge_motion_xy, normalize_options, normalize_stack_gap
    position, scale, seconds, opacity = normalize_options(position, scale, seconds, opacity)
    plan = layer_plan(entries, duration, seconds)
    if not plan: return graph
    parts = [graph[:-6]+'[work_src_0]']
    for n, layer in enumerate(plan):
        display_width = int(384*scale/2)*2
        x = 'W-w-32' if position.startswith('right') else '32'
        row = int(round(160*scale + normalize_stack_gap(stack_gap)))*layer['row']
        y = f'62+{row}' if position.endswith('top') else f'H-h-62-{row}'
        x, y = badge_motion_xy(position, motion, layer['start'], x, y)
        display_height = int(layer['height']*display_width/layer['width']/2)*2
        filters = f"format=rgba,scale=w={display_width}:h={display_height},colorchannelmixer=aa={opacity:.6f}"
        if layer['kind'] == 'peak':
            # geq retains the original alpha, including portrait cut-outs.
            alpha = peak_expression(layer['time'], layer['duration']).replace('t-', 'T-')
            alpha = alpha.replace('(t-', '(T-')
            filters += f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*({alpha})*{entries.strength:.6f}'"
        parts.append(f'[{badge_input+layer["index"]}:v]{filters}[work_img_{n}]')
        out = 'vout' if n == len(plan)-1 else f'work_src_{n+1}'
        parts.append(f"[work_src_{n}][work_img_{n}]overlay=x='{x}':y='{y}':format=auto:shortest=0:eof_action=repeat:enable='gte(t,{layer['start']:.6f})*lt(t,{layer['end']:.6f})'[{out}]")
    return ';'.join(parts)


def render_preview_pair(template, icon_a, icon_b, elapsed, *, size=(1920, 1080), row=0):
    """RGBA full-frame mirror overlay, using the same clock/layers as export.

    ``elapsed`` is mirror replay time minus kill time, never a wall-clock timer.
    Icons are resolved real champion PNG paths. No text or fabricated portrait.
    """
    from PIL import Image
    # Render at the mirror's actual size. Building a 1080p canvas and scaling
    # it back down for every frame was the dominant Work-preview CPU cost.
    return _render_preview_native(template, icon_a, icon_b, elapsed, row=row, size=size)


def _preview_layers(template, icon_a, icon_b, size, scale):
    frame_id = template.work_kill_frame_id
    effect_id = getattr(template, 'work_kill_effect_id', '')
    review = bool(getattr(template, 'work_kill_review', False))
    _, frame_path = resolve_asset(frame_id, review=review)
    effect_path = resolve_asset(effect_id, 'effects', review)[1] if effect_id else None
    return _preview_layers_cached(frame_id, file_signature(icon_a), file_signature(icon_b),
                                  effect_id, review, size, scale, file_signature(CATALOG),
                                  file_signature(frame_path),
                                  file_signature(effect_path) if effect_path else None)


@lru_cache(maxsize=16)
def _preview_layers_cached(frame_id, icon_a, icon_b, effect_id, review, size, scale,
                           catalog_signature, frame_signature, effect_signature):
    from PIL import Image
    frame, _ = resolve_asset(frame_id, review=review)
    width = int(384*scale/2)*2
    layers = []
    if effect_id:
        effect, path = resolve_asset(effect_id, 'effects', review)
        layers.append((_rgba_cached(frame_signature), 1., 0.))
        layers.append((render_peak(frame, effect, path), 0., float(effect.get('duration', .8))))
    layers.append((render_pair(frame_id, icon_a[0], icon_b[0], review=review,
                               include_ornament=not bool(effect_id)), 1., 0.))
    result = []
    for image, fixed_alpha, duration in layers:
        height = int(image.height*width/image.width/2)*2
        scaled = image.resize((max(1, round(width*size[0]/1920)),
                               max(1, round(height*size[1]/1080))), Image.Resampling.LANCZOS)
        result.append((scaled, fixed_alpha, duration, width, height))
    return tuple(result)


def _render_preview_native(template, icon_a, icon_b, elapsed, *, row=0, size=(1920, 1080)):
    from PIL import Image
    from .kill_icons import normalize_options, normalize_motion, normalize_stack_gap
    scale_x, scale_y = size[0] / 1920., size[1] / 1080.
    canvas = Image.new('RGBA', size)
    position, scale, seconds, opacity = normalize_options(template.kill_icon_position,
            template.kill_icon_scale, template.kill_icon_duration, template.kill_icon_opacity)
    if elapsed < 0 or elapsed >= seconds: return canvas
    layers = _preview_layers(template, icon_a, icon_b, size, scale)
    motion = normalize_motion(template.kill_icon_motion)
    for image, fixed_alpha, duration, w, h in layers:
        alpha = (fixed_alpha if not duration else
                 peak_opacity(elapsed, duration)*strength(template.work_kill_strength))
        x = 1920-w-32 if position.startswith('right') else 32
        offset = round(160*scale + normalize_stack_gap(template.kill_stack_gap))*row
        y = 62+offset if position.endswith('top') else 1080-h-62-offset
        u = max(0., min(1., 1-elapsed/.260))
        ease = u*u*(3-2*u)
        if motion == 'slide_left': x -= (1920+20)*ease
        elif motion == 'slide_right': x += (1920+20)*ease
        elif motion == 'slide_up': y += (1080+20)*ease
        elif motion == 'slide_down': y -= (1080+20)*ease
        elif motion == 'pop': x += 16*math.exp(-18*elapsed)*math.cos(28*elapsed)
        layer = image.copy()
        layer.putalpha(layer.getchannel('A').point(lambda v: round(v*alpha*opacity)))
        canvas.alpha_composite(layer, (round(x*scale_x), round(y*scale_y)))
    return canvas
