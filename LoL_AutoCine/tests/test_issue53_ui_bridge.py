from __future__ import annotations

from threading import Thread

from core.ui_bridge import HANDLERS, LegacyUIBridge, SharedUIState, UIThreadRequired


class FakeLegacyApp:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        if name not in {method for method, _ in HANDLERS.values()}:
            raise AttributeError(name)

        def record(*args):
            self.calls.append((name, args))
        return record


def test_all_contract_routes_resolve_and_retain_session():
    app = FakeLegacyApp()
    state = SharedUIState(replay_session_id="replay-1", mirror_session_id="mirror-1",
                          active_job_id="job-1", target_player_id="player-7")
    bridge = LegacyUIBridge(app, state)
    bridge.set_scene_state("scene-2", ("scene-1", "scene-2", "scene-1"))
    for event in HANDLERS:
        bridge.dispatch(event)
    bridge.switch_view("candidate-8-detail")
    bridge.switch_view("candidate-3-main")
    assert len(app.calls) == len(HANDLERS)
    assert state.checked_scene_ids == ("scene-1", "scene-2")
    assert (state.replay_session_id, state.mirror_session_id, state.active_job_id,
            state.target_player_id, state.selected_scene_id) == (
                "replay-1", "mirror-1", "job-1", "player-7", "scene-2")
    assert app.calls[-4:] == [("_focus_editor_zone", (zone,)) for zone in
                              ("scene", "camera", "fx", "output")]


def test_unknown_event_and_worker_thread_are_rejected():
    bridge = LegacyUIBridge(FakeLegacyApp())
    try:
        bridge.dispatch("camera.teleport")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown event accepted")
    errors = []

    def from_worker():
        try:
            bridge.dispatch("scan.start")
        except Exception as exc:
            errors.append(exc)

    worker = Thread(target=from_worker)
    worker.start()
    worker.join()
    assert len(errors) == 1 and isinstance(errors[0], UIThreadRequired)
