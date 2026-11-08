"""Pixel Paddock layout A+ : small wordmark header, airy headline, sector pagination, HUD."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from pp import text, para, tlen, cap, R, C, W, H, G, framed, contact_sheet

SECT = [(168, 85, 247), (57, 255, 20), (250, 204, 21)]   # S1 purple, S2 green, S3 yellow
HEAD_TOP, HEAD_LH, BODY_LH = 165, 75, 45


def flag(d, x, y, n=5, s=5):
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0: R(d, x + i * s, y + j * s, x + (i + 1) * s, y + (j + 1) * s, C["ink"])


def page(n, total, date):
    im = Image.new("RGB", (W, H), C["paper"]); d = ImageDraw.Draw(im); r = random.Random(n)
    for _ in range(1500):
        x, y = r.randrange(0, W, G), r.randrange(0, H, G); R(d, x, y, x + G, y + G, C["speck"])
    flag(d, 40, 45)
    text(im, 85, 70, "THE PIXEL PADDOCK", "labelb", C["ink"])
    text(im, W - 40 - tlen("label", date), 70, date, "label", C["mute"])
    R(d, 40, 90, W - 40, 95, C["ink"]); R(d, 40, 100, W - 40, 105, C["ink"])
    return im, d


def footer(im, d, n, txt, total=3):
    R(d, 40, H - 90, W - 40, H - 85, C["ink"])
    text(im, 40, H - 40, "F1 NEWS", "label", C["red"])
    text(im, 40 + tlen("label", "F1 NEWS") + 30, H - 40, txt, "label", C["ink"])
    lw = tlen("label", "S1"); step = lw + 10 + 45 + 25
    x = W - 40 - total * step + 25
    for i in range(total):
        on = i < n
        text(im, x, H - 40, f"S{i+1}", "label", C["ink"] if on else C["mute"])
        R(d, x + lw + 10, H - 60, x + lw + 55, H - 40, SECT[i] if on else C["rule"])
        x += step


def headline(im, t, top=HEAD_TOP):
    return para(im, 40, top, t, "head", C["ink"], 1000, HEAD_LH)


def body(im, top, t, col=None, maxw=1000, x=40):
    return para(im, x, top, t, "body", col or C["ink"], maxw, BODY_LH)


def cover_image(im, d, scene, top, hud):
    y = framed(im, scene, 40, top)
    text(im, W - 60 - tlen("label", hud), y - 30, hud, "label", C["ink"])
    R(d, W - 60 - tlen("label", hud) - 25, y - 50, W - 60 - tlen("label", hud) - 10, y - 35, C["red"])
    return y


def fig(im, base, caption, n=1):
    lab = f"FIG.{n}"; text(im, 40, base, lab, "label", C["red"])
    text(im, 40 + tlen("label", lab) + 20, base, caption, "body", C["ink"])


def box(im, d, top, h, title):
    R(d, 40, top, W - 40, top + h, C["ink"]); R(d, 45, top + 5, W - 45, top + h - 5, C["box"])
    text(im, 70, top + 50, title, "labelb", C["red"])


def fact_file(im, d, top, rows, title="FACT FILE", keyw=330):
    h = 85 + 50 * len(rows); box(im, d, top, h, title); b = top + 100
    for k, v in rows:
        text(im, 70, b, k, "label", C["mute"]); text(im, 70 + keyw, b, v, "body", C["ink"]); b += 50
    return top + h
