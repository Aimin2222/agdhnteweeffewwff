"""Pure clip-boundary camera choices. QA approval is explicit and side-specific.

No replay/world position or visual quality is inferred from event metadata.
An empty approval ledger is deliberately the default until Windows QA.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math

CONTROL_MODES = {"manual": "従来の手動カメラ", "fixed_auto": "固定視点＋自動構図補正", "full_auto": "フルオートシネマ"}
SUPPORTED_STYLES = ("third_cinema", "third", "geo_aim", "cinema", "fps", "orbit", "lolnam_cinema", "follow", "cinema_top", "top")

@dataclass(frozen=True)
class CameraDecision:
    mode: str | None
    team: str
    original_style: str
    style: str
    kill_times: tuple[float, ...]
    reasons: tuple[str, ...]
    fallback: bool = False

    def to_dict(self):
        return asdict(self)


def decide_camera(mode, team, selected_style, kill_times=(), *, approved=None, excluded=()):
    """Choose once before attachment; never switch types inside a running clip.

    `approved` is an explicit {BLUE: [style], RED: [style]} Windows QA ledger,
    not the historical camera-number opinions. Missing sides are unverified.
    """
    side = "RED" if str(team).upper() in ("RED", "CHAOS") else "BLUE"
    times = []
    for value in kill_times:
        try:
            value = float(value)
            if math.isfinite(value):
                times.append(value)
        except (TypeError, ValueError, OverflowError):
            continue
    times = tuple(sorted(times))
    if mode is None:
        return CameraDecision(None, side, selected_style, selected_style, times, ("legacy_settings_preserved",))
    if not isinstance(mode, str) or mode not in CONTROL_MODES:
        # A future/invalid serialized mode must not silently enable automation.
        return CameraDecision("manual", side, selected_style, selected_style, times, ("unknown_mode_manual_fallback",), True)
    if mode != "full_auto":
        return CameraDecision(mode, side, selected_style, selected_style, times,
                              ("manual_auto_disabled" if mode == "manual" else "selected_style_preserved",))
    allowed = approved.get(side, ()) if isinstance(approved, dict) else ()
    if not isinstance(allowed, (tuple, list)):
        allowed = ()
    excluded = {s for s in excluded if isinstance(s, str)} if isinstance(excluded, (list, tuple, set)) else set()
    excluded = {s.split(":", 1)[1] if s.startswith(side + ":") else s for s in excluded
                if isinstance(s, str) and (":" not in s or s.startswith(side + ":"))}
    candidates = set(s for s in allowed if isinstance(s, str) and s in SUPPORTED_STYLES and s not in excluded)
    # No enemy 3D coordinates are assumed. Multiplicity is metadata only.
    multi = len(times) >= 2
    priority = (("cinema_top", "top", "third", "third_cinema", "follow", "cinema", "geo_aim", "lolnam_cinema", "fps", "orbit")
                if multi else ("third_cinema", "third", "lolnam_cinema", "cinema_top", "follow", "cinema", "top", "geo_aim", "fps", "orbit"))
    chosen = next((s for s in priority if s in candidates), None)
    if chosen is None:
        # Explicitly excluded views must also be excluded from a fallback.
        fallback = selected_style if selected_style in SUPPORTED_STYLES and selected_style not in excluded else "top"
        return CameraDecision(mode, side, selected_style, fallback, times,
                              ("no_verified_candidate_for_side", "fixed_target_lock_fallback", "visual_qa_unverified"), True)
    return CameraDecision(mode, side, selected_style, chosen, times,
                          ("clip_boundary_only", "multi_kill_wide_priority" if multi else "single_kill_cinema_priority", "explicit_side_qa_approval"))
