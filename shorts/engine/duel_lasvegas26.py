"""QUALI DUEL Las Vegas 2026: Antonelli (fastest, 1:33.893) vs Verstappen (1:34.151, starts on pole after ANT's grid penalty).
OpenF1 session 11416. Facts + sources in ../SOURCES_DUEL.md"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import duel
from duel import *
apply_brand()
from replay import INK, MUT, GRN, RED, YEL

HERE = os.path.dirname(os.path.abspath(__file__))
du = Duel(f"{HERE}/../data/2026_lasvegas_q", "ANT", "VER")
du.track_m, du.car_m, du.zoom_px = 36, 20, 12      # closest separate sections: 121 m
A, B = du.cars
cA = lambda k: sum(A["secs"][:k]); cB = lambda k: sum(B["secs"][:k])
g1, g2 = A["secs"][0] - B["secs"][0], A["secs"][1] - B["secs"][1]

plan = [(-1.0, None), (54.0, 4.2), (90.5, 2.8), (97.3, 1.0)]       # lap time -> playback speed
calls = [
    (max(cA(1), cB(1)) + .2, "VER", [("S1: VER", INK, 2), (f"-{g1:.3f} S", GRN, 2)], "up"),
    (max(cA(2), cB(2)) + .2, "VER", [("S2: VER", INK, 2), (f"-{g2:.3f} S", GRN, 2)], "up"),
    (max(cA(2), cB(2)) + 9, "VER", [("VER AHEAD", INK, 2), (f"BY {cA(2) - cB(2):.3f} S", GRN, 2)], "up"),
    (63.0, "ANT", [("ANT IN THE TOW", GRN, 2), ("351 KM/H", INK, 2)], "up"),
    (74.0, "ANT", [("ANT CLOSES", INK, 2), ("THE GAP", GRN, 2)], "up"),
    (84.0, "ANT", [("NECK AND NECK", INK, 2)], "up"),
    (A["lap"] + .05, "ANT", [("ANTONELLI", INK, 2), (f"FASTER BY {B['lap'] - A['lap']:.3f}", GRN, 2)], "up"),
    (B["lap"] + .1, "ANT", [("S3 DECIDED IT", INK, 2), (f"ANT -{B['secs'][2] - A['secs'][2]:.3f} S", GRN, 2)], "up"),
]
before = [dict(frames=100, brand=[("QUALI", "acc", 11), ("DUEL", "acc", 11), ("LAS VEGAS 2026", "ink", 5)], chip="ANT VS VER", logo=False)]
after = [
    dict(frames=150, table=True, mood="podium"),
    dict(frames=110, mood="podium", note=[("FASTEST: ANT", GRN, 2), ("5-PLACE GRID", RED, 2), ("PENALTY", RED, 2), ("VER ON POLE", INK, 2)]),
    dict(frames=140, brand=[("QUALI", "acc", 9), ("DUEL", "acc", 9), ("LAS VEGAS 2026", "ink", 4)], follow=True),
]

if __name__ == "__main__":
    render_duel(du, plan, "duel_2026_lasvegas", before, after, calls, mood_split=54.0)
