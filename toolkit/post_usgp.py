import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_usgp"); os.makedirs(OUT, exist_ok=True)
DATE = "19.10.26"
HUD_COTA = "30.13N 97.64W"
HUD_BLQ = "44.49N 11.34E"
GREEN = C["red"]

def hx(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def r(d, x0, y0, x1, y1, c): d.rectangle([x0, y0, x1, y1], fill=c)
def p(d, x, y, c): d.point((x, y), fill=c)
G5 = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
      "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
      "8": "111101111101111", "9": "111101111001111", " ": "000000000000000", "+": "000010111010000",
      "-": "000000111000000", "P": "111101111100100", "K": "101101110101101", "R": "111101110101101", "H": "101101111101101", "V": "101101101101010"}
def num(d, x, y, s, c, sc=1):
    for ch in s:
        g = G5[ch]
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == "1": r(d, x + i * sc, y + j * sc, x + i * sc + sc - 1, y + j * sc + sc - 1, c)
        x += 4 * sc

SILVER, NAVY, PAPAYA, FERRARI = hx("#c7ccd3"), hx("#1e3a8a"), hx("#ff8000"), hx("#dc2626")
TYRE = hx("#0b0b0d")

def car_td(d, x, y, col, nose="up"):
    """small top-down car 7 wide x 14 tall, nose up"""
    r(d, x, y, x + 6, y + 1, col)                 # front wing
    r(d, x + 2, y + 2, x + 4, y + 12, col)        # body
    r(d, x + 1, y + 6, x + 5, y + 10, col)        # sidepods
    r(d, x, y + 2, x + 1, y + 5, TYRE); r(d, x + 5, y + 2, x + 6, y + 5, TYRE)
    r(d, x, y + 9, x + 1, y + 12, TYRE); r(d, x + 5, y + 9, x + 6, y + 12, TYRE)
    r(d, x + 1, y + 13, x + 5, y + 13, col)       # rear wing
    p(d, x + 3, y + 6, hx("#facc15"))             # helmet

def scene_turn1():
    """Top-down COTA Turn 1 hairpin (no sky): silver car leads the pack into the left-hander."""
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#2f6b34")); d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(500): p(d, rnd.randrange(w), rnd.randrange(h), hx("#2a6030"))
    # run-off asphalt (top)
    r(d, 40, 2, 170, 22, hx("#4b4f57"))
    # hairpin: straight coming up on right (x 120-150), turn at top, exit going down-left (x 60-90)
    r(d, 120, 30, 150, 119, hx("#3a3d44"))
    r(d, 60, 30, 90, 119, hx("#3a3d44"))
    d.pieslice([60, 8, 150, 52], 180, 360, fill=hx("#3a3d44"))
    r(d, 91, 30, 119, 119, hx("#2f6b34"))
    d.pieslice([90, 26, 120, 34], 180, 360, fill=hx("#2f6b34"))
    # kerbs on the apex (inner) and exit
    for k in range(0, 12):
        a = math.radians(180 + k * 15)
        x, y = 105 + 16 * math.cos(a), 31 + 6 * math.sin(a)
        r(d, int(x), int(y) - 1, int(x) + 1, int(y), hx("#e5e7eb") if k % 2 else FERRARI)
    for y in range(36, 119, 6):
        r(d, 57, y, 59, y + 2, FERRARI); r(d, 57, y + 3, 59, y + 5, hx("#e5e7eb"))
    # start/finish style white lines on the straight
    r(d, 120, 100, 150, 101, hx("#e5e7eb"))
    # cars: silver at the apex, pack behind on the straight
    car_td(d, 98, 18, SILVER)
    car_td(d, 128, 46, NAVY); car_td(d, 139, 60, PAPAYA); car_td(d, 125, 72, FERRARI); car_td(d, 138, 86, SILVER)
    # hidden: "340" painted in the run-off, longhorn skull in the grass, "25" grid slot
    num(d, 92, 6, "340", hx("#6b7280"), sc=2)
    lx, ly = 22, 60
    r(d, lx + 3, ly + 2, lx + 7, ly + 7, hx("#e7e1d3"))
    r(d, lx, ly, lx + 2, ly + 1, hx("#e7e1d3")); r(d, lx + 8, ly, lx + 10, ly + 1, hx("#e7e1d3"))
    r(d, lx - 1, ly - 2, lx, ly - 1, hx("#e7e1d3")); r(d, lx + 10, ly - 2, lx + 11, ly - 1, hx("#e7e1d3"))
    p(d, lx + 4, ly + 4, TYRE); p(d, lx + 6, ly + 4, TYRE)
    num(d, 66, 92, "25", hx("#4b4f57"))
    return im

def scene_tower():
    """Diagram: points bars before Austin, ghost +25 for Kimi."""
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#0e131b")); d = ImageDraw.Draw(im)
    rows = [("K", 340, SILVER), ("R", 238, SILVER), ("H", 229, FERRARI), ("V", 221, NAVY)]
    sc = 150 / 365
    for i, (lab, pts, col) in enumerate(rows):
        y = 10 + i * 22
        num(d, 6, y + 3, lab, hx("#94a3b8"))
        r(d, 14, y, 14 + int(pts * sc), y + 10, col if col != NAVY else hx("#3b5bdb"))
        num(d, 18 + int((365 if i == 0 else pts) * sc), y + 3, str(pts), hx("#e5e7eb"))
        if i == 0:
            x0 = 15 + int(pts * sc)
            for xx in range(x0, 14 + int(365 * sc), 2): r(d, xx, y, xx, y + 10, hx("#39ff14"))
            num(d, 4 + int(365 * sc), y - 7, "+25", hx("#39ff14"))
    # gap brackets: 102 between K and R
    gx = 14 + int(238 * sc)
    for yy in range(14, 30, 2): p(d, gx, yy, hx("#64748b"))
    num(d, gx + 4, 24, "102", hx("#64748b"))
    # six race cells at bottom (Austin first, lit)
    for k in range(6):
        x = 8 + k * 16
        r(d, x, 102, x + 12, 110, hx("#39ff14") if k == 0 else hx("#1f2937"))
    return im

def scene_shelf():
    """Indoor: trophy shelf in a Bologna bedroom; empty spot waits, red 1953-style model car, tricolore pennant."""
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#2b2320")); d = ImageDraw.Draw(im)
    for x in range(0, w, 12): r(d, x, 0, x, 119, hx("#2f2723"))
    # window-less wall, lamp glow
    d.ellipse([140, -20, 210, 40], fill=hx("#3a2f28"))
    # shelves
    for y in (48, 92):
        r(d, 10, y, 190, y + 3, hx("#6b4a2f")); r(d, 10, y + 4, 190, y + 5, hx("#3f2b1c"))
    # top shelf: small trophies + empty glowing spot with "20" tag
    for k, x in enumerate((18, 34, 50, 66)):
        r(d, x + 2, 36, x + 8, 41, hx("#facc15")); r(d, x + 4, 42, x + 6, 45, hx("#a16207")); r(d, x + 2, 46, x + 8, 47, hx("#a16207"))
    ex = 110
    for k in range(5): r(d, ex + 2 * k, 46 - 2 * k, ex + 22 - 2 * k, 47 - 2 * k, hx("#3a312b"))
    r(d, ex + 2, 18, ex + 20, 47, None) if False else None
    for yy in range(14, 46, 3): p(d, ex + 4, yy, hx("#39ff14")); p(d, ex + 18, yy, hx("#39ff14"))
    r(d, ex + 6, 42, ex + 16, 46, hx("#1b1814")); num(d, ex + 7, 42, "20", hx("#39ff14"))
    # bottom shelf: red cigar-shaped 1953-style model car with plate "1953"
    cx, cy = 26, 80
    r(d, cx, cy, cx + 34, cy + 6, FERRARI); r(d, cx + 34, cy + 1, cx + 37, cy + 5, FERRARI)
    r(d, cx + 14, cy - 3, cx + 18, cy, hx("#111111"))
    for xx in (cx + 4, cx + 26):
        d.ellipse([xx, cy + 4, xx + 7, cy + 11], fill=TYRE); p(d, xx + 3, cy + 7, hx("#9ca3af"))
    r(d, cx + 6, 86, cx + 26, 91, hx("#d6c7a1")); num(d, cx + 8, 86, "1953", hx("#3f2b1c"))
    # helmet-shaped bookend in plain yellow/blue
    d.ellipse([80, 72, 98, 90], fill=hx("#facc15")); r(d, 88, 77, 96, 80, hx("#1e293b")); r(d, 80, 86, 98, 91, hx("#facc15")); r(d, 80, 82, 98, 83, hx("#1e3a8a"))
    # tricolore pennant on wall
    r(d, 150, 58, 156, 74, hx("#16a34a")); r(d, 157, 58, 163, 74, hx("#f5f5f4")); r(d, 164, 58, 170, 74, FERRARI)
    # hidden: wall calendar "2010" with one circled date
    r(d, 14, 6, 34, 26, hx("#e7e1d3")); r(d, 14, 6, 34, 9, FERRARI); num(d, 16, 12, "2010", hx("#3f2b1c"))
    d.ellipse([24, 18, 30, 24], outline=FERRARI)
    # floor dark so HUD reads
    r(d, 0, 98, 199, 119, hx("#1a1513"))
    return im

def schedule_box(im, d, top):
    rows = [("FRI 23", "PRACTICE 1", "19:30"), ("FRI 23", "PRACTICE 2", "23:00"), ("SAT 24", "PRACTICE 3", "19:30"),
            ("SAT 24", "QUALIFYING", "23:00"), ("SUN 25", "RACE", "21:00")]
    h = 85 + 50 * len(rows); box(im, d, top, h, "RACE WEEK, BERLIN TIME"); b = top + 100
    for day, s, t in rows:
        hi = s == "RACE"
        if hi: R(d, 55, b - 40, W - 55, b + 10, GREEN)
        col = C["onred"] if hi else C["ink"]
        text(im, 70, b, day, "body", C["onred"] if hi else C["mute"]); text(im, 270, b, s, "body", col)
        text(im, W - 70 - tlen("body", t), b, t, "body", col); b += 50
    return top + h

def gap_box(im, d, top):
    rows = [("RUSSELL P8", 123, "ALIVE"), ("RUSSELL P9", 125, "TIE"), ("HAMILTON P4", 124, "ALIVE"), ("HAMILTON P5", 126, "OUT")]
    h = 85 + 70 * len(rows) + 40; box(im, d, top, h, "GAP AFTER A KIMI WIN"); b = top + 110
    x0, x1, lo, hi_ = 380, 760, 118, 128
    def X(v): return x0 + int((v - lo) / (hi_ - lo) * (x1 - x0)) // 5 * 5
    for name, gap, verdict in rows:
        text(im, 70, b, name, "body", C["ink"])
        win = verdict != "ALIVE"
        R(d, x0, b - 30, X(gap), b - 5, GREEN if win else C["mute"])
        text(im, 800, b, str(gap), "body", C["ink"])
        text(im, W - 70 - tlen("label", verdict), b - 5, verdict, "label", GREEN if win else C["mute"]); b += 70
    tx = X(125)
    R(d, tx, top + 70, tx + 5, b - 50, C["ink"])
    text(im, tx - tlen("label", "125") // 2, b - 5, "125", "label", C["ink"])
    return top + h

def ladder_box(im, d, top):
    rows = [("ANTONELLI", "2026?", "20Y 61D"), ("VETTEL", "2010", "23Y 134D"), ("HAMILTON", "2008", "23Y 300D"), ("ALONSO", "2005", "24Y 58D")]
    h = 85 + 50 * len(rows); box(im, d, top, h, "YOUNGEST CHAMPIONS"); b = top + 100
    for name, yr, age in rows:
        hi = yr.endswith("?")
        if hi: R(d, 55, b - 40, W - 55, b + 10, GREEN)
        col = C["onred"] if hi else C["ink"]
        text(im, 70, b, name, "body", col); text(im, 420, b, yr, "body", C["onred"] if hi else C["mute"])
        text(im, W - 70 - tlen("body", age), b, age, "body", col); b += 50
    return top + h

def two_col(im, d, y, left, right):
    yl = body(im, y + 45, left, maxw=475); yr = body(im, y + 45, right, maxw=475, x=565)
    R(d, 535, y + 45, 540, max(yl, yr) + 10, C["rule"]); return max(yl, yr)

STAND = [("KIMI", "340 pts, leader"), ("RUSSELL", "238 pts, -102"), ("HAMILTON", "229 pts, -111"),
         ("VERSTAPPEN", "221 pts, -119"), ("STILL OPEN", "150 pts, Austin + 5 races")]

def variant_a():
    im, d = page(1, 3, DATE)
    y = headline(im, "ANTONELLI CAN WIN THE TITLE IN AUSTIN")
    y = cover_image(im, d, scene_turn1(), y + 75, HUD_COTA)
    fig(im, y + 60, "COTA Turn 1, top-down. Find 340.")
    body(im, y + 95, "Kimi P1, Russell P9 or lower, Lewis P5 or lower.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/A1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "A WIN ALONE IS NOT ENOUGH IN AUSTIN")
    yy = two_col(im, d, y, "Antonelli must win on Sunday. Then Russell has to finish 9th or lower and Hamilton 5th or lower.",
                 "Any other result and the fight goes on to Mexico. A Kimi win would knock Verstappen, Leclerc and Norris out.")
    fact_file(im, d, yy + 50, STAND, title="STANDINGS BEFORE AUSTIN")
    footer(im, d, 2, "VIA RN365"); im.save(f"{OUT}/A2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "RACE WEEK: LIGHTS OUT SUN 21:00 CET")
    y = body(im, y + 45, "Clocks go back on race morning, so Sunday is CET. Not a sprint weekend.")
    schedule_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/A3_context.png")

def variant_b():
    im, d = page(1, 3, DATE)
    y = headline(im, "102 POINTS CLEAR, 150 STILL TO PLAY FOR")
    y = cover_image(im, d, scene_tower(), y + 75, "6 RACES LEFT")
    fig(im, y + 60, "Points before Austin. Green = +25.")
    body(im, y + 95, "Kimi 340, Russell 238, Hamilton 229, Max 221.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/B1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "THE MAGIC NUMBER AFTER AUSTIN: 125")
    y = body(im, y + 45, "After Austin, five races and 125 points remain. A win takes Kimi to 365, so he needs a 125-point lead.")
    fact_file(im, d, y + 50, [("KIMI", "must win: 340 + 25 = 365"), ("RUSSELL", "P9 or lower"), ("HAMILTON", "P5 or lower"),
                              ("KIMI P2-P10", "no title in Austin"), ("STILL OPEN", "150 pts incl. Austin")], title="THE CLINCH MATHS")
    footer(im, d, 2, "VIA RN365"); im.save(f"{OUT}/B2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "A TIE AT 125 GOES TO KIMI ON WINS")
    y = body(im, y + 45, "Green = Kimi is champion. Russell P9 leaves exactly 125: a tie Kimi wins on countback.")
    gap_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/B3_context.png")

def variant_c():
    im, d = page(1, 3, DATE)
    y = headline(im, "ANTONELLI, 20, CHASES VETTEL'S AGE RECORD")
    y = cover_image(im, d, scene_shelf(), y + 75, HUD_BLQ)
    fig(im, y + 60, "A shelf in Bologna. Spot the 1953 car.")
    body(im, y + 95, "A COTA title would beat Vettel's 2010 record.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/C1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "FIRST ITALIAN CHAMPION SINCE ASCARI, 1953")
    yy = two_col(im, d, y, "Win the title in Austin and Antonelli becomes F1's youngest champion, ahead of Vettel in 2010.",
                 "He would also end a 73-year wait for Italy. The last Italian champion was Alberto Ascari.")
    fact_file(im, d, yy + 50, [("BORN", "25 Aug 2006, Bologna"), ("ON 25 OCT", "20 years, 61 days"),
                               ("RECORD", "Vettel, 23y 134d, 2010"), ("LAST ITALIAN", "Ascari, 1953")])
    footer(im, d, 2, "VIA RN365"); im.save(f"{OUT}/C2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "20Y 61D WOULD BEAT VETTEL BY 3 YEARS")
    y = body(im, y + 45, "The threat: Verstappen arrives in Austin with two straight wins.")
    ladder_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/C3_context.png")

if __name__ == "__main__":
    variant_a(); variant_b(); variant_c()
    names = [f"{v}{i}_{n}" for v in "ABC" for i, n in ((1, "cover"), (2, "details"), (3, "context"))]
    sh = Image.new("RGB", (3 * 550 + 10, 3 * 685 + 10), (60, 60, 60))
    for k, nme in enumerate(names):
        sh.paste(Image.open(f"{OUT}/{nme}.png").resize((540, 675)), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    sh.save(f"{OUT}/sheet.png")
    print("ok")
