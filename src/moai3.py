"""Moai series: eyebrow raise, 🗿🍷, OK., deal-with-it glasses, fried ES VERDAD."""
import os
import numpy as np
from PIL import Image, ImageDraw
import moai_common as mc
import m6
from deepfry import fry

S = 512
here = os.path.dirname(os.path.abspath(__file__))
EYE = (0.556, 0.206)  # eye socket centre in MOAI layer coords (0..1)
BROW = (0.43, 0.67, 0.06, 0.26)  # x0, x1, y0, y1 of the brow region to lift


def raise_brow(amount):
    """warp the MOAI layer so the brow ridge lifts by `amount` (fraction of layer height)."""
    a = np.asarray(mc.MOAI)
    H, W = a.shape[:2]
    y, x = np.mgrid[0:H, 0:W] / H
    x0, x1, y0, y1 = BROW
    wx = np.clip(np.minimum((x - x0) / 0.06, (x1 - x) / 0.06), 0, 1)
    wy = np.sin(np.clip((y - y0) / (y1 - y0), 0, 1) * np.pi)  # 0 at edges, peak mid-brow
    wy *= (x - x0) / (x1 - x0) * 0.6 + 0.4  # outer side lifts more (skeptical look)
    sy = np.clip((y + amount * wx * wy) * H, 0, H - 1).astype(int)
    sx = (x * W).astype(int)
    return Image.fromarray(a[sy, sx], "LA")


def with_layer(layer, fn):
    old = mc.MOAI
    mc.MOAI = layer
    try:
        return fn()
    finally:
        mc.MOAI = old


def ceja():
    frames, delays = [], []
    seq = [(0, 0, (0, 0))] * 4 + [(0.35, 0, (0, 0)), (0.8, 0.15, (8, -6)), (1.0, 0.05, (-5, 4)), (1.0, 0, (0, 0))] + [(1.0, 0, (0, 0))] * 4
    for i, (r, fl, sh) in enumerate(seq):
        layer = raise_brow(0.045 * r)
        z = 1.8 + 0.25 * (i / (len(seq) - 1))
        frames.append(with_layer(layer, lambda: mc.shot(z, EYE[0] - 0.02, EYE[1] + 0.08, shake=sh, flash=fl)))
        delays.append(500 if i == 0 else 800 if i == len(seq) - 1 else 80)
    return frames, delays


def vino():
    fr = mc.moai_card(1.15, 0.5, 0.48)
    glass = m6.emoji("1f377", 190).rotate(12, expand=True, resample=Image.BICUBIC)
    fr.alpha_composite(glass, (322, 290))
    return fr


def ok():
    fr = mc.moai_card(1.2, 0.52, 0.45)
    m6.meme_text(fr, "OK.", size=150, y=440)
    return fr


def profile_glasses(p=8):
    """pixel shades seen from the side: one lens + temple arm going back."""
    W, H = 30, 7
    g = Image.new("RGBA", (W * p, H * p))
    d = ImageDraw.Draw(g)
    px = lambda x, y, c: d.rectangle([x * p, y * p, x * p + p - 1, y * p + p - 1], fill=c)
    for x in range(0, 18):  # temple arm
        px(x, 1, "black")
    for x in range(17, 30):
        px(x, 0, "black")
    for y in range(1, 6):
        inset = 1 if y == 5 else 0
        for x in range(18 + inset, 30 - inset):
            px(x, y, "black")
    px(20, 1, "white"); px(21, 1, "white"); px(21, 2, "white"); px(22, 2, "white")
    return g


def lentes():
    G = profile_glasses(10)
    frames, delays = [], []
    z, cx, cy = 1.35, 0.52, 0.4
    # where the eye lands in frame coords for this camera
    ex = (EYE[0] - (cx - 0.5 / z)) * z * S
    ey = (EYE[1] - (cy - 0.5 / z)) * z * S
    lens_c = (24 * 10, 3 * 10)  # lens centre inside the glasses sprite
    tx, ty = ex - 6 - lens_c[0], ey + 8 - lens_c[1]
    steps = 8
    for i in range(steps + 6):
        k = min(1, i / steps)
        sh = {steps: (12, -8), steps + 1: (-7, 5), steps + 2: (3, -2)}.get(i, (0, 0))
        fr = mc.shot(z, cx, cy)
        fr.alpha_composite(G, (int(tx), int(-G.height + (ty + G.height) * k * k)))
        if i >= steps:
            m6.meme_text(fr, "DEAL WITH IT", size=90, y=450)
        if sh != (0, 0):
            big = fr.resize((S + 30, S + 30))
            fr2 = Image.new("RGBA", (S, S), (0, 0, 0, 255)); fr2.alpha_composite(big, (-15 + sh[0], -15 + sh[1]))
            fr2.putalpha(mc.RMASK); fr = fr2
        frames.append(fr)
        delays.append(900 if i == steps + 5 else 90)
    return frames, delays


def es_verdad():
    fr = mc.moai_card(1.1, 0.5, 0.47)
    m6.meme_text(fr, "ES VERDAD", size=110, y=445)
    out = fry(fr)
    out.putalpha(mc.RMASK)
    return out


if __name__ == "__main__":
    base = os.path.join(here, "moai3frames"); os.makedirs(base, exist_ok=True)
    for name in ("vino", "ok", "es_verdad"):
        globals()[name]().save(os.path.join(base, name + ".png")); print(name)
    for name in ("ceja", "lentes"):
        frames, delays = globals()[name]()
        d = os.path.join(base, name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
        print(name, len(frames))
