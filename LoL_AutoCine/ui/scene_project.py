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

VERSION = 1
PROFILES = ('auto', 'smooth', 'cinematic', 'dynamic')


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
            intensity=data.get('intensity') if data.get('intensity') in ('natural','standard','strong') else 'standard'
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
    return t


@dataclass
class SceneProject:
    shots: dict[str, Shot] = field(default_factory=dict)
    _undo: list = field(default_factory=list, repr=False)
    _redo: list = field(default_factory=list, repr=False)
    MAX_HISTORY = 100

    def snapshot(self):
        return {key: asdict(value) for key,value in self.shots.items()}

    def _remember(self):
        self._undo.append(self.snapshot())
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
        self.shots = {k: Shot.validated(v) for k,v in state.items()}

    def undo(self) -> bool:
        if not self._undo: return False
        self._redo.append(self.snapshot())
        self._restore(self._undo.pop())
        return True

    def redo(self) -> bool:
        if not self._redo: return False
        self._undo.append(self.snapshot())
        self._restore(self._redo.pop())
        return True

    def to_dict(self):
        return {'schema_version': VERSION, 'application': 'LoL AutoCine', 'shots': self.snapshot()}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data,dict) or data.get('schema_version') != VERSION:
            raise ValueError('未対応の編集プロジェクト形式です')
        obj = data.get('shots',{})
        if not isinstance(obj,dict) or len(obj)>5000:
            raise ValueError('シーンデータが不正です')
        return cls({k: Shot.validated(v) for k,v in obj.items() if isinstance(k,str) and len(k)<=600})

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
