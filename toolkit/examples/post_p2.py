import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_p2"').replace('DATE = "07.11.26"','DATE = "10.11.26"'))
FONT3["/"]="001001010100100"
HUD="36.11N 115.17W"; YEL=hx("#facc15")
NOW=[("VER",279),("RUS",262),("HAM",261),("LEC",249),("NOR",246)]
BRZ={"VER":18,"RUS":12,"HAM":2,"LEC":4,"NOR":25}
BEF=[(c,p-BRZ[c]) for c,p in NOW]
LEFT=75
def s_bars():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FIGHT FOR P2, POINTS + MAX STILL OPEN",INK)
    S=150/380
    for i,(c,p) in enumerate(NOW):
        y=16+i*15
        tx(d,6,y+3,c,INK); r(d,24,y,24+int(p*S),y+9,hx(TC[c]))
        d.rectangle([24+int(p*S),y,24+int((p+LEFT)*S),y+9],outline=SL)
        tx(d,28,y+3,str(p),BG)
    tx(d,6,94,"OUTLINE = +75, 3 RACES LEFT",MUT); calm(d); return im
def s_ladder():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"GAP TO VERSTAPPEN IN P2",INK)
    for i,(c,p) in enumerate(NOW):
        g=279-p; y=16+i*15
        r(d,6,y,194,y+11,BOXC); r(d,6,y,8,y+11,hx(TC[c])); tx(d,12,y+4,f"P{i+2} {c}",INK)
        if g: r(d,60,y+3,60+g*3,y+8,RED); tx(d,64+g*3,y+4,f"-{g}",RED)
        else: tx(d,60,y+4,"279 PTS",GREEN)
    tx(d,6,96,"PIASTRI 127 BACK: OUT OF REACH",MUT); calm(d); return im
def s_cut():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"WHO CAN STILL FINISH P2?",INK)
    rows=NOW+[("PIA",152)]
    for i,(c,p) in enumerate(rows):
        g=279-p; y=14+i*12; ok=g<=LEFT
        tx(d,6,y,c,INK); tx(d,30,y,str(p),MUT)
        r(d,60,y,60+min(g,130),y+5,SL if ok else RED)
        tx(d,166,y,"IN" if ok else "OUT",GREEN if ok else RED)
    x=60+LEFT; d.line([(x,12),(x,86)],fill=INK); tx(d,x-10,90,"75 PTS",INK)
    tx(d,6,100,"BAR = GAP TO VER",MUT); calm(d); return im
def s_slope():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"P2-P6 BEFORE > AFTER SAO PAULO",INK)
    tx(d,22,13,"BEFORE",MUT); tx(d,150,13,"AFTER",MUT)
    b=sorted(BEF,key=lambda t:-t[1]); a=NOW
    def Y(k): return 24+k*14
    for k,(c,p) in enumerate(b):
        lab=f"{c} {p}"; tx(d,44-len(lab)*4,Y(k),lab,INK)
        j=[x[0] for x in a].index(c); d.line([(46,Y(k)+2),(146,Y(j)+2)],fill=hx(TC[c]))
    for j,(c,p) in enumerate(a): tx(d,150,Y(j),f"{c} {p}",INK)
    calm(d); return im
def s_haul():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"POINTS SCORED IN SAO PAULO",INK)
    for i,(c,_) in enumerate(sorted(NOW,key=lambda t:-BRZ[t[0]])):
        p=BRZ[c]; y=16+i*15
        tx(d,6,y+3,c,INK); r(d,24,y,24+p*5,y+9,hx(TC[c])); tx(d,28+p*5,y+3,str(p),INK)
    tx(d,6,94,"NOR WIN 25, VER P2 18, RUS P4 12",MUT); calm(d); return im
def s_cal():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"REMAINING CALENDAR",INK)
    rows=[("LAS VEGAS","22 NOV","SET",GREEN),("QATAR","29 NOV","CONFIRMED",GREEN),("ABU DHABI","6 DEC","CONFIRMED",GREEN)]
    for k,(n,dt,st,col) in enumerate(rows):
        y=18+k*20; r(d,6,y,194,y+15,BOXC); tx(d,12,y+5,n,INK); tx(d,70,y+5,dt,INK); tx(d,110,y+5,st,col)
    tx(d,6,84,"IMOLA BACKUP SHELVED",MUT); tx(d,6,94,"75 POINTS LEFT PER DRIVER",GREEN); calm(d); return im
def s_big():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"P2 TO P6 IN THE DRIVERS' STANDINGS",INK)
    # big pixel 33
    big={"3":["111","001","111","001","111"]}
    for n,ch in enumerate("33"):
        for yy,row in enumerate(big[ch]):
            for xx,v in enumerate(row):
                if v=="1": r(d,10+n*34+xx*9,18+yy*9,18+n*34+xx*9,26+yy*9,GREEN)
    tx(d,84,26,"POINTS COVER",INK); tx(d,84,36,"FIVE DRIVERS",INK); tx(d,84,50,"VER 279",MUT); tx(d,84,60,"NOR 246",MUT)
    for k in range(34): r(d,10+k*5,74,12+k*5,80,GREEN if k<33 else SL)
    tx(d,6,88,"ONE TICK PER POINT",MUT); calm(d); return im
def s_teams():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"P2 CONTENDERS BY TEAM",INK)
    groups=[("RED BULL",[("VER",279)]),("MERCEDES",[("RUS",262)]),("FERRARI",[("HAM",261),("LEC",249)]),("MCLAREN",[("NOR",246)])]
    x=6
    for n,ds in groups:
        w=44; r(d,x,16,x+w,84,BOXC); r(d,x,16,x+w,18,hx(TC[ds[0][0]]))
        tx(d,x+3,24,n,MUT)
        for k,(c,p) in enumerate(ds): tx(d,x+3,40+k*18,c,INK); tx(d,x+3,48+k*18,str(p),GREEN)
        x+=w+4
    calm(d); return im
def s_tiles():
    im=Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"THE P2 FIGHT IN SIX NUMBERS",INK)
    tiles=[("33","PTS COVER P2-P6"),("1","PT RUS OVER HAM"),("17","VER OVER RUS"),("25","NORRIS GAINED SUNDAY"),("3","RACES LEFT"),("390","ANTONELLI, CHAMPION")]
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
slide(1,"5 DRIVERS WITHIN 33 POINTS IN THE FIGHT FOR P2",s_bars,"Drivers' points after Sao Paulo.","Antonelli is champion; P2 is wide open.","SWIPE >>>","1_1")
slide(2,"RUSSELL 17 BEHIND VERSTAPPEN, HAMILTON 18",s_ladder,"Gap to Verstappen in second.","Leclerc and Norris within 33.","SWIPE >>>","1_2")
slide(3,"75 POINTS LEFT: PIASTRI IS OUT OF THE P2 RACE",s_cut,"Who can still mathematically reach P2.","Qatar and Abu Dhabi are confirmed.","FOLLOW","1_3")
slide(1,"SAO PAULO SHAKES UP THE FIGHT FOR P2",s_slope,"P2-P6 before and after Sao Paulo.","Russell jumps Hamilton by one point.","SWIPE >>>","2_1")
slide(2,"NORRIS 25, VERSTAPPEN 18, HAMILTON 2 IN BRAZIL",s_haul,"Points scored at Interlagos.","Hamilton started from the back.","SWIPE >>>","2_2")
slide(3,"QATAR AND ABU DHABI ON: 75 POINTS LEFT",s_cal,"What is left of the 2026 calendar.","FIA president: ready for both races.","FOLLOW","2_3")
slide(1,"33 POINTS COVER P2 TO P6 WITH 3 RACES TO GO",s_big,"The spread behind champion Antonelli.","Verstappen 279, Norris 246.","SWIPE >>>","3_1")
slide(2,"4 TEAMS, 5 DRIVERS FIGHT FOR P2",s_teams,"P2 contenders by team.","Ferrari has two cars in it.","SWIPE >>>","3_2")
slide(3,"17, 1, 33: THE P2 FIGHT IN NUMBERS",s_tiles,"Six numbers from the standings.","Next stop: Las Vegas, 22 November.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
