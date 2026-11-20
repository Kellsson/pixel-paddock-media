import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_flash"').replace('DATE = "07.11.26"','DATE = "21.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "NEWS FLASH 01"'))
from pp import text, tlen, framed
# NEWS FLASH No. 1, v3 (Marius 21.11.): big "01 OF 03" counter at the very top of the page, then ONE headline,
# details as cards (v1 style) in story colour, one story per slide, "next" teaser to drive the swipe.
# Sources (2 each, year 2026 checked):
#  V8 2030: FIA press release 20.11.26 + RACER/Motorsport.com/The Race 20.11.26
#  Piastri -10: F1.com 18.11.26 + PlanetF1 + Autosport (5th ICE, limit 4, reliability)
#  Bottas 2027 / Herta: RACER 18.11.26 + PlanetF1 18.11.26 (+ F1.com Towriss 20.11.26)
#  Left out (1 source only): Aron/Vesti Alpine, Herta declined reserve role, WMSC Shanghai vote.
STORIES = {
 "v8":  dict(col=GREEN, tag="ENGINES", teaser="V8 RETURN",
             cards=[("2030", "2.1 L TURBO V8", "WITH LIMITED HYBRID", "NEW ENGINE RULES FROM 2030"),
                    ("ALL", "AGREED UNANIMOUSLY", "FIA, F1, TEAMS, PU MAKERS", "GOAL: LIGHTER, SIMPLER, CHEAPER")]),
 "pia": dict(col=hx(TC["PIA"]), tag="VEGAS GRID", teaser="PIASTRI -10",
             cards=[("-10", "10-PLACE GRID DROP", "FOR OSCAR PIASTRI", "RACE: SAT 20:00 LOCAL, SUN 04:00 UTC"),
                    ("5TH", "FIFTH ENGINE OF 2026", "THE LIMIT IS FOUR", "MCLAREN: RELIABILITY ISSUE")]),
 "bot": dict(col=hx(TC["BOT"]), tag="2027 SEATS", teaser="BOTTAS STAYS",
             cards=[("2027", "BOTTAS STAYS AT CADILLAC", "NEXT TO PEREZ AGAIN", "LINE-UP UNCHANGED FOR YEAR TWO"),
                    ("NO", "NO RACE SEAT FOR HERTA", "DESPITE SUPER LICENCE POINTS", "EARNED IN FP1 RUNS FOR CADILLAC")]),
}

def px(s, col, k):           # pixel-font text block scaled k times (same 3x5 font as the scenes)
    t = Image.new("RGB", (len(s)*4+1, 7), BG); tx(ImageDraw.Draw(t), 0, 1, s, col)
    return t.resize((t.width*k, t.height*k), Image.NEAREST)
def paste_px(im, x, y, s, col, k):
    b = px(s, col, k); m = Image.eval(b.convert("L"), lambda v: 255 if v > 30 else 0); im.paste(b, (x, y), m)

def counter(im, d, i, st, first):
    y = 135
    paste_px(im, 40, y, f"0{i+1}", st["col"], 12)                       # 01 in story colour
    d.line([(158, y+80), (182, y+4)], fill=C["rule"], width=10)         # slash
    paste_px(im, 196, y, "03", hx("#3b4656"), 12)                       # 03 big, subdued
    for j in range(3):                                                  # colour-coded progress
        R(d, 340+j*60, y+56, 390+j*60, y+70, st["col"] if j == i else C["rule"])
    lab = "NEWS FLASH"; text(im, W-40-tlen("labelb", lab), y+36, lab, "labelb", C["red"])
    text(im, W-40-tlen("label", st["tag"]), y+70, st["tag"], "label", C["mute"])

def card(d, im, y, c, stat, h1, h2, ctx):
    r(d, 6, y, 194, y+38, BOXC); r(d, 6, y, 8, y+38, c)
    sc = px(stat, c, 2); m = Image.eval(sc.convert("L"), lambda v: 255 if v > 30 else 0)
    im.paste(sc, (12 + max(0, (34-sc.width)//2), y+12), m)
    tx(d, 50, y+7, h1, INK); tx(d, 50, y+15, h2, INK); tx(d, 50, y+28, ctx, MUT)

def scene_for(order, i):
    st = STORIES[order[i]]
    def s():
        im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
        for k, cd in enumerate(st["cards"]): card(d, im, 6+k*44, st["col"], *cd)
        if i < 2: tx(d, 6, 101, f"NEXT: {STORIES[order[i+1]]['teaser']}  >>>", GREEN)
        else:     tx(d, 6, 101, "THAT'S ALL 3. FOLLOW FOR MORE", GREEN)
        return im
    return s

def slide(k, head, order, foot, name):
    im, d = page(k, 3, DATE)
    counter(im, d, k-1, STORIES[order[k-1]], k == 1)
    y = headline(im, head, top=330)
    framed(im, scene_for(order, k-1)(), 40, y + 100)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

HEAD = {"v8": "V8 ENGINES RETURN TO F1 IN 2030", "pia": "PIASTRI GETS A 10-PLACE GRID DROP", "bot": "BOTTAS STAYS, NO 2027 SEAT FOR HERTA"}
HEAD3 = {"v8": "THE V8 IS BACK FROM 2030", "pia": "PIASTRI STARTS 10 PLACES BACK", "bot": "CADILLAC KEEPS BOTTAS FOR 2027"}
BOD = {"v8": "FIA, F1, teams and engine makers all signed up.", "pia": "He is fitting his fifth combustion engine of 2026.",
       "bot": "Same Cadillac line-up next year: Bottas and Perez."}
FIG = ["Story 1 of 3. Swipe for the next one.", "Story 2 of 3. One more to go.", "Story 3 of 3."]
V = {"1": (["v8", "pia", "bot"], HEAD), "2": (["pia", "v8", "bot"], HEAD), "3": (["v8", "bot", "pia"], HEAD3)}
for v, (order, heads) in V.items():
    for i in range(3):
        slide(i+1, heads[order[i]], order, "", f"{v}_{i+1}")
names = [f"{v}_{i}" for v in "123" for i in "123"]
sh = Image.new("RGB", (3*550+10, 3*685+10), (60, 60, 60))
for k, n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540, 675)), (10+(k%3)*550, 10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
