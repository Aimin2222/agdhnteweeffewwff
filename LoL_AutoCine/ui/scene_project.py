# -*- coding: utf-8 -*-
"""Versioned and validated per-scene editor project. No Tk, GPU or Replay API dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict, replace
from pathlib import Path
import copy
import json
import math
import os
import tempfile

VERSION = 3
PROFILES = ('auto', 'smooth', 'cinematic', 'dynamic')


def validate_keyframes(frames):
    """Relative-to-kill keyframes: time, additive yaw, distance zoom %, and FOV delta."""
    if frames is None:
        return []
    if not isinstance(frames, list) or len(frames) > 40:
        raise ValueError('キーフレーム数は40件までです')
    clean = {}
    for frame in frames:
        if not isinstance(frame, dict):
            raise ValueError('キーフレーム形式が不正です')
        t = bound(frame.get('time'), -15, 15, 0)
        clean[t] = {'time': t,
                    'yaw': bound(frame.get('yaw'), -70, 70, 0),
                    'zoom': bound(frame.get('zoom'), -30, 30, 0),
                    'fov': bound(frame.get('fov'), -15, 15, 0)}
    return [clean[t] for t in sorted(clean)]



def bound(value, lower: float, upper: float, default: float) -> float:
    try:
        val = float(value)
        if not math.isfinite(val):
            return default
    except (ValueError, TypeError):
        return default
    return round(min(upper, max(lower, val)), 2)


def scene_key(kill) -> str:
    """Stable across rescans (event id can change, don't key only on list index)."""
    return '|'.join((str(getattr(kill, 'event_id', -1)),
                     f'{float(getattr(kill,"time",0)):.2f}',
                     str(getattr(kill,'killer','')), str(getattr(kill,'victim',''))))


@dataclass
class Shot:
    profile: str = 'auto'
    arc: float = 10.0
    dolly: float = 3.0
    yaw: float = 0.0
    pre: float = 4.0
    post: float = 3.0
    intensity: str = 'standard'
    keyframes: list = field(default_factory=list)
    fx_override: bool = False
    temperature: float = 0.0
    bloom: float = 0.25
    focus_blur: float = 0.0
    dof_blur: float = 0.0
    highlight_pulse: float = 0.0  # 0=off, kill-timed warm/white accent

    @classmethod
    def validated(cls, data):
        if not isinstance(data, dict):
            raise ValueError('Scene data must be an object')
        return cls(
            profile=data.get('profile') if data.get('profile') in PROFILES else 'auto',
            arc=bound(data.get('arc'), 0, 75, 10),
            dolly=bound(data.get('dolly'), 0, 15, 3),
            yaw=bound(data.get('yaw'), -180, 180, 0),
            pre=bound(data.get('pre'), 1, 15, 4),
            post=bound(data.get('post'), 1, 15, 3),
            intensity=data.get('intensity') if data.get('intensity') in ('natural','standard','strong') else 'standard',
            keyframes=validate_keyframes(data.get('keyframes', [])),
            fx_override=data.get('fx_override') is True,
            temperature=bound(data.get('temperature'), -1.0, 1.0, 0.0),
            bloom=bound(data.get('bloom'), 0.0, 1.0, 0.25),
            focus_blur=bound(data.get('focus_blur'), 0.0, 1.0, 0.0),
            dof_blur=bound(data.get('dof_blur'), 0.0, 20.0, 0.0),
            highlight_pulse=bound(data.get('highlight_pulse'), 0.0, 1.0, 0.0)
        )


def recommend(kill, base_pre: float = 4, base_post: float = 3) -> Shot:
    multi = max(1, min(5, int(getattr(kill,'multikill',1))))
    assist = getattr(kill,'role','kill') == 'assist'
    if assist:
        return Shot('smooth', 8, 2, 0, base_pre, base_post, 'natural')
    if multi >= 3:
        return Shot('dynamic', 22, 8, 0, min(15,base_pre+1), min(15,base_post+1), 'strong')
    if multi == 2:
        return Shot('cinematic', 14, 5, 0, base_pre, min(15,base_post+0.5), 'standard')
    return Shot('cinematic', 10, 3, 0, base_pre, base_post, 'standard')


def apply_shot(base, shot: Shot):
    """Create an isolated Template copy; never mutate the editor's shared template."""
    t = copy.deepcopy(base)
    s = Shot.validated(asdict(shot))
    t.motion_profile = s.profile
    t.motion_arc = s.arc
    t.motion_dolly = s.dolly
    t.third_yaw = s.yaw
    t.pre = s.pre
    t.post = s.post
    t.intensity = s.intensity
    # Reuse the existing camera and effect pipelines; no renderer duplication.
    t.scene_keyframes = copy.deepcopy(s.keyframes)
    t.highlight_pulse = s.highlight_pulse
    if s.fx_override:
        t.temperature = s.temperature
        t.bloom = s.bloom
        effects = dict(getattr(t, 'video_effects', {}) or {})
        effects['focus_blur'] = s.focus_blur
        t.video_effects = effects
        t.dof_enabled = s.dof_blur > 0
        t.dof_blur = s.dof_blur
    return t


@dataclass
class SceneProject:
    shots: dict[str, Shot] = field(default_factory=dict)
    sequence: list[str] = field(default_factory=list)
    _undo: list = field(default_factory=list, repr=False)
    _redo: list = field(default_factory=list, repr=False)
    MAX_HISTORY = 100

    def snapshot(self):
        return {key: asdict(value) for key,value in self.shots.items()}

    def ordered_keys(self, keys):
        """Return existing keys in the user's montage order, followed by new scenes."""
        seen = set()
        incoming = []
        for key in keys:
            if isinstance(key, str) and key not in seen:
                incoming.append(key)
                seen.add(key)
        present = set(incoming)
        ordered = [key for key in self.sequence if key in present]
        known = set(ordered)
        return ordered + [key for key in incoming if key not in known]

    def move(self, key: str, visible_keys, step: int) -> bool:
        """Move one visible scene without changing the chronological scan results."""
        keys = self.ordered_keys(visible_keys)
        if key not in keys:
            return False
        index = keys.index(key)
        target = index + int(step)
        if not 0 <= target < len(keys):
            return False
        self._remember()
        keys[index], keys[target] = keys[target], keys[index]
        # Preserve any scenes from other scans at the end of the project's sequence.
        visible = set(keys)
        self.sequence = keys + [k for k in self.sequence if k not in visible]
        return True

    def move_to(self, key: str, visible_keys, position: int) -> bool:
        """Move one visible scene directly to a zero-based montage slot."""
        keys = self.ordered_keys(visible_keys)
        if key not in keys or not keys:
            return False
        target = max(0, min(int(position), len(keys)-1))
        if keys.index(key) == target:
            return False
        self._remember()
        keys.remove(key)
        keys.insert(target,key)
        visible = set(keys)
        self.sequence = keys + [k for k in self.sequence if k not in visible]
        return True

    def reset_order(self, visible_keys) -> bool:
        keys = list(dict.fromkeys(k for k in visible_keys if isinstance(k, str)))
        current = self.ordered_keys(keys)
        if current == keys:
            return False
        self._remember()
        selected = set(keys)
        self.sequence = keys + [k for k in self.sequence if k not in selected]
        return True

    def _state(self):
        return {'shots': self.snapshot(), 'sequence': list(self.sequence)}

    def _remember(self):
        self._undo.append(self._state())
        self._undo = self._undo[-self.MAX_HISTORY:]
        self._redo.clear()

    def put(self, key: str, shot: Shot):
        if not key or len(key) > 600:
            raise ValueError('Invalid scene key')
        checked = Shot.validated(asdict(shot))
        if key in self.shots and self.shots[key] == checked:
            return
        self._remember()
        self.shots[key] = checked

    def put_many(self, scenes):
        validated = {key: Shot.validated(asdict(shot)) for key,shot in scenes.items()
                     if isinstance(key,str) and 0<len(key)<=600}
        if not validated or all(self.shots.get(key)==shot for key,shot in validated.items()):
            return
        self._remember()
        self.shots.update(validated)

    def remove(self, key):
        if key in self.shots:
            self._remember()
            del self.shots[key]

    def _restore(self, state):
        self.shots = {k: Shot.validated(v) for k,v in state['shots'].items()}
        self.sequence = list(state['sequence'])

    def undo(self) -> bool:
        if not self._undo: return False
        self._redo.append(self._state())
        self._restore(self._undo.pop())
        return True

    def redo(self) -> bool:
        if not self._redo: return False
        self._undo.append(self._state())
        self._restore(self._redo.pop())
        return True

    def to_dict(self):
        return {'schema_version': VERSION, 'application': 'LoL AutoCine', 'shots': self.snapshot(), 'sequence': list(self.sequence)}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data,dict) or data.get('schema_version') not in (1, 2, VERSION):
            raise ValueError('未対応の編集プロジェクト形式です')
        obj = data.get('shots',{})
        if not isinstance(obj,dict) or len(obj)>5000:
            raise ValueError('シーンデータが不正です')
        seq = data.get('sequence', [])
        if not isinstance(seq, list) or len(seq) > 5000 or any(not isinstance(k, str) or not 0 < len(k) <= 600 for k in seq):
            raise ValueError('シーンの並び順データが不正です')
        return cls({k: Shot.validated(v) for k,v in obj.items() if isinstance(k,str) and len(k)<=600},
                   list(dict.fromkeys(seq)))

    def save(self, path):
        path=Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content=json.dumps(self.to_dict(),ensure_ascii=False,indent=2)
        fd,tmp=tempfile.mkstemp(prefix='.autocine_',suffix='.tmp',dir=str(path.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as fp:
                fp.write(content)
                fp.flush();os.fsync(fp.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    @classmethod
    def load(cls,path):
        path=Path(path)
        if path.stat().st_size>5_000_000:
            raise ValueError('編集ファイルが大きすぎます')
        return cls.from_dict(json.loads(path.read_text(encoding='utf-8')))
