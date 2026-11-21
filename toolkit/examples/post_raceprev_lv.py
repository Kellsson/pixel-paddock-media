import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_rprev"').replace('DATE = "07.11.26"','DATE = "21.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "36.11N 115.17W"'))
# Las Vegas GP 2026 race preview (Marius 21.11.: grid, race times, Russell vs Verstappen feud).
# Sources (2 each, 2026 checked):
#  Grid: The Race "starting grid after five penalties" 21.11. + Motorsport.com starting grid 21.11. (identical)
#  Penalties: ANT +5, PIA +10, SAI +10, STR +10, BEA +35 (The Race + Motorsport); quali P: F1.com + Motorsport
#  Feud: Russell "Somebody's got to stand up to that guy" (Motorsport + RACER headline); Verstappen "Nothing happened" (Motorsport)
#        Verstappen quote "Nothing happened" left out (only 1 source checked)
#  Stewards: warning for VER, change of direction under braking (Motorsport + The Race)
#  Standings: VER 279, RUS 262, HAM 261 (Jolpica + Motorsport)
#  Times: F1.com schedule (Sat 20:00 local = Sun 04:00 UTC), converted.
GRID = ["VER","RUS","NOR","HAD","LIN","ANT","LAW","GAS","COL","LEC","HAM","HUL","BOR","ALB","CAM","PER","PIA","ALO","BOT","SAI","STR","BEA"]
PEN = {"ANT":5,"PIA":10,"SAI":10,"STR":10,"BEA":35}

def s_grid():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"STARTING GRID, P1-P22",INK)
    for i,c in enumerate(GRID):
        row=i//2; col=i%2
        x=8+row*17; y=20+col*30+(0 if col==0 else 6)
        r(d,x,y,x+14,y+22,BOXC); r(d,x,y,x+14,y+2,hx(TC[c]))
        if c in PEN: d.rectangle([x,y,x+14,y+22],outline=RED)
        tx(d,x+1,y+6,c,INK); tx(d,x+1,y+14,str(i+1),MUT)
    d.line([(4,16),(4,82)],fill=INK)
    tx(d,6,90,"RED = GRID PENALTY",RED); tx(d,6,98,"5 CARS, ALL FOR POWER UNIT PARTS",MUT)
    calm(d); return im

def s_pen():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FIVE GRID PENALTIES",INK)
    rows=[("ANT","+5","Q1 > P6"),("PIA","+10","Q7 > P17"),("SAI","+10","Q14 > P20"),("STR","+10","Q20 > P21"),("BEA","+35","Q22 > P22")]
    for k,(c,a,b) in enumerate(rows):
        y=14+k*17
        r(d,6,y,194,y+14,BOXC); r(d,6,y,8,y+14,hx(TC[c]))
        tx(d,12,y+5,c,INK)
        d.rectangle([30,y+2,54,y+12],outline=RED); tx(d,42-len(a)*2,y+5,a,RED)
        tx(d,62,y+5,b,INK); tx(d,130,y+5,"PU PARTS",MUT)
    tx(d,6,102,"Q = QUALIFYING, P = GRID SLOT",MUT); calm(d); return im

def s_feud():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FRONT ROW, AFTER FP3 CONTACT",INK)
    for k,(c,p,nm) in enumerate((("VER","P1","VERSTAPPEN"),("RUS","P2","RUSSELL"))):
        x=8+k*96; col=hx(TC[c])
        r(d,x,16,x+88,56,BOXC); r(d,x,16,x+88,18,col)
        tx(d,x+6,24,p,GREEN); tx(d,x+22,24,nm,INK)
        tx(d,x+6,36,"WDC",MUT); tx(d,x+30,36,"P2  279" if c=="VER" else "P3  262",INK)
        tx(d,x+6,46,"WINS 2026",MUT); tx(d,x+50,46,"3",INK)
    r(d,6,62,194,84,BOXC); r(d,6,62,8,84,hx(TC["RUS"]))
    tx(d,12,66,"RUSSELL: SOMEBODY'S GOT TO",INK); tx(d,12,74,"STAND UP TO THAT GUY",INK)
    r(d,6,88,194,104,BOXC); r(d,6,88,8,104,hx("#facc15"))
    tx(d,12,94,"STEWARDS: WARNING FOR VERSTAPPEN",INK)
    calm(d); return im

def s_p2():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"THE FIGHT FOR P2 IN THE TITLE",INK)
    rows=[("VER",279),("RUS",262),("HAM",261),("LEC",249),("NOR",246)]
    for k,(c,p) in enumerate(rows):
        y=16+k*15; w=int((p-200)/80*120)
        tx(d,6,y+4,f"P{k+2}",MUT); tx(d,22,y+4,c,INK)
        r(d,42,y+2,42+w,y+10,hx(TC[c])); tx(d,46+w,y+4,str(p),INK)
    tx(d,6,96,"VER 17 AHEAD OF RUS, HAM 1 BEHIND",INK); tx(d,6,104,"3 RACES TO GO, VEGAS FIRST",MUT)
    calm(d); return im

def s_times():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"LIGHTS OUT, LAS VEGAS GP",INK)
    rows=[("LAS VEGAS","20:00","SAT"),("UTC","04:00","SUN"),("MEXICO CITY","22:00","SAT"),("NEW YORK","23:00","SAT"),("SAO PAULO","01:00","SUN"),("LONDON","04:00","SUN"),("TOKYO","13:00","SUN")]
    for k,(city,t,n) in enumerate(rows):
        y=14+k*12
        r(d,6,y,194,y+10,SL if k==0 else BOXC)
        tx(d,12,y+3,city,INK); tx(d,120,y+3,t,GREEN if k==0 else INK); tx(d,150,y+3,n,MUT)
    tx(d,6,102,"50 LAPS, 6.201 KM",MUT); calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

# V1: grid -> feud -> times
slide(1,"VERSTAPPEN ON POLE, RUSSELL NEXT TO HIM",s_grid,"Las Vegas GP starting grid.","Fastest qualifier Antonelli starts sixth.","SWIPE >>>","1_1")
slide(2,"RUSSELL VS VERSTAPPEN: ROUND TWO FROM ROW ONE",s_feud,"The front row after their FP3 contact.","The stewards gave Verstappen a warning.","SWIPE >>>","1_2")
slide(3,"LIGHTS OUT SAT 20:00 LOCAL, SUN 04:00 UTC",s_times,"Race start in seven time zones.","50 laps of the Las Vegas Strip Circuit.","FOLLOW","1_3")
# V2: feud -> penalties -> times
slide(1,"FRONT ROW FEUD: RUSSELL STARTS NEXT TO VERSTAPPEN",s_feud,"After their clash in final practice.","Russell: somebody has to stand up to him.","SWIPE >>>","2_1")
slide(2,"FIVE GRID PENALTIES RESHAPE THE VEGAS GRID",s_pen,"Qualifying result vs starting slot.","Piastri falls from seventh to 17th.","SWIPE >>>","2_2")
slide(3,"RACE: SAT 20:00 IN VEGAS, SUN 04:00 UTC",s_times,"Race start in seven time zones.","Saturday night in Vegas, Sunday morning in Europe.","FOLLOW","2_3")
# V3: penalties -> P2 fight -> grid
slide(1,"ANTONELLI FASTEST, BUT VERSTAPPEN HAS POLE",s_pen,"Five drivers take grid penalties.","Antonelli drops five places to P6.","SWIPE >>>","3_1")
slide(2,"VERSTAPPEN AND RUSSELL: 17 POINTS FOR P2",s_p2,"Drivers' standings before Las Vegas.","Hamilton is one point behind Russell.","SWIPE >>>","3_2")
slide(3,"THE GRID: VERSTAPPEN, RUSSELL, NORRIS",s_grid,"Las Vegas GP starting grid.","Lights out Sat 20:00 local, Sun 04:00 UTC.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
