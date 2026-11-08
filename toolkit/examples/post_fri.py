import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
from post_usgp import hx, r, GREEN
from post_cota import tx, FONT3
for k,v in {":":"000010000010000",">":"100010001010100","?":"111001011000010","=":"000111000111000","Z":"111001010100111","Q":"010101101110011","'":"010010000000000"}.items(): FONT3[k]=v
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_fri"); os.makedirs(OUT, exist_ok=True)
DATE = "07.11.26"
INK = hx("#e5e7eb"); MUT = hx("#64748b"); BG = hx("#0e131b"); SL = hx("#334155"); BOXC = hx("#1f2937"); RED = hx("#e05050")
HUD = "23.70S 46.70W"
TC = {"VER":"#3671c6","HAD":"#3671c6","HAM":"#dc0000","LEC":"#dc0000","ANT":"#27f4d2","RUS":"#27f4d2","NOR":"#ff8000","PIA":"#ff8000",
      "BOR":"#c0c0c0","HUL":"#c0c0c0","BEA":"#b6babd","CAM":"#b6babd","COL":"#ff87bc","GAS":"#ff87bc","MIN":"#ff87bc","LAW":"#6692ff","LIN":"#6692ff",
      "ALO":"#229971","STR":"#229971","SAI":"#1868db","ALB":"#1868db","PER":"#b0b0b0","BOT":"#b0b0b0"}
def ms(t): m,s=t.split(":"); return int(m)*60+float(s)
FP1=[("NOR",0),("ANT",.082),("VER",.236),("HAM",.324),("RUS",.386),("HAD",.439),("MIN",.852),("BOR",.897),("COL",.937),("LAW",.998)]
FP2=[("ANT",0),("NOR",.253),("VER",.259),("RUS",.273),("PIA",.321),("HAM",.450),("LEC",.720),("BOR",1.017),("HAD",1.076),("BEA",1.228)]
FP2T={"ANT":"1:10.763","NOR":"1:11.016","VER":"1:11.022","RUS":"1:11.036","PIA":"1:11.084","HAM":"1:11.213","LEC":"1:11.483","BOR":"1:11.780",
      "HAD":"1:11.839","BEA":"1:11.991","COL":"1:11.996","LIN":"1:12.008","LAW":"1:12.042","GAS":"1:12.109","ALO":"1:12.538","CAM":"1:12.561",
      "SAI":"1:12.742","STR":"1:12.942","ALB":"1:12.953","PER":"1:13.316","BOT":"1:13.383"}
def calm(d): r(d, 130, 104, 199, 119, BG)

def tower(title, rows, foot, rook=()):
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,title,INK)
    for i,(c,g) in enumerate(rows):
        y=14+i*8; hl=i==0
        tx(d,6,y,f"{i+1}",MUT); r(d,16,y-1,17,y+5,hx(TC[c])); tx(d,20,y,c,GREEN if hl else INK)
        if c in rook: r(d,34,y-1,38,y+5,GREEN); tx(d,35,y,"R",BG)
        w=int(g/1.25*100); r(d,42,y,42+max(w,1),y+4,GREEN if hl else SL)
        tx(d,148,y,"P1" if g==0 else f"+{g:.3f}",GREEN if hl else MUT)
    tx(d,6,96,foot,MUT); calm(d); return im

def s_fp2(): return tower("FP2 TOP 10, GAP TO P1",FP2,"BAR = GAP, 1.25S FULL SCALE")
def s_fp1(): return tower("FP1 TOP 10, GAP TO P1",FP1,"R = FP1 STAND-IN",rook=("MIN",))

def s_standins():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FP1 FINISHING SLOTS, P1-P22",INK)
    x0=10; dx=8.4
    for p in range(1,23):
        x=int(x0+(p-1)*dx); r(d,x,30,x+5,35,SL)
        if p in (1,10,22): tx(d,x-1 if p<10 else x-3,40,str(p),MUT)
    pins=[(7,"MINI",-1),(11,"FORNAROLI",1),(18,"CAMARA",-1),(20,"HERTA",1),(21,"BEGANOVIC",-1),(22,"SLATER",1)]
    for p,nm,side in pins:
        x=int(x0+(p-1)*dx); col=GREEN if p!=18 else INK
        r(d,x,30,x+5,35,col)
        if side<0:
            d.line([(x+2,29),(x+2,22)],fill=col); tx(d,max(2,min(x+2-len(nm)*2,196-len(nm)*4)),15,nm,col)
        else:
            d.line([(x+2,36),(x+2,50+((p%3)*8))],fill=col); tx(d,max(2,min(x+2-len(nm)*2,196-len(nm)*4)),53+((p%3)*8),nm,col)
    r(d,6,86,10,90,GREEN); tx(d,14,86,"FP1 STAND-IN",MUT); r(d,72,86,76,90,INK); tx(d,80,86,"DEBUT RACE DRIVER",MUT)
    tx(d,6,96,"MINI: P7 IN GASLY'S ALPINE",INK); calm(d); return im

def s_ruler():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FP2 GAP RULER, 0 TO 0.5S",INK)
    x0,x1=12,188
    def X(g): return int(x0+g/0.5*(x1-x0))
    r(d,x0,54,x1,55,SL)
    for g in (0,.1,.2,.3,.4,.5):
        r(d,X(g),51,X(g),58,MUT); tx(d,X(g)-6 if g else X(g)-2,62,"0" if g==0 else f".{int(g*10)}",MUT)
    r(d,X(0),46,X(.321),48,GREEN); tx(d,X(0),38,"TOP 5: 0.321S",GREEN)
    marks=[("ANT",0,1),("NOR",.253,0),("VER",.259,1),("RUS",.273,2),("PIA",.321,0),("HAM",.450,1)]
    for c,g,lv in marks:
        x=X(g); r(d,x-1,56,x+1,58,hx(TC[c]))
        y=72+lv*8; d.line([(x,59),(x,y-1)],fill=hx(TC[c])); tx(d,min(x-6,184),y,c,INK if c!="HAM" else MUT)
    tx(d,6,98,"NOR-VER: 0.006S",INK); calm(d); return im

def s_slope():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FP1 > FP2, TOP 10 ONLY",INK)
    tx(d,26,13,"FP1",MUT); tx(d,150,13,"FP2",MUT)
    f1=[c for c,_ in FP1]; f2=[c for c,_ in FP2]
    def Y(p): return 21+(p-1)*7.6
    for i,c in enumerate(f1):
        y=Y(i+1); lab=f"P{i+1} {c}"; tx(d,44-len(lab)*4,int(y),lab,INK if c in f2 else MUT)
        if c in f2:
            j=f2.index(c); d.line([(46,int(y)+2),(146,int(Y(j+1))+2)],fill=hx(TC[c]))
    for j,c in enumerate(f2):
        tx(d,150,int(Y(j+1)),f"P{j+1} {c}",INK if c in f1 else MUT)
    calm(d); return im

def s_board():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FRIDAY NOTES FOR THE WEEKEND",INK)
    rows=[("RUS","-5","GRID","FRESH ENGINE"),("HUL","0","LAPS","NO RUNNING IN FP2"),("CAM","P16","FP2","IMPEDED LECLERC EARLY ON")]
    for k,(c,a,b,why) in enumerate(rows):
        y=18+k*24
        r(d,6,y,194,y+20,BOXC); r(d,6,y,8,y+20,hx(TC[c]))
        tx(d,12,y+8,c,INK)
        col=RED if k<2 else INK
        d.rectangle([30,y+3,54,y+17],outline=col); tx(d,42-len(a)*2,y+5,a,col); tx(d,42-len(b)*2,y+11,b,col)
        tx(d,60,y+8,why,MUT)
    tx(d,6,96,"RUSSELL WAS P4 IN FP2",INK); calm(d); return im

def s_mates():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FP2 TEAM-MATE GAPS",INK)
    pairs=[("VER","HAD"),("BEA","CAM"),("ALO","STR"),("ANT","RUS"),("HAM","LEC"),("SAI","ALB"),("COL","GAS"),("NOR","PIA"),("PER","BOT"),("LIN","LAW")]
    for i,(a,b) in enumerate(pairs):
        g=ms(FP2T[b])-ms(FP2T[a]); y=14+i*8; hl=i==0
        r(d,6,y-1,7,y+5,hx(TC[a])); tx(d,10,y,f"{a}>{b}",INK)
        w=int(g/0.85*100); r(d,58,y,58+max(w,1),y+4,GREEN if hl else SL)
        tx(d,162,y,f"{g:.3f}",GREEN if hl else MUT)
    tx(d,6,98,"AUDI: HULKENBERG NO TIME",MUT); calm(d); return im

def s_delta():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"BEST LAP, FP1 VS FP2",INK)
    base=ms("1:11.717")
    rows=[("NOR",base,ms(FP2T["NOR"])),("ANT",base+.082,ms(FP2T["ANT"])),("VER",base+.236,ms(FP2T["VER"])),
          ("HAM",base+.324,ms(FP2T["HAM"])),("RUS",base+.386,ms(FP2T["RUS"]))]
    lo,hi=70.6,72.2
    def X(t): return int(40+(t-lo)/(hi-lo)*110)
    for i,(c,a,b) in enumerate(rows):
        y=18+i*13
        r(d,6,y,7,y+8,hx(TC[c])); tx(d,10,y+2,c,INK)
        r(d,40,y,X(a),y+3,SL); r(d,40,y+5,X(b),y+8,GREEN)
        tx(d,156,y+2,f"-{a-b:.3f}",INK)
    r(d,6,86,10,89,SL); tx(d,14,86,"FP1",MUT); r(d,34,86,38,89,GREEN); tx(d,42,86,"FP2",MUT); tx(d,70,86,"SHORTER = FASTER",MUT)
    tx(d,6,96,"BEST: 1:11.717 > 1:10.763",INK); calm(d); return im

def s_vs():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"NORRIS VS ANTONELLI, FRIDAY",INK)
    for k,(ses,win,gap,col) in enumerate((("FP1","NOR","0.082S",hx(TC["NOR"])),("FP2","ANT","0.253S",hx(TC["ANT"])))):
        x=10+k*96
        r(d,x,16,x+84,80,BOXC); r(d,x,16,x+84,18,col)
        tx(d,x+34,24,ses,MUT)
        tx(d,x+28,38,win,GREEN); tx(d,x+24,48,"AHEAD BY",MUT); tx(d,x+30,58,gap,INK)
        tx(d,x+10,70,"P1 "+win+"  P2 "+("ANT" if win=="NOR" else "NOR"),MUT)
    tx(d,6,90,"SAME TWO DRIVERS, SWAPPED",INK)
    calm(d); return im

def s_tiles():
    im = Image.new("RGB",(200,120),BG); d=ImageDraw.Draw(im)
    tx(d,6,4,"FRIDAY AT INTERLAGOS IN NUMBERS",INK)
    tiles=[("1:10.763","FP2 BEST, ANT"),("0.954S","FP1 TO FP2"),("0.006S","NOR TO VER, FP2"),("P16","CAMARA IN FP2"),("-5","RUS GRID DROP"),("0","HUL LAPS IN FP2")]
    for k,(big,sm) in enumerate(tiles):
        x=6+(k%2)*96; y=14+(k//2)*28
        r(d,x,y,x+90,y+24,BOXC)
        tx(d,x+4,y+5,big,RED if big in ("-5","0") else GREEN); tx(d,x+4,y+15,sm,MUT)
    calm(d); return im

def slide(k, head, scene, figt, bod, foot, name):
    im, d = page(k, 3, DATE)
    y = headline(im, head)
    y = cover_image(im, d, scene(), y + 75, HUD)
    fig(im, y + 60, figt, k)
    body(im, y + 95, bod)
    footer(im, d, k, foot); im.save(f"{OUT}/{name}.png")

slide(1,"ANTONELLI TOPS FP2 IN SAO PAULO BY 0.253S",s_fp2,"FP2 top 10, gap to Antonelli.","1:10.763 in misty, overcast conditions.","SWIPE >>>","1_1")
slide(2,"NORRIS LED FP1 BY 0.082S, MINI P7",s_fp1,"FP1 top 10, gap to Norris.","Mini drove Gasly's Alpine in FP1.","SWIPE >>>","1_2")
slide(3,"TOP 5 IN FP2 WITHIN 0.321 SECONDS",s_ruler,"Gap to P1, top 6 in FP2.","Norris and Verstappen: 0.006s apart.","FOLLOW","1_3")
slide(1,"FP1 TO FP2: ANTONELLI UP FROM P2 TO P1",s_slope,"Top 10 in FP1 vs top 10 in FP2.","Grey: only in one of the two top 10s.","SWIPE >>>","2_1")
slide(2,"RUSSELL P4 IN FP2, BUT 5 PLACES DOWN ON THE GRID",s_board,"Friday notes that shape Saturday.","Fresh engine: the drop applies to Sunday's grid.","SWIPE >>>","2_2")
slide(3,"VERSTAPPEN 0.817S CLEAR OF HADJAR IN FP2",s_mates,"Team-mate gaps, FP2 best laps.","Lindblad edged Lawson by 0.034s.","FOLLOW","2_3")
slide(1,"FP2 BEST LAP 0.954S FASTER THAN FP1",s_delta,"FP1 vs FP2 best laps, top 5 of FP1.","Russell found the most: 1.067s.","SWIPE >>>","3_1")
slide(2,"NORRIS VS ANTONELLI: 0.082S, THEN 0.253S",s_vs,"Who led whom in each session.","Verstappen P3 in both sessions.","SWIPE >>>","3_2")
slide(3,"1:10.763, -5, 0 LAPS: FRIDAY AT INTERLAGOS",s_tiles,"Six numbers from Friday.","FP3 and qualifying follow on Saturday.","FOLLOW","3_3")
names=[f"{v}_{i}" for v in "123" for i in "123"]
sh=Image.new("RGB",(3*550+10,3*685+10),(60,60,60))
for k,n in enumerate(names): sh.paste(Image.open(f"{OUT}/{n}.png").resize((540,675)),(10+(k%3)*550,10+(k//3)*685))
sh.save(f"{OUT}/sheet.png"); print("ok")
