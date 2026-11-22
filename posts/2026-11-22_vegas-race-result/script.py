import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_rres"').replace('DATE = "07.11.26"','DATE = "22.11.26"').replace('HUD = "23.70S 46.70W"','HUD = "36.11N 115.17W"'))
# Las Vegas GP 2026 race result (Marius 22.11.: race topics into the result carousel).
# Sources (2 each, 2026 checked):
#  Result/gaps: FIA Doc 65 Final Race Classification + The Race/Motorsport.com result tables
#  Grid: FIA Doc 53 + The Race/Motorsport starting grid
#  Penalties: LEC 10 s (FIA Doc 60, stays P10 per Doc 65); HAD 10 s (Doc 64)
#  Ferrari "unacceptable": The Race + RACER + Motorsport.com 22.11.
#  Verstappen "so far below my level": Motorsport.com + The Race 22.11.; Russell late crash, P9: Motorsport + The Race
#  Standings after Vegas: FIA Doc 66 + Jolpica (VER 304, HAM 267, RUS 264, NOR 264, LEC 250); 2 races left (Jolpica calendar)
TOP = [("VER",0.0),("NOR",0.639),("PIA",1.529),("ANT",2.574),("GAS",2.927)]
MOV = [("PIA",17,3),("SAI",20,8),("HAM",11,7),("GAS",8,5),("RUS",2,9)]

def s_podium():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"PODIUM, LAS VEGAS GP",INK)
    for c,x,h,p,g in (("NOR",22,34,"2","+0.639"),("VER",78,46,"1","WINNER"),("PIA",134,26,"3","+1.529")):
        col=hx(TC[c]); y=96-h
        r(d,x,y,x+44,96,BOXC); r(d,x,y,x+44,y+2,col)
        tx(d,x+20,y+6,p,GREEN if p=="1" else INK); tx(d,x+16,y-10,c,INK); tx(d,x+22-len(g)*2,y+16,g,MUT)
    d.line([(6,96),(194,96)],fill=SL)
    tx(d,6,104,"PIASTRI STARTED P17",MUT); calm(d); return im

def s_gaps():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"TOP 5 WITHIN 2.927 SECONDS",INK)
    for k,(c,g) in enumerate(TOP):
        y=18+k*15; w=int(g/3.0*120)
        tx(d,6,y+3,f"P{k+1}",MUT); tx(d,22,y+3,c,INK)
        r(d,42,y+1,42+max(w,2),y+9,hx(TC[c])); tx(d,46+w,y+3,"LEADER" if g==0 else f"+{g:.3f}",INK)
    tx(d,6,96,"AFTER 50 LAPS AND 1:27:39",MUT); tx(d,6,104,"BAR = GAP TO VERSTAPPEN",MUT); calm(d); return im

def s_movers():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"GRID SLOT VS FINISH",INK)
    for k,(c,g,f) in enumerate(MOV):
        y=16+k*16; up=g>f
        r(d,6,y,194,y+13,BOXC); r(d,6,y,8,y+13,hx(TC[c]))
        tx(d,12,y+4,c,INK); tx(d,40,y+4,f"P{g}",MUT); tx(d,62,y+4,">",MUT); tx(d,72,y+4,f"P{f}",INK)
        dlt=g-f; tx(d,100,y+4,(f"+{dlt}" if up else str(dlt))+" PLACES",GREEN if up else RED)
    tx(d,6,100,"PIASTRI AND SAINZ HAD GRID PENALTIES",MUT); calm(d); return im

def s_ferrari():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FERRARI VS FERRARI",INK)
    for k,(c,nm,pos,note) in enumerate((("HAM","HAMILTON","P7","HIT BY TEAM-MATE"),("LEC","LECLERC","P10","10 S PENALTY"))):
        x=8+k*96; col=hx(TC[c])
        r(d,x,16,x+88,56,BOXC); r(d,x,16,x+88,18,col)
        tx(d,x+6,24,nm,INK); tx(d,x+6,36,"FINISH",MUT); tx(d,x+40,36,pos,INK); tx(d,x+6,46,note,RED if c=="LEC" else MUT)
    r(d,6,64,194,84,BOXC); r(d,6,64,8,84,hx(TC["LEC"]))
    tx(d,12,68,"FERRARI: COMPLETELY",INK); tx(d,12,76,"UNACCEPTABLE",INK)
    tx(d,6,94,"PENALTY FOR CAUSING A COLLISION",MUT); tx(d,6,102,"LECLERC STILL KEPT P10",MUT); calm(d); return im

def s_feud():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FROM THE FRONT ROW TO THE FINISH",INK)
    for k,(c,nm,g,f,note) in enumerate((("VER","VERSTAPPEN","P1","P1","WINS"),("RUS","RUSSELL","P2","P9","LATE CRASH"))):
        x=8+k*96; col=hx(TC[c])
        r(d,x,16,x+88,56,BOXC); r(d,x,16,x+88,18,col)
        tx(d,x+6,24,nm,INK); tx(d,x+6,36,"GRID",MUT); tx(d,x+30,36,g,INK); tx(d,x+48,36,"FIN",MUT); tx(d,x+66,36,f,GREEN if f=="P1" else RED)
        tx(d,x+6,46,note,GREEN if c=="VER" else MUT)
    r(d,6,64,194,84,BOXC); r(d,6,64,8,84,hx(TC["VER"]))
    tx(d,12,68,"VERSTAPPEN ON RUSSELL:",INK); tx(d,12,76,"SO FAR BELOW MY LEVEL",INK)
    tx(d,6,96,"RUSSELL HIT THE WALL CHASING P2",MUT); calm(d); return im

def s_p2():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FIGHT FOR P2, AFTER VEGAS",INK)
    rows=[("VER",304),("HAM",267),("RUS",264),("NOR",264),("LEC",250)]
    for k,(c,p) in enumerate(rows):
        y=16+k*15; w=int((p-200)/110*120)
        tx(d,6,y+4,f"P{k+2}",MUT); tx(d,22,y+4,c,INK)
        r(d,42,y+2,42+w,y+10,hx(TC[c])); tx(d,46+w,y+4,str(p),INK)
    tx(d,6,94,"VERSTAPPEN 37 CLEAR IN P2",INK); tx(d,6,102,"2 RACES LEFT: QATAR, ABU DHABI",MUT)
    calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

# V1: podium -> movers -> P2 fight
slide(1,"VERSTAPPEN WINS IN VEGAS, NORRIS 0.639S BEHIND",s_podium,"Las Vegas GP podium.","Piastri completes the podium from 17th on the grid.","SWIPE >>>","1_1")
slide(2,"PIASTRI GAINS 14 PLACES, SAINZ 12",s_movers,"Grid slot vs finishing position.","Russell drops from the front row to ninth.","SWIPE >>>","1_2")
slide(3,"VERSTAPPEN NOW 37 POINTS CLEAR IN P2",s_p2,"Drivers' standings after Las Vegas.","Hamilton, Russell and Norris are split by three points.","FOLLOW","1_3")
# V2: Ferrari -> feud -> gaps
slide(1,"FERRARI COLLIDE: LECLERC PENALISED, HAMILTON P7",s_ferrari,"The Ferrari clash in Las Vegas.","Ferrari called it completely unacceptable.","SWIPE >>>","2_1")
slide(2,"VERSTAPPEN WINS, RUSSELL HITS THE WALL IN P2",s_feud,"The front row, start to finish.","Verstappen: Russell is so far below my level.","SWIPE >>>","2_2")
slide(3,"TOP FIVE COVERED BY 2.927 SECONDS",s_gaps,"Gaps at the flag in Las Vegas.","Verstappen, Norris, Piastri, Antonelli, Gasly.","FOLLOW","2_3")
# V3: movers -> P2 -> Ferrari
slide(1,"PIASTRI FROM P17 TO THE VEGAS PODIUM",s_movers,"Grid slot vs finishing position.","Sainz climbs from 20th to eighth.","SWIPE >>>","3_1")
slide(2,"VERSTAPPEN'S FOURTH WIN BUILDS A 37-POINT GAP",s_p2,"Drivers' standings after Las Vegas.","Two races left: Qatar and Abu Dhabi.","SWIPE >>>","3_2")
slide(3,"LECLERC 10S PENALTY AFTER HITTING HAMILTON",s_ferrari,"The Ferrari clash in Las Vegas.","Leclerc still kept tenth place.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
