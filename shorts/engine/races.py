import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from map_recap import *
SOFT = (255, 150, 150)

def gears_inset(lost_times, stuck_at):
    def f(d, fr):
        lost = {g for g, t in lost_times if fr >= t}; stuck = fr >= stuck_at
        d.rectangle([14, 168, 120, 196], fill=(6, 8, 16), outline=EDGE); tx(d, 18, 171, "GEARS", MUT)
        for g in range(1, 7):
            x = 18 + (g - 1) * 17; y = 179
            col = RED if g in lost else (GRN if stuck and g == 6 else ((80, 90, 112) if stuck else INK))
            d.rectangle([x, y, x + 12, y + 13], outline=col); tx(d, x + 5, y + 4, str(g), col)
            if g in lost: d.line([(x + 1, y + 12), (x + 11, y + 1)], fill=RED)
    return f

R91 = dict(geo=f"{HERE}/geo/br.geojson", laps=71, start_frac=0.0,
    cars={"SEN": ("MCL91", (242, 201, 76)), "PAT": ("WIL91", None), "MAN": ("WIL91", None), "BER": ("MCL91", None)},
    names={"SEN": "SENNA", "PAT": "PATRESE", "MAN": "MANSELL", "BER": "BERGER"},
    grid={"SEN": 0, "PAT": 60, "MAN": 120, "BER": 180}, out={"MAN": 7},
    segments=[
        dict(frames=150, laps=(0, 0), cam=("over",), hide=("BER",), nohud=True,
             text=[("INTERLAGOS 1991", INK, 2), ("SENNA: SEVEN HOME RACES", INK, 1), ("AND NOT ONE WIN", YEL, 1)]),
        dict(frames=150, laps=(0, 0), cam=("frac", .985, 3.0), hide=("BER",), labels=("SEN", "PAT", "MAN"), nohud=True,
             text=[("THE GRID", INK, 2), ("P1 SENNA, MCLAREN", YEL, 1), ("P2 PATRESE, P3 MANSELL", INK, 1)]),
        dict(frames=120, laps=(0, .5), linear=False, cam=("car", "SEN", 2.4), tick=0, gaps={"PAT": 80, "MAN": 130, "BER": 300},
             text=[("LIGHTS OUT", GRN, 2), ("SENNA LEADS", INK, 1)]),
        dict(frames=150, laps=(.5, 30), cam=("over",), gaps={"MAN": 100, "PAT": 420, "BER": 650},
             text=[("MANSELL CHASES SENNA", INK, 1)]),
        dict(frames=150, laps=(30, 30.9), cam=("frac", .95, 2.6), tick=30 / 71, gaps={"MAN": 1150}, labels=("MAN",),
             text=[("MANSELL'S PIT STOP", YEL, 1), ("14 SECONDS", INK, 2), ("GEARBOX WON'T FIND FIRST", INK, 1)]),
        dict(frames=120, laps=(30.9, 59), cam=("over",), gaps={"MAN": 700, "PAT": 800},
             text=[("SENNA STILL LEADS", INK, 1)]),
        dict(frames=150, laps=(59, 59.8), cam=("car", "MAN", 2.6), stop={"MAN": .35}, labels=("MAN",), tick=59 / 71,
             text=[("MANSELL OUT", SOFT, 2), ("GEARBOX FAILURE", INK, 1)]),
        dict(frames=270, laps=(59.8, 65), cam=("car", "SEN", 2.6), tick=62 / 71, inset=gears_inset([(50, 0), (110, 0), (160, 0)][0:0] or [(4, 50), (5, 110), (3, 160)], 210),
             text=[("NOW SENNA'S", INK, 2), ("GEARBOX GOES", INK, 2), ("4TH, 5TH, 3RD. ONLY 6TH LEFT", YEL, 1)], tspeed=1.1),
        dict(frames=210, laps=(65, 70.6), cam=("over",), rain=1, gaps={"PAT": 320, "BER": 650},
             text=[("RAIN", INK, 2), ("PATRESE CLOSES IN", YEL, 1), ("SENNA HAS ONE GEAR", INK, 1)]),
        dict(frames=150, laps=(70.6, 71), linear=False, cam=("frac", .0, 2.8), rain=.5, gaps={"PAT": 170}, labels=("SEN", "PAT"), win=True, tick=1.0,
             text=[("SENNA WINS", GRN, 2), ("+2.991 S", INK, 2)]),
        dict(frames=180, laps=(71, 71), board=("FINAL CLASSIFICATION", [("1", "SENNA", "MCL91", "WINNER"), ("2", "PATRESE", "WIL91", "+2.991"), ("3", "BERGER", "MCL91", "+5.416")],
             ["FIRST HOME WIN", "AT THE 8TH ATTEMPT", "", "MANSELL: OUT, GEARBOX"])),
        dict(frames=150, laps=(71, 71), cam=("over",), hide=("SEN", "PAT", "MAN", "BER"), nohud=True, outro=True,
             text=[("35 YEARS LATER", YEL, 2), ("ANTONELLI RACES A SENNA", INK, 1), ("TRIBUTE HELMET HERE", INK, 1), ("THIS SUNDAY", GRN, 1)]),
    ])
R91["audio"] = make_audio("map91")

L05 = 5807
R05 = dict(geo=f"{HERE}/geo/jp.geojson", laps=53, start_frac=0.0, rot=-60,
    cars={"RSC": ("TOY05", None), "FIS": ("REN05", None), "MSC": ("FER05", None), "ALO": ("REN05", None), "RAI": ("MCL05", None), "MON": ("MCL05", None)},
    names={"RSC": "R. SCHUMACHER", "FIS": "FISICHELLA", "MSC": "M. SCHUMACHER", "ALO": "ALONSO", "RAI": "RAIKKONEN", "MON": "MONTOYA"},
    grid={"RSC": 0, "FIS": 120, "MSC": 780, "ALO": 900, "RAI": 960, "MON": 1020}, out={"MON": 3},
    segments=[
        dict(frames=150, laps=(0, 0), cam=("over",), nohud=True,
             text=[("SUZUKA 2005", INK, 2), ("RAIN IN QUALIFYING", INK, 1), ("SCRAMBLES THE GRID", YEL, 1)]),
        dict(frames=210, laps=(0, 0), cam=("pan", .995, .80, 2.8), nohud=True, labels=("RSC", "FIS", "MSC", "ALO", "RAI", "MON"),
             text=[("THE GRID", INK, 2), ("P1 R. SCHUMACHER", INK, 1), ("P3 FISICHELLA", INK, 1), ("P14 M. SCHUMACHER", MUT, 1), ("P16 ALONSO, P17 RAIKKONEN", YEL, 1)], tspeed=2.0),
        dict(frames=150, laps=(0, 1.3), linear=False, cam=("over",), tick=0, stop={"MON": .55}, sc=True,
             gaps={"FIS": 110, "MSC": 700, "ALO": 790, "RAI": 840},
             text=[("LIGHTS OUT", GRN, 2), ("MONTOYA CRASHES OUT", SOFT, 1), ("SAFETY CAR", YEL, 1)]),
        dict(frames=120, laps=(1.3, 5), cam=("over",), sc=True, gaps={"FIS": 90, "MSC": 420, "ALO": 470, "RAI": 520},
             text=[("THE FIELD BUNCHES UP", INK, 1)]),
        dict(frames=180, laps=(5, 19.89), cam=("over",), gaps={"FIS": 120, "MSC": 300, "ALO": 330, "RAI": 420},
             text=[("ALONSO AND RAIKKONEN", INK, 1), ("CARVE THROUGH THE FIELD", INK, 1)]),
        dict(frames=200, laps=(19.89, 19.95), cam=("frac", .875, 3.0), gaps={"MSC": 335, "ALO": 300}, labels=("ALO", "MSC"), tick=20 / 53,
             text=[("130R", YEL, 2), ("ALONSO AROUND THE OUTSIDE", INK, 1), ("OF M. SCHUMACHER", INK, 1)]),
        dict(frames=180, laps=(19.95, 44), cam=("over",), gaps={"RSC": 380, "FIS": -100, "MSC": 700, "ALO": 520, "RAI": 260},
             text=[("FISICHELLA LEADS", INK, 1), ("AFTER THE PIT STOPS", INK, 1)]),
        dict(frames=120, laps=(44, 44.5), cam=("car", "RAI", 2.4), labels=("RAI",), tick=44 / 53,
             text=[("RAIKKONEN", INK, 2), ("FASTEST LAP: 1:31.540", YEL, 1)]),
        dict(frames=150, laps=(44.5, 51.88), cam=("over",), gaps={"RAI": -55, "ALO": 650},
             text=[("RAIKKONEN HUNTS", INK, 1), ("FISICHELLA DOWN", INK, 1)]),
        dict(frames=170, laps=(51.88, 51.935), cam=("frac", .935, 3.2), gaps={"RAI": -78}, labels=("FIS", "RAI"), tick=52 / 53,
             text=[("LAP 52", MUT, 1), ("FISICHELLA DEFENDS", INK, 1), ("INTO THE CHICANE", INK, 1)]),
        dict(frames=200, laps=(52.03, 52.09), cam=("frac", .07, 3.2), gaps={"RAI": -128}, labels=("FIS", "RAI"),
             text=[("FINAL LAP, TURN 1", YEL, 1), ("AROUND THE OUTSIDE", INK, 1), ("RAIKKONEN TAKES THE LEAD", GRN, 1)]),
        dict(frames=150, laps=(52.09, 53 - 205 / L05), linear=False, cam=("frac", .0, 2.6), gaps={"RAI": -205}, labels=("RAI", "FIS"), win=True, tick=1.0,
             text=[("RAIKKONEN WINS", GRN, 2), ("FROM 17TH ON THE GRID", INK, 1), ("+1.633 S", INK, 1)]),
        dict(frames=180, laps=(53, 53), board=("FINAL CLASSIFICATION", [("1", "RAIKKONEN", "MCL05", "WINNER"), ("2", "FISICHELLA", "REN05", "+1.633"),
             ("3", "ALONSO", "REN05", "+17.456"), ("4", "WEBBER", "WIL05", "+22.274"), ("5", "BUTTON", "GEN", "+29.507"), ("6", "COULTHARD", "GEN", "+31.601")],
             ["FROM 17TH TO THE WIN", "FASTEST LAP: RAIKKONEN", "1:31.540, LAP 44"])),
        dict(frames=120, laps=(53, 53), cam=("over",), hide=tuple(["RSC", "FIS", "MSC", "ALO", "RAI", "MON"]), nohud=True, outro=True,
             text=[("SUZUKA 2005", INK, 2), ("17TH TO FIRST", YEL, 1), ("ON THE LAST LAP", INK, 1)]),
    ])
R05["audio"] = make_audio("map05")

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("91", "both"): render(R91, "recap_map_1991")
    if which in ("05", "both"): render(R05, "recap_map_2005")
