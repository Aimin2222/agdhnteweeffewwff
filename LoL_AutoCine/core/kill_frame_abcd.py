# -*- coding: utf-8 -*-
"""A/B/C/D kill frames. D uses pixels cropped from the user's ORIGINAL concept boards.

The composite concept boards contain example faces and captions: never draw the
entire board over gameplay. Extract its central ornamental artwork only, and
supply the true match portraits through the existing DDragon icon pipeline.
No preview stand-ins silently replace a missing original concept board.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re
import shutil
import unicodedata

@dataclass(frozen=True)
class Theme:
    code: str
    name: str
    group: str
    aliases: tuple[str, ...]
    color: tuple[int, int, int]
    intro: str

def _t(code, name, group, aliases, color, intro="pop"):
    return Theme(code, name, group, tuple(aliases), color, intro)

THEMES = (
    # Names track actual AutoCine concept boards generated in this chat.
    _t("demacia","デマーシア","出身",["demacia"],(224,190,104),"slide_up"),
    _t("noxus","ノクサス","出身",["noxus"],(226,64,76),"slide_left"),
    _t("ionia","アイオニア","出身",["ionia"],(245,152,194),"slide_up"),
    _t("freljord","フレヨルド","出身",["freljord"],(111,203,255),"slide_down"),
    _t("piltover","ピルトーヴァー","出身",["piltover"],(233,191,112),"slide_right"),
    _t("zaun","ザウン","出身",["zaun"],(111,229,80),"slide_left"),
    _t("bilgewater","ビルジウォーター","出身",["bilgewater"],(88,193,207),"slide_up"),
    _t("shurima","シュリーマ","出身",["shurima"],(238,184,81),"pop"),
    _t("targon","ターゴン","出身",["targon"],(188,150,250),"slide_up"),
    _t("void","ヴォイド","出身",["void"],(194,73,252),"pop"),
    _t("ixtal","イクスタル","出身",["ixtal"],(77,206,135),"pop"),
    _t("shadow_isles","シャドウアイル","出身",["shadowisles"],(85,229,204),"slide_down"),
    _t("bandle_city","バンドルシティ","出身",["bandlecity"],(250,192,101),"pop"),
    _t("project","PROJECT","スキン",["project"],(247,77,141),"slide_left"),
    _t("star_guardian","スターガーディアン","スキン",["starguardian"],(255,164,230),"pop"),
    _t("kda","K/DA","スキン",["k_da","kda"],(246,115,215),"pop"),
    _t("heartsteel","ハートスティール","スキン",["heartsteel"],(234,78,91),"slide_left"),
    _t("spirit_blossom","スピリットブロッサム","スキン",["spiritblossom"],(248,164,213),"slide_up"),
    _t("dark_star","ダークスター","スキン",["darkstar"],(167,81,237),"pop"),
    _t("high_noon","ハイヌーン","スキン",["highnoon"],(253,147,50),"slide_right"),
    _t("blood_moon","血月","スキン",["bloodmoon"],(233,65,73),"pop"),
    _t("warring_kingdoms","覇王","スキン",["warringkingdoms"],(238,181,83),"slide_up"),
    _t("pool_party","プールパーティー","スキン",["poolparty"],(69,207,252),"pop"),
    _t("soul_fighter","ソウルファイター","スキン",["soulfighter"],(247,95,210),"pop"),
    _t("odyssey","オデッセイ","スキン",["odyssey"],(106,173,250),"slide_right"),
    _t("winter_festival","冬の祝祭","スキン",["snowdown","winterfestival"],(133,197,255),"pop"),
    _t("battle_academia","バトルアカデミア","スキン",["battleacademia"],(89,145,250),"slide_up"),
    _t("arcana","アルカナ","スキン",["arcana"],(221,175,119),"pop"),
    _t("coven","コヴェン","スキン",["coven"],(186,82,93),"slide_down"),
    _t("eclipse","エクリプス","スキン",["eclipse"],(250,175,89),"pop"),
    _t("elderwood","エルダウッド","スキン",["elderwood"],(98,224,171),"slide_up"),
    _t("cosmic","コズミック","スキン",["cosmic"],(136,181,254),"pop"),
    _t("dark_cosmic","ダークコズミック","スキン",["darkcosmic"],(181,91,250),"pop"),
    _t("dawnbringer","ドーンブリンガー","スキン",["dawnbringer"],(239,200,118),"slide_up"),
    _t("nightbringer","ナイトブリンガー","スキン",["nightbringer"],(253,92,71),"slide_down"),
    _t("infernal","インフェルナル","スキン",["infernal"],(254,139,53),"pop"),
    _t("arcade","アーケード","スキン",["arcade"],(100,231,255),"pop"),
    _t("bewitching","ビウィッチング","スキン",["bewitching"],(249,134,216),"slide_up"),
    _t("porcelain","磁器","スキン",["porcelain"],(131,185,255),"pop"),
    _t("psyops","PsyOps","スキン",["psyops","サイオプス"],(183,104,251),"slide_left"),
    _t("steel_valkyries","スティールヴァルキリーズ","スキン",["steelvalkyries"],(130,205,252),"slide_up"),
    _t("broken_covenant","ブロークンコヴェナント","スキン",["brokencovenant"],(236,100,110),"slide_down"),
    _t("faerie_court","フェアリーコート","スキン",["faeriecourt"],(238,152,212),"pop"),
    _t("space_groove","スペースグルーヴ","スキン",["spacegroove"],(107,223,250),"pop"),
    _t("ocean_song","オーシャンソング","スキン",["oceansong"],(74,207,244),"slide_up"),
    _t("mecha_kingdoms","メカキングダムズ","スキン",["mechakingdoms"],(252,172,91),"slide_right"),
    _t("dragonmancer","ドラゴンマンサー","スキン",["dragonmancer"],(87,194,255),"pop"),
    _t("shan_hai","山海絵巻","スキン",["shanhaiscrolls","山海絵巻"],(216,172,111),"slide_up"),
    _t("mecha","メカ","スキン",["mecha"],(89,192,252),"slide_right"),
    _t("battlecast","バトルキャスト","スキン",["battlecast"],(252,93,70),"slide_left"),
)
BY_CODE = {t.code:t for t in THEMES}
MARKS = ("melee", "ranged", "hybrid")
STRENGTHS = ("weak", "strong")
ABCD = {"abc_a":"A｜超シンプル", "abc_b":"B｜シンプル高級感", "abc_c":"C｜シネマ衝突"}

def boards_dir():
    return Path(__file__).resolve().parent.parent / "assets" / "kill_concept_boards"

def _style_parts(style):
    m = re.fullmatch(r"d_([a-z0-9_]+)_(weak|strong)", str(style))
    if m and m.group(1) in BY_CODE:
        return BY_CODE[m.group(1)],m.group(2)
    return None

def installed_theme_styles():
    """Only advertise D styles which have a real user-board source image."""
    result={}
    for t in THEMES:
        if (boards_dir() / (t.code+".png")).is_file():
            for power in STRENGTHS:
                result[f"d_{t.code}_{power}"] = f"D｜{t.name}｜{'装飾弱め' if power=='weak' else '装飾強め'}"
    return result

def normalize_board_name(name):
    x=unicodedata.normalize("NFKC",str(name)).casefold()
    return re.sub(r"[\s_\-./\\（）()\[\]]+","",x)

def recognize_board(filename):
    """Use precise long aliases first (e.g. Dark Cosmic before Cosmic)."""
    key=normalize_board_name(Path(filename).stem)
    aliases=[]
    for theme in THEMES:
        for alias in (theme.name, theme.code, *theme.aliases):
            aliases.append((normalize_board_name(alias),theme.code))
    for match,code in sorted(aliases,key=lambda v:len(v[0]),reverse=True):
        if match and match in key:
            return code
    return None

def install_concept_board(source, theme_code=None):
    """Preserve the EXACT uploaded PNG pixels; no generative redraw or substitution."""
    from PIL import Image
    source=Path(source)
    code=theme_code or recognize_board(source.name)
    if code not in BY_CODE:
        raise ValueError("テーマを識別できません。日本語テーマ名をファイル名に入れてください。")
    if source.suffix.lower() not in (".png",".webp",".jpg",".jpeg"):
        raise ValueError("PNG/JPG/WEBPのデザインボードを選んでください")
    if source.stat().st_size > 30_000_000:
        raise ValueError("画像が30MBを超えています")
    with Image.open(source) as im:
        im.verify()
    with Image.open(source) as im:
        if im.width < 700 or im.height < 600:
            raise ValueError("元ボード画像が小さすぎます (700x600以上)")
        rgba=im.convert("RGBA")
    dst=boards_dir()/(code+".png")
    dst.parent.mkdir(parents=True,exist_ok=True)
    # Save copy of the ORIGINAL full concept image as lossless PNG.
    rgba.save(dst,format="PNG")
    return code,dst

def _clip_float(x,lo,hi):
    try:
        n=float(x)
        if math.isfinite(n): return max(lo,min(hi,n))
    except (TypeError,ValueError,OverflowError): pass
    return lo

def _clip_xy(im, centre, size):
    x,y=centre; w,h=size
    return im.crop((round((x-w/2)*im.width),round((y-h/2)*im.height),
                    round((x+w/2)*im.width),round((y+h/2)*im.height)))

def _cut_board_motif(board, strong, kind):
    """Extract decoration pixels from original concept board. Faces/captions excluded.

    The default areas match the real 2-column concept-sheet layout used in
    this chat. The lower part contains melee/ranged/hybrid motif variations.
    Image processing only removes uniform surrounding panel color.
    """
    from PIL import Image,ImageChops,ImageEnhance,ImageFilter
    if kind in MARKS:
        cx={"melee":.165,"ranged":.50,"hybrid":.835}[kind]
        part=_clip_xy(board,(cx,.875),(.11,.14))
    else:
        part=_clip_xy(board,(.707 if strong else .233,.31),(.125,.13))
    part=part.convert("RGBA")
    if part.getbbox() is None:
        raise ValueError("コンセプトボードの中央装飾が空です")
    # Edges of the crop are typically flat dark/white plate, not the emblem.
    corners=[part.getpixel((x,y))[:3] for x,y in ((0,0),(part.width-1,0),(0,part.height-1),(part.width-1,part.height-1))]
    bg=tuple(sorted(c[i] for c in corners)[2] for i in range(3))
    solid=Image.new("RGB",part.size,bg)
    delta=ImageChops.difference(part.convert("RGB"),solid).convert("L")
    # Dark-on-white, gold-on-blue and luminous-on-black all work without
    # replacing the concept artwork with generated line art.
    alpha=delta.point(lambda p:max(0,min(255,int((p-18)*5))))
    alpha=alpha.filter(ImageFilter.GaussianBlur(.6))
    if part.getextrema()[3] != (255,255):
        alpha=ImageChops.multiply(alpha,part.getchannel("A"))
    part.putalpha(alpha)
    return part

def _paste_fit(canvas,layer,box):
    from PIL import Image
    x,y,w,h=box
    layer=layer.copy()
    layer.thumbnail((w,h),Image.Resampling.LANCZOS)
    canvas.alpha_composite(layer,(x+(w-layer.width)//2,y+(h-layer.height)//2))

def _portrait(canvas,source,rect):
    from PIL import Image,ImageDraw,ImageOps
    if source is None:return
    x,y,size=rect
    with Image.open(source) as im:
        pic=ImageOps.fit(im.convert("RGBA"),(size,size),method=Image.Resampling.LANCZOS)
    mask=Image.new("L",(size,size))
    ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    pic.putalpha(mask)
    canvas.alpha_composite(pic,(x,y))

def render_abcd_badge(path, style, *, killer_icon=None,victim_icon=None,
                      mark_style="auto", glow_strength=.85, glow_enabled=True,
                      frame_color="",glow_color="",hires=False,**ignored):
    """Render a usable transparent badge; D *requires* the real board PNG."""
    from PIL import Image,ImageDraw,ImageFilter
    from core.kill_icons import valid_hex
    selected=_style_parts(style)
    if selected:
        theme,level=selected
        board_path=boards_dir()/(theme.code+".png")
        if not board_path.is_file():
            raise FileNotFoundError(f"元デザイン画像がありません: {board_path}")
        with Image.open(board_path) as src:board=src.convert("RGBA")
        rgb=theme.color
    elif style in ABCD:
        board=None
        level={"abc_a":"weak","abc_b":"weak","abc_c":"strong"}[style]
        rgb={"abc_a":(200,213,225),"abc_b":(243,197,102),"abc_c":(125,209,255)}[style]
    else:
        raise ValueError(f"Unknown A/B/C/D style: {style}")
    if valid_hex(frame_color):rgb=tuple(bytes.fromhex(frame_color[1:]))
    lum=tuple(min(255,int(v+max(0,255-v)*.44)) for v in rgb)
    factor=2 if hires else 1
    w,h=385*factor,116*factor
    canvas=Image.new("RGBA",(w,h),(0,0,0,0))
    glow=_clip_float(glow_strength,0,2) if glow_enabled else 0
    paint=ImageDraw.Draw(canvas)
    def r(rect):return tuple(int(round(v*factor)) for v in rect)
    for x in (44,273):
        rect=r((x-5,19,x+73,100))
        if level=="strong" or style=="abc_b":
            paint.rounded_rectangle(r((x-12,12,x+80,107)),radius=10*factor,fill=(5,10,23,105),outline=(*rgb,180),width=2*factor)
        paint.ellipse(rect,fill=(11,15,24,220),outline=(*rgb,255),width=(3 if level=="strong" else 2)*factor)
    _portrait(canvas,killer_icon,(44*factor,24*factor,68*factor))
    _portrait(canvas,victim_icon,(273*factor,24*factor,68*factor))
    paint=ImageDraw.Draw(canvas)
    for x in (44,273):
        paint.ellipse(r((x-2,22,x+70,94)),outline=(*lum,250),width=2*factor)
    # Strong designs may extend decorative arcs; keep character faces clear.
    if style=="abc_a":
        paint.line(r((171,34,213,82)),fill=(*rgb,255),width=3*factor)
        paint.line(r((213,34,171,82)),fill=(252,252,255,255),width=3*factor)
    elif style=="abc_b":
        paint.line(r((164,57,220,57)),fill=(*rgb,210),width=2*factor)
        for p in ((171,35,213,82),(213,35,171,82)):
            paint.line(r(p),fill=(*lum,255),width=5*factor)
        paint.polygon([tuple(int(t*factor) for t in pt) for pt in ((192,32),(201,57),(192,84),(183,57))],outline=(*rgb,245))
        paint.ellipse(r((188,54,196,62)),fill=(255,250,233,255))
    elif style=="abc_c":
        for a,b in ((156,34),(218,82),(156,82),(218,34)):
            paint.line(r((a,b,192,58)),fill=(*rgb,170),width=4*factor)
        paint.line(r((163,25,221,91)),fill=(253,237,248,255),width=7*factor)
        paint.line(r((221,25,163,91)),fill=(*rgb,255),width=7*factor)
        for px,py in ((160,27),(225,83),(161,83),(224,27)):
            paint.ellipse(r((px-3,py-3,px+3,py+3)),fill=(*lum,255))
    else:
        # The ornament is a crop of the original board, NOT a redrawn motif.
        kind={"theme_melee":"melee","theme_ranged":"ranged","theme_hybrid":"hybrid"}.get(mark_style)
        ornament=_cut_board_motif(board,level=="strong",kind)
        # Some concept boards are designed for very large centre features;
        # resize only (do not paint over faces or static example text).
        _paste_fit(canvas,ornament,r((153,13,78,90)))
    if glow:
        aura=canvas.filter(ImageFilter.GaussianBlur(max(1,int(4*factor*glow))))
        aura.putalpha(aura.getchannel("A").point(lambda a:min(175,int(a*glow*.42))))
        canvas=Image.alpha_composite(aura,canvas)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path,format="PNG")
    return Path(path)

def theme_intro_motion(style, selected_motion):
    """Per-theme entry personality, without changing the GPU/audio engine."""
    if selected_motion!="instant":return selected_motion
    s=_style_parts(style)
    if s:return s[0].intro
    if style=="abc_b":return "slide_up"
    if style=="abc_c":return "pop"
    return "instant"
