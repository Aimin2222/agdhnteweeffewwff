# -*- coding: utf-8 -*-
"""Review-ready RED and BLUE camera reels from previously captured clips."""
from pathlib import Path


def assemble_side_reels(root, camera_entries, *, log=lambda _m: None, concatenate=None):
    """Join each side's QA clips; failures never delete original footage."""
    if concatenate is None:
        from .effects import concat_clips
        concatenate = concat_clips
    root = Path(root)
    result = {}
    for side in ("RED", "BLUE"):
        paths = [Path(path) for entry in camera_entries if entry.get("side") == side
                 for path in entry.get("outputs", [])]
        paths = [path for path in paths if path.is_file() and path.stat().st_size > 0]
        if len(paths) < 2:
            result[side] = {"outputs": [], "error": "Not enough clips"}
            continue
        destination = root / side / f"{side}_camera_review_all.mp4"
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            concatenate(paths, destination)
            if not destination.is_file() or destination.stat().st_size == 0:
                raise RuntimeError("No review video was written")
            result[side] = {"outputs": [str(destination)], "clips": len(paths)}
            log(f"{side}サイドの比較動画を作成: {destination.name} ({len(paths)}クリップ)")
        except Exception as exc:
            result[side] = {"outputs": [], "error": f"{type(exc).__name__}: {exc}"}
            log(f"{side}の比較動画を作れませんでした（個別MP4は保持）: {exc}")
    return result
