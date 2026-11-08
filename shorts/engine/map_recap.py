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
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 4, 112, 8, 172
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

def draw_map(im, tr, cam, start_frac=0.0, sc_on=False, dim=1.0):
    d = ImageDraw.Draw(im); z = cam[2]
    P = [project(tr, cam, p) for p in tr.pts] + [project(tr, cam, tr.pts[0])]
    w = max(3, int(2 + z * 2.2))
    c = lambda col: tuple(int(v * dim + BG[i] * (1 - dim)) for i, v in enumerate(col))
    d.line(P, fill=c((60, 68, 92)), width=w + 2); d.line(P, fill=c((38, 42, 54) if not sc_on else (70, 62, 20)), width=w)
    d.line(P, fill=c((48, 54, 70)), width=1)
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
    tx(d, 8, 12, "LAP", MUT); tx(d, 22, 12, f"{lap}/{laps}", INK)
    if leader: d.rectangle([54, 12, 56, 16], fill=team_col(lead_team)); tx(d, 59, 12, leader, INK)
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
    bx0, bx1, by = 14, 102, 122
    d.rectangle([bx0, by, bx1, by + 3], fill=(30, 34, 48))
    d.rectangle([bx0, by, bx0 + int((bx1 - bx0) * lerp(a, b, k) / laps), by + 3], fill=GRN)
    for m in marks:
        xm = bx0 + int((bx1 - bx0) * m / laps); d.rectangle([xm, by - 2, xm, by + 5], fill=YEL)
    if sub and t > .55: tx(d, CX - tw(sub) // 2, 134, sub, INK)
    return im

def note_card(im, tr, lines, fr, speed=1.2):
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.25)
    im = shade(im, (0, 0, NW, NH), .4)
    return panel(im, typed(lines, fr, speed), y0=70)

def results_board(im, title, rows, extra, fr):
    """Timing board. rows: (pos, name, team, gap, grid). Rows flip in from the back, P1 last, then notes."""
    d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 22, SAFE_X1, 168], fill=(22, 26, 34)); d.rectangle([SAFE_X0 + 3, 25, SAFE_X1 - 3, 165], fill=(4, 14, 8))
    for y in range(26, 165, 3): d.line([(SAFE_X0 + 3, y), (SAFE_X1 - 3, y)], fill=(2, 10, 6))
    G1, G2 = (150, 255, 160), (70, 150, 90)
    tx(d, CX - tw(title) // 2, 30, title, GRN)
    d.line([(10, 39), (106, 39)], fill=(30, 70, 40))
    n = len(rows); start, step = 14, 16
    glyph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for k, (p, name, team, gap, grid) in enumerate(rows):
        order = n - 1 - k                     # back of the field first
        t_in = start + order * step + (14 if k == 0 else 0)
        if fr < t_in: continue
        y = 44 + k * 17; age = fr - t_in
        scramble = age < 8
        def sc_(s): return "".join(glyph[(ord(ch) * 7 + fr * 13 + i * 5) % len(glyph)] if ch != " " and scramble else ch for i, ch in enumerate(s))
        if k == 0 and age > 8 and (fr // 6) % 2 == 0: d.rectangle([9, y - 2, 107, y + 13], outline=GRN)
        tx(d, 12, y, p, GRN if k == 0 else G1)
        d.rectangle([19, y, 20, y + 4], fill=team_col(team))
        tx(d, 23, y, sc_(name), INK if k == 0 else G1)
        g = sc_(gap); tx(d, 105 - tw(g), y, g, GRN if k == 0 else G1)
        if not scramble and grid:
            delta = grid - int(p)
            tx(d, 23, y + 7, f"GRID {grid}", G2)
            if delta:
                col = GRN if delta > 0 else RED; tri(d, 60, y + 7, delta > 0, col); tx(d, 66, y + 7, str(abs(delta)), col)
            else: tx(d, 60, y + 7, "=", G2) if "=" in FONT3 else d.rectangle([60, y + 9, 64, y + 9], fill=G2)
    y = 48 + n * 17; t_ex = start + n * step + 26
    for i, s in enumerate(extra):
        if fr >= t_ex + i * 10: tx(d, CX - tw(s) // 2, y, s, YEL if i == 0 else G2)
        y += 9
    return im

def slope_chart(im, title, rows, fr, maxgrid):
    """Grid vs finish: where the top finishers started. No driver highlighted (house rule)."""
    d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 22, SAFE_X1, 168], fill=(14, 16, 26)); d.rectangle([SAFE_X0, 22, SAFE_X1, 168], outline=EDGE)
    tx(d, CX - tw(title) // 2, 28, title, INK)
    xL, xR, y0, y1 = 20, 46, 46, 158
    tx(d, xL - tw("GRID") // 2, 38, "GRID", MUT); tx(d, xR - tw("FINISH") // 2, 38, "FINISH", MUT)
    yg = lambda g: y0 + (y1 - y0) * (g - 1) / max(1, maxgrid - 1)
    yf = lambda f: y0 + (f - 1) * 12
    for g in range(1, maxgrid + 1):
        d.point((xL - 2, yg(g)), fill=(60, 66, 90))
    k = ease(min(1, fr / 40))
    for p, name, team, gap, grid in rows:
        f = int(p); a = (xL, yg(grid)); b = (xR, yf(f)); col = team_col(team)
        e = (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        d.line([a, e], fill=col, width=1)
        d.rectangle([a[0] - 1, a[1] - 1, a[0] + 1, a[1] + 1], fill=col)
        tx(d, xL - 6 - tw(str(grid)), int(a[1]) - 2, str(grid), MUT)
        if k >= 1:
            d.rectangle([b[0] - 1, b[1] - 1, b[0] + 1, b[1] + 1], fill=col)
            tx(d, xR + 4, int(b[1]) - 2, f"{f} {name}", INK)
    return im

def grid_card(im, tr, rows, fr):
    """Starting grid as a staggered slot diagram. rows: (pos, code or None, team). Unnamed slots are grey."""
    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.18); d = ImageDraw.Draw(im)
    n = max(r[0] for r in rows); step = min(12, 92 / max(1, n - 1)); y0 = 74
    xl, xr = 44, 70; px = 9 if n > 10 else 12
    d.line([(CX - 22, y0 - 8), (CX + 22, y0 - 8)], fill=INK)
    for k, (pos, code, team) in enumerate(sorted(rows)):
        if fr < 6 + k * 3: continue
        x = xl if pos % 2 else xr; y = y0 + (pos - 1) * step
        d.line([(x - 5, y - px * .55), (x + 5, y - px * .55)], fill=(70, 78, 104))
        draw_car(d, x, y, -math.pi / 2, team if code else "GEN", px)
        num = str(pos)
        if code:
            col = YEL if code.startswith("*") else INK; c = code.lstrip("*")
            if pos % 2: tx(d, x - 9 - tw(c), int(y) - 2, c, col); tx(d, x - 9 - tw(c) - 4 - tw(num), int(y) - 2, num, MUT)
            else: tx(d, x + 9, int(y) - 2, c, col); tx(d, x + 9 + tw(c) + 4, int(y) - 2, num, MUT)
    return im

def strategy_card(im, title, rows, sub, laps, fr):
    """Pit-stop strategy infographic: one bar per driver over the race distance, stops marked with lap numbers."""
    d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 40, SAFE_X1, 150], fill=(14, 16, 26), outline=EDGE)
    tx(d, CX - tw(title, 2) // 2, 48, title, INK, 2)
    bx0, bx1 = 12, 104; k = ease(min(1, fr / 45))
    for i, (name, team, stops) in enumerate(rows):
        y = 74 + i * 30
        tx(d, bx0, y, name, INK); d.rectangle([bx0 + tw(name) + 3, y, bx0 + tw(name) + 4, y + 4], fill=team_col(team))
        by = y + 9
        d.rectangle([bx0, by, bx1, by + 4], fill=(30, 34, 48))
        d.rectangle([bx0, by, bx0 + int((bx1 - bx0) * k), by + 4], fill=team_col(team))
        for st in stops:
            if k * laps >= st:
                xs = bx0 + int((bx1 - bx0) * st / laps); d.rectangle([xs - 1, by - 2, xs + 1, by + 6], fill=YEL)
                tx(d, xs - tw(str(st)) // 2, by + 9, str(st), YEL)
    tx(d, bx0, 136, "LAP 1", MUT); tx(d, bx1 - tw(str(laps)) + 1, 136, str(laps), MUT)
    if fr > 60 and sub:
        for j, s in enumerate(sub): tx(d, CX - tw(s) // 2, 156 + j * 8, s, INK)
    return im

# ---------------- generic renderer ----------------
def render(R, name):
    tr = Track(R["geo"], rot=R.get("rot", 0)); L = tr.raw_len
    segs = R["segments"]; total = sum(s["frames"] for s in segs)
    marks = [s["jump"][1] for s in segs if "jump" in s]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", R["audio"](segs, total), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    cam_prev = (tr.cx, tr.cy, 1.0); snaps = []; gone = set(); cut = True
    gaps_prev = {c: R["grid"][c] for c in R["cars"]}
    for si, sg in enumerate(segs):
        F = sg["frames"]; gone |= set(sg.get("drop", ()))
        if "jump" in sg or "board" in sg or "slope" in sg or "note" in sg or "strategy" in sg or "gridcard" in sg or sg.get("outro"):
            for fr in range(F):
                im = Image.new("RGB", (NW, NH), BG)
                if "jump" in sg: im = lap_card(im, tr, *sg["jump"], R["laps"], fr / max(1, F - 1), sg.get("sub"), marks)
                elif "board" in sg: im = results_board(im, *sg["board"], fr)
                elif "slope" in sg: im = slope_chart(im, sg["slope"], R["results"], fr, R["maxgrid"])
                elif "note" in sg: im = note_card(im, tr, sg["note"], fr, sg.get("tspeed", 1.2))
                elif "strategy" in sg: im = strategy_card(im, *sg["strategy"], R["laps"], fr)
                elif "gridcard" in sg: im = panel(grid_card(im, tr, sg["gridcard"], fr), typed(sg["text"], fr, sg.get("tspeed", 1.6)), y0=10)
                else:
                    draw_map(im, tr, (tr.cx, tr.cy, 1.0), dim=.5)
                    im = panel(im, typed(sg["text"], fr, 1.2), y0=70)
                    if fr > 30:
                        d = ImageDraw.Draw(im); tx(d, CX - tw("THE PIXEL PADDOCK") // 2, 150, "THE PIXEL PADDOCK", GRN)
                if fr == F - 4: snaps.append(im)
                p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
            cut = True
            continue
        g0 = dict(gaps_prev); g0.update(sg.get("set", {})); g1 = dict(g0); g1.update(sg.get("gaps", {}))
        v_lead = (sg["laps"][1] - sg["laps"][0]) * L / max(1, F - 1)  # metres per frame
        spin_state = {}
        for fr in range(F):
            t = fr / max(1, F - 1); te = ease(t)
            lapf = lerp(sg["laps"][0], sg["laps"][1], t if sg.get("linear", True) else te)
            lead_s = lapf * L
            pos, lat, ang_add = {}, {}, {}
            for c in R["cars"]:
                gap = lerp(g0[c], g1[c], te)
                pos[c] = lead_s - gap
                la = sg.get("lat", {}).get(c); lat[c] = lerp(la[0], la[1], te) if la else 0
                ang_add[c] = 0
                sp = sg.get("spin", {}).get(c)
                if sp is not None and t >= sp[0]:
                    if c not in spin_state: spin_state[c] = pos[c]
                    dt = (t - sp[0]) * F; tau = 10
                    pos[c] = spin_state[c] + v_lead * tau * (1 - math.exp(-dt / tau))
                    ang_add[c] = sp[1] * ease(min(1, dt / 30)); lat[c] = sp[2] * ease(min(1, dt / 25))
                if c in sg.get("pit", {}):
                    pf, side = sg["pit"][c]; pos[c] = pf * L; lat[c] = side
            tgt = sg.get("cam", ("over",))
            if tgt[0] == "over": ctg = (tr.cx, tr.cy, 1.0)
            elif tgt[0] == "frac": x, y = tr.at(tgt[1]); ctg = (x, y, tgt[2])
            elif tgt[0] == "pan": x, y = tr.at(lerp(tgt[1], tgt[2], ease(t))); ctg = (x, y, tgt[3])
            else: x, y = tr.at(pos[tgt[1]] / L); ctg = (x, y, tgt[2])
            if cut: cam = ctg
            else:
                k = ease(min(1, fr / 24)); cam = tuple(lerp(cam_prev[i], ctg[i], k) for i in range(3))
            im = Image.new("RGB", (NW, NH), BG)
            sc_v = sg.get("sc", False); sc_on = sc_v is True or (sc_v is not False and t >= sc_v)
            d = draw_map(im, tr, cam, R.get("start_frac", 0), sc_on=sc_on)
            z = cam[2]; px = 7 + (z - 1) * 7
            for c in sorted(R["cars"], key=lambda c: pos[c]):
                if c in sg.get("hide", ()) or c in gone: continue
                fr_ = pos[c] / L
                x, y = project(tr, cam, tr.at(fr_)); h = tr.heading(fr_)
                x += -math.sin(h) * lat[c] * px * .5; y += math.cos(h) * lat[c] * px * .5
                if -20 < x < NW + 20 and -20 < y < NH + 20:
                    draw_car(d, x, y, h + ang_add[c], R["cars"][c][0], px, helmet=R["cars"][c][1])
                    if z >= 2.2 and c in sg.get("labels", ()):
                        lx, ly = int(x) - tw(c) // 2, int(y) - int(px * .6) - 8
                        tx(d, lx + 1, ly + 1, c, (6, 8, 16)); tx(d, lx, ly, c, INK)
            if sg.get("rain"):
                rr = np.random.default_rng(fr)
                for _ in range(int(90 * sg["rain"])):
                    x0 = int(rr.integers(0, NW + 10)); y0 = int(rr.integers(0, NH)); d.line([(x0, y0), (x0 - 2, y0 + 4)], fill=(120, 140, 175))
            if sc_on and (fr // 8) % 2:
                d.rectangle([SAFE_X1 - 22, 154, SAFE_X1 - 1, 167], fill=YEL); tx(d, SAFE_X1 - 17, 158, "SC", (10, 10, 10))
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
            if fr == F - 4: snaps.append(im)
            p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
            cut = False
        cam_prev = cam; gaps_prev = g1
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", total / FPS)

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
                n = len(sg["board"][1])
                for k in range(n):
                    tt = st + (14 + k * 16 + (14 if k == n - 1 else 0)) / FPS
                    for j in range(4): mix(buf, tone(NOTE(90 - j), .02, .05, "sq", 30), tt + j * .05)
                    mix(buf, tone(NOTE(72 + (k * 2 if k < n - 1 else 12)), .14, .08, "sq", 6), tt + .27)
            elif "slope" in sg:
                for k, m in enumerate([67, 71, 74]): mix(buf, tone(NOTE(m), .18, .06, "tri", 3), st + .2 + k * .4)
            elif sg.get("outro"):
                for m, t, du in MOTIF: mix(buf, tone(NOTE(m), du * 1.2, .10, "tri", 1.5), st + .3 + t)
            else:
                if sg.get("text") or sg.get("note"): mix(buf, tone(NOTE(76), .08, .07, "sq", 10), st + .1)
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
