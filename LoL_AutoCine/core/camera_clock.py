# -*- coding: utf-8 -*-
"""Continuous replay time estimator for camera animation.

Playback observations arrive over HTTPS and must not be added as discrete
position steps at 4 Hz. Gradually compensate clock drift by changing the
estimated progression speed; only a genuine external seek jumps the clock.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass
class SmoothReplayClock:
    time: float
    drift: float = 0.0
    max_rate_correction: float = 0.08
    seek_threshold: float = 1.50

    def observe(self, actual_time: float) -> bool:
        """Accept a replay timestamp. Return True if an external seek was found."""
        try:
            actual = float(actual_time)
        except (TypeError, ValueError):
            return False
        if not math.isfinite(actual):
            return False
        error = actual - self.time
        if abs(error) > self.seek_threshold:
            self.time = actual
            self.drift = 0.0
            return True
        self.drift = error
        return False

    def advance(self, elapsed: float, requested_speed: float = 1.0) -> float:
        # Local HTTPS camera writes can take 80–110 ms on actual machines.
        # Capping every elapsed step at 100 ms/80 ms discards replay time and
        # accumulates drift. Keep a safety cap for true system stalls, but
        # account for ordinary slow API requests in full.
        dt = max(0.0, min(0.25, float(elapsed)))
        speed = max(0.0, float(requested_speed))
        correction = max(-self.max_rate_correction,
                         min(self.max_rate_correction, self.drift * 0.45))
        # Paused/replay zero speed must not advance due to drift correction.
        correction = correction if speed > 0 else 0.0
        progressed = max(0.0, speed + correction) * dt
        self.time += progressed
        self.drift -= correction * dt
        return self.time
