"""Round 4: Solid P + double pixel ring (echo of the header double rule), accent variants."""
import os, math
from PIL import Image, ImageDraw
from logo import PAPER, INK, RED, circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_logo")
N, S = 72, 15                      # 72-grid, 15 px per cell -> 1080
GREEN = (57, 255, 20)              # neon green
GREEN_SOFT = (74, 222, 128)

P_ROWS = [
    "1111111111100",
    "1111111111110",
    "1111111111111",
    "1111000001111",
    "1111000001111",
    "1111000001111",
    "1111000001111",
    "1111000001111",
    "1111000001111",
    "1111111111111",
    "1111111111110",
    "1111111111100",
] + ["1111000000000"] * 8          # 13 x 20 cells at 36-grid


def base():
    im = Image.new("RGB", (N, N), PAPER); d = ImageDraw.Draw(im)
    return im, d


def ring(d, rad_out, th, col, seg=None, seg_col=None):
    c = N / 2
    for y in range(N):
        for x in range(N):
            dist = math.hypot(x + 0.5 - c, y + 0.5 - c)
            if rad_out - th <= dist < rad_out:
                colr = col
                if seg:
                    a = (math.degrees(math.atan2(y + 0.5 - c, x + 0.5 - c)) + 360) % 360
                    if seg[0] <= a <= seg[1]: colr = seg_col
                d.point((x, y), fill=colr)


def draw_P(d, ox, oy, col=INK, cell=2):
    for j, row in enumerate(P_ROWS):
        for i, b in enumerate(row):
            if b == "1":
                d.rectangle([ox + i * cell, oy + j * cell, ox + i * cell + cell - 1, oy + j * cell + cell - 1], fill=col)


def mark(accent=None, where=None, seg=None):
    im, d = base()
    # double ring: two equal 1-cell rings with a 1-cell gap, like the header's double rule
    ring(d, 33, 1, INK, seg=seg, seg_col=accent)
    ring(d, 31, 1, INK)
    w, h = 13 * 2, 20 * 2
    ox, oy = (N - w) // 2 + 1, (N - h) // 2          # optical centring: P is heavier on the left
    draw_P(d, ox, oy)
    if where == "stop":          # full stop after the P, on the baseline: "P."
        x = ox + 4 * 2 + 4; y = oy + h - 4
        d.rectangle([x, y, x + 3, y + 3], fill=accent)
    elif where == "apex":        # inside the bowl, against the right edge
        x = ox + 9 * 2 - 4; y = oy + 5 * 2
        d.rectangle([x, y, x + 3, y + 3], fill=accent)
    return im.resize((N * S, N * S), Image.NEAREST)


if __name__ == "__main__":
    concepts = [
        ("A  RED FULL STOP", mark(RED, "stop")),
        ("B  GREEN FULL STOP", mark(GREEN, "stop")),
        ("C  GREEN SECTOR ON RING", mark(GREEN, None, seg=(300, 340))),
        ("D  RINGS ONLY", mark()),
    ]
    for name, im in concepts:
        im.save(f"{OUT}/r4_{name.split()[0]}.png")
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
    board.save(f"{OUT}/board4.png")
    print("ok")
