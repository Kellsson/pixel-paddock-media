import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_flash"').replace('DATE = "07.11.26"','DATE = "21.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "NEWS FLASH 01"'))
# NEWS FLASH No. 1, v2 (Marius 21.11.: clearly 3 stories, one per slide, info first, no noise, swipe prompt).
# Sources (2 each, year 2026 checked):
#  V8 2030: FIA press release 20.11.26 + RACER/Motorsport.com/The Race 20.11.26
#  Piastri -10: F1.com 18.11.26 + PlanetF1 + Autosport (5th ICE, limit 4, reliability)
#  Bottas 2027 / Herta: RACER 18.11.26 + PlanetF1 18.11.26 (Herta super licence points, no 2027 seat)
#  Left out (1 source only): Aron/Vesti Alpine, Herta declined reserve role, WMSC Shanghai vote.
STORIES = {
 "v8":  dict(tag="ENGINES", col=GREEN, title=["V8S ARE BACK"], stat="2030",
             rows=[("ENGINE","2.1 L TURBO V8"),("HYBRID","LIMITED"),("AGREED","UNANIMOUSLY"),("GOAL","LIGHTER, SIMPLER, CHEAPER")],
             teaser="V8 RETURN"),
 "pia": dict(tag="VEGAS GRID", col=hx(TC["PIA"]), title=["PIASTRI DROPS"], stat="-10",
             rows=[("WHY","5TH ENGINE OF 2026"),("LIMIT","4 PER SEASON"),("CAUSE","RELIABILITY ISSUE"),("RACE","SAT 20:00 LOCAL")],
             teaser="PIASTRI -10"),
 "bot": dict(tag="2027 SEATS", col=hx(TC["BOT"]), title=["BOTTAS STAYS"], stat="2027",
             rows=[("TEAM","CADILLAC"),("TEAM-MATE","PEREZ"),("LEFT OUT","COLTON HERTA"),("HERTA","HAS SUPER LICENCE POINTS")],
             teaser="BOTTAS STAYS"),
}

def big(im, x, y, s, col, k=2):
    t = Image.new("RGB", (len(s)*4+2, 7), BG); tx(ImageDraw.Draw(t), 0, 1, s, col)
    t = t.resize((t.width*k, t.height*k), Image.NEAREST); im.paste(t, (x, y - k))

def scene_for(order, i):
    key = order[i]; st = STORIES[key]
    def s():
        im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im)
        # story counter: big number + 3-segment progress
        big(im, 6, 5, f"0{i+1}", st["col"], 3); tx(d, 32, 13, "OF 03", MUT)
        for j in range(3):
            r(d, 60+j*20, 12, 76+j*20, 15, st["col"] if j == i else (SL if j > i else MUT))
        tx(d, 196-len(st["tag"])*4, 6, st["tag"], MUT); tx(d, 196-len("NEWS FLASH")*4, 13, "NEWS FLASH", RED)
        r(d, 6, 22, 194, 22, SL)
        # title + key stat
        for k, ln in enumerate(st["title"]): big(im, 6, 28+k*14, ln, INK, 2)
        y0 = 28 + len(st["title"])*14
        big(im, 194-len(st["stat"])*8, 28, st["stat"], st["col"], 2)
        # fact rows
        for k, (a, b) in enumerate(st["rows"]):
            y = y0 + 2 + k*10
            r(d, 6, y, 8, y+6, st["col"]); tx(d, 12, y+1, a, MUT); tx(d, 56, y+1, b, INK)
        # swipe / end line
        yb = y0 + 2 + len(st["rows"])*10 + 6
        if i < 2: tx(d, 6, yb, f"NEXT: {STORIES[order[i+1]]['teaser']}  >>>", GREEN)
        else:     tx(d, 6, yb, "THAT'S ALL 3. FOLLOW FOR MORE", GREEN)
        return im
    return s

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

V = {
 "1": (["v8","pia","bot"], ["NEWS FLASH: 3 STORIES, 3 SWIPES. 1: V8S RETURN IN 2030",
                            "2: PIASTRI DROPS 10 PLACES IN VEGAS",
                            "3: BOTTAS KEEPS HIS CADILLAC SEAT"]),
 "2": (["pia","v8","bot"], ["NEWS FLASH 1 OF 3: PIASTRI 10-PLACE GRID DROP",
                            "NEWS FLASH 2 OF 3: V8 ENGINES BACK IN 2030",
                            "NEWS FLASH 3 OF 3: BOTTAS STAYS, HERTA OUT"]),
 "3": (["v8","bot","pia"], ["THIS WEEK IN 3 SWIPES. 01: THE V8 IS BACK",
                            "02: BOTTAS STAYS AT CADILLAC FOR 2027",
                            "03: PIASTRI STARTS 10 PLACES BACK"]),
}
FIG = ["Story 1 of 3. Swipe for the next one.", "Story 2 of 3. One more to go.", "Story 3 of 3."]
BOD = {"v8": "FIA, F1, teams and engine makers all signed up.", "pia": "Fifth combustion engine of the season, limit is four.",
       "bot": "Same line-up next year: Bottas and Perez."}
for v, (order, heads) in V.items():
    for i in range(3):
        slide(i+1, heads[i], scene_for(order, i), FIG[i], BOD[order[i]], "SWIPE >>>" if i < 2 else "FOLLOW", f"{v}_{i+1}")
names = [f"{v}_{i}" for v in "123" for i in "123"]
sh = Image.new("RGB", (3*550+10, 3*685+10), (60, 60, 60))
for k, n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540, 675)), (10+(k%3)*550, 10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
