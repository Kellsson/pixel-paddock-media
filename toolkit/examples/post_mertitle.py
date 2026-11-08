import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "post_fer.py")).read().split("def scene_t4")[0]
ns = {"__file__": os.path.join(HERE, "post_fer.py")}; exec(compile(src, "fer", "exec"), ns)
globals().update({k: v for k, v in ns.items() if not k.startswith("__")})
fsrc = open(os.path.join(HERE, "post_fer.py")).read()
exec(compile(fsrc[fsrc.index("def scene_brazil"):fsrc.index("def slide")], "fb", "exec"), globals())
OUT = os.path.join(HERE, "out_mert"); os.makedirs(OUT, exist_ok=True)
DATE = "03.11.26"; HUD = "23.70S 46.70W"
MER = hx("#27f4d2"); FER_ = hx("#dc0000"); RBR_ = hx("#3671c6"); MCL = hx("#ff8000")

def scene_math():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "THE MATHS: MERCEDES VS FERRARI", INK)
    x0 = 10; s = 1.3
    tx(d, x0, 16, "LEAD NOW", MUT); r(d, x0, 24, x0 + int(126 * s), 34, MER); tx(d, x0 + int(126 * s) + 4, 27, "126", INK)
    tx(d, x0, 42, "NEEDED AFTER BRAZIL", MUT); r(d, x0, 50, x0 + int(126 * s), 60, MER); r(d, x0 + int(126 * s) + 1, 50, x0 + int(129 * s), 60, GREEN)
    tx(d, x0 + int(129 * s) + 4, 53, "129", GREEN)
    lx = x0 + int(129 * s); d.line([(lx, 20), (lx, 66)], fill=RED)
    tx(d, x0, 70, "= 3 RACES X 43 PTS", INK); tx(d, x0, 78, "MAX FERRARI CAN STILL GAIN", MUT)
    d.rectangle([6, 88, 150, 100], outline=GREEN); tx(d, 10, 92, "OUTSCORE FERRARI BY 3: TITLE", GREEN)
    r(d, 130, 104, 199, 119, BG); return im

def scene_routes():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "MERCEDES FINISHES THAT SEAL IT", INK)
    rows = [("1-2", True), ("1-3", True), ("1-4", True)]
    for k, (fin, ok) in enumerate(rows):
        y = 16 + k * 18; a, b = fin.split("-")
        r(d, 6, y, 194, y + 14, BOXC); r(d, 6, y, 8, y + 14, MER)
        for i, p in enumerate((a, b)):
            d.rectangle([14 + i * 22, y + 2, 32 + i * 22, y + 12], outline=MER); tx(d, 18 + i * 22, y + 5, "P" + p, INK)
        tx(d, 64, y + 5, "WHATEVER FERRARI DO", MUT); tx(d, 156, y + 5, "TITLE", GREEN)
    tx(d, 6, 74, "A WIN PLUS P4 OR BETTER", INK)
    tx(d, 6, 84, "IF FERRARI WIN: BOTH MERCEDES", MUT); tx(d, 6, 92, "ON THE PODIUM, OTHER FERRARI FAR BACK", MUT)
    r(d, 130, 104, 199, 119, BG); return im

def scene_streak():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "CONSTRUCTORS' CHAMPIONS SINCE 2014", INK)
    yrs = [(2014 + i, MER, "MER") for i in range(8)] + [(2022, RBR_, "RBR"), (2023, RBR_, "RBR"), (2024, MCL, "MCL"), (2025, MCL, "MCL")]
    for k, (yr, col, t) in enumerate(yrs):
        x = 6 + (k % 7) * 27; y = 16 + (k // 7) * 34
        r(d, x, y, x + 23, y + 24, col if t == "MER" else BOXC); d.rectangle([x, y, x + 23, y + 24], outline=col)
        tx(d, x + 2, y + 4, str(yr)[2:], BG if t == "MER" else INK); tx(d, x + 2, y + 14, t, BG if t == "MER" else col)
    x = 6 + 5 * 27; y = 50
    d.rectangle([x, y, x + 50, y + 24], outline=GREEN); tx(d, x + 3, y + 4, "2026", GREEN); tx(d, x + 3, y + 14, "MER?", GREEN)
    tx(d, 6, 88, "8 IN A ROW, THEN 4 YEARS WAITING", INK)
    r(d, 130, 104, 199, 119, BG); return im

def scene_wins():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "IF POINTS END LEVEL: WINS DECIDE", INK)
    for k, (t, n, col) in enumerate([("MERCEDES", 12, MER), ("FERRARI", 2, FER_)]):
        y = 18 + k * 34; tx(d, 6, y, t, INK)
        for i in range(n): r(d, 6 + i * 12, y + 9, 15 + i * 12, y + 18, col)
        tx(d, 10 + n * 12, y + 12, str(n), col)
    tx(d, 6, 88, "ANTONELLI: 9 OF MERCEDES' 12 WINS", GREEN)
    r(d, 130, 104, 199, 119, BG); return im

def scene_ladder():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
    tx(d, 6, 4, "MERCEDES MINUS FERRARI IN BRAZIL", INK)
    rows = [("+3 OR MORE", "LEAD 129+", "CHAMPIONS", GREEN), ("+2", "LEAD 128", "NOT YET", MUT), ("LEVEL", "LEAD 126", "NOT YET", MUT), ("FERRARI AHEAD", "UNDER 126", "NOT YET", RED)]
    for k, (a, b, c, col) in enumerate(rows):
        y = 16 + k * 18
        r(d, 6, y, 194, y + 14, BOXC); d.rectangle([6, y, 194, y + 14], outline=col if k == 0 else BOXC)
        tx(d, 10, y + 5, a, INK); tx(d, 84, y + 5, b, MUT); tx(d, 146, y + 5, c, col)
    tx(d, 6, 94, "THEN 3 MORE CHANCES", MUT)
    r(d, 130, 104, 199, 119, BG); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k); body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

slide(1, "MERCEDES CAN WIN THE CONSTRUCTORS' TITLE IN SAO PAULO", scene_math, "Lead now vs lead needed after Brazil.",
      "Outscore Ferrari by 3 points and it's done.", "SWIPE >>>", "1_1")
slide(2, "A 1-2, 1-3 OR 1-4 IS ENOUGH", scene_routes, "Mercedes results that clinch it.",
      "Antonelli or Russell win, the other P4 or better.", "SWIPE >>>", "1_2")
slide(3, "THE FIRST MERCEDES TEAM TITLE SINCE 2021?", scene_streak, "Constructors' champions, 2014-2025.",
      "Las Vegas, Qatar and Abu Dhabi still to come.", "FOLLOW", "1_3")
slide(1, "8 IN A ROW, THEN 4 YEARS WAITING: MERCEDES CAN END IT SUNDAY", scene_streak, "Constructors' champions, 2014-2025.",
      "126 points ahead of Ferrari, four races left.", "SWIPE >>>", "2_1")
slide(2, "WHY 3 POINTS ARE ENOUGH", scene_math, "Lead now vs lead needed after Brazil.",
      "After Brazil, 129 points remain for Ferrari to win.", "SWIPE >>>", "2_2")
slide(3, "AND IF IT ENDS LEVEL? WINS DECIDE", scene_wins, "Grand Prix wins in 2026.",
      "Countback favours Mercedes, 12 wins to 2.", "FOLLOW", "2_3")
slide(1, "WIN AND P4: MERCEDES' SIMPLEST ROUTE TO THE TITLE", scene_routes, "Mercedes results that clinch it.",
      "Ferrari are the only team still in the fight.", "SWIPE >>>", "3_1")
slide(2, "EVERY BRAZIL OUTCOME, ONE TABLE", scene_ladder, "Mercedes minus Ferrari points in Brazil.",
      "Anything below +3 sends it to Las Vegas.", "SWIPE >>>", "3_2")
slide(3, "WHEN TO WATCH: SUNDAY 14:00 AT INTERLAGOS", scene_brazil, "Interlagos sessions, local time.",
      "Quali Saturday 15:00 local, 18:00 UTC.", "FOLLOW", "3_3")
from PIL import Image as I
sh = I.new("RGB", (3 * 550 + 10, 3 * 685 + 10), (60, 60, 60))
for k, nme in enumerate([f"{v}_{i}" for v in "123" for i in "123"]):
    sh.paste(I.open(f"{OUT}/{nme}.png").resize((540, 675)), (10 + (k % 3) * 550, 10 + (k // 3) * 685))
sh.save(f"{OUT}/sheet.png"); print("ok")
