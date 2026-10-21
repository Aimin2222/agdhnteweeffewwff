"""UI-only state and operation adapter for the 29-screen comparison project.

All methods are called on Tk's main thread. The adapter owns no replay,
capture, camera, effect, encoder, or audio implementation. Screen/theme
changes only alter presentation state; they never invoke render handlers.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from ui.director_work_controls import MODE_LABELS, select_frame_with_effect
from core.work_kill_assets import list_assets, paired_effect_for_frame
from core.camera import CAMERA_SIDE_CHOICES
from core.kill_icons import MOTION_STYLES
from core.players import norm
from ui.scene_project import scene_key
from ui.hud_presets import HUD_MODES


AUDIT = Path(__file__).resolve().parents[1] / "design" / "ui" / "implementation_audit_29_20261021"


def _screens() -> dict[str, dict]:
    rows = json.loads((AUDIT / "SCREENS_29.json").read_text(encoding="utf-8"))
    if len(rows) != 29 or len({x["family"] for x in rows}) != 12:
        raise ValueError("29画面または12候補グループが不足しています")
    return {x["id"]: x for x in rows}


SCREENS = _screens()
LEGACY_RECONSTRUCTIONS = {"T-A-M": "T-A-M.html"}
DEFAULT_SCREEN = None  # The user has not adopted or selected a candidate yet.
THEMES = {"light", "dark", "system"}
CAMERA_SIDES = {"auto": CAMERA_SIDE_CHOICES["auto"],
                "BLUE": CAMERA_SIDE_CHOICES["blue"],
                "RED": CAMERA_SIDE_CHOICES["red"]}
CAMERA_KEYS = {"third_dist": (500.0, 1400.0), "cam_height": (0.0, 900.0),
               "third_yaw": (-180.0, 180.0), "motion_arc": (0.0, 45.0),
               "motion_dolly": (0.0, 15.0)}
RESEARCH_FRAME_CARDS = (
    "083/a_simple_main", "004/demacia_frame", "004/noxus_frame",
    "004/bilgewater_frame",
)


def default_preferences_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    return base / "LoL_AutoCine" / "ui29_workspace.json"


class Audit29Runtime:
    """A single App-backed comparison session. No candidate gets its own App."""

    def __init__(self, app, preferences_path: Path | None = None):
        self.app = app
        self.preferences_path = preferences_path or default_preferences_path()
        self.screen_id = DEFAULT_SCREEN
        self.theme = "system"
        self._restore_appearance()

    def _restore_appearance(self):
        try:
            data = json.loads(self.preferences_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if data.get("screen_id") in SCREENS:
            self.screen_id = data["screen_id"]
        if data.get("theme") in THEMES:
            self.theme = data["theme"]

    def _save_appearance(self):
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"screen_id": self.screen_id, "theme": self.theme}
        replacement = self.preferences_path.with_suffix(".tmp")
        replacement.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        replacement.replace(self.preferences_path)

    def select_screen(self, screen_id: str):
        if screen_id not in SCREENS:
            raise ValueError(f"unknown screen: {screen_id}")
        self.screen_id = screen_id
        self._save_appearance()
        return self.snapshot()

    def select_theme(self, theme: str):
        if theme not in THEMES:
            raise ValueError(f"unknown theme: {theme}")
        self.theme = theme
        self._save_appearance()
        return self.snapshot()

    def snapshot(self) -> dict:
        app = self.app
        scene_rows = []
        selected = app.lb_kills.curselection()
        teams = {alias: player.team for player in app.players
                 if callable(getattr(player, "aliases", None))
                 for alias in player.aliases()}
        for index, event in enumerate(app.kills):
            team = teams.get(norm(getattr(event, "killer", "")))
            scene_rows.append({
                "index": index, "time": round(float(event.time), 2),
                "side": "BLUE" if team == "ORDER" else "RED" if team == "CHAOS" else "",
                "role": str(getattr(event, "role", "kill")),
                "killer": str(getattr(event, "killer", "")),
                "victim": str(getattr(event, "victim", "")),
                "multikill": int(getattr(event, "multikill", 1)),
                "checked": index in app.checked_kills,
                "selected": bool(selected and selected[0] == index),
            })
        camera_values = {key: float(app.sl[key].get()) for key in CAMERA_KEYS if key in app.sl}
        frame_catalog = {item["id"]: item for item in list_assets("frames", review=True)
                         if item["id"] in RESEARCH_FRAME_CARDS}
        frame_cards = []
        for frame_id in RESEARCH_FRAME_CARDS:
            item = frame_catalog.get(frame_id)
            if item is None:
                continue
            effect = paired_effect_for_frame(frame_id)
            frame_cards.append({"id": frame_id, "label": item["label"],
                                "status": item["status"],
                                "paired_effect_id": effect["id"] if effect else None,
                                "paired_effect_status": effect["status"] if effect else None})
        return {
            "workspace": {"screen_id": self.screen_id,
                          "candidate_id": SCREENS[self.screen_id]["family"] if self.screen_id else None,
                          "theme": self.theme,
                          "screens": [{"id": x["id"], "family": x["family"],
                                       "name": x["family_name"],
                                       "implemented": "html" in x or x["id"] in LEGACY_RECONSTRUCTIONS}
                                      for x in SCREENS.values()]},
            "replay": {"connected": bool(app.players),
                       "player_count": len(app.players),
                       "players": [{"slot": int(player.slot), "name": player.name,
                                    "champion": player.champion,
                                    "side": "BLUE" if player.team == "ORDER" else "RED"}
                                   for player in app.players if hasattr(player, "slot")],
                       "capture_running": bool(getattr(app, "source", None) and app.source.running),
                       "target_slot": getattr(getattr(app, "locked", None), "slot", None)},
            "scenes": scene_rows,
            "selected_scene_index": selected[0] if selected else None,
            "checked_count": len(app.checked_kills),
            "scan": {"status": str(app.lbl_scan.cget("text")) if hasattr(app, "lbl_scan") else "未スキャン",
                     "percent": float(app.pb_scan["value"]) if hasattr(app, "pb_scan") else 0.0,
                     "duration": float(getattr(getattr(app, "_match_scan_cache", None), "length", 0) or 0)},
            "event_mode": app.var_event_mode.get(),
            "edit_mode": app.var_edit_mode.get() if hasattr(app, "var_edit_mode") else "easy",
            "camera": {"mode": app.var_camera_control_mode.get(),
                       "side": app.var_camera_side.get(), "style": app.var_style.get(),
                       "values": camera_values},
            "frame": {"id": app.var_work_frame.get(), "effect_id": app.var_work_effect.get(),
                      "review": bool(app.var_work_review.get()),
                      "strength": app.var_work_strength.get(),
                      "motion": app.var_kill_icon_motion.get(), "cards": frame_cards},
            "preview": {"mirror_requested": bool(app.var_mirror.get()),
                        "fx_enabled": bool(app.var_live.get()),
                        "target_hz": app.var_preview_hz.get(),
                        "measured_fps": round(app._mirror_present_rate.fps(), 1)},
            "output": {"busy": bool(app.busy), "path": str(app.out_root),
                       "fps": app.var_fps_ui.get(), "encoder_policy": app.var_encoder_policy.get(),
                       "game_audio": bool(app.var_gaudio.get()), "hud": app.var_hud_mode.get()},
            "capabilities": {"engage": False,
                             "engage_reason": "エンゲージ専用検出・操作は未実装。キルとして扱いません"},
        }

    def perform(self, action: str, data: dict | None = None) -> dict:
        """Dispatch whitelisted UI actions to the existing App on Tk's thread."""
        app = self.app
        data = data or {}
        if action == "screen":
            return self.select_screen(str(data["id"]))
        if action == "theme":
            return self.select_theme(str(data["value"]))
        if action == "open_replay":
            app.on_open_replay()
        elif action == "prepare":
            app.on_quick_prepare()
        elif action == "scan":
            app.on_scan()
        elif action == "target_lock":
            slot = int(data["slot"])
            if slot not in {int(player.slot) for player in app.players}:
                raise ValueError("target player not found")
            app.tree.selection_set(str(slot))
            app.on_lock()
        elif action == "event_mode":
            labels = {"kill": "キル", "assist": "アシスト", "both": "キル＋アシスト"}
            mode = str(data["value"])
            if mode not in labels:
                raise ValueError("invalid event mode")
            old_checked = {scene_key(app.kills[i]) for i in app.checked_kills if 0 <= i < len(app.kills)}
            old_selected = app.lb_kills.curselection()
            selected_key = scene_key(app.kills[old_selected[0]]) if old_selected and old_selected[0] < len(app.kills) else None
            app.var_event_mode.set(labels[mode])
            app.checked_kills = {i for i, event in enumerate(app.kills) if scene_key(event) in old_checked}
            app._rebuild_kills_keep_position()
            if selected_key is not None:
                match = next((i for i, event in enumerate(app.kills) if scene_key(event) == selected_key), None)
                if match is not None:
                    app.lb_kills.selection_clear(0, "end")
                    app.lb_kills.selection_set(match)
                    app.on_scene_selection()
        elif action == "select_scene":
            index = int(data["index"])
            if not 0 <= index < len(app.kills):
                raise ValueError("scene index out of range")
            app.lb_kills.selection_clear(0, "end")
            app.lb_kills.selection_set(index)
            app.on_scene_selection()
        elif action == "jump_selected":
            app.on_jump_selected()
        elif action == "check_scene":
            index = int(data["index"])
            if not 0 <= index < len(app.kills):
                raise ValueError("scene index out of range")
            if bool(data["checked"]):
                app.checked_kills.add(index)
            else:
                app.checked_kills.discard(index)
            app._rebuild_kills_keep_position()
        elif action == "check_all":
            app.on_check_all()
        elif action == "uncheck_all":
            app.on_uncheck_all()
        elif action == "mirror_start":
            app.on_mirror_start()
        elif action == "mirror_stop":
            app.on_mirror_stop(reason="29画面UI停止")
        elif action == "preview_play":
            app.on_preview_play()
        elif action == "preview_stop":
            app.on_preview_stop()
        elif action == "camera_mode":
            mode = data.get("value")
            if mode not in MODE_LABELS:
                raise ValueError("unknown camera mode")
            app.var_camera_control_mode.set(MODE_LABELS[mode])
        elif action == "camera_side":
            side = data.get("value")
            if side not in CAMERA_SIDES:
                raise ValueError("unknown side")
            app.var_camera_side.set(CAMERA_SIDES[side])
        elif action == "camera_style":
            from core.camera import STYLES
            style = str(data["value"])
            if style not in STYLES:
                raise ValueError("unknown camera style")
            app.var_style.set(STYLES[style])
        elif action == "camera_number":
            key, value = str(data["key"]), float(data["value"])
            if key not in CAMERA_KEYS or key not in app.sl:
                raise ValueError("unknown camera setting")
            low, high = CAMERA_KEYS[key]
            if not low <= value <= high:
                raise ValueError("camera value out of range")
            app.sl[key].set(value)
        elif action == "trim":
            key, value = str(data["key"]), float(data["value"])
            if key not in ("pre", "post") or not 1 <= value <= 15:
                raise ValueError("invalid trim")
            (app.var_pre if key == "pre" else app.var_post).set(value)
        elif action == "frame":
            select_frame_with_effect(app, str(data["id"]))
        elif action == "work_gallery":
            app._open_work_gallery()
        elif action == "work_settings":
            app._open_work_kill_settings()
        elif action == "effect_strength":
            value = str(data["value"])
            if value not in ("weak", "strong"):
                raise ValueError("invalid effect strength")
            app.var_work_strength.set(value)
        elif action == "motion":
            motion = str(data["value"])
            if motion not in MOTION_STYLES:
                raise ValueError("unknown entrance motion")
            app.var_kill_icon_motion.set(MOTION_STYLES[motion])
        elif action == "fx_enabled":
            app.var_live.set(bool(data["value"]))
        elif action == "output_fps":
            fps = int(data["value"])
            if fps not in (60, 144):
                raise ValueError("unsupported output frame rate")
            app.var_fps_ui.set(f"{fps} FPS")
        elif action == "encoder_policy":
            policies = {"auto": "自動（NVENC優先・失敗時CPU）", "gpu": "GPU優先（NVENC）",
                        "cpu": "CPU優先（libx264）"}
            policy = str(data["value"])
            if policy not in policies:
                raise ValueError("unknown encoder policy")
            app.var_encoder_policy.set(policies[policy])
        elif action == "game_audio":
            app.var_gaudio.set(bool(data["value"]))
        elif action == "hud":
            mode = str(data["value"])
            if mode not in HUD_MODES:
                raise ValueError("unknown HUD mode")
            app._set_hud_mode(mode, save=True)
        elif action == "export_checked":
            app.on_make_checked()
        elif action == "export_selected":
            app.on_make_selected()
        elif action == "export_all":
            app.on_make_clips()
        elif action == "export_smart":
            app.on_smart_one_click()
        elif action == "cancel_job":
            app.on_stop()
        elif action == "output_folder":
            app.on_pick_out()
        elif action == "scene_save":
            if not app.lb_kills.curselection():
                raise ValueError("先に保存するシーンを選択してください")
            if app.busy:
                raise ValueError("書き出し中はシーン設定を保存できません")
            app.on_save_scene()
        elif action == "scene_undo":
            app.on_scene_undo()
        elif action == "scene_redo":
            app.on_scene_redo()
        elif action == "project_export":
            app.root.deiconify()
            app.root.lift()
            app.on_scene_export()
        elif action == "project_import":
            app.root.deiconify()
            app.root.lift()
            app.on_scene_import()
        elif action == "native_settings":
            app._focus_settings()
            app.root.deiconify()
            app.root.lift()
        elif action == "native_editor_zone":
            zone = str(data["zone"])
            if zone not in ("scene", "camera", "color", "fx", "output"):
                raise ValueError("unknown editor zone")
            app._focus_editor_zone(zone)
            app.root.deiconify()
            app.root.lift()
        elif action == "edit_mode":
            mode = str(data["value"])
            if mode not in ("easy", "advanced"):
                raise ValueError("unknown edit mode")
            app.var_edit_mode.set(mode)
            app._apply_edit_mode(log=False)
            if mode == "advanced":
                app.root.deiconify()
                app.root.lift()
        elif action == "diagnostics":
            app.on_show_diagnostics()
        elif action == "automatic_qa":
            app.on_automatic_qa()
        elif action == "camera_qa":
            app.on_dev_camera_qa()
        elif action == "engage":
            raise NotImplementedError("エンゲージ専用検出は未実装です")
        else:
            raise ValueError(f"unknown UI action: {action}")
        return self.snapshot()
