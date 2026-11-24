"""QUALI DUEL Las Vegas 2026: Antonelli (fastest, 1:33.893) vs Verstappen (1:34.151, starts on pole after ANT's grid penalty).
OpenF1 session 11416. Facts + sources in ../SOURCES_DUEL.md"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import duel
from duel import *
apply_brand()
from replay import INK, MUT, GRN, RED, YEL

HERE = os.path.dirname(os.path.abspath(__file__))
du = Duel(f"{HERE}/../data/2026_lasvegas_q", "ANT", "VER")
du.track_m, du.car_m, du.zoom_px = 36, 20, 12      # closest separate sections: 121 m
A, B = du.cars
# real landmarks: circuit outline (bacinger/f1-circuits, lon/lat) aligned to the data line; coordinates from Wikipedia/OSM
rms = landmarks_from_geo(du, f"{HERE}/../../toolkit/geo/lv.geojson",
                         {"SPHERE": (-115.1617, 36.1208), "BELLAGIO": (-115.1741, 36.1127)})
print("geo fit rms m", round(rms, 1))
L = {l["name"]: l for l in du.landmarks}
L["SPHERE"].update(r_m=78)                                       # 157 m wide
dB = float(np.argmin(((du.C - L["BELLAGIO"]["p"]) ** 2).sum(1))) / len(du.C) * du.length
x_, y_, hB = du.at(dB); L["BELLAGIO"].update(kind="LAKE", w_m=250, h_m=80, ang=hB, label="BELLAGIO")
# "THE STRIP" tag beside Las Vegas Blvd, opposite side from the Bellagio lake
x_, y_, h_ = du.at(4150); nx, ny = -math.sin(h_), math.cos(h_)
side = -1 if (L["BELLAGIO"]["p"][0] - x_) * nx + (L["BELLAGIO"]["p"][1] - y_) * ny > 0 else 1
du.landmarks.append(dict(name="THE STRIP", kind="TAG", p=np.array([x_ + side * nx * 42, y_ + side * ny * 42])))
# the tow: Lindblad was on track ahead of Antonelli for almost his whole lap (OpenF1 location, all cars)
du.add_tow("ANT", f"{HERE}/../data/2026_lasvegas_q/ant_lap_all.pkl", "LIN", show=(58.0, 74.0))
cA = lambda k: sum(A["secs"][:k]); cB = lambda k: sum(B["secs"][:k])
g1, g2 = A["secs"][0] - B["secs"][0], A["secs"][1] - B["secs"][1]

plan = [(-1.0, None), (54.0, 4.2), (90.5, 2.8), (97.3, 1.0)]       # lap time -> playback speed
calls = [
    (max(cA(1), cB(1)) + .2, "VER", [("S1: VER", INK, 2), (f"-{g1:.3f} S", GRN, 2)], "up"),
    (max(cA(2), cB(2)) + .2, "VER", [("S2: VER", INK, 2), (f"-{g2:.3f} S", GRN, 2)], "up"),
    (max(cA(2), cB(2)) + 9, "VER", [("VER AHEAD", INK, 2), (f"BY {cA(2) - cB(2):.3f} S", GRN, 2)], "up"),
    (60.0, "LIN", [("LINDBLAD AHEAD", INK, 2), ("= ANT'S TOW", GRN, 2)], "up"),
    (66.5, "ANT", [("ANT 351 KM/H", GRN, 2), ("VER MAX 340", INK, 2)], "up"),
    (74.0, "ANT", [("ANT CLOSES", INK, 2), ("THE GAP", GRN, 2)], "up"),
    (84.0, "ANT", [("NECK AND NECK", INK, 2)], "up"),
    (A["lap"] + .05, "ANT", [("ANTONELLI", INK, 2), (f"FASTER BY {B['lap'] - A['lap']:.3f}", GRN, 2)], "up"),
    (B["lap"] + .1, "ANT", [("S3 DECIDED IT", INK, 2), (f"ANT -{B['secs'][2] - A['secs'][2]:.3f} S", GRN, 2)], "up"),
]
before = [dict(frames=110, brand=[("QUALI", "acc", 11), ("DUEL", "acc", 11), ("LAS VEGAS 2026", "ink", 5)], chip="ANT VS VER", logo=False, cars=1020)]
after = [
    dict(frames=150, table=True, mood="podium"),
    dict(frames=110, mood="podium", note=[("ANT: LIN TOW", GRN, 2), ("ALL LAP", GRN, 2), ("VER: NO TOW", INK, 2)]),
    dict(frames=110, mood="podium", note=[("FASTEST: ANT", GRN, 2), ("5-PLACE GRID", RED, 2), ("PENALTY", RED, 2), ("VER ON POLE", INK, 2)]),
    dict(frames=140, brand=[("QUALI", "acc", 9), ("DUEL", "acc", 9), ("LAS VEGAS 2026", "ink", 4)], follow=True),
]

if __name__ == "__main__":
    render_duel(du, plan, "duel_2026_lasvegas", before, after, calls, mood_split=54.0)
