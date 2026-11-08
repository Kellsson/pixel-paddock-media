"""Round 5: crisp midpoint-circle rings on a 36-grid (30 px cells), Solid P, accent options."""
import os
from PIL import Image, ImageDraw
from logo import PAPER, INK, RED, circle
from logo4 import P_ROWS, GREEN
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_logo")
N, S = 36, 30

def midpoint_circle(d, cx, cy, r, col):
    x, y, err = r, 0, 1 - r
    pts = set()
    while x >= y:
        for a, b in ((x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)):
            pts.add((cx + a, cy + b))
        y += 1
        if err < 0: err += 2 * y + 1
        else: x -= 1; err += 2 * (y - x) + 1
    for p in pts: d.point(p, fill=col)
    return pts

def mark(accent=None, where=None, ring_accent=None):
    im = Image.new("RGB", (N, N), PAPER); d = ImageDraw.Draw(im)
    c = N // 2 - 1 if N % 2 == 0 else N // 2   # 17 -> ring centred on cell 17.5 approx
    # use centre between cells: draw on 2x then downsample? keep simple: centre cell 17, image 35 used + 1 margin
    outer = midpoint_circle(d, 17, 17, 16, INK)
    inner = midpoint_circle(d, 17, 17, 14, INK)
    if ring_accent:
        for (x, y) in outer:
            if x > 17 and y < 17 and (x - 17) > (17 - y) * 0.4 and (x - 17) < (17 - y) * 2.5: d.point((x, y), fill=ring_accent)
    ox, oy = 17 - 6, 17 - 10
    for j, row in enumerate(P_ROWS):
        for i, b in enumerate(row):
            if b == "1": d.point((ox + i, oy + j), fill=INK)
    if where == "stop":
        d.rectangle([ox + 6, oy + 18, ox + 7, oy + 19], fill=accent)
    im = im.crop((0, 0, 35, 35)).resize((35 * S, 35 * S), Image.NEAREST)
    out = Image.new("RGB", (1080, 1080), PAPER); out.paste(im, ((1080 - im.width) // 2, (1080 - im.height) // 2))
    return out

if __name__ == "__main__":
    concepts = [("A RED FULL STOP", mark(RED, "stop")), ("B GREEN FULL STOP", mark(GREEN, "stop")),
                ("C GREEN SECTOR", mark(ring_accent=GREEN)), ("D RINGS ONLY", mark())]
    for name, im in concepts: im.save(f"{OUT}/r5_{name.split()[0]}.png")
    cw = 330; W2 = len(concepts) * cw + 40
    board = Image.new("RGB", (W2, 700), (245, 245, 245)); bd = ImageDraw.Draw(board)
    bd.rectangle([0, 470, W2, 700], fill=(0, 0, 0))
    for k, (name, im) in enumerate(concepts):
        x = 20 + k * cw
        board.paste(circle(im, 260, (245, 245, 245)), (x + 20, 30))
        board.paste(circle(im, 110, (245, 245, 245)), (x + 20, 310))
        board.paste(circle(im, 44, (245, 245, 245)), (x + 170, 343))
        bd.text((x + 20, 440), name, fill=(30, 30, 30))
        board.paste(circle(im, 110, (0, 0, 0)), (x + 20, 525)); board.paste(circle(im, 44, (0, 0, 0)), (x + 170, 558))
    board.save(f"{OUT}/board5.png"); print("ok")
