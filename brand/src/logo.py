"""Refined profile-picture concepts for The Pixel Paddock. 72x72 design grid, x15 -> 1080."""
import os, math
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out_logo"); os.makedirs(OUT, exist_ok=True)
N, S = 72, 15
PAPER = (20, 18, 15); INK = (236, 227, 207); RED = (232, 35, 63); MUTE = (90, 84, 74)
PURPLE = (168, 85, 247)


def canvas(bg=PAPER):
    im = Image.new("RGB", (N, N), bg); return im, ImageDraw.Draw(im)


def r(d, x0, y0, x1, y1, c): d.rectangle([x0, y0, x1, y1], fill=c)


def final(im): return im.resize((N * S, N * S), Image.NEAREST)


def ring(d, cx, cy, rad, th, col, a0=0, a1=360, check=None):
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            dist = math.hypot(dx, dy)
            if rad - th <= dist <= rad:
                ang = (math.degrees(math.atan2(dy, dx)) + 360) % 360
                if a0 <= ang <= a1 or (a0 > a1 and (ang >= a0 or ang <= a1)):
                    if check and check[0] <= ang <= check[1]:
                        c = INK if ((x // 2) + (y // 2)) % 2 == 0 else PAPER
                        d.point((x, y), fill=c)
                    else:
                        d.point((x, y), fill=col)


# ------------------------------------------------------------------ 1  APEX P
def apex_p():
    """A single geometric P; its bowl is a racing line, the apex marked by one red pixel block."""
    im, d = canvas()
    st = 7                                # stroke
    x0, y0, h = 24, 16, 40                # stem
    r(d, x0, y0, x0 + st - 1, y0 + h - 1, INK)
    # bowl: stepped quarter-circle corners (pixel-precise), outer 22 wide x 24 tall
    bx1, by0, by1 = x0 + 24, y0, y0 + 23
    r(d, x0, by0, bx1 - 6, by0 + st - 1, INK)              # top bar
    r(d, x0, by1 - st + 1, bx1 - 6, by1, INK)              # bottom bar
    # right side with rounded corners made from steps
    for y in range(by0, by1 + 1):
        t = y - by0
        inset = 0
        if t < 6: inset = [5, 3, 2, 1, 1, 0][t]
        if t > 17: inset = [0, 1, 1, 2, 3, 5][t - 18]
        r(d, bx1 - st + 1 - (0), y, bx1 - inset, y, INK) if inset < st else None
        r(d, bx1 - 6 - st + 1, y, bx1 - inset, y, INK) if t < st or t > by1 - by0 - st else None
    # tidy: fill right stroke fully between corners
    r(d, bx1 - st + 1, by0 + 5, bx1, by1 - 5, INK)
    # apex: red block at the inner right of the bowl
    r(d, bx1 - st - 3, by0 + 10, bx1 - st - 1, by0 + 13, RED)
    return final(im)


# ------------------------------------------------------------------ 2  ROUNDEL
def roundel():
    """Pixel ring like a gauge / steering wheel; one quarter is a chequered flag; red dot centre."""
    im, d = canvas()
    ring(d, 36, 36, 26, 5, INK, check=(300, 360))
    r(d, 34, 34, 37, 37, RED)
    return final(im)


# ------------------------------------------------------------------ 3  PURPLE SECTORS
def sectors():
    """Three purple bars = three purple sectors = a perfect lap. Ultra-minimal, data-native."""
    im, d = canvas()
    for k in range(3):
        y = 24 + k * 9
        r(d, 18, y, 53, y + 5, PURPLE)
    # tiny cream lap marker
    r(d, 18, 52, 21, 53, INK); r(d, 24, 52, 27, 53, INK); r(d, 30, 52, 33, 53, INK)
    return final(im)


# ------------------------------------------------------------------ 4  PP LIGATURE
def pp_ligature():
    """Two Ps sharing one stem: cream P left, red P right, offset like a motion trail."""
    im, d = canvas()
    st = 6
    def P(x, y, col):
        r(d, x, y, x + st - 1, y + 38, col)                # stem
        r(d, x, y, x + 15, y + st - 1, col)                # top
        r(d, x, y + 16, x + 15, y + 16 + st - 1, col)      # middle
        r(d, x + 16, y + 1, x + 16 + st - 1, y + 20, col)  # bowl right
        r(d, x + 15, y, x + 16, y, col); r(d, x + 15, y + 21, x + 16, y + 21, col)
    P(17, 17, INK)
    P(34, 17, RED)
    return final(im)


# ------------------------------------------------------------------ 5  TOP-DOWN CAR
def car_badge():
    """One clean top-down car, generous negative space, a hairline ring."""
    im, d = canvas()
    ring(d, 36, 36, 30, 1, MUTE)
    k = (8, 8, 9)
    cx, y = 32, 14
    r(d, cx - 4, y, cx + 11, y + 2, RED)                      # front wing
    r(d, cx + 2, y + 3, cx + 5, y + 12, INK)                  # nose
    r(d, cx - 3, y + 6, cx, y + 13, k); r(d, cx + 7, y + 6, cx + 10, y + 13, k)
    r(d, cx, y + 14, cx + 7, y + 34, INK)                     # tub
    r(d, cx - 2, y + 20, cx + 9, y + 31, INK)                 # sidepods
    r(d, cx + 3, y + 17, cx + 4, y + 18, RED)                 # helmet
    r(d, cx - 4, y + 27, cx - 1, y + 36, k); r(d, cx + 8, y + 27, cx + 11, y + 36, k)
    r(d, cx - 2, y + 39, cx + 9, y + 41, INK)                 # rear wing
    return final(im)


def circle(im, size, bg):
    sm = im.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0); ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGB", (size, size), bg); out.paste(sm, (0, 0), mask); return out


if __name__ == "__main__":
    concepts = [("1 APEX P", apex_p()), ("2 ROUNDEL", roundel()), ("3 PURPLE SECTORS", sectors()),
                ("4 PP LIGATURE", pp_ligature()), ("5 CAR BADGE", car_badge())]
    for name, im in concepts:
        im.save(f"{OUT}/logo_{name.split()[0]}.png")
    # board: big circle + 110 + 44 on light and dark
    cw = 300
    board = Image.new("RGB", (len(concepts) * cw + 40, 560), (245, 245, 245)); bd = ImageDraw.Draw(board)
    dark = Image.new("RGB", (len(concepts) * cw + 40, 140), (0, 0, 0))
    for k, (name, im) in enumerate(concepts):
        x = 20 + k * cw
        board.paste(circle(im, 240, (245, 245, 245)), (x + 20, 30))
        board.paste(circle(im, 110, (245, 245, 245)), (x + 20, 300))
        board.paste(circle(im, 44, (245, 245, 245)), (x + 150, 333))
        bd.text((x + 20, 440), name, fill=(30, 30, 30))
        dark.paste(circle(im, 110, (0, 0, 0)), (x + 20, 15)); dark.paste(circle(im, 44, (0, 0, 0)), (x + 150, 48))
    board.paste(dark, (0, 470 - 30 + 50))
    board = board.crop((0, 0, board.width, 470 + 140 - 30 + 50))
    board.save(f"{OUT}/board.png")
    print("ok")
