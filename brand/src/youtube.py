"""YouTube channel kit: profile picture (800x800), banner (2560x1440), video watermark (150x150).
Uses the final logo mark from logo6 (pixel P, double ring, green full stop).
Run: cd brand/src && python3 youtube.py  -> writes to ../youtube/"""
import os, json, random
from PIL import Image, ImageDraw, ImageFont
from logo import PAPER, INK
from logo4 import P_ROWS, GREEN
from logo5 import midpoint_circle

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "..", "youtube"); os.makedirs(OUT, exist_ok=True)
FD = os.path.join(D, "..", "..", "toolkit", "fonts")
GEO = os.path.join(D, "..", "..", "toolkit", "geo")
HEAD = f"{FD}/fontsource-press-start-2p-5.3.0/files/press-start-2p-latin-400-normal.woff"
LAB = f"{FD}/fontsource-silkscreen-5.3.0/files/silkscreen-latin-400-normal.woff"
LABB = f"{FD}/fontsource-silkscreen-5.3.0/files/silkscreen-latin-700-normal.woff"
SPECK = (27, 24, 20); RULE = (58, 53, 44); MUTE = (184, 173, 150); BOX = (31, 27, 22)


def mark_cells(n=71):
    """the logo mark at 1 px per cell (same geometry as logo6.mark(GREEN, 'stop'))"""
    im = Image.new("RGB", (n, n), PAPER); d = ImageDraw.Draw(im); c = n // 2
    midpoint_circle(d, c, c, 32, INK); midpoint_circle(d, c, c, 30, INK)
    w, h = 26, 40; ox, oy = c - w // 2 + 1, c - h // 2
    for j, row in enumerate(P_ROWS):
        for i, b in enumerate(row):
            if b == "1": d.rectangle([ox + 2 * i, oy + 2 * j, ox + 2 * i + 1, oy + 2 * j + 1], fill=INK)
    d.rectangle([ox + 12, oy + h - 4, ox + 15, oy + h - 1], fill=GREEN)
    return im


def disc_mask(n, r):
    m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).ellipse([n / 2 - r, n / 2 - r, n / 2 + r, n / 2 + r], fill=255)
    return m


def text(im, x, base, t, path, size, sc, col, anchor="ls"):
    f = ImageFont.truetype(path, size); asc, desc = f.getmetrics()
    w = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(t, font=f)) + 4; h = asc + desc + 4
    m = Image.new("L", (w, h), 0); dd = ImageDraw.Draw(m); dd.fontmode = "1"
    dd.text((0, asc), t, font=f, fill=255, anchor="ls")
    m = m.point(lambda v: 255 if v > 127 else 0)
    bb = m.getbbox(); m = m.crop((bb[0], 0, bb[2], h)).resize(((bb[2] - bb[0]) * sc, h * sc), Image.NEAREST)
    if anchor == "ms": x -= m.width // 2
    im.paste(Image.new("RGB", m.size, col), (x, base - asc * sc), m)
    return m.width


def tw(t, path, size, sc):
    m = Image.new("L", (2000, 60)); dd = ImageDraw.Draw(m); dd.fontmode = "1"
    dd.text((0, 40), t, font=ImageFont.truetype(path, size), fill=255, anchor="ls"); bb = m.getbbox()
    return (bb[2] - bb[0]) * sc


def track(im, key, cx, cy, size, col, px=5, rot=0):
    import math
    g = json.load(open(f"{GEO}/{key}.geojson")); f = g["features"][0]["geometry"]
    pts = f["coordinates"] if f["type"] == "LineString" else f["coordinates"][0]
    lat0 = sum(p[1] for p in pts) / len(pts)
    xy = [(p[0] * math.cos(math.radians(lat0)), -p[1]) for p in pts]
    a = math.radians(rot); xy = [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in xy]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]; s = size / max(max(xs) - min(xs), max(ys) - min(ys))
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    d = ImageDraw.Draw(im); prev = None
    for x, y in xy + xy[:1]:
        q = (int((cx + (x - mx) * s) // px) * px, int((cy + (y - my) * s) // px) * px)
        if prev:  # pixel-stepped line
            n = max(abs(q[0] - prev[0]), abs(q[1] - prev[1])) // px + 1
            for k in range(n + 1):
                u = (int((prev[0] + (q[0] - prev[0]) * k / n) // px) * px, int((prev[1] + (q[1] - prev[1]) * k / n) // px) * px)
                d.rectangle([u[0], u[1], u[0] + px - 1, u[1] + px - 1], fill=col)
        prev = q


def profile():
    m = mark_cells(); S = 11
    out = Image.new("RGB", (800, 800), PAPER); big = m.resize((71 * S, 71 * S), Image.NEAREST)
    out.paste(big, ((800 - big.width) // 2, (800 - big.height) // 2)); out.save(f"{OUT}/yt_profile_800.png")


def watermark():
    m = mark_cells(); big = m.resize((142, 142), Image.NEAREST)
    out = Image.new("RGBA", (150, 150), (0, 0, 0, 0)); out.paste(big, (4, 4))
    out.putalpha(disc_mask(150, 74)); out.save(f"{OUT}/yt_watermark_150.png")


def banner():
    W, H = 2560, 1440; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(9000):
        x, y = rnd.randrange(0, W, 5), rnd.randrange(0, H, 5); d.rectangle([x, y, x + 4, y + 4], fill=SPECK)
    # faint track outlines outside the safe area (only visible on TV/desktop)
    track(im, "jp", 270, 720, 340, RULE, rot=0)
    track(im, "br", W - 270, 720, 330, RULE, rot=0)
    # safe area: 1546 x 423 centred
    sx, sy, sw, sh = (W - 1546) // 2, (H - 423) // 2, 1546, 423
    # pixel chequer strips above/below the safe area
    for row, yy in enumerate((sy - 40, sy + sh + 20)):
        for i in range(0, sw, 20):
            for r in range(2):
                if ((i // 20) + r + row) % 2 == 0: d.rectangle([sx + i, yy + r * 10, sx + i + 9, yy + r * 10 + 9], fill=RULE)
    # logo mark
    m = mark_cells().resize((71 * 5, 71 * 5), Image.NEAREST)
    mk = Image.new("RGB", m.size, PAPER); mk.paste(m, (0, 0))
    im.paste(mk, (sx + 20, sy + (sh - 355) // 2), disc_mask(355, 176))
    # wordmark + tagline
    tx = sx + 20 + 355 + 70
    text(im, tx, sy + 120, "F1 HISTORY + NEWS", LABB, 8, 5, GREEN)
    text(im, tx, sy + 225, "THE PIXEL", HEAD, 8, 9, INK)
    pw = text(im, tx, sy + 315, "PADDOCK", HEAD, 8, 9, INK)
    dot_x = tx + pw + 18  # green square full stop, as in the logo
    d.rectangle([dot_x, sy + 315 - 18, dot_x + 17, sy + 315 - 1], fill=GREEN)
    text(im, tx, sy + 385, "RACES REPLAYED IN PIXELS · VERIFIED FACTS", LAB, 8, 4, MUTE)
    im.save(f"{OUT}/yt_banner_2560x1440.png")
    # previews: how it crops on phone / desktop
    pv = im.copy(); pd = ImageDraw.Draw(pv)
    pd.rectangle([sx, sy, sx + sw, sy + sh], outline=(232, 35, 63), width=6)
    pd.rectangle([0, (H - 423) // 2, W, (H + 423) // 2], outline=(56, 189, 248), width=4)
    pv.resize((1280, 720), Image.NEAREST).save(f"{OUT}/preview_banner_safearea.png")


if __name__ == "__main__":
    profile(); watermark(); banner(); print("ok")
