"""Race replay: 2026 Mexico City GP (OpenF1 session 11404). Facts and their sources: ../SOURCES_REPLAY.md
Race times t = seconds after 2026-11-01 20:00:00 UTC. Every highlight time below was located in the position data."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replay import *

HERE = os.path.dirname(os.path.abspath(__file__))
R = Race(f"{HERE}/../data/2026_mexico", f"{HERE}/../data/2026_mexico.npz")
R.track_m, R.car_m = 30, 16          # closest separate track sections: 65 m
R.sc = [(3846, 3962), (7502, 7918)]
R.crash = dict(car="BOT", t_off=3828.6, t_stop=3833.8)   # data: ~339 km/h at 3826, standstill at 3834 just after T1  # race control: SC deployed lap 44 -> red flag; SC lap 59 -> in at end of lap 62
grid = R.order(100)
R.grid_rows = [(i + 1, ("*" if c == "HAM" else "") + c, R.dr[c]["_team"]) for i, c in enumerate(grid)]
res = R.result
R.podium_rows = [(str(r["position"]), R.dr[R.acr[r["driver_number"]]]["last_name"].upper(), R.dr[R.acr[r["driver_number"]]]["_team"],
                  "WINNER" if r["position"] == 1 else f"+{r['gap_to_leader']:.3f}", grid.index(R.acr[r["driver_number"]]) + 1) for r in res[:6]]

S = [
    dict(frames=105, brand=[("F1 RACE REPLAY", "acc", 6), ("MEXICO CITY", "ink", 5), ("1 NOV 2026", "mute", 4)], chip="TITLE DECIDER"),
    dict(frames=85, grid=True, header=[("HAMILTON", INK, 2), ("ON POLE", YEL, 2)], mark=(1,)),
    # start: Ferraris fight, run wide at T4, Verstappen up to P2, Leclerc leads
    dict(t0=204, t1=257, dur=7.0, live=True, cam=("pack", ["HAM", "LEC", "VER"], 11), labels=("HAM", "LEC", "VER"),
         call=[(212, "HAM", [("LIGHTS OUT", GRN, 2)], "up"), (236, "LEC", [("BOTH FERRARIS", INK, 2), ("RUN WIDE", YEL, 2)], "up"),
               (247, "VER", [("VER UP TO P2", GRN, 2)], "up")]),
    dict(t0=257, t1=1222, dur=2.8, cam=("over",)),
    dict(t0=1222, t1=1240, dur=2.0, live=True, cam=("over",), call=[(1223, "LEC", [("LECLERC", INK, 2), ("5 S PENALTY", RED, 2)], "up")]),
    dict(t0=1240, t1=2640, dur=2.6, cam=("over",)),
    dict(t0=2640, t1=2660, dur=2.2, live=True, cam=("over",), call=[(2641, "ANT", [("ANTONELLI LEADS", YEL, 2), ("YET TO STOP", INK, 2)], "up")]),
    dict(t0=2660, t1=3790, dur=2.4, cam=("over",)),
    dict(t0=3790, t1=3806, dur=1.8, live=True, cam=("over",), call=[(3791, "VER", [("VER LEADS", YEL, 2), ("AFTER THE STOPS", INK, 2)], "up")]),
    dict(t0=3806, t1=3824, dur=1.2, cam=("car", "BOT", 12)),
    # Bottas: suspension failure into Turn 1
    dict(t0=3824, t1=3842, dur=6.4, live=True, cam=("car", "BOT", 12), labels=("BOT",),
         call=[(3826.5, "BOT", [("SUSPENSION", RED, 2), ("FAILURE", RED, 2)], "up"), (3833.8, "BOT", [("INTO THE", RED, 2), ("BARRIER", RED, 2)], "up")]),
    dict(frames=80, note=[("RED FLAG", RED, 2), ("BARRIER REPAIRS", INK, 2)]),
    # standing restart: Hamilton past Leclerc into T1
    dict(t0=6488, t1=6513, dur=7.4, live=True, cam=("pack", ["VER", "HAM", "LEC"], 11), labels=("VER", "HAM", "LEC"),
         call=[(6489, "VER", [("STANDING", INK, 2), ("RESTART", YEL, 2)], "up"), (6497, "HAM", [("HAMILTON", INK, 2), ("TO P2", YEL, 2)], "up")]),
    dict(t0=6513, t1=6588, dur=1.3, cam=("car", "ANT", 12)),
    dict(t0=6588, t1=6603, dur=5.0, live=True, cam=("pack", ["ANT", "LEC"], 12), labels=("ANT", "LEC"),
         call=[(6594.5, "ANT", [("ANTONELLI", INK, 2), ("TO P3", YEL, 2)], "up")]),
    dict(t0=6603, t1=7480, dur=2.4, cam=("over",)),
    # Lindblad / Piastri, Turn 2
    dict(t0=7480, t1=7495, dur=5.4, live=True, cam=("pack", ["LIN", "PIA"], 12), labels=("LIN", "PIA"),
         call=[(7486.5, "LIN", [("CONTACT", RED, 2), ("LIN AND PIA", INK, 2)], "up")]),
    dict(t0=7495, t1=8618, dur=3.3, cam=("over",), call=[(7520, "VER", [("SAFETY CAR", YEL, 2)], "up")]),
    # finish
    dict(t0=8618, t1=8638, dur=5.5, live=True, cam=("pack", ["VER", "HAM"], 11), labels=("VER", "HAM"), win=True,
         call=[(8620, "HAM", [("HAMILTON", INK, 2), ("ON THE ATTACK", YEL, 2)], "down"), (8634, "VER", [("VERSTAPPEN", GRN, 2), ("WINS", GRN, 2)], "up")]),
    dict(frames=110, note=[("ANTONELLI P3", INK, 2), ("WORLD CHAMPION", YEL, 2), ("YOUNGEST EVER", GRN, 2), ("AGE 20Y 68D", MUT, 2)]),
    dict(frames=170, board=True, extra=["WON BY 0.799 S"]),
    dict(frames=150, brand=[("F1 RACE REPLAY", "acc", 5), ("MEXICO CITY", "ink", 4)], follow=True),
]

if __name__ == "__main__":
    render(R, S, "replay_2026_mexico", "rep26mex")
