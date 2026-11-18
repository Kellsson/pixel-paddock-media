"""Session reel straight from OpenF1 (api.openf1.org): top 10, gaps, moves vs previous session, auto insight.
Usage: python3 reel_session.py YEAR "LOCATION" "SESSION NAME" LABEL OUT_NAME [GP_KEY]
  e.g. python3 reel_session.py 2026 "Las Vegas" "Practice 1" FP1 2026-11-20_fp1 "LAS VEGAS"
Session names (OpenF1): Practice 1/2/3, Qualifying, Sprint Qualifying, Sprint, Race.
Writes out_reel/OUT_NAME.mp4 (+ _cover/_sheet) and out_reel/OUT_NAME.json (rows, for the caption).
Results still need a second-source check (F1.com) before posting."""
import sys, json, urllib.request, urllib.parse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_v4
from reel_results import OUT

API = "https://api.openf1.org/v1"
TEAMMAP = {"Haas F1 Team": "Haas", "Red Bull Racing": "Red Bull", "Kick Sauber": "Audi", "RB": "Racing Bulls"}
PREV = {"Practice 2": "Practice 1", "Practice 3": "Practice 2", "Qualifying": "Practice 3", "Race": "Qualifying"}

def get(path, **q):
    return json.load(urllib.request.urlopen(f"{API}/{path}?{urllib.parse.urlencode(q)}"))

def session_key(year, location, name):
    s = [x for x in get("sessions", year=year, location=location) if x["session_name"] == name]
    if not s: raise SystemExit(f"no session {name} @ {location} {year}")
    return s[0]["session_key"]

def classification(sk):
    res = sorted([r for r in get("session_result", session_key=sk) if r.get("position")], key=lambda r: r["position"])
    drv = {d["driver_number"]: d for d in get("drivers", session_key=sk)}
    out = []
    lead_laps = res[0].get("number_of_laps") or 0
    for r in res:
        d = drv[r["driver_number"]]; team = TEAMMAP.get(d["team_name"], d["team_name"])
        g = r.get("gap_to_leader")
        if isinstance(g, list): g = next((x for x in reversed(g) if x is not None), None)   # quali: last segment reached
        if r["position"] == 1: gs = "LEADER"
        elif isinstance(g, str): gs = g.upper()
        elif g is None: gs = "NO TIME"
        elif (r.get("number_of_laps") or 0) < lead_laps and "Race" in name_glob: gs = f"+{lead_laps - r['number_of_laps']} LAP"
        else: gs = f"+{g:.3f}"
        out.append((d["name_acronym"], team, gs, r))
    return out

if __name__ == "__main__":
    year, loc, name, label, out_name = sys.argv[1:6]; gp = sys.argv[6] if len(sys.argv) > 6 else loc.upper()
    name_glob = name
    sk = session_key(year, loc, name); cl = classification(sk)
    rows = [(c, t, g) for c, t, g, _ in cl[:10]]
    moves, mlabel = None, "VS GRID"
    if name in PREV:
        try:
            prev = {c: i + 1 for i, (c, *_rest) in enumerate(classification(session_key(year, loc, PREV[name])))}
            moves = {c: prev[c] - (i + 1) for i, (c, *_r) in enumerate(cl[:10]) if c in prev}
            mlabel = "VS GRID" if name == "Race" else f"VS {dict(zip(PREV.values(), ['FP1','FP2','FP3','QUALI'])).get(PREV[name], 'PREV')}"
        except SystemExit: pass
    p1, p2, p10 = cl[0], cl[1], cl[min(9, len(cl) - 1)]
    if name == "Race":
        ins = [f"{p1[0]} WINS {label if label != 'RACE' else ''}".strip(), f"MARGIN TO P2: {p2[2].lstrip('+')}S" if p2[2][0] == "+" and "LAP" not in p2[2] else f"P2: {p2[0]}"]
        if moves:
            best = max(moves.items(), key=lambda kv: kv[1])
            if best[1] > 0: ins.append(f"{best[0]} +{best[1]} VS GRID")
    else:
        ins = [f"{p1[0]} TOPS {label}", f"MARGIN TO P2: {p2[2].lstrip('+')}S"]
        if p10[2].startswith("+"): ins.append(f"TOP 10 WITHIN {p10[2].lstrip('+')}S")
    reel_v4.make(label, rows, out_name, gp=gp, insight=ins, moves=moves, moves_label=mlabel)
    json.dump({"session_key": sk, "rows": rows, "moves": moves, "insight": ins}, open(f"{OUT}/{out_name}.json", "w"), indent=1)
    print(json.dumps({"rows": rows, "insight": ins}))
