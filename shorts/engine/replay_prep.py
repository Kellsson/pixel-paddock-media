"""Prepare an OpenF1 race for the replay engine.
Usage: python3 replay_prep.py <raw_dir> <out.npz>
raw_dir holds OpenF1 JSON (drivers, laps, position, intervals, race_control, pit, session_result) and loc.npz
(t<n>, p<n>: seconds since T0 and raw x/y per car). Writes a compact npz with:
  track (N,2) centre line in metres (rotated for portrait), pit (M,2) pit lane, length
  per car: t, x, y, d (race distance in metres, monotonic-ish)
"""
import sys, json, math, datetime as dt
import numpy as np

raw, out = sys.argv[1], sys.argv[2]
J = lambda n: json.load(open(f"{raw}/{n}.json"))
drivers = J("drivers"); laps = J("laps")
L = np.load(f"{raw}/loc.npz")
T0 = dt.datetime.fromisoformat(open(f"{raw}/T0.txt").read().strip())
ts = lambda s: (dt.datetime.fromisoformat(s) - T0).total_seconds()
nums = [d["driver_number"] for d in drivers]
T_START = float(open(f"{raw}/start.txt").read().strip())
SCALE = .1   # OpenF1 location units are decimetres

def lap_samples(n, k):
    ls = {l["lap_number"]: l for l in laps if l["driver_number"] == n}
    if k not in ls or k + 1 not in ls or not ls[k]["date_start"] or not ls[k + 1]["date_start"]: return None
    a, b = ts(ls[k]["date_start"]), ts(ls[k + 1]["date_start"])
    t, p = L[f"t{n}"], L[f"p{n}"] * SCALE
    m = (t >= a) & (t < b)
    return p[m] if m.sum() > 50 else None

# --- reference centre line: one clean lap, then densified with laps of many cars
ref_n = int(sys.argv[3]) if len(sys.argv) > 3 else nums[0]
ref = lap_samples(ref_n, 10)
def resample(P, n):
    seg = np.sqrt((np.diff(np.vstack([P, P[:1]]), axis=0) ** 2).sum(1)); cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], n, endpoint=False)
    Q = np.vstack([P, P[:1]])
    return np.stack([np.interp(s, cum, Q[:, 0]), np.interp(s, cum, Q[:, 1])], 1), cum[-1]
R0, _ = resample(ref, 1500)
pts = []
for n in nums:
    for k in range(6, 16):
        q = lap_samples(n, k)
        if q is not None: pts.append(q)
P = np.vstack(pts)
# progress of every point on R0, then median per bin -> dense, smooth centre line
idx = np.argmin(((P[:, None, :] - R0[None, ::3, :]) ** 2).sum(-1), axis=1) * 3
bins = np.zeros((1500, 2)); cnt = np.zeros(1500)
for i, b in enumerate(idx):
    bins[b] += P[i]; cnt[b] += 1
ok = cnt > 0
for i in np.where(~ok)[0]: bins[i] = R0[i]; cnt[i] = 1
C = bins / cnt[:, None]
for _ in range(3):  # light smoothing, circular
    C = (np.roll(C, 1, 0) + 2 * C + np.roll(C, -1, 0)) / 4
C, length = resample(C, 1500)

# --- rotate so the track is tall rather than wide (portrait video)
best = None
for a in range(0, 180, 3):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    Rm = np.array([[ca, -sa], [sa, ca]]); Q = C @ Rm.T; w, h = np.ptp(Q, 0)
    score = min(108 / w, 112 / h)
    if best is None or score > best[0]: best = (score, a, Rm)
_, ang, Rm = best
def tf(Q): Q = Q @ Rm.T; return np.stack([Q[:, 0], -Q[:, 1]], 1)   # screen y points down
Cs = tf(C)

# --- per car: screen coords, race distance along the centre line
res = {"track": Cs, "length": length, "rot": ang}
Csub = Cs[::2]
for n in nums:
    t = L[f"t{n}"]; p = tf(L[f"p{n}"] * SCALE)
    j = np.argmin(((p[:, None, :] - Csub[None, :, :]) ** 2).sum(-1), axis=1) * 2
    s = j / len(Cs) * length; off = np.sqrt(((p - Cs[j]) ** 2).sum(1))
    # continuous race distance: unwrap the lap position, then put the start line at 0 for the race start
    ds = np.diff(s); ds = (ds + length / 2) % length - length / 2
    d = np.concatenate([[s[0]], s[0] + np.cumsum(ds)])
    i0 = np.searchsorted(t, T_START); d -= length * round((d[i0] - (d[i0] % length if d[i0] % length < length / 2 else d[i0] % length - length)) / length)
    res[f"t{n}"] = t.astype(np.float32); res[f"x{n}"] = p[:, 0].astype(np.float32); res[f"y{n}"] = p[:, 1].astype(np.float32)
    res[f"d{n}"] = d.astype(np.float32); res[f"o{n}"] = off.astype(np.float16)
np.savez_compressed(out, **res)
print("length m", round(length), "rot", ang)
