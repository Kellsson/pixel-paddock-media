import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from reel_v4 import make
rows=[("VER","Red Bull","1:11.622"),("ANT","Mercedes","+0.025"),("NOR","McLaren","+0.131"),("RUS","Mercedes","+0.184"),("LEC","Ferrari","+0.274"),
("PIA","McLaren","+0.313"),("LIN","Racing Bulls","+0.438"),("LAW","Racing Bulls","+0.549"),("HAD","Red Bull","+0.591"),("BOR","Audi","+1.022")]
make("FP3", rows, "fp3br_reel", gp="SAO PAULO", rookies=("LIN",), insight=["VERSTAPPEN P1","BUT HE STARTS","FROM THE BACK"])
