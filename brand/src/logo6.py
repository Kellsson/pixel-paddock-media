"""Round 6: thin, crisp midpoint rings on a 72-grid (15 px), Solid P at 2x, accents."""
import os
from PIL import Image, ImageDraw
from logo import PAPER, INK, RED, circle
from logo4 import P_ROWS, GREEN
from logo5 import midpoint_circle
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_logo")
S = 15

def mark(accent=None, where=None, ring_accent=None, n=71):
    im = Image.new("RGB", (n, n), PAPER); d = ImageDraw.Draw(im)
    c = n // 2
    outer = midpoint_circle(d, c, c, 32, INK)
    midpoint_circle(d, c, c, 30, INK)
    if ring_accent:
        for (x, y) in outer:
            dx, dy = x - c, c - y
            if dx > 0 and dy > 0 and 0.45 < dy / max(dx, 1) < 1.6: d.point((x, y), fill=ring_accent)
    w, h = 26, 40
    ox, oy = c - w // 2 + 1, c - h // 2
    for j, row in enumerate(P_ROWS):
        for i, b in enumerate(row):
            if b == "1": d.rectangle([ox + 2 * i, oy + 2 * j, ox + 2 * i + 1, oy + 2 * j + 1], fill=INK)
    if where == "stop":
        d.rectangle([ox + 12, oy + h - 4, ox + 15, oy + h - 1], fill=accent)
    big = im.resize((n * S, n * S), Image.NEAREST)
    out = Image.new("RGB", (1080, 1080), PAPER); out.paste(big, ((1080 - big.width) // 2, (1080 - big.height) // 2))
    return out

if __name__ == "__main__":
    concepts = [("A RED FULL STOP", mark(RED, "stop")), ("B GREEN FULL STOP", mark(GREEN, "stop")),
                ("C GREEN SECTOR", mark(ring_accent=GREEN)), ("D RINGS ONLY", mark())]
    for name, im in concepts: im.save(f"{OUT}/r6_{name.split()[0]}.png")
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
    board.save(f"{OUT}/board6.png"); print("ok")
