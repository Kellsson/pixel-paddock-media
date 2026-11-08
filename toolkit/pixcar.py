"""Pixel Paddock car sprites (side view, nose right). Procedural era template + zone liveries (colours only, no logos).
Sprite box ~48 x 14 px at native resolution."""
from PIL import Image, ImageDraw

def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)

LIVERIES = {
    # McLaren MP4/6 (1991): luminous red (McLaren: RAL 3024 'daylight fluorescent red') over white.
    "MCL_1991": dict(top=(238, 46, 44), side=(244, 244, 244), pod=(238, 46, 44), podlow=(244, 244, 244), air=(238, 46, 44),
                     wing=(238, 46, 44), plate=(244, 244, 244), fwing=(238, 46, 44), numbg=(244, 244, 244), num=(18, 18, 18)),
    # Williams FW14 (1991): blue monocoque side + nose, white sidepods, yellow airbox.
    "WIL_1991": dict(top=(244, 244, 244), side=(30, 62, 150), pod=(244, 244, 244), podlow=(244, 244, 244), air=(246, 196, 0),
                     wing=(244, 244, 244), plate=(30, 62, 150), fwing=(30, 62, 150), numbg=(244, 244, 244), num=(30, 62, 150)),
}
TYRE = (20, 20, 22); RIM = (110, 114, 122); FLOOR = (24, 24, 28)

DIGITS = {"1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"], "5": ["111", "100", "111", "001", "111"],
          "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "2_": []}

def wheel(d, cx, cy, r, f):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TYRE)
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=shade(RIM, .7))
    sp = (f // 2) % 2
    if sp: d.point((cx - 1, cy), fill=RIM); d.point((cx + 1, cy), fill=RIM)
    else: d.point((cx, cy - 1), fill=RIM); d.point((cx, cy + 1), fill=RIM)
    d.point((cx - r + 1, cy - r + 2), fill=(60, 60, 66))  # sidewall highlight

def draw(im, x, y, livery, helmet=(240, 240, 240), number=None, f=0):
    L = LIVERIES[livery]; d = ImageDraw.Draw(im)
    # floor / plank
    d.rectangle([x + 6, y + 11, x + 40, y + 11], fill=FLOOR)
    # rear wing: endplate + two elements
    d.rectangle([x + 0, y + 0, x + 1, y + 7], fill=L["plate"])
    d.rectangle([x + 1, y + 0, x + 6, y + 1], fill=L["wing"]); d.rectangle([x + 2, y + 3, x + 6, y + 3], fill=shade(L["wing"], .8))
    d.rectangle([x + 5, y + 4, x + 6, y + 8], fill=(40, 40, 44))  # wing pillar
    # engine cover sweeping up to airbox above the driver
    d.polygon([(x + 7, y + 8), (x + 7, y + 6), (x + 18, y + 3), (x + 22, y + 1), (x + 25, y + 1), (x + 26, y + 4), (x + 26, y + 8)], fill=L["air"])
    d.line([(x + 8, y + 6), (x + 18, y + 3)], fill=shade(L["air"], 1.15))
    d.rectangle([x + 23, y + 2, x + 24, y + 3], fill=(16, 16, 20))   # airbox intake
    # sidepod (two-tone)
    d.rectangle([x + 13, y + 6, x + 28, y + 8], fill=L["pod"]); d.rectangle([x + 12, y + 9, x + 29, y + 10], fill=L["podlow"])
    d.line([(x + 13, y + 6), (x + 28, y + 6)], fill=shade(L["pod"], 1.15))
    # monocoque + nose, top colour above side colour
    d.polygon([(x + 26, y + 5), (x + 33, y + 6), (x + 45, y + 9), (x + 45, y + 10), (x + 26, y + 10)], fill=L["side"])
    d.polygon([(x + 26, y + 4), (x + 33, y + 5), (x + 45, y + 8), (x + 45, y + 9), (x + 33, y + 6), (x + 26, y + 6)], fill=L["top"])
    # cockpit + helmet
    d.rectangle([x + 27, y + 3, x + 30, y + 4], fill=(14, 14, 18))
    d.rectangle([x + 27, y + 2, x + 29, y + 4], fill=helmet); d.point((x + 29, y + 3), fill=(20, 24, 34))
    # number panel on nose
    if number:
        d.rectangle([x + 34, y + 6, x + 38, y + 8], fill=L["numbg"])
        d.point((x + 36, y + 7), fill=L["num"])
    # front wing + endplate
    d.rectangle([x + 40, y + 12, x + 47, y + 12], fill=L["fwing"]); d.rectangle([x + 46, y + 10, x + 47, y + 12], fill=L["plate"])
    # wheels last (in front of bodywork in side view)
    wheel(d, x + 9, y + 9, 5, f)
    wheel(d, x + 39, y + 10, 4, f)
    return 48, 15

if __name__ == "__main__":
    im = Image.new("RGB", (60, 54), (30, 36, 50))
    draw(im, 6, 4, "MCL_1991", helmet=(242, 201, 76), number="1")
    draw(im, 6, 20, "WIL_1991", number="6")
    draw(im, 6, 36, "MCL_1991", number="2")
    im.resize((600, 540), Image.NEAREST).save("/tmp/claude-0/-home-claude/30bf535a-4055-5b32-9799-4678dcb3a6b5/scratchpad/out_short/cars_preview.png")
