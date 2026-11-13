"""Pixel Paddock Historic Race Recap: top-down MAP REPLAY engine (v2).

Real circuit layout (bacinger/f1-circuits GeoJSON), top-down era cars, readable text panels.
v2 changes:
- Time skips are full-screen "LAP XX / YY" cards; inside a scene the cars move at a believable speed.
- Everything important sits inside the YouTube Shorts safe zone (bottom and right edge stay free
  for channel name, caption and the like/comment buttons). No timeline bar at the bottom.
- Results: animated timing board (rows flip in from the back to P1) plus a grid-vs-finish slope chart.
"""
import os, sys, math, json, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from font3 import FONT3
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out_short"); os.makedirs(OUT, exist_ok=True)
NW, NH, SC, FPS, SR = 135, 240, 8, 30, 44100
# YouTube Shorts safe zone in logical pixels (1 px = 8 video px): keep text and key action inside it.
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 6, 129, 8, 172
YT_X = 114   # below y=120 the YouTube like/comment buttons sit right of this
CX = (SAFE_X0 + SAFE_X1) // 2
for k, v in {":": "000010000010000", "'": "010010000000000", ",": "000000000010100", ".": "000000000000010", "+": "000010111010000",
             "-": "000000111000000", "!": "010010010000010", "/": "001001010100100", "Q": "010101101110011", "?": "111001011000010", "Z": "111001010100111"}.items():
    FONT3.setdefault(k, v)
INK, MUT, YEL, GRN, RED = (243, 244, 246), (148, 163, 184), (242, 201, 76), (57, 255, 20), (239, 68, 68)
BG = (10, 12, 20); EDGE = (52, 60, 86); PANEL = (6, 8, 16)

def tx(d, x, y, s, c, sc=1):
    for ch in s.upper():
        g = FONT3.get(ch)
        if g:
            for j in range(5):
                for i in range(3):
                    if g[j * 3 + i] == "1": d.rectangle([x + i * sc, y + j * sc, x + i * sc + sc - 1, y + j * sc + sc - 1], fill=c)
        x += 4 * sc
def tw(s, sc=1): return len(s) * 4 * sc - sc
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def tri(d, x, y, up, col):
    if up: d.polygon([(x, y + 4), (x + 4, y + 4), (x + 2, y)], fill=col)
    else: d.polygon([(x, y), (x + 4, y), (x + 2, y + 4)], fill=col)

# ---------------- top-down cars (x forward, y right; units = car lengths) ----------------
def rect(x0, x1, y0, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def car_shapes(L):
    T = (16, 16, 18)
    s = [(T, rect(.27, .40, .13, .23)), (T, rect(.27, .40, -.23, -.13)), (T, rect(-.43, -.27, .13, .24)), (T, rect(-.43, -.27, -.24, -.13)),
         (L["fwing"], rect(.43, .50, -.22, .22)), (L["nose"], [(.50, -.03), (.50, .03), (.12, .07), (.12, -.07)]),
         (L["pod"], [(-.22, -.18), (.08, -.15), (.10, -.08), (-.22, -.08)]), (L["pod"], [(-.22, .18), (.08, .15), (.10, .08), (-.22, .08)]),
         (L["body"], rect(-.30, .14, -.08, .08)), (L["air"], [(-.36, -.04), (-.36, .04), (.0, .06), (.0, -.06)]),
         (L["rwing"], rect(-.50, -.43, -.19, .19))]
    if "accent" in L: s.append((L["accent"], rect(-.10, .04, -.08, -.05))); s.append((L["accent"], rect(-.10, .04, .05, .08)))
    return s
TEAMS = {
    # 1991. McLaren MP4/6: luminous red over white. Williams FW14: blue nose/monocoque, white sidepods, yellow airbox.
    "MCL91": dict(fwing=(238, 46, 44), nose=(238, 46, 44), pod=(238, 46, 44), body=(244, 244, 244), air=(238, 46, 44), rwing=(238, 46, 44)),
    "WIL91": dict(fwing=(30, 62, 150), nose=(30, 62, 150), pod=(244, 244, 244), body=(30, 62, 150), air=(246, 196, 0), rwing=(244, 244, 244)),
    "FER91": dict(fwing=(210, 10, 10), nose=(210, 10, 10), pod=(210, 10, 10), body=(210, 10, 10), air=(210, 10, 10), rwing=(210, 10, 10)),
    # 2005. McLaren MP4-20: silver / anthracite with red accents. Renault R25: light blue + yellow.
    "MCL05": dict(fwing=(70, 72, 80), nose=(200, 204, 212), pod=(200, 204, 212), body=(70, 72, 80), air=(200, 204, 212), rwing=(70, 72, 80), accent=(232, 50, 40)),
    "REN05": dict(fwing=(40, 120, 200), nose=(250, 200, 0), pod=(40, 120, 200), body=(40, 120, 200), air=(250, 200, 0), rwing=(40, 120, 200)),
    "FER05": dict(fwing=(210, 10, 10), nose=(210, 10, 10), pod=(210, 10, 10), body=(210, 10, 10), air=(210, 10, 10), rwing=(240, 240, 240)),
    "TOY05": dict(fwing=(240, 240, 240), nose=(240, 240, 240), pod=(220, 20, 30), body=(240, 240, 240), air=(240, 240, 240), rwing=(220, 20, 30)),
    "WIL05": dict(fwing=(20, 40, 110), nose=(240, 240, 240), pod=(240, 240, 240), body=(20, 40, 110), air=(240, 240, 240), rwing=(20, 40, 110)),
    "GEN": dict(fwing=(120, 124, 132), nose=(120, 124, 132), pod=(120, 124, 132), body=(120, 124, 132), air=(120, 124, 132), rwing=(120, 124, 132)),
}
def team_col(team):
    # colour used for bars and lines on the dark boards (white pods would read as "no team")
    L = TEAMS[team]; c = L["pod"]
    return L["body"] if sum(c) > 690 else c
def draw_car(d, x, y, ang, team, px, helmet=None):
    ca, sa = math.cos(ang), math.sin(ang)
    for col, poly in car_shapes(TEAMS[team]):
        d.polygon([(x + (u * ca - v * sa) * px, y + (u * sa + v * ca) * px) for u, v in poly], fill=col)
    if helmet and px >= 14:
        hx_, hy_ = x + .02 * ca * px, y + .02 * sa * px
        d.ellipse([hx_ - 1, hy_ - 1, hx_ + 1, hy_ + 1], fill=helmet)

# ---------------- track ----------------
class Track:
    def __init__(self, path, n=1200, rot=0):
        js = json.load(open(path)); co = js['features'][0]['geometry']['coordinates']
        self.length_m = js['features'][0]['properties']['length']
        lat0 = sum(c[1] for c in co) / len(co)
        P = [(lo * math.cos(math.radians(lat0)) * 111320, -la * 110540) for lo, la in co]
        if P[0] == P[-1]: P = P[:-1]
        if rot:
            ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot)); P = [(x * ca - y * sa, x * sa + y * ca) for x, y in P]
        cum = [0]
        for i in range(1, len(P) + 1): cum.append(cum[-1] + math.dist(P[i - 1], P[i % len(P)]))
        self.raw_len = cum[-1]; self.pts = []; j = 0
        for k in range(n):
            s = cum[-1] * k / n
            while cum[j + 1] < s: j += 1
            a, b = P[j], P[(j + 1) % len(P)]; t = (s - cum[j]) / max(1e-6, cum[j + 1] - cum[j])
            self.pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        xs = [p[0] for p in self.pts]; ys = [p[1] for p in self.pts]
        self.cx, self.cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        self.fit = min((SAFE_X1 - SAFE_X0 - 8) / (max(xs) - min(xs)), 112 / (max(ys) - min(ys)))
        self.n = n
    def at(self, frac):
        f = (frac % 1) * self.n; i = int(f); t = f - i
        a, b = self.pts[i % self.n], self.pts[(i + 1) % self.n]
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    def heading(self, frac):
        a = self.at(frac - .002); b = self.at(frac + .002); return math.atan2(b[1] - a[1], b[0] - a[0])

MAP_CY = 116
def project(tr, cam, p):
    cx, cy, z = cam; s = tr.fit * z
    return CX + (p[0] - cx) * s, MAP_CY + (p[1] - cy) * s

# Real-world sizes per circuit (set by render from the race config). Track width is chosen below the
# smallest gap between two separate parts of the circuit, so sections never merge at any zoom.
# Car length = track width / 1.25, so two cars fit side by side. Zoom only changes how big it all looks.
SIZE = {"track_m": 26.0, "car_m": 21.0, "fit": .1}
def car_px(z): return max(5.0, SIZE["car_m"] * SIZE["fit"] * z)
def track_w(z): return max(3, int(round(SIZE["track_m"] * SIZE["fit"] * z)))
def lat_half(z):
    """screen offset for lat = +-1 (car centre at the track edge minus half a car width)"""
    return max(.5, track_w(z) / 2 - car_px(z) * .25)
def zoom_for(R, px):
    """zoom at which a car is px logical pixels long"""
    tr = Track(R["geo"], rot=R.get("rot", 0)); return px / (R["car_m"] * tr.fit)

_GX, _GY = np.meshgrid(np.arange(NW) + .5, np.arange(NH) + .5)
_MAP_CACHE = {}
def track_dist(tr, cam, w):
    """Distance (logical px) from every screen pixel to the track centre line. One continuous band,
    no joints, so the asphalt never shows notches or gaps."""
    key = (id(tr), round(cam[0], 2), round(cam[1], 2), round(cam[2], 4))
    if key in _MAP_CACHE: return _MAP_CACHE[key]
    P = np.array([project(tr, cam, p) for p in tr.pts] + [project(tr, cam, tr.pts[0])])
    A, B = P[:-1], P[1:]; m = w / 2 + 3
    keep = ~((np.maximum(A[:, 0], B[:, 0]) < -m) | (np.minimum(A[:, 0], B[:, 0]) > NW + m) |
             (np.maximum(A[:, 1], B[:, 1]) < -m) | (np.minimum(A[:, 1], B[:, 1]) > NH + m))
    A, B = A[keep], B[keep]; D = np.full((NH, NW), 1e9)
    gx, gy = _GX[..., None], _GY[..., None]
    for i in range(0, len(A), 48):
        a_, b_ = A[i:i + 48], B[i:i + 48]; ab = b_ - a_; L2 = np.maximum((ab ** 2).sum(1), 1e-9)
        t = np.clip(((gx - a_[:, 0]) * ab[:, 0] + (gy - a_[:, 1]) * ab[:, 1]) / L2, 0, 1)
        dx = gx - (a_[:, 0] + t * ab[:, 0]); dy = gy - (a_[:, 1] + t * ab[:, 1])
        D = np.minimum(D, np.sqrt(dx * dx + dy * dy).min(-1))
    if len(_MAP_CACHE) > 400: _MAP_CACHE.clear()
    _MAP_CACHE[key] = D
    return D

def draw_map(im, tr, cam, start_frac=0.0, sc_on=False, dim=1.0):
    z = cam[2]; w = track_w(z)
    c = lambda col: tuple(int(v * dim + BG[i] * (1 - dim)) for i, v in enumerate(col))
    D = track_dist(tr, cam, w); a = np.asarray(im).copy()
    a[D <= w / 2 + 1] = c((60, 68, 92))
    a[D <= w / 2] = c((38, 42, 54) if not sc_on else (70, 62, 20))
    if w >= 6: a[D <= .55] = c((48, 54, 70))
    im.paste(Image.fromarray(a)); d = ImageDraw.Draw(im)
    x, y = project(tr, cam, tr.at(start_frac)); h = tr.heading(start_frac) + math.pi / 2
    for k in range(-w // 2 - 1, w // 2 + 2):
        d.point((x + math.cos(h) * k, y + math.sin(h) * k), fill=c(INK) if k % 2 else (20, 20, 20))
    return d

def shade(im, box, k=.2):
    x0, y0, x1, y1 = box
    a = np.asarray(im).astype(float)
    a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * k + np.array(PANEL) * (1 - k)
    return Image.fromarray(a.astype(np.uint8))

def panel(im, lines, y0=24):
    if not lines: return im
    h = sum(5 * s + 5 for _, _, s in lines) + 7
    im = shade(im, (SAFE_X0, y0, SAFE_X1, y0 + h)); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, y0, SAFE_X1 - 1, y0 + h - 1], outline=EDGE)
    y = y0 + 5
    for s, c, sc in lines:
        tx(d, CX - tw(s, sc) // 2, y, s, c, sc); y += 5 * sc + 5
    return im

def typed(lines, f, speed=1.4):
    out = []; budget = f * speed
    for s, c, sc in lines:
        n = int(budget / (1 if sc == 1 else 2)); out.append((s[:max(0, n)] if n < len(s) else s, c, sc)); budget = max(0, budget - len(s) * (1 if sc == 1 else 2))
    return out

def hud(im, lap, laps, leader=None, lead_team=None):
    # compact top strip: lap counter + leader. Nothing at the bottom (YouTube overlays live there).
    im = shade(im, (SAFE_X0, 8, SAFE_X1, 20), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 8, SAFE_X1 - 1, 19], outline=EDGE)
    tx(d, SAFE_X0 + 4, 12, "LAP", MUT); tx(d, SAFE_X0 + 18, 12, f"{lap}/{laps}", INK)
    if leader: d.rectangle([SAFE_X0 + 50, 12, SAFE_X0 + 52, 16], fill=team_col(lead_team)); tx(d, SAFE_X0 + 55, 12, leader, INK)
    return im

# ---------------- full-screen cards ----------------
def lap_card(im, tr, a, b, laps, t, sub=None, marks=()):
    """Time-skip card: lap number rolls from a to b, progress bar shows how far into the race we are."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.25)
    im = shade(im, (0, 0, NW, NH), .35); d = ImageDraw.Draw(im)
    k = ease(min(1, t / .65)); n = int(round(lerp(a, b, k)))
    tx(d, CX - tw("LAP", 2) // 2, 62, "LAP", MUT, 2)
    s = str(n); big = 6; tot = f"/{laps}"
    wbig = tw(s, big); wsm = tw(tot, 2); x0 = CX - (wbig + 3 + wsm) // 2
    tx(d, x0, 80, s, INK if t < .65 else YEL, big); tx(d, x0 + wbig + 3, 100, tot, MUT, 2)
    bx0, bx1, by = CX - 44, CX + 44, 122
    d.rectangle([bx0, by, bx1, by + 3], fill=(30, 34, 48))
    d.rectangle([bx0, by, bx0 + int((bx1 - bx0) * lerp(a, b, k) / laps), by + 3], fill=GRN)
    for m in marks:
        xm = bx0 + int((bx1 - bx0) * m / laps); d.rectangle([xm, by - 2, xm, by + 5], fill=YEL)
    if sub and t > .55: tx(d, CX - tw(sub) // 2, 134, sub, INK)
    return im

def note_card(im, tr, lines, fr, speed=1.2, step=14):
    """Lines pop in one at a time (step frames apart). Big numbers welcome: ("0", YEL, 6)."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.25)
    im = shade(im, (0, 0, NW, NH), .4)
    h = sum(5 * sc + 6 for _, _, sc in lines) + 8
    shown = [(t, c, sc) if fr >= 6 + i * step else ("", c, sc) for i, (t, c, sc) in enumerate(lines)]
    return panel(im, shown, y0=max(30, 96 - h // 2))

def results_board(im, title, rows, extra, fr):
    """Timing board. rows: (pos, name, team, gap, grid). Rows flip in from the back, P1 last, then notes."""
    d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 22, SAFE_X1, 168], fill=(22, 26, 34)); d.rectangle([SAFE_X0 + 3, 25, SAFE_X1 - 3, 165], fill=(4, 14, 8))
    for y in range(26, 165, 3): d.line([(SAFE_X0 + 3, y), (SAFE_X1 - 3, y)], fill=(2, 10, 6))
    G1, G2 = (150, 255, 160), (70, 150, 90)
    tx(d, CX - tw(title) // 2, 30, title, GRN)
    X = CX - 58   # board content was laid out for a centre of 58
    d.line([(X + 10, 39), (X + 106, 39)], fill=(30, 70, 40))
    n = len(rows); start, step = 10, 12
    glyph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for k, (p, name, team, gap, grid) in enumerate(rows):
        order = n - 1 - k                     # back of the field first
        t_in = start + order * step + (12 if k == 0 else 0)
        if fr < t_in: continue
        y = 44 + k * 17; age = fr - t_in
        scramble = age < 8
        def sc_(s): return "".join(glyph[(ord(ch) * 7 + fr * 13 + i * 5) % len(glyph)] if ch != " " and scramble else ch for i, ch in enumerate(s))
        if k == 0 and age > 8 and (fr // 6) % 2 == 0: d.rectangle([X + 9, y - 2, X + 107, y + 13], outline=GRN)
        tx(d, X + 12, y, p, GRN if k == 0 else G1)
        d.rectangle([X + 19, y, X + 20, y + 4], fill=team_col(team))
        tx(d, X + 23, y, sc_(name), INK if k == 0 else G1)
        g = sc_(gap); tx(d, X + 105 - tw(g), y, g, GRN if k == 0 else G1)
        if not scramble and grid:
            delta = grid - int(p)
            tx(d, X + 23, y + 7, f"GRID {grid}", G2)
            if delta:
                col = GRN if delta > 0 else RED; tri(d, X + 60, y + 7, delta > 0, col); tx(d, X + 66, y + 7, str(abs(delta)), col)
            else: d.rectangle([X + 60, y + 9, X + 64, y + 9], fill=G2)
    y = 48 + n * 17; t_ex = start + n * step + 20
    for i, s in enumerate(extra):
        if fr >= t_ex + i * 10: tx(d, CX - tw(s) // 2, y, s, YEL if i == 0 else G2)
        y += 9
    return im

def grid_slot(rows, pos):
    n = max(r[0] for r in rows); step = min(12, 90 / max(1, n - 1)); y0 = 78
    return (CX - 13 if pos % 2 else CX + 13), y0 + (pos - 1) * step

def grid_card(im, tr, rows, fr, fire=None, delay=True):
    """Starting grid as a staggered slot diagram. rows: (pos, code or None, team). Unnamed slots are grey."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.18); d = ImageDraw.Draw(im)
    n = max(r[0] for r in rows); step = min(12, 90 / max(1, n - 1)); y0 = 78
    xl, xr = CX - 13, CX + 13; px = 9 if n > 10 else 12
    d.line([(CX - 22, y0 - 8), (CX + 22, y0 - 8)], fill=INK)
    for k, (pos, code, team) in enumerate(sorted(rows)):
        if delay and fr < 6 + k * 3: continue
        x = xl if pos % 2 else xr; y = y0 + (pos - 1) * step
        d.line([(x - 5, y - px * .55), (x + 5, y - px * .55)], fill=(70, 78, 104))
        draw_car(d, x, y, -math.pi / 2, team if code else "GEN", px)
        num = str(pos)
        if code:
            col = YEL if code.startswith("*") else INK; c = code.lstrip("*")
            if pos % 2: tx(d, x - 9 - tw(c), int(y) - 2, c, col); tx(d, x - 9 - tw(c) - 4 - tw(num), int(y) - 2, num, MUT)
            else: tx(d, x + 9, int(y) - 2, c, col); tx(d, x + 9 + tw(c) + 4, int(y) - 2, num, MUT)
        if fire == pos and fr > 10:
            rr = np.random.default_rng(fr // 2)
            for _ in range(14):
                fx = x + rr.integers(-3, 4); fy = y + px * .15 + rr.integers(-1, 3); hgt = int(rr.integers(2, 7))
                d.line([(fx, fy), (fx + rr.integers(-1, 2), fy - hgt)], fill=[(255, 220, 60), (255, 140, 20), (230, 50, 20)][int(rr.integers(0, 3))])
    return im

def box_size(lines):
    return max(tw(t, sc) for t, _, sc in lines) + 10, sum(5 * sc + 4 for _, _, sc in lines) + 6

def clamp_box(bx0, by0, w, h):
    xmax = (YT_X if by0 + h > 120 else SAFE_X1) - w
    return int(max(SAFE_X0, min(xmax, bx0))), int(by0)

def box_hits(box, avoid, skip=None):
    bx0, by0, w, h = box; n = 0
    for k_, x, y, r in avoid:
        if k_ == skip: r = r * .8
        qx = min(max(x, bx0), bx0 + w); qy = min(max(y, by0), by0 + h)
        if (qx - x) ** 2 + (qy - y) ** 2 < (r + 2) ** 2: n += 1
    return n

def place_callout(anchor, lines, pref, avoid, target):
    """Try above/below and left/centre/right; pick the spot that covers no car and no label."""
    ax, ay = anchor; w, h = box_size(lines); best = None
    for side in (pref, "down" if pref == "up" else "up"):
        for gap in (17, 26, 36, 48):
            for xo in (-w / 2, -w + 14, -14):
                by0 = ay - gap - h if side == "up" else ay + gap
                bx0, by0c = clamp_box(ax + xo, by0, w, h)
                oob = by0 < 24 or by0 + h > SAFE_Y1
                score = box_hits((bx0, by0c, w, h), avoid, target) * 10 + oob * 25 + (side != pref) + (gap - 17) * .03 + (xo != -w / 2) * .3
                if best is None or score < best[0]: best = (score, bx0 - ax, by0c - ay, side)
    return best[1:]

def callout(im, anchor, lines, age, rel):
    """Fact box right next to the action, with a yellow pointer to the car. lines: [(text, colour, scale)]."""
    if age < 0 or not lines: return im, None
    ax, ay = anchor; dx, dy, side = rel
    w, h = box_size(lines)
    bx0, by0 = clamp_box(ax + dx, max(24, min(SAFE_Y1 - h, ay + dy)), w, h)
    k = ease(min(1, age / 5)); wk = max(4, int(w * k))
    cx0 = bx0 + (w - wk) // 2
    im = shade(im, (cx0, by0, cx0 + wk, by0 + h), .12); d = ImageDraw.Draw(im)
    d.rectangle([cx0, by0, cx0 + wk - 1, by0 + h - 1], outline=YEL)
    px_ = min(max(ax, bx0 + 3), bx0 + w - 4)
    if by0 > ay: d.line([(px_, by0 - 1), (ax, ay + 4)], fill=YEL)
    else: d.line([(px_, by0 + h), (ax, ay - 4)], fill=YEL)
    if age >= 5:
        budget = (age - 5) * 3; y = by0 + 4
        for t, c, sc in lines:
            show = t[:max(0, budget)]; budget -= len(t)
            tx(d, bx0 + (w - tw(t, sc)) // 2, y, show, c, sc); y += 5 * sc + 4
    return im, (bx0, by0, w, h)

WARN = {}
def warn(video, seg, msg): WARN.setdefault((video, seg, msg), 0); WARN[(video, seg, msg)] += 1

def headline(im, text, col, age, y=24, sc=2):
    if age < 0: return im
    w = tw(text, sc) + 10
    im = shade(im, (CX - w // 2, y, CX - w // 2 + w, y + 5 * sc + 8), .12); d = ImageDraw.Draw(im)
    d.rectangle([CX - w // 2, y, CX - w // 2 + w - 1, y + 5 * sc + 7], outline=EDGE)
    tx(d, CX - tw(text, sc) // 2, y + 4, text[:max(0, age * 2)], col, sc)
    return im

def compare_card(im, tr, title, rows, unit, fr, note=None):
    """Bars that fill with a running number, one after the other. rows: (label, value, colour)."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.2)
    im = shade(im, (0, 0, NW, NH), .4); d = ImageDraw.Draw(im)
    tx(d, CX - tw(title, 2) // 2, 48, title, INK, 2)
    vmax = max(v for _, v, _ in rows); bx0, bx1 = CX - 52, CX + 52
    for i, (lbl, v, col) in enumerate(rows):
        t0 = 10 + i * 40; y = 74 + i * 34
        if fr < t0: continue
        k = min(1, (fr - t0) / 30); val = v * k
        tx(d, bx0, y, lbl, MUT if k < 1 else INK, 2)
        by = y + 14
        d.rectangle([bx0, by, bx1, by + 7], fill=(30, 34, 48))
        d.rectangle([bx0, by, bx0 + int((bx1 - bx0) * val / vmax), by + 7], fill=col)
        num = f"{val:.0f} {unit}"; tx(d, bx1 - tw(num, 2), y, num, col if k >= 1 else INK, 2)
    if note and fr > 10 + len(rows) * 40:
        for j, (t, c, sc) in enumerate(note): tx(d, CX - tw(t, sc) // 2, 148 + j * 14, t, c, sc)
    return im

def strategy_card(im, title, rows, sub, laps, fr):
    """Pit-stop strategy infographic: one bar per driver over the race distance, stops marked with lap numbers."""
    d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 40, SAFE_X1, 146], fill=(14, 16, 26), outline=EDGE)
    tx(d, CX - tw(title, 2) // 2, 48, title, INK, 2)
    bx0, bx1 = CX - 46, CX + 46; k = ease(min(1, fr / 45))
    for i, (name, team, stops) in enumerate(rows):
        y = 70 + i * 34
        tx(d, bx0, y, name, INK, 2); d.rectangle([bx0 + tw(name, 2) + 4, y, bx0 + tw(name, 2) + 6, y + 9], fill=team_col(team))
        by = y + 14
        d.rectangle([bx0, by, bx1, by + 4], fill=(30, 34, 48))
        d.rectangle([bx0, by, bx0 + int((bx1 - bx0) * k), by + 4], fill=team_col(team))
        for st in stops:
            if k * laps >= st:
                xs = bx0 + int((bx1 - bx0) * st / laps); d.rectangle([xs - 1, by - 2, xs + 1, by + 6], fill=YEL)
                tx(d, xs - tw(str(st), 2) // 2, by + 8, str(st), YEL, 2)
    if fr > 60 and sub:
        for j, (s, c, sc) in enumerate(sub): tx(d, CX - tw(s, sc) // 2, 156 + j * 14, s, c, sc)
    return im

def apply_calls(im, sg, fr, anchors, avoid=(), where=("", 0)):
    if sg.get("head"): im = headline(im, sg["head"][0], sg["head"][1], fr - sg["head"][2] if len(sg["head"]) > 2 else fr - 4)
    calls = [c for c in sg.get("call", ()) if fr >= c[0] and (len(c) < 5 or fr < c[4])]
    if calls:
        at, tgt, lines, side = calls[-1][:4]   # only one fact on screen at a time
        if tgt in anchors:
            cache = sg.setdefault("_place", {})
            others = [a for a in avoid if a[0] != tgt]
            if at not in cache:
                p_ = place_callout(anchors[tgt], lines, side, avoid, tgt); cache[at] = [list(p_), list(p_)]
            cur, goal = cache[at]
            ax, ay = anchors[tgt]; w_, h_ = box_size(lines)
            b_ = clamp_box(ax + cur[0], max(24, min(SAFE_Y1 - h_, ay + cur[1])), w_, h_)
            if box_hits((*b_, w_, h_), others):          # cars moved into the box: glide to a free spot
                p_ = place_callout(anchors[tgt], lines, side, avoid, tgt)
                nb = clamp_box(ax + p_[0], max(24, min(SAFE_Y1 - h_, ay + p_[1])), w_, h_)
                if box_hits((*nb, w_, h_), others) < box_hits((*b_, w_, h_), others): goal[:] = list(p_)
            cur[0] += (goal[0] - cur[0]) * .25; cur[1] += (goal[1] - cur[1]) * .25; cur[2] = goal[2]
            im, box = callout(im, anchors[tgt], lines, fr - at, tuple(cur))
            if box and fr - at >= 5 and box_hits(box, [a for a in avoid if a[0] != tgt]):
                warn(where[0], where[1], f"callout '{lines[0][0]}' covers a car/label")
    elif sg.get("head") is None and False: pass
    return im

PODIUM_T = {3: 10, 2: 22, 1: 36}          # frame each podium step rises
ROWS_T0, ROWS_STEP, EXTRA_T0 = 60, 9, 92
def podium_board(im, tr, title, rows, extra, fr):
    """Final result: podium with the top-3 cars, then P4-P6 as a compact list, then one or two notes.
    rows: (pos, name, team, gap, grid). extra: [note1 (big, yellow), note2 (small)]."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.22)
    im = shade(im, (0, 0, NW, NH), .55); d = ImageDraw.Draw(im)
    if fr > PODIUM_T[1] + 18:                                  # confetti in the winner's colours
        rr = np.random.default_rng(7); cols = [YEL, team_col(rows[0][2]), INK]
        for k in range(40):
            x0 = rr.uniform(0, NW); sp = rr.uniform(.6, 1.4); ph = rr.uniform(0, 200)
            y = (ph + (fr - PODIUM_T[1] - 18) * sp) % 200 + 20
            if y < 150 and not (40 <= y <= 46): d.rectangle([x0 + math.sin(y / 9 + k) * 3, y, x0 + math.sin(y / 9 + k) * 3 + 1, y], fill=cols[k % 3])
    tx(d, CX - tw(title, 2) // 2, 26, title, INK, 2)
    for i in range(0, NW, 3):                                   # chequered strip
        for j in range(2): d.rectangle([i, 40 + j * 3, i + 2, 42 + j * 3], fill=INK if (i // 3 + j) % 2 == 0 else (30, 34, 48))
    steps = {2: (CX - 52, 88), 1: (CX - 17, 78), 3: (CX + 18, 94)}   # x0, top
    bottom = 108
    for p in (3, 2, 1):
        t0 = PODIUM_T[p]
        if fr < t0: continue
        k = ease(min(1, (fr - t0) / 10)); x0, top = steps[p]; top_k = int(lerp(bottom, top, k))
        _, name, team, gap, grid = rows[p - 1]
        d.rectangle([x0, top_k, x0 + 34, bottom], fill=(30, 34, 48), outline=EDGE)
        d.rectangle([x0, top_k, x0 + 34, top_k + 1], fill=YEL if p == 1 else (150, 160, 180) if p == 2 else (176, 120, 70))
        if k >= 1:
            tx(d, x0 + 17 - tw(str(p), 2) // 2, top + 6, str(p), YEL if p == 1 else INK, 2)
            drop = ease(min(1, (fr - t0 - 10) / 8)); cy = lerp(top - 40, top - 11, drop)
            draw_car(d, x0 + 17, cy, -math.pi / 2, team, 15)
            if drop >= 1:
                code = name.replace(". ", "")[:3] if "." not in name else name.split()[-1][:3]
                tx(d, x0 + 17 - tw(code) // 2, top - 26, code, YEL if p == 1 else INK)
                g = "WINNER" if p == 1 else gap
                tx(d, x0 + 17 - tw(g) // 2, bottom + 3, g, GRN if p == 1 else INK)
                gl = f"FROM P{grid}"; tx(d, x0 + 17 - tw(gl) // 2, bottom + 10, gl, MUT)
    for i, (p, name, team, gap, grid) in enumerate(rows[3:6]):
        t0 = ROWS_T0 + i * ROWS_STEP
        if fr < t0: continue
        y = 128 + i * 8; xo = int(lerp(-40, 0, ease(min(1, (fr - t0) / 6))))
        tx(d, 14 + xo, y, p, MUT); d.rectangle([20 + xo, y, 21 + xo, y + 4], fill=team_col(team))
        tx(d, 25 + xo, y, name, INK); tx(d, 106 - tw(gap) + xo, y, gap, INK)
        delta = grid - int(p)
        if delta: tri(d, 110 + xo, y, delta > 0, GRN if delta > 0 else RED)
    if fr >= EXTRA_T0 and extra:
        tx(d, CX - tw(extra[0], 2) // 2, 154, extra[0], YEL, 2)
    if fr >= EXTRA_T0 + 12 and len(extra) > 1:
        tx(d, CX - tw(extra[1]) // 2, 167, extra[1], MUT)
    return im

# ---------------- generic renderer ----------------
def render(R, name):
    tr = Track(R["geo"], rot=R.get("rot", 0)); L = tr.raw_len
    SIZE.update(track_m=R["track_m"], car_m=R["car_m"], fit=tr.fit)
    segs = R["segments"]; total = sum(s["frames"] for s in segs)
    marks = [s["jump"][1] for s in segs if "jump" in s]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", R["audio"](segs, total), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    cam_prev = (tr.cx, tr.cy, 1.0); snaps = []; gone = set(); cut = True
    gaps_prev = {c: R["grid"][c] for c in R["cars"]}
    for si, sg in enumerate(segs):
        F = sg["frames"]; gone |= set(sg.get("drop", ()))
        if "jump" in sg or "board" in sg or "note" in sg or "strategy" in sg or "gridcard" in sg or "compare" in sg or sg.get("outro"):
            for fr in range(F):
                im = Image.new("RGB", (NW, NH), BG)
                if "jump" in sg: im = lap_card(im, tr, *sg["jump"], R["laps"], fr / max(1, F - 1), sg.get("sub"), marks)
                elif "board" in sg: im = podium_board(im, tr, *sg["board"], fr)
                elif "compare" in sg: im = compare_card(im, tr, *sg["compare"][:3], fr, *sg["compare"][3:])
                elif "note" in sg: im = note_card(im, tr, sg["note"], fr, sg.get("tspeed", 1.2))
                elif "strategy" in sg: im = strategy_card(im, *sg["strategy"], R["laps"], fr)
                elif "gridcard" in sg:
                    im = grid_card(im, tr, sg["gridcard"], fr, sg.get("fire"), sg.get("delay", True))
                    if sg.get("mark") and fr > 20 and (fr // 8) % 2 == 0:
                        d = ImageDraw.Draw(im)
                        for m_ in sg["mark"]:
                            x_, y_ = grid_slot(sg["gridcard"], m_)
                            x0_ = x_ - 32 if m_ % 2 else x_ - 6; d.rectangle([x0_, y_ - 6, x0_ + 38, y_ + 6], outline=YEL)
                    if sg.get("header"):
                        im = panel(im, [(t, c, sc_) if fr >= 4 + i * 14 else ("", c, sc_) for i, (t, c, sc_) in enumerate(sg["header"])], y0=24)
                    anchors = {("slot", r[0]): grid_slot(sg["gridcard"], r[0]) for r in sg["gridcard"]}
                    av = [(("slot", k_), x_, y_, 6) for k_, (x_, y_) in anchors.items()]
                    im = apply_calls(im, sg, fr, anchors, av, (name, si))
                else:
                    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.5)
                    im = panel(im, [(t, c, sc_) if fr >= 6 + i * 14 else ("", c, sc_) for i, (t, c, sc_) in enumerate(sg["text"])], y0=70)
                    if fr > 50:
                        d = ImageDraw.Draw(im); tx(d, CX - tw("THE PIXEL PADDOCK") // 2, 130, "THE PIXEL PADDOCK", GRN)
                if fr == F - 4: snaps.append(im)
                p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
            cut = True
            continue
        g0 = dict(gaps_prev); g0.update(sg.get("set", {})); g1 = dict(g0); g1.update(sg.get("gaps", {}))
        v_lead = (sg["laps"][1] - sg["laps"][0]) * L / max(1, F - 1)  # metres per frame
        spin_state = {}; prev_pos = {}
        for fr in range(F):
            t = fr / max(1, F - 1); te = ease(t)
            lapf = lerp(sg["laps"][0], sg["laps"][1], t if sg.get("linear", True) else te)
            lead_s = lapf * L
            pos, lat, ang_add = {}, {}, {}
            for c in R["cars"]:
                gap = lerp(g0[c], g1[c], t if sg.get("glin") else te)   # glin: steady closing speed (overtakes)
                pos[c] = lead_s - gap
                la = sg.get("lat", {}).get(c); lat[c] = lerp(la[0], la[1], te) if la else 0
                ang_add[c] = 0
                sp = sg.get("spin", {}).get(c)
                if sp is not None and t >= sp[0]:
                    if c not in spin_state: spin_state[c] = pos[c]
                    dt = (t - sp[0]) * F; tau = 10
                    pos[c] = spin_state[c] + v_lead * tau * (1 - math.exp(-dt / tau))
                    ang_add[c] = sp[1] * ease(min(1, dt / 30)); lat[c] = sp[2] * ease(min(1, dt / 25))
                    if abs(sp[2]) > 2.5: warn(name, si, f"{c} spins too far off ({sp[2]}), may cross another part of the track")
                if c in sg.get("pit", {}):
                    pf, side = sg["pit"][c]; pos[c] = pf * L; lat[c] = side
            tgt = sg.get("cam", ("over",))
            if tgt[0] == "over": ctg = (tr.cx, tr.cy, 1.0)
            elif tgt[0] == "frac": x, y = tr.at(tgt[1]); ctg = (x, y, tgt[2])
            elif tgt[0] == "pan": x, y = tr.at(lerp(tgt[1], tgt[2], ease(t))); ctg = (x, y, tgt[3])
            else:
                x, y = tr.at(pos[tgt[1]] / L); dx, dy = (tgt[3], tgt[4]) if len(tgt) > 4 else (0, 0)
                ctg = (x - dx / (tr.fit * tgt[2]), y - dy / (tr.fit * tgt[2]), tgt[2])
            if cut: cam = ctg
            else:
                k = ease(min(1, fr / 24)); cam = tuple(lerp(cam_prev[i], ctg[i], k) for i in range(3))
            im = Image.new("RGB", (NW, NH), BG)
            sc_v = sg.get("sc", False); sc_on = sc_v is True or (sc_v is not False and t >= sc_v)
            d = draw_map(im, tr, cam, R.get("start_frac", 0), sc_on=sc_on)
            z = cam[2]; px = car_px(z); anchors = {}; avoid = []
            for c in sorted(R["cars"], key=lambda c: pos[c]):
                if c in sg.get("hide", ()) or c in gone: continue
                fr_ = pos[c] / L
                x, y = project(tr, cam, tr.at(fr_)); h = tr.heading(fr_)
                hl = lat_half(z); x += -math.sin(h) * lat[c] * hl; y += math.cos(h) * lat[c] * hl
                anchors[c] = (x, y); avoid.append((c, x, y, px * .55))
                if -20 < x < NW + 20 and -20 < y < NH + 20:
                    draw_car(d, x, y, h + ang_add[c], R["cars"][c][0], px, helmet=R["cars"][c][1])
                    if px >= 8 and c in sg.get("labels", ()):
                        lab = (f"P{sg['pos'][c]} " if c in sg.get("pos", {}) else "") + c
                        lx, ly = int(x) - tw(lab) // 2, int(y) - int(px * .6) - 8
                        tx(d, lx + 1, ly + 1, lab, (6, 8, 16)); tx(d, lx, ly, lab, YEL if c in sg.get("pos", {}) and sg["pos"][c] == 1 else INK)
                        avoid.append((c, x, ly + 2, tw(lab) / 2 + 1))
                # plausibility: never backwards (unless spinning / pitting), stay on track
                if c not in sg.get("spin", {}) and c not in sg.get("pit", {}) and c not in sg.get("hide", ()):
                    if fr > 0 and pos[c] < prev_pos.get(c, -1e9) - .3: warn(name, si, f"{c} moves backwards")
                    if fr > 0 and c in prev_pos and v_lead > 1 and sg.get("linear", True):
                        ratio = (pos[c] - prev_pos[c]) / v_lead
                        if ratio > 1.3 or ratio < .7: warn(name, si, f"{c} speed outside 0.7-1.3x the reference car")
                    if abs(lat[c]) > 1.05: warn(name, si, f"{c} off track (lat {lat[c]:.1f})")
                prev_pos[c] = pos[c]
            vis_ = [(c, anchors[c], tr.heading(pos[c] / L)) for c in anchors if c not in sg.get("hide", ()) and c not in gone and c not in sg.get("pit", {})
                    and -10 < anchors[c][0] < NW + 10 and -10 < anchors[c][1] < NH + 10]
            for i_ in range(len(vis_)):
                for j_ in range(i_ + 1, len(vis_)):
                    (ca, (xa, ya), ha), (cb, (xb, yb), _) = vis_[i_], vis_[j_]
                    dx_, dy_ = xb - xa, yb - ya
                    lo = abs(dx_ * math.cos(ha) + dy_ * math.sin(ha)); la = abs(-dx_ * math.sin(ha) + dy_ * math.cos(ha))
                    if lo < .95 * px and la < .47 * px and px >= 8: warn(name, si, f"{ca} and {cb} overlap")
            if sg.get("rain"):
                rr = np.random.default_rng(fr)
                for _ in range(int(90 * sg["rain"])):
                    x0 = int(rr.integers(0, NW + 10)); y0 = int(rr.integers(0, NH)); d.line([(x0, y0), (x0 - 2, y0 + 4)], fill=(120, 140, 175))
            if sg.get("inset"): sg["inset"](d, fr)
            if sg.get("timer"):
                a, b, lbl = sg["timer"]; k = min(1, fr / (F * .7)); val = lerp(a, b, k)
                s = f"{val:4.1f} S".strip(); col = YEL if k >= 1 else INK
                d.rectangle([SAFE_X0, 140, SAFE_X0 + 56, 167], fill=PANEL, outline=EDGE)
                tx(d, SAFE_X0 + 4, 144, lbl, MUT); tx(d, SAFE_X0 + 4, 152, s, col, 2)
            nohud = sg.get("nohud") or sg.get("nolap")
            im = panel(im, typed(sg.get("text", []), fr, sg.get("tspeed", 1.6)), y0=10 if sg.get("nohud") else 24)
            if not nohud:
                vis = [c for c in R["cars"] if c not in gone and c not in sg.get("hide", ()) and c not in sg.get("pit", {}) and c not in sg.get("spin", {})]
                lead = sg.get("leader") or max(vis, key=lambda c: pos[c])
                lapn = min(R["laps"], max(1, math.floor(lapf) + 1))
                im = hud(im, lapn, R["laps"]) if sg.get("noleader") else hud(im, lapn, R["laps"], R["names"][lead], R["cars"][lead][0])
                if sc_on:
                    d = ImageDraw.Draw(im); on = (fr // 10) % 2 == 0
                    d.rectangle([SAFE_X0 + 48, 9, SAFE_X1 - 2, 18], fill=YEL if on else (90, 76, 20))
                    tx(d, (SAFE_X0 + 48 + SAFE_X1 - 2) // 2 - tw("SAFETY CAR") // 2, 11, "SAFETY CAR", (10, 10, 10) if on else YEL)
            for f_ in sg.get("fracs", ()): anchors[("frac", f_)] = project(tr, cam, tr.at(f_))
            im = apply_calls(im, sg, fr, anchors, avoid, (name, si))
            if fr == F - 4: snaps.append(im)
            p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
            cut = False
        cam_prev = cam; gaps_prev = g1
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", round(total / FPS, 1))
    for (v, sgi, msg), n in sorted(WARN.items()):
        if v == name: print(f"  CHECK seg {sgi}: {msg} ({n} frames)")

# ---------------- audio (shared) ----------------
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
def tone(fq, dur, vol=.2, kind="sq", decay=4):
    t = np.arange(int(SR * dur)) / SR
    w = np.sign(np.sin(2 * np.pi * fq * t)) * .7 if kind == "sq" else 2 * np.abs(2 * ((t * fq) % 1) - 1) - 1
    return w * vol * np.minimum(1, t * 60) * np.exp(-decay * t)
def mix(buf, sig, at):
    i = int(at * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += sig[:j - i]
MOTIF = [(64, 0, .3), (67, .3, .3), (71, .6, .3), (69, .9, .6), (67, 1.5, .3), (64, 1.8, .9)]
def make_audio(tag):
    def f(segs, total):
        buf = np.zeros(int(SR * total / FPS) + SR)
        for m, t, du in MOTIF: mix(buf, tone(NOTE(m), du * 1.2, .10, "tri", 1.5), .3 + t)
        acc = 0; env = np.zeros(len(buf))
        for sg in segs:
            st = acc / FPS; F = sg["frames"]
            if "jump" in sg:   # rising whoosh of blips while the lap number rolls
                for k in range(8): mix(buf, tone(NOTE(60 + k * 2), .06, .06, "sq", 12), st + k * .09)
                mix(buf, tone(NOTE(84), .25, .08, "sq", 5), st + .85)
            elif "board" in sg:
                for p, m in ((3, 67), (2, 71), (1, 74)):
                    tt = st + PODIUM_T[p] / FPS
                    for j in range(5): mix(buf, tone(NOTE(m - 12 + j * 3), .03, .05, "sq", 25), tt + j * .05)
                    mix(buf, tone(NOTE(m + 12), .18 if p > 1 else .6, .09, "sq", 4), tt + 18 / FPS)
                for i in range(3): mix(buf, tone(NOTE(84), .03, .04, "sq", 30), st + (ROWS_T0 + i * ROWS_STEP) / FPS)
                mix(buf, tone(NOTE(79), .1, .07, "sq", 8), st + EXTRA_T0 / FPS)
            elif "compare" in sg:
                for i in range(len(sg["compare"][1])):
                    t0 = st + (10 + i * 40) / FPS
                    for k in range(10): mix(buf, tone(NOTE(84), .015, .045, "sq", 40), t0 + k * 30 / FPS / 10)
                    mix(buf, tone(NOTE(76 + i * 5), .2, .08, "sq", 5), t0 + 30 / FPS)
            elif sg.get("outro"):
                for m, t, du in MOTIF: mix(buf, tone(NOTE(m), du * 1.2, .10, "tri", 1.5), st + .3 + t)
            else:
                if sg.get("note") or sg.get("text"):
                    for i in range(len(sg.get("note") or sg.get("text"))): mix(buf, tone(NOTE(76 + i * 2), .07, .06, "sq", 10), st + (6 + i * 14) / FPS)
                for i, _ in enumerate(sg.get("header", ())): mix(buf, tone(NOTE(76 + i * 2), .07, .06, "sq", 10), st + (4 + i * 14) / FPS)
                for c in sg.get("call", ()): mix(buf, tone(NOTE(81), .06, .07, "sq", 12), st + c[0] / FPS); mix(buf, tone(NOTE(88), .05, .05, "sq", 12), st + c[0] / FPS + .06)
                if sg.get("fire"):
                    nz = np.random.default_rng(5).uniform(-1, 1, int(SR * F / FPS)) * .03; mix(buf, nz, st + .4)
                if sg.get("rain"):
                    nz = np.convolve(np.random.default_rng(3).uniform(-1, 1, int(SR * F / FPS)), np.ones(8) / 8, mode="same") * .06 * sg["rain"]
                    mix(buf, nz, st)
                if sg.get("win"):
                    for k, m in enumerate([72, 76, 79, 84]): mix(buf, tone(NOTE(m), .3 if k < 3 else 1.1, .11, "sq", 2.5), st + .4 + k * .15)
                if sg.get("spin"):
                    sp = list(sg["spin"].values())[0][0]
                    mix(buf, tone(NOTE(45), .5, .09, "sq", 4), st + sp * F / FPS)
                if sg.get("timer"):
                    for k in range(int(F * .7 / FPS * 4)): mix(buf, tone(NOTE(84), .015, .04, "sq", 40), st + k * .25)
                if "laps" in sg and sg["laps"][1] > sg["laps"][0]:
                    env[int(st * SR):int((st + F / FPS) * SR)] = 1
            acc += F
        tt = np.arange(len(buf)) / SR; pitch = 90 + 30 * (np.sin(tt * 1.3) * .5 + .5)
        bed = np.sign(np.sin(2 * np.pi * np.cumsum(pitch) / SR)) * .022
        env = np.convolve(env, np.ones(SR // 4) / (SR // 4), mode="same")
        buf += bed * env
        buf = np.clip(buf, -1, 1); path = f"{OUT}/{tag}.wav"
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
        return path
    return f
