import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"post_fri.py")).read().split("def slide(")[0].replace('"out_fri"','"out_race"').replace('DATE = "07.11.26"','DATE = "08.11.26"'))
FONT3["/"]="001001010100100"
ROWS=[("NOR",0),("VER",14.602),("HAD",24.485),("RUS",33.991),("ANT",36.017),("PIA",56.475),("LAW",75.402),("LEC",78.586),("HAM",None),("HUL",None)]
GRIDP={"NOR":1,"ANT":2,"LAW":3,"HUL":4,"HAD":5,"BEA":6,"RUS":7,"ALO":8,"ALB":9,"PIA":10,"CAM":11,"LIN":12,"SAI":13,"LEC":14,"COL":15,"GAS":16,"STR":17,"BOT":18,"BOR":19,"HAM":20,"VER":21,"PER":22}
MER,FER=652,510; LEFT=129
def s_gaps():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"RACE TOP 10, GAP TO WINNER",INK)
    for i,(c,g) in enumerate(ROWS):
        y=14+i*8; hl=i==0
        tx(d,6,y,f"{i+1}",MUT); r(d,16,y-1,17,y+5,hx(TC[c])); tx(d,20,y,c,GREEN if hl else INK)
        if g is None: tx(d,42,y,"LAPPED",MUT); tx(d,148,y,"+1 LAP",MUT); continue
        w=int(g/80*100); r(d,42,y,42+max(w,1),y+4,GREEN if hl else SL)
        tx(d,148,y,"WIN" if g==0 else f"+{g:.1f}",GREEN if hl else MUT)
    tx(d,6,96,"BAR = GAP IN SEC, 80 FULL SCALE",MUT); calm(d); return im
def s_gain():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"PLACES GAINED VS GRID, TOP 10",INK)
    x0=100
    d.line([(x0,14),(x0,94)],fill=SL)
    for i,(c,_) in enumerate(ROWS):
        y=14+i*8; m=GRIDP[c]-(i+1)
        tx(d,6,y,f"P{i+1} {c}",INK)
        if m>0: r(d,x0+1,y,x0+1+m*4,y+4,GREEN); tx(d,x0+4+m*4,y,f"+{m}",GREEN)
        elif m<0: r(d,x0+m*4,y,x0-1,y+4,RED); tx(d,x0+m*4-14,y,f"{m}",RED)
        else: tx(d,x0+4,y,"0",MUT)
    tx(d,6,98,"GRID AFTER PENALTIES",MUT); calm(d); return im
def s_points():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"CONSTRUCTORS, AFTER SAO PAULO",INK)
    S=150/800
    for k,(n,p,col,mx) in enumerate((("MER",MER,"#27f4d2",0),("FER",FER,"#dc0000",LEFT))):
        y=24+k*26
        tx(d,6,y+4,n,INK); r(d,26,y,26+int(p*S),y+12,hx(col))
        if mx: d.rectangle([26+int(p*S),y,26+int((p+mx)*S),y+12],outline=INK)
        tx(d,26+int((p+mx)*S)+4,y+4,str(p) if not mx else f"{p} +{mx} MAX",INK)
    tx(d,6,82,f"GAP {MER-FER} > {LEFT} STILL OPEN",GREEN); tx(d,6,94,"3 RACES LEFT, 43 PTS EACH",MUT)
    calm(d); return im
def s_slope():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"GRID > FINISH, TOP 10 FINISHERS",INK)
    tx(d,22,12,"GRID",MUT); tx(d,150,12,"FINISH",MUT)
    def Y(p): return 21+(p-1)*7.6
    order=sorted(ROWS,key=lambda t:GRIDP[t[0]])
    for j,(c,_) in enumerate(order):
        lab=f"P{GRIDP[c]} {c}"; tx(d,44-len(lab)*4,int(Y(j+1))-2,lab,INK)
        f=[x[0] for x in ROWS].index(c)+1
        d.line([(46,int(Y(j+1))),(146,int(Y(f)))],fill=hx(TC[c]))
    for i,(c,_) in enumerate(ROWS): tx(d,150,int(Y(i+1))-2,f"P{i+1} {c}",INK)
    calm(d); return im
def s_math():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"WHY IT IS DECIDED",INK)
    boxes=[("BEFORE","126 PTS AHEAD"),("SUNDAY","MER 22 / FER 6"),("NOW",f"{MER-FER} PTS AHEAD"),("LEFT","3 X 43 = 129")]
    for k,(a,b) in enumerate(boxes):
        y=16+k*18; r(d,6,y,194,y+14,BOXC); tx(d,12,y+5,a,MUT); tx(d,60,y+5,b,INK)
    r(d,6,90,194,102,GREEN); tx(d,12,94,"MERCEDES: CONSTRUCTORS' CHAMPIONS",BG); calm(d); return im
def s_rb():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"RED BULL DOUBLE PODIUM",INK)
    for k,(c,g,f) in enumerate((("VER",21,2),("HAD",5,3))):
        x=10+k*96; r(d,x,16,x+84,80,BOXC); r(d,x,16,x+84,18,hx(TC[c]))
        tx(d,x+34,26,c,INK); tx(d,x+10,42,f"GRID  P{g}",MUT); tx(d,x+10,54,f"FINISH P{f}",GREEN); tx(d,x+10,66,f"+{g-f} PLACES",INK)
    tx(d,6,92,"NORRIS WON FROM POLE",MUT); calm(d); return im
def s_champs():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"CONSTRUCTORS' CHAMPIONS 2014-2026",INK)
    yrs=[(y,"MER") for y in range(2014,2022)]+[(2022,"RBR"),(2023,"RBR"),(2024,"MCL"),(2025,"MCL"),(2026,"MER")]
    cols={"MER":"#27f4d2","RBR":"#3671c6","MCL":"#ff8000"}
    for k,(y,t) in enumerate(yrs):
        x=6+k*14.6; x=int(x)
        r(d,x,30,x+12,60,hx(cols[t]))
        if y==2026: d.rectangle([x-1,29,x+13,61],outline=GREEN)
        tx(d,x,66,str(y)[2:],INK if y==2026 else MUT)
    r(d,6,80,10,84,hx(cols["MER"])); tx(d,14,80,"MER",MUT); r(d,36,80,40,84,hx(cols["RBR"])); tx(d,44,80,"RBR",MUT); r(d,66,80,70,84,hx(cols["MCL"])); tx(d,74,80,"MCL",MUT)
    tx(d,6,94,"FIRST TEAM TITLE SINCE 2021",GREEN); calm(d); return im
def s_ruler():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"GAP TO WINNER, 0-40 SEC",INK)
    x0,x1=12,188
    def X(g): return int(x0+g/40*(x1-x0))
    r(d,x0,54,x1,55,SL)
    for g in (0,10,20,30,40): r(d,X(g),51,X(g),58,MUT); tx(d,X(g)-4,62,str(g),MUT)
    for c,g,lv in (("NOR",0,0),("VER",14.602,1),("HAD",24.485,0),("RUS",33.991,1),("ANT",36.017,2)):
        x=X(g); r(d,x-1,56,x+1,58,hx(TC[c])); y=72+lv*8; d.line([(x,59),(x,y-1)],fill=hx(TC[c])); tx(d,min(x-6,182),y,c,INK)
    r(d,X(0),46,X(14.602),48,GREEN); tx(d,X(0),38,"NOR CLEAR BY 14.6 SEC",GREEN); calm(d); return im
def s_tiles():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"SAO PAULO IN SIX NUMBERS",INK)
    tiles=[("14.6","SEC: NORRIS' MARGIN"),("+19","VERSTAPPEN P21>P2"),(str(MER-FER),"MER LEAD OVER FER"),("+11","HAMILTON P20>P9"),("71","LAPS"),("2","RED BULLS ON PODIUM")]
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
slide(1,"NORRIS WINS IN SAO PAULO, VERSTAPPEN 21ST TO 2ND",s_gaps,"Race top 10, gap to the winner.","Norris led home a Red Bull double podium.","SWIPE >>>","1_1")
slide(2,"VERSTAPPEN +19, HAMILTON +11 FROM THE BACK",s_gain,"Places gained vs the starting grid.","Antonelli, Lawson and Hulkenberg lost ground.","SWIPE >>>","1_2")
slide(3,f"MERCEDES {MER-FER} POINTS CLEAR: TEAM TITLE SEALED",s_points,"Constructors' points after round 20.","Ferrari can't close the gap in 3 races.","FOLLOW","1_3")
slide(1,"FROM P21 TO P2: VERSTAPPEN'S CHARGE",s_slope,"Starting grid vs finish, top 10.","Norris converted pole into the win.","SWIPE >>>","2_1")
slide(2,f"MERCEDES WIN THE 2026 CONSTRUCTORS' TITLE",s_math,"The maths after Sao Paulo.","Ferrari scored 6 points to Mercedes' 22.","SWIPE >>>","2_2")
slide(3,"VERSTAPPEN AND HADJAR PUT 2 RED BULLS ON THE PODIUM",s_rb,"Red Bull's grid vs finish.","Verstappen gained 19 places.","FOLLOW","2_3")
slide(1,"MERCEDES' FIRST CONSTRUCTORS' TITLE SINCE 2021",s_champs,"Constructors' champions since 2014.","Sealed at Interlagos with 3 races to go.","SWIPE >>>","3_1")
slide(2,"NORRIS WINS BY 14.6S AT INTERLAGOS",s_ruler,"Gaps to the winner, top 5.","Verstappen second, Hadjar third.","SWIPE >>>","3_2")
slide(3,f"14.6S, +19, {MER-FER}: SAO PAULO IN NUMBERS",s_tiles,"Six numbers from the race.","Three races left in 2026.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("done")
