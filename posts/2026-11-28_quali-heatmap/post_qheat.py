# 2026 qualifying heatmap: every driver, every round, one image (Marius 28.11.26).
# Data: Jolpica /ergast/f1/2026/qualifying (qualifying classification, NOT grid after penalties).
# Spot check: R21 Las Vegas ANT P1, VER P2, RUS P3, PIA P7 = matches FIA/F1.com (our verified quali reel 21.11.).
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(HERE, "..", "fonts")
def F(rel, size): return ImageFont.truetype(os.path.join(FD, rel), size)
PS = lambda s: F("fontsource-press-start-2p-5.3.0/files/press-start-2p-latin-400-normal.woff", s)
SK = lambda s: F("fontsource-silkscreen-5.3.0/files/silkscreen-latin-400-normal.woff", s)
SKB = lambda s: F("fontsource-silkscreen-5.3.0/files/silkscreen-latin-700-normal.woff", s)
def hx(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
PAPER, SPECK, BOX, INK, MUTE, RULE, GREEN = map(hx, ["#14120f", "#1b1814", "#1f1b16", "#ece3cf", "#b8ad96", "#3a352c", "#39ff14"])
TC = {"VER":"#3671c6","HAD":"#3671c6","TSU":"#3671c6","HAM":"#dc0000","LEC":"#dc0000","ANT":"#27f4d2","RUS":"#27f4d2","NOR":"#ff8000","PIA":"#ff8000",
      "BOR":"#c0c0c0","HUL":"#c0c0c0","BEA":"#b6babd","CAM":"#b6babd","OCO":"#b6babd","COL":"#ff87bc","GAS":"#ff87bc","LAW":"#6692ff","LIN":"#6692ff",
      "ALO":"#229971","STR":"#229971","SAI":"#1868db","ALB":"#1868db","PER":"#b0b0b0","BOT":"#b0b0b0","HIR":"#b6babd"}
NT = {("HAD",4),("HAD",17),("LAW",19),("BEA",21)}  # no lap time (OpenF1 None/RT), classified last by Jolpica
CODES = ["AUS","CHN","JPN","MIA","CAN","MON","BAR","AUT","GBR","BEL","HUN","NED","ITA","ESP","AZE","MAL","SIN","USA","MEX","BRA","LVG"]

cache = os.path.join(HERE, "qheat_2026.json")
if not os.path.exists(cache):
    pos, off = {}, 0
    while True:
        d = json.load(urllib.request.urlopen(f"https://api.jolpi.ca/ergast/f1/2026/qualifying/?limit=100&offset={off}", timeout=60))["MRData"]
        for r in d["RaceTable"]["Races"]:
            for q in r["QualifyingResults"]:
                pos.setdefault(q["Driver"]["code"], {})[r["round"]] = int(q["position"])
        off += 100
        if off >= int(d["total"]): break
    json.dump(pos, open(cache, "w"), indent=1)
pos = {k: {int(a): b for a, b in v.items()} for k, v in json.load(open(cache)).items()}
N = len(CODES)
avg = {c: sum(v.values()) / len(v) for c, v in pos.items()}
regular = sorted([c for c in pos if len(pos[c]) >= 10], key=lambda c: avg[c])
stand = sorted([c for c in pos if len(pos[c]) < 10], key=lambda c: avg[c])

BANDS = [(1, "#39ff14"), (3, "#24b30f"), (6, "#1b7e10"), (10, "#195414"), (16, "#2a2a1f"), (22, "#181512")]
def cell_col(p):
    for lim, c in BANDS:
        if p <= lim: return hx(c)

W, H = 1080, 1350
im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
for y in range(0, H, 10):
    for x in range((y // 10) % 2 * 5, W, 20): d.rectangle([x, y, x + 4, y + 4], fill=SPECK)
# header
d.text((40, 34), "THE PIXEL PADDOCK", font=SKB(16), fill=INK); d.text((W - 40, 34), "F1 STATS", font=SKB(16), fill=GREEN, anchor="ra")
d.line([(40, 60), (W - 40, 60)], fill=RULE, width=2)
d.text((40, 84), "EVERY QUALI OF 2026", font=PS(32), fill=INK)
d.text((40, 132), "QUALIFYING POSITION OF EVERY DRIVER IN ALL 21 ROUNDS", font=SK(16), fill=MUTE)
d.text((40, 156), "SORTED BY AVERAGE. BRIGHTER = FURTHER FORWARD", font=SK(16), fill=MUTE)

L, top = 108, 262; AVGW = 78
cw = (W - 40 - L - AVGW - 8) / N; ch = 37
for j, c in enumerate(CODES):
    x = L + j * cw + cw / 2
    lab = Image.new("RGBA", (40, 14), (0, 0, 0, 0)); ImageDraw.Draw(lab).text((0, 0), c, font=SK(8), fill=MUTE)
    lab = lab.resize((80, 28), Image.NEAREST).rotate(90, expand=True)
    im.paste(lab, (int(x - 14), top - 84), lab)
d.text((W - 40 - AVGW / 2, top - 22), "AVG", font=SKB(16), fill=GREEN, anchor="ma")

def row(y, code):
    d.rectangle([40, y + 4, 45, y + ch - 4], fill=hx(TC.get(code, "#888888")))
    d.text((54, y + ch / 2), code, font=SKB(16), fill=INK, anchor="lm")
    for j in range(N):
        x0 = L + j * cw; p = pos[code].get(j + 1)
        if p is None:
            d.rectangle([x0 + 2, y + 2, x0 + cw - 2, y + ch - 2], outline=RULE)
            continue
        if (code, j + 1) in NT:
            d.rectangle([x0 + 2, y + 2, x0 + cw - 2, y + ch - 2], fill=hx("#181512"), outline=hx("#e05050"))
            d.text((x0 + cw / 2, y + ch / 2 + 1), "NT", font=SK(16), fill=hx("#e05050"), anchor="mm"); continue
        col = cell_col(p)
        d.rectangle([x0 + 2, y + 2, x0 + cw - 2, y + ch - 2], fill=col)
        tcol = PAPER if p <= 3 else (INK if p <= 16 else MUTE)
        d.text((x0 + cw / 2, y + ch / 2 + 1), str(p), font=SK(16), fill=tcol, anchor="mm")
    d.text((W - 40 - AVGW / 2, y + ch / 2 + 1), f"{avg[code]:.1f}", font=SKB(16), fill=GREEN if code == regular[0] else INK, anchor="mm")

y = top
for c in regular: row(y, c); y += ch
y += 10; d.text((40, y), "STAND-INS AND MID-SEASON SWAPS", font=SK(16), fill=MUTE); y += 22
for c in stand: row(y, c); y += ch

# legend + footer
y += 14
lx = 40
for lab, c in [("POLE", "#39ff14"), ("P2-3", "#24b30f"), ("P4-6", "#1b7e10"), ("P7-10", "#195414"), ("P11-16", "#2a2a1f"), ("P17+", "#181512")]:
    d.rectangle([lx, y, lx + 22, y + 20], fill=hx(c), outline=RULE); d.text((lx + 30, y + 10), lab, font=SK(16), fill=INK, anchor="lm"); lx += 30 + int(d.textlength(lab, font=SK(16))) + 26
d.rectangle([lx, y, lx + 22, y + 20], outline=RULE); d.text((lx + 30, y + 10), "NO RESULT", font=SK(16), fill=MUTE, anchor="lm")
y += 30; d.text((40, y + 10), "NT = NO TIME SET, CLASSIFIED LAST (COUNTS AS P22 IN THE AVERAGE)", font=SK(16), fill=hx("#e05050"), anchor="lm")
y += 34
d.line([(40, H - 46), (W - 40, H - 46)], fill=RULE, width=2)
d.text((40, H - 30), "@THE.PIXEL.PADDOCK", font=SKB(16), fill=MUTE); d.text((W / 2 + 40, H - 30), "DATA: JOLPICA", font=SK(16), fill=MUTE, anchor="ma"); d.text((W - 40, H - 30), "BEFORE QATAR", font=SKB(16), fill=GREEN, anchor="ra")
os.makedirs(os.path.join(HERE, "out_qheat"), exist_ok=True)
im.save(os.path.join(HERE, "out_qheat", "qheat.png")); print("rows", len(regular), len(stand), "end y", y)
