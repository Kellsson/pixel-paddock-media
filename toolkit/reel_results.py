import os, sys, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp import _f, C
from post_usgp import GREEN
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out_reel"; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
def R(d, x0, y0, x1, y1, c): d.rectangle([int(x0), int(y0), int(x1) - 1, int(y1) - 1], fill=c)
def glyphs(t, n, sc):
    f, _ = _f(n); asc, desc = f.getmetrics()
    w = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(t, font=f)) + 4; h = asc + desc + 4
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m); d.fontmode = "1"; d.text((0, asc), t, font=f, fill=255, anchor="ls")
    m = m.point(lambda v: 255 if v > 127 else 0).resize((w * sc, h * sc), Image.NEAREST); return m, asc * sc
def big(im, x, base, t, n, sc, col, right=False):
    m, a = glyphs(t, n, sc); bb = m.getbbox(); w = bb[2] if bb else 0
    if right: x = x - w
    im.paste(Image.new("RGB", m.size, col), (int(x), int(base - a)), m); return w
def width(t, n, sc): m, _ = glyphs(t, n, sc); bb = m.getbbox(); return bb[2] if bb else 0

TEAM = {"Ferrari": "#dc0000", "Mercedes": "#27f4d2", "Red Bull": "#3671c6", "Racing Bulls": "#6692ff", "McLaren": "#ff8000", "Haas": "#b6babd", "Aston Martin": "#229971", "Alpine": "#ff87bc", "Audi": "#c0c0c0", "Williams": "#1868db", "Cadillac": "#b0b0b0"}
def hx(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def make(session, rows, tagline, out_name, hook_big, hook_sub, question, sub="UNITED STATES GP · COTA"):
    def bgimg():
        bg = Image.new("RGB", (W, H), C["paper"]); d = ImageDraw.Draw(bg); r = random.Random(3)
        for _ in range(2200):
            x, y = r.randrange(0, W, 5), r.randrange(0, H, 5); R(d, x, y, x + 5, y + 5, C["speck"])
        return bg, d
    # hook screen
    hook, d = bgimg()
    big(hook, 40, 330, f"F1 AUSTIN · {session}", "head", 6, C["mute"])
    wv = width(hook_big, "head", 24); big(hook, (W - wv) // 2, 900, hook_big, "head", 24, GREEN)
    ws = width("SECONDS", "head", 8); big(hook, (W - ws) // 2, 1010, "SECONDS", "head", 8, C["ink"])
    yy = 1160
    for ln in hook_sub:
        wl = width(ln, "head", 5); big(hook, (W - wl) // 2, yy, ln, "head", 5, C["ink"]); yy += 60
    # list background
    bg, d = bgimg()
    big(bg, 40, 330, "F1 AUSTIN", "head", 10, C["ink"])
    big(bg, 40, 510, session, "head", 20, GREEN)
    big(bg, 40, 560, sub, "label", 5, C["mute"])
    R(d, 40, 590, W - 40, 600, C["ink"])
    ROW_H, TOP, SLIDE = 82, 630, 8
    L0 = 45
    T = [L0 + k * 5 for k in range(7)]           # P10..P4 fast
    T += [T[-1] + 18, T[-1] + 18 + 21, T[-1] + 18 + 21 + 27]   # P3, P2, P1 with growing pauses
    tP1 = T[-1]; tTag = tP1 + 20; tQ = tP1 + 35; total = tQ + 60
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-movflags", "+faststart", f"{OUT}/{out_name}.mp4"], stdin=subprocess.PIPE)
    for fi in range(total):
        if fi < L0:
            im = hook.copy()
            if fi < 4: im = Image.blend(Image.new("RGB", (W, H), C["paper"]), im, fi / 4)
            p.stdin.write(im.tobytes()); 
            if fi == 30: im.save(f"{OUT}/{out_name}_hook.png")
            continue
        im = bg.copy(); d = ImageDraw.Draw(im)
        for k in range(10):
            pos = 10 - k; code, team, gap = rows[pos - 1]; t0 = T[k]
            if fi < t0: continue
            u = min(1, (fi - t0) / SLIDE); ease = 1 - (1 - u) ** 3; dx = (1 - ease) * W
            y = TOP + (pos - 1) * ROW_H; lead = pos == 1
            R(d, 40 + dx, y, W - 40 + dx, y + ROW_H - 10, GREEN if lead else C["box"])
            ink = C["onred"] if lead else C["ink"]; mute = C["onred"] if lead else C["mute"]
            big(im, 60 + dx, y + 61, str(pos), "head", 6, mute)
            R(d, 190 + dx, y + 10, 205 + dx, y + ROW_H - 20, hx(TEAM[team]))
            big(im, 230 + dx, y + 64, code, "head", 7, ink)
            big(im, W - 60 + dx, y + 56, gap, "body", 4, ink, right=True)
        if fi >= tTag: big(im, 40, 1500, tagline, "body", 4, C["ink"])
        if fi >= tQ:
            big(im, 40, 1590, question, "head", 6, GREEN)
            big(im, 40, 1640, "@THE.PIXEL.PADDOCK", "label", 5, C["mute"])
        # P1 impact: flash + shake
        if tP1 + SLIDE <= fi < tP1 + SLIDE + 10:
            off = [6, -6, 4, -4, 3, -3, 2, -2, 1, 0][fi - tP1 - SLIDE]
            im = im.transform(im.size, Image.AFFINE, (1, 0, off, 0, 1, 0), fillcolor=C["paper"])
            if fi - tP1 - SLIDE < 2: im = Image.blend(im, Image.new("RGB", (W, H), GREEN), 0.25)
        p.stdin.write(im.tobytes())
        if fi == total - 1: im.save(f"{OUT}/{out_name}_last.png")
        if fi == T[8] + 10: im.save(f"{OUT}/{out_name}_mid.png")
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    FP2 = [("LEC", "Ferrari", "1:35.291"), ("ANT", "Mercedes", "+0.042"), ("VER", "Red Bull", "+0.189"), ("HAM", "Ferrari", "+0.615"),
           ("RUS", "Mercedes", "+0.744"), ("LAW", "Racing Bulls", "+1.040"), ("NOR", "McLaren", "+1.082"), ("PIA", "McLaren", "+1.096"),
           ("HAD", "Red Bull", "+1.120"), ("BEA", "Haas", "+1.245")]
    make("FP2", FP2, "Leclerc fastest in FP1 and FP2.", "fp2_reel_v2", "0.042", ["LECLERC VS", "TITLE LEADER ANTONELLI"], "WHO TAKES POLE?")
    print("ok")
