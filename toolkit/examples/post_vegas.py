import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_vegas"').replace('DATE = "07.11.26"','DATE = "19.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "36.11N 115.17W"'))
# Las Vegas GP 2026 preview. Times: F1.com (Las Vegas = UTC-8). History: Jolpica circuits/vegas.
PINK = hx("#ff3d9a")

# --- stylised Strip Circuit (anticlockwise; north up). Schematic, not to scale.
TRACK = [(150,92),(120,92),(70,92),(58,92),(52,88),(56,84),(48,80),(48,40),(48,24),(56,17),(70,16),(122,16),
         (132,15),(142,19),(146,27),(140,34),(138,40),(138,78),(144,82),(156,84),(158,89),(150,92)]
def draw_track(d, col=INK, w=2):
    for (x0,y0),(x1,y1) in zip(TRACK, TRACK[1:]):
        d.line([(x0,y0),(x1,y1)], fill=col, width=w)

def s_track():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"LAS VEGAS STRIP CIRCUIT",INK)
    draw_track(d, SL, 4); draw_track(d, INK, 2)
    d.line([(48,32),(48,72)], fill=PINK, width=2)           # the Strip
    tx(d,8,50,"THE",PINK); tx(d,4,58,"STRIP",PINK)
    d.ellipse([150,14,162,26], outline=GREEN); tx(d,166,17,"SPHERE",MUT)
    r(d,134,90,136,95,GREEN); tx(d,104,98,"START",GREEN)  # start line
    tx(d,166,86,"PIT",MUT)
    tx(d,60,60,"6.201 KM",INK); tx(d,60,68,"50 LAPS",MUT); tx(d,60,76,"ANTICLOCKWISE",MUT)
    calm(d); return im

def s_race_tz():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"LIGHTS OUT, LAS VEGAS GP",INK)
    rows=[("LAS VEGAS","20:00","SAT"),("UTC","04:00","SUN"),("NEW YORK","23:00","SAT"),("SAO PAULO","01:00","SUN"),("BERLIN","05:00","SUN"),("TOKYO","13:00","SUN")]
    for k,(city,t,n) in enumerate(rows):
        y=16+k*13
        r(d,6,y,194,y+10,SL if k==0 else BOXC)
        tx(d,12,y+3,city,INK); tx(d,120,y+3,t,GREEN if k==0 else INK); tx(d,150,y+3,n,MUT)
    tx(d,6,98,"SAT 21 NOV LOCAL = SUN 22 NOV UTC",MUT); calm(d); return im

def s_weekend():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"THE WEEKEND, LOCAL VS UTC",INK)
    tx(d,50,16,"LAS VEGAS",MUT); tx(d,130,16,"UTC",MUT)
    rows=[("FP1","THU 16:30","FRI 00:30"),("FP2","THU 20:00","FRI 04:00"),("FP3","FRI 16:30","SAT 00:30"),("QUALI","FRI 20:00","SAT 04:00"),("RACE","SAT 20:00","SUN 04:00")]
    for k,(s_,a,b) in enumerate(rows):
        y=26+k*14; hl=s_=="RACE"
        r(d,6,y,194,y+11,SL if hl else BOXC)
        tx(d,10,y+3,s_,GREEN if hl else INK); tx(d,50,y+3,a,INK); tx(d,130,y+3,b,GREEN if hl else INK)
    tx(d,6,100,"UTC IS ALWAYS 8H AHEAD",MUT); calm(d); return im

HIST=[("2023","VER",2,"LEC"),("2024","RUS",1,"RUS"),("2025","VER",2,"NOR")]
def s_history():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"VEGAS WINNERS SINCE 2023",INK)
    for k,(yr,w,g,pole) in enumerate(HIST):
        x=8+k*64; r(d,x,16,x+56,82,BOXC); r(d,x,16,x+56,18,hx(TC[w]))
        tx(d,x+18,24,yr,MUT); tx(d,x+22,38,w,INK)
        tx(d,x+6,52,"FROM",MUT); tx(d,x+30,52,f"P{g}",GREEN)
        tx(d,x+6,66,"POLE",MUT); tx(d,x+30,66,pole,INK if pole!=w else GREEN)
    tx(d,6,92,"POLE CONVERTED: 1 OF 3",INK); calm(d); return im

COMEBACK=[("2023","PER",11,3,"#3671c6"),("2024","HAM",10,2,"#27f4d2"),("2025","ANT",17,3,"#27f4d2")]   # team colours of that year
def s_comeback():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"PODIUM FROM P10 OR LOWER",INK)
    def Y(p): return 40+(p-1)*2.8
    for k,(yr,c,g,f,tc) in enumerate(COMEBACK):
        x=8+k*64; col=hx(tc)
        r(d,x,14,x+56,98,BOXC); r(d,x,14,x+56,16,col)
        tx(d,x+4,20,yr,MUT); tx(d,x+4,29,c,INK); tx(d,x+36,29,f"+{g-f}",GREEN)
        r(d,x+12,int(Y(1)),x+13,int(Y(20)),SL)
        r(d,x+10,int(Y(f)),x+15,int(Y(g)),col)
        r(d,x+8,int(Y(f))-1,x+17,int(Y(f))+1,col)
        tx(d,x+22,int(Y(g))-2,f"P{g}",MUT); tx(d,x+22,int(Y(f))-2,f"P{f}",GREEN)
    tx(d,6,104,"EVERY YEAR SO FAR",INK); calm(d); return im

def s_stats():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"VEGAS IN SIX NUMBERS",INK)
    tiles=[("6.201","KM PER LAP"),("50","LAPS"),("20:00","LOCAL START"),("3","RACES SINCE 2023"),("1","POLE TURNED INTO A WIN"),("2037","CONTRACT RUNS TO")]
    for k,(big,sm) in enumerate(tiles):
        x=6+(k%2)*96; y=14+(k//2)*28
        r(d,x,y,x+90,y+24,BOXC); tx(d,x+4,y+5,big,GREEN); tx(d,x+4,y+15,sm,MUT)
    calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

slide(1,"LAS VEGAS: 50 NIGHT LAPS OF THE 6.201 KM STRIP CIRCUIT",s_track,"Las Vegas Strip Circuit, schematic.","Round 21 of 23, the first of three to go.","SWIPE >>>","1_1")
slide(2,"LIGHTS OUT SAT 20:00 LOCAL, SUN 04:00 UTC",s_race_tz,"Race start in six time zones.","Saturday night in Vegas is Sunday in Europe and Asia.","SWIPE >>>","1_2")
slide(3,"A PODIUM FROM P10 OR LOWER IN EVERY VEGAS RACE",s_comeback,"Lowest grid slot to reach the podium.","Perez 2023, Hamilton 2024, Antonelli 2025.","FOLLOW","1_3")
slide(1,"VERSTAPPEN WON 2 OF 3 VEGAS RACES, BOTH FROM P2",s_history,"Winners and pole sitters since 2023.","Only Russell has turned Vegas pole into a win.","SWIPE >>>","2_1")
slide(2,"FP1 THURSDAY 16:30 LOCAL, RACE SATURDAY 20:00",s_weekend,"Every session, local time vs UTC.","Las Vegas runs 8 hours behind UTC.","SWIPE >>>","2_2")
slide(3,"6.201 KM, 50 LAPS, CONTRACT UNTIL 2037",s_stats,"Six numbers for the weekend.","Las Vegas is on the calendar for 12 more seasons.","FOLLOW","2_3")
slide(1,"PEREZ P11, HAMILTON P10, ANTONELLI P17 TO THE PODIUM",s_comeback,"Lowest grid slot to reach the podium.","Every Vegas race so far had a comeback podium.","SWIPE >>>","3_1")
slide(2,"VEGAS: DOWN THE STRIP, AROUND THE SPHERE, 50 TIMES",s_track,"Las Vegas Strip Circuit, schematic.","6.201 km, raced anticlockwise.","SWIPE >>>","3_2")
slide(3,"QUALI FRI 20:00 LOCAL, RACE SAT 20:00 LOCAL",s_weekend,"Every session, local time vs UTC.","Race: Sunday 04:00 UTC.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
