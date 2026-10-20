"""OpenCL mirror processing via OpenCV UMat, with an explicit CPU fallback.

WGC delivers BGRA in host memory and Tk displays host pixels, so one upload
and one download are unavoidable. Intermediate resize/grade/blur operations
stay in UMat when the selected OpenCL device is a GPU. This is independent of
the FFmpeg/NVENC export backend.
"""
from __future__ import annotations

from functools import lru_cache
import threading

import numpy as np


_status_lock = threading.Lock()
_status = ('not_started', '')


def _set_status(mode, reason=''):
    global _status
    with _status_lock:
        _status = (mode, reason)


def last_status():
    with _status_lock:
        return _status


@lru_cache(maxsize=1)
def probe():
    """Exercise an actual device buffer; a compiled OpenCL flag is insufficient."""
    try:
        import cv2
        if not cv2.ocl.haveOpenCL():
            return False, 'OpenCL runtime unavailable'
        cv2.ocl.setUseOpenCL(True)
        if not cv2.ocl.useOpenCL():
            return False, 'OpenCL runtime disabled'
        device = cv2.ocl.Device_getDefault()
        if not device.available() or not (int(device.type()) & 4):
            return False, 'selected OpenCL device is not a GPU'
        sample = cv2.UMat(np.zeros((16, 16, 3), np.uint8))
        filtered = cv2.GaussianBlur(sample, (0, 0), 1)
        if not filtered.handle(cv2.ACCESS_READ) or filtered.get().shape != (16, 16, 3):
            return False, 'OpenCL device buffer verification failed'
        return True, str(device.name())
    except Exception as exc:
        return False, f'{type(exc).__name__}: {exc}'


UNSUPPORTED_VIDEO_FX = {'glitch', 'vhs_damage', 'chroma_leak'}
SUPPORTED_VIDEO_FX = {
    'mirror', 'motion_camera', 'camera_shake', 'wiggle', 'spin_motion',
    'zoom_blur', 'block_motion', 'kaleidoscope', 'focus_blur', 'vr_blur',
    'sphere_blur', 'glint', 'flash', 'vr_light_leak',
}


def unsupported_reason(template):
    if template is None:
        return ''
    if getattr(template, 'curve_enabled', False):
        return 'curve uses CPU preview'
    if getattr(template, 'lut_path', ''):
        return 'LUT uses CPU preview'
    for key, value in (getattr(template, 'video_effects', {}) or {}).items():
        try:
            active = float(value) > .001
        except (TypeError, ValueError):
            active = False
        if active and key not in SUPPORTED_VIDEO_FX:
            return f'{key} uses CPU preview'
    return ''


def _strength(template, key):
    try:
        return max(0., min(1., float((template.video_effects or {}).get(key, 0.))))
    except (AttributeError, TypeError, ValueError):
        return 0.


def _warp(u, width, height, zoom=1., dx=0., dy=0., angle=0.):
    import cv2
    matrix = cv2.getRotationMatrix2D((width / 2., height / 2.), angle, zoom)
    matrix[0, 2] += dx
    matrix[1, 2] += dy
    return cv2.warpAffine(u, matrix, (width, height), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def _camera(u, template, width, height):
    style = getattr(template, 'style', '')
    if style not in ('cinema', 'follow', 'cinema_top', 'top', 'fps', 'orbit'):
        return u
    intensity = {'natural': .6, 'standard': 1., 'strong': 1.4}.get(template.intensity, 1.)
    base = max(.3, min(1., float(template.dist_scale)))
    zoom = 1. + (1. - base) * (.55 * intensity if style in ('cinema', 'cinema_top') else .18)
    if style in ('cinema_top', 'top'):
        zoom *= .92
    zoom = max(1., min(1.55, zoom))
    shift_y = int(max(-.12, min(.12, (float(template.cam_height) - 170.) / 900.)) * height)
    return _warp(u, width, height, zoom=zoom, dy=shift_y) if zoom > 1.001 or shift_y else u


def _video_fx(u, template, width, height):
    import cv2
    if _strength(template, 'mirror'):
        u = cv2.flip(u, 1)
    motion = _strength(template, 'motion_camera')
    shake = _strength(template, 'camera_shake')
    wiggle = _strength(template, 'wiggle')
    amp = (.01 + .025 * motion if motion else 0.) + (
        .008 + .025 * shake if shake else 0.) + (.004 + .015 * wiggle if wiggle else 0.)
    if amp:
        u = _warp(u, width, height, zoom=1. / (1. - 2 * amp),
                  dy=round(height * amp))
    spin = _strength(template, 'spin_motion')
    if spin:
        u = _warp(u, width, height, angle=1.5 * spin)
    zoom = _strength(template, 'zoom_blur')
    if zoom:
        u = cv2.addWeighted(u, .65, _warp(u, width, height, zoom=1. + .025 * zoom), .35, 0)
    blocks = _strength(template, 'block_motion')
    if blocks:
        factor = max(4, int(8 + 24 * blocks))
        small = cv2.resize(u, (max(1, width // factor), max(1, height // factor)),
                           interpolation=cv2.INTER_AREA)
        u = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
    kaleidoscope = _strength(template, 'kaleidoscope')
    if kaleidoscope:
        u = cv2.addWeighted(u, 1 - .22 * kaleidoscope,
                            cv2.flip(u, 1), .22 * kaleidoscope, 0)
    blur = max(_strength(template, key) for key in ('focus_blur', 'vr_blur', 'sphere_blur'))
    if blur:
        u = cv2.GaussianBlur(u, (0, 0), 1. + 3. * blur)
    glint = _strength(template, 'glint')
    if glint:
        u = cv2.addWeighted(u, .78, cv2.GaussianBlur(u, (0, 0), 4.),
                            .22 * (.5 + glint), 0)
    # phase=.5 in the legacy static mirror preview, so flash is inactive there.
    return u


@lru_cache(maxsize=24)
def _vignette_mask(width, height, angle):
    from .preview import _vignette_r
    r = np.cos(angle * _vignette_r(width, height)) ** 4
    return np.repeat(r.astype(np.float32), 3, axis=2)


@lru_cache(maxsize=24)
def _focus_mask(width, height, cx, cy, radius, feather, shape, near, focus, far):
    if shape == 'band':
        fc = np.clip(focus / max(near + focus + far, 1.), .05, .95)
        span = max(.025, min((focus-near) / max(focus+far, 1.),
                             (far-focus) / max(focus+far, 1.)))
        yy = np.linspace(0., 1., height, dtype=np.float32)[:, None]
        weight = np.repeat(np.clip((np.abs(yy-fc)-span)/max(span, .02), 0, 1), width, axis=1)
    else:
        yy, xx = np.ogrid[:height, :width]
        distance = np.hypot((xx/width-cx)*width/height, yy/height-cy)
        weight = np.clip((distance-radius)/feather, 0, 1)
    return np.repeat(weight.astype(np.float32)[:, :, None], 3, axis=2)


def _pixel_mix(base, other, mask):
    import cv2
    weight = cv2.UMat(mask)
    inverse = cv2.UMat(1. - mask)
    left = cv2.multiply(base, inverse, dtype=cv2.CV_32F)
    right = cv2.multiply(other, weight, dtype=cv2.CV_32F)
    return cv2.convertScaleAbs(cv2.add(left, right))


def _grade(u, template, width, height):
    import cv2
    from .effects import FOG_RGB, grade_values, vignette_angle
    from .focus_fx import focus_settings
    g = grade_values(template.grade, template.grade_strength, template.contrast)
    contrast = float(g['contrast'])
    beta = 255. * (.5 * (1. - contrast) + float(g['brightness']))
    u = cv2.addWeighted(u, contrast, u, 0., beta)
    saturation = float(g['saturation'])
    if abs(saturation - 1.) > .001:
        weights = np.array([.299, .587, .114], np.float32)
        matrix = np.eye(3, dtype=np.float32) * saturation + (1.-saturation) * weights
        u = cv2.transform(u, matrix)
    gamma = float(g['gamma'])
    if abs(gamma - 1.) > .001:
        lut = np.clip((np.arange(256, dtype=np.float32)/255.) ** (1./max(.1, gamma))*255., 0, 255).astype(np.uint8)
        u = cv2.LUT(u, lut)
    temperature = max(-1., min(1., float(template.temperature)))
    shifts = [g['rs']*.125+g['rm']*.25+g['rh']*.125+.04*temperature,
              g['gs']*.125+g['gm']*.25+g['gh']*.125,
              g['bs']*.125+g['bm']*.25+g['bh']*.125-.04*temperature]
    if any(abs(x) > .001 for x in shifts):
        u = cv2.add(u, tuple(round(x*255) for x in shifts)+(0,))
    if template.bloom > 0:
        blurred = cv2.GaussianBlur(u, (0, 0), max(2, width // 60))
        u = cv2.addWeighted(u, 1., blurred, min(.3, .225 * template.bloom), -3.)
    if template.vignette > 0:
        mask = cv2.UMat(_vignette_mask(width, height, vignette_angle(template.vignette)))
        u = cv2.convertScaleAbs(cv2.multiply(u, mask, dtype=cv2.CV_32F))
    if template.fog_enabled and template.fog_strength > .001:
        opacity = max(0., min(.45, float(template.fog_strength) * .35))
        color = FOG_RGB.get(template.fog_preset, FOG_RGB['teal'])
        fog = cv2.UMat(np.full((height, width, 3), color, np.uint8))
        u = cv2.addWeighted(u, 1.-opacity, fog, opacity, 0)
    if template.dof_enabled and template.dof_blur > .01:
        cx, cy, radius, feather = focus_settings(template)
        mask = _focus_mask(width, height, cx, cy, radius, feather, template.dof_shape,
                           float(template.dof_near_distance), float(template.dof_focus_distance),
                           float(template.dof_far_distance))
        blurred = cv2.GaussianBlur(u, (0, 0), float(template.dof_blur)*.75)
        u = _pixel_mix(u, blurred, mask)
    grain = max(0., min(1., float(getattr(template, 'grain', 0.) or 0.)))
    if grain:
        # The CPU preview's grain used a full-frame float conversion, which
        # made a common preset take over 130 ms. Upload one grayscale noise
        # plane and blend on the GPU; export keeps its existing FFmpeg filter.
        noise = np.random.default_rng().integers(0, 256, (height, width), dtype=np.uint8)
        noise_gpu = cv2.cvtColor(cv2.UMat(noise), cv2.COLOR_GRAY2RGB)
        amplitude = (3.06 + 12.75 * grain) / 73.9
        u = cv2.addWeighted(u, 1., noise_gpu, amplitude, -127.5 * amplitude)
    if template.bars > 0:
        bar = int(height * .12 * min(1., float(template.bars)))
        if bar:
            cv2.rectangle(u, (0, 0), (width, bar-1), (0, 0, 0), -1)
            cv2.rectangle(u, (0, height-bar), (width, height), (0, 0, 0), -1)
    return u


def render(frame_bgra, width, height, template=None, title='', split=0.):
    """Return RGB pixels and pre-grade pixels, or None for a logged CPU fallback."""
    usable, device = probe()
    if not usable:
        _set_status('CPU', device)
        return None
    reason = unsupported_reason(template)
    if reason:
        _set_status('CPU', reason)
        return None
    try:
        import cv2
        from PIL import Image
        from .preview import _title_overlay
        # OpenCV's OpenCL switch may be thread-local. Rendering runs in the
        # bounded mirror worker even when the capability probe ran in the UI.
        cv2.ocl.setUseOpenCL(True)
        if not cv2.ocl.useOpenCL():
            _set_status('CPU', 'OpenCL disabled in mirror worker')
            return None
        in_height, in_width = frame_bgra.shape[:2]
        ratio = min(1., width/in_width, height/in_height)
        out_width, out_height = max(1, round(in_width*ratio)), max(1, round(in_height*ratio))
        u = cv2.UMat(frame_bgra)
        u = cv2.cvtColor(u, cv2.COLOR_BGRA2RGB)
        if (out_width, out_height) != (in_width, in_height):
            u = cv2.resize(u, (out_width, out_height), interpolation=cv2.INTER_LINEAR)
        if template is not None:
            u = _camera(u, template, out_width, out_height)
            u = _video_fx(u, template, out_width, out_height)
        original = u.get()
        if template is None:
            _set_status('OpenCL GPU', device)
            return original, original
        u = _grade(u, template, out_width, out_height)
        rgb = u.get()
        if title:
            image = Image.fromarray(rgb).convert('RGBA')
            image.alpha_composite(_title_overlay(title, out_width, out_height),
                                  (0, int(out_height*.14)))
            rgb = np.asarray(image.convert('RGB'))
        if split > 0:
            x = int(out_width * min(1., split))
            rgb[:, :x] = original[:, :x]
            if 0 < x < out_width:
                rgb[:, max(0, x-1):x+1] = 255
        _set_status('OpenCL GPU', device)
        return rgb, original
    except Exception as exc:
        _set_status('CPU', f'OpenCL preview error: {type(exc).__name__}: {exc}')
        return None
