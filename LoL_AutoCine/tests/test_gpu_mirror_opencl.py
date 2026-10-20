"""Live GPU mirror uses the device only when its OpenCL buffer is verified."""
from types import SimpleNamespace

import numpy as np
import pytest

from core import gpu_mirror
from core.effects import Template
import legacy_app


def frame():
    bgra = np.zeros((90, 160, 4), np.uint8)
    bgra[:, :, 2] = 180  # RGB red from BGRA input
    bgra[40:50, 70:90, 1] = 255
    bgra[:, :, 3] = 255
    return bgra


def test_unavailable_gpu_falls_back_without_losing_color(monkeypatch):
    monkeypatch.setattr(gpu_mirror, 'probe', lambda: (False, 'test unavailable'))
    source = SimpleNamespace(latest=frame)
    image, _ = legacy_app._render_live_preview((source, 160, 90, None, '', 0., 160, 90))
    assert image.getpixel((5, 5)) == (180, 0, 0)
    assert gpu_mirror.last_status() == ('CPU', 'test unavailable')


def test_unsupported_effect_reports_cpu_reason(monkeypatch):
    monkeypatch.setattr(gpu_mirror, 'probe', lambda: (True, 'test GPU'))
    assert gpu_mirror.render(frame(), 160, 90, Template(grain=.5)) is None
    assert gpu_mirror.last_status() == ('CPU', 'grain uses CPU preview')


def test_real_opencl_device_processes_mirror_pixels(monkeypatch):
    usable, device = gpu_mirror.probe()
    if not usable:
        pytest.skip(device)
    monkeypatch.setattr(legacy_app, 'apply_video_effect_preview',
                        lambda *_args, **_kw: pytest.fail('CPU video preview selected'))
    source = SimpleNamespace(latest=frame)
    raw, _ = legacy_app._render_live_preview((source, 160, 90, None, '', 0., 160, 90))
    assert raw.getpixel((5, 5)) == (180, 0, 0)
    template = Template(bloom=.4, dof_enabled=True, dof_blur=3., vignette=.3)
    with_fx, _ = legacy_app._render_live_preview((source, 160, 90, template,
                                                  '', 0., 160, 90))
    assert with_fx.size == raw.size
    assert np.any(np.asarray(with_fx) != np.asarray(raw))
    assert gpu_mirror.last_status() == ('OpenCL GPU', device)


def test_mirror_fill_canvas_is_optional_and_keeps_output_resolution():
    source = SimpleNamespace(latest=frame)
    # A wide editor panel would otherwise have large side bars around 16:9.
    fit, _ = legacy_app._render_live_preview((source, 160, 90, None, '', 0.,
                                               240, 90, None, False, False))
    fill, _ = legacy_app._render_live_preview((source, 160, 90, None, '', 0.,
                                                240, 90, None, False, True))
    assert fit.size == (160, 90)
    assert fill.size == (240, 90)
    assert fill.getpixel((5, 45)) == (180, 0, 0)
