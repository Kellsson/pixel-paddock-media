"""F1 TRACK GUIDE: Lusail - Oscar Piastri's 2025 pole lap (1:19.387). Sources: ../SOURCES_GUIDE.md"""
import os, sys, json, math, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from guide import *

R = f"{HERE}/../data/2025_qatar_q"
# centre line from all of PIA's and NOR's flying laps of the session (more samples = smoother line)
L = [l for l in json.load(open(f"{R}/laps.json")) if l["driver_number"] in (81, 4) and l["lap_duration"] and l["lap_duration"] < 82]
ext, allp = [], []
for n, f in ((81, "pia_loc_all"), (4, "nor_loc_all")):
    loc = json.load(open(f"{R}/{f}.json")); T = np.array([dt.datetime.fromisoformat(x["date"]).timestamp() for x in loc])
    P = np.array([[x["x"], x["y"]] for x in loc], float) * .1; allp.append((n, T, P))
    for l in L:
        if l["driver_number"] == n:
            a = dt.datetime.fromisoformat(l["date_start"]).timestamp(); ext.append(P[(T >= a) & (T <= a + l["lap_duration"])])
mv = json.load(open(f"{R}/mv_lusail.json"))
du = Guide(R, "PIA", np.vstack(ext), [[k["trackPosition"]["x"], k["trackPosition"]["y"]] for k in mv["corners"]])
c = du.car; A = c
du.track_m, du.car_m, du.zoom_px, du.grass_m = 30, 18, 13, 16

# pit lane: positions of PIA and NOR around their pit entries/exits in this session
pit = [p for p in json.load(open(f"{R}/pit.json")) if p["driver_number"] in (81, 4)]
pp = []
for n, T, P in allp:
    for e in pit:
        if e["driver_number"] != n: continue
        t0 = dt.datetime.fromisoformat(e["date"]).timestamp(); win = [(t0 - 25, t0 + 25)]
        if e["lane_duration"]: win.append((t0 + e["lane_duration"] - 25, t0 + e["lane_duration"] + 25))
        for a, b in win: pp.append(du.tf(P[(T >= a) & (T <= b)]))
prof = du.set_pitlane(np.vstack(pp)); sd = du.pit_side
# our track is drawn ~2x real width (30 m vs ~12-15 m): shift real lateral offsets out by the extra half-width
grow = lambda o: np.sign(o) * (du.track_m / 2 + max(0.0, abs(o) - 7))
du.pit[:, 1] = [grow(o) for o in du.pit[:, 1]]; du.pit_w = 10
print("pit lane s", round(prof[0, 0]), "..", round(prof[-1, 0]), "offset", round(float(np.median(prof[:, 1]))))
# pit building (50 garages, the longest in motorsport) behind the pit lane; main grandstand directly opposite
po = float(np.median(np.abs(du.pit[:, 1])))
gs0, gs1 = prof[0, 0], prof[-1, 0] - 30
du.buildings = [
    dict(kind="pits", s0=gs0, s1=gs1, o0=sd * (po + 6), o1=sd * (po + 26), doors=50, door_off=sd * (po + 6.5),
         fill=ROOF, poly=strip(du, gs0, gs1, sd * (po + 6), sd * (po + 26)), label="PIT BUILDING"),
    dict(kind="stand", s0=gs0 + 60, s1=gs1 - 60, o0=-sd * (du.track_m / 2 + du.grass_m + 4), o1=-sd * (du.track_m / 2 + du.grass_m + 30),
         fill=STAND, poly=strip(du, gs0 + 60, gs1 - 60, -sd * (du.track_m / 2 + du.grass_m + 4), -sd * (du.track_m / 2 + du.grass_m + 30)),
         label="MAIN GRANDSTAND"),
]
# floodlight poles all round the lap (positions schematic: one every 40 m, alternating sides)
du.poles = [du.off_pt(s, (1 if k % 2 else -1) * (du.track_m / 2 + du.grass_m + 3)) for k, s in enumerate(np.arange(10, du.length, 40))]
du.poles = [p for p in du.poles if not any(min(b["s0"], b["s1"]) - 40 < ((du.lateral(np.array([p]))[0][0] + du.length / 2) % du.length - du.length / 2) < max(b["s0"], b["s1"]) + 40 for b in du.buildings)]

# facts from the raw telemetry (car_data ~3.7 Hz) of this lap
cd = json.load(open(f"{R}/PIA_car_data.json")); ts = lambda s: (dt.datetime.fromisoformat(s) - c["T0"]).total_seconds()
raw = [(ts(x["date"]), x) for x in cd if 0 <= ts(x["date"]) <= c["lap"]]
vmax = max(x["speed"] for _, x in raw)
thr = 100 * np.mean([x["throttle"] >= 98 for _, x in raw]); brk = 100 * np.mean([x["brake"] > 0 for _, x in raw])
dist_of = lambda t: float(np.interp(t, c["t"], c["d"]))
def corner_min(n, back=120, fwd=60):
    s = du.corners[n - 1]["s"]; k = [(t, x) for t, x in raw if s - back < dist_of(t) < s + fwd]
    t, x = min(k, key=lambda q: q[1]["speed"]); return x["speed"], x["n_gear"], t
FACT = {n: corner_min(n) for n in range(1, 17)}
brake_t1 = max(x["speed"] for t, x in raw if dist_of(t) < du.corners[0]["s"] - 100)
print("vmax", vmax, "thr", round(thr), "brk", round(brk), "T1 brake from", brake_t1, {n: FACT[n][:2] for n in FACT})
json.dump(dict(vmax=vmax, thr=thr, brk=brk, corners={n: FACT[n][:2] for n in FACT}), open(f"{R}/facts.json", "w"))
ORD = {1: "1ST", 2: "2ND", 3: "3RD"}; o = lambda g: ORD.get(g, f"{g}TH")
du.hud_sub = "POLE 2025"; du.lap_txt = "1:19.387"

t1v, t1g, t1t = FACT[1]; t6v, t6g, t6t = FACT[6]; t12v, t12g, t12t = FACT[12]; t16v, t16g, t16t = FACT[16]
plan = [(-1.0, None), (5.0, 2.4), (11.5, 1.1), (28.0, 2.4), (33.5, 1.1), (54.0, 2.6), (64.5, 1.5), (70.0, 2.6), (74.5, 1.3), (c["lap"], 1.8)]
calls = [
    (-0.6, "PIA", [("1068 M", GRN, 2), ("MAIN STRAIGHT", INK, 2)], "up", 4.6),
    (4.8, "PIA", [(f"{vmax} KM/H", GRN, 2), ("THEN BRAKE", INK, 2)], "up", 8.2),
    (8.3, "PIA", [(f"T1: {t1v} KM/H", INK, 2), (f"{o(t1g)} GEAR", GRN, 2)], "up", 12.6),
    (14.0, "PIA", [("FAKE GRASS", GRN, 2), ("KEEPS SAND OFF", INK, 2)], "up", 27.0),
    (29.5, "PIA", [("SLOWEST: T6", INK, 2), (f"{t6v} KM/H {o(t6g)}", GRN, 2)], "up", 35.0),
    (37.0, "PIA", [("1000 LIGHT", INK, 2), ("POLES AROUND", INK, 2)], "up", 53.0),
    (55.5, "PIA", [(f"T12: {t12v} KM/H", GRN, 2), (f"{o(t12g)} GEAR", INK, 2)], "up", 64.0),
    (65.0, "PIA", [("T12-T15", INK, 2), ("ALL 7TH GEAR", GRN, 2)], "up", 70.5),
    (71.0, "PIA", [(f"T16: {t16v} KM/H", INK, 2), ("LAST CORNER", GRN, 2)], "up", 76.0),
    (76.2, "pits", [("WORLD'S LONGEST", INK, 2), ("PIT BUILDING", GRN, 2)], "down", c["lap"]),
    (c["lap"] + .5, "PIA", [("POLE BY 0.108", GRN, 2), ("AHEAD OF NORRIS", INK, 2)], "down"),
]
before = [dict(frames=120, brand=[("F1 TRACK", "acc", 11), ("GUIDE", "acc", 11), ("LUSAIL", "ink", 5)],
               car_lines=[("PIASTRI", "ink", 6), ("2025 POLE LAP", "mute", 4), ("1:19.387", "acc", 5)], car_y=880)]
after = [
    dict(frames=110, mood="podium", note=[("FLAT OUT", INK, 2), (f"{thr:.0f} % OF THE LAP", GRN, 2), ("ON THE BRAKES", INK, 2), (f"{brk:.0f} %", RED, 2)]),
    dict(frames=140, brand=[("F1 TRACK", "acc", 9), ("GUIDE", "acc", 9), ("LUSAIL", "ink", 4)], follow=True),
]
if __name__ == "__main__":
    render_guide(du, plan, "guide_2025_lusail", before, after, calls, mood_split=54.0, hold_s=3.0)
