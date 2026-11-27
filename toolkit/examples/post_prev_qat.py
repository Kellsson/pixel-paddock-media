import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_qprev"').replace('DATE = "07.11.26"','DATE = "27.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "25.49N 51.45E"'))
# Qatar GP 2026 weekend preview (Marius 27.11.: "weekend preview").
# Sources (2 each, 2026 checked):
#  27-lap limit per set, 57 laps -> min 2 stops, 2025 limit 25: Pirelli statement via F1.com explained + The Race 26.11.
#  Front min pressure 29 psi (highest ever at weekend start; previous 2026 max 28 psi Suzuka/Silverstone/Spa), rear 27.5: The Race 26.11. (FIA notes)
#  C1/C2/C3, 2 hard / 4 medium / 7 soft = 13 sets: F1.com 26.11.; hardest three compounds also The Race
#  Standings after R21: ANT 402 (champion), VER 304, HAM 267, RUS 264, NOR 264, LEC 250: Jolpica + Motorsport/F1.com Vegas result
#  Times: Jolpica + The Race schedule (race 16:00 UTC = 19:00 Doha = 11:00 ET)
HARD, MED, SOFT = hx("#e5e7eb"), hx("#facc15"), hx("#ef4444")

def s_limit():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"57 LAPS, MAX 27 PER TYRE SET",INK)
    x0, x1 = 8, 192; L = lambda n: x0 + int((x1-x0)*n/57)
    # one-stop impossible: 30 + 27 would need a 30-lap stint
    tx(d,6,18,"ONE STOP",MUT)
    r(d,L(0),28,L(28)-1,38,SOFT); r(d,L(28),28,L(57),38,MED)
    d.rectangle([L(27),26,L(28),40],fill=RED); tx(d,L(29)+2,30,"> 27 LAPS",BG)
    tx(d,6,46,"TWO STOPS",GREEN)
    r(d,L(0),56,L(19)-1,66,MED); r(d,L(19),56,L(38)-1,66,HARD); r(d,L(38),56,L(57),66,MED)
    for a,b in ((0,19),(19,38),(38,57)): tx(d,L(a)+12,59,str(b-a),BG)
    for n in (0,27,57):
        tx(d,L(n)-len(str(n))*2,72,str(n),MUT)
    d.line([(L(27),70),(L(27),66)],fill=RED)
    tx(d,6,88,"SC AND VSC LAPS COUNT TOO",INK); tx(d,6,98,"LIMIT 2025: 25 LAPS",MUT)
    calm(d); return im

def s_psi():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"MINIMUM FRONT TYRE PRESSURE",INK)
    rows=[("QATAR",29.0,GREEN),("SUZUKA",28.0,MUT),("SILVERSTONE",28.0,MUT),("SPA",28.0,MUT)]
    for k,(n,p,c) in enumerate(rows):
        y=18+k*16; w=int((p-24)/6*120)
        tx(d,6,y+3,n,INK if k==0 else MUT)
        r(d,62,y,62+w,y+9,c); tx(d,66+w,y+2,f"{p:.0f} PSI",INK)
    r(d,6,82,194,101,BOXC); r(d,6,82,8,101,GREEN)
    tx(d,12,85,"HIGHEST EVER AT THE START",INK); tx(d,12,93,"OF A RACE WEEKEND. REAR: 27.5 PSI",MUT)
    calm(d); return im

def s_sets():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"13 SETS PER DRIVER",INK)
    rows=[("C1 HARD",2,HARD),("C2 MEDIUM",4,MED),("C3 SOFT",7,SOFT)]
    for k,(n,cnt,c) in enumerate(rows):
        y=18+k*24
        tx(d,6,y+7,n,INK); tx(d,58,y+7,f"X{cnt}",MUT)
        for i in range(cnt):
            cx=82+i*16; d.ellipse([cx,y,cx+13,y+13],fill=hx("#1f2937"),outline=c); d.ellipse([cx+4,y+4,cx+9,y+9],fill=BOXC)
    tx(d,6,94,"THE THREE HARDEST COMPOUNDS",INK); tx(d,6,104,"LIKE SUZUKA AND SILVERSTONE",MUT)
    calm(d); return im

def s_p2():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"THE FIGHT FOR P2, 2 RACES LEFT",INK)
    rows=[("VER",304),("HAM",267),("RUS",264),("NOR",264),("LEC",250)]
    for k,(c,p) in enumerate(rows):
        y=16+k*15; w=int((p-230)/80*120)
        tx(d,6,y+4,f"P{k+2}",MUT); tx(d,22,y+4,c,INK)
        r(d,42,y+2,42+w,y+10,hx(TC[c])); tx(d,46+w,y+4,str(p),INK)
    tx(d,6,96,"VER 37 CLEAR, 50 POINTS LEFT",INK); tx(d,6,104,"CHAMPION ANTONELLI: 402",MUT)
    calm(d); return im

def s_times():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"LIGHTS OUT, QATAR GP, SUNDAY",INK)
    rows=[("DOHA","19:00",""),("UTC","16:00",""),("LONDON","16:00",""),("NEW YORK","11:00",""),("LOS ANGELES","08:00",""),("SAO PAULO","13:00",""),("TOKYO","01:00","MON")]
    for k,(city,t,n) in enumerate(rows):
        y=14+k*12
        r(d,6,y,194,y+10,SL if k==0 else BOXC)
        tx(d,12,y+3,city,INK); tx(d,120,y+3,t,GREEN if k==0 else INK); tx(d,150,y+3,n,MUT)
    tx(d,6,102,"QUALI SAT 18:00 UTC",MUT); calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

# V1: tyre limit -> sets -> times
slide(1,"QATAR: NO TYRE SET MAY RUN MORE THAN 27 LAPS",s_limit,"Pirelli's stint cap for Lusail.","57 laps means at least two stops for everyone.","SWIPE >>>","1_1")
slide(2,"PIRELLI BRINGS ITS HARDEST TYRES TO LUSAIL",s_sets,"Allocation per driver.","Two hard, four medium and seven soft sets.","SWIPE >>>","1_2")
slide(3,"LIGHTS OUT SUNDAY 19:00 IN DOHA, 16:00 UTC",s_times,"Race start in seven time zones.","Qualifying on Saturday at 18:00 UTC.","FOLLOW","1_3")
# V2: limit -> pressure -> P2 fight
slide(1,"FORCED TWO-STOPPER: 27-LAP LIMIT IN QATAR",s_limit,"Why a one-stop is ruled out.","Safety car laps count towards the limit too.","SWIPE >>>","2_1")
slide(2,"RECORD 29 PSI FRONT TYRE PRESSURE",s_psi,"Minimum front pressure, 2026.","Lusail's fast right-handers punish the front-left.","SWIPE >>>","2_2")
slide(3,"VERSTAPPEN 37 POINTS CLEAR IN THE FIGHT FOR P2",s_p2,"Drivers' standings before Qatar.","Russell and Norris are level on 264.","FOLLOW","2_3")
# V3: P2 fight -> limit -> times
slide(1,"TWO RACES LEFT: WHO FINISHES BEHIND ANTONELLI?",s_p2,"Drivers' standings before Qatar.","Hamilton, Russell and Norris split by three points.","SWIPE >>>","3_1")
slide(2,"27 LAPS PER SET, AT LEAST TWO STOPS",s_limit,"Pirelli's stint cap for Lusail.","The limit was 25 laps last year.","SWIPE >>>","3_2")
slide(3,"QATAR GP: SUNDAY 16:00 UTC",s_times,"Race start in seven time zones.","19:00 under the lights in Doha.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
