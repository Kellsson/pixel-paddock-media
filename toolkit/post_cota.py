import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
from post_usgp import hx, r, p, two_col, GREEN
from post_slater import tx, tw as tw3, F as FONT3
FONT3["%"] = "101001010100101"; FONT3[","] = "000000000010100"
from mock_v2 import track, COTA_TURNS, NUDGE, el_week
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_cota"); os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
DATE = "23.10.26"
INK = hx("#e5e7eb"); MUT = hx("#64748b"); BG = hx("#0e131b"); BOX = hx("#1f2937")
PUR, YEL = SECT[0], SECT[2]
PTS = track(f"{HERE}/geo/us.geojson"); N = len(PTS)
ABS_OFF = {14: (13, 48), 16: (-72, 18)}
RESURF = (72, 89)                     # T9-T11 resurfaced 2026
BORROW = [((20, 52), PUR, "T3-T6", "SILVERSTONE"), ((99, 131), YEL, "T12-T15", "HOCKENHEIM"), ((132, 152), GREEN, "T16-T18", "ISTANBUL T8")]

def fitP(x0, y0, bw, bh):
    xs = [q[0] for q in PTS]; ys = [q[1] for q in PTS]
    S = min(bw / (max(xs) - min(xs)), bh / (max(ys) - min(ys)))
    ox = x0 + (bw - (max(xs) - min(xs)) * S) / 2; oy = y0 + (bh - (max(ys) - min(ys)) * S) / 2
    return [(ox + (x - min(xs)) * S, oy + (max(ys) - y) * S) for x, y in PTS]

def big_map(im, d, top, hls, legend, title, h=780):
    box(im, d, top, h, title)
    P = fitP(115, top + 120, 860, 520)
    lw, lh = W // 5, H // 5
    def layer(ok, col):
        L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        for i in range(N):
            if ok(i):
                a, b = P[i], P[(i + 1) % N]; ld.line([(a[0] / 5, a[1] / 5), (b[0] / 5, b[1] / 5)], fill=col, width=3)
        return L.resize((W, H), Image.NEAREST)
    L = layer(lambda i: True, C["mute"] + (255,)); im.paste(L, (0, 0), L)
    for (i0, i1), col in hls:
        L = layer(lambda i, i0=i0, i1=i1: i0 <= i <= i1, col + (255,)); im.paste(L, (0, 0), L)
    d = ImageDraw.Draw(im)
    sx, sy = int(P[0][0] // 5 * 5), int(P[0][1] // 5 * 5)
    for k in range(-3, 3):
        for j in range(2):
            R(d, sx + j * 5 + k * 5 - 5, sy + k * 5 - j * 5 + 5, sx + j * 5 + k * 5, sy + k * 5 - j * 5 + 10, C["ink"] if (k + j) % 2 else C["paper"])
    for t, i in COTA_TURNS.items():
        a = P[(i - 2) % N]; b = P[(i + 2) % N]; c = P[i]
        dx, dy = b[0] - a[0], b[1] - a[1]; Ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ln, dx / Ln
        mx, my = (a[0] + b[0]) / 2 - c[0], (a[1] + b[1]) / 2 - c[1]
        if mx * nx + my * ny > 0: nx, ny = -nx, -ny
        ddx, ddy = NUDGE.get(t, (0, 0))
        px, py = int(c[0] // 5 * 5), int(c[1] // 5 * 5); R(d, px - 5, py - 5, px + 10, py + 10, C["ink"])
        lab = str(t); w = tlen("label", lab)
        x = c[0] + nx * 38 - w / 2 + ddx; y = c[1] + ny * 38 + 14 + ddy
        if t in ABS_OFF: x, y = c[0] + ABS_OFF[t][0], c[1] + ABS_OFF[t][1]
        col = C["ink"]
        for (i0, i1), hc in hls:
            if i0 <= i <= i1: col = hc
        text(im, int(x // 5 * 5), int(y // 5 * 5), lab, "label", col)
    y = top + h - 45; x = 70
    for col, lab in legend:
        R(d, x, y - 20, x + 30, y - 5, col); text(im, x + 45, y, lab, "label", col); x += 45 + tlen("label", lab) + 35
    return top + h

def scene_map(hls, labels=True):
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    P = fitP(14, 8, 172, 98)
    for i in range(N):
        a, b = P[i], P[(i + 1) % N]; d.line([a, b], fill=MUT, width=3)
    for (i0, i1), col in hls:
        for i in range(i0, i1):
            a, b = P[i], P[(i + 1) % N]; d.line([a, b], fill=col, width=3)
    sx, sy = int(P[0][0]), int(P[0][1])
    for k in range(-2, 2): r(d, sx + k, sy + k, sx + k, sy + k, INK if k % 2 else BG)
    return im, d, P

def scene_resurf():
    im, d, P = scene_map([(RESURF, GREEN)])
    for t, off in ((1, (2, 3)), (9, (-4, 4)), (10, (-3, 3)), (11, (4, -2)), (12, (-9, -6)), (20, (-12, -3))):
        x, y = P[COTA_TURNS[t]]; tx(d, int(x + off[0]), int(y + off[1]), str(t), GREEN if 9 <= t <= 11 else INK)
    tx(d, 6, 6, "COTA", INK); tx(d, 6, 13, "20 TURNS", MUT)
    r(d, 104, 70, 108, 73, GREEN); tx(d, 111, 70, "NEW 2026", GREEN)
    r(d, 130, 104, 199, 119, BG)
    return im

def scene_numbers():
    """Chart cover: SC/VSC probability bars + key numbers."""
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 8, 6, "AUSTIN, LAST 7 RACES", MUT)
    for k, (lab, v, col) in enumerate((("SC", 29, YEL), ("VSC", 43, hx("#f59e0b")))):
        y = 18 + k * 18; tx(d, 8, y + 3, lab, INK)
        r(d, 26, y, 26 + 100, y + 10, BOX); r(d, 26, y, 26 + v, y + 10, col)
        tx(d, 26 + v + 4, y + 3, f"{v}%", INK)
    # stat tiles row
    tiles = [("71", "OVERTAKES 2025"), ("230", "METRES TO-T1"), ("19.9", "SEC PIT-LOSS")]
    for k, (v, lab) in enumerate(tiles):
        x = 8 + k * 62; r(d, x, 60, x + 56, 98, BOX); d.rectangle([x, 60, x + 56, 98], outline=GREEN if k == 0 else MUT)
        tx(d, x + 5, 66, v, GREEN if k == 0 else INK, 2)
        for j, wd in enumerate(lab.split(" ", 1)): tx(d, x + 5, 82 + j * 7, wd.replace("-", " "), MUT)
    r(d, 130, 104, 199, 119, BG)
    return im

def scene_borrow():
    """Comparison cover: three mini maps, each with the section borrowed from a famous circuit."""
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "COTA BORROWED", INK)
    for k, (rng, col, tl, orig) in enumerate(BORROW):
        x0 = 4 + k * 66; P = fitP(x0 + 2, 16, 58, 40)
        r(d, x0, 14, x0 + 62, 98, BOX)
        for i in range(N):
            a, b = P[i], P[(i + 1) % N]; d.line([a, b], fill=MUT, width=1)
        for i in range(rng[0], rng[1]):
            a, b = P[i], P[(i + 1) % N]; d.line([a, b], fill=col, width=3)
        tx(d, x0 + 3, 62, tl, col)
        tx(d, x0 + 3, 72, "FROM", MUT)
        words = orig.split(" ")
        tx(d, x0 + 3, 80, words[0][:15], INK)
        if len(words) > 1: tx(d, x0 + 3, 88, words[1], INK)
    r(d, 130, 104, 199, 119, BG)
    return im

FACTS = [("LENGTH", "5.513 km, 20 turns"), ("RACE", "56 laps, 308.4 km"), ("DIRECTION", "anti-clockwise"),
         ("LAP RECORD", "1:36.169, Leclerc 2019"), ("FP1 TODAY", "19:30 Berlin")]

def v1():
    im, d = page(1, 3, DATE)
    y = headline(im, "COTA: 71 OVERTAKES, 43% VSC CHANCE")
    y = cover_image(im, d, scene_numbers(), y + 75, "30.13N 97.64W")
    fig(im, y + 60, "Safety car odds and key race numbers.")
    body(im, y + 95, "FP1 at the Circuit of the Americas starts 19:30 Berlin.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/1_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "230 M FROM POLE TO THE FIRST BRAKE")
    yy = two_col(im, d, y, "The run to Turn 1 is short and steep: 230 m from pole to the braking point, uphill into a tight left hairpin.",
                 "In the last seven Austin races the safety car came out 29% of the time, the VSC 43%. A stop costs 19.9 s.")
    fact_file(im, d, yy + 50, FACTS, keyw=380)
    footer(im, d, 2, "VIA F1.COM"); im.save(f"{OUT}/1_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "THE REAL LAYOUT, ALL 20 TURNS")
    y = body(im, y + 45, "Drawn from GPS data. Green: new asphalt from Turn 9 to Turn 11.")
    big_map(im, d, y + 50, [(RESURF, GREEN)], [(GREEN, "T9-T11 RESURFACED"), (C["mute"], "5.513 KM")], "TRACK MAP, COTA · 20 TURNS")
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/1_3_context.png")

def v2():
    im, d = page(1, 3, DATE)
    y = headline(im, "COTA, 20 TURNS: NEW ASPHALT IN T9-T11")
    y = cover_image(im, d, scene_resurf(), y + 75, "30.13N 97.64W")
    fig(im, y + 60, "GPS track map, resurfaced part in green.")
    body(im, y + 95, "5.513 km, anti-clockwise, 56 laps on Sunday.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/2_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "FOUR CORNERS THAT DECIDE A LAP")
    y = body(im, y + 45, "Where the time is won and lost at COTA, per F1's own track notes.")
    fact_file(im, d, y + 50, [("T1", "steep uphill, many lines"), ("T13-T15", "hardest section"),
                              ("T14", "heavy load on the tyres"), ("T19", "track limits trap"), ("T20", "easy to lose traction")],
              title="KEY CORNERS", keyw=300)
    footer(im, d, 2, "VIA F1.COM"); im.save(f"{OUT}/2_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "WHEN TO WATCH, 5 TIME ZONES")
    y = body(im, y + 45, "Europe switches to winter time on Sunday, the US a week later.")
    el_week(im, d, y + 50, done=0)
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/2_3_context.png")

def v3():
    im, d = page(1, 3, DATE)
    y = headline(im, "3 SECTIONS OF COTA COPY OTHER TRACKS")
    y = cover_image(im, d, scene_borrow(), y + 75, "30.13N 97.64W")
    fig(im, y + 60, "Three borrowed sections, highlighted.")
    body(im, y + 95, "5.513 km, 20 turns, FP1 tonight at 19:30 Berlin.")
    footer(im, d, 1, "SWIPE >>>"); im.save(f"{OUT}/3_1_cover.png")
    im, d = page(2, 3, DATE)
    y = headline(im, "A 2012 TRACK BUILT FROM GREATEST HITS")
    yy = two_col(im, d, y, "The esses from Turn 3 to 6 are modelled on Silverstone's Maggotts and Becketts.",
                 "The stadium bends follow Hockenheim, and the multi-apex right after it echoes Istanbul's Turn 8.")
    fact_file(im, d, yy + 50, [("OPENED", "October 2012"), ("FIRST GP", "18 Nov 2012"), ("LENGTH", "5.513 km, 20 turns"),
                               ("ELEVATION", "41 m top to bottom"), ("MOST WINS", "Hamilton, 6 US GPs")], keyw=380)
    footer(im, d, 2, "VIA WIKIPEDIA"); im.save(f"{OUT}/3_2_details.png")
    im, d = page(3, 3, DATE)
    y = headline(im, "WHERE EACH COPY SITS ON THE LAP")
    y = body(im, y + 45, "Real layout from GPS data, all 20 turns numbered.")
    big_map(im, d, y + 50, [(r_, c_) for r_, c_, *_ in BORROW], [(PUR, "SILVERSTONE"), (YEL, "HOCKENHEIM"), (GREEN, "IST. T8")],
            "TRACK MAP, COTA · 20 TURNS")
    footer(im, d, 3, "FOLLOW"); im.save(f"{OUT}/3_3_context.png")

v1(); v2(); v3()
names = [f"{v}_{i}_{n}" for v in "123" for i, n in ((1, "cover"), (2, "details"), (3, "context"))]
sh = Image.new("RGB", (3 * 550 + 10, 3 * 685 + 10), (60, 60, 60))
for k, nme in enumerate(names):
    sh.paste(Image.open(f"{OUT}/{nme}.png").resize((540, 675)), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
sh.save(f"{OUT}/sheet.png"); print("ok")
