"""Pixel Paddock F1 TRACK GUIDE: one real pole lap (OpenF1 position + telemetry) driven around a pixel map of the
circuit, with corner numbers, live speed / gear / throttle / brake, and real surroundings.

Accuracy: lap and sector times are official. Position and telemetry come at ~3.7 Hz; the car runs on the smoothed
centre line at its measured distance, pinned to the official sector times (same method as the quali duel).
Surroundings are only drawn where a source or the data backs them up (see SOURCES_GUIDE.md).
"""
import os, sys, math, json, datetime as dt, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import duel as DU
from duel import *                       # Duel, gsmooth, minimap, brand helpers, map helpers ...
import map_recap as M
from PIL import Image, ImageDraw

SAND, SAND_LT, GRASS, GRASS_LT = (31, 27, 20), (46, 40, 29), (40, 64, 34), (52, 82, 44)
POLE, GLOW = (236, 227, 207), (88, 80, 46)
ROOF, DOOR, STAND, STAND_LT = (58, 56, 54), (210, 190, 120), (54, 50, 58), (84, 78, 92)


class Guide(Duel):
    """one car; corners from the F1 timing map (MultiViewer), pit lane from pit-entry position data"""
    def __init__(self, raw, code, extra, corners_dm):
        super().__init__(raw, code, code, extra)
        self.cars = self.cars[:1]; self.car = self.cars[0]
        P = self.tf(np.array(corners_dm, float) * .1)
        self.corners = []
        for k, p in enumerate(P):
            j = int(np.argmin(((self.C - p) ** 2).sum(1))); s = j / len(self.C) * self.length
            a, b = self.at(s - 25)[2], self.at(s + 25)[2]; turn = (b - a + math.pi) % (2 * math.pi) - math.pi
            self.corners.append(dict(n=k + 1, s=s, side=-1 if turn > 0 else 1))   # tag on the outside of the corner
        self.pit = None; self.buildings = []; self.poles = []
    def lateral(self, P):
        """distance along + signed offset from the centre line (+ = left of travel direction)"""
        j = np.argmin(((P[:, None, :] - self.C[None, :, :]) ** 2).sum(-1), axis=1)
        s = j / len(self.C) * self.length; out = []
        for p, ss in zip(P, s):
            x, y, h = self.at(ss); out.append((p[0] - x) * -math.sin(h) + (p[1] - y) * math.cos(h))
        return s, np.array(out)
    def set_pitlane(self, P, min_off=9.0):
        s, o = self.lateral(P); m = np.abs(o) > min_off
        s, o = s[m], o[m]; s = np.where(s > self.length / 2, s - self.length, s)     # around the line: -x .. +x
        bins = np.arange(s.min(), s.max() + 20, 20); prof = []
        for a in bins:
            k = (s >= a) & (s < a + 20)
            if k.sum() >= 2: prof.append((a + 10, float(np.median(o[k]))))
        prof = np.array(prof); prof[:, 1] = gsmooth(prof[:, 1], 1.2)
        self.pit = prof; self.pit_side = float(np.sign(np.median(prof[:, 1])))
        return prof
    def off_pt(self, s, off):
        x, y, h = self.at(s); return np.array([x - math.sin(h) * off, y + math.cos(h) * off])


def strip(du, s0, s1, o0, o1, n=24):
    """polygon of a band beside the track between distances s0..s1 and lateral offsets o0..o1"""
    a = [du.off_pt(s, o0) for s in np.linspace(s0, s1, n)]; b = [du.off_pt(s, o1) for s in np.linspace(s1, s0, n)]
    return a + b


def draw_ground(im, du, cam, z, fr):
    """desert at night: sand, the artificial-grass band that keeps the sand off the track, pit lane + buildings"""
    tr = du.tr; w = track_w(z); s_px = tr.fit * z
    D = M.track_dist(tr, cam, w); a = np.asarray(im).copy()
    sand = D > w / 2 + du.grass_m * s_px
    a[sand] = SAND
    if du.grass_m > 0: a[~sand] = GRASS
    im.paste(Image.fromarray(a)); d = ImageDraw.Draw(im)
    hw, hh = NW / 2 / s_px + 10, NH / 2 / s_px + 10                    # sand grains anchored to the world (no flicker)
    for gx in range(int((cam[0] - hw) // 7), int((cam[0] + hw) // 7) + 1):
        for gy in range(int((cam[1] - hh) // 7), int((cam[1] + hh) // 7) + 1):
            hsh = (gx * 73856093 ^ gy * 19349663) & 0xffff
            if hsh % 5: continue
            sx, sy = project(tr, cam, (gx * 7 + (hsh % 7), gy * 7 + (hsh // 7) % 7))
            if 0 <= sx < NW and 0 <= sy < NH and D[int(sy), int(sx)] > w / 2 + du.grass_m * s_px + 1:
                d.point((sx, sy), fill=SAND_LT)
    if du.pit is not None:                                             # pit lane: asphalt beside the main straight
        pts = [project(tr, cam, du.off_pt(s, o)) for s, o in du.pit]
        d.line(pts, fill=M.THEME["asphalt"], width=max(2, int(du.pit_w * s_px)))
    for b in du.buildings:
        poly = [project(tr, cam, p) for p in b["poly"]]
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        if max(xs) < -5 or min(xs) > NW + 5 or max(ys) < -5 or min(ys) > NH + 5: continue
        d.polygon(poly, fill=b["fill"])
        if b["kind"] == "pits":                                        # one lit door per garage, facing the pit lane
            for s in np.linspace(b["s0"], b["s1"], b["doors"]):
                p = project(tr, cam, du.off_pt(s, b["door_off"])); d.point(p, fill=DOOR)
        if b["kind"] == "stand":                                       # seat rows + crowd specks
            for k in range(1, 4):
                o = b["o0"] + (b["o1"] - b["o0"]) * k / 4
                d.line([project(tr, cam, du.off_pt(s, o)) for s in np.linspace(b["s0"], b["s1"], 16)], fill=STAND_LT)
    return d


def draw_poles(d, du, cam, z, fr):
    for p in du.poles:
        sx, sy = project(du.tr, cam, p)
        if -3 < sx < NW + 3 and -3 < sy < NH + 3:
            d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=GLOW); d.point((sx, sy), fill=POLE)


def drs_lines(d, du, cam, z, avoid):
    """FIA DRS detection / activation lines across the track"""
    for s, col, lb in du.drs_marks:
        x_, y_, h_ = du.at(s); sx, sy = project(du.tr, cam, (x_, y_)); hw = track_w(z) / 2
        if not (-hw < sx < NW + hw and -hw < sy < NH + hw): continue
        for q in range(-int(hw), int(hw) + 1):
            if q % 3 != 2: d.point((sx - math.sin(h_) * q, sy + math.cos(h_) * q), fill=col)
        ox, oy = sx - math.sin(h_) * (hw + 8), sy + math.cos(h_) * (hw + 8)
        lx, ly = int(ox - tw(lb) / 2), int(oy - 2)
        if 2 < lx < NW - tw(lb) - 2 and 4 < ly < NH - 8:
            d.rectangle([lx - 2, ly - 2, lx + tw(lb) + 1, ly + 6], fill=BG, outline=col); tx(d, lx, ly, lb, col)
            avoid.append((lb, ox, oy, tw(lb) / 2 + 3))


def corner_tags(d, du, cam, z, avoid):
    s_px = du.tr.fit * z
    for c in du.corners:
        off = c["side"] * (du.track_m / 2 + du.grass_m + 14)
        sx, sy = project(du.tr, cam, du.off_pt(c["s"], off)); lb = f"T{c['n']}"
        if 4 < sx < NW - 4 and 4 < sy < NH - 4:
            lx, ly = int(sx - tw(lb) / 2), int(sy - 2)
            d.rectangle([lx - 2, ly - 2, lx + tw(lb) + 1, ly + 6], fill=BG, outline=EDGE); tx(d, lx, ly, lb, INK)
            avoid.append((lb, sx, sy, 7))


def guide_hud(im, du, t, lapt_txt, col):
    c = du.car; tm = float(np.interp(du.dist(c, t), c["d"], c["t"]))
    v = float(np.interp(tm, c["ct"], c["v"])); k = int(np.argmin(np.abs(c["ct"] - tm)))
    gear, thr, brk = int(c["ch"]["n_gear"][k]), float(np.interp(tm, c["ct"], c["ch"]["throttle"])), c["ch"]["brake"][k] > 0
    drs = c["ch"]["drs"][k] >= 10
    im = shade(im, (SAFE_X0, 7, SAFE_X1, 27), .15); d = ImageDraw.Draw(im); d.rectangle([SAFE_X0, 7, SAFE_X1 - 1, 26], outline=EDGE)
    d.rectangle([SAFE_X0 + 4, 11, SAFE_X0 + 5, 15], fill=team_col(c["team"])); tx(d, SAFE_X0 + 8, 11, c["code"], INK)
    if len(lapt_txt) <= 6: tx(d, SAFE_X0 + 4, 18, du.hud_sub, MUT)
    tx(d, SAFE_X1 - 6 - tw(lapt_txt, 3), 10, lapt_txt, col, 3)
    y0 = TOW_Y; W_ = 68; im = shade(im, (SAFE_X0, y0, SAFE_X0 + W_, y0 + 40), .15); d = ImageDraw.Draw(im)
    d.rectangle([SAFE_X0, y0, SAFE_X0 + W_ - 1, y0 + 39], outline=EDGE)
    s = f"{int(round(v))}"; tx(d, SAFE_X0 + 4, y0 + 5, s, INK, 3); tx(d, SAFE_X0 + 4 + tw(s, 3) + 2, y0 + 12, "KMH", MUT)
    d.rectangle([SAFE_X0 + 52, y0 + 4, SAFE_X0 + 64, y0 + 17], outline=EDGE); g = str(gear) if gear > 0 else "N"
    tx(d, SAFE_X0 + 58 - tw(g, 2) // 2, y0 + 7, g, YEL, 2)
    if getattr(du, "show_drs", False):                                  # DRS flap open (telemetry)
        d.rectangle([SAFE_X0 + 51, y0 + 24, SAFE_X0 + 64, y0 + 34], fill=GRN if drs else BG, outline=GRN if drs else EDGE)
        tx(d, SAFE_X0 + 52, y0 + 27, "DRS", BG if drs else MUT)
    for i, (lb, val, colr) in enumerate((("THR", thr / 100, GRN), ("BRK", 1.0 if brk else 0.0, RED))):
        y = y0 + 23 + i * 8; tx(d, SAFE_X0 + 4, y, lb, MUT); x1 = SAFE_X0 + 20
        bl = 28 if getattr(du, "show_drs", False) else 44
        d.rectangle([x1, y, x1 + bl, y + 4], outline=EDGE)
        if val > .02: d.rectangle([x1 + 1, y + 1, x1 + 1 + int((bl - 2) * val), y + 3], fill=colr)
    return im, [("_hud", SAFE_X0 + 31, y0 + 20, 34)]


def title_one(big, du, fr, y0, lines):
    """the car in team colours under the title, driver + lap below"""
    W = big.size[0]; d = ImageDraw.Draw(big); K = 7; c = du.car
    k = ease(min(1, max(0, fr - 30) / 14))
    if k > 0:
        sm = Image.new("RGB", (34, 34), PP["paper"]); draw_car(ImageDraw.Draw(sm), 17, 17, -math.pi / 2, c["team"], 30)
        car = sm.resize((34 * K, 34 * K), Image.NEAREST)
        mask = Image.fromarray((np.abs(np.asarray(car, int) - np.array(PP["paper"])).sum(2) > 6).astype(np.uint8) * 255)
        cx = W // 2; big.paste(car, (cx - 17 * K, int(y0 + (1 - k) * 500)), mask)
    if fr >= 46:
        y = y0 + 34 * K + 40
        for txt, col, sz in lines:
            w_ = btext(big, txt, "label", sz, PP[col], y, W // 2); y += 14 * sz + 22
    return big


def render_guide(du, plan, name, cards_before, cards_after, calls, mood_split=None, hold_s=0, hold_calls=()):
    import subprocess, wave, music
    tr = du.tr; SIZE.update(track_m=du.track_m, car_m=du.car_m, fit=tr.fit); apply_brand(); M.HIRES = []
    globals().update({k: getattr(M, k) for k in ('INK', 'MUT', 'YEL', 'GRN', 'RED', 'EDGE', 'PANEL', 'BG')})
    DU.__dict__.update({k: getattr(M, k) for k in ('INK', 'MUT', 'YEL', 'GRN', 'RED', 'EDGE', 'PANEL', 'BG')})
    times = []; t = plan[0][0]
    for t_end, sp in plan[1:]:
        while t < t_end: times.append(t); t += sp / FPS
    t_fin = du.car["lap"]
    times = [x for x in times if x < t_fin] + [t_fin + k / FPS for k in range(int(hold_s * FPS))]
    times = np.array(times); F = len(times)
    call_f = [(int(np.searchsorted(times, c_[0])), c_[1], c_[2], c_[3]) + ((int(np.searchsorted(times, c_[4])),) if len(c_) > 4 else ())
              for c_ in calls]
    segs = cards_before + [dict(frames=F, lap=True, call=call_f)] + cards_after
    total = sum(s["frames"] for s in segs)
    aud = []
    for s in segs:
        a = {k: v for k, v in s.items() if k in ("note", "call", "frames")}
        if s.get("brand"): a["note"] = s["brand"]
        aud.append(a)
    wav = M.make_audio(name, motif=False)(aud, total)
    secs, acc = [], 0
    for i, s in enumerate(segs):
        if s.get("lap"):
            secs.append((acc / FPS, "race"))
            if mood_split: secs.append(((acc + int(np.searchsorted(times, mood_split))) / FPS, "finish"))
        else: secs.append((acc / FPS, s.get("mood", "title" if i == 0 else "outro" if i == len(segs) - 1 else "podium")))
        acc += s["frames"]
    song = music.song(total / FPS + 1, secs)
    with wave.open(wav) as w: fx = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32767
    n = min(len(fx), len(song)); mixd = np.tanh(fx[:n] * .9 + song[:n] * .55)
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(music.SR); w.writeframes((mixd * 32767 * .9).astype(np.int16).tobytes())
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-af", "volume=7dB,alimiter=limit=0.95",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", f"{OUT}/{name}.mp4"], stdin=subprocess.PIPE)
    snaps = []; WARN.clear(); c = du.car
    for si, s in enumerate(segs):
        Fs = s["frames"]
        for fr in range(Fs):
            if s.get("brand"):
                big = brand_card(fr, du, s["brand"], None, False, s.get("follow", False), False)
                if s.get("car_lines"): big = title_one(big, du, fr, s["car_y"], s["car_lines"])
                M.HIRES = []; p.stdin.write(big.tobytes())
                if fr == Fs - 4: snaps.append(big.resize((NW, NH), Image.NEAREST))
                continue
            im = Image.new("RGB", (NW, NH), BG)
            if s.get("note"): im = note_card(im, tr, s["note"], fr)
            elif s.get("lap"):
                frozen = times[fr] >= t_fin; t = float(min(times[fr], t_fin - 1e-3))
                x, y, h, v, dd = du.pose(c, t)
                z = du.zoom_px / (du.car_m * tr.fit)
                ez = ease((times[fr] - t_fin) / 1.2) if frozen else 0
                cam = (x, y + 10 * ez / (tr.fit * z), z)
                draw_ground(im, du, cam, z, fr)
                d = draw_map(im, tr, cam); px = car_px(z); avoid = []; anchors = {}
                for dd_ in du.dsec[1:3]:                                     # sector lines
                    x_, y_, h_ = du.at(dd_); h_ += math.pi / 2; sx, sy = project(tr, cam, (x_, y_)); hw = track_w(z) / 2
                    for q in range(-int(hw), int(hw) + 1, 2): d.point((sx + math.cos(h_) * q, sy + math.sin(h_) * q), fill=MUT)
                x_, y_, h_ = du.at(0.0); fx_, fy_ = project(tr, cam, (x_, y_)); hw_ = track_w(z) / 2
                for q in range(-int(hw_), int(hw_) + 1):                       # chequered line
                    for r_ in (0, 1):
                        d.point((fx_ - math.sin(h_) * q + math.cos(h_) * r_, fy_ + math.cos(h_) * q + math.sin(h_) * r_), fill=INK if (q + r_) % 2 else BG)
                draw_poles(d, du, cam, z, fr)
                for b in du.buildings:                                         # building labels
                    if b.get("label"):
                        bx, by = project(tr, cam, du.off_pt((b["s0"] + b["s1"]) / 2, (b["o0"] + b["o1"]) / 2))
                        if 10 < bx < NW - 10 and 10 < by < NH - 10:
                            lx = int(max(SAFE_X0 + 1, min(SAFE_X1 - 1 - tw(b["label"]), bx - tw(b["label"]) / 2)))
                            d.rectangle([lx - 1, int(by) - 3, lx + tw(b["label"]), int(by) + 5], fill=BG); tx(d, lx, int(by) - 2, b["label"], MUT)
                            avoid.append((b["label"], bx, by, tw(b["label"]) / 2 + 2)); anchors[b["kind"]] = (bx, by)
                drs_lines(d, du, cam, z, avoid)
                corner_tags(d, du, cam, z, avoid)
                for cn in du.corners: anchors[f"T{cn['n']}"] = project(tr, cam, du.off_pt(cn["s"], 0))
                sx, sy = project(tr, cam, (x, y)); draw_car(d, sx, sy, h, c["team"], px)
                anchors[c["code"]] = (sx, sy); avoid.append((c["code"], sx, sy, px * .55))
                if frozen: lt, col = du.lap_txt, GRN
                else:
                    tt = max(0.0, t); lt, col = f"{int(tt // 60)}:{tt % 60:04.1f}", INK
                im, av = guide_hud(im, du, t, lt, col); avoid += av
                im, av = minimap(im, du, t); avoid += av
                im = apply_calls(im, {"call": s["call"], "_place": s.setdefault("_place", {})}, fr, anchors, avoid, (name, si))
            if fr == Fs - 4: snaps.append(im)
            p.stdin.write(finish_frame(im).tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{name}_sheet.png"); print(name, "sec", round(total / FPS, 1))
