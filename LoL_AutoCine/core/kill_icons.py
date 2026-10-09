# -*- coding: utf-8 -*-
"""Original optional right-side kill-feed overlays for 16:9 LoL highlights.

Do not touch the game's HUD. A transparent PNG is composed into the exported
clip at the exact scene event times, so this works with HUD-hidden recordings.
All editor-supplied options are normalized here, before they reach FFmpeg.
"""
from __future__ import annotations

import math
from pathlib import Path

STYLES = {
    "off": "なし（従来どおり）",
    "simple": "シンプル",
    "cinema": "シネマ・ゴールド",
    "neon": "ネオン・ブルー",
    "impact": "インパクト・レッド",
}
REVERSE_STYLES = {label: code for code, label in STYLES.items()}
POSITIONS = {
    "right-top": "右上（おすすめ）",
    "right-bottom": "右下",
    "left-top": "左上",
    "left-bottom": "左下",
}
REVERSE_POSITIONS = {label: code for code, label in POSITIONS.items()}
COLORS = {
    "simple": (196, 208, 223),
    "cinema": (247, 197, 102),
    "neon": (160, 139, 255),
    "impact": (255, 122, 125),
}


def normalize(style: str) -> str:
    return str(style) if style in STYLES else "off"


def normalize_options(position="right-top", scale=1.0, seconds=1.55, opacity=1.0):
    """Pure validation: keep FFmpeg expressions bounded and injection-safe."""
    def finite(value, fallback, lower, upper):
        try:
            val = float(value)
        except (TypeError, ValueError, OverflowError):
            val = fallback
        return max(lower, min(upper, val)) if math.isfinite(val) else fallback
    pos = position if position in POSITIONS else "right-top"
    return pos, finite(scale, 1.0, .5, 1.8), finite(seconds, 1.55, .45, 4.0), finite(opacity, 1.0, .25, 1.0)


def _rounded_portrait(canvas, source, xy, radius=11):
    """Paste the original champion portrait, not a fake silhouette or text."""
    from PIL import Image, ImageDraw, ImageOps
    left, top, size = xy
    with Image.open(source) as src:
        square = ImageOps.fit(src.convert("RGB"), (size, size), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (size,size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,size-1,size-1), radius=radius, fill=255)
    canvas.paste(square, (left,top), mask)


def make_badge(path: Path, style: str, count: int = 1, *, killer_icon=None, victim_icon=None) -> Path:
    """A champion x champion graphic. No KILL, x1, count or player names.

    Icons must be genuine (local/cache or Riot Data Dragon). If callers cannot
    resolve either portrait, they must not present this as a verified kill pair.
    The count argument remains only for compatibility with older callers.
    """
    from PIL import Image, ImageDraw, ImageFilter
    style = normalize(style)
    if style == "off":
        raise ValueError("Kill decoration is disabled")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    color = COLORS[style]
    w,h=385,116
    base=Image.new("RGBA", (w,h), (0,0,0,0))
    glow=Image.new("RGBA", (w,h), (0,0,0,0))
    g=ImageDraw.Draw(glow)
    if style != "simple":
        for x in (78, 307):
            g.rounded_rectangle((x-38,16,x+38,100), radius=12, outline=(*color,190), width=9)
        g.line((169,38,216,79),fill=(*color,185),width=7)
        g.line((214,38,169,79),fill=(*color,185),width=7)
        base=Image.alpha_composite(base,glow.filter(ImageFilter.GaussianBlur(11)))
    d=ImageDraw.Draw(base)
    # Small separated portrait medallions, not a full-width title card.
    for x in (38,267):
        d.rounded_rectangle((x-4,14,x+80,102), radius=14,fill=(13,19,30,210),outline=(*color,255),width=3)
    if killer_icon is not None:
        _rounded_portrait(base,killer_icon,(44,24,68))
    if victim_icon is not None:
        _rounded_portrait(base,victim_icon,(273,24,68))
    d=ImageDraw.Draw(base)
    for x in (38,267):
        d.rounded_rectangle((x-4,14,x+80,102),radius=14,outline=(*color,245),width=2)
    # Distinctive restrained clash motif, no "x" text or count.
    if style == "cinema":
        d.polygon([(171,29),(185,48),(215,83),(201,91),(188,69)],fill=(*color,240))
        d.polygon([(213,29),(199,48),(169,83),(183,91),(196,69)],fill=(255,244,212,232))
    elif style == "neon":
        d.line((171,33,213,83),fill=(*color,255),width=5)
        d.line((213,33,171,83),fill=(224,213,255,255),width=5)
        d.ellipse((185,52,199,66),fill=(250,250,255,230))
    elif style == "impact":
        d.polygon([(166,27),(192,52),(219,23),(205,55),(221,88),(192,65),(168,91),(181,58)],fill=(*color,245))
        d.line((166,29,220,88),fill=(255,225,214,240),width=3)
    else:
        d.line((173,35,210,82),fill=(*color,245),width=4)
        d.line((210,35,173,82),fill=(*color,245),width=4)
    base.save(path,format="PNG")
    return path


def _player_for_name(name, roster):
    """Match exact summoner/game names, never guess from champion display names."""
    from .players import norm
    target=norm(str(name or ""))
    if not target:
        return None
    players = []
    for p in roster or []:
        d = p if isinstance(p,dict) else p.to_dict()
        players.append((d, [d.get("name"),d.get("summoner"),d.get("riot_id")]))
    exact = [d for d, aliases in players if target in {norm(x) for x in aliases if x}]
    if exact:
        return exact[0] if len(exact) == 1 else None
    short = [d for d, aliases in players if target in
             {norm(x.split("#")[0]) for x in aliases if isinstance(x,str) and "#" in x}]
    return short[0] if len(short) == 1 else None


def _icon_id(player):
    import re
    # The replay raw character code is usually Riot's Data Dragon ID.
    raw=(player.get("selection_name") or player.get("raw_champion") or "")
    raw=str(raw).replace("game_character_displayname_", "")
    synonyms={"Wukong":"MonkeyKing", "FiddleSticks":"Fiddlesticks", "NunuWillump":"Nunu",
              "RenataGlasc":"Renata", "Kaisa":"Kaisa", "Khazix":"Khazix"}
    raw=synonyms.get(raw,raw)
    return raw if re.fullmatch(r"[A-Za-z0-9]{2,36}",raw) else None


def champion_icon(player, *, cache_dir=None, download=True):
    """Resolve a genuine Riot champion icon; cache online results for offline runs.

    Never fabricate an incorrect replacement or turn an arbitrary user string
    into a URL. Use bundled/local PNGs first; downloading is best-effort.
    """
    import os, json, urllib.request
    from PIL import Image
    identifier=_icon_id(player)
    if identifier is None:
        return None
    app_root=Path(__file__).resolve().parents[1]
    cache=Path(cache_dir) if cache_dir is not None else Path(os.getenv("LOCALAPPDATA",str(Path.home()/".cache")))/"LoL_AutoCine"/"champion_icons"
    # Local custom packs let all badges work when no Internet is available.
    for cand in (app_root/"assets"/"champion_icons"/(identifier+".png"),cache/(identifier+".png")):
        if cand.is_file():
            try:
                with Image.open(cand) as im: im.verify()
                return cand
            except (OSError,ValueError):
                pass
    if not download:
        return None
    try:
        cache.mkdir(parents=True,exist_ok=True)
        version_file=cache/"ddragon_version.txt"
        if version_file.exists():
            version=version_file.read_text('ascii').strip()
        else:
            req=urllib.request.Request("https://ddragon.leagueoflegends.com/api/versions.json",headers={"User-Agent":"LoL-AutoCine/5.9.9"})
            with urllib.request.urlopen(req,timeout=3.0) as r:
                version=json.loads(r.read(16000))[0]
            version_file.write_text(version,encoding="ascii")
        import re
        if not re.fullmatch(r"\d+\.\d+\.\d+",version):
            return None
        url=f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{identifier}.png"
        with urllib.request.urlopen(url,timeout=4.0) as r:
            data=r.read(400000)
        # Validate before publishing the cache file.
        import io
        with Image.open(io.BytesIO(data)) as im: im.verify()
        target=cache/(identifier+".png")
        target.write_bytes(data)
        return target
    except Exception:
        return None


def make_event_badges(output: Path, style: str, kills, events, roster, *, icon_lookup=None, log=None):
    """Produce genuine portrait pairs separately for every kill in a clip."""
    entries=[]
    icon_lookup = champion_icon if icon_lookup is None else icon_lookup
    resolved_icons = {}
    if len(events)!=len(kills):
        if log:log("キルアイコン: イベント時刻とキル件数が一致しないため装飾を省略")
        return entries
    for k,event in zip(kills,events):
        a=_player_for_name(getattr(k,"killer",None),roster)
        b=_player_for_name(getattr(k,"victim",None),roster)
        if not a or not b:
            if log:log("キルアイコン: キラーか対象のプレイヤー情報がなく装飾を省略")
            continue
        def resolve(player):
            identifier = _icon_id(player)
            if identifier not in resolved_icons:
                resolved_icons[identifier] = icon_lookup(player) if identifier else None
            return resolved_icons[identifier]
        icon_a=resolve(a)
        icon_b=resolve(b)
        if icon_a is None or icon_b is None:
            if log:log("キルアイコン: 公式肖像アイコン未取得。ネット接続またはassets/champion_iconsを確認")
            continue
        f=Path(output).with_name(Path(output).stem+f".kill_pair_{len(entries)+1:02d}.png")
        make_badge(f,style,killer_icon=icon_a,victim_icon=icon_b)
        entries.append((f,float(event[0])))
    return entries


def with_badges(graph: str, badge_input: int, badges, *, duration: float,
                position="right-top",scale=1.0,seconds=1.55,opacity=1.0,style="simple"):
    """Overlay each unique kill pair at its own event time. Later kills replace earlier ones."""
    if not graph.endswith("[vout]"):
        raise ValueError("Existing video graph has no [vout]")
    if not badges:
        return graph
    position,scale,seconds,opacity=normalize_options(position,scale,seconds,opacity)
    valid=sorted([(i,float(t)) for i,(_,t) in enumerate(badges) if math.isfinite(float(t)) and 0<=float(t)<=duration],key=lambda p:p[1])
    if not valid: return graph
    planned=[]
    for n,(img_index,t) in enumerate(valid):
        first=max(0.0,t-0.10)
        after=max(0.0,valid[n+1][1]-0.10) if n+1<len(valid) else float(duration)
        last=min(float(duration),t+seconds,after)
        if last>first:
            planned.append((img_index,t,first,last))
    if not planned:
        return graph
    pieces=[graph[:-6]+"[pair_src_0]"]
    x="W-w-32" if position.startswith("right") else "32"
    y="62" if position.endswith("top") else "H-h-62"
    for n,(img_index,t,first,last) in enumerate(planned):
        extra=(f"+7*sin(35*(t-{t:.3f}))*exp(-11*abs(t-{t:.3f}))" if normalize(style)=="impact" else "")
        inlabel=f"pair_src_{n}"
        outlabel="vout" if n==len(planned)-1 else f"pair_src_{n+1}"
        pieces.append(f"[{int(badge_input)+img_index}:v]format=rgba,scale=w='trunc(iw*{scale:.3f}/2)*2':h='trunc(ih*{scale:.3f}/2)*2',colorchannelmixer=aa={opacity:.3f}[pair_img_{n}]")
        pieces.append(f"[{inlabel}][pair_img_{n}]overlay=x='{x+extra}':y='{y}':format=auto:shortest=0:eof_action=repeat:enable='between(t,{first:.3f},{last:.3f})'[{outlabel}]")
    return ";".join(pieces[:-1]+[pieces[-1].replace("[vout]","[pair_finished]") , "[pair_finished]format=yuv420p[vout]"])


def with_badge(graph: str, badge_input: int, events, *, duration: float,
               position: str = "right-top", scale: float = 1.0,
               seconds: float = 1.55, opacity: float = 1.0,
               style: str = "simple") -> str:
    """Append a bounded, kill-synchronized overlay after the existing [vout].

    The output is still named [vout]. No audio graph or gameplay frames change.
    """
    if not graph.endswith("[vout]"):
        raise ValueError("Existing video graph has no [vout]")
    position, scale, seconds, opacity = normalize_options(position, scale, seconds, opacity)
    valid_duration = max(0.0, float(duration))
    times = []
    for event in list(events or [])[:24]:
        try:
            t = float(event[0])
        except (ValueError, TypeError, IndexError):
            continue
        if math.isfinite(t) and 0 <= t <= valid_duration:
            times.append(t)
    if not times:
        return graph
    spans = []
    for center in times:
        lo = max(0.0, center - 0.10)
        hi = min(valid_duration, center + seconds)
        if hi > lo:
            spans.append(f"between(t,{lo:.3f},{hi:.3f})")
    if not spans:
        return graph
    y = "62" if position.endswith("top") else "H-h-62"
    x = "W-w-32" if position.startswith("right") else "32"
    if normalize(style) == "impact":
        # Small, damped kick rather than a disorienting screen shake.
        kick = "+".join(f"7*sin(35*(t-{center:.3f}))*exp(-11*abs(t-{center:.3f}))" for center in times[:6])
        x += "+" + kick
    return (graph[:-6] + "[pre_kill_badge];"
            + f"[{int(badge_input)}:v]format=rgba,"
            + f"scale=w='trunc(iw*{scale:.3f}/2)*2':h='trunc(ih*{scale:.3f}/2)*2',"
            + f"colorchannelmixer=aa={opacity:.3f}[kill_badge];"
            + "[pre_kill_badge][kill_badge]"
            + f"overlay=x='{x}':y='{y}':format=auto:shortest=0:eof_action=repeat:"
            + f"enable='{'+'.join(spans)}',format=yuv420p[vout]")
