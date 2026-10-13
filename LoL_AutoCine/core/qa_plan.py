# -*- coding: utf-8 -*-
"""Data-only remote test plan; never downloads or executes Python source."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.request import Request, urlopen

REMOTE_PLAN = ("https://raw.githubusercontent.com/Aimin2222/agdhnteweeffewwff/"
               "refs/heads/codex/lol-autocine-v51026-qa30mb-handoff/"
               "LoL_AutoCine/qa/test_plan.json")
LOCAL_PLAN = Path(__file__).resolve().parents[1] / "qa" / "test_plan.json"
ALLOWED_CAMERA = ("third", "third_cinema", "fps", "lolnam_cinema", "geo_aim")
ALLOWED_MONTAGE = ("cut", "flash", "dark", "white", "soft", "gold", "cool", "pulse", "cinema", "shadow")
ALLOWED_SPATIAL = ("fade", "wipeleft", "slideright", "circleopen", "pixelize", "smoothup")
ALLOWED_BADGE = ("instant", "slide_left", "slide_right", "slide_up", "slide_down", "pop")


def validate_plan(value):
    """Restrict remote JSON strictly to known test operations and safe sizes."""
    if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
            or value.get("schema_version") != 1):
        raise ValueError("QA plan schema mismatch")
    def choose(key, allowed):
        raw = value.get(key, list(allowed))
        if not isinstance(raw, list) or not raw or len(raw) > len(allowed):
            raise ValueError("Invalid QA test list: " + key)
        if any(not isinstance(x, str) or x not in allowed for x in raw):
            raise ValueError("Unknown QA test: " + key)
        return list(dict.fromkeys(raw))
    try:
        size = int(value.get("max_zip_mb", 30))
    except (TypeError, ValueError) as e:
        raise ValueError("Invalid ZIP size") from e
    if size < 30 or size > 500:
        raise ValueError("QA ZIP cap must be 30–500 MB (CameraQA enforces 30 MB)")
    visual = value.get("include_visual_comparison", True)
    if type(visual) is not bool:
        raise ValueError("Invalid visual comparison flag")
    return {
        "schema_version": 1,
        "plan_id": str(value.get("plan_id", "local"))[:128],
        "camera_modes": choose("camera_modes", ALLOWED_CAMERA),
        "montage_styles": choose("montage_styles", ALLOWED_MONTAGE),
        "badge_motions": choose("badge_motions", ALLOWED_BADGE),
        "spatial_transition_previews": choose("spatial_transition_previews", ALLOWED_SPATIAL),
        "max_zip_mb": size,
        "include_visual_comparison": visual,
    }


def load_qa_plan(*, log=lambda _m: None, allow_remote=True):
    local = validate_plan(json.loads(LOCAL_PLAN.read_text(encoding="utf-8")))
    if not allow_remote:
        return local, "bundled"
    try:
        request = Request(REMOTE_PLAN, headers={"User-Agent": "AutoCine-QA/1"})
        with urlopen(request, timeout=3) as response:
            raw = response.read(64 * 1024 + 1)
        if len(raw) > 64 * 1024:
            raise ValueError("QA plan is too large")
        remote = validate_plan(json.loads(raw.decode("utf-8")))
        log("開発用テスト計画をGitHubから取得: " + remote["plan_id"])
        return remote, "github"
    except Exception as exc:
        log("テスト計画の通信に失敗。付属の計画を使用: " + str(exc))
        return local, "bundled"
