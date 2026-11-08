"""Results reel v4: gap bars, rookie tag, position arrows, insight card, self-made 8-bit sound."""
import os, sys, subprocess, wave, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp import C
from post_usgp import GREEN
from reel_results import big, width, R, TEAM, hx, W, H, FPS, OUT
from reel_v3 import BG, slam, LOGO
from mock_v2 import track as load_track
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
TRACKS = {"AUSTIN": f"{HERE}/geo/us.geojson", "MEXICO CITY": f"{HERE}/geo/mx.geojson", "SAO PAULO": f"{HERE}/geo/br.geojson"}

def track_pts(gp):
    P = load_track(TRACKS[gp]); xs = [q[0] for q in P]; ys = [q[1] for q in P]
    TB = (180, 1200, 900, 1540)
    S_ = min((TB[2] - TB[0]) / (max(xs) - min(xs)), (TB[3] - TB[1]) / (max(ys) - min(ys)))
    ox = TB[0] + ((TB[2] - TB[0]) - (max(xs) - min(xs)) * S_) / 2; oy = TB[1] + ((TB[3] - TB[1]) - (max(ys) - min(ys)) * S_) / 2
    return [(ox + (x - min(xs)) * S_, oy + (max(ys) - y) * S_) for x, y in P]

def draw_track(im, TP, frac):
    N = len(TP); n = int(N * frac)
    L = Image.new("RGBA", (W // 5, H // 5), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i in range(n):
        a, b = TP[i], TP[(i + 1) % N]; d.line([(a[0] / 5, a[1] / 5), (b[0] / 5, b[1] / 5)], fill=C["mute"] + (255,), width=3)
    L = L.resize((W, H), Image.NEAREST); im.paste(L, (0, 0), L)
    if 0 < frac < 1:
        x, y = TP[n % N]; x, y = int(x // 5 * 5), int(y // 5 * 5); R(ImageDraw.Draw(im), x - 10, y - 10, x + 15, y + 15, GREEN)

# ---------- sound ----------
def tone(f, dur, vol=0.25, kind="sq", decay=6.0):
    t = np.arange(int(SR * dur)) / SR
    w = np.sign(np.sin(2 * np.pi * f * t)) if kind == "sq" else (2 * np.abs(2 * ((t * f) % 1) - 1) - 1)
    return w * vol * np.exp(-decay * t)

def noise(dur, vol=0.3, decay=25):
    t = np.arange(int(SR * dur)) / SR; r = np.random.default_rng(1).uniform(-1, 1, len(t))
    return r * vol * np.exp(-decay * t)

def mix(buf, sig, at):
    i = int(at * SR); j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]

def write_wav(buf, path):
    buf = np.clip(buf, -1, 1); data = (buf * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

NOTE = {k: 440 * 2 ** ((v - 69) / 12) for k, v in dict(C4=60, D4=62, E4=64, G4=67, A4=69, C5=72, D5=74, E5=76, G5=79, A5=81, C6=84).items()}

# ---------- reel ----------
def gap_s(g):
    try: return float(g.replace("+", "").replace("s", ""))
    except ValueError: return None

def make(session, rows, out_name, gp="AUSTIN", insight=None, rookies=(), moves=None, cover_frame=80, moves_label="VS GRID"):
    """rows: [(code, team, gap)], P1 first. moves: {code: +n/-n} vs previous session. insight: list of 2-4 short lines."""
    TP = track_pts(gp)
    INTRO, RES0 = 96, 96
    T = [RES0 + 8 + k * 16 for k in range(7)]; T += [T[-1] + 32, T[-1] + 32 + 38, T[-1] + 32 + 38 + 46]
    RES_END = T[-1] + 105
    INS = 105 if insight else 0
    OUTRO = RES_END + INS; total = OUTRO + 120
    gaps = [gap_s(g) for _, _, g in rows[1:]]; gmax = max([g for g in gaps if g is not None] or [1])
    BIG = 14
    while max(width(session, "head", BIG), width(gp, "head", BIG)) > 1000: BIG -= 1
    # audio
    buf = np.zeros(int(SR * total / FPS) + SR)
    for t0 in (0, 14, 32, 54): mix(buf, noise(0.10, 0.18) + tone(110, 0.10, 0.15), t0 / FPS)
    # intro jingle: rising 8-bit fanfare, beat = 1 frame unit of 7
    mel = [("C5", 0, .12), ("E5", 7, .12), ("G5", 14, .12), ("C6", 21, .25), ("G5", 32, .12), ("A5", 39, .12), ("C6", 46, .12), ("E5", 54, .16), ("G5", 61, .16), ("C6", 68, .5)]
    for n, f0, du in mel: mix(buf, tone(NOTE[n], du, 0.11, decay=4), f0 / FPS)
    bass = [("C4", 0), ("C4", 14), ("A4", 32), ("G4", 54), ("C4", 68)]
    for n, f0 in bass: mix(buf, tone(NOTE[n] / 2, 0.22, 0.12, kind="tri", decay=5), f0 / FPS)
    scale = ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5"]
    for k in range(9): mix(buf, tone(NOTE[scale[k]], 0.10, 0.18), T[k] / FPS)
    for f in ("C5", "E5", "G5", "C6"): mix(buf, tone(NOTE[f], 0.7, 0.12, decay=3), T[-1] / FPS)
    mix(buf, noise(0.25, 0.2, 12), (T[-1] + 9) / FPS)
    if insight: mix(buf, tone(NOTE["A5"], 0.15, 0.15), RES_END / FPS); mix(buf, tone(NOTE["E5"], 0.2, 0.12), (RES_END + 5) / FPS)
    for k, f in enumerate(("C5", "E5", "G5")): mix(buf, tone(NOTE[f], 0.15, 0.15), (OUTRO + k * 8) / FPS)
    wav = f"{OUT}/{out_name}.wav"; write_wav(buf * 0.9, wav)

    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{OUT}/{out_name}.mp4"], stdin=subprocess.PIPE)
    snaps = {}
    for fi in range(total):
        im = BG.copy(); d = ImageDraw.Draw(im)
        if fi < INTRO:
            slam(im, fi, 0, 0, 520, "F1 RESULTS", "head", 7, C["mute"], center=True)
            slam(im, fi, 14, 0, 760, gp, "head", BIG, C["ink"], center=True)
            slam(im, fi, 32, 0, 960, session, "head", BIG, GREEN, center=True)
            slam(im, fi, 54, 0, 1100, "TOP 10", "head", 7, C["mute"], center=True)
            draw_track(im, TP, min(1, max(0, fi / 70)))
            if fi == cover_frame: snaps["intro"] = im.copy(); im.save(f"{OUT}/{out_name}_cover.png")
        elif fi < RES_END:
            big(im, 40, 330, f"F1 {gp}" if len(gp) <= 8 else gp, "head", 9 if len(gp) <= 8 else 7, C["ink"])
            big(im, W - 40, 330, session, "head", 9 if len(session) <= 3 else 6, GREEN, right=True)
            big(im, 40, 390, "RESULTS · TOP 10", "label", 6, C["mute"])
            R(d, 40, 420, W - 40, 430, C["ink"])
            ROW, TOP = 95, 470
            for k in range(10):
                pos = 10 - k; code, team, gap = rows[pos - 1]; t0 = T[k]
                if fi < t0: continue
                u = min(1, (fi - t0) / 9); dx = (1 - (1 - (1 - u) ** 3)) * W
                y = TOP + (pos - 1) * ROW; lead = pos == 1
                R(d, 40 + dx, y, W - 40 + dx, y + ROW - 12, GREEN if lead else C["box"])
                ink = C["onred"] if lead else C["ink"]
                big(im, 65 + dx, y + 68, str(pos), "head", 7, C["onred"] if lead else C["mute"])
                R(d, 200 + dx, y + 12, 215 + dx, y + ROW - 24, hx(TEAM[team]))
                big(im, 240 + dx, y + 72, code, "head", 8, ink)
                cx = 240 + width(code, "head", 8) + 14
                if code in rookies:
                    R(d, cx + dx, y + 16, cx + 46 + dx, y + 62, GREEN if not lead else C["onred"])
                    big(im, cx + 9 + dx, y + 56, "R", "head", 4, C["paper"] if not lead else GREEN); cx += 58
                if moves and code in moves and moves[code]:
                    m = moves[code]; up = m > 0; col = (GREEN if up else (230, 80, 80)) if not lead else C["onred"]
                    tx0 = cx + dx; ty = y + 22
                    tri = [(tx0, ty + 30), (tx0 + 30, ty + 30), (tx0 + 15, ty)] if up else [(tx0, ty), (tx0 + 30, ty), (tx0 + 15, ty + 30)]
                    d.polygon(tri, fill=col); big(im, tx0 + 38, y + 56, str(abs(m)), "head", 4, col)
                # gap bar
                g = gap_s(gap)
                if not lead and g is not None:
                    bx0, bx1 = 560, 760; L = max(5, int((bx1 - bx0) * min(1, g / gmax) * min(1, (fi - t0) / 12)))
                    R(d, bx0 + dx, y + 34, bx1 + dx, y + 48, C["rule"]); R(d, bx0 + dx, y + 34, bx0 + L + dx, y + 48, C["mute"])
                big(im, W - 60 + dx, y + 64, gap, "body", 5, ink, right=True)
            if fi >= T[-1] + 12:
                big(im, 40, 1450, "BAR = GAP TO P1", "label", 5, C["mute"])
                if rookies: R(d, 520, 1424, 546, 1450, GREEN); big(im, 560, 1450, "= ROOKIE / STAND-IN", "label", 5, C["mute"])
                if moves: d.polygon([(40, 1520), (64, 1520), (52, 1496)], fill=GREEN); d.polygon([(72, 1496), (96, 1496), (84, 1520)], fill=(230, 80, 80)); big(im, 110, 1520, "= PLACES " + moves_label, "label", 5, C["mute"])
            if T[-1] + 9 <= fi < T[-1] + 17:
                off = [6, -6, 4, -4, 3, -2, 1, 0][fi - T[-1] - 9]
                im = im.transform(im.size, Image.AFFINE, (1, 0, off, 0, 1, 0), fillcolor=C["paper"])
            if fi == RES_END - 1: snaps["res"] = im.copy()
        elif fi < OUTRO:
            k0 = RES_END
            slam(im, fi, k0, 0, 560, "THE TAKEAWAY", "label", 8, GREEN, center=True)
            yb = 800
            for i, line in enumerate(insight):
                sc = 16 if i == 0 else 7
                while width(line, "head", sc) > 980: sc -= 1
                slam(im, fi, k0 + 10 + i * 14, 0, yb, line, "head", sc, C["ink"] if i else GREEN, center=True)
                yb += 170 if i == 0 else 110
            if fi == OUTRO - 1: snaps["ins"] = im.copy()
        else:
            k = fi - OUTRO
            slam(im, fi, OUTRO, 0, 480, "FOLLOW", "head", 16, GREEN, center=True)
            slam(im, fi, OUTRO + 14, 0, 620, "THE PIXEL", "head", 11, C["ink"], center=True)
            slam(im, fi, OUTRO + 22, 0, 740, "PADDOCK", "head", 11, C["ink"], center=True)
            if k >= 32:
                im.paste(LOGO, ((W - 360) // 2, 800))
                s_ = "@THE.PIXEL.PADDOCK"; big(im, (W - width(s_, "labelb", 6)) // 2, 1230, s_, "labelb", 6, C["mute"])
            slam(im, fi, OUTRO + 50, 0, 1340, "FOR F1 DATA,", "head", 6, C["ink"], center=True)
            slam(im, fi, OUTRO + 58, 0, 1410, "CONDENSED.", "head", 6, GREEN, center=True)
            if fi == total - 1: snaps["outro"] = im.copy()
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    keys = [k for k in ("intro", "res", "ins", "outro") if k in snaps]
    sh = Image.new("RGB", (540 * len(keys), 960))
    for i, n in enumerate(keys): sh.paste(snaps[n].resize((540, 960)), (i * 540, 0))
    sh.save(f"{OUT}/{out_name}_sheet.png"); print("frames", total, "sec", round(total / FPS, 1))

if __name__ == "__main__":
    RACE = [("ANT", "Mercedes", "1:35:16.650"), ("LEC", "Ferrari", "+13.078"), ("VER", "Red Bull", "+17.485"), ("HAM", "Ferrari", "+18.515"),
            ("NOR", "McLaren", "+30.521"), ("HAD", "Red Bull", "+34.373"), ("PIA", "McLaren", "+52.674"), ("RUS", "Mercedes", "+54.303"),
            ("LAW", "Racing Bulls", "+79.183"), ("GAS", "Alpine", "+87.516")]
    MOVES = {"ANT": 0, "LEC": 2, "VER": -1, "HAM": 1, "NOR": 3, "HAD": -3, "PIA": 0, "RUS": -2, "LAW": 0, "GAS": 0}
    make("RACE", RACE, "test_v4", gp="AUSTIN", moves=MOVES, rookies=("LAW",),
         insight=["13.078 S", "WINNING MARGIN", "LEAD NOW 123 PTS"])
