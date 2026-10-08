# -*- coding: utf-8 -*-
"""Optional per-scene rendering adapter. Not part of GPU backend.

Default run_auto_edit path is unchanged. When scene mode is enabled we render
one scene per existing run_auto_edit invocation, preserving audio and ffmpeg
through core.jobs; then concatenate the successful outputs once.
"""
from __future__ import annotations
from dataclasses import dataclass,field
import copy
from pathlib import Path
from typing import Callable
from .scene_project import SceneProject, Shot, recommend, scene_key, apply_shot

@dataclass
class BatchResult:
    outputs: list = field(default_factory=list)
    failed: list = field(default_factory=list)
    montage: object = None


def order_scenes(kills, order):
    """Stable ordering: explicitly ordered kills first, new/unlisted kills afterwards."""
    if not order:
        return list(kills)
    lookup = {key: i for i, key in enumerate(order)}
    incoming = list(kills)
    return [kill for _, kill in sorted(enumerate(incoming),
                                     key=lambda entry: (lookup.get(scene_key(entry[1]), len(lookup)), entry[0]))]


def build_scene_templates(kills, tpl, overrides: dict, *, auto: bool, order=None):
    for kill in order_scenes(kills, order):
        key=scene_key(kill)
        if key in overrides:
            shot=Shot.validated(overrides[key])
        elif auto:
            shot=recommend(kill, tpl.pre, tpl.post)
        else:
            yield kill, copy.deepcopy(tpl)
            continue
        scene_template = apply_shot(tpl,shot)
        # Only third-person modes are adapted to Lolnam-style motion. Respect FPS/top modes.
        if scene_template.style in ('third', 'third_cinema'):
            scene_template.style = 'lolnam_cinema'
        yield kill, scene_template


def render_scenes(api,source,player,kills,tpl,out_root,make_montage,
                  overrides, *, auto=False,progress=None,stop=None,log=lambda s:None,audio_factory=None,
                  run_edit=None, concat=None, unique_path=None, order=None):
    """Inject dependencies for tests; never read tkinter variables here.

    Per-scene override uses standalone clips (no cross-scene multikill merging).
    When disabled the caller should invoke core.jobs.run_auto_edit directly.
    """
    if run_edit is None:
        from core.jobs import run_auto_edit as run_edit
    if concat is None:
        from core.effects import concat_clips as concat
    if unique_path is None:
        from core.jobs import unique_path as unique_path
    out=BatchResult()
    scenes=list(build_scene_templates(kills,tpl,overrides,auto=auto,order=order))
    for i,(kill,scene_tpl) in enumerate(scenes,1):
        if stop is not None and stop.is_set():
            log('中止しました。');break
        log(f'SCENE_PLAN {i}/{len(scenes)} event={getattr(kill,"event_id", "?")} '
            f'camera={scene_tpl.motion_profile} arc={scene_tpl.motion_arc:g} dolly={scene_tpl.motion_dolly:g} '
            f'pre={scene_tpl.pre:g} post={scene_tpl.post:g}')
        def child_progress(_done,_total,pct,message):
            if progress:
                progress(i-1,len(scenes),100*(i-1+pct/100)/max(1,len(scenes)),f'{i}/{len(scenes)} {message}')
        try:
            single=run_edit(api,source,player,[kill],scene_tpl,out_root,False,
                            progress=child_progress,stop=stop,log=log,audio_factory=audio_factory)
            out.outputs.extend(single.outputs)
            out.failed.extend([(i,msg) for _,msg in single.failed])
        except Exception as e:
            out.failed.append((i,f'{type(e).__name__}: {e}'))
            log(f'SCENE_ERROR {i}: {e}')
        if progress:
            progress(i,len(scenes),100*i/max(1,len(scenes)),f'シーン {i}/{len(scenes)} 完了')
    if make_montage and len(out.outputs)>=2 and not (stop is not None and stop.is_set()):
        try:
            from core.jobs import safe_name
            out_dir=Path(out_root)/f'{safe_name(player.name)}_{safe_name(player.champion)}'
            target=unique_path(out_dir/'montage.mp4')
            concat(out.outputs,target)
            out.montage=target
            log(f'シーン別モンタージュ保存: {target.name}')
        except Exception as e:
            out.failed.append((0,f'montage: {e}'))
            log(f'モンタージュ失敗: {e}')
    return out
