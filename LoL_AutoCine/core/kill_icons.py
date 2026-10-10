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

MARK_STYLES = {
    'auto': 'テンプレートに合わせる',
    'cross': 'シャープX',
    'slash': '二重斬撃',
    'swords': '交差する剣',
    'bolt': '稲妻',
    'crystal': 'クリスタル',
    'crest': '金のエンブレム',
    'shard': '細いガラス斬撃（新）',
    'none': '表示なし（アイコンのみ）',
    'royal': 'ロイヤルゴールド紋章（参考画像風）',
    'lolkill': 'LoL風・撃破エンブレム（オリジナル）',
}
REVERSE_MARK_STYLES = {value: key for key, value in MARK_STYLES.items()}


def valid_hex(value: str, default: str = '') -> str:
    """Strict RGB hex validation for user-configurable decoration colours."""
    import re
    value = str(value or '').strip()
    return value.upper() if re.fullmatch(r'#[0-9a-fA-F]{6}', value) else default


def normalize_design(frame_color='', glow_color='', glow_enabled=True,
                     glow_strength=.65, border_width=3, mark_style='auto'):
    def finite(value, default, minimum, maximum):
        try:
            number = float(value)
            return max(minimum, min(maximum, number)) if math.isfinite(number) else default
        except (ValueError, TypeError, OverflowError):
            return default
    return (valid_hex(frame_color), valid_hex(glow_color), bool(glow_enabled),
            finite(glow_strength, .85, 0, 2), int(finite(border_width, 3, 1, 8)),
            mark_style if mark_style in MARK_STYLES else 'auto')


def _rgb(hex_color, fallback):
    return tuple(bytes.fromhex(hex_color[1:])) if hex_color else fallback


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


def make_badge(path: Path, style: str, count: int = 1, *, killer_icon=None, victim_icon=None,
               frame_color='', glow_color='', glow_enabled=True, glow_strength=.85,
               border_width=3, mark_style='auto', sparkle_strength=1.0):
    """Build an ORIGINAL transparent premium kill-feed asset with genuine portraits.

    The reference artwork is a visual target only: do not stamp static
    champions/background into a dynamic clip. This runtime image remains RGBA
    so frame, bloom and centre crest overlay actual gameplay.
    """
    from PIL import Image, ImageDraw, ImageFilter
    style = normalize(style)
    if style == "off":
        raise ValueError("Kill decoration is disabled")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame_color, glow_color, glow_enabled, glow_strength, border_width, mark_style = normalize_design(
        frame_color, glow_color, glow_enabled, glow_strength, border_width, mark_style)
    mark = mark_style if mark_style != 'auto' else {
        'simple':'none', 'cinema':'royal', 'neon':'lolkill', 'impact':'lolkill'
    }[style]
    gold = (249, 194, 84)
    color = _rgb(frame_color, COLORS[style])
    light_color = _rgb(glow_color, color)
    w, h = 385, 116
    base = Image.new('RGBA', (w, h))
    intensity = min(2.0, max(0.0, float(glow_strength))) if glow_enabled else 0.0
    try:
        sparkle = max(0.0, min(2.0, float(sparkle_strength)))
    except (TypeError, ValueError):
        sparkle = 1.0

    # Multi-scale glows really emit light beyond the painted line: separate
    # halo, middle bloom and a bright core, all on transparent layers.
    if intensity:
        emit = Image.new('RGBA', (w, h))
        halo_draw = ImageDraw.Draw(emit)
        for x in (37, 266):
            halo_draw.rounded_rectangle((x-5, 13, x+82, 103), radius=8,
                                         outline=(*light_color, 255), width=8)
        if mark != 'none':
            halo_draw.ellipse((166, 25, 219, 92), outline=(*light_color, 240), width=7)
        for blur, alpha in ((19, .65), (9, .8), (3, .55)):
            layer = emit.filter(ImageFilter.GaussianBlur(blur))
            layer.putalpha(layer.getchannel('A').point(
                lambda a, factor=alpha: min(255, int(a * factor * intensity))))
            base = Image.alpha_composite(base, layer)
        # Long soft horizontal streaks and tiny sparks, without burying faces.
        shine = Image.new('RGBA', (w, h))
        sd = ImageDraw.Draw(shine)
        ray_alpha = min(220, int(70 * intensity * sparkle))
        for x0, x1, cy in ((2, 74, 20), (312, 383, 20), (2, 65, 97), (319, 383, 97)):
            sd.line((x0,cy,x1,cy), fill=(*light_color,ray_alpha),width=2)
        base = Image.alpha_composite(base, shine.filter(ImageFilter.GaussianBlur(3)))

    d = ImageDraw.Draw(base)
    for x in (37, 266):
        # Bevelled, cut-corner metallic quadrilateral inspired by the
        # provided sample, not a copy of any third-party UI asset.
        poly = [(x+8, 13), (x+74,13), (x+82,21), (x+82,94),
                (x+73,103), (x+8,103), (x-5,90), (x-5,25)]
        d.polygon(poly,fill=(8,12,22,226))
        d.line(poly + [poly[0]],fill=(*color,255),width=max(1,border_width+1),joint='curve')
        d.line([(x+8,17),(x+70,17),(x+77,24)],fill=(255,248,212,255),width=2)
        d.line([(x+77,92),(x+70,99),(x+9,99)],fill=(*color,255),width=2)
        d.line([(x,28),(x,88),(x+10,98)],fill=(*color,222),width=2)

    if killer_icon is not None:
        _rounded_portrait(base, killer_icon, (44,24,68), radius=3)
    if victim_icon is not None:
        _rounded_portrait(base, victim_icon, (273,24,68), radius=3)
    d = ImageDraw.Draw(base)
    for x in (37,266):
        d.rectangle((x+6, 21, x+77, 95),outline=(255,219,122,240) if style=='cinema' else (*color,238),width=2)
        d.line((x-1,21,x+14,21), fill=(255,255,229,255),width=2)
        d.line((x+65,98,x+81,98), fill=(*color,255),width=2)
        # Corner flares create the "actually glowing" gold-white glint.
        if intensity and sparkle:
            for cx,cy in ((x-2,19),(x+80,98)):
                strength = min(255,int(105 * intensity * sparkle))
                d.line((cx-9,cy,cx+9,cy),fill=(255,241,176,strength),width=2)
                d.line((cx,cy-9,cx,cy+9),fill=(255,241,176,strength),width=2)
                d.polygon(((cx,cy-4),(cx+4,cy),(cx,cy+4),(cx-4,cy)),
                          fill=(255,255,243,min(255,int(170*intensity*sparkle))))

    cx,cy=192,58
    if mark == 'none':
        pass
    elif mark in ('royal','lolkill'):
        # New symmetrical high-end emblem, generated from vector geometry.
        # Six polished feathers converging into a diamond-tipped spear.
        metal = (255,211,111,255) if style=='cinema' else (*color,255)
        core = (255,250,222,255)
        d.ellipse((cx-16,cy-22,cx+16,cy+22),outline=(*light_color,210),width=2)
        for sign in (-1,1):
            for offset in (-1,0,1):
                y=cy+offset*14
                d.polygon([(cx+sign*5,y),(cx+sign*24,y-9),
                           (cx+sign*17,y+1),(cx+sign*7,y+7)],fill=metal)
                d.line((cx+sign*7,y+2,cx+sign*19,y-5),fill=core,width=1)
        if mark=='royal':
            d.polygon([(cx,cy-33),(cx+7,cy-4),(cx,cy+27),(cx-7,cy-4)],
                      fill=metal)
            d.polygon([(cx,cy-21),(cx+3,cy-4),(cx,cy+15),(cx-3,cy-4)],
                      fill=core)
        else:
            d.polygon([(cx,cy-28),(cx+9,cy-4),(cx,cy+24),(cx-9,cy-4)],
                      fill=metal)
            d.line((cx-17,cy+27,cx+17,cy-27),fill=core,width=2)
        d.polygon([(cx-7,cy),(cx,cy-9),(cx+7,cy),(cx,cy+9)],fill=core)
    elif mark == 'crest':
        d.ellipse((cx-14,cy-14,cx+14,cy+14),outline=(*color,240),width=3)
        for dx,dy in ((0,-32),(24,-18),(30,0),(24,18),(0,32),(-24,18),(-30,0),(-24,-18)):
            d.line((cx+dx*.42,cy+dy*.42,cx+dx,cy+dy),fill=(*color,255),width=4)
        d.polygon([(cx,cy-16),(cx+10,cy),(cx,cy+16),(cx-10,cy)],fill=(*color,255))
    elif mark == 'shard':
        d.polygon([(184,26),(195,28),(207,49),(194,61),(190,85),(181,91),(185,62),(198,48)],
                  fill=(*color,255))
        d.line((180,84,204,30),fill=(255,248,230,250),width=2)
    elif mark == 'slash':
        d.polygon([(171,29),(185,48),(215,83),(201,91),(188,69)],fill=(*color,255))
        d.polygon([(213,29),(199,48),(169,83),(183,91),(196,69)],fill=(255,244,212,255))
    elif mark == 'cross':
        d.line((171,33,213,83),fill=(*color,255),width=5)
        d.line((213,33,171,83),fill=(224,213,255,255),width=5)
    elif mark == 'bolt':
        d.polygon([(166,27),(192,52),(219,23),(205,55),(221,88),(192,65),(168,91),(181,58)],
                  fill=(*color,255))
    elif mark == 'swords':
        d.line((172,30,211,83),fill=(*color,255),width=8)
        d.line((212,30,173,83),fill=(245,246,255,255),width=8)
    elif mark == 'crystal':
        d.polygon([(192,22),(216,58),(192,96),(168,58)],fill=(*color,255))
    else:
        d.line((173,35,210,82),fill=(*color,255),width=4)
        d.line((210,35,173,82),fill=(*color,255),width=4)
    if mark != 'none':
        # Guarantees a crisp luminous pixel at the heart of every ornament.
        d.ellipse((cx-2,cy-2,cx+2,cy+2),fill=(255,250,222,250))
    base.save(path,format='PNG')
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


def make_event_badges(output: Path, style: str, kills, events, roster, *, icon_lookup=None, log=None, **design):
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
        make_badge(f,style,killer_icon=icon_a,victim_icon=icon_b,**design)
        entries.append((f,float(event[0])))
    return entries


def badge_plan(badges, duration, seconds):
    """Identical bounded stacking for CPU and GPU portrait compositors."""
    valid = sorted([(i,float(t)) for i,(_,t) in enumerate(badges)
                    if math.isfinite(float(t)) and 0 <= float(t) <= duration], key=lambda it:it[1])
    planned=[]
    for idx,t in valid:
        start=max(0.,t-.10)
        end=min(float(duration),t+seconds)
        if end <= start:
            continue
        active=[entry for entry in planned if entry['end'] > start]
        available=set(range(3)) - {entry['row'] for entry in active}
        if not available:
            oldest=min(active,key=lambda entry:entry['start'])
            oldest['end']=max(oldest['start'],start-.01)
            available.add(oldest['row'])
        planned.append(dict(index=idx, time=t, start=start, end=end, row=min(available)))
    return [entry for entry in planned if entry['end']>entry['start']]


def with_badges(graph: str, badge_input: int, badges, *, duration: float,
                position="right-top",scale=1.0,seconds=1.55,opacity=1.0,style="simple",stack_gap=4):
    """Show separate portrait pairs as a compact stacked kill feed (max 3 rows)."""
    if not graph.endswith("[vout]"):
        raise ValueError("Existing video graph has no [vout]")
    if not badges:
        return graph
    position, scale, seconds, opacity = normalize_options(position, scale, seconds, opacity)
    planned=badge_plan(badges,duration,seconds)
    if not planned:
        return graph
    parts=[graph[:-6]+"[pair_src_0]"]
    x="W-w-32" if position.startswith("right") else "32"
    for n,entry in enumerate(planned):
        idx,t=entry['index'],entry['time']
        start,end=entry['start'],entry['end']
        row=entry['row']
        step=int(round(116*scale + max(0, min(36, int(stack_gap)))))
        y=(f"62+{step*row}" if position.endswith('top') else f"H-h-62-{step*row}")
        extra=(f"+7*sin(35*(t-{t:.3f}))*exp(-11*abs(t-{t:.3f}))" if normalize(style)=="impact" else "")
        inlabel=f"pair_src_{n}"
        outlabel="vout" if n==len(planned)-1 else f"pair_src_{n+1}"
        parts.append(f"[{int(badge_input)+idx}:v]format=rgba,scale=w='trunc(iw*{scale:.3f}/2)*2':h='trunc(ih*{scale:.3f}/2)*2',colorchannelmixer=aa={opacity:.3f}[pair_img_{n}]")
        parts.append(f"[{inlabel}][pair_img_{n}]overlay=x='{x+extra}':y='{y}':format=auto:shortest=0:eof_action=repeat:enable='between(t,{start:.3f},{end:.3f})'[{outlabel}]")
    parts[-1]=parts[-1].replace('[vout]','[pair_finished]')
    parts.append('[pair_finished]format=yuv420p[vout]')
    return ';'.join(parts)


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
