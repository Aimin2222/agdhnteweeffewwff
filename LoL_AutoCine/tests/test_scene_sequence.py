# -*- coding: utf-8 -*-
"""Montage ordering should never change the default render pipeline or GPU/audio code."""
from types import SimpleNamespace
import tkinter as tk
import pytest
from core.scanner import Kill
from core.players import Player
from core.effects import Template
from ui.scene_project import Shot, SceneProject, scene_key
from ui.scene_batch import order_scenes, render_scenes
from legacy_app import App


def events():
    return [Kill(11, 101.0, 'Aimin', 'Enemy1', []),
            Kill(22, 202.0, 'Aimin', 'Enemy2', []),
            Kill(33, 303.0, 'Aimin', 'Enemy3', [])]


def test_sequence_edit_save_undo_and_version_migration(tmp_path):
    ks = events()
    keys = [scene_key(k) for k in ks]
    p = SceneProject()
    assert p.ordered_keys(keys) == keys
    assert p.move(keys[1], keys, -1)
    assert p.ordered_keys(keys) == [keys[1], keys[0], keys[2]]
    p.put(keys[1], Shot(arc=40))
    assert p.undo() and keys[1] not in p.shots
    assert p.ordered_keys(keys)[0] == keys[1]
    assert p.undo() and p.ordered_keys(keys) == keys
    assert p.redo() and p.ordered_keys(keys)[0] == keys[1]
    assert p.redo() and p.shots[keys[1]].arc == 40
    target = tmp_path / 'project.json'
    p.save(target)
    restored = SceneProject.load(target)
    assert restored.to_dict()['schema_version'] == 3
    assert restored.ordered_keys(keys)[0] == keys[1]
    assert restored.shots[keys[1]].arc == 40
    # v5.9.0 (v1 schema) loads without an order, with all camera settings intact.
    old = SceneProject.from_dict({'schema_version': 1, 'shots': {keys[0]: {'arc': 30}}})
    assert old.shots[keys[0]].arc == 30
    assert old.ordered_keys(keys) == keys
    assert restored.reset_order(keys)
    assert restored.ordered_keys(keys) == keys
    assert restored.undo() and restored.ordered_keys(keys)[0] == keys[1]


def test_new_and_filtered_scenes_keep_stable_order():
    ks = events()
    keys = [scene_key(k) for k in ks]
    p = SceneProject()
    p.move(keys[2], keys, -1)
    p.move(keys[2], keys, -1)
    assert [k.time for k in order_scenes(ks, p.sequence)] == [303, 101, 202]
    assert [k.time for k in order_scenes(ks[1:], p.sequence)] == [303, 202]
    assert [k.time for k in order_scenes(ks, None)] == [101, 202, 303]
    newer = Kill(44, 404.0, 'Aimin', 'Enemy4', [])
    assert [k.time for k in order_scenes(ks + [newer], p.sequence)] == [303, 101, 202, 404]
    assert not p.move(keys[2], keys, -1)  # already at the top
    assert p.move_to(keys[0], keys, 2)
    assert p.ordered_keys(keys) == [keys[2], keys[1], keys[0]]
    with pytest.raises(ValueError):
        SceneProject.from_dict({'schema_version': 2, 'shots': {}, 'sequence': 'bad'})


def test_render_uses_sequence_and_unmodified_audio_pipeline(tmp_path):
    ks = events()
    keys = [scene_key(k) for k in ks]
    outputs = []
    def fake_run(api, src, player, selected, template, out_root, montage, **kwargs):
        assert kwargs['audio_factory'] is not None
        assert template.game_audio
        assert not montage
        outputs.append(selected[0].event_id)
        return SimpleNamespace(outputs=[tmp_path / f'{selected[0].event_id}.mp4'], failed=[])
    report = render_scenes(None, None, SimpleNamespace(name='Aimin', champion='Lee Sin'), ks,
                           Template(game_audio=True), tmp_path, True, {}, auto=True,
                           order=[keys[2], keys[0], keys[1]], run_edit=fake_run,
                           concat=lambda clips,path: None, unique_path=lambda path:path,
                           audio_factory=lambda path:None)
    assert outputs == [33, 11, 22]
    assert report.montage is not None and len(report.outputs) == 3


def test_ui_reorder_dispatch_and_undo(tmp_path):
    root = tk.Tk()
    try:
        app = App(root)
        app.scene_project_path = tmp_path/'scenes.json'
        app.locked = Player(1, 'Aimin','Aimin#1','Aimin','Lee Sin','ORDER')
        app.kills = events()
        app.checked_kills = {0,1,2}
        app._fill_kills()
        app.lb_kills.selection_set(1)
        app.on_scene_selection()
        app.on_move_scene(-1)
        assert app.scene_order_list.get(0).startswith('01. 202')
        assert '#01' in app.lb_kills.get(1)
        app._autosave_project()
        assert SceneProject.load(app.scene_project_path).sequence[0] == scene_key(app.kills[1])
        recorded = []
        app._run_bg = lambda fn,*a: recorded.append((fn,a))
        app._need_lock = lambda:True
        app.on_make_checked()
        assert recorded[-1][0].__name__ == '_make_list'
        assert recorded[-1][1][-1][0] == scene_key(app.kills[1])
        app.on_scene_undo()
        assert app.scene_project.ordered_keys(scene_key(k) for k in app.kills)[0] == scene_key(app.kills[0])
        app.on_scene_redo()
        assert app.scene_project.ordered_keys(scene_key(k) for k in app.kills)[0] == scene_key(app.kills[1])
        # drag reorder on the timeline list should update the persisted sequence
        root.update_idletasks()
        app.scene_order_list.event_generate('<ButtonPress-1>', x=24, y=12)
        app.scene_order_list.event_generate('<ButtonRelease-1>', x=24, y=50)
        app.on_reset_scene_order()
        assert app.scene_project.ordered_keys(scene_key(k) for k in app.kills)[0] == scene_key(app.kills[0])
    finally:
        root.destroy()
