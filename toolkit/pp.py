"""The Pixel Paddock (dark) v2 — baseline-aligned text, 5 px layout grid.
Headlines/labels: 5 px glyph pixels. Body: Jersey 10 at 3 px glyph pixels (readability).
All x positions and baselines snap to the 5 px grid."""
import os, random
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(D, "fonts")
W, H, G = 1080, 1350, 5
FONTS = {  # name: (path, size where 1 design px = 1 px, glyph scale)
    "head": (f"{FD}/fontsource-press-start-2p-5.3.0/files/press-start-2p-latin-400-normal.woff", 8, 5),
    "label": (f"{FD}/fontsource-silkscreen-5.3.0/files/silkscreen-latin-400-normal.woff", 8, 5),
    "labelb": (f"{FD}/fontsource-silkscreen-5.3.0/files/silkscreen-latin-700-normal.woff", 8, 5),
    "body": (f"{FD}/fontsource-jersey-10-5.3.0/files/jersey-10-latin-400-normal.woff", 18.6667, 3),
}
C = dict(paper=(20, 18, 15), speck=(27, 24, 20), box=(31, 27, 22), ink=(236, 227, 207),
         mute=(184, 173, 150), rule=(58, 53, 44), red=(57, 255, 20), onred=(20, 18, 15), signal=(232, 35, 63))


def _f(n):
    p, s, sc = FONTS[n]; return ImageFont.truetype(p, s), sc


def snap(v): return int(round(v / G)) * G


def tlen(n, t):
    f, sc = _f(n)
    return int(round(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(t, font=f))) * sc


def cap(n):
    """cap height in output px"""
    f, sc = _f(n)
    m = Image.new("L", (40, 40)); d = ImageDraw.Draw(m); d.fontmode = "1"; d.text((0, 30), "H", font=f, fill=255, anchor="ls")
    bb = m.getbbox(); return (bb[3] - bb[1]) * sc


def text(im, x, base, t, n, col):
    """draw t with its BASELINE at y=base (snapped to grid)."""
    f, sc = _f(n); asc, desc = f.getmetrics()
    w = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(t, font=f)) + 4; h = asc + desc + 4
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m); d.fontmode = "1"
    d.text((0, asc), t, font=f, fill=255, anchor="ls")
    m = m.point(lambda v: 255 if v > 127 else 0).resize((w * sc, h * sc), Image.NEAREST)
    im.paste(Image.new("RGB", m.size, col), (snap(x), snap(base) - asc * sc), m)


def wrap(n, t, maxw):
    out, cur = [], ""
    for w in t.split():
        x = (cur + " " + w).strip()
        if tlen(n, x) <= maxw: cur = x
        else: out.append(cur); cur = w
    return out + [cur]


def para(im, x, top, t, n, col, maxw, lh):
    """paragraph whose first line's cap top sits at `top`; returns y just below last line's baseline"""
    base = snap(top + cap(n))
    for ln in wrap(n, t, maxw):
        text(im, x, base, ln, n, col); base += lh
    return base - lh


def R(d, x0, y0, x1, y1, c): d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=c)


# --- page furniture -------------------------------------------------------
HEAD_LH, BODY_LH = 60, 45
HEAD_TOP = 205  # headline cap top: 30 px below the strap rule


def base_page(n, total, date, section=None):
    im = Image.new("RGB", (W, H), C["paper"]); d = ImageDraw.Draw(im); r = random.Random(n)
    for _ in range(1500):
        x, y = r.randrange(0, W, G), r.randrange(0, H, G); R(d, x, y, x + G, y + G, C["speck"])
    text(im, 40, 70, "THE PIXEL PADDOCK", "head", C["ink"])          # cap 35 -> top 35
    R(d, 40, 90, W - 40, 95, C["ink"]); R(d, 40, 100, W - 40, 105, C["ink"])
    # strap: 20 px gap above (105->125 cap top) and below (150 baseline -> 170 rule)
    text(im, 40, 150, "F1 NEWS", "label", C["red"])
    s = f"{date} · {n}/{total}"; text(im, W - 40 - tlen("label", s), 150, s, "label", C["mute"])
    R(d, 40, 170, W - 40, 175, C["mute"])
    return im, d


def footer(im, d, txt):
    R(d, 40, H - 90, W - 40, H - 85, C["ink"])
    text(im, 40, H - 40, txt, "label", C["ink"])
    for i in range(6):
        for j in range(2):
            if (i + j) % 2 == 0: R(d, W - 130 + i * 15, H - 70 + j * 15, W - 115 + i * 15, H - 55 + j * 15, C["ink"])


def headline(im, top, t):
    return para(im, 40, top, t, "head", C["ink"], 1000, HEAD_LH)


def body(im, top, t, col=None, maxw=1000, x=40):
    return para(im, x, top, t, "body", col or C["ink"], maxw, BODY_LH)


def framed(im, scene, x, y, s=5):
    d = ImageDraw.Draw(im); big = scene.resize((scene.width * s, scene.height * s), Image.NEAREST)
    R(d, x - 10, y - 10, x + big.width + 10, y + big.height + 10, C["ink"])
    R(d, x - 5, y - 5, x + big.width + 5, y + big.height + 5, (0, 0, 0))
    im.paste(big, (x, y)); return y + big.height + 10


def fig(im, base, caption, n=1):
    lab = f"FIG.{n}"; text(im, 40, base, lab, "label", C["red"])
    text(im, 40 + tlen("label", lab) + 20, base, caption, "body", C["ink"])


def fact_file(im, d, top, rows, title="FACT FILE"):
    h = 85 + 50 * len(rows)
    R(d, 40, top, W - 40, top + h, C["ink"]); R(d, 45, top + 5, W - 45, top + h - 5, C["box"])
    text(im, 70, top + 50, title, "labelb", C["red"])
    base = top + 100
    for k, v in rows:
        text(im, 70, base, k, "label", C["mute"]); text(im, 400, base, v, "body", C["ink"]); base += 50
    return top + h


def contact_sheet(paths, out):
    sh = Image.new("RGB", (len(paths) * 550 + 10, 695), (60, 60, 60))
    for i, p in enumerate(paths):
        sh.paste(Image.open(p).resize((540, 675)), (10 + i * 550, 10))
    sh.save(out)
