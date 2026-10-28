"""UI replacement seam for the existing Tk application.

The selected UI may change, but this object and the legacy App stay alive.
No renderer, recorder, replay connection, or Tk widget is created here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import threading
from typing import Any


@dataclass
class SharedUIState:
    replay_session_id: str | None = None
    target_player_id: str | None = None
    selected_scene_id: str | None = None
    checked_scene_ids: tuple[str, ...] = ()
    camera_side: str = "auto"
    camera_mode: str = "manual"
    camera_style: str = "third_cinema"
    camera_parameters: dict[str, Any] = field(default_factory=dict)
    output_settings: dict[str, Any] = field(default_factory=dict)
    mirror_session_id: str | None = None
    active_job_id: str | None = None
    view_key: str = "legacy"


class UIThreadRequired(RuntimeError):
    """Tk commands must be issued by the thread that constructed the bridge."""


# Actual legacy handlers, not duplicated backend implementations. Entries with
# a zone argument navigate the existing detailed editor without editing values.
HANDLERS: dict[str, tuple[str, str | None]] = {
    "replay.open": ("on_open_replay", None),
    "scan.start": ("on_scan", None),
    "preview.play": ("on_preview_play", None),
    "preview.stop": ("on_preview_stop", None),
    "mirror.start": ("on_mirror_start", None),
    "mirror.stop": ("on_mirror_stop", None),
    "export.selected": ("on_make_selected", None),
    "export.checked": ("on_make_checked", None),
    "export.all": ("on_make_clips", None),
    "jobs.cancel": ("on_stop", None),
    "assets.open": ("_open_work_gallery", None),
    "frames.open": ("_open_kill_frame_gallery", None),
    "settings.open": ("_focus_settings", None),
    "diagnostics.open": ("on_show_diagnostics", None),
    "scene.open": ("_focus_editor_zone", "scene"),
    "camera.open": ("_focus_editor_zone", "camera"),
    "fx.open": ("_focus_editor_zone", "fx"),
    "output.open": ("_focus_editor_zone", "output"),
}


class LegacyUIBridge:
    """Call existing App handlers without reconstructing the App or its jobs.

    This is opt-in preparation; the current UI does not instantiate it. A new
    view must dispatch from the Tk UI thread and retain this instance across
    view changes. Long jobs remain owned by the original App.
    """

    def __init__(self, app: Any, state: SharedUIState | None = None) -> None:
        self.app = app
        self.state = state if state is not None else SharedUIState()
        self._owner = threading.get_ident()

    def _on_ui_thread(self) -> None:
        if threading.get_ident() != self._owner:
            raise UIThreadRequired("Dispatch Tk events using root.after on the UI thread")

    def switch_view(self, view_key: str) -> SharedUIState:
        self._on_ui_thread()
        if not view_key:
            raise ValueError("view_key is required")
        self.state.view_key = view_key
        return self.state

    def dispatch(self, event: str) -> Any:
        self._on_ui_thread()
        try:
            method_name, argument = HANDLERS[event]
        except KeyError as exc:
            raise ValueError(f"Unsupported UI event: {event}") from exc
        handler = getattr(self.app, method_name)
        return handler() if argument is None else handler(argument)

    def set_scene_state(self, selected: str | None, checked: tuple[str, ...]) -> None:
        """Store stable scene IDs; widget index mapping belongs to the chosen view."""
        self._on_ui_thread()
        self.state.selected_scene_id = selected
        self.state.checked_scene_ids = tuple(dict.fromkeys(checked))

    def mark_job(self, job_id: str | None) -> None:
        self._on_ui_thread()
        self.state.active_job_id = job_id

    def mark_mirror(self, session_id: str | None) -> None:
        self._on_ui_thread()
        self.state.mirror_session_id = session_id
