import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
from post_usgp import hx, r, p, num, two_col, GREEN
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_honda"); os.makedirs(OUT, exist_ok=True)
DATE = "19.10.26"
HUD_SAKURA = "36.68N 139.97E"
AMR = hx("#00665e"); PINK = hx("#f9a8d4")

def blossom(d, x, y, w, h, seed=1):
    r(d, x, y, x + w, y + h, hx("#e7e1d3")); r(d, x + 1, y + 1, x + w - 1, y + h - 1, hx("#1e293b"))
    r(d, x + w // 2, y + h // 2, x + w // 2 + 1, y + h - 2, hx("#78350f"))
    rnd = random.Random(seed)
    for _ in range(28): p(d, x + 3 + rnd.randrange(w - 5), y + 3 + rnd.randrange(h // 2), PINK)

def scene_dyno():
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#1c1f24")); d = ImageDraw.Draw(im)
    for x in range(0, w, 20): r(d, x, 0, x, 70, hx("#22262c"))
    r(d, 0, 78, w - 1, 119, hx("#2a2d33")); r(d, 0, 78, w - 1, 79, hx("#3f444c"))
    for x in range(0, w, 16): r(d, x, 80, x + 7, 119, hx("#262930"))
    # monitor with traces (schematic): rival higher, ours lower
    r(d, 120, 10, 186, 46, hx("#0a0e15")); r(d, 120, 10, 186, 11, hx("#334155"))
    for k, x in enumerate(range(124, 182)):
        p(d, x, 38 - int((x - 124) * 0.38), hx("#94a3b8"))
        p(d, x, 41 - int((x - 124) * 0.27), GREEN)
    r(d, 150, 47, 152, 60, hx("#334155")); r(d, 142, 60, 160, 62, hx("#334155"))
    # engine on stand: dark V6 block (unlit), battery pack glowing green next to it
    r(d, 40, 58, 92, 86, hx("#3b3f46")); r(d, 44, 50, 64, 58, hx("#4b5058")); r(d, 68, 50, 88, 58, hx("#4b5058"))
    for x in (46, 52, 58, 70, 76, 82): r(d, x, 52, x + 3, 55, hx("#2a2d33"))
    r(d, 92, 66, 104, 78, hx("#6b7280")); d.ellipse([94, 68, 102, 76], fill=hx("#3b3f46"))   # turbo
    r(d, 36, 86, 96, 90, hx("#52565e")); r(d, 40, 90, 44, 104, hx("#52565e")); r(d, 88, 90, 92, 104, hx("#52565e"))
    r(d, 108, 88, 132, 104, hx("#111827")); r(d, 110, 90, 130, 102, hx("#14532d"))
    for x in range(112, 129, 4): r(d, x, 92, x + 2, 100, GREEN)
    # cables
    for t in range(0, 30): p(d, 96 + t // 2, 78 + t // 3, hx("#facc15"))
    # hidden: blossom poster, calendar 2023, two crossed-out years
    blossom(d, 10, 8, 26, 34, 4)
    r(d, 46, 10, 74, 34, hx("#e7e1d3")); r(d, 46, 10, 74, 13, hx("#dc2626")); num(d, 48, 17, "2023", hx("#3f2b1c"))
    for k, yr in enumerate(("24", "25")):
        x = 82 + k * 16; num(d, x, 22, yr, hx("#64748b")); r(d, x - 1, 24, x + 8, 24, hx("#dc2626"))
    r(d, 140, 104, 199, 119, hx("#202329"))
    return im

TEAMS = [("MER", 561, hx("#c7ccd3")), ("FER", 418, hx("#dc2626")), ("MCL", 317, hx("#ff8000")), ("RBR", 306, hx("#3b5bdb")),
         ("RB", 94, hx("#93c5fd")), ("ALP", 68, hx("#ec4899")), ("HAA", 30, hx("#e5e7eb")), ("AUD", 19, hx("#9ca3af")),
         ("WIL", 12, hx("#60a5fa")), ("AMR", 7, AMR), ("CAD", 0, hx("#facc15"))]

def scene_bars():
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#0e131b")); d = ImageDraw.Draw(im)
    base = 100; sc = 80 / 561
    for i, (lab, pts, col) in enumerate(TEAMS):
        x = 10 + i * 17
        top = base - max(1, int(pts * sc))
        r(d, x, top, x + 11, base, col if lab == "AMR" else tuple(int(c * 0.55) for c in col))
        if lab == "AMR":
            num(d, x + 4, top - 8, "7", GREEN)
            for yy in range(top - 30, top - 10, 2): p(d, x + 5, yy, GREEN)
    r(d, 6, base + 1, 194, base + 1, hx("#475569"))
    num(d, 12, 6, "561", hx("#64748b"))
    r(d, 140, 104, 199, 119, hx("#0e131b"))
    return im

def scene_office():
    w, h = 200, 120
    im = Image.new("RGB", (w, h), hx("#24262b")); d = ImageDraw.Draw(im)
    for x in range(0, w, 14): r(d, x, 0, x, 70, hx("#282a30"))
    blossom(d, 128, 8, 40, 46, 9)
    # calendar 2027 with 1 circled
    r(d, 22, 10, 48, 38, hx("#e7e1d3")); r(d, 22, 10, 48, 13, hx("#dc2626")); num(d, 27, 16, "2027", hx("#3f2b1c"))
    d.ellipse([24, 25, 32, 33], outline=hx("#dc2626")); num(d, 27, 27, "1", hx("#3f2b1c"))
    # desk
    r(d, 0, 72, w - 1, 119, hx("#3b2a1e")); r(d, 0, 72, w - 1, 74, hx("#5a4030"))
    # packing box (retiring)
    r(d, 20, 50, 62, 76, hx("#b08a5a")); r(d, 20, 50, 62, 53, hx("#8a6a42")); r(d, 30, 44, 34, 50, hx("#e5e7eb")); r(d, 40, 42, 50, 50, hx("#facc15"))
    # model car in Aston green on desk
    cx, cy = 80, 66
    r(d, cx, cy, cx + 30, cy + 5, AMR); r(d, cx + 12, cy - 3, cx + 16, cy, hx("#111111")); r(d, cx + 28, cy - 2, cx + 31, cy, AMR)
    for xx in (cx + 2, cx + 22):
        d.ellipse([xx, cy + 3, xx + 6, cy + 9], fill=hx("#0b0b0d"))
    # nameplate, mug, a small V6 paperweight
    r(d, 120, 78, 150, 84, hx("#d6c7a1")); num(d, 129, 79, "KW", hx("#3f2b1c")) if False else r(d, 124, 80, 146, 81, hx("#3f2b1c"))
    r(d, 160, 64, 168, 76, hx("#f5f5f4")); r(d, 168, 67, 170, 72, hx("#f5f5f4"))
    r(d, 0, 100, 199, 119, hx("#2c1f16"))
    return im

def tl_box(im, d, top, rows, title):
    h = 85 + 55 * len(rows); box(im, d, top, h, title); b = top + 105
    for yr, what, hi in rows:
        text(im, 70, b, yr, "label", GREEN if hi else C["mute"]); text(im, 330, b, what, "body", C["ink"]); b += 55
    return top + h

def split_box(im, d, top):
    h = 330; box(im, d, top, h, "2026 POWER UNIT, SCHEMATIC"); b = top + 110
    x0, x1 = 70, W - 70; mid = (x0 + x1) // 2 // 5 * 5
    R(d, x0, b - 30, mid - 5, b + 20, C["mute"]); R(d, mid, b - 30, x1, b + 20, GREEN)
    text(im, x0 + 20, b + 5, "ENGINE 50%", "label", C["onred"]); text(im, mid + 20, b + 5, "ELECTRIC 50%", "label", C["onred"])
    b += 85
    text(im, 70, b, "Honda built battery + motor first,", "body", C["ink"]); b += 45
    text(im, 70, b, "so the combustion engine fell behind.", "body", C["ink"]); b += 45
    text(im, 70, b, "New for 2026: no MGU-H, 350 kW MGU-K.", "body", C["mute"])
    return top + h

def table_box(im, d, top):
    rows = [("1", "MERCEDES", "561"), ("2", "FERRARI", "418"), ("3", "MCLAREN", "317"), ("...", "", ""),
            ("9", "WILLIAMS", "12"), ("10", "ASTON MARTIN", "7"), ("11", "CADILLAC", "0")]
    h = 85 + 50 * len(rows); box(im, d, top, h, "CONSTRUCTORS, AFTER SINGAPORE"); b = top + 100
    for pos, team, pts in rows:
        hi = team == "ASTON MARTIN"
        if hi: R(d, 55, b - 40, W - 55, b + 10, GREEN)
        col = C["onred"] if hi else C["ink"]
        text(im, 70, b, pos, "body", C["onred"] if hi else C["mute"]); text(im, 180, b, team, "body", col)
        if pts: text(im, W - 70 - tlen("body", pts), b, pts, "body", col)
        b += 50
    return top + h

FACTS = [("WHO", "Koji Watanabe, HRC president"), ("SAID TO", "Motorsport.com Japan"), ("LOST", "almost two years"),
         ("ASTON", "P10 of 11, 7 points"), ("NEXT BOSS", "Keiichi Yasuda, 1 Jan 2027")]

def variant_a():
    im, d = page(1, 3, DATE)
    y = headline(im, "HONDA BOSS: WE LOST ALMOST 2 YEARS")
    y = cover_image(im, d, scene_dyno(), y + 75, HUD_SAKURA)
    fig(im, y + 60, "Sakura dyno, schematic. Count the years.")
    body(im, y + 95, "Watanabe on why Aston's Honda is down on power.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/A1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "THE REASON: A LATE START ON THE 2026 ENGINE")
    yy = two_col(im, d, y, "Honda decided to return about a year after its rivals, then had to rebuild its F1 team.",
                 "Watanabe says FIA figures show Honda clearly below the others. Spec 2 hit its power target but hurt drivability.")
    fact_file(im, d, yy + 50, FACTS)
    footer(im, d, 2, "VIA MS.COM"); im.save(f"{OUT}/A2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "2026: HALF THE POWER IS ELECTRIC")
    y = body(im, y + 45, "Short on staff, Honda put the parts with the longest lead time first.")
    split_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/A3_context.png")

def variant_b():
    im, d = page(1, 3, DATE)
    y = headline(im, "7 POINTS, P10 OF 11: ASTON'S HONDA YEAR")
    y = cover_image(im, d, scene_bars(), y + 75, "AFTER SINGAPORE")
    fig(im, y + 60, "Team points, one bar each. Find the 7.")
    body(im, y + 95, "Honda's boss: we lost almost two years.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/B1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "ALONSO 7 POINTS, STROLL STILL ON ZERO")
    y = body(im, y + 45, "Both drivers have complained about a lack of power. Watanabe blames a late start, staff shortages and budget and working-hour limits.")
    fact_file(im, d, y + 50, [("ALONSO", "P17, 7 points"), ("STROLL", "P21, 0 points"), ("ASTON", "P10, 7 points"),
                              ("GAP TO P1", "554 points to Mercedes"), ("LOST", "almost two years")], title="BY THE NUMBERS")
    footer(im, d, 2, "VIA MS.COM"); im.save(f"{OUT}/B2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "ASTON IS 554 POINTS BEHIND MERCEDES")
    y = body(im, y + 45, "Only newcomers Cadillac sit below them.")
    table_box(im, d, y + 50)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/B3_context.png")

def variant_c():
    im, d = page(1, 3, DATE)
    y = headline(im, "HONDA'S OUTGOING BOSS: 'WE STARTED LATE'")
    y = cover_image(im, d, scene_office(), y + 75, HUD_SAKURA)
    fig(im, y + 60, "Last weeks at Sakura. Spot the green car.")
    body(im, y + 95, "Watanabe retires at the end of 2026.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/C1_cover.png")

    im, d = page(2, 3, DATE)
    y = headline(im, "AN ASTON CHASSIS NOW SITS IN SAKURA")
    yy = two_col(im, d, y, "After the Japanese GP, Aston Martin sent a chassis to Honda's Sakura base for testing. Aston staff now work there.",
                 "Watanabe says the partnership is getting stronger and that neither side is perfect. Goal: compete properly next year.")
    fact_file(im, d, yy + 50, [("WHO", "Koji Watanabe, HRC president"), ("STEPS DOWN", "end of 2026"),
                               ("SUCCESSOR", "Keiichi Yasuda, 1 Jan 2027"), ("NEW PU", "clean sheet, not 2025-based")])
    footer(im, d, 2, "VIA MS.COM"); im.save(f"{OUT}/C2_details.png")

    im, d = page(3, 3, DATE)
    y = headline(im, "FROM 2021 EXIT TO 2027 RESET")
    y = body(im, y + 45, "How the lost time added up, in five lines.")
    tl_box(im, d, y + 50, [("END 2021", "Honda leaves F1", False), ("2023", "Return with Aston announced", False),
                           ("2026", "Clean-sheet PU, down on power", False), ("OCT 26", "'Almost two years lost'", True),
                           ("1 JAN 27", "Yasuda takes over HRC", False)], "HONDA, THE LOG")
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/C3_context.png")

if __name__ == "__main__":
    variant_a(); variant_b(); variant_c()
    names = [f"{v}{i}_{n}" for v in "ABC" for i, n in ((1, "cover"), (2, "details"), (3, "context"))]
    sh = Image.new("RGB", (3 * 550 + 10, 3 * 685 + 10), (60, 60, 60))
    for k, nme in enumerate(names):
        sh.paste(Image.open(f"{OUT}/{nme}.png").resize((540, 675)), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    sh.save(f"{OUT}/sheet.png")
    print("ok")
