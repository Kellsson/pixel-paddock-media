"""Download one race from OpenF1 for the replay engine (data stays local, not in the repo: OpenF1 is CC BY-NC-SA,
non-commercial). Usage: python3 replay_fetch.py <session_key> <out_dir> <T0 iso, e.g. 2026-11-01T20:00:00+00:00> <race start s after T0> <end s>
Then: python3 replay_prep.py <out_dir> <out_dir>.npz <reference driver number>"""
import sys, os, json, time, urllib.request, datetime as dt
import numpy as np
sk, out, T0s, start, end = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
os.makedirs(out, exist_ok=True); B = "https://api.openf1.org/v1"
get = lambda u: json.load(urllib.request.urlopen(u, timeout=300))
for ep in ("drivers", "laps", "position", "intervals", "race_control", "pit", "session_result"):
    json.dump(get(f"{B}/{ep}?session_key={sk}"), open(f"{out}/{ep}.json", "w")); time.sleep(.5)
T0 = dt.datetime.fromisoformat(T0s); a = (T0 - dt.timedelta(seconds=0)).strftime("%Y-%m-%dT%H:%M:%S"); b = (T0 + dt.timedelta(seconds=end)).strftime("%Y-%m-%dT%H:%M:%S")
arr = {}
for d in json.load(open(f"{out}/drivers.json")):
    n = d["driver_number"]; L = get(f"{B}/location?session_key={sk}&driver_number={n}&date>{a}&date<{b}")
    arr[f"t{n}"] = np.array([(dt.datetime.fromisoformat(x["date"]) - T0).total_seconds() for x in L])
    arr[f"p{n}"] = np.array([[x["x"], x["y"]] for x in L], float); time.sleep(.5); print(n, len(L))
np.savez_compressed(f"{out}/loc.npz", **arr)
open(f"{out}/T0.txt", "w").write(T0s); open(f"{out}/start.txt", "w").write(str(start))
