"""Real FFmpeg frames for the opt-in Work Flash/tmix experiments."""
from __future__ import annotations

from fractions import Fraction
import math
import subprocess

import imageio_ffmpeg
import numpy as np
import pytest

from core.effects import Template, _build_video_effect_filters


def _template(**revisions):
    template = Template()
    for name, value in revisions.items():
        setattr(template, name, value)
    return template


def _filter(template: Template, effect: str, events=()):
    template.video_effects = {effect: 0.5}
    graph = _build_video_effect_filters(template, 1.0, list(events), False)
    return next(item for item in graph if item.startswith("eq=brightness=") or
                (effect == "zoom_blur" and "tmix=" in item))


def _ffmpeg_frames(filter_graph: str, rate: str, color: str, count: int,
                   drop_frame: int | None = None) -> np.ndarray:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if drop_frame is not None:
        filter_graph = f"select='not(eq(n,{drop_frame}))'," + filter_graph
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
               "-i", f"color=c={color}:s=16x16:r={rate}:d=1",
               "-vf", filter_graph, "-fps_mode", "passthrough",
               "-frames:v", str(count), "-pix_fmt", "rgb24",
               "-f", "rawvideo", "pipe:1"]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=30, check=False)
    assert process.returncode == 0, process.stderr.decode("utf-8", "replace")
    return np.frombuffer(process.stdout, dtype=np.uint8).reshape((-1, 16, 16, 3))


@pytest.mark.parametrize("rate", ["30", "60", "60000/1001"])
def test_causal_flash_begins_on_first_pts_at_or_after_event(rate):
    event = 0.5004
    first = math.ceil(Fraction("0.5004") * Fraction(rate))
    legacy = _filter(Template(), "flash", [(event, 0.92)])
    candidate = _filter(_template(flash_revision="causal_pts_v1"),
                        "flash", [(event, 0.92)])
    before = _ffmpeg_frames(legacy, rate, "black", first + 2)
    after = _ffmpeg_frames(candidate, rate, "black", first + 2)
    if rate in ("30", "60"):
        # Baseline reproduces premature light from three-decimal rounding.
        assert before[first - 1].mean() > before[0].mean() + 20
    assert after[first - 1].mean() == after[0].mean()
    assert after[first].mean() > after[0].mean() + 10


def test_future_event_does_not_change_earlier_flash_and_empty_is_safe():
    one = _filter(_template(flash_revision="causal_pts_v1"), "flash", [(0.3, 0.5)])
    two = _filter(_template(flash_revision="causal_pts_v1"), "flash",
                  [(0.3, 0.5), (0.7, 0.9)])
    image_one = _ffmpeg_frames(one, "30", "black", 22)
    image_two = _ffmpeg_frames(two, "30", "black", 22)
    assert np.array_equal(image_one[:21], image_two[:21])
    assert not _build_video_effect_filters(Template(video_effects={"flash": 0.5}),
                                           1.0, [], False)


def test_vfr_missing_frame_uses_remaining_pts_not_output_index():
    candidate = _filter(_template(flash_revision="causal_pts_v1"),
                        "flash", [(0.5004, 0.92)])
    frames = _ffmpeg_frames(candidate, "30", "black", 18, drop_frame=15)
    # Output index 15 is original source frame 16 (PTS 0.5333), after a gap.
    assert frames[14].mean() == frames[0].mean()
    assert frames[15].mean() > frames[0].mean() + 10


def test_exact_single_onset_matches_legacy_strength():
    legacy = _filter(Template(), "flash", [(0.5, 0.92)])
    candidate = _filter(_template(flash_revision="causal_pts_v1"),
                        "flash", [(0.5, 0.92)])
    old = _ffmpeg_frames(legacy, "30", "black", 18)
    new = _ffmpeg_frames(candidate, "30", "black", 18)
    assert np.array_equal(old[15:18], new[15:18])


