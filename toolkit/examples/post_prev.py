import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_prev"').replace('DATE = "07.11.26"','DATE = "08.11.26"'))
GRID=["NOR","ANT","LAW","HUL","HAD","BEA","RUS","ALO","ALB","PIA","CAM","LIN","SAI","LEC","COL","GAS","STR","BOT","BOR","HAM","VER","PER"]
PEN={"RUS","LEC","HAM","VER","PER"}
def s_grid():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"STARTING GRID, P1-P22",INK)
    for i,c in enumerate(GRID):
        row=i//2; col=i%2
        x=8+row*17; y=20+col*30+ (0 if col==0 else 6)
        r(d,x,y,x+14,y+22,BOXC); r(d,x,y,x+14,y+2,hx(TC[c]))
        if c in PEN: d.rectangle([x,y,x+14,y+22],outline=RED)
        tx(d,x+1,y+6,c,INK); tx(d,x+1,y+14,str(i+1),MUT)
    d.line([(4,16),(4,82)],fill=INK)
    tx(d,6,90,"RED = GRID PENALTY",RED); tx(d,6,98,"5 CARS DROPPED",MUT)
    calm(d); return im
def s_board():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"GRID PENALTIES, SAO PAULO",INK)
    rows=[("RUS","-5","P2>P7","NEW ICE"),("LEC","-10","P4>P14","NEW ICE"),("HAM","BACK","P20","10 + 65 PLACES"),("VER","BACK","P21","30 PLACES"),("PER","BACK","P22","30 PLACES")]
    for k,(c,a,b,why) in enumerate(rows):
        y=14+k*17
        r(d,6,y,194,y+14,BOXC); r(d,6,y,8,y+14,hx(TC[c]))
        tx(d,12,y+5,c,INK)
        d.rectangle([30,y+2,52,y+12],outline=RED); tx(d,41-len(a)*2,y+5,a,RED)
        tx(d,58,y+5,b,INK); tx(d,98,y+5,why,MUT)
    calm(d); return im
def s_times():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"LIGHTS OUT, SUNDAY 8 NOV",INK)
    rows=[("SAO PAULO","14:00",""),("UTC","17:00",""),("NEW YORK","12:00",""),("LONDON","17:00",""),("BERLIN","18:00",""),("TOKYO","02:00","MON")]
    for k,(city,t,n) in enumerate(rows):
        y=16+k*13
        r(d,6,y,194,y+10,SL if k==0 else BOXC)
        tx(d,12,y+3,city,INK); tx(d,120,y+3,t,GREEN if k==0 else INK)
        if n: tx(d,146,y+3,n,MUT)
    tx(d,6,98,"71 LAPS, 4.309 KM",MUT); calm(d); return im
def s_slope():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"QUALI TOP 10 > GRID",INK)
    Q=["NOR","RUS","ANT","LEC","LAW","HUL","HAD","BEA","ALO","ALB"]
    gp={c:GRID.index(c)+1 for c in GRID}
    tx(d,22,13,"QUALI",MUT); tx(d,150,13,"GRID",MUT)
    def Y(p): return 20+(p-1)*6.2
    for i,c in enumerate(Q):
        lab=f"P{i+1} {c}"; tx(d,44-len(lab)*4,int(Y(i+1)),lab,INK)
        g=gp[c]; d.line([(46,int(Y(i+1))+2),(146,int(Y(g))+2)],fill=hx(TC[c]))
        tx(d,150,int(Y(g)),f"P{g} {c}",INK)
    calm(d); return im
def s_tiles65():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"HAMILTON: 65 PLACES ON TOP OF 10",INK)
    comps=[("ICE","5"),("TC","10"),("EXH","10"),("ES","10"),("CE","10"),("MGU-K","10"),("ANC","10")]
    for k,(n,v) in enumerate(comps):
        x=6+(k%4)*48; y=16+(k//4)*30
        r(d,x,y,x+44,y+24,BOXC); tx(d,x+4,y+5,n,INK); tx(d,x+4,y+15,"+"+v,RED)
    x=6+3*48; y=46; r(d,x,y,x+44,y+24,SL); tx(d,x+4,y+5,"TOTAL",INK); tx(d,x+4,y+15,"75",RED)
    tx(d,6,82,"FRESH PU AFTER FP3 SMOKE",MUT); tx(d,6,92,"SAME RESULT: BACK OF GRID",INK); calm(d); return im
def s_stats():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"SUNDAY IN SIX NUMBERS",INK)
    tiles=[("P3","LAWSON'S GRID SLOT"),("5","CARS WITH PENALTIES"),("P7","RUSSELL FROM P2"),("P14","LECLERC FROM P4"),("71","LAPS"),("+3","MERC VS FER FOR TITLE"),]
    for k,(big,sm) in enumerate(tiles):
        x=6+(k%2)*96; y=14+(k//2)*28
        r(d,x,y,x+90,y+24,BOXC); tx(d,x+4,y+5,big,GREEN); tx(d,x+4,y+15,sm,MUT)
    calm(d); return im
def s_weekend():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"WHO TOPPED EACH SESSION",INK)
    ss=[("FP1","NOR"),("FP2","ANT"),("FP3","VER"),("QUALI","NOR"),("RACE","?")]
    for k,(s,w) in enumerate(ss):
        x=6+k*38; r(d,x,24,x+34,70,BOXC)
        if w!="?": r(d,x,24,x+34,26,hx(TC[w]))
        tx(d,x+17-len(s)*2,32,s,MUT); tx(d,x+11,48,w,GREEN if w=="?" else INK)
    d.line([(6,78),(194,78)],fill=SL)
    tx(d,6,86,"NOR 2, ANT 1, VER 1",INK); calm(d); return im
def s_back():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"THE BACK ROW CLUB",INK)
    for k,(c,p,pen) in enumerate((("HAM","P20","75"),("VER","P21","30"),("PER","P22","30"))):
        x=8+k*64; r(d,x,16,x+56,76,BOXC); r(d,x,16,x+56,18,hx(TC[c]))
        tx(d,x+22,26,c,INK); tx(d,x+22,38,p,GREEN); tx(d,x+6,52,"PENALTY",MUT); tx(d,x+6,62,pen+" PLACES",RED)
    tx(d,6,88,"3 CHAMPIONS? NO: 2 + PEREZ",MUT) if False else tx(d,6,88,"ALL THREE START FROM THE BACK",INK)
    calm(d); return im
def s_front():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FRONT ROW: NOR VS ANT, BY SESSION",INK)
    ss=[("FP1",1,2),("FP2",2,1),("FP3",3,2),("QUALI",1,3),("GRID",1,2)]
    def Y(p): return 24+(p-1)*16
    for k,(s_,n,a) in enumerate(ss):
        x=30+k*38
        tx(d,x-len(s_)*2,90,s_,MUT)
        for c,p in (("NOR",n),("ANT",a)):
            r(d,x-3,Y(p)-3,x+3,Y(p)+3,hx(TC[c]))
        if k:
            px=30+(k-1)*38
            d.line([(px,Y(ss[k-1][1])),(x,Y(n))],fill=hx(TC["NOR"])); d.line([(px,Y(ss[k-1][2])),(x,Y(a))],fill=hx(TC["ANT"]))
    for p in (1,2,3): tx(d,4,Y(p)-2,f"P{p}",MUT)
    tx(d,6,100,"ORANGE NOR, TEAL ANT",MUT); calm(d); return im
def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")
slide(1,"NORRIS ON POLE, LAWSON P3 AFTER 5 GRID PENALTIES",s_grid,"Sao Paulo GP starting grid.","Russell, Leclerc, Hamilton, Verstappen, Perez dropped.","SWIPE >>>","1_1")
slide(2,"RUSSELL P7, LECLERC P14: ENGINES COST PLACES",s_board,"Grid penalties at Interlagos.","Hamilton, Verstappen, Perez start from the back.","SWIPE >>>","1_2")
slide(3,"LIGHTS OUT AT 14:00 LOCAL, 17:00 UTC",s_times,"Race start in six time zones.","71 laps of Interlagos.","FOLLOW","1_3")
slide(1,"PENALTIES LIFT LAWSON FROM P5 TO P3 ON THE GRID",s_slope,"Qualifying top 10 vs starting grid.","Russell and Leclerc drop, six drivers move up.","SWIPE >>>","2_1")
slide(2,"HAMILTON: 65 EXTRA PLACES FOR A FRESH PU",s_tiles65,"Stewards' component tally.","On top of his earlier 10-place drop.","SWIPE >>>","2_2")
slide(3,"P3, 5, 71: SUNDAY IN SAO PAULO",s_stats,"Six numbers for race day.","Mercedes can seal the constructors' title.","FOLLOW","2_3")
slide(1,"NORRIS TOPPED 2 OF 4 SESSIONS IN SAO PAULO",s_weekend,"Session toppers this weekend.","Pole sitter Norris starts ahead of Antonelli.","SWIPE >>>","3_1")
slide(2,"HAMILTON, VERSTAPPEN, PEREZ START P20-P22",s_back,"Back of the grid after penalties.","Verstappen and Perez: 30 places each.","SWIPE >>>","3_2")
slide(3,"NORRIS AND ANTONELLI SHARE THE FRONT ROW",s_front,"Their positions in every session.","Race: 14:00 local, 17:00 UTC, 12:00 New York.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
