"""Pixel Paddock QUALI DUEL: two fastest laps from OpenF1 run side by side (ghost duel).

Accuracy: lap and sector times are official (ms). Positions/telemetry come at ~3.7 Hz; each car's time-over-distance
curve is pinned to its official sector times, so the delta is exact at every sector line and interpolated between them.
"""
import os, sys, math, json, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay as RP
from replay import *            # brand, fonts, finish_frame, brand_card, RTrack, livery ...
import map_recap as M
from PIL import Image, ImageDraw

def gsmooth(y, sig):
    k = np.arange(-int(3 * sig), int(3 * sig) + 1); w = np.exp(-.5 * (k / sig) ** 2); w /= w.sum()
    yp = np.concatenate([np.full(len(k) // 2, y[0]), y, np.full(len(k) // 2, y[-1])])
    return np.convolve(yp, w, "valid")

def load_lap(raw, code, num, lap):
    T0 = dt.datetime.fromisoformat(lap["date_start"])
    ts = lambda s: (dt.datetime.fromisoformat(s) - T0).total_seconds()
    loc = json.load(open(f"{raw}/{code}_location.json")); cd = json.load(open(f"{raw}/{code}_car_data.json"))
    t = np.array([ts(x["date"]) for x in loc]); p = np.array([[x["x"], x["y"]] for x in loc], float) * .1
    ct = np.array([ts(x["date"]) for x in cd]); v = np.array([x["speed"] for x in cd], float)
    ch = {k: np.array([x[k] for x in cd], float) for k in ("n_gear", "throttle", "brake", "rpm", "drs")}
    secs = [lap["duration_sector_1"], lap["duration_sector_2"], lap["duration_sector_3"]]
    return dict(code=code, t=t, p=p, ct=ct, v=v, secs=secs, lap=lap["lap_duration"], ch=ch, T0=T0)

def build(raw, a_code, b_code, extra=None):
    D = {d["name_acronym"]: d for d in json.load(open(f"{raw}/drivers.json"))}
    L = json.load(open(f"{raw}/laps.json"))
    cars = []
    for c in (a_code, b_code):
        n = D[c]["driver_number"]; best = min([l for l in L if l["driver_number"] == n and l["lap_duration"]], key=lambda l: l["lap_duration"])
        cars.append(load_lap(raw, c, n, best))
    # centre line from both laps (only samples inside the lap), resampled + smoothed
    pts = np.vstack([c["p"][(c["t"] >= 0) & (c["t"] <= c["lap"])] for c in cars] + ([extra] if extra is not None else []))
    A = cars[0]["p"][(cars[0]["t"] >= 0) & (cars[0]["t"] <= cars[0]["lap"])]
    def resample(P, n, closed=True):
        Q = np.vstack([P, P[:1]]) if closed else P
        seg = np.sqrt((np.diff(Q, axis=0) ** 2).sum(1)); cum = np.concatenate([[0], np.cumsum(seg)])
        s = np.linspace(0, cum[-1], n, endpoint=False)
        return np.stack([np.interp(s, cum, Q[:, 0]), np.interp(s, cum, Q[:, 1])], 1), cum[-1]
    R0, _ = resample(A, 1500)
    idx = np.argmin(((pts[:, None, :] - R0[None, ::2, :]) ** 2).sum(-1), axis=1) * 2
    acc = np.zeros((1500, 2)); cnt = np.zeros(1500)
    np.add.at(acc, idx, pts); np.add.at(cnt, idx, 1)
    C = np.where(cnt[:, None] > 0, acc / np.maximum(cnt, 1)[:, None], R0)
    for _ in range(4): C = (np.roll(C, 1, 0) + 2 * C + np.roll(C, -1, 0)) / 4
    C, length = resample(C, 1500)
    # rotate for portrait
    best = None
    for ang in range(0, 180, 3):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang)); Rm = np.array([[ca, -sa], [sa, ca]])
        Q = C @ Rm.T; w, h = np.ptp(Q, 0); sc = min(108 / w, 100 / h)
        if best is None or sc > best[0]: best = (sc, Rm)
    Rm = best[1]; tf = lambda Q: (lambda Z: np.stack([Z[:, 0], -Z[:, 1]], 1))(Q @ Rm.T)
    Cs = tf(C)
    # start line = car A at t=0
    sA = np.array([np.interp(0, cars[0]["t"], tf(cars[0]["p"])[:, k]) for k in (0, 1)])
    i0 = int(np.argmin(((Cs - sA) ** 2).sum(1))); Cs = np.roll(Cs, -i0, 0)
    for c in cars:
        P = tf(c["p"]); j = np.argmin(((P[:, None, :] - Cs[None, ::2, :]) ** 2).sum(-1), axis=1) * 2
        s = j / len(Cs) * length; ds = np.diff(s); ds = (ds + length / 2) % length - length / 2
        d = np.concatenate([[s[0]], s[0] + np.cumsum(ds)])
        d -= length * round(np.interp(0, c["t"], d) / length)
        d = np.maximum.accumulate(d)                     # never backwards
        # smooth: projection steps (~8 m) and 3.7 Hz sampling make d(t) jagged -> uniform 20 Hz grid + gaussian (0.35 s)
        tg = np.arange(c["t"][0], c["t"][-1], .05); dg = gsmooth(np.interp(tg, c["t"], d), 7)
        c.update(P=P, t_raw=c["t"], d_raw=d, t=tg, d=np.maximum.accumulate(dg))
        c["v"] = gsmooth(c["v"], 1.5)
    # sector lines: distance where each car's measured time equals its official split, averaged over both cars
    cum = lambda c, k: sum(c["secs"][:k])
    dsec = [0.0]
    for k in (1, 2):
        dsec.append(float(np.mean([np.interp(cum(c, k), c["t"], c["d"]) for c in cars])))
    dsec.append(length)
    for c in cars:   # official time at distance: piecewise mapping pinned to the official splits
        tm = lambda dd: np.interp(dd, c["d"], c["t"])
        def T(dd, c=c, tm=tm):
            dd = np.asarray(dd, float); out = np.zeros_like(dd)
            for k in range(3):
                a, b = dsec[k], dsec[k + 1]; m = (dd >= a) & (dd <= b) if k < 2 else (dd >= a)
                ta, tb = tm(a), tm(b); oa = cum(c, k); ob = cum(c, k + 1)
                out[m] = oa + (tm(dd[m]) - ta) * (ob - oa) / max(1e-6, tb - ta)
            out[dd < 0] = tm(dd[dd < 0]); return out
        c["T"] = T
        dd = np.linspace(-200, length + 200, 6000); c["dgrid"] = dd; c["Tgrid"] = T(dd)
        c["Tgrid"] = np.maximum.accumulate(c["Tgrid"])
    return D, cars, Cs, length, dsec, tf

class Duel:
    """Both laps are drawn on the SAME smoothed centre line at their own distance -> a true overlay (ghost) comparison."""
    def __init__(self, raw, a, b, extra=None):
        self.raw = raw
        self.D, self.cars, C, self.length, self.dsec, self.tf = build(raw, a, b, extra)
        self.C = C; self.tr = RTrack(C, self.length); self.extra = []; self.landmarks = []
        for c in self.cars:
            k = "T26_" + self.D[c["code"]]["team_name"].replace(" ", "")[:10]
            TEAMS.setdefault(k, livery(self.D[c["code"]]["team_colour"])); c["team"] = k
        A, B = self.cars                                 # delta on a fine time grid, lightly smoothed (display only)
        self.tg = np.arange(0, min(A["lap"], B["lap"]), .05)
        dl = np.array([float(np.interp(self.dist(A, t), B["dgrid"], B["Tgrid"])) - t for t in self.tg])
        self.dl = gsmooth(dl, 5)
    def at(self, d):
        """point + heading on the centre line at distance d"""
        n = len(self.C); f = (d % self.length) / self.length * n
        i = int(f) % n; j = (i + 1) % n; u = f - int(f); p = self.C[i] * (1 - u) + self.C[j] * u
        a_, b_ = self.C[(i - 2) % n], self.C[(i + 3) % n]
        return p[0], p[1], math.atan2(b_[1] - a_[1], b_[0] - a_[0])
    def dist(self, c, t): return float(np.interp(t, c["Tgrid"], c["dgrid"]))
    def pose(self, c, t):
        d = self.dist(c, t); x, y, h = self.at(d); tm = np.interp(d, c["d"], c["t"])
        return x, y, h, float(np.interp(tm, c["ct"], c["v"])), d
    def delta(self, t):
        """+ : car B is behind car A by this many seconds (at A's current position)"""
        A, B = self.cars
        if t >= min(A["lap"], B["lap"]): return B["lap"] - A["lap"]     # someone has finished: official gap
        return float(np.interp(t, self.tg, self.dl))
    def add_tow(self, ref_code, pkl, code, show):
        """another car on track during ref's real lap (from all-car location data), placed at its real distance gap"""
        import pickle
        c = next(c for c in self.cars if c["code"] == ref_code); t, p = pickle.load(open(pkl, "rb"))[code]
        P = self.tf(p * 1.0); j = np.argmin(((P[:, None, :] - self.C[None, ::2, :]) ** 2).sum(-1), axis=1) * 2
        s_ = j / len(self.C) * self.length
        dr = np.interp(t, c["t_raw"], c["d_raw"]) % self.length
        gap = (s_ - dr + self.length / 2) % self.length - self.length / 2          # metres ahead of ref (real)
        tg = np.arange(t[0], t[-1], .05); gap = gsmooth(np.interp(tg, t, gap), 10)
        self.extra.append(dict(code=code, ref=c, tg=tg, gap=gap, show=show))
    def extra_pose(self, e, t):
        g = float(np.interp(t, e["tg"], e["gap"])); d = self.dist(e["ref"], t) + g
        return (*self.at(d), d, g)

# ---------------- drawing ----------------
def landmarks_from_geo(du, geojson, places):
    """align a circuit outline (lon/lat GeoJSON) to our data centre line (best similarity transform over start offset
    and direction) and map real landmark coordinates {name: (lon, lat)} into track space. Returns rms fit error (m)."""
    js = json.load(open(geojson)); co = np.array(js["features"][0]["geometry"]["coordinates"])
    lat0 = co[:, 1].mean(); toM = lambda ll: np.stack([ll[:, 0] * math.cos(math.radians(lat0)) * 111320, -ll[:, 1] * 110540], 1)
    def rs(P, n):
        Q = np.vstack([P, P[:1]]); seg = np.sqrt((np.diff(Q, axis=0) ** 2).sum(1)); cum = np.concatenate([[0], np.cumsum(seg)])
        s = np.linspace(0, cum[-1], n, endpoint=False); return np.stack([np.interp(s, cum, Q[:, 0]), np.interp(s, cum, Q[:, 1])], 1)
    n = 300; A = rs(du.C, n); G = toM(co); best = None
    for flip in (1, -1):
        Gb = rs(G[::flip], n)
        for k in range(0, n, 2):
            Bp = np.roll(Gb, -k, 0); ma, mb = A.mean(0), Bp.mean(0); X, Y = Bp - mb, A - ma
            U, S, Vt = np.linalg.svd(Y.T @ X); Dm = np.diag([1, np.sign(np.linalg.det(U @ Vt))]); Rm = U @ Dm @ Vt
            sc = (S * np.diag(Dm)).sum() / (X ** 2).sum(); err = ((Y - sc * X @ Rm.T) ** 2).sum(1).mean()
            if best is None or err < best[0]: best = (err, Rm, sc, ma, mb)
    err, Rm, sc, ma, mb = best
    for name, ll in places.items():
        q = (toM(np.array([ll])) - mb) * sc @ Rm.T + ma
        du.landmarks.append(dict(name=name, p=q[0]))
    return math.sqrt(err)

WATER, WATER_LT, SPH_DK = (30, 50, 62), (58, 92, 108), (36, 32, 40)
def draw_landmarks(im, du, cam, fr, avoid):
    """real landmarks next to the circuit, at real scale (Sphere: 157 m wide; Bellagio lake ~ 300 m long)"""
    d = ImageDraw.Draw(im); s = du.tr.fit * cam[2]
    for L in du.landmarks:
        sx, sy = project(du.tr, cam, L["p"]); kind = L.get("kind", L["name"])
        if kind == "SPHERE":
            r = L.get("r_m", 78) * s
            if not (-r < sx < NW + r and -r < sy < NH + r): continue
            for yy in range(int(sy - r), int(sy + r) + 1, 2):        # LED dome: 2-px dots, rolling colour bands + light from top-left
                for xx in range(int(sx - r), int(sx + r) + 1, 2):
                    u, v = (xx - sx) / r, (yy - sy) / r; q = u * u + v * v
                    if q > 1: continue
                    z_ = math.sqrt(1 - q); lon = math.atan2(u, z_) + fr * .03; lat = math.asin(max(-1, min(1, v)))
                    band = int((lon * 2 + lat * 1.5) / math.pi * 3) % 6        # one green band rolling round a dim dome
                    col = GRN if band == 0 else (70, 64, 54); lt = .25 + .45 * max(0, (-u * .5 - v * .5 + z_) / 1.4)
                    d.rectangle([xx, yy, xx + 1, yy + 1], fill=tuple(int(c_ * lt + SPH_DK[i] * (1 - lt)) for i, c_ in enumerate(col)))
            lbl_y = sy + r + 3
        elif kind == "LAKE":
            w2, h2, ang = L["w_m"] / 2 * s, L["h_m"] / 2 * s, L["ang"]
            if not (-w2 < sx < NW + w2 and -w2 < sy < NH + w2): continue
            ca, sa = math.cos(ang), math.sin(ang)
            poly = [(sx + w2 * math.cos(a) * ca - h2 * math.sin(a) * sa, sy + w2 * math.cos(a) * sa + h2 * math.sin(a) * ca)
                    for a in np.linspace(0, 2 * math.pi, 40)]
            d.polygon(poly, fill=WATER)
            for k in range(-9, 10):                                   # fountain jets along the lake, a wave running through them
                ph = math.sin(fr * .25 - k * .7); u = k / 10 * w2 * .85
                jx, jy = sx + u * ca, sy + u * sa
                if ph > -.2:
                    rr = 1 + int(ph * 1.6); d.ellipse([jx - rr, jy - rr, jx + rr, jy + rr], fill=WATER_LT)
                    d.point((jx, jy), fill=INK)
            lbl_y = sy + h2 + 3
        else:
            if not (0 < sx < NW and 0 < sy < NH): continue
            lbl_y = sy
        lbl = L.get("label", L["name"]); lx = int(max(SAFE_X0 + 1, min(SAFE_X1 - 1 - tw(lbl), sx - tw(lbl) / 2)))
        if L.get("label", True): tx(d, lx, int(lbl_y), lbl, MUT); avoid.append(("_lm", sx, lbl_y + 2, tw(lbl) / 2 + 2))
    return d

def gap_ribbon(d, du, cam, d0, d1, col, z):
    """the stretch of track between the two cars, in the leading car's colour"""
    n = max(2, int((d1 - d0) / 1.5)); pts = []
    for k in range(n + 1):
        x, y, h = du.at(d0 + (d1 - d0) * k / n); pts.append(project(du.tr, cam, (x, y)) + (h,))
    d.line([(p[0], p[1]) for p in pts], fill=col, width=2)

def nose_line(d, du, cam, dd, col, z):
    """line across the track at the car's nose, in the car's colour"""
    x, y, h = du.at(dd); sx, sy = project(du.tr, cam, (x, y)); hw = track_w(z) / 2 - 1
    d.line([(sx - math.sin(h) * hw, sy + math.cos(h) * hw), (sx + math.sin(h) * hw, sy - math.cos(h) * hw)], fill=col, width=1)

def ghost_car(im, sx, sy, h, team, px, k):
    lay = im.copy(); draw_car(ImageDraw.Draw(lay), sx, sy, h, team, px); return Image.blend(im, lay, k)

def duel_hud(im, du, t, speeds, lead_i=None, gap_m=None):
    A, B = du.cars; dl = du.delta(t)
    if lead_i is None: lead_i = 0 if dl >= 0 else 1
    lead, gap = du.cars[lead_i], abs(dl)
    im = shade(im, (SAFE_X0, 7, SAFE_X1, 27), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 7, SAFE_X1 - 1, 26], outline=EDGE)
    if gap < .05:      # below what ~3.7 Hz position data can resolve between the sector lines: call it level
        tx(d, SAFE_X0 + 4, 11, "GAP", MUT); tx(d, SAFE_X1 - 6 - tw("LEVEL", 3), 10, "LEVEL", INK, 3)
    else:
        tx(d, SAFE_X0 + 4, 11, "AHEAD", MUT)
        d.rectangle([SAFE_X0 + 4, 18, SAFE_X0 + 5, 22], fill=team_col(lead["team"])); tx(d, SAFE_X0 + 8, 18, lead["code"], INK)
        s = f"{gap:.2f}"; tx(d, SAFE_X1 - 6 - tw(s, 3), 10, s, GRN, 3)
        if gap_m is not None and gap_m >= 1:
            m_ = f"{gap_m:.0f} M"; tx(d, SAFE_X0 + 28 - tw(m_) // 2 + 12, 18, m_, MUT)
    # driver rows: speed now
    y0 = TOW_Y; im = shade(im, (SAFE_X0, y0, SAFE_X0 + 56, y0 + 24), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, y0, SAFE_X0 + 55, y0 + 23], outline=EDGE)
    for i, (c, v) in enumerate(zip(du.cars, speeds)):
        y = y0 + 5 + i * 9
        d.rectangle([SAFE_X0 + 4, y, SAFE_X0 + 5, y + 4], fill=team_col(c["team"])); tx(d, SAFE_X0 + 8, y, c["code"], INK)
        s = f"{int(v)}"; tx(d, SAFE_X0 + 40 - tw(s), y, s, INK); tx(d, SAFE_X0 + 42, y, "KMH", MUT)
    return im, [("_hud", SAFE_X0 + 28, y0 + 12, 30)]

def minimap(im, du, t):
    """small whole-track map, top right, with both cars and the sector lines"""
    x0, y0, w, h = SAFE_X1 - 52, TOW_Y, 52, 40
    im = shade(im, (x0, y0, x0 + w, y0 + h), .15); d = ImageDraw.Draw(im); d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=EDGE)
    P = np.array(du.tr.pts[::6]); mn = P.min(0); s = min((w - 8) / np.ptp(P[:, 0]), (h - 8) / np.ptp(P[:, 1]))
    off = np.array([x0 + (w - np.ptp(P[:, 0]) * s) / 2, y0 + (h - np.ptp(P[:, 1]) * s) / 2])
    Q = (P - mn) * s + off; d.line([tuple(q) for q in Q] + [tuple(Q[0])], fill=(84, 76, 62), width=1)
    for k, dd in enumerate(du.dsec[:3]):
        i = int(dd / du.length * len(du.tr.pts)) % len(du.tr.pts); q = (np.array(du.tr.pts[i]) - mn) * s + off
        d.rectangle([q[0] - 1, q[1] - 1, q[0] + 1, q[1] + 1], fill=MUT if k else INK)
    for c in reversed(du.cars):
        x, y, *_ = du.pose(c, t); q = (np.array([x, y]) - mn) * s + off
        d.rectangle([q[0] - 1, q[1] - 1, q[0] + 1, q[1] + 1], fill=team_col(c["team"]))
    return im, [("_map", x0 + w / 2, y0 + h / 2, 30)]

def sector_table(im, du, fr, title="SECTORS"):
    A, B = du.cars; d = ImageDraw.Draw(im)
    draw_map(im, du.tr, (du.tr.cx, du.tr.cy, 1.0), dim=.2); im = shade(im, (0, 0, NW, NH), .45); d = ImageDraw.Draw(im)
    tx(d, CX - tw(title, 2) // 2, 40, title, INK, 2)
    cols = [SAFE_X0 + 36, SAFE_X0 + 70, SAFE_X0 + 104]
    for c, x in zip(du.cars, cols[:2]):
        d.rectangle([x - 12, 60, x - 11, 64], fill=team_col(c["team"])); tx(d, x - 8, 60, c["code"], INK)
    tx(d, cols[2] - 8, 60, "GAP", MUT)
    rows = [(f"S{k + 1}", A["secs"][k], B["secs"][k]) for k in range(3)] + [("LAP", A["lap"], B["lap"])]
    for i, (lbl, a, b) in enumerate(rows):
        if fr < 10 + i * 14: continue
        y = 74 + i * 16; last = lbl == "LAP"
        if last: d.line([(SAFE_X0 + 4, y - 5), (SAFE_X1 - 4, y - 5)], fill=EDGE)
        tx(d, SAFE_X0 + 4, y, lbl, MUT if not last else INK)
        fmt = lambda v: f"{int(v // 60)}:{v % 60:06.3f}" if v >= 60 else f"{v:.3f}"
        for v, x, win in ((a, cols[0], a < b), (b, cols[1], b < a)):
            s = fmt(v); tx(d, x + 14 - tw(s), y, s, GRN if win else INK)
        g = b - a; who = A if g > 0 else B; s = f"{abs(g):.3f}"
        d.rectangle([cols[2] - 12, y, cols[2] - 11, y + 4], fill=team_col(who["team"])); tx(d, cols[2] - 8, y, s, INK)
    return im

def title_cars(big, du, fr, y0):
    """both cars in their team colours under the title, sliding in from the sides, surname under each"""
    W = big.size[0]; d = ImageDraw.Draw(big); K = 7
    for i, c in enumerate(du.cars):
        k = ease(min(1, max(0, fr - 30 - i * 4) / 14))
        if k <= 0: continue
        sm = Image.new("RGB", (34, 34), PP["paper"]); draw_car(ImageDraw.Draw(sm), 17, 17, -math.pi / 2, c["team"], 30)
        car = sm.resize((34 * K, 34 * K), Image.NEAREST)
        mask = Image.fromarray((np.abs(np.asarray(car, int) - np.array(PP["paper"])).sum(2) > 6).astype(np.uint8) * 255)
        cx = int(W / 2 + (-1 if i == 0 else 1) * (W * .22 + (1 - k) * W * .5)); big.paste(car, (cx - 17 * K, y0), mask)
        name = du.D[c["code"]]["last_name"].upper(); col = team_col(c["team"])
        if k >= 1:
            ln = btext(big, name, "label", 4, PP["ink"], y0 + 34 * K + 40, cx)
            d.rectangle([cx - ln // 2, y0 + 34 * K + 70, cx + ln // 2, y0 + 34 * K + 77], fill=col)
    if fr >= 46: btext(big, "VS", "head", 6, PP["acc"], y0 + 17 * K)
    return big

# ---------------- render ----------------
def render_duel(du, plan, name, cards_before, cards_after, calls, mood_split=None, hold_s=0):
    import subprocess, wave, music
    TEAMS.setdefault("TOW_GREY", livery("8A8170"))
    tr = du.tr; SIZE.update(track_m=du.track_m, car_m=du.car_m, fit=tr.fit); apply_brand(); M.HIRES = []
    globals().update({k: getattr(M, k) for k in ('INK', 'MUT', 'YEL', 'GRN', 'RED', 'EDGE', 'PANEL', 'BG')})
    # lap-time per frame from piecewise speeds [(t_end, speed)]
    times = []; t = plan[0][0]
    for t_end, sp in plan[1:]:
        while t < t_end: times.append(t); t += sp / FPS
    # freeze when the first car crosses the line: both cars stop, gap is shown. Virtual time keeps running for the
    # fact boxes (a call at first_lap + x appears x seconds into the freeze).
    t_fin = min(c["lap"] for c in du.cars)
    times = [x for x in times if x < t_fin] + [t_fin + k / FPS for k in range(int(hold_s * FPS))] if hold_s else times
    times = np.array(times); F_duel = len(times)
    call_f = [(int(np.searchsorted(times, tc)), tgt, lines, side) + ((int(np.searchsorted(times, c_[4])),) if len(c_) > 4 else ())
              for c_ in calls for tc, tgt, lines, side in [c_[:4]]]
    segs = cards_before + [dict(frames=F_duel, duel=True, call=call_f)] + cards_after
    total = sum(s["frames"] for s in segs)
    aud = []
    for s in segs:
        a = {k: v for k, v in s.items() if k in ("note", "call", "board", "frames", "brand", "chip", "outro", "win")}
        if s.get("brand"): a["note"] = s["brand"]
        if s.get("table"): a["note"] = [1, 2, 3, 4]
        aud.append(a)
    wav = M.make_audio(name, motif=False)(aud, total)
    secs, acc = [], 0
    for i, s in enumerate(segs):
        if s.get("duel"):
            secs.append((acc / FPS, "race"))
            if mood_split: secs.append(((acc + int(np.searchsorted(times, mood_split))) / FPS, "finish"))
        else:
            secs.append((acc / FPS, s.get("mood", "title" if i == 0 else "outro" if i == len(segs) - 1 else "podium")))
        acc += s["frames"]
    song = music.song(total / FPS + 1, secs)
    with wave.open(wav) as w: fx = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32767
    n = min(len(fx), len(song)); mixd = np.tanh(fx[:n] * .9 + song[:n] * .55)
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(music.SR); w.writeframes((mixd * 32767 * .9).astype(np.int16).tobytes())
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-af", "volume=7dB,alimiter=limit=0.95",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    snaps = []; WARN.clear()
    for si, s in enumerate(segs):
        F = s["frames"]
        for fr in range(F):
            if s.get("brand"):
                big = brand_card(fr, du, s["brand"], s.get("chip"), s.get("track", True) and not s.get("cars"), s.get("follow", False), s.get("logo", True))
                if s.get("cars"): big = title_cars(big, du, fr, s["cars"])
                M.HIRES = []; p.stdin.write(big.tobytes())
                if fr == F - 4: snaps.append(big.resize((NW, NH), Image.NEAREST))
                continue
            im = Image.new("RGB", (NW, NH), BG)
            if s.get("note"): im = note_card(im, tr, s["note"], fr)
            elif s.get("table"): im = sector_table(im, du, fr)
            elif s.get("duel"):
                frozen = hold_s and times[fr] >= t_fin
                t = float(min(times[fr], t_fin - 1e-3) if hold_s else times[fr]); poses = [du.pose(c, t) for c in du.cars]
                dl = du.delta(t); want = 0 if dl >= 0 else 1
                if abs(dl) > .02 or s.get("_lead") is None: s["_lead"] = want if s.get("_lead") is None or abs(dl) > .02 else s["_lead"]
                li = s["_lead"]; gi = 1 - li
                mid = ((poses[0][0] + poses[1][0]) / 2, (poses[0][1] + poses[1][1]) / 2)
                z = du.zoom_px / (du.car_m * tr.fit)
                ez = ease((times[fr] - t_fin) / 1.2) if frozen else 0
                z *= 1 + 1.3 * ez                                              # zoom in on the gap at the line
                cam = (mid[0], mid[1] + 28 * ez / (tr.fit * z), z)             # and lift the cars to make room below
                d = draw_map(im, tr, cam); px = car_px(z); anchors = {}; avoid = []
                d = draw_landmarks(im, du, cam, fr, avoid)
                for k_, dd in enumerate(du.dsec[1:3]):                       # sector lines on track
                    x_, y_, h = du.at(dd); h += math.pi / 2; sx, sy = project(tr, cam, (x_, y_)); hw = track_w(z) / 2
                    for q in range(-int(hw), int(hw) + 1, 2): d.point((sx + math.cos(h) * q, sy + math.sin(h) * q), fill=MUT)
                x_, y_, h_ = du.at(0.0); fx_, fy_ = project(tr, cam, (x_, y_)); hw_ = track_w(z) / 2
                for q in range(-int(hw_), int(hw_) + 1):
                    for r_ in (0, 1):
                        cx_ = fx_ - math.sin(h_) * q + math.cos(h_) * r_; cy_ = fy_ + math.cos(h_) * q + math.sin(h_) * r_
                        d.point((cx_, cy_), fill=INK if (q + r_) % 2 else BG)
                gap_m = poses[li][4] - poses[gi][4]
                nose = du.car_m * .5
                if gap_m > .5: gap_ribbon(d, du, cam, poses[gi][4] + nose, poses[li][4] + nose, team_col(du.cars[li]["team"]), z)
                for e in du.extra:                                             # real car ahead on track (tow), faint
                    a0, a1 = e["show"]; k = min(1, (t - a0) / 1.5, (a1 - t) / 1.5)
                    if k <= 0: continue
                    x, y, h, dd, g = du.extra_pose(e, t); sx, sy = project(tr, cam, (x, y))
                    im = ghost_car(im, sx, sy, h, "TOW_GREY", px, .55 * k); d = ImageDraw.Draw(im)
                    if k > .5:
                        tx(d, int(sx) - tw(e["code"]) // 2, int(sy + px * .6) + 3, e["code"], MUT)
                        avoid.append((e["code"], sx, sy + px * .6 + 5, 8))
                    anchors[e["code"]] = (sx, sy); avoid.append((e["code"], sx, sy, px * .55))
                scr = {}
                for i in (gi, li):                                             # trailing car = ghost underneath, leader on top
                    c = du.cars[i]; x, y, h, v, dd = poses[i]; sx, sy = project(tr, cam, (x, y)); scr[i] = (sx, sy)
                    if i == gi: im = ghost_car(im, sx, sy, h, c["team"], px, .5); d = ImageDraw.Draw(im)
                    else: draw_car(d, sx, sy, h, c["team"], px)
                    anchors[c["code"]] = (sx, sy); avoid.append((c["code"], sx, sy, px * .55))
                for i in (gi, li): nose_line(d, du, cam, poses[i][4] + nose, team_col(du.cars[i]["team"]), z)
                if frozen and gap_m > 2:                                       # the loser's gap, measured on track
                    x_, y_, h_ = du.at((poses[gi][4] + poses[li][4]) / 2 + nose); mx, my = project(tr, cam, (x_, y_))
                    k_ = 1; lb = f"{gap_m:.0f} M"
                    nx_, ny_ = -math.sin(h_), math.cos(h_); off = track_w(z) / 2 + 8
                    if ny_ < 0: nx_, ny_ = -nx_, -ny_                             # label below the track (leader label sits above)
                    lx = int(mx - tw(lb, 2) / 2); ly = int(my + (track_w(z) / 2) / max(.35, abs(math.cos(h_))) + 5)
                    if ez > .5:
                        d.rectangle([lx - 3, ly - 3, lx + tw(lb, 2) + 2, ly + 12], fill=BG, outline=team_col(du.cars[li]["team"]))
                        tx(d, lx, ly, lb, INK, 2); avoid.append(("_gap", lx + tw(lb, 2) / 2, ly + 5, tw(lb, 2) / 2 + 4))
                # labels at a fixed screen offset: leader above its car, ghost below (no jitter, never on top of each other)
                for i, up in ((li, True), (gi, False)):
                    c = du.cars[i]; sx, sy = scr[i]; lx = int(round(sx)) - tw(c["code"]) // 2
                    ly = int(round(sy - px * .6 - 8)) if up else int(round(sy + px * .6 + 3))
                    d.rectangle([lx - 1, ly - 1, lx + tw(c["code"]), ly + 5], fill=BG)
                    tx(d, lx, ly, c["code"], INK if up else MUT); avoid.append((c["code"], sx, ly + 2, 8))
                im, av = duel_hud(im, du, t, [pp[3] for pp in poses], li, gap_m); avoid += av
                im, av = minimap(im, du, t); avoid += av
                im = apply_calls(im, {"call": s["call"], "_place": s.setdefault("_place", {})}, fr, anchors, avoid, (name, si))
            if fr == F - 4: snaps.append(im)
            p.stdin.write(finish_frame(im).tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", round(total / FPS, 1))
