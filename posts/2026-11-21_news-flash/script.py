import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_flash"').replace('DATE = "07.11.26"','DATE = "21.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "NEWS FLASH 01"'))
# NEWS FLASH No. 1 (Marius 21.11.: short-headline carousel when there are several small stories).
# Sources (2 each, year 2026 checked):
#  V8 2030: FIA press release 20.11.26 + RACER/Motorsport.com/The Race 20.11.26 (2.1 l turbo V8, unanimous, limited hybrid)
#  Bottas 2027 / Herta: RACER 18.11.26 + PlanetF1 18.11.26 (+ F1.com Towriss 20.11.26)
#  Piastri -10: F1.com 18.11.26 + PlanetF1 + Autosport (5th ICE, limit 4)
#  FP1 washout: OpenF1 race control + The Race/PlanetF1 (no times, 20 laps)
#  FP2: OpenF1 session_result + F1.com (RUS 1:47.272, GAS +0.071, LEC +0.333, inters)
#  Left out (1 source only): Aron leaves Alpine / Vesti; WMSC Shanghai vote.
YEL = hx("#f5c542"); BLUE = hx("#60a5fa")

def ico_v8(d, x, y):            # V8 block: two banks of 4 cylinders + turbo
    for i in range(4):
        r(d, x+2+i*5, y+3, x+5+i*5, y+8, INK); r(d, x+2+i*5, y+13, x+5+i*5, y+18, INK)
    r(d, x+1, y+9, x+21, y+12, SL); d.ellipse([x+16, y+17, x+23, y+24], outline=GREEN); r(d, x+19, y+20, x+20, y+21, GREEN)
def ico_seat(d, x, y, col, empty=False):   # driver seat / helmet silhouette
    d.ellipse([x+5, y+2, x+19, y+16], outline=col, fill=None if empty else col); r(d, x+7, y+7, x+17, y+10, BG if not empty else col)
    r(d, x+3, y+18, x+21, y+22, col)
    if empty: d.line([(x+3, y+2), (x+21, y+22)], fill=RED)
def ico_grid(d, x, y):          # grid slots with -10 arrow
    for k in range(4): r(d, x+2+(k%2)*10, y+2+k*5, x+8+(k%2)*10, y+4+k*5, SL)
    d.line([(x+20, y+2), (x+20, y+20)], fill=RED); d.line([(x+17, y+17), (x+20, y+21), (x+23, y+17)], fill=RED)
def ico_rain(d, x, y):
    d.ellipse([x+2, y+3, x+14, y+13], fill=SL); d.ellipse([x+9, y+1, x+22, y+13], fill=SL); r(d, x+4, y+9, x+20, y+13, SL)
    for k in range(4): d.line([(x+5+k*5, y+16), (x+3+k*5, y+22)], fill=BLUE)
def ico_watch(d, x, y):
    d.ellipse([x+3, y+4, x+21, y+22], outline=INK); r(d, x+10, y+1, x+14, y+3, INK); d.line([(x+12, y+13), (x+12, y+7)], fill=GREEN); d.line([(x+12, y+13), (x+17, y+15)], fill=GREEN)

def card(d, y, icon, head1, head2, ctx, col):
    r(d, 6, y, 194, y+38, BOXC); r(d, 6, y, 8, y+38, col)
    icon(d, 12, y+7)
    tx(d, 42, y+6, head1, INK); tx(d, 42, y+14, head2, INK); tx(d, 42, y+27, ctx, MUT)

CUR = [1]
def banner(d, n):
    n = CUR[0]
    r(d, 6, 4, 50, 12, RED); tx(d, 9, 6, "NEWS FLASH", INK)
    tx(d, 56, 6, f"{n} OF 3", MUT); tx(d, 150, 6, "21 NOV 2026", MUT)

def s_engine():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im); banner(d, 1)
    card(d, 18, ico_v8, "V8S RETURN IN 2030", "2.1 L TURBO, LIMITED HYBRID", "FIA, FOM, TEAMS + PU MAKERS: UNANIMOUS", GREEN)
    card(d, 62, lambda d_, x, y: ico_seat(d_, x, y, hx(TC["BOT"])), "BOTTAS STAYS AT CADILLAC", "NEXT TO PEREZ IN 2027", "LINE-UP UNCHANGED FOR YEAR TWO", hx(TC["BOT"]))
    calm(d); return im
def s_grid():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im); banner(d, 2)
    card(d, 18, ico_grid, "PIASTRI: 10-PLACE GRID DROP", "FIFTH ENGINE OF 2026", "LIMIT IS FOUR, RELIABILITY ISSUE", hx(TC["PIA"]))
    card(d, 62, lambda d_, x, y: ico_seat(d_, x, y, MUT, empty=True), "NO 2027 SEAT FOR HERTA", "DESPITE HIS SUPER LICENCE", "REPORTEDLY TURNED DOWN RESERVE ROLE", MUT)
    calm(d); return im
def s_track():
    im = Image.new("RGB", (200, 120), BG); d = ImageDraw.Draw(im); banner(d, 3)
    card(d, 18, ico_rain, "FP1 WASHOUT IN VEGAS", "20 LAPS, ZERO TIMES", "WET TRACK, LOW GRIP ALL SESSION", BLUE)
    card(d, 62, ico_watch, "RUSSELL TOPS WET FP2", "1:47.272 ON INTERS", "GASLY +0.071, LECLERC +0.333", hx(TC["RUS"]))
    calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    CUR[0] = k
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

# V1: engine first
slide(1, "NEWS FLASH: V8 ENGINES ARE COMING BACK TO F1 IN 2030", s_engine, "Two headlines you might have missed.", "2.1 litre turbo V8, agreed by everyone involved.", "SWIPE >>>", "1_1")
slide(2, "PIASTRI DROPS 10 PLACES, HERTA MISSES OUT", s_grid, "Grid and driver market news.", "Bottas stays, so Cadillac has no seat for Herta.", "SWIPE >>>", "1_2")
slide(3, "VEGAS SO FAR: NO TIMES IN FP1, RUSSELL TOPS FP2", s_track, "The weekend before qualifying.", "Qualifying: Fri 20:00 local, Sat 04:00 UTC.", "FOLLOW", "1_3")
# V2: Vegas first, future last
slide(1, "NEWS FLASH: RAIN, A GRID DROP AND THE V8 RETURN", s_track, "Vegas practice in two lines.", "FP1 washed out, FP2 on intermediates.", "SWIPE >>>", "2_1")
slide(2, "PIASTRI STARTS 10 PLACES BACK ON SATURDAY", s_grid, "Grid and driver market news.", "His fifth combustion engine of the season.", "SWIPE >>>", "2_2")
slide(3, "2030: TURBO V8S. 2027: BOTTAS STAYS", s_engine, "Looking ahead.", "Simpler, lighter and cheaper power units, says the FIA.", "FOLLOW", "2_3")
# V3: punchy
slide(1, "THE V8 IS BACK: F1 AGREES 2030 ENGINE PLAN", s_engine, "News flash, 21 November.", "Plus: Bottas keeps his Cadillac seat.", "SWIPE >>>", "3_1")
slide(2, "GRID DROP FOR PIASTRI, NO SEAT FOR HERTA", s_grid, "Two drivers, two setbacks.", "Piastri: 5th engine. Herta: no 2027 drive.", "SWIPE >>>", "3_2")
slide(3, "ZERO TIMES IN FP1, RUSSELL FASTEST IN FP2", s_track, "Las Vegas practice recap.", "Qualifying: Sat 04:00 UTC, 23:00 New York (Fri).", "FOLLOW", "3_3")
names = [f"{v}_{i}" for v in "123" for i in "123"]
sh = Image.new("RGB", (3*550+10, 3*685+10), (60, 60, 60))
for k, n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540, 675)), (10+(k%3)*550, 10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
