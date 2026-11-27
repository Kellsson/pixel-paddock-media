import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_flash2"').replace('DATE = "07.11.26"','DATE = "27.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "NEWS FLASH 02"'))
from pp import text, tlen, framed
# NEWS FLASH No. 2 (Marius 27.11.: "weekend preview / newsflash"), same v5 layout as No. 1.
# Sources (2+ each, 2026 checked):
#  Bearman Haas 2027 / grid complete: The Race + Motorsport + F1.com + RACER 26.11.26 (F1.com subheading "Bearman and Ocon" is a typo)
#  Cost cap: The Race + Motorsport + RACER + F1.com 25.11.26 (Williams 627,000 GBP = 0.48 pct, 1.5 pct less ATR for 12 months; Alpine procedural only)
#  Russell reply: Motorsport + The Race + RACER 26.11.26 ("amusing", "I stand by what I said")
STORIES = {
 "grid": dict(col=hx(TC["BEA"]), tag="2027 SEATS", teaser="2027 GRID SET",
             cards=[("2027", "BEARMAN STAYS AT HAAS", "THIRD FULL SEASON THERE", "NEW TEAM-MATE: RAFAEL CAMARA"),
                    ("21", "OF 22 SEATS UNCHANGED", "ONLY HAAS HAS A NEW PAIRING", "CAMARA REPLACES OCON")]),
 "cap":  dict(col=hx(TC["ALB"]), tag="COST CAP", teaser="COST CAP BREACH",
             cards=[("0.48", "PERCENT OVER THE 2025 CAP", "WILLIAMS, ABOUT 627,000 GBP", "PLUS 1.5 PCT LESS AERO TESTING"),
                    ("ALP", "ALPINE: PROCEDURAL BREACH", "COSTS WRONGLY LEFT OUT", "NO OVERSPEND, FINE ONLY")]),
 "rus":  dict(col=hx(TC["RUS"]), tag="QATAR MEDIA DAY", teaser="RUSSELL HITS BACK",
             cards=[("VS", "RUSSELL: VERSTAPPEN'S WORDS", "WERE AMUSING", "AFTER SO FAR BELOW MY LEVEL"),
                    ("P2", "I STAND BY WHAT I SAID", "RUSSELL KEEPS HIS STANCE", "HE IS 40 POINTS BEHIND VER")]),
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
        im = Image.new("RGB", (200, 94), BG); d = ImageDraw.Draw(im)
        for k, cd in enumerate(st["cards"]): card(d, im, 6+k*44, st["col"], *cd)
        return im
    return s

def slide(k, head, order, foot, name):
    im, d = page(k, 3, DATE)
    counter(im, d, k-1, STORIES[order[k-1]], k == 1)
    y = headline(im, head, top=330)
    yb = framed(im, scene_for(order, k-1)(), 40, y + 100)
    i = k-1
    nxt = f"NEXT: {STORIES[order[i+1]]['teaser']}  >>>" if i < 2 else "THAT'S ALL 3. FOLLOW FOR MORE"
    text(im, 40, yb + 80, nxt, "labelb", C["red"])
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

HEAD = {"grid": "BEARMAN STAYS, THE 2027 GRID IS COMPLETE", "cap": "WILLIAMS AND ALPINE BREACHED THE 2025 COST CAP", "rus": "RUSSELL ON VERSTAPPEN: AMUSING"}
HEAD3 = {"grid": "ONLY ONE NEW PAIRING FOR 2027", "cap": "WILLIAMS LOSES WIND TUNNEL TIME", "rus": "RUSSELL STANDS BY HIS VEGAS WORDS"}
V = {"1": (["grid", "cap", "rus"], HEAD), "2": (["cap", "grid", "rus"], HEAD), "3": (["grid", "rus", "cap"], HEAD3)}
for v, (order, heads) in V.items():
    for i in range(3):
        slide(i+1, heads[order[i]], order, "", f"{v}_{i+1}")
names = [f"{v}_{i}" for v in "123" for i in "123"]
sh = Image.new("RGB", (3*550+10, 3*685+10), (60, 60, 60))
for k, n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540, 675)), (10+(k%3)*550, 10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
