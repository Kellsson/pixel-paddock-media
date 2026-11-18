"""Track-tour reel: camera flies a lap of the real circuit (bacinger GeoJSON), zooms into hotspots and
pops up fact callouts next to the car. Same look as the map-recap shorts (map_recap.py).
Usage: python3 track_tour.py lv    -> out_short/tour_lv.mp4 (+ _sheet.png)
Every fact needs two sources: see ../SOURCES.md (section "Track tour Las Vegas")."""
import sys, math, subprocess
import numpy as np
from map_recap import *   # Track, draw_map, project, callout, headline, panel, shade, draw_car, tone, mix, constants

def nearest_frac(tr, p):
    i = min(range(tr.n), key=lambda k: math.dist(tr.pts[k], p)); return i / tr.n

def ll(lo, la, tr_geo):
    js = json.load(open(tr_geo)); co = js['features'][0]['geometry']['coordinates']
    lat0 = sum(c[1] for c in co) / len(co)
    return (lo * math.cos(math.radians(lat0)) * 111320, -la * 110540)

def first_corner(tr, start=.004, stop=.12):
    """frac of the first sharp corner after the line (largest heading change per step)."""
    best = None
    for k in range(int(start * tr.n), int(stop * tr.n)):
        f = k / tr.n; dh = abs((tr.heading(f + .004) - tr.heading(f - .004) + math.pi) % (2 * math.pi) - math.pi)
        if best is None or dh > best[0] + 1e-6: best = (dh, f)
        if best and best[0] > 1.2 and dh < .3: break
    return best[1]

# ----------------------------------------------------------------- Las Vegas
def cfg_lv():
    geo = f"{HERE}/geo/lv.geojson"; tr = Track(geo)
    sphere = ll(-115.1621, 36.1206, geo)
    js = json.load(open(geo)); co = js['features'][0]['geometry']['coordinates']
    strip_pts = [ll(lo, la, geo) for lo, la in co if lo < -115.1705]
    f_strip = min(nearest_frac(tr, p) for p in strip_pts)          # where the cars turn onto the Strip
    f_strip_end = max(nearest_frac(tr, p) for p in strip_pts)
    f_t1 = first_corner(tr); f_sph = nearest_frac(tr, sphere)
    S = lambda t, c, s=1: (t, c, s)
    return dict(
        name="tour_lv", geo=geo, tr=tr, track_m=18.0, car_m=14.0,
        title=("LAS VEGAS", "TRACK TOUR"), info="6.201 KM - 17 TURNS - 50 LAPS",
        landmarks=[("sphere", sphere, 78.0)],          # Sphere: 516 ft wide -> radius ~78 m
        spots=[  # (frac, [beats]); beat = lines for one callout
            (f_t1, [[S("TURN 1", YEL, 2), S("2023: VER PUSHES LEC WIDE", INK), S("5S PENALTY, WINS ANYWAY", MUT)],
                    [S("TURN 1", YEL, 2), S("2025: NOR BRAKES TOO LATE", INK), S("VER TAKES THE LEAD", MUT)]]),
            (f_sph, [[S("THE SPHERE", YEL, 2), S("WORLD'S LARGEST", INK), S("SPHERICAL BUILDING", INK)]]),
            (f_strip + .01, [[S("THE STRIP", YEL, 2), S("1.9 KM FLAT OUT", INK), S("UP TO 350 KM/H", MUT)]]),
            (.985, [[S("FINISH LINE", YEL, 2), S("2024: VER FINISHES P5", INK), S("AND WINS HIS 4TH TITLE", MUT)],
                    [S("FINISH LINE", YEL, 2), S("2025: BOTH MCLARENS", INK), S("DSQ FOR PLANK WEAR", MUT)]]),
        ],
        note=[S("DID YOU KNOW?", YEL, 2), S("", INK), S("FP1 2023 WAS", INK, 2), S("RED-FLAGGED", INK, 2), S("AFTER 9 MINUTES:", MUT), S("SAINZ HIT A DRAIN COVER", MUT)],
        outro=[S("LIGHTS OUT", YEL, 2), S("SAT 20:00 LOCAL", INK, 2), S("SUN 04:00 UTC", INK, 2), S("", INK), S("FOLLOW THE PIXEL PADDOCK", MUT)],
    )

CFG = {"lv": cfg_lv}

TEAMS["PP"] = dict(fwing=GRN, nose=INK, pod=INK, body=INK, air=GRN, rwing=GRN)

# ----------------------------------------------------------------- timeline
INTRO, OUTRO, NOTEF = 96, 120, 110
BEAT = 84              # frames a callout stays up
Z_CRUISE, Z_SPOT = 4.5, 8.5

def build_timeline(C):
    """per-frame (frac, zoom, beat_lines, beat_age). Cruise between spots fast, slow down at spots."""
    tl = []; f = 0.0; spots = C["spots"]
    def cruise(f0, f1, frames):
        for i in range(frames):
            u = ease(i / max(1, frames - 1)); tl.append([f0 + (f1 - f0) * u, None, None, -1])
    # launch from the line to the first spot
    for k, (fs, beats) in enumerate(spots):
        a = fs - .012
        dist = (a - f) % 1 if k else a - f
        cruise(f, f + dist, max(24, int(dist * 260)))
        f = f + dist
        n = BEAT * len(beats)
        for i in range(n):
            b = i // BEAT; tl.append([f + .024 * i / n, None, beats[b], i % BEAT])
        f = f + .024
    # finish the lap (if the last spot was before the line) and stop on the line
    if f < 1: cruise(f, 1.0, max(12, int((1 - f) * 260)))
    # zoom profile: Z_SPOT while a callout is up, eased in/out over 14 frames
    tgt = [Z_SPOT if r[2] else Z_CRUISE for r in tl]; z = Z_CRUISE
    for r, t in zip(tl, tgt):
        z += (t - z) * .12; r[1] = z
    return tl

def sphere_px(im, tr, cam, p, r_m, fr):
    d = ImageDraw.Draw(im); x, y = project(tr, cam, p); r = max(2, r_m * tr.fit * cam[2])
    for k in range(int(r * 6) + 8):     # LED dots around the rim, slowly cycling colours
        a = k / (int(r * 6) + 8) * 2 * math.pi
        col = [(255, 180, 40), (255, 90, 160), (90, 200, 255)][(k + fr // 6) % 3]
        d.point((x + math.cos(a) * r, y + math.sin(a) * r), fill=col)
    return x, y

def render_tour(C):
    tr = C["tr"]; SIZE.update(track_m=C["track_m"], car_m=C["car_m"], fit=tr.fit)
    tl = build_timeline(C); NF = NOTEF if C.get("note") else 0; END = INTRO + len(tl); total = END + NF + OUTRO
    # ---- audio: engine hum tied to car speed + blips at callouts + jingles
    n = int(SR * total / FPS) + SR; buf = np.zeros(n)
    sp = np.zeros(total)
    for i in range(1, len(tl)): sp[INTRO + i] = ((tl[i][0] - tl[i - 1][0]) % 1) * 1000
    spf = np.interp(np.arange(n) / SR * FPS, np.arange(total), sp)
    freq = 55 + spf * 14; ph = np.cumsum(freq / SR) * 2 * math.pi
    hum = np.sign(np.sin(ph)) * .035 * np.clip(spf / 4 + .25, 0, 1); hum[: int(SR * INTRO / FPS)] = 0
    hum[int(SR * (INTRO + len(tl)) / FPS):] = 0; buf += hum
    for t0, nts in ((0, (64, 67, 71, 76)), (END + NF, (76, 71, 67, 64, 67, 71, 76))):
        for k, m in enumerate(nts): mix(buf, tone(NOTE(m), .16, .12), (t0 + k * 6) / FPS)
    for i, r in enumerate(tl):
        if r[2] and r[3] == 0: mix(buf, tone(NOTE(81), .07, .12), (INTRO + i) / FPS); mix(buf, tone(NOTE(88), .09, .1), (INTRO + i + 3) / FPS)
    if NF: mix(buf, tone(NOTE(72), .12, .12), (END + 6) / FPS); mix(buf, tone(NOTE(79), .2, .1), (END + 12) / FPS)
    import wave
    wav = f"{OUT}/{C['name']}.wav"; a = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(wav, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(a.tobytes())

    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{NW*SC}x{NH*SC}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          f"{OUT}/{C['name']}.mp4"], stdin=subprocess.PIPE)
    snaps = []; over = (tr.cx, tr.cy, 1.0); cam = over
    for fr in range(total):
        im = Image.new("RGB", (NW, NH), BG)
        if END <= fr < END + NF:
            nf = fr - END
            im = note_card(im, tr, C["note"], nf, step=10)
            if nf == NF - 10: snaps.append(im.copy())
        elif fr < INTRO or fr >= END + NF:
            o = fr >= END + NF; age = fr - (END + NF) if o else fr
            draw_map(im, tr, over, dim=.55 if o else min(1, .3 + age / 40))
            for _, pnt, rm in C["landmarks"]: sphere_px(im, tr, over, pnt, rm, fr)
            if not o:
                im = headline(im, C["title"][0], INK, age - 4, y=24)
                im = headline(im, C["title"][1], YEL, age - 18, y=42)
                im = headline(im, C["info"], MUT, age - 34, y=178, sc=1)
                if age == 70: snaps.append(im.copy())
            else:
                im = shade(im, (0, 0, NW, NH), .45)
                shown = [l if age >= 6 + i * 10 else ("", l[1], l[2]) for i, l in enumerate(C["outro"])]
                im = panel(im, shown, y0=70)
                if age == OUTRO - 10: snaps.append(im.copy())
        else:
            f, z, lines, bage = tl[fr - INTRO]
            car = tr.at(f); look = tr.at(f + .012)
            tgt = ((car[0] * 2 + look[0]) / 3, (car[1] * 2 + look[1]) / 3, z)
            cam = tuple(c + (t - c) * (.18 if fr > INTRO else 1) for c, t in zip(cam, tgt))
            d = draw_map(im, tr, cam)
            for _, pnt, rm in C["landmarks"]: sphere_px(im, tr, cam, pnt, rm, fr)
            d = ImageDraw.Draw(im); x, y = project(tr, cam, car)
            draw_car(d, x, y, tr.heading(f), "PP", max(8.0, car_px(z)))
            if lines:
                w, h = box_size(lines)
                im, _ = callout(im, (x, y), lines, bage, (-w / 2, -h - 16, "up"))
            im = shade(im, (SAFE_X0, 8, SAFE_X1, 20), .15); d = ImageDraw.Draw(im)
            d.rectangle([SAFE_X0, 8, SAFE_X1 - 1, 19], outline=EDGE)
            tx(d, SAFE_X0 + 4, 12, C["title"][0], INK); bx0 = SAFE_X0 + 4 + tw(C["title"][0]) + 6; bx1 = SAFE_X1 - 5
            d.rectangle([bx0, 13, bx1, 15], fill=(30, 34, 48)); d.rectangle([bx0, 13, bx0 + int((bx1 - bx0) * min(1, f)), 15], fill=GRN)
            if lines and bage == BEAT - 12: snaps.append(im.copy())
        p.stdin.write(im.resize((NW * SC, NH * SC), Image.NEAREST).tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (180 * len(snaps), 320))
    for i, s_ in enumerate(snaps): sh.paste(s_.resize((180, 320), Image.NEAREST), (i * 180, 0))
    sh.save(f"{OUT}/{C['name']}_sheet.png")
    print("frames", total, "sec", round(total / FPS, 1), "spots", [round(s[0], 3) for s in C["spots"]])

if __name__ == "__main__":
    render_tour(CFG[sys.argv[1] if len(sys.argv) > 1 else "lv"]())
