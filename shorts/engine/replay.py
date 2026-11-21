"""Pixel Paddock RACE REPLAY engine: real OpenF1 position data, all cars on the real racing line.

Timeline = list of segments:
  card:  dict(frames, note=[...]) | dict(frames, grid=True, header=[...], mark=(..)) | dict(frames, board=True) | dict(frames, outro=True, text=[...])
  race:  dict(t0, t1, dur=seconds of video, live=True|False, cam=("over",) | ("car", "VER", px) | ("pack", ["HAM","LEC"], px),
              call=[(race_time, "VER", [(text, colour, scale)], "up"|"down")], labels=(...), win=True)
         live segments run at constant speed; fast-forward segments (live=False) blend their speed into the neighbours.
Everything on screen comes from the data files, story facts are listed in ../SOURCES_REPLAY.md.
"""
import os, sys, math, json, subprocess, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import map_recap as M
from map_recap import (tx, tw, ease, lerp, draw_car, TEAMS, team_col, shade, panel, INK, MUT, YEL, GRN, RED, BG, EDGE, PANEL,
                       SAFE_X0, SAFE_X1, SAFE_Y1, CX, NW, NH, SC, FPS, OUT, project, draw_map, apply_calls, podium_board, note_card,
                       grid_card, grid_slot, hud, SIZE, car_px, track_w, WARN)
from PIL import Image, ImageDraw

def hexcol(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def livery(h):
    c = hexcol(h); dk = tuple(int(v * .55) for v in c); lt = tuple(min(255, int(v * .6 + 255 * .4)) for v in c)
    return dict(fwing=dk, nose=c, pod=c, body=c, air=lt, rwing=dk)

class RTrack(M.Track):
    def __init__(self, C, length):
        self.pts = [tuple(p) for p in C]; self.n = len(self.pts); self.raw_len = self.length_m = length
        xs, ys = C[:, 0], C[:, 1]
        self.cx, self.cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        self.fit = min((SAFE_X1 - SAFE_X0 - 10) / np.ptp(xs), 100 / np.ptp(ys))

class Race:
    def __init__(self, data_dir, npz):
        J = lambda n: json.load(open(f"{data_dir}/{n}.json"))
        self.T0 = dt.datetime.fromisoformat(open(f"{data_dir}/T0.txt").read().strip())
        ts = lambda s: (dt.datetime.fromisoformat(s) - self.T0).total_seconds(); self.ts = ts
        Z = np.load(npz); self.Z = Z
        self.tr = RTrack(Z["track"], float(Z["length"]))
        dr = J("drivers"); self.dr = {d["name_acronym"]: d for d in dr}
        self.num = {d["name_acronym"]: d["driver_number"] for d in dr}
        for d in dr:
            key = "T26_" + d["team_name"].replace(" ", "")[:10]
            TEAMS.setdefault(key, livery(d["team_colour"])); d["_team"] = key
        self.cars = list(self.num)
        self.t = {c: Z[f"t{self.num[c]}"].astype(float) for c in self.cars}
        self.x = {c: Z[f"x{self.num[c]}"].astype(float) for c in self.cars}
        self.y = {c: Z[f"y{self.num[c]}"].astype(float) for c in self.cars}
        self.d = {c: Z[f"d{self.num[c]}"].astype(float) for c in self.cars}
        # official running order (timing lines) and intervals
        acr = {v: k for k, v in self.num.items()}
        self.pos_ev = sorted([(ts(p["date"]), acr[p["driver_number"]], p["position"]) for p in J("position")])
        self.int_ev = {}
        for i in J("intervals"):
            self.int_ev.setdefault(acr[i["driver_number"]], []).append((ts(i["date"]), i["interval"]))
        for c in self.int_ev: self.int_ev[c].sort()
        self.lap_starts = {}
        for l in J("laps"):
            if l["date_start"]: self.lap_starts.setdefault(acr[l["driver_number"]], []).append(ts(l["date_start"]))
        for c in self.lap_starts: self.lap_starts[c].sort()
        self.laps = max(l["lap_number"] for l in J("laps"))
        self.result = sorted(J("session_result"), key=lambda r: r["position"] or 99)
        self.acr = acr
        # retirements: hide a DNF car 30 s after it last moved
        self.gone_at = {}
        for r in self.result:
            if r.get("dnf"):
                c = acr[r["driver_number"]]; t, d = self.t[c], self.d[c]
                v = np.gradient(d, t); mv = np.where(v > 5)[0]
                self.gone_at[c] = t[mv[-1]] + 30 if len(mv) else 0
        self.sc = [(3846, 3962), (7502, 7905)]       # filled per race in the config
        self.heading = {c: 0.0 for c in self.cars}

    def at(self, c, t):
        tt = self.t[c]; x = np.interp(t, tt, self.x[c]); y = np.interp(t, tt, self.y[c])
        x0, y0 = np.interp(t - .35, tt, self.x[c]), np.interp(t - .35, tt, self.y[c])
        x1, y1 = np.interp(t + .35, tt, self.x[c]), np.interp(t + .35, tt, self.y[c])
        if math.hypot(x1 - x0, y1 - y0) > .6: self.heading[c] = math.atan2(y1 - y0, x1 - x0)
        return x, y, self.heading[c]
    def order(self, t):
        cur = {}
        for te, c, p in self.pos_ev:
            if te > t: break
            cur[c] = p
        return [c for c, p in sorted(cur.items(), key=lambda kv: kv[1])]
    def interval(self, c, t):
        ev = self.int_ev.get(c, []); v = None
        for te, val in ev:
            if te > t: break
            v = val
        return v
    def lap(self, c, t):
        return max(1, min(self.laps, sum(1 for s in self.lap_starts.get(c, []) if s <= t)))
    def visible(self, c, t):
        return not (c in self.gone_at and t > self.gone_at[c])

# ---------------- drawing helpers ----------------
def tower(im, R, t, n=5):
    order = R.order(t)[:n]
    if not order: return im, []
    h = 6 + n * 9
    im = shade(im, (SAFE_X0, 24, SAFE_X0 + 56, 24 + h), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, 24, SAFE_X0 + 55, 24 + h - 1], outline=EDGE)
    for i, c in enumerate(order):
        y = 28 + i * 9
        tx(d, SAFE_X0 + 3, y, str(i + 1), YEL if i == 0 else MUT)
        d.rectangle([SAFE_X0 + 9, y, SAFE_X0 + 10, y + 4], fill=team_col(R.dr[c]["_team"]))
        tx(d, SAFE_X0 + 13, y, c, INK)
        if i > 0:
            iv = R.interval(c, t)
            s = f"+{iv:.1f}" if isinstance(iv, (int, float)) and iv < 60 else ""
            tx(d, SAFE_X0 + 53 - tw(s), y, s, MUT)
    av = [("_tower", SAFE_X0 + 28, 24 + h * k / 3, 30) for k in range(4)]
    return im, av

def sc_banner(im, fr, text="SAFETY CAR", col=YEL):
    d = ImageDraw.Draw(im); on = (fr // 10) % 2 == 0
    d.rectangle([SAFE_X0 + 60, 9, SAFE_X1 - 2, 18], fill=col if on else tuple(int(v * .4) for v in col))
    tx(d, (SAFE_X0 + 60 + SAFE_X1 - 2) // 2 - tw(text) // 2, 11, text, (10, 10, 10) if on else col)

# ---------------- timeline ----------------
def hermite(u, t0, t1, dur, v0, v1):
    V = (t1 - t0) / dur; v0 = min(v0, 2.8 * V); v1 = min(v1, 2.8 * V)
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
    return h00 * t0 + h10 * dur * v0 + h01 * t1 + h11 * dur * v1

def plan(segs):
    """frames and race time per frame for race segments"""
    for i, sg in enumerate(segs):
        if "t0" not in sg: continue
        F = max(2, int(round(sg["dur"] * FPS))); sg["frames"] = F
        speed = lambda s: (s["t1"] - s["t0"]) / s["dur"]
        if sg.get("live"): sg["times"] = np.linspace(sg["t0"], sg["t1"], F, endpoint=False)
        else:
            prv = segs[i - 1] if i > 0 and "t0" in segs[i - 1] and abs(segs[i - 1]["t1"] - sg["t0"]) < 1 else None
            nxt = segs[i + 1] if i + 1 < len(segs) and "t0" in segs[i + 1] and abs(segs[i + 1]["t0"] - sg["t1"]) < 1 else None
            v0 = speed(prv) if prv else 0; v1 = speed(nxt) if nxt else 0
            u = np.arange(F) / F
            sg["times"] = hermite(u, sg["t0"], sg["t1"], sg["dur"], v0, v1)
        sg["call_f"] = []
        for tc, tgt, lines, side in sg.get("call", ()):
            f = int(np.searchsorted(sg["times"], tc)); sg["call_f"].append((min(f, F - 1), tgt, lines, side))
        sg["laps"] = (0, 1)          # engine sound bed in make_audio

def render(R, segs, name, audio_tag):
    plan(segs)
    tr = R.tr; SIZE.update(track_m=R.track_m, car_m=R.car_m, fit=tr.fit)
    total = sum(s["frames"] for s in segs)
    aud_segs = []
    for sg in segs:
        a = {k: v for k, v in sg.items() if k not in ("times", "call", "call_f", "board", "grid")}
        if "call_f" in sg: a["call"] = sg["call_f"]
        if sg.get("board"): a["board"] = ("", R.podium_rows, [])
        aud_segs.append(a)
    wav = M.make_audio(audio_tag)(aud_segs, total)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    over = (tr.cx, tr.cy - 8 / tr.fit, 1.0)
    cam = over; snaps = []; WARN.clear()
    for si, sg in enumerate(segs):
        F = sg["frames"]
        if "t0" not in sg:
            for fr in range(F):
                im = Image.new("RGB", (NW, NH), BG)
                if sg.get("note"): im = note_card(im, tr, sg["note"], fr)
                elif sg.get("grid"):
                    rows = R.grid_rows
                    im = grid_card(im, tr, rows, fr)
                    if sg.get("mark") and fr > 20 and (fr // 8) % 2 == 0:
                        d = ImageDraw.Draw(im)
                        for m_ in sg["mark"]:
                            x_, y_ = grid_slot(rows, m_); x0_ = x_ - 32 if m_ % 2 else x_ - 6
                            d.rectangle([x0_, y_ - 4, x0_ + 38, y_ + 4], outline=YEL)
                    if sg.get("header"):
                        im = panel(im, [(t, c, s_) if fr >= 4 + i * 14 else ("", c, s_) for i, (t, c, s_) in enumerate(sg["header"])], y0=24)
                elif sg.get("board"): im = podium_board(im, tr, "RESULT", R.podium_rows, sg.get("extra", []), fr)
                elif sg.get("outro"):
                    draw_map(im, tr, over, dim=.5)
                    im = panel(im, [(t, c, s_) if fr >= 6 + i * 14 else ("", c, s_) for i, (t, c, s_) in enumerate(sg["text"])], y0=70)
                    if fr > 40: d = ImageDraw.Draw(im); tx(d, CX - tw("THE PIXEL PADDOCK") // 2, 130, "THE PIXEL PADDOCK", GRN)
                if fr == F - 4: snaps.append(im)
                p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
            cam = over
            continue
        cam_start = cam
        for fr in range(F):
            t = float(sg["times"][fr])
            spec = sg.get("cam", ("over",))
            if spec[0] == "over": tgt = over
            else:
                cs = [spec[1]] if spec[0] == "car" else spec[1]
                pts = [R.at(c, t)[:2] for c in cs]
                px_ = spec[2]; z = px_ / (R.car_m * tr.fit)
                tgt = (sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts), z)
            k = ease(min(1, fr / 22))
            cam = (lerp(cam_start[0], tgt[0], k), lerp(cam_start[1], tgt[1], k), math.exp(lerp(math.log(cam_start[2]), math.log(tgt[2]), k)))
            sc_on = any(a <= t < b for a, b in R.sc)
            im = Image.new("RGB", (NW, NH), BG)
            d = draw_map(im, tr, cam, sc_on=sc_on)
            z = cam[2]; px = car_px(z); anchors = {}; avoid = []
            order = R.order(t)
            for c in sorted(R.cars, key=lambda c: -order.index(c) if c in order else -99):
                if not R.visible(c, t): continue
                x, y, h = R.at(c, t)
                sx, sy = project(tr, cam, (x, y)); anchors[c] = (sx, sy)
                if not (-20 < sx < NW + 20 and -20 < sy < NH + 20): continue
                col = team_col(R.dr[c]["_team"])
                if px < 8:
                    d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=col)
                else:
                    draw_car(d, sx, sy, h, R.dr[c]["_team"], px); avoid.append((c, sx, sy, px * .55))
                    if c in sg.get("labels", ()):
                        lx, ly = int(sx) - tw(c) // 2, int(sy) - int(px * .6) - 8
                        tx(d, lx + 1, ly + 1, c, (6, 8, 16)); tx(d, lx, ly, c, INK); avoid.append((c, sx, ly + 2, tw(c) / 2 + 1))
            leader = order[0] if order else R.cars[0]
            im = hud(im, R.lap(leader, t), R.laps, R.dr[leader]["last_name"].upper(), R.dr[leader]["_team"])
            if sc_on: sc_banner(im, fr)
            if sg.get("red"): sc_banner(im, fr, "RED FLAG", RED)
            if not sg.get("notower"):
                im, av = tower(im, R, t); avoid += av
            sgc = {"call": sg["call_f"], "_place": sg.setdefault("_place", {})}
            im = apply_calls(im, sgc, fr, anchors, avoid, (name, si))
            if fr == F - 4: snaps.append(im)
            p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", round(total / FPS, 1))
    for (v, sgi, msg), n in sorted(WARN.items()):
        if v == name: print(f"  CHECK seg {sgi}: {msg} ({n} frames)")
