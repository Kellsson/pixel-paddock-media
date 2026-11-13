"""Race configs for the historic recap shorts. Every on-screen fact is listed with its sources in ../SOURCES.md.

Storytelling rules (v3):
- One fact per beat. A beat is either a card or a callout box next to the car it is about.
- Callouts: call=[(frame, target, [(text, colour, scale)], side)], only the latest one is shown.
  target = car code, ("slot", grid position) on a grid card, or ("frac", track fraction) listed in fracs.
- Max 2 lines, scale 2, about 13 characters per line.
- Time skips only via jump cards.
Lap convention: `laps` = laps completed by the reference car (lapf 19.6 = on lap 20). Gaps in metres behind it."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from map_recap import *
K = 0.8   # pace: action scenes and grid cards run at 80 % of their written length

def gears_inset(lost, stuck_at):
    """lost: [(gear, frame)], stuck_at: frame from which only 6th is left."""
    def f(d, fr):
        gone = {g for g, t in lost if fr >= t}; stuck = fr >= stuck_at
        x0 = CX - 50
        d.rectangle([x0, 134, x0 + 100, 166], fill=PANEL, outline=EDGE); tx(d, x0 + 4, 137, "SENNA'S GEARS", MUT)
        for g in range(1, 7):
            x = x0 + 4 + (g - 1) * 16; y = 145
            col = RED if g in gone else (GRN if stuck and g == 6 else ((80, 90, 112) if stuck else INK))
            d.rectangle([x, y, x + 13, y + 17], outline=col); tx(d, x + 4, y + 4, str(g), col, 2)
            if g in gone: d.line([(x + 1, y + 16), (x + 12, y + 1)], fill=RED)
    return f

# ---------------------------------------------------------------- Brazil 1991
G91 = [(1, "*SEN", "MCL91"), (2, "PAT", "WIL91"), (3, "MAN", "WIL91"), (4, "BER", "MCL91"), (5, "ALE", "FER91"), (6, "PRO", "FER91"), (7, "PIQ", "GEN")]
R91 = dict(geo=f"{HERE}/geo/br.geojson", laps=71, start_frac=0.0, track_m=28, car_m=22,   # closest separate sections: 43 m
    cars={"SEN": ("MCL91", (242, 201, 76)), "PAT": ("WIL91", None), "MAN": ("WIL91", None), "BER": ("MCL91", None)},
    names={"SEN": "SENNA", "PAT": "PATRESE", "MAN": "MANSELL", "BER": "BERGER"},
    grid={"SEN": 0, "PAT": 40, "MAN": 80, "BER": 120},
    results=[("1", "SENNA", "MCL91", "WINNER", 1), ("2", "PATRESE", "WIL91", "+2.991", 2), ("3", "BERGER", "MCL91", "+5.416", 4),
             ("4", "PROST", "FER91", "+19.369", 6), ("5", "PIQUET", "GEN", "+21.960", 7), ("6", "ALESI", "FER91", "+23.641", 5)],
    segments=[
        dict(frames=80, note=[("F1 HISTORY", GRN, 2), ("BRAZIL 1991", INK, 2), ("INTERLAGOS", MUT, 2)]),
        dict(frames=115, note=[("SENNA", INK, 2), ("2 WORLD TITLES", MUT, 2), ("HOME WINS", INK, 2), ("0", YEL, 6)]),
        dict(frames=110, gridcard=G91, header=[("THE GRID", INK, 2), ("SENNA ON POLE", YEL, 2)], mark=(1,)),
        dict(frames=120, gridcard=G91, delay=False, fire=4, header=[("FIRE ON", RED, 2), ("BERGER'S CAR", INK, 2)]),
        dict(frames=125, laps=(0, .07), linear=False, cam=("car", "SEN", 2.4), labels=("SEN", "MAN", "PAT"),
             lat={"SEN": (-.9, 0), "PAT": (.9, .5), "MAN": (-.9, -.5), "BER": (.9, .5)}, gaps={"MAN": 80, "PAT": 165, "BER": 260},
             call=[(35, "SEN", [("SENNA LEADS", INK, 2)], "down")]),
        dict(frames=40, jump=(1, 20)),
        dict(frames=135, laps=(19.55, 19.68), cam=("car", "SEN", 2.8, 0, -25), labels=("SEN", "MAN"), set={"MAN": 120, "PAT": 900, "BER": 1400}, gaps={"MAN": 75},
             hide=("PAT", "BER"), pos={"SEN": 1, "MAN": 2}, call=[(28, "MAN", [("P2 MANSELL", INK, 2), ("HUNTS SENNA", YEL, 2)], "down")]),
        dict(frames=140, laps=(21.93, 22.03), cam=("frac", .985, 3.0), nolap=True, labels=("MAN",), hide=("SEN", "PAT", "BER"), pit={"MAN": (.99, -2.6)},
             call=[(30, "MAN", [("MANSELL PITS", INK, 2)], "up"), (80, "MAN", [("NO 1ST GEAR", RED, 2)], "up")]),
        dict(frames=135, compare=("PIT STOP", [("USUAL", 6, (120, 130, 150)), ("MANSELL", 14, YEL)], "S", [("8 S LOST", YEL, 2)])),
        dict(frames=40, jump=(22, 50)),
        dict(frames=135, laps=(49.88, 49.98), cam=("frac", .985, 2.6), labels=("MAN",), hide=("SEN", "PAT", "BER"), pit={"MAN": (.99, -2.6)}, leader="SEN",
             call=[(28, "MAN", [("PUNCTURE", RED, 2), ("PITS AGAIN", INK, 2)], "up")]),
        dict(frames=40, jump=(50, 60)),
        dict(frames=190, laps=(59.10, 59.20), cam=("car", "MAN", 2.8), labels=("MAN",), set={"MAN": 470, "PAT": 1600, "BER": 2600},
             spin={"MAN": (.40, 2 * math.pi * 1.25, 2.2)}, hide=("SEN", "PAT", "BER"), leader="SEN",
             call=[(90, "MAN", [("GEARBOX FAILS", RED, 2)], "up"), (140, "MAN", [("MANSELL OUT", RED, 2)], "up")]),
        dict(frames=40, jump=(60, 65), drop=("MAN",)),
        dict(frames=300, laps=(64.20, 64.40), cam=("car", "SEN", 3.0), labels=("SEN",), set={"PAT": 1300, "BER": 2100}, hide=("PAT", "BER"),
             inset=gears_inset([(4, int(40 * K)), (3, int(120 * K)), (5, int(120 * K))], int(175 * K)),
             call=[(40, "SEN", [("4TH GONE", RED, 2)], "up"), (120, "SEN", [("3RD + 5TH", RED, 2), ("GONE TOO", INK, 2)], "up"),
                   (175, "SEN", [("ONLY 6TH LEFT", YEL, 2)], "up"), (235, "SEN", [("7 LAPS TO GO", INK, 2)], "up")]),
        dict(frames=40, jump=(65, 69)),
        dict(frames=190, laps=(68.30, 68.45), cam=("car", "PAT", 2.2), labels=("SEN", "PAT"), pos={"SEN": 1, "PAT": 2}, rain=1, set={"PAT": 330, "BER": 620}, gaps={"PAT": 290}, hide=("BER",),
             call=[(25, "PAT", [("RAIN", MUT, 2), ("PATRESE CLOSES", INK, 2)], "down"), (105, "PAT", [("HIS GEARBOX", INK, 2), ("FAILS TOO", YEL, 2)], "down")]),
        dict(frames=175, laps=(70.93, 71.0), linear=False, cam=("car", "SEN", 2.4, 0, 30), rain=.6, set={"PAT": 230, "BER": 420}, gaps={"PAT": 200}, hide=("BER",),
             labels=("SEN", "PAT"), win=True,
             call=[(20, "SEN", [("SENNA WINS", GRN, 2)], "up"), (90, "PAT", [("+2.991 S", YEL, 2)], "up")]),
        dict(frames=95, note=[("CRAMPS", YEL, 2), ("SENNA IS LIFTED", INK, 2), ("FROM THE CAR", INK, 2)]),
        dict(frames=170, board=("RESULT", None, ["1ST HOME WIN", "FASTEST LAP: MANSELL"])),
        dict(frames=150, outro=True, text=[("F1 HISTORY", GRN, 2), ("BRAZIL 1991", INK, 2), ("WON IN 6TH GEAR", YEL, 2)]),
    ])
R91["audio"] = make_audio("map91")

# ---------------------------------------------------------------- Japan 2005
G05 = [(1, "RSC", "TOY05"), (2, "BUT", "GEN"), (3, "FIS", "REN05")] + [(p, None, "GEN") for p in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)] \
    + [(14, "MSC", "FER05"), (16, "*ALO", "REN05"), (17, "*RAI", "MCL05"), (18, "MON", "MCL05")]
R05 = dict(geo=f"{HERE}/geo/jp.geojson", laps=53, start_frac=0.0, rot=-120, track_m=22, car_m=17.6,   # closest separate sections: 36 m (crossover excluded)
    cars={"RSC": ("TOY05", None), "FIS": ("REN05", None), "MSC": ("FER05", None), "ALO": ("REN05", None), "RAI": ("MCL05", None),
          "MON": ("MCL05", None), "VIL": ("GEN", None)},
    names={"RSC": "R. SCHUMACHER", "FIS": "FISICHELLA", "MSC": "M. SCHUMACHER", "ALO": "ALONSO", "RAI": "RAIKKONEN", "MON": "MONTOYA", "VIL": "VILLENEUVE"},
    grid={"RSC": 0, "FIS": 150, "MSC": 975, "ALO": 1125, "RAI": 1200, "MON": 1275, "VIL": 700},
    results=[("1", "RAIKKONEN", "MCL05", "WINNER", 17), ("2", "FISICHELLA", "REN05", "+1.633", 3), ("3", "ALONSO", "REN05", "+17.456", 16),
             ("4", "WEBBER", "WIL05", "+22.274", 7), ("5", "BUTTON", "GEN", "+29.507", 2), ("6", "COULTHARD", "GEN", "+31.601", 6)],
    segments=[
        dict(frames=80, note=[("F1 HISTORY", GRN, 2), ("JAPAN 2005", INK, 2), ("SUZUKA", MUT, 2)]),
        dict(frames=100, gridcard=G05, header=[("WET QUALIFYING", INK, 2), ("MIXED-UP GRID", MUT, 2)]),
        dict(frames=110, gridcard=G05, delay=False, header=[("ALONSO 16TH", INK, 2), ("RAIKKONEN 17TH", YEL, 2)], mark=(16, 17)),
        dict(frames=120, laps=(0, .05), linear=False, cam=("car", "RSC", 2.2), hide=("VIL",), labels=("RSC", "FIS"),
             lat={"RSC": (-.9, 0), "FIS": (-.9, 0), "MSC": (.9, .6), "ALO": (.9, .6), "RAI": (-.9, -.6), "MON": (.9, .6)},
             gaps={"FIS": 200, "MSC": 1000, "ALO": 1150, "RAI": 1300, "MON": 1450},
             call=[(30, "RSC", [("R. SCHUMACHER", INK, 2), ("LEADS", INK, 2)], "up")]),
        dict(frames=200, laps=(0.948, 0.985), cam=("frac", .962, 3.0), labels=("MON", "VIL"), hide=("RSC", "FIS", "MSC", "ALO", "RAI"), noscale=True,
             set={"VIL": 0, "MON": 30}, gaps={"VIL": 0, "MON": 4}, lat={"VIL": (-.4, -.15), "MON": (1.0, 1.0)},
             spin={"MON": (.42, 2 * math.pi * .9, 2.2)}, sc=.7, noleader=True,
             call=[(20, "VIL", [("VILLENEUVE", INK, 2), ("SQUEEZES", INK, 2)], "up"), (95, "MON", [("MONTOYA OUT", RED, 2)], "up")]),
        dict(frames=40, jump=(2, 13), drop=("MON", "VIL")),
        dict(frames=125, laps=(13.02, 13.08), cam=("car", "FIS", 2.6), labels=("FIS",), hide=("RSC", "MSC", "ALO", "RAI"), set={"FIS": 0},
             call=[(28, "FIS", [("FISICHELLA", INK, 2), ("NOW LEADS", YEL, 2)], "up")]),
        dict(frames=40, jump=(13, 20)),
        dict(frames=230, laps=(19.80, 19.90), cam=("car", "MSC", 6.0), labels=("ALO", "MSC"), hide=("RSC", "FIS", "RAI"), noleader=True,
             set={"MSC": 0, "ALO": 80}, gaps={"MSC": 0, "ALO": -50}, glin=True, lat={"ALO": (.9, .9), "MSC": (-.75, -.8)},
             call=[(20, "ALO", [("ALONSO", INK, 2), ("ATTACKS", INK, 2)], "down"), (125, "ALO", [("OUTSIDE PASS", YEL, 2), ("IN 130R", INK, 2)], "up")]),
        dict(frames=140, strategy=("TWO PLANS", [("FISICHELLA", "REN05", [20, 38]), ("RAIKKONEN", "MCL05", [26, 45])], [("KIMI STOPS LATER", YEL, 2)])),
        dict(frames=40, jump=(20, 44)),
        dict(frames=130, laps=(43.55, 43.62), cam=("car", "RAI", 2.6), labels=("RAI",), hide=("RSC", "FIS", "MSC", "ALO"), set={"RAI": 0}, noleader=True,
             call=[(28, "RAI", [("FASTEST LAP", YEL, 2), ("1:31.540", INK, 2)], "up")]),
        dict(frames=40, jump=(44, 50)),
        dict(frames=135, laps=(49.40, 49.50), cam=("car", "RAI", 2.2), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 300}, gaps={"RAI": 200}, pos={"FIS": 1, "RAI": 2},
             call=[(28, "RAI", [("P2 RAIKKONEN", INK, 2), ("HUNTS FOR P1", YEL, 2)], "down")]),
        dict(frames=40, jump=(50, 52)),
        dict(frames=170, laps=(51.905, 51.935), cam=("frac", .925, 3.2), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 170}, gaps={"RAI": 140},
             lat={"FIS": (0, -.8), "RAI": (0, .3)}, pos={"FIS": 1, "RAI": 2},
             call=[(25, "FIS", [("FISICHELLA", INK, 2), ("DEFENDS HARD", YEL, 2)], "up"), (100, "FIS", [("SLOW EXIT", RED, 2)], "up")]),
        dict(frames=200, laps=(52.0, 52.10), cam=("car", "FIS", 6.0), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 70}, gaps={"RAI": -60}, glin=True,
             lat={"FIS": (.65, .65), "RAI": (-.9, -.85)},
             call=[(15, "RAI", [("LAST LAP", YEL, 2)], "up"), (110, "RAI", [("OUTSIDE PASS", INK, 2), ("FOR THE LEAD", GRN, 2)], "up")]),
        dict(frames=175, laps=(52.93, 53.0), linear=False, cam=("car", "RAI", 2.4, 0, -28), labels=("RAI", "FIS"), hide=("RSC", "MSC", "ALO"), set={"RAI": 0, "FIS": 180}, pos={"RAI": 1, "FIS": 2}, win=True,
             call=[(20, "RAI", [("RAIKKONEN", GRN, 2), ("WINS", GRN, 2)], "up"), (90, "FIS", [("+1.633 S", YEL, 2)], "down")]),
        dict(frames=170, board=("RESULT", None, ["17TH TO 1ST", "FASTEST LAP: RAIKKONEN"])),
        dict(frames=150, outro=True, text=[("F1 HISTORY", GRN, 2), ("JAPAN 2005", INK, 2), ("17TH TO 1ST", YEL, 2)]),
    ])
R05["audio"] = make_audio("map05")

OLD_PX = lambda z: min(7 + (z - 1) * 7, 17)
def to_real_scale(R):
    """Scenes were laid out with zoom values and gaps for the old exaggerated car size. Keep the on-screen
    look (car size in pixels, gaps in car lengths) but now in real-world-sized track and cars."""
    fit = Track(R["geo"], rot=R.get("rot", 0)).fit; first = True
    for sg in R["segments"]:
        if "laps" not in sg: continue
        cam = list(sg.get("cam", ("over",)))
        z_old = cam[2] if cam[0] in ("car", "frac") else (cam[3] if cam[0] == "pan" else 1.0)
        f = R["car_m"] / (OLD_PX(z_old) / (fit * z_old))          # metres scale factor for gaps
        if cam[0] in ("car", "frac"): cam[2] = zoom_for(R, OLD_PX(z_old))
        elif cam[0] == "pan": cam[3] = zoom_for(R, OLD_PX(z_old))
        sg["cam"] = tuple(cam)
        for key in (() if sg.get("noscale") else ("set", "gaps")):
            if key in sg: sg[key] = {c: v * f for c, v in sg[key].items()}
        if first: R["grid"] = {c: v * f for c, v in R["grid"].items()}; first = False

def pace(R, k=K):
    to_real_scale(R)
    for sg in R["segments"]:
        if "laps" in sg or "gridcard" in sg:
            sg["frames"] = int(sg["frames"] * k)
            sg["call"] = [(int(c[0] * k),) + tuple(c[1:]) for c in sg.get("call", ())]
for R in (R91, R05):
    pace(R)
    for sg in R["segments"]:
        if "board" in sg: sg["board"] = (sg["board"][0], R["results"], sg["board"][2])

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("91", "both"): render(R91, "recap_map_1991")
    if which in ("05", "both"): render(R05, "recap_map_2005")
