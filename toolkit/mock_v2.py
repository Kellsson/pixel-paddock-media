import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp2 import *
from pp import text, tlen, R, C, W, H
from post_usgp import GREEN
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_mock"); os.makedirs(OUT, exist_ok=True)
G5 = GREEN
HERE = os.path.dirname(os.path.abspath(__file__))

def track(path):
    co = json.load(open(path))['features'][0]['geometry']['coordinates']
    lat0 = sum(c[1] for c in co) / len(co); lon0 = sum(c[0] for c in co) / len(co)
    return [((lo - lon0) * math.cos(math.radians(lat0)) * 111320, (la - lat0) * 110540) for lo, la in co][:-1]

# apex index in GeoJSON + direction (+1 left, -1 right), derived from heading change
COTA_TURNS = {1: 7, 2: 17, 3: 26, 4: 31, 5: 38, 6: 50, 7: 58, 8: 67, 9: 75, 10: 80, 11: 87, 12: 101,
              13: 109, 14: 115, 15: 129, 16: 134, 17: 140, 18: 150, 19: 156, 20: 164}
ABS = {14: (450, 740), 16: (345, 750)}
NUDGE = {4: (95, 65), 3: (-10, 15), 14: (-55, -5), 16: (25, 0), 13: (10, 0), 1: (0, -5), 20: (15, 0)}

def el_map(im, d, top, hl=(2, 10)):
    h = 780; box(im, d, top, h, "TRACK MAP, COTA · 20 TURNS")
    pts = track(f"{HERE}/geo/us.geojson"); n = len(pts)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    bw, bh = 860, 520; S = min(bw / (max(xs) - min(xs)), bh / (max(ys) - min(ys)))
    ox = 115 + (bw - (max(xs) - min(xs)) * S) / 2; oy = top + 120
    P = [(ox + (x - min(xs)) * S, oy + (max(ys) - y) * S) for x, y in pts]
    # pixelate: draw at 1/5 scale then upscale nearest
    lw, lh = W // 5, H // 5
    def layer(seg_ok, col):
        L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        for i in range(n):
            if seg_ok(i):
                a, b = P[i], P[(i + 1) % n]
                ld.line([(a[0] / 5, a[1] / 5), (b[0] / 5, b[1] / 5)], fill=col, width=3)
        return L.resize((W, H), Image.NEAREST)
    i0, i1 = COTA_TURNS[hl[0]] - 5, COTA_TURNS[hl[1]] + 3
    base = layer(lambda i: True, C["mute"] + (255,)); im.paste(base, (0, 0), base)
    hi = layer(lambda i: i0 <= i <= i1, G5 + (255,)); im.paste(hi, (0, 0), hi)
    d = ImageDraw.Draw(im)
    # start/finish line (index 0), chequer block across the track
    sx, sy = P[0]; sx, sy = int(sx // 5 * 5), int(sy // 5 * 5)
    for k in range(-3, 3):
        for j in range(2):
            R(d, sx + j * 5 + k * 5 - 5, sy + k * 5 - j * 5 + 5, sx + j * 5 + k * 5, sy + k * 5 - j * 5 + 10, C["ink"] if (k + j) % 2 else C["paper"])
    # direction arrow on main straight (heading from idx 168 to 0 continues to 5)
    # turn labels
    for t, i in COTA_TURNS.items():
        a = P[(i - 2) % n]; b = P[(i + 2) % n]; c = P[i]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        cross = (P[i][0] - a[0]) * dy - (P[i][1] - a[1]) * dx
        nx, ny = -dy / L, dx / L
        # outward = away from curve centre: centre lies toward midpoint(a,b) from c
        mx, my = (a[0] + b[0]) / 2 - c[0], (a[1] + b[1]) / 2 - c[1]
        if mx * nx + my * ny > 0: nx, ny = -nx, -ny
        ddx, ddy = NUDGE.get(t, (0, 0))
        px, py = int(c[0] // 5 * 5), int(c[1] // 5 * 5); R(d, px - 5, py - 5, px + 10, py + 10, C["ink"])
        lab = str(t); tw = tlen("label", lab)
        x = c[0] + nx * 38 - tw / 2 + ddx; y = c[1] + ny * 38 + 14 + ddy
        if t in ABS: x, y = ABS[t]
        col = G5 if hl[0] <= t <= hl[1] else C["ink"]
        text(im, int(x // 5 * 5), int(y // 5 * 5), lab, "label", col)
    y = top + h - 45
    R(d, 70, y - 20, 110, y - 5, G5); text(im, 130, y, "T2-T10, THE ESSES", "label", G5)
    R(d, 600, y - 20, 640, y - 5, C["mute"]); text(im, 660, y, "5.513 KM", "label", C["mute"])
    return top + h

# sessions in UTC (US GP 2026: Fri 23 Oct - Sun 25 Oct; US still on CDT, UK/EU on summer time until Sun 25 Oct 01:00 UTC)
SESS = [("FP1", "FRI", (23, 17, 30)), ("FP2", "FRI", (23, 21, 0)), ("FP3", "SAT", (24, 17, 30)),
        ("Q", "SAT", (24, 21, 0)), ("RACE", "SUN", (25, 20, 0))]
def off(city, day, hh):
    utc_hour = day * 24 + hh
    eu_dst = utc_hour < 25 * 24 + 1
    return {"AUSTIN": -5, "NEW YORK": -4, "LONDON": 1 if eu_dst else 0, "BERLIN": 2 if eu_dst else 1, "TOKYO": 9}[city]

def el_week(im, d, top, done=1):
    cities = ["AUSTIN", "NEW YORK", "LONDON", "BERLIN", "TOKYO"]
    h = 300 + 70 * len(cities); box(im, d, top, h, "RACE WEEKEND, 5 TIME ZONES")
    x0 = 330; cw = 138
    for k, (name, day, _) in enumerate(SESS):
        x = x0 + k * cw; col = G5 if k < done else C["rule"]
        R(d, x, top + 90, x + cw - 8, top + 145, col)
        text(im, x + 5, top + 130, name, "label", C["onred"] if k < done else C["ink"])
        text(im, x + 10, top + 185, day, "label", C["mute"])
    y = top + 260
    for city in cities:
        hlr = city == cities[0]
        if hlr: R(d, 55, y - 45, W - 55, y + 15, C["rule"])
        text(im, 70, y, city + (" +1" if city == "TOKYO" else ""), "label", C["ink"] if hlr else C["mute"])
        for k, (name, day, (dd, hh, mm)) in enumerate(SESS):
            o = off(city, dd, hh); tot = hh + o; ld = dd + tot // 24; lh = tot % 24
            s = f"{lh:02d}:{mm:02d}"; x = x0 + k * cw + 10
            text(im, x, y, s, "body", C["ink"])
            if False and ld != dd + (0 if city != "TOKYO" else 0) and ld > dd and city == "TOKYO":
                text(im, x + tlen("body", s) + 5, y - 15, "+1", "label", G5)
        y += 70
    leg = ("Green = done · Grey = track time · +1 = next day" if done else "Grey band = track time · Tokyo +1 = next day")
    text(im, 70, top + h - 30, leg, "body", C["mute"])
    return top + h

if __name__ == "__main__":
    for fn, hl, sub, fnc in [("1_sector_map", "1 · TRACK MAP", "Real layout, every corner numbered.", el_map),
                             ("5_weekend_bar", "5 · WEEKEND BAR", "Every session in five time zones.", el_week)]:
        im, d = page(1, 3, "MOCKUP")
        y = headline(im, hl); y = body(im, y + 45, sub + " Mock-up with real data.")
        fnc(im, d, y + 50); footer(im, d, 1, "MOCKUP"); im.save(f"{OUT}/{fn}.png")
    print("ok")
