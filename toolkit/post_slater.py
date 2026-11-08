import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
from post_usgp import hx, r, p, num, two_col, GREEN
from post_honda import tl_box
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_slater"); os.makedirs(OUT, exist_ok=True)
DATE = "23.10.26"
INK = hx("#e5e7eb"); MUT = hx("#64748b"); BG = hx("#0e131b"); BOX = hx("#1f2937"); GOLD = hx("#facc15")
AUDI = hx("#d1d5db")  # neutral silver, no livery art

F = {"A": "010101111101101", "C": "111100100100111", "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
     "G": "111100101101111", "I": "111010010010111", "J": "001001001101111", "L": "100100100100111", "M": "101111111101101",
     "N": "110101101101101", "O": "111101101101111", "P": "111101111100100", "R": "110101110101101", "S": "111100111001111",
     "T": "111010010010010", "U": "101101101101111", "V": "101101101101010", "X": "101101010101101", "B": "110101110101110",
     "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
     "5": "111100111001111", "6": "111100111101111", "7": "111001010010010", "8": "111101111101111", "9": "111101111001111",
     "W": "101101111111101", "H": "101101111101101", "K": "101110100110101", "Y": "101101010010010",
     " ": "000000000000000", "-": "000000111000000", ".": "000000000000010", "+": "000010111010000"}
def tx(d, x, y, s, c, sc=1):
    for ch in s:
        g = F[ch]
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == "1": r(d, x + i * sc, y + j * sc, x + i * sc + sc - 1, y + j * sc + sc - 1, c)
        x += 4 * sc
def tw(s, sc=1): return len(s) * 4 * sc - sc

def trophy(d, x, y, c=GOLD):
    r(d, x, y, x + 6, y + 3, c); r(d, x + 1, y + 4, x + 5, y + 4, c); r(d, x + 2, y + 5, x + 4, y + 6, c); r(d, x + 1, y + 7, x + 5, y + 7, c)

# ---------- covers
def scene_bars():
    """Wins per season, title trophies; right panel: the two FP1 dates."""
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    base = 98; data = [("2023", "GJ", 16, True), ("2024", "IF4", 15, True), ("2025", "FR", 8, True), ("2026", "F3", 1, False)]
    tx(d, 8, 6, "WINS PER SEASON", MUT)
    for i, (yr, ser, v, title) in enumerate(data):
        x = 10 + i * 30; top = base - v * 4
        r(d, x, top, x + 20, base, GOLD if title else GREEN)
        tx(d, x + 10 - tw(str(v)) // 2, top - 7, str(v), INK)
        if title: trophy(d, x + 7, top - 17)
        tx(d, x + 10 - tw(ser) // 2, base + 3, ser, INK); tx(d, x + 10 - tw(yr) // 2, base + 10, yr, MUT)
    r(d, 6, base, 128, base, hx("#334155"))
    tx(d, 103, 76, "P2", GREEN)
    # FP1 panel
    r(d, 136, 14, 194, 92, BOX); d.rectangle([136, 14, 194, 92], outline=GREEN)
    tx(d, 165 - tw("FP1", 2) // 2, 20, "FP1", GREEN, 2)
    for k, (dt, cc) in enumerate((("30.10", "MEX"), ("06.11", "SAO"))):
        y = 40 + k * 24; r(d, 142, y, 188, y + 18, hx("#123018"))
        tx(d, 145, y + 3, dt, INK); tx(d, 145, y + 10, cc, GREEN)
    return im

def scene_ladder():
    """Staircase: each step one category with year, top step F1 FP1 in green."""
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    steps = [("GJ", "2023", True), ("F4", "2024", True), ("FR", "2025", True), ("F3", "2026", False), ("F2", "2027", False)]
    sw, sh = 30, 15; x0, base = 8, 108
    for i, (ser, yr, title) in enumerate(steps):
        x = x0 + i * sw; top = base - (i + 1) * sh
        col = hx("#334155") if ser == "F2" else MUT
        r(d, x, top, x + sw - 2, base, BOX); r(d, x, top, x + sw - 2, top + 1, col)
        tx(d, x + 3, top + 4, ser, INK); tx(d, x + 3, top + 11, yr, MUT if ser != "F2" else hx("#94a3b8"))
        if title: trophy(d, x + 19, top + 4)
    # top step: F1 FP1
    x = x0 + 5 * sw; top = base - 6 * sh
    r(d, x, top, x + 38, base, hx("#123018")); r(d, x, top, x + 38, top + 1, GREEN)
    tx(d, x + 4, top + 4, "F1", GREEN, 2); tx(d, x + 4, top + 17, "FP1", GREEN); tx(d, x + 4, top + 24, "X2", INK)
    # driver marker on F3 step, arrow to F1
    fx = x0 + 3 * sw + 18; fy = base - 4 * sh - 8
    r(d, fx, fy, fx + 6, fy + 6, AUDI); r(d, fx + 1, fy + 2, fx + 5, fy + 3, hx("#111827"))
    tx(d, 8, 6, "THE LADDER", MUT)
    return im

def scene_calendar():
    """Three-week calendar strip, Mon-Sun, 26 Oct - 8 Nov plus this week; FP1 Fridays in green."""
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 8, 6, "OCT-NOV 2026", MUT)
    days = "MTWTFSS"
    for i, ch in enumerate(["MO", "TU", "WE", "TH", "FR", "SA", "SU"]):
        tx(d, 12 + i * 26 + 5, 18, ch, MUT)
    start = 19  # Monday 19 Oct
    dates = []
    for w in range(3):
        for i in range(7):
            n = start + w * 7 + i
            dates.append(n if n <= 31 else n - 31)
    for k, n in enumerate(dates):
        w, i = divmod(k, 7); x = 10 + i * 26; y = 28 + w * 28
        fp1 = (w == 1 and i == 4) or (w == 2 and i == 4)
        now = (w == 0 and i == 4)
        fill = hx("#123018") if fp1 else BOX
        r(d, x, y, x + 22, y + 24, fill)
        if fp1: d.rectangle([x, y, x + 22, y + 24], outline=GREEN)
        if now: d.rectangle([x, y, x + 22, y + 24], outline=MUT)
        tx(d, x + 3, y + 3, f"{n:02d}", INK if fp1 else (INK if now else hx("#94a3b8")))
        if fp1: tx(d, x + 3, y + 12, "FP1", GREEN)
        if now: tx(d, x + 3, y + 12, "USA", MUT)
        if w == 1 and i == 6: tx(d, x + 3, y + 12, "MEX", hx("#94a3b8"))
        if w == 2 and i == 6: tx(d, x + 3, y + 12, "SAO", hx("#94a3b8"))
    return im

# ---------- boxes
def career_box(im, d, top):
    rows = [("2023", "Ginetta Junior", "16", "P1"), ("2024", "Italian F4", "15", "P1"), ("2024", "F4 UAE", "2", "P1"),
            ("2025", "Formula Regional EU", "8", "P1"), ("2026", "FIA F3, Trident", "1", "P2")]
    h = 140 + 55 * len(rows); box(im, d, top, h, "CAREER LOG, MAIN SERIES"); b = top + 105
    text(im, 70, b, "YEAR", "label", C["mute"]); text(im, 250, b, "SERIES", "label", C["mute"])
    text(im, 800 - tlen("label", "WINS"), b, "WINS", "label", C["mute"]); text(im, W - 70 - tlen("label", "POS"), b, "POS", "label", C["mute"])
    b += 60
    for yr, s, wn, pos in rows:
        hi = yr == "2026"
        if hi: R(d, 55, b - 40, W - 55, b + 10, GREEN)
        col = C["onred"] if hi else C["ink"]
        text(im, 70, b, yr, "body", C["onred"] if hi else C["mute"]); text(im, 250, b, s, "body", col)
        text(im, 800 - tlen("body", wn), b, wn, "body", col); text(im, W - 70 - tlen("body", pos), b, pos, "body", col)
        b += 55
    return top + h

def tiles(im, d, top):
    vals = [("18", "YEARS", "born Aug 2008"), ("5", "TITLES", "since 2022"), ("8", "PODIUMS", "F3 2026"),
            ("3", "POLES", "F3 2026"), ("2", "FP1 RUNS", "MEX + SAO"), ("4", "FP1 QUOTA", "per team")]
    tw_, th = 315, 205; x0 = 40
    for i, (big, unit, cap) in enumerate(vals):
        x = x0 + (i % 3) * (tw_ + 27); y = top + (i // 3) * (th + 25)
        R(d, x, y, x + tw_, y + th, C["ink"]); R(d, x + 5, y + 5, x + tw_ - 5, y + th - 5, C["box"])
        text(im, x + 25, y + 85, big, "head", GREEN if i == 4 else C["ink"])
        text(im, x + 25, y + 130, unit, "labelb", C["mute"])
        text(im, x + 25, y + 175, cap, "body", C["ink"])
    return top + 2 * th + 25

def slots_box(im, d, top):
    """Audi's 4 mandatory rookie FP1 sessions in 2026."""
    h = 330; box(im, d, top, h, "AUDI ROOKIE FP1S, 2026"); y = top + 95
    sl = [("ARON", "done", False), ("ARON", "done", False), ("SLATER", "MEX 30.10", True), ("SLATER", "SAO 06.11", True)]
    w = 225
    for i, (n, t, hi) in enumerate(sl):
        x = 70 + i * (w + 15)
        R(d, x, y, x + w, y + 120, GREEN if hi else C["rule"])
        text(im, x + 20, y + 50, n, "labelb", C["onred"] if hi else C["ink"])
        text(im, x + 20, y + 100, t, "body", C["onred"] if hi else C["mute"])
    text(im, 70, y + 185, "Rule: 4 FP1 runs per team for young drivers.", "body", C["ink"])
    return top + h

FACTS = [("DRIVER", "Freddie Slater, 18, GB"), ("TEAM", "Audi, car R26"), ("SESSIONS", "FP1 Mexico City, Sao Paulo"),
         ("DATES", "Fri 30 Oct, Fri 6 Nov"), ("2027", "Formula 2, Invicta Racing")]

def v1():
    im, d = page(1, 3, DATE)
    y = headline(im, "AUDI GIVES SLATER, 18, TWO F1 PRACTICE RUNS")
    y = cover_image(im, d, scene_bars(), y + 75, "52.19N 1.71W")
    fig(im, y + 60, "Wins per season 2023-26, plus both FP1 dates.")
    body(im, y + 95, "F3 runner-up drives FP1 in Mexico and Sao Paulo.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/1_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "FROM F3 RUNNER-UP TO AN F1 FRIDAY")
    yy = two_col(im, d, y, "Slater was Audi's first junior signing in January. He finished F3 second, about 14 points off champion Ugo Ugochukwu.",
                 "Audi's racing director Allan McNish called it the right time for the step. In 2027 Slater races F2 for Invicta.")
    fact_file(im, d, yy + 50, FACTS)
    footer(im, d, 2, "VIA F1.COM"); im.save(f"{OUT}/1_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "4 TITLES IN 3 SEASONS, THEN F3")
    y = body(im, y + 45, "Fewer wins with every step up, but a title each year until F3.")
    career_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/1_3_context.png")

def v2():
    im, d = page(1, 3, DATE)
    y = headline(im, "SLATER, 18, SKIPS AHEAD: F1 FP1 BEFORE F2")
    y = cover_image(im, d, scene_ladder(), y + 75, "52.19N 1.71W")
    fig(im, y + 60, "The ladder: Ginetta to F3, F2 next, F1 FP1 now.")
    body(im, y + 95, "Audi puts its junior in the R26 on 30 Oct and 6 Nov.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/2_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "WHY AUDI NEEDS A ROOKIE ON FRIDAYS")
    yy = two_col(im, d, y, "Teams must give young drivers four FP1 runs a year. Alpine junior Paul Aron already did two for Audi.",
                 "Slater covers the last two, taking the car of Nico Hulkenberg in one session and Gabriel Bortoleto in the other.")
    slots_box(im, d, yy + 50)
    footer(im, d, 2, "VIA GPREMIO"); im.save(f"{OUT}/2_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "SLATER IN SIX NUMBERS")
    y = body(im, y + 45, "Champion in Italian F4 and Formula Regional Europe, F3 runner-up as a rookie.")
    tiles(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/2_3_context.png")

def v3():
    im, d = page(1, 3, DATE)
    y = headline(im, "2 FRIDAYS, 2 FP1S: SLATER'S AUDI DEBUT")
    y = cover_image(im, d, scene_calendar(), y + 75, "19.43N 99.13W")
    fig(im, y + 60, "Calendar: Austin now, FP1 on 30 Oct and 6 Nov.")
    body(im, y + 95, "The 18-year-old F3 runner-up drives the Audi R26.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/3_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "ONE SESSION EACH IN TWO AUDI CARS")
    yy = two_col(im, d, y, "Slater replaces Hulkenberg in one FP1 and Bortoleto in the other. It is his first F1 race weekend.",
                 "He won one F3 feature race, in Budapest, took three poles and eight podiums, and was the top rookie.")
    fact_file(im, d, yy + 50, FACTS)
    footer(im, d, 2, "VIA F1.COM"); im.save(f"{OUT}/3_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "FROM GINETTAS TO THE R26")
    y = body(im, y + 45, "Five years from junior sports cars to an F1 car.")
    tl_box(im, d, y + 50, [("2023", "Ginetta Junior champion", False), ("2024", "Italian F4 + F4 UAE champion", False),
                           ("2025", "Formula Regional EU champion", False), ("JAN 26", "joins Audi programme", False),
                           ("SEP 26", "F3 runner-up, Trident", False), ("30 OCT", "FP1, Mexico City", True),
                           ("6 NOV", "FP1, Sao Paulo", True), ("2027", "F2 with Invicta Racing", False)], "THE SLATER LOG")
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/3_3_context.png")

v1(); v2(); v3()
names = [f"{v}_{i}_{n}" for v in "123" for i, n in ((1, "cover"), (2, "details"), (3, "context"))]
sh = Image.new("RGB", (3 * 550 + 10, 3 * 685 + 10), (60, 60, 60))
for k, nme in enumerate(names):
    sh.paste(Image.open(f"{OUT}/{nme}.png").resize((540, 675)), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
sh.save(f"{OUT}/sheet.png"); print("ok")
