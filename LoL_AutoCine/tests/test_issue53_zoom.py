"""Real FFmpeg pixel samples for the opt-in Zoom tmix normalization."""
import subprocess

import imageio_ffmpeg
import numpy as np
import pytest

from core.effects import Template, _build_video_effect_filters


def _frames(graph: str, level: int) -> np.ndarray:
    color = f"0x{level:02x}{level:02x}{level:02x}"
    process = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={color}:s=16x16:r=30:d=1",
         "-vf", graph, "-frames:v", "4", "-pix_fmt", "rgb24",
         "-f", "rawvideo", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
    )
    assert process.returncode == 0, process.stderr.decode("utf-8", "replace")
    return np.frombuffer(process.stdout, dtype=np.uint8).reshape((-1, 16, 16, 3))


@pytest.mark.parametrize("level", [32, 96, 180])
def test_normalized_tmix_keeps_flat_brightness(level):
    legacy = Template(video_effects={"zoom_blur": 0.5})
    candidate = Template(video_effects={"zoom_blur": 0.5})
    candidate.zoom_blur_revision = "normalized_tmix_v1"
    old_graph = _build_video_effect_filters(legacy, 1.0, [], False)[0]
    new_graph = _build_video_effect_filters(candidate, 1.0, [], False)[0]
    assert "weights='1 2 1':scale=4" in old_graph
    assert "weights='1 2 1':scale=0.25" in new_graph
    old = _frames("tmix=frames=3:weights='1 2 1':scale=4", level)
    new = _frames("tmix=frames=3:weights='1 2 1':scale=0.25", level)
    assert abs(float(old[3].mean()) - level) > 20
    assert abs(float(new[3].mean()) - level) <= 3
