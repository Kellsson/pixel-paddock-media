"""Pixel Paddock Historic Race Recap: top-down MAP REPLAY engine.
Real circuit layout (bacinger/f1-circuits GeoJSON), top-down era cars, chronological lap counter,
camera zooms into events, readable text panels, results board at the end."""
import os, sys, math, json, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from font3 import FONT3
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out_short"); os.makedirs(OUT, exist_ok=True)
NW, NH, SC, FPS, SR = 135, 240, 8, 30, 44100
for k, v in {":": "000010000010000", "'": "010010000000000", ",": "000000000010100", ".": "000000000000010", "+": "000010111010000",
             "-": "000000111000000", "!": "010010010000010", "/": "001001010100100", "Q": "010101101110011", "?": "111001011000010", "Z": "111001010100111"}.items():
    FONT3.setdefault(k, v)
INK, MUT, YEL, GRN, RED = (243, 244, 246), (148, 163, 184), (242, 201, 76), (57, 255, 20), (239, 68, 68)
BG = (10, 12, 20); EDGE = (52, 60, 86)

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
    # 1991. McLaren MP4/6: RAL 3024 luminous red over white. Williams FW14: blue nose/monocoque, white sidepods, yellow airbox.
    "MCL91": dict(fwing=(238, 46, 44), nose=(238, 46, 44), pod=(238, 46, 44), body=(244, 244, 244), air=(238, 46, 44), rwing=(238, 46, 44)),
    "WIL91": dict(fwing=(30, 62, 150), nose=(30, 62, 150), pod=(244, 244, 244), body=(30, 62, 150), air=(246, 196, 0), rwing=(244, 244, 244)),
    # 2005. McLaren MP4-20: Silver / Anthracite / Rocket Red (West scheme). Renault R25: light blue + yellow.
    "MCL05": dict(fwing=(70, 72, 80), nose=(200, 204, 212), pod=(200, 204, 212), body=(70, 72, 80), air=(200, 204, 212), rwing=(70, 72, 80), accent=(232, 50, 40)),
    "REN05": dict(fwing=(40, 120, 200), nose=(250, 200, 0), pod=(40, 120, 200), body=(40, 120, 200), air=(250, 200, 0), rwing=(40, 120, 200)),
    "FER05": dict(fwing=(210, 10, 10), nose=(210, 10, 10), pod=(210, 10, 10), body=(210, 10, 10), air=(210, 10, 10), rwing=(240, 240, 240)),
    "TOY05": dict(fwing=(240, 240, 240), nose=(240, 240, 240), pod=(220, 20, 30), body=(240, 240, 240), air=(240, 240, 240), rwing=(220, 20, 30)),
    "GEN": dict(fwing=(120, 124, 132), nose=(120, 124, 132), pod=(120, 124, 132), body=(120, 124, 132), air=(120, 124, 132), rwing=(120, 124, 132)),
    "WIL05": dict(fwing=(20, 40, 110), nose=(240, 240, 240), pod=(240, 240, 240), body=(20, 40, 110), air=(240, 240, 240), rwing=(20, 40, 110)),
}
def draw_car(d, x, y, ang, team, px, helmet=None):
    ca, sa = math.cos(ang), math.sin(ang)
    for col, poly in car_shapes(TEAMS[team]):
        pts = [(x + (u * ca - v * sa) * px, y + (u * sa + v * ca) * px) for u, v in poly]
        d.polygon(pts, fill=col)
    if helmet and px >= 14:
        hx_, hy_ = x + .02 * ca * px, y + .02 * sa * px
        d.ellipse([hx_ - 1, hy_ - 1, hx_ + 1, hy_ + 1], fill=helmet)

# ---------------- track ----------------
class Track:
    def __init__(self, path, n=900, rot=0):
        co = json.load(open(path))['features'][0]['geometry']['coordinates']
        self.length_m = json.load(open(path))['features'][0]['properties']['length']
        lat0 = sum(c[1] for c in co) / len(co)
        P = [((lo) * math.cos(math.radians(lat0)) * 111320, -(la) * 110540) for lo, la in co]
        if P[0] == P[-1]: P = P[:-1]
        if rot:
            ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot)); P = [(x * ca - y * sa, x * sa + y * ca) for x, y in P]
        cum = [0]
        for i in range(1, len(P) + 1): cum.append(cum[-1] + math.dist(P[i - 1], P[i % len(P)]))
        self.raw_len = cum[-1]; self.pts = []
        for k in range(n):
            s = cum[-1] * k / n; i = max(j for j in range(len(cum) - 1) if cum[j] <= s)
            a, b = P[i], P[(i + 1) % len(P)]; t = (s - cum[i]) / max(1e-6, cum[i + 1] - cum[i])
            self.pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        xs = [p[0] for p in self.pts]; ys = [p[1] for p in self.pts]
        self.cx, self.cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        self.fit = min(123 / (max(xs) - min(xs)), 150 / (max(ys) - min(ys)))
        self.n = n
    def at(self, frac):
        f = (frac % 1) * self.n; i = int(f); t = f - i
        a, b = self.pts[i % self.n], self.pts[(i + 1) % self.n]
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    def heading(self, frac):
        a = self.at(frac - .002); b = self.at(frac + .002); return math.atan2(b[1] - a[1], b[0] - a[0])

def project(tr, cam, p):
    cx, cy, z = cam; s = tr.fit * z
    return 67 + (p[0] - cx) * s, 118 + (p[1] - cy) * s

def draw_map(im, tr, cam, start_frac=0.0, sc_on=False):
    d = ImageDraw.Draw(im); z = cam[2]
    P = [project(tr, cam, p) for p in tr.pts] + [project(tr, cam, tr.pts[0])]
    w = max(3, int(2 + z * 2.2))
    d.line(P, fill=(60, 68, 92), width=w + 2); d.line(P, fill=(38, 42, 54) if not sc_on else (70, 62, 20), width=w)
    d.line(P, fill=(48, 54, 70), width=1)
    # start/finish chequer
    x, y = project(tr, cam, tr.at(start_frac)); h = tr.heading(start_frac) + math.pi / 2
    for k in range(-w // 2 - 1, w // 2 + 2):
        d.point((x + math.cos(h) * k, y + math.sin(h) * k), fill=INK if k % 2 else (20, 20, 20))
    return d

def panel(im, lines, y0=6):
    if not lines: return im
    h = sum(5 * s + 5 for _, _, s in lines) + 7
    a = np.asarray(im).astype(float)
    a[y0:y0 + h, 4:NW - 4] = a[y0:y0 + h, 4:NW - 4] * .2 + np.array([6, 8, 16]) * .8
    im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rectangle([4, y0, NW - 5, y0 + h - 1], outline=EDGE)
    y = y0 + 5
    for s, c, sc in lines:
        tx(d, (NW - tw(s, sc)) // 2, y, s, c, sc); y += 5 * sc + 5
    return im

def typed(lines, f, speed=1.4):
    out = []; budget = f * speed
    for s, c, sc in lines:
        n = int(budget / (1 if sc == 1 else 2)); out.append((s[:max(0, n)] + "" if n < len(s) else s, c, sc)); budget = max(0, budget - len(s) * (1 if sc == 1 else 2))
    return out

def hud(im, lap, laps, leader, lead_team, ticks, prog):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 208, NW, 240], fill=(8, 10, 18)); d.line([(0, 208), (NW, 208)], fill=EDGE)
    tx(d, 5, 213, "LAP", MUT); tx(d, 5, 221, f"{lap}/{laps}", INK)
    tx(d, 46, 213, "LEADER", MUT); col = TEAMS[lead_team]["pod"]; d.rectangle([46, 221, 48, 227], fill=col); tx(d, 51, 221, leader, INK)
    # chronological lap bar with event ticks
    x0, x1 = 5, 129
    d.rectangle([x0, 232, x1, 234], fill=(30, 34, 48))
    d.rectangle([x0, 232, x0 + int((x1 - x0) * prog), 234], fill=GRN)
    for t in ticks:
        tx_ = x0 + int((x1 - x0) * t); d.rectangle([tx_, 230, tx_, 236], fill=YEL)

def results_board(im, title, rows, extra):
    d = ImageDraw.Draw(im)
    d.rectangle([6, 20, 128, 196], fill=(22, 26, 34)); d.rectangle([10, 24, 124, 192], fill=(4, 14, 8))
    for y in range(25, 192, 3): d.line([(10, y), (124, y)], fill=(2, 10, 6))
    G1, G2 = (120, 255, 140), (60, 160, 80)
    tx(d, (NW - tw(title)) // 2, 30, title, GRN)
    for k, (p, n, team, g) in enumerate(rows):
        y = 44 + k * 12
        tx(d, 14, y, p, G1); d.rectangle([22, y, 23, y + 4], fill=TEAMS[team]["pod"]); tx(d, 27, y, n, G1); tx(d, 84, y, g, GRN if k == 0 else G1)
    y = 48 + len(rows) * 12
    for s in extra: tx(d, 14, y, s, G2); y += 10

# ---------------- generic renderer ----------------
def render(R, name):
    tr = Track(R["geo"], rot=R.get("rot", 0)); L = tr.raw_len
    segs = R["segments"]; total = sum(s["frames"] for s in segs)
    ticks = [s["tick"] for s in segs if "tick" in s]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", R["audio"](segs, total), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    cam_prev = (tr.cx, tr.cy, 1.0); snaps = []
    gaps_prev = {c: R["grid"][c] for c in R["cars"]}
    for si, sg in enumerate(segs):
        F = sg["frames"]; g0 = dict(gaps_prev); g1 = dict(g0); g1.update(sg.get("gaps", {}))
        for fr in range(F):
            t = fr / max(1, F - 1); te = ease(t)
            lapf = lerp(sg["laps"][0], sg["laps"][1], t if sg.get("linear", True) else te)
            lead_s = lapf * L
            pos = {}
            for c in R["cars"]:
                gap = lerp(g0[c], g1[c], te)
                if c in sg.get("stop", {}) and fr / F >= sg["stop"][c]: gap = g0[c] + (lapf - lerp(sg["laps"][0], sg["laps"][1], sg["stop"][c])) * L
                pos[c] = lead_s - gap
            # camera
            tgt = sg.get("cam", ("over",))
            if tgt[0] == "over": ctg = (tr.cx, tr.cy, 1.0)
            elif tgt[0] == "frac": x, y = tr.at(tgt[1]); ctg = (x, y, tgt[2])
            elif tgt[0] == "pan": x, y = tr.at(lerp(tgt[1], tgt[2], ease(t))); ctg = (x, y, tgt[3])
            else: x, y = tr.at(pos[tgt[1]] / L); ctg = (x, y, tgt[2])
            k = ease(min(1, fr / 24)) if si > 0 else 1
            cam = tuple(lerp(cam_prev[i], ctg[i], k) for i in range(3)) if tgt[0] != "car" or fr < 24 else ctg
            if tgt[0] == "car" and fr >= 24: cam = ctg
            im = Image.new("RGB", (NW, NH), BG)
            if sg.get("board"):
                results_board(im, *sg["board"])
            else:
                d = draw_map(im, tr, cam, R.get("start_frac", 0), sc_on=sg.get("sc", False))
                z = cam[2]; px = 7 + (z - 1) * 7
                for c in sorted(R["cars"], key=lambda c: pos[c]):
                    if c in sg.get("hide", ()) or (c in R.get("out", {}) and si >= R["out"][c]): continue
                    fr_ = pos[c] / L
                    x, y = project(tr, cam, tr.at(fr_))
                    if -20 < x < NW + 20 and -20 < y < 230:
                        draw_car(d, x, y, tr.heading(fr_), R["cars"][c][0], px, helmet=R["cars"][c][1])
                        if z >= 2.2 and c in sg.get("labels", ()):
                            tx(d, int(x) - tw(c) // 2 + 1, int(y) - int(px * .6) - 7, c, (6, 8, 16)); tx(d, int(x) - tw(c) // 2, int(y) - int(px * .6) - 8, c, INK)
                if sg.get("rain"):
                    rr = np.random.default_rng(fr)
                    for _ in range(int(90 * sg["rain"])):
                        x0 = int(rr.integers(0, NW + 10)); y0 = int(rr.integers(0, 205)); d.line([(x0, y0), (x0 - 2, y0 + 4)], fill=(120, 140, 175))
                if sg.get("sc") and (fr // 8) % 2: tx(d, NW - 22, 196, "SC", YEL, 2) if False else (d.rectangle([NW - 26, 190, NW - 5, 203], fill=YEL), tx(d, NW - 21, 194, "SC", (10, 10, 10)))
                if sg.get("inset"): sg["inset"](d, fr)
            im = panel(im, typed(sg.get("text", []), fr, sg.get("tspeed", 1.6)))
            if not sg.get("board") and not sg.get("nohud"):
                lead = max((c for c in R["cars"] if not (c in R.get("out", {}) and si >= R["out"][c])), key=lambda c: pos[c])
                hud(im, max(0, min(R["laps"], int(lapf) + (1 if lapf > 0 else 0))) if lapf < R["laps"] else R["laps"], R["laps"], R["names"][lead], R["cars"][lead][0], ticks, min(1, lapf / R["laps"]))
            if sg.get("outro") and fr > 40:
                d = ImageDraw.Draw(im); d.rectangle([0, 208, NW, 240], fill=(8, 10, 18)); tx(d, (NW - tw("THE PIXEL PADDOCK")) // 2, 221, "THE PIXEL PADDOCK", INK)
            if fr == F - 4: snaps.append(im)
            p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
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
def make_audio(tag, rain_segs=()):
    def f(segs, total):
        buf = np.zeros(int(SR * total / FPS) + SR); t0 = 0
        for m, t, du in MOTIF: mix(buf, tone(NOTE(m), du * 1.2, .10, "tri", 1.5), .3 + t)
        acc = 0
        for sg in segs:
            st = acc / FPS
            if sg.get("text"): mix(buf, tone(NOTE(76), .08, .07, "sq", 10), st + .1)
            if sg.get("tick") is not None: mix(buf, tone(NOTE(81), .12, .08, "sq", 8), st + .15); mix(buf, tone(NOTE(88), .2, .07, "sq", 6), st + .27)
            if sg.get("rain"):
                n = np.convolve(np.random.default_rng(3).uniform(-1, 1, int(SR * sg["frames"] / FPS)), np.ones(8) / 8, mode="same") * .06
                mix(buf, n, st)
            if sg.get("win"):
                for k, m in enumerate([72, 76, 79, 84]): mix(buf, tone(NOTE(m), .3 if k < 3 else 1.1, .11, "sq", 2.5), st + .4 + k * .15)
            if sg.get("outro"):
                for m, t, du in MOTIF: mix(buf, tone(NOTE(m), du * 1.2, .10, "tri", 1.5), st + .3 + t)
            acc += sg["frames"]
        # engine bed under the racing segments
        tt = np.arange(len(buf)) / SR; pitch = 90 + 30 * (np.sin(tt * 1.3) * .5 + .5)
        bed = np.sign(np.sin(2 * np.pi * np.cumsum(pitch) / SR)) * .022
        env = np.zeros(len(buf)); acc = 0
        for sg in segs:
            if not sg.get("board") and not sg.get("outro") and sg["laps"][1] > 0:
                env[int(acc / FPS * SR):int((acc + sg["frames"]) / FPS * SR)] = 1
            acc += sg["frames"]
        env = np.convolve(env, np.ones(SR // 4) / (SR // 4), mode="same")
        buf += bed * env
        buf = np.clip(buf, -1, 1); path = f"{OUT}/{tag}.wav"
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
        return path
    return f
