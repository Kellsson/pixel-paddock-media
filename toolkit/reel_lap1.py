"""Lap-1 reel: places gained on the opening lap over a season (data: Jolpica, toolkit/data/jolpica_YYYY).
Scenes: staggered title intro -> diverging block chart (1 block = 1 place) with kings/champions highlights
-> best and worst single start (one scene each, animated position ladder) -> takeaway -> outro. Self-made 8-bit sound.
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

def meta(year=2026, rounds=20):
    D = f"{HERE}/data/jolpica_{year}"
    total = len(json.load(open(f"{D}/races.json"))["MRData"]["RaceTable"]["Races"])
    names = {}
    for r in range(1, rounds + 1):
        for x in json.load(open(f"{D}/res_{r}.json"))["MRData"]["RaceTable"]["Races"][0]["Results"]:
            names[x["Driver"]["code"]] = x["Driver"]["familyName"].upper()
    return total, names

def gp_name(race):
    n = race.replace(" Grand Prix", " GP").upper()
    return {"BRAZILIAN GP": "SAO PAULO GP"}.get(n, n)

def dim(im, y0, y1, a=0.68):
    box = (0, int(y0), W, int(y1)); reg = im.crop(box)
    im.paste(Image.blend(reg, Image.new("RGB", reg.size, C["paper"]), a), box)

def frame_rows(d, y0, y1, col):
    for (a, b, c, e) in ((30, y0, W - 30, y0 + 4), (30, y1 - 4, W - 30, y1), (30, y0, 34, y1), (W - 34, y0, W - 30, y1)):
        R(d, a, b, c, e, col)


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

# ---------- reel ----------
def make(out_name="lap1_2026", year=2026, rounds=20, takeaway=None):
    rows, best, worst = load(year, rounds); total_rounds, NAMES = meta(year, rounds)
    N = len(rows)
    tie = [i for i in range(N) if rows[i][2] == rows[0][2]]
    mer = [i for i, r in enumerate(rows) if r[1] == "Mercedes"]
    mer_sum = sum(rows[i][2] for i in mer)
    # ---- timeline (frames @30fps) ----
    IN = dict(f1=0, lap=14, kings=28, after=52, q1=76, q2=84); INTRO = 140
    T = {}; t = INTRO + 12
    for i in range(N - 1, -1, -1):
        if i in tie: continue
        T[i] = t; t += 9 if i > 3 else 20
    for i in tie: T[i] = t
    TOP_HIT = t
    HL1 = TOP_HIT + 30; HL2 = HL1 + 80; CH_END = HL2 + 95
    CARD = [CH_END, CH_END + 165]; CARD_END = CARD[1] + 165
    TK0 = CARD_END; TK_END = TK0 + 110 if takeaway else TK0
    OUT0 = TK_END; total = OUT0 + 120

    # ---- audio ----
    buf = np.zeros(int(SR * total / FPS) + SR)
    for k, t0 in enumerate(IN.values()):
        if k < 4: mix(buf, noise(0.10, 0.18) + tone(110, 0.10, 0.15), t0 / FPS)
    mel = [("C5", 14, .12), ("E5", 21, .12), ("G5", 28, .25), ("C6", 52, .3), ("G5", 76, .12), ("C6", 84, .4)]
    for nn, f0, du in mel: mix(buf, tone(NOTE[nn], du, 0.1, decay=4), f0 / FPS)
    scale = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5", "C6"]
    for k, i in enumerate(sorted(T, key=lambda i: T[i])):
        if i in tie: continue
        mix(buf, tone(NOTE[scale[min(len(scale) - 1, k // 2)]], 0.08, 0.13), T[i] / FPS)
    for f in ("C5", "E5", "G5", "C6"): mix(buf, tone(NOTE[f], 0.8, 0.11, decay=3), TOP_HIT / FPS)
    mix(buf, noise(0.25, 0.2, 12), (TOP_HIT + 6) / FPS)
    for f in ("C5", "G5"): mix(buf, tone(NOTE[f], 0.3, 0.12, decay=4), HL1 / FPS)
    for f in ("E4", "C4"): mix(buf, tone(NOTE[f], 0.35, 0.14, kind="tri", decay=3), HL2 / FPS); 
    mix(buf, tone(NOTE["C4"] / 2, 0.5, 0.14, kind="tri", decay=3), (HL2 + 8) / FPS)
    for c0, (gain, *_ ) in zip(CARD, (best, worst)):
        mix(buf, noise(0.10, 0.18) + tone(110, 0.10, 0.15), c0 / FPS)
        mix(buf, tone(NOTE["A4"], 0.12, 0.13), (c0 + 28) / FPS)
        seq = scale if gain > 0 else scale[::-1]
        for k in range(11): mix(buf, tone(NOTE[seq[k]], 0.06, 0.1), (c0 + 50 + k * 3.5) / FPS)
        mix(buf, tone(NOTE["C6" if gain > 0 else "C4"], 0.4, 0.14, decay=4), (c0 + 92) / FPS)
        mix(buf, tone(NOTE["E5" if gain > 0 else "D4"], 0.3, 0.12, decay=4), (c0 + 108) / FPS)
    if takeaway: mix(buf, tone(NOTE["A5"], 0.15, 0.15), TK0 / FPS); mix(buf, tone(NOTE["E5"], 0.2, 0.12), (TK0 + 5) / FPS)
    for k, f in enumerate(("C5", "E5", "G5")): mix(buf, tone(NOTE[f], 0.15, 0.15), (OUT0 + k * 8) / FPS)
    wav = f"{OUT}/{out_name}.wav"; write_wav(buf * 0.9, wav)

    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{OUT}/{out_name}.mp4"], stdin=subprocess.PIPE)

    AX, TOPY, ROW = 560, 470, 52
    vmax = max(abs(r[2]) for r in rows); BLK = min(10, 330 // vmax)
    snaps = {}
    for fi in range(total):
        im = BG.copy(); d = ImageDraw.Draw(im)
        if fi < INTRO:
            slam(im, fi, IN["f1"], 0, 560, "F1", "head", 14, C["ink"], center=True)
            slam(im, fi, IN["lap"], 0, 810, "LAP 1", "head", 22, GREEN, center=True)
            slam(im, fi, IN["kings"], 0, 980, "KINGS", "head", 14, C["ink"], center=True)
            slam(im, fi, IN["after"], 0, 1110, f"AFTER {rounds} OF {total_rounds} RACES · {year}", "label", 6, C["mute"], center=True)
            slam(im, fi, IN["q1"], 0, 1330, "WHO GAINS THE MOST", "head", 5, C["ink"], center=True)
            slam(im, fi, IN["q2"], 0, 1410, "PLACES OFF THE START?", "head", 5, GREEN, center=True)
            if fi == 115: snaps["intro"] = im.copy(); im.save(f"{OUT}/{out_name}_cover.png")
        elif fi < CH_END:
            big(im, 40, 300, "F1 LAP 1 KINGS", "head", 8, C["ink"])
            big(im, 40, 360, f"PLACES GAINED · AFTER {rounds} OF {total_rounds} RACES", "label", 5, C["mute"])
            R(d, 40, 390, W - 40, 400, C["ink"])
            R(d, AX - 1, TOPY - 20, AX + 2, TOPY + N * ROW, C["rule"])
            big(im, AX + 14, TOPY - 26, "GAINED >", "label", 4, GREEN)
            big(im, AX - 14, TOPY - 26, "< LOST", "label", 4, NEG, right=True)
            for i, (code, team, v, n) in enumerate(rows):
                if i not in T or fi < T[i]: continue
                y = TOPY + i * ROW; age = fi - T[i]
                tc = hx(TEAM[team]); rank = "1=" if i in tie else str(i + 1)
                big(im, 40, y + 38, rank, "head", 4, C["mute"])
                nb = min(abs(v), int(abs(v) * min(1, age / 12)) + 1) if v else 0
                pos = v >= 0; col = GREEN if pos else NEG
                if pos:
                    R(d, AX - 26, y + 8, AX - 18, y + 42, tc); big(im, AX - 36, y + 40, code, "head", 5, C["ink"], right=True)
                else:
                    R(d, AX + 18, y + 8, AX + 26, y + 42, tc); big(im, AX + 36, y + 40, code, "head", 5, C["ink"])
                for b in range(nb):
                    bx = AX + 4 + b * BLK if pos else AX - 4 - (b + 1) * BLK
                    R(d, bx, y + 12, bx + BLK - 2, y + 38, col)
                tip = AX + 4 + nb * BLK if pos else AX - 4 - nb * BLK
                if age >= 10:
                    if pos: big(im, tip + 14, y + 40, f"{v:+d}", "head", 4, col)
                    else: big(im, tip - 14, y + 40, f"{v:+d}", "head", 4, col, right=True)
            big(im, 40, TOPY + N * ROW + 60, "1 BLOCK = 1 PLACE · MIN. 10 STARTS", "label", 5, C["mute"])
            big(im, 40, TOPY + N * ROW + 105, "LAP-1 RETIREMENTS NOT COUNTED · DATA: JOLPICA", "label", 4, C["mute"])
            # --- highlights: dim the rest, frame the rows, caption replaces the subtitle ---
            hl = None
            if HL1 <= fi < HL2:
                names = " & ".join(NAMES[rows[i][0]] for i in tie)
                hl = (tie, GREEN, f"KINGS: {names}, +{rows[0][2]} EACH")
            elif HL2 <= fi < CH_END:
                hl = (mer, NEG, f"THE CHAMPIONS: MERCEDES, {mer_sum:+d} COMBINED")
            if hl:
                idx, hc, cap = hl
                for i in range(N):
                    if i not in idx: dim(im, TOPY + i * ROW, TOPY + (i + 1) * ROW)
                d = ImageDraw.Draw(im)
                R(d, 40, 318, W - 40, 378, C["paper"])
                if (fi - (HL1 if hc == GREEN else HL2)) >= 6:
                    if max(idx) - min(idx) + 1 == len(idx): frame_rows(d, TOPY + min(idx) * ROW, TOPY + (max(idx) + 1) * ROW, hc)
                    else:
                        for i in idx: frame_rows(d, TOPY + i * ROW, TOPY + (i + 1) * ROW, hc)
                    sc = 6
                    while width(cap, "label", sc) > W - 80: sc -= 1
                    big(im, 40, 362, cap, "label", sc, hc)
            if TOP_HIT <= fi < TOP_HIT + 8:
                off = [6, -6, 4, -4, 3, -2, 1, 0][fi - TOP_HIT]
                im = im.transform(im.size, Image.AFFINE, (1, 0, off, 0, 1, 0), fillcolor=C["paper"])
                if fi - TOP_HIT < 2: im = Image.blend(im, Image.new("RGB", (W, H), GREEN), 0.2)
            if fi == HL1 - 2: snaps["chart"] = im.copy()
            if fi == HL2 - 2: snaps["hl1"] = im.copy()
            if fi == CH_END - 2: snaps["hl2"] = im.copy()
        elif fi < CARD_END:
            side = 0 if fi < CARD[1] else 1; c0 = CARD[side]
            gain, code, race, g, l1, team = (best, worst)[side]
            col = GREEN if gain > 0 else NEG; tc = hx(TEAM[team])
            slam(im, fi, c0, 0, 300, "BEST START" if gain > 0 else "WORST START", "head", 9, col, center=True)
            slam(im, fi, c0 + 4, 0, 370, f"OF {year} · ONE LAP, ONE STORY", "label", 5, C["mute"], center=True)
            slam(im, fi, c0 + 12, 0, 520, NAMES[code], "head", 8, C["ink"], center=True)
            if fi >= c0 + 18:
                wn = width(NAMES[code], "head", 8); R(d, (W - wn) // 2, 545, (W + wn) // 2, 555, tc)
            slam(im, fi, c0 + 18, 0, 610, gp_name(race), "label", 6, C["mute"], center=True)
            # ladder
            LX, LY, SL = 60, 690, 40
            for s_ in range(22):
                yy = LY + s_ * SL
                R(d, LX, yy + 4, LX + 280, yy + SL - 4, C["box"])
                big(im, LX + 10, yy + 31, f"P{s_ + 1}", "label", 4, C["mute"] if s_ + 1 in (g, l1) else C["rule"])
            u = min(1, max(0, (fi - c0 - 50) / 40)); e = u * u * (3 - 2 * u)
            pnow = g + (l1 - g) * e
            # trail
            a, b_ = sorted((g, pnow))
            if u > 0: R(d, LX + 288, LY + (a - 1) * SL + 14, LX + 298, LY + (b_ - 1) * SL + SL - 14, col)
            R(d, LX, LY + (g - 1) * SL + 6, LX + 6, LY + g * SL - 6, C["mute"])
            car(d, LX + 120, int(LY + (pnow - 1) * SL + 3), tc, px=7)
            # facts column
            FX = 440
            if fi >= c0 + 28:
                big(im, FX, 860, "STARTED", "label", 6, C["mute"]); big(im, FX, 990, f"P{g}", "head", 12, C["ink"])
            if fi >= c0 + 92:
                big(im, FX, 1140, "AFTER LAP 1", "label", 6, C["mute"]); big(im, FX, 1270, f"P{l1}", "head", 12, col)
            if fi >= c0 + 108:
                big(im, FX, 1420, f"{gain:+d} PLACES", "head", 7, col)
            if fi == c0 + 160: snaps[f"card{side}"] = im.copy()
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
    keys = [k for k in ("intro", "chart", "hl1", "hl2", "card0", "card1", "ins", "outro") if k in snaps]
    sh = Image.new("RGB", (360 * len(keys), 640))
    for i, nm in enumerate(keys): sh.paste(snaps[nm].resize((360, 640)), (i * 360, 0))
    sh.save(f"{OUT}/{out_name}_sheet.png")
    for nm in keys: snaps[nm].save(f"{OUT}/{out_name}_{nm}.png")
    print("frames", total, "sec", round(total / FPS, 1))

if __name__ == "__main__":
    rows, _, _ = load()
    mer = sum(r[2] for r in rows if r[1] == "Mercedes")
    make(takeaway=[f"{mer:+d}", "MERCEDES ON LAP 1", "STILL WON THE TITLE"])
