import os, sys, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp import C
from post_usgp import GREEN
from reel_results import big, width, R, TEAM, hx, W, H, FPS, OUT
import random
from post_cota import PTS, N
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = Image.open(f"{HERE}/../brand/logo/profile_picture.png").convert("RGB").resize((360, 360), Image.NEAREST)

def bg():
    im = Image.new("RGB", (W, H), C["paper"]); d = ImageDraw.Draw(im); r = random.Random(3)
    for _ in range(2200):
        x, y = r.randrange(0, W, 5), r.randrange(0, H, 5); R(d, x, y, x + 5, y + 5, C["speck"])
    return im
BG = bg()

# track geometry for the intro
xs = [q[0] for q in PTS]; ys = [q[1] for q in PTS]
TB = (180, 1200, 900, 1540)
S_ = min((TB[2] - TB[0]) / (max(xs) - min(xs)), (TB[3] - TB[1]) / (max(ys) - min(ys)))
ox = TB[0] + ((TB[2] - TB[0]) - (max(xs) - min(xs)) * S_) / 2; oy = TB[1] + ((TB[3] - TB[1]) - (max(ys) - min(ys)) * S_) / 2
TP = [(ox + (x - min(xs)) * S_, oy + (max(ys) - y) * S_) for x, y in PTS]

def track(im, frac):
    n = int(N * frac); lw, lh = W // 5, H // 5
    L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i in range(n):
        a, b = TP[i], TP[(i + 1) % N]; d.line([(a[0] / 5, a[1] / 5), (b[0] / 5, b[1] / 5)], fill=C["mute"] + (255,), width=3)
    L = L.resize((W, H), Image.NEAREST); im.paste(L, (0, 0), L)
    if 0 < frac < 1:
        x, y = TP[n % N]; x, y = int(x // 5 * 5), int(y // 5 * 5); R(ImageDraw.Draw(im), x - 10, y - 10, x + 15, y + 15, GREEN)

def slam(im, fi, t0, x, base, s, font, sc, col, center=False):
    """word drops in: 6 frames, from 120 px above with overshoot."""
    if fi < t0: return
    u = min(1, (fi - t0) / 6); off = int((1 - u) ** 2 * -120)
    if center: x = (W - width(s, font, sc)) // 2
    big(im, x, base + off, s, font, sc, col)

def make(session, rows, out_name, gp="AUSTIN"):
    INTRO, RES0 = 66, 66
    T = [RES0 + 6 + k * 12 for k in range(7)]; T += [T[-1] + 27, T[-1] + 27 + 33, T[-1] + 27 + 33 + 42]
    RES_END = T[-1] + 75; OUTRO = RES_END; total = OUTRO + 95
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-movflags", "+faststart", f"{OUT}/{out_name}.mp4"], stdin=subprocess.PIPE)
    snaps = {}
    SSC = 30
    while width(session, "head", SSC) > 1000: SSC -= 2
    for fi in range(total):
        im = BG.copy(); d = ImageDraw.Draw(im)
        if fi < INTRO:
            slam(im, fi, 0, 0, 470, "F1", "head", 16, C["ink"], center=True)
            slam(im, fi, 10, 0, 590, "RESULTS", "head", 9, C["ink"], center=True)
            slam(im, fi, 20, 0, 750, gp, "head", 13, C["ink"], center=True)
            slam(im, fi, 30, 0, 1020, session, "head", SSC, GREEN, center=True)
            slam(im, fi, 42, 0, 1130, "TOP 10", "head", 8, C["ink"], center=True)
            track(im, min(1, max(0, fi / 48)))
            if fi == 60: snaps["intro"] = im.copy(); im.save(f"{OUT}/{out_name}_cover.png")
        elif fi < OUTRO:
            big(im, 40, 330, f"F1 {gp}", "head", 9, C["ink"])
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
                big(im, W - 60 + dx, y + 64, gap, "body", 5, ink, right=True)
            if T[-1] + 9 <= fi < T[-1] + 17:
                off = [6, -6, 4, -4, 3, -2, 1, 0][fi - T[-1] - 9]
                im = im.transform(im.size, Image.AFFINE, (1, 0, off, 0, 1, 0), fillcolor=C["paper"])
            if fi == RES_END - 1: snaps["res"] = im.copy()
        else:
            k = fi - OUTRO
            if k < 4: im = Image.blend(BG, im, 1)
            slam(im, fi, OUTRO, 0, 480, "FOLLOW", "head", 16, GREEN, center=True)
            slam(im, fi, OUTRO + 10, 0, 620, "THE PIXEL", "head", 11, C["ink"], center=True)
            slam(im, fi, OUTRO + 16, 0, 740, "PADDOCK", "head", 11, C["ink"], center=True)
            if k >= 24:
                im.paste(LOGO, ((W - 360) // 2, 800))
                s_ = "@THE.PIXEL.PADDOCK"; big(im, (W - width(s_, "labelb", 6)) // 2, 1230, s_, "labelb", 6, C["mute"])
            slam(im, fi, OUTRO + 40, 0, 1340, "FOR F1 DATA,", "head", 6, C["ink"], center=True)
            slam(im, fi, OUTRO + 46, 0, 1410, "CONDENSED.", "head", 6, GREEN, center=True)
            if fi == total - 1: snaps["outro"] = im.copy()
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    sh = Image.new("RGB", (1620, 960))
    for i, n in enumerate(("intro", "res", "outro")): sh.paste(snaps[n].resize((540, 960)), (i * 540, 0))
    sh.save(f"{OUT}/{out_name}_sheet.png")

if __name__ == "__main__":
    FP2 = [("LEC", "Ferrari", "1:35.291"), ("ANT", "Mercedes", "+0.042"), ("VER", "Red Bull", "+0.189"), ("HAM", "Ferrari", "+0.615"),
           ("RUS", "Mercedes", "+0.744"), ("LAW", "Racing Bulls", "+1.040"), ("NOR", "McLaren", "+1.082"), ("PIA", "McLaren", "+1.096"),
           ("HAD", "Red Bull", "+1.120"), ("BEA", "Haas", "+1.245")]
    make("FP2", FP2, "fp2_reel_v3"); print("ok")
