"""Lap-1 reel: places gained on the opening lap over a season (data: Jolpica, toolkit/data/jolpica_YYYY).
Scenes: start-light gantry intro -> diverging block chart (1 block = 1 place) -> best/worst single starts
(animated position ladders) -> takeaway -> outro. Self-made 8-bit sound.
Usage: python3 reel_lap1.py   -> out_reel/lap1_2026.mp4 (+ _sheet.png, _cover.png)"""
import os, sys, json, collections, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp import C
from post_usgp import GREEN
from reel_results import big, width, R, TEAM, hx, W, H, FPS, OUT
from reel_v3 import BG, slam, LOGO
from reel_v4 import tone, noise, mix, write_wav, NOTE, SR

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = (230, 80, 80)
LAMP_ON, LAMP_OFF = (235, 45, 40), (52, 44, 38)
TEAMMAP = {"RB F1 Team": "Racing Bulls", "Haas F1 Team": "Haas", "Cadillac F1 Team": "Cadillac", "Alpine F1 Team": "Alpine"}

# ---------- data ----------
def load(year=2026, rounds=20, min_starts=10):
    D = f"{HERE}/data/jolpica_{year}"
    tot, n, teams = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
    single = []
    for r in range(1, rounds + 1):
        Rc = json.load(open(f"{D}/res_{r}.json"))["MRData"]["RaceTable"]["Races"][0]
        L = json.load(open(f"{D}/lap1_{r}.json"))["MRData"]["RaceTable"]["Races"][0]["Laps"][0]["Timings"]
        p1 = {t["driverId"]: int(t["position"]) for t in L}
        for x in Rc["Results"]:
            code, g, did = x["Driver"]["code"], int(x["grid"]), x["Driver"]["driverId"]
            team = TEAMMAP.get(x["Constructor"]["name"], x["Constructor"]["name"]); teams[code][team] += 1
            if g == 0 or did not in p1: continue          # pit-lane starts / lap-1 retirements not counted
            gain = g - p1[did]; tot[code] += gain; n[code] += 1
            single.append((gain, code, Rc["raceName"], g, p1[did], team))
    rows = [(c, teams[c].most_common(1)[0][0], tot[c], n[c]) for c in tot if n[c] >= min_starts]
    rows.sort(key=lambda r: (-r[2], -r[2] / r[3]))
    return rows, max(single), min(single)

# ---------- pixel sprites ----------
CAR = ["RR..WW...WW..",
       "RR.BBBBBBBBB.F",
       "RRBBBBCCBBBBBF",
       "RR.BBBBBBBBB.F",
       "RR..WW...WW.."]
def car(d, x, y, col, px=4, left=False):
    """top-down car, nose pointing right (or left). (x, y) = top-left."""
    dark = (78, 70, 60)
    wmax = max(len(r) for r in CAR)
    for j, row in enumerate(CAR):
        for i, ch in enumerate(row):
            if ch == ".": continue
            c = {"R": dark, "W": dark, "C": (18, 16, 13), "B": col, "F": col}[ch]
            ii = (wmax - 1 - i) if left else i
            R(d, x + ii * px, y + j * px, x + ii * px + px, y + j * px + px, c)
    return wmax * px

def gantry(d, cx, y, lit):
    """F1 start gantry: 5 columns x 2 lamps; lit = number of columns on."""
    cw, gap = 120, 26; x0 = cx - (5 * cw + 4 * gap) // 2
    R(d, x0 - 40, y - 30, x0 + 5 * cw + 4 * gap + 40, y - 10, C["rule"])
    for k in range(5):
        x = x0 + k * (cw + gap)
        R(d, x, y, x + cw, y + 250, (30, 26, 22)); R(d, x + 10, y + 10, x + cw - 10, y + 240, (38, 33, 28))
        for j in range(2):
            col = LAMP_ON if k < lit else LAMP_OFF; ly = y + 30 + j * 110
            R(d, x + 25, ly, x + cw - 25, ly + 70, col)
            if k < lit: R(d, x + 33, ly + 8, x + 50, ly + 25, (255, 150, 140))   # pixel highlight

# ---------- reel ----------
def make(out_name="lap1_2026", year=2026, rounds=20, takeaway=None):
    rows, best, worst = load(year, rounds)
    N = len(rows)
    # timeline (frames)
    LIGHTS = [12, 24, 36, 48, 60]; OUTL = 82; INTRO = 140
    T = {}; t = INTRO + 10
    order = list(range(N - 1, -1, -1))                      # reveal bottom (worst) -> top
    tie = [i for i in range(N) if rows[i][2] == rows[0][2]]
    for i in order:
        if i in tie: continue
        T[i] = t; t += 9 if i > 3 else 22
    for i in tie: T[i] = t
    TOP_HIT = t; CH_END = TOP_HIT + 130
    CARD0 = CH_END; CARD_END = CARD0 + 150
    TK0 = CARD_END; TK_END = TK0 + 110 if takeaway else TK0
    OUT0 = TK_END; total = OUT0 + 120

    # ---- audio ----
    buf = np.zeros(int(SR * total / FPS) + SR)
    for f in LIGHTS: mix(buf, tone(NOTE["C4"], 0.18, 0.16, decay=3), f / FPS)
    mix(buf, noise(0.5, 0.22, 5), OUTL / FPS)
    for k, f in enumerate(("C5", "E5", "G5", "C6")): mix(buf, tone(NOTE[f], 0.12, 0.12), (OUTL + 4 + k * 5) / FPS)
    scale = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5", "C6"]
    for k, i in enumerate(sorted(T, key=lambda i: T[i])):
        if i in tie: continue
        mix(buf, tone(NOTE[scale[min(len(scale) - 1, k // 2)]], 0.08, 0.13), T[i] / FPS)
    for f in ("C5", "E5", "G5", "C6"): mix(buf, tone(NOTE[f], 0.8, 0.11, decay=3), TOP_HIT / FPS)
    mix(buf, noise(0.25, 0.2, 12), (TOP_HIT + 6) / FPS)
    mix(buf, tone(NOTE["A4"], 0.15, 0.14), (CH_END - 60) / FPS)
    for k in range(11): mix(buf, tone(NOTE[scale[k]], 0.05, 0.1), (CARD0 + 20 + k * 3) / FPS)
    for k in range(11): mix(buf, tone(NOTE[scale[10 - k]], 0.05, 0.1, kind="tri"), (CARD0 + 70 + k * 3) / FPS)
    if takeaway: mix(buf, tone(NOTE["A5"], 0.15, 0.15), TK0 / FPS); mix(buf, tone(NOTE["E5"], 0.2, 0.12), (TK0 + 5) / FPS)
    for k, f in enumerate(("C5", "E5", "G5")): mix(buf, tone(NOTE[f], 0.15, 0.15), (OUT0 + k * 8) / FPS)
    wav = f"{OUT}/{out_name}.wav"; write_wav(buf * 0.9, wav)

    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{OUT}/{out_name}.mp4"], stdin=subprocess.PIPE)

    AX, BLK, TOPY, ROW = 560, 9, 470, 52
    vmax = max(abs(r[2]) for r in rows)
    BLK = min(BLK, 300 // vmax)
    grid_cars = [hx(TEAM[t]) for t in ("McLaren", "Mercedes", "Ferrari", "Red Bull", "Williams", "Aston Martin")]
    snaps = {}
    for fi in range(total):
        im = BG.copy(); d = ImageDraw.Draw(im)
        if fi < INTRO:
            lit = sum(fi >= f for f in LIGHTS) if fi < OUTL else 0
            if fi < OUTL: big(im, (W - width("LAP 1 KINGS", "head", 9)) // 2, 260, "LAP 1 KINGS", "head", 9, C["ink"])
            gantry(d, W // 2, 340, lit)
            if fi < OUTL:
                for j, ln in enumerate(("WHO GAINS THE MOST", "PLACES ON LAP 1?")):
                    big(im, (W - width(ln, "head", 5)) // 2, 760 + j * 80, ln, "head", 5, C["ink"] if j == 0 else GREEN)
            else:
                slam(im, fi, OUTL, 0, 820, "LAP 1", "head", 22, GREEN, center=True)
                slam(im, fi, OUTL + 8, 0, 940, "KINGS", "head", 12, C["ink"], center=True)
                slam(im, fi, OUTL + 18, 0, 1040, f"PLACES GAINED ON LAP 1 · {year}", "label", 6, C["mute"], center=True)
            # grid of pixel cars launching at lights out
            for k, col in enumerate(grid_cars):
                gx = 160 + (k % 2) * 120 + (k // 2) * 260; gy = 1250 + (k % 2) * 110
                if fi >= OUTL:
                    u = (fi - OUTL) / 30; gx += int((u ** 2) * 1500 * (1 + 0.15 * (k % 3)))
                R(d, 140 + (k // 2) * 260, gy - 14, 150 + (k // 2) * 260, gy + 34, C["rule"])     # grid slot mark
                car(d, gx, gy, col, px=7)
            R(d, 40, 1500, W - 40, 1505, C["rule"])
            big(im, 40, 1560, f"{rounds} RACES · GRID VS END OF LAP 1", "label", 5, C["mute"])
            if fi == 70: snaps["intro"] = im.copy(); im.save(f"{OUT}/{out_name}_cover.png")
        elif fi < CH_END:
            big(im, 40, 300, "LAP 1 KINGS", "head", 9, C["ink"])
            big(im, 40, 360, f"PLACES GAINED · {year} · {rounds} RACES", "label", 5, C["mute"])
            R(d, 40, 390, W - 40, 400, C["ink"])
            R(d, AX - 1, TOPY - 20, AX + 2, TOPY + N * ROW, C["rule"])
            big(im, AX + 14, TOPY - 26, "GAINED >", "label", 4, GREEN)
            big(im, AX - 14, TOPY - 26, "< LOST", "label", 4, NEG, right=True)
            for i, (code, team, v, n) in enumerate(rows):
                if i not in T or fi < T[i]: continue
                y = TOPY + i * ROW; age = fi - T[i]
                u = min(1, age / 6); dx = int((1 - (1 - (1 - u) ** 3)) * 60)
                tc = hx(TEAM[team]); rank = "1=" if i in tie else str(i + 1)
                big(im, 40, y + 38, rank, "head", 4, C["mute"])
                nb = min(abs(v), int(abs(v) * min(1, age / 12)) + 1) if v else 0
                pos = v >= 0
                # label on the opposite side of the axis
                if pos:
                    R(d, AX - 26, y + 8, AX - 18, y + 42, tc); big(im, AX - 36 - dx, y + 40, code, "head", 5, C["ink"], right=True)
                else:
                    R(d, AX + 18, y + 8, AX + 26, y + 42, tc); big(im, AX + 36 + dx, y + 40, code, "head", 5, C["ink"])
                col = GREEN if pos else NEG
                for b in range(nb):
                    bx = AX + 4 + b * BLK if pos else AX - 4 - (b + 1) * BLK
                    R(d, bx, y + 12, bx + BLK - 2, y + 38, col)
                tip = AX + 4 + nb * BLK if pos else AX - 4 - nb * BLK
                if v:
                    cw = car(d, tip + 6 if pos else tip - 6 - 14 * 4, y + 15, tc, px=4, left=not pos)
                    lab = f"{v:+d}"
                    if pos: big(im, tip + 16 + cw, y + 40, lab, "head", 4, col)
                    else: big(im, tip - 16 - cw, y + 40, lab, "head", 4, col, right=True)
                else:
                    big(im, AX + 36 + 120, y + 40, "±0", "head", 4, C["mute"])
            if fi >= TOP_HIT + 10:
                big(im, 40, TOPY + N * ROW + 60, "1 BLOCK = 1 PLACE · MIN. 10 STARTS", "label", 5, C["mute"])
                big(im, 40, TOPY + N * ROW + 105, "LAP-1 RETIREMENTS NOT COUNTED · DATA: JOLPICA", "label", 4, C["mute"])
            # Mercedes callout: frame the champions' rows
            if fi >= CH_END - 70:
                mer = [i for i, r in enumerate(rows) if r[1] == "Mercedes"]
                blink = ((fi - (CH_END - 70)) // 8) % 2 == 0 or fi > CH_END - 40
                if blink:
                    for i in mer:
                        y = TOPY + i * ROW
                        for (a, b_, c_, e) in ((30, y + 2, W - 30, y + 6), (30, y + ROW - 6, W - 30, y + ROW - 2), (30, y + 2, 34, y + ROW - 2), (W - 34, y + 2, W - 30, y + ROW - 2)):
                            R(d, a, b_, c_, e, C["ink"])
                    for i in mer:
                        y = TOPY + i * ROW; big(im, W - 50, y + 36, "< CHAMPIONS", "label", 4, C["ink"], right=True)
            if TOP_HIT <= fi < TOP_HIT + 8:
                off = [6, -6, 4, -4, 3, -2, 1, 0][fi - TOP_HIT]
                im = im.transform(im.size, Image.AFFINE, (1, 0, off, 0, 1, 0), fillcolor=C["paper"])
                if fi - TOP_HIT < 2: im = Image.blend(im, Image.new("RGB", (W, H), GREEN), 0.2)
            if fi == CH_END - 20: snaps["chart"] = im.copy()
        elif fi < CARD_END:
            k = fi - CARD0
            slam(im, fi, CARD0, 0, 330, "ONE LAP, ONE STORY", "head", 6, C["ink"], center=True)
            slam(im, fi, CARD0 + 4, 0, 390, "BIGGEST SWINGS OF THE SEASON", "label", 6, C["mute"], center=True)
            for side, (gain, code, race, g, l1, team) in enumerate((best, worst)):
                x0 = 60 + side * 500; col = GREEN if gain > 0 else NEG; tc = hx(TEAM[team])
                t0 = CARD0 + 10 + side * 50
                if fi < t0: continue
                R(d, x0, 450, x0 + 460, 1640, C["box"]); R(d, x0, 450, x0 + 460, 462, col)
                big(im, x0 + 30, 540, "BEST" if gain > 0 else "WORST", "label", 6, col)
                big(im, x0 + 30, 630, code, "head", 9, C["ink"]); R(d, x0 + 30, 650, x0 + 230, 658, tc)
                rn = race.replace(" Grand Prix", "").upper().replace("BRAZILIAN", "SAO PAULO").replace("CANADIAN", "CANADA")
                big(im, x0 + 30, 710, rn, "label", 5, C["mute"])
                # ladder of 22 slots
                ly0, sl = 760, 30
                for s in range(22):
                    yy = ly0 + s * sl
                    R(d, x0 + 30, yy + 4, x0 + 50, yy + sl - 4, C["rule"])
                    if s in (0, 9, 19, 21): big(im, x0 + 60, yy + 24, f"P{s + 1}", "label", 3, C["mute"])
                u = min(1, max(0, (fi - t0 - 10) / 28)); e = u * u * (3 - 2 * u)
                pos_now = g + (l1 - g) * e
                yy = ly0 + (pos_now - 1) * sl
                R(d, x0 + 160, ly0 + (g - 1) * sl + 8, x0 + 175, ly0 + (g - 1) * sl + sl - 8, C["mute"])   # start marker
                car(d, x0 + 180, int(yy) - 1, tc, px=6)
                if u >= 1:
                    big(im, x0 + 300, ly0 + (g - 1) * sl + 26, f"P{g}", "head", 4, C["mute"])
                    big(im, x0 + 300, ly0 + (l1 - 1) * sl + 26, f"P{l1}", "head", 4, col)
                    big(im, x0 + 230, 1610, f"{gain:+d}", "head", 9, col, right=False) if False else big(im, x0 + 430, 1615, f"{gain:+d}", "head", 9, col, right=True)
            if fi == CARD_END - 2: snaps["cards"] = im.copy()
        elif fi < TK_END:
            slam(im, fi, TK0, 0, 560, "THE TAKEAWAY", "label", 8, GREEN, center=True)
            yb = 800
            for i, line in enumerate(takeaway):
                sc = 16 if i == 0 else 7
                while width(line, "head", sc) > 980: sc -= 1
                slam(im, fi, TK0 + 10 + i * 14, 0, yb, line, "head", sc, (NEG if i == 0 else C["ink"]), center=True)
                yb += 170 if i == 0 else 110
            if fi == TK_END - 1: snaps["ins"] = im.copy()
        else:
            k = fi - OUT0
            slam(im, fi, OUT0, 0, 480, "FOLLOW", "head", 16, GREEN, center=True)
            slam(im, fi, OUT0 + 14, 0, 620, "THE PIXEL", "head", 11, C["ink"], center=True)
            slam(im, fi, OUT0 + 22, 0, 740, "PADDOCK", "head", 11, C["ink"], center=True)
            if k >= 32:
                im.paste(LOGO, ((W - 360) // 2, 800))
                s_ = "@THE.PIXEL.PADDOCK"; big(im, (W - width(s_, "labelb", 6)) // 2, 1230, s_, "labelb", 6, C["mute"])
            slam(im, fi, OUT0 + 50, 0, 1340, "FOR F1 DATA,", "head", 6, C["ink"], center=True)
            slam(im, fi, OUT0 + 58, 0, 1410, "CONDENSED.", "head", 6, GREEN, center=True)
            if fi == total - 1: snaps["outro"] = im.copy()
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    keys = [k for k in ("intro", "chart", "cards", "ins", "outro") if k in snaps]
    sh = Image.new("RGB", (540 * len(keys), 960))
    for i, nm in enumerate(keys): sh.paste(snaps[nm].resize((540, 960)), (i * 540, 0))
    sh.save(f"{OUT}/{out_name}_sheet.png")
    for nm in keys: snaps[nm].save(f"{OUT}/{out_name}_{nm}.png")
    print("frames", total, "sec", round(total / FPS, 1), "best", best, "worst", worst)

if __name__ == "__main__":
    rows, _, _ = load()
    mer = sum(r[2] for r in rows if r[1] == "Mercedes")
    make(takeaway=[f"{mer:+d}", "MERCEDES ON LAP 1", "STILL WON THE TITLE"])
