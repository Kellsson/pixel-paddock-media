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

def load_lap(raw, code, num, lap):
    T0 = dt.datetime.fromisoformat(lap["date_start"])
    ts = lambda s: (dt.datetime.fromisoformat(s) - T0).total_seconds()
    loc = json.load(open(f"{raw}/{code}_location.json")); cd = json.load(open(f"{raw}/{code}_car_data.json"))
    t = np.array([ts(x["date"]) for x in loc]); p = np.array([[x["x"], x["y"]] for x in loc], float) * .1
    ct = np.array([ts(x["date"]) for x in cd]); v = np.array([x["speed"] for x in cd], float)
    secs = [lap["duration_sector_1"], lap["duration_sector_2"], lap["duration_sector_3"]]
    return dict(code=code, t=t, p=p, ct=ct, v=v, secs=secs, lap=lap["lap_duration"])

def build(raw, a_code, b_code):
    D = {d["name_acronym"]: d for d in json.load(open(f"{raw}/drivers.json"))}
    L = json.load(open(f"{raw}/laps.json"))
    cars = []
    for c in (a_code, b_code):
        n = D[c]["driver_number"]; best = min([l for l in L if l["driver_number"] == n and l["lap_duration"]], key=lambda l: l["lap_duration"])
        cars.append(load_lap(raw, c, n, best))
    # centre line from both laps (only samples inside the lap), resampled + smoothed
    pts = np.vstack([c["p"][(c["t"] >= 0) & (c["t"] <= c["lap"])] for c in cars])
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
        c.update(P=P, d=d)
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
    return D, cars, Cs, length, dsec

class Duel:
    def __init__(self, raw, a, b):
        self.D, self.cars, C, self.length, self.dsec = build(raw, a, b)
        self.tr = RTrack(C, self.length)
        for c in self.cars:
            k = "T26_" + self.D[c["code"]]["team_name"].replace(" ", "")[:10]
            TEAMS.setdefault(k, livery(self.D[c["code"]]["team_colour"])); c["team"] = k
    def dist(self, c, t): return float(np.interp(t, c["Tgrid"], c["dgrid"]))
    def pose(self, c, t):
        d = self.dist(c, t); tm = np.interp(d, c["d"], c["t"])
        x = np.interp(tm, c["t"], c["P"][:, 0]); y = np.interp(tm, c["t"], c["P"][:, 1])
        x1 = np.interp(tm + .3, c["t"], c["P"][:, 0]); y1 = np.interp(tm + .3, c["t"], c["P"][:, 1])
        x0 = np.interp(tm - .3, c["t"], c["P"][:, 0]); y0 = np.interp(tm - .3, c["t"], c["P"][:, 1])
        return x, y, math.atan2(y1 - y0, x1 - x0), float(np.interp(tm, c["ct"], c["v"])), d
    def delta(self, t):
        """+ : car B is behind car A by this many seconds (at A's current position)"""
        A, B = self.cars
        if t >= min(A["lap"], B["lap"]): return B["lap"] - A["lap"]     # someone has finished: official gap
        return float(np.interp(self.dist(A, t), B["dgrid"], B["Tgrid"])) - t

# ---------------- drawing ----------------
def duel_hud(im, du, t, speeds):
    A, B = du.cars; dl = du.delta(t)
    lead, gap = (A, dl) if dl >= 0 else (B, -dl)
    im = shade(im, (SAFE_X0, 7, SAFE_X1, 27), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 7, SAFE_X1 - 1, 26], outline=EDGE)
    if gap < .05:      # below what ~3.7 Hz position data can resolve between the sector lines: call it level
        tx(d, SAFE_X0 + 4, 11, "GAP", MUT); tx(d, SAFE_X1 - 6 - tw("LEVEL", 3), 10, "LEVEL", INK, 3)
    else:
        tx(d, SAFE_X0 + 4, 11, "AHEAD", MUT)
        d.rectangle([SAFE_X0 + 4, 18, SAFE_X0 + 5, 22], fill=team_col(lead["team"])); tx(d, SAFE_X0 + 8, 18, lead["code"], INK)
        s = f"{gap:.2f}"; tx(d, SAFE_X1 - 6 - tw(s, 3), 10, s, GRN, 3)
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

# ---------------- render ----------------
def render_duel(du, plan, name, cards_before, cards_after, calls, mood_split=None):
    import subprocess, wave, music
    tr = du.tr; SIZE.update(track_m=du.track_m, car_m=du.car_m, fit=tr.fit); apply_brand(); M.HIRES = []
    globals().update({k: getattr(M, k) for k in ('INK', 'MUT', 'YEL', 'GRN', 'RED', 'EDGE', 'PANEL', 'BG')})
    # lap-time per frame from piecewise speeds [(t_end, speed)]
    times = []; t = plan[0][0]
    for t_end, sp in plan[1:]:
        while t < t_end: times.append(t); t += sp / FPS
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
                big = brand_card(fr, du, s["brand"], s.get("chip"), s.get("track", True), s.get("follow", False), s.get("logo", True))
                M.HIRES = []; p.stdin.write(big.tobytes())
                if fr == F - 4: snaps.append(big.resize((NW, NH), Image.NEAREST))
                continue
            im = Image.new("RGB", (NW, NH), BG)
            if s.get("note"): im = note_card(im, tr, s["note"], fr)
            elif s.get("table"): im = sector_table(im, du, fr)
            elif s.get("duel"):
                t = float(times[fr]); poses = [du.pose(c, t) for c in du.cars]
                mid = ((poses[0][0] + poses[1][0]) / 2, (poses[0][1] + poses[1][1]) / 2)
                z = du.zoom_px / (du.car_m * tr.fit); cam = (mid[0], mid[1], z)
                d = draw_map(im, tr, cam); px = car_px(z); anchors = {}; avoid = []; placed = []
                for k_, dd in enumerate(du.dsec[1:3]):                       # sector lines on track
                    i = int(dd / du.length * tr.n) % tr.n; a_, b_ = tr.pts[i], tr.pts[(i + 3) % tr.n]
                    h = math.atan2(b_[1] - a_[1], b_[0] - a_[0]) + math.pi / 2; sx, sy = project(tr, cam, a_)
                    hw = track_w(z) / 2
                    for q in range(-int(hw), int(hw) + 1, 2): d.point((sx + math.cos(h) * q, sy + math.sin(h) * q), fill=MUT)
                for c, (x, y, h, v, dd) in sorted(zip(du.cars, poses), key=lambda cp: cp[1][4]):
                    sx, sy = project(tr, cam, (x, y))
                    side = 1 if c is du.cars[0] else -1                 # ghost duel: each car keeps its own half of the track
                    o = track_w(z) * .2 * side; sx += -math.sin(h) * o; sy += math.cos(h) * o
                    anchors[c["code"]] = (sx, sy)
                    draw_car(d, sx, sy, h, c["team"], px); avoid.append((c["code"], sx, sy, px * .55))
                    lx, ly = int(sx) - tw(c["code"]) // 2, int(sy) - int(px * .6) - 8
                    for _ in range(3):
                        if any(abs(lx - a) < tw(c["code"]) + 2 and abs(ly - b) < 7 for a, b in placed): ly -= 7
                    placed.append((lx, ly)); tx(d, lx, ly, c["code"], INK); avoid.append((c["code"], sx, ly + 2, 8))
                im, av = duel_hud(im, du, t, [pp[3] for pp in poses]); avoid += av
                im, av = minimap(im, du, t); avoid += av
                im = apply_calls(im, {"call": s["call"], "_place": s.setdefault("_place", {})}, fr, anchors, avoid, (name, si))
            if fr == F - 4: snaps.append(im)
            p.stdin.write(finish_frame(im).tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", round(total / FPS, 1))
