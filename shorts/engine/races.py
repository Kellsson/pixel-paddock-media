"""Race configs for the historic recap shorts. Every on-screen fact is listed with its sources in ../SOURCES.md.
Lap convention: `laps` = laps completed by the reference car (lapf 19.6 = on lap 20). Gaps in metres behind it."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from map_recap import *
SOFT = (255, 150, 150)

def gears_inset(lost, stuck_at):
    """lost: [(gear, frame)], stuck_at: frame from which only 6th is left."""
    def f(d, fr):
        gone = {g for g, t in lost if fr >= t}; stuck = fr >= stuck_at
        d.rectangle([SAFE_X0, 142, SAFE_X0 + 106, 167], fill=PANEL, outline=EDGE); tx(d, SAFE_X0 + 4, 145, "SENNA'S GEARS", MUT)
        for g in range(1, 7):
            x = SAFE_X0 + 4 + (g - 1) * 17; y = 152
            col = RED if g in gone else (GRN if stuck and g == 6 else ((80, 90, 112) if stuck else INK))
            d.rectangle([x, y, x + 12, y + 12], outline=col); tx(d, x + 5, y + 4, str(g), col)
            if g in gone: d.line([(x + 1, y + 11), (x + 11, y + 1)], fill=RED)
    return f

# ---------------------------------------------------------------- Brazil 1991
R91 = dict(geo=f"{HERE}/geo/br.geojson", laps=71, start_frac=0.0,
    cars={"SEN": ("MCL91", (242, 201, 76)), "PAT": ("WIL91", None), "MAN": ("WIL91", None), "BER": ("MCL91", None)},
    names={"SEN": "SENNA", "PAT": "PATRESE", "MAN": "MANSELL", "BER": "BERGER"},
    grid={"SEN": 0, "PAT": 30, "MAN": 60, "BER": 90}, maxgrid=7,
    results=[("1", "SENNA", "MCL91", "WINNER", 1), ("2", "PATRESE", "WIL91", "+2.991", 2), ("3", "BERGER", "MCL91", "+5.416", 4),
             ("4", "PROST", "FER91", "+19.369", 6), ("5", "PIQUET", "GEN", "+21.960", 7), ("6", "ALESI", "FER91", "+23.641", 5)],
    segments=[
        dict(frames=120, laps=(0, 0), cam=("over",), hide=("SEN", "PAT", "MAN", "BER"), nohud=True,
             text=[("BRAZIL 1991", INK, 2), ("INTERLAGOS, SAO PAULO", MUT, 1), ("DOUBLE WORLD CHAMPION SENNA", INK, 1), ("HAS NEVER WON AT HOME", YEL, 1)]),
        dict(frames=150, gridcard=[(1, "*SEN", "MCL91"), (2, "PAT", "WIL91"), (3, "MAN", "WIL91"), (4, "BER", "MCL91"), (5, "ALE", "FER91"), (6, "PRO", "FER91"), (7, "PIQ", "GEN")],
             text=[("THE GRID", INK, 2), ("P1 SENNA, MCLAREN", YEL, 1), ("P2 PATRESE, P3 MANSELL", INK, 1), ("FIRE ON BERGER'S MCLAREN", MUT, 1)]),
        dict(frames=120, laps=(0, .07), linear=False, cam=("car", "SEN", 2.4), labels=("SEN", "MAN", "PAT"),
             lat={"SEN": (-.9, 0), "PAT": (.9, 0), "MAN": (-.9, 0), "BER": (.9, 0)}, gaps={"MAN": 70, "PAT": 140, "BER": 260},
             text=[("LIGHTS OUT", GRN, 2), ("SENNA LEADS", INK, 1), ("MANSELL UP TO 2ND", INK, 1)]),
        dict(frames=42, jump=(1, 20), sub="MANSELL HUNTS SENNA"),
        dict(frames=150, laps=(19.55, 19.68), cam=("car", "SEN", 2.8), labels=("SEN", "MAN"), set={"MAN": 110, "PAT": 900, "BER": 1400}, gaps={"MAN": 70}, hide=("PAT", "BER"),
             text=[("THE CHASE", INK, 2), ("MANSELL CLOSES ON SENNA", INK, 1)]),
        dict(frames=165, laps=(21.93, 22.03), cam=("frac", .985, 3.0), nolap=True, labels=("MAN", "SEN"), pit={"MAN": (.99, -2.6)},
             set={"PAT": 700, "BER": 1100}, timer=(0, 14.0, "PIT STOP"),
             text=[("MANSELL PITS", INK, 2), ("GEARBOX WON'T FIND 1ST", YEL, 1), ("A 6 S TYRE STOP TAKES 14", INK, 1)]),
        dict(frames=42, jump=(22, 50), sub="PUNCTURE"),
        dict(frames=135, laps=(49.88, 49.98), cam=("frac", .985, 2.6), labels=("MAN",), pit={"MAN": (.99, -2.6)}, set={"PAT": 500, "BER": 900},
             text=[("PUNCTURE", SOFT, 2), ("MANSELL PITS AGAIN", INK, 1)]),
        dict(frames=42, jump=(50, 60), sub="MANSELL CHARGES BACK"),
        dict(frames=180, laps=(59.10, 59.20), cam=("car", "MAN", 2.8), labels=("MAN",), set={"MAN": 470, "PAT": 1600, "BER": 2600},
             spin={"MAN": (.45, 2 * math.pi * 1.25, 3.2)}, hide=("SEN", "PAT", "BER"), leader="SEN",
             text=[("MANSELL OUT", SOFT, 2), ("GEARBOX FAILS, HE SPINS", INK, 1), ("AFTER 59 LAPS", MUT, 1)]),
        dict(frames=42, jump=(60, 65), sub="7 LAPS TO GO", drop=("MAN",)),
        dict(frames=240, laps=(64.25, 64.40), cam=("car", "SEN", 3.0), labels=("SEN",), set={"PAT": 1300, "BER": 2100}, hide=("PAT", "BER"),
             inset=gears_inset([(4, 40), (3, 120), (5, 150)], 150),
             text=[("GEAR TROUBLE", INK, 2), ("4TH GONE. THEN 3RD AND 5TH", INK, 1), ("LAST 7 LAPS IN 6TH ONLY", YEL, 1)], tspeed=1.2),
        dict(frames=42, jump=(65, 69), sub="RAIN"),
        dict(frames=150, laps=(68.30, 68.42), cam=("car", "PAT", 2.2), labels=("SEN", "PAT"), rain=1, set={"PAT": 330, "BER": 620}, gaps={"PAT": 290},
             text=[("RAIN", INK, 2), ("PATRESE CLOSES IN", INK, 1), ("HIS GEARBOX IS FAILING TOO", YEL, 1)]),
        dict(frames=150, laps=(70.93, 71.0), linear=False, cam=("car", "SEN", 2.4), rain=.6, set={"PAT": 230, "BER": 420}, gaps={"PAT": 200}, labels=("SEN", "PAT"), win=True,
             text=[("SENNA WINS", GRN, 2), ("2.991 S AHEAD OF PATRESE", INK, 1)]),
        dict(frames=130, note=[("AFTER THE FLAG", MUT, 1), ("CRAMPS", INK, 2), ("LIFTED FROM THE CAR", INK, 1), ("CAN BARELY LIFT THE TROPHY", YEL, 1)]),
        dict(frames=230, board=("FINAL CLASSIFICATION", None, ["FIRST WIN AT HOME", "FASTEST LAP: MANSELL"])),
        dict(frames=140, slope="GRID VS FINISH"),
        dict(frames=75, outro=True, text=[("BRAZIL 1991", INK, 2), ("WON IN SIXTH GEAR", YEL, 1)]),
    ])
R91["audio"] = make_audio("map91")

# ---------------------------------------------------------------- Japan 2005
R05 = dict(geo=f"{HERE}/geo/jp.geojson", laps=53, start_frac=0.0, rot=-120,
    cars={"RSC": ("TOY05", None), "FIS": ("REN05", None), "MSC": ("FER05", None), "ALO": ("REN05", None), "RAI": ("MCL05", None),
          "MON": ("MCL05", None), "VIL": ("GEN", None)},
    names={"RSC": "R. SCHUMACHER", "FIS": "FISICHELLA", "MSC": "M. SCHUMACHER", "ALO": "ALONSO", "RAI": "RAIKKONEN", "MON": "MONTOYA", "VIL": "VILLENEUVE"},
    grid={"RSC": 0, "FIS": 40, "MSC": 260, "ALO": 300, "RAI": 320, "MON": 340, "VIL": 150}, maxgrid=17,
    results=[("1", "RAIKKONEN", "MCL05", "WINNER", 17), ("2", "FISICHELLA", "REN05", "+1.633", 3), ("3", "ALONSO", "REN05", "+17.456", 16),
             ("4", "WEBBER", "WIL05", "+22.274", 7), ("5", "BUTTON", "GEN", "+29.507", 2), ("6", "COULTHARD", "GEN", "+31.601", 6)],
    segments=[
        dict(frames=120, laps=(0, 0), cam=("over",), hide=tuple("RSC FIS MSC ALO RAI MON VIL".split()), nohud=True,
             text=[("JAPAN 2005", INK, 2), ("SUZUKA", MUT, 1), ("RAIN IN QUALIFYING", INK, 1), ("SCRAMBLES THE GRID", YEL, 1)]),
        dict(frames=180, gridcard=[(1, "RSC", "TOY05"), (2, "BUT", "GEN"), (3, "FIS", "REN05")] + [(p, None, "GEN") for p in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)]
             + [(14, "MSC", "FER05"), (16, "*ALO", "REN05"), (17, "*RAI", "MCL05"), (18, "MON", "MCL05")],
             text=[("THE GRID", INK, 2), ("P1 R. SCHUMACHER, TOYOTA", INK, 1), ("P3 FISICHELLA, RENAULT", INK, 1), ("P16 ALONSO, P17 RAIKKONEN", YEL, 1)], tspeed=2.0),
        dict(frames=100, laps=(0, .05), linear=False, cam=("car", "RSC", 2.2), hide=("VIL",), labels=("RSC", "FIS"),
             lat={"RSC": (-.9, 0), "FIS": (-.9, 0), "MSC": (.9, 0), "ALO": (.9, 0), "RAI": (-.9, 0), "MON": (.9, 0)},
             gaps={"FIS": 120, "MSC": 600, "ALO": 700, "RAI": 760, "MON": 820}, text=[("LIGHTS OUT", GRN, 2)]),
        dict(frames=160, laps=(1.10, 1.135), cam=("frac", .962, 3.0), labels=("MON", "VIL"), hide=("RSC", "FIS", "MSC", "ALO", "RAI"),
             set={"VIL": 880, "MON": 930}, gaps={"VIL": 880, "MON": 892}, lat={"VIL": (0, .9), "MON": (0, 1.8)},
             spin={"MON": (.55, 2 * math.pi * .9, 4.5)}, sc=.6, noleader=True,
             text=[("END OF LAP 1", MUT, 1), ("MONTOYA CRASHES OUT", SOFT, 1), ("SQUEEZED BY VILLENEUVE", INK, 1), ("SAFETY CAR, 6 LAPS", YEL, 1)]),
        dict(frames=42, jump=(2, 14), sub="R. SCHUMACHER PITS", drop=("MON", "VIL")),
        dict(frames=120, laps=(13.02, 13.08), cam=("car", "FIS", 2.6), labels=("FIS",), hide=("RSC", "MSC", "ALO", "RAI"), set={"FIS": 0},
             text=[("NEW LEADER", INK, 2), ("R. SCHUMACHER PITS EARLY", INK, 1), ("FISICHELLA LEADS", YEL, 1)]),
        dict(frames=42, jump=(14, 20), sub="130R"),
        dict(frames=210, laps=(19.85, 19.89), cam=("car", "MSC", 3.2), labels=("ALO", "MSC"), hide=("RSC", "FIS", "RAI"), noleader=True,
             set={"MSC": 0, "ALO": 45}, gaps={"MSC": 0, "ALO": -35}, lat={"ALO": (0, 1.8), "MSC": (0, -.4)},
             text=[("130R", YEL, 2), ("ALONSO AROUND THE OUTSIDE", INK, 1), ("OF M. SCHUMACHER", INK, 1)], tspeed=1.4),
        dict(frames=150, strategy=("TWO PLANS", [("FISICHELLA", "REN05", [20, 38]), ("RAIKKONEN", "MCL05", [26, 45])], ["RAIKKONEN STOPS LATER"])),
        dict(frames=42, jump=(20, 44), sub="FASTEST LAP"),
        dict(frames=120, laps=(43.55, 43.62), cam=("car", "RAI", 2.6), labels=("RAI",), hide=("RSC", "FIS", "MSC", "ALO"), set={"RAI": 0}, noleader=True,
             text=[("RAIKKONEN", INK, 2), ("FASTEST LAP: 1:31.540", YEL, 1), ("ONE LAP BEFORE HIS LAST STOP", INK, 1)]),
        dict(frames=42, jump=(44, 50), sub="THE HUNT"),
        dict(frames=150, laps=(49.40, 49.50), cam=("car", "RAI", 2.2), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 170}, gaps={"RAI": 130},
             text=[("THE HUNT", INK, 2), ("RAIKKONEN REJOINED 2ND", INK, 1), ("FISICHELLA IN SIGHT", YEL, 1)]),
        dict(frames=42, jump=(50, 52), sub="2 LAPS TO GO"),
        dict(frames=150, laps=(51.905, 51.935), cam=("frac", .925, 3.2), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 60}, gaps={"RAI": 38},
             lat={"FIS": (0, -.8), "RAI": (0, .3)},
             text=[("CHICANE", INK, 2), ("FISICHELLA DEFENDS HARD", INK, 1), ("AND LOSES MOMENTUM", YEL, 1)]),
        dict(frames=190, laps=(52.025, 52.075), cam=("frac", .06, 3.2), labels=("FIS", "RAI"), hide=("RSC", "MSC", "ALO"), set={"FIS": 0, "RAI": 25}, gaps={"RAI": -40},
             lat={"FIS": (.7, .7), "RAI": (-1.6, -.3)},
             text=[("FINAL LAP, TURN 1", YEL, 1), ("AROUND THE OUTSIDE", INK, 1), ("RAIKKONEN TAKES THE LEAD", GRN, 1)], tspeed=1.3),
        dict(frames=150, laps=(52.93, 53.0), linear=False, cam=("car", "RAI", 2.4), labels=("RAI", "FIS"), hide=("RSC", "MSC", "ALO"), set={"RAI": 0, "FIS": 180}, win=True,
             text=[("RAIKKONEN", GRN, 2), ("WINS FROM 17TH ON THE GRID", INK, 1), ("1.633 S AHEAD", INK, 1)]),
        dict(frames=230, board=("FINAL CLASSIFICATION", None, ["17TH TO 1ST", "FASTEST LAP: RAIKKONEN"])),
        dict(frames=150, slope="GRID VS FINISH"),
        dict(frames=75, outro=True, text=[("JAPAN 2005", INK, 2), ("17TH TO 1ST", YEL, 1)]),
    ])
R05["audio"] = make_audio("map05")

for R in (R91, R05):
    for sg in R["segments"]:
        if "board" in sg: sg["board"] = (sg["board"][0], R["results"], sg["board"][2])

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("91", "both"): render(R91, "recap_map_1991")
    if which in ("05", "both"): render(R05, "recap_map_2005")
