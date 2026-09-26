"""Shared moai layers (B&W photo cut-out, fog/rays backdrop) and a 2D camera."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 512
here = os.path.dirname(os.path.abspath(__file__))
rnd = np.random.default_rng(7)

# ---- moai layer (grayscale + alpha), square, padded
src = Image.open(os.path.join(here, "moai_big.jpg")).convert("L")
mask = Image.open(os.path.join(here, "moai_mask.png")).convert("L")
k = src.width / 400
g = np.asarray(src).astype(float) / 255
g = np.clip((g - 0.08) / 0.62, 0, 1) ** 1.25
g = g * (0.35 + 0.6 * np.linspace(0, 1, g.shape[1])[None, :])
lum = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8))
x0, y0, x1, y1 = [int(v * k) for v in (60, 12, 375, 592)]
side = y1 - y0
MOAI = Image.new("LA", (side, side))
MOAI.paste(Image.merge("LA", (lum.crop((x0, y0, x1, y1)), mask.crop((x0, y0, x1, y1)))),
           ((side - (x1 - x0)) // 2 + int(20 * k), 0))
MOAI = MOAI.resize((1400, 1400), Image.LANCZOS)  # working resolution


# ---- background: fog + god rays, bigger than frame for parallax
def fbm(n, seed):
    r = np.random.default_rng(seed)
    acc = np.zeros((n, n))
    for o, w in ((6, 1), (12, .5), (24, .25), (48, .12)):
        acc += w * np.asarray(Image.fromarray((r.random((o, o)) * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)) / 255
    return acc / 1.87


B = 1400
fog = fbm(B, 3)
yy, xx = np.mgrid[0:B, 0:B] / B
rays = np.zeros((B, B))
ang = np.arctan2(yy - (-0.1), xx - 0.85)
for a0, wdt in ((1.9, .05), (2.1, .03), (2.35, .06), (2.6, .025), (1.7, .02)):
    rays += np.exp(-((ang - a0) / wdt) ** 2)
bgv = 0.06 + 0.16 * np.clip(fog - 0.35, 0, 1) * 2 + 0.10 * rays * (1 - yy)
BG = Image.fromarray((np.clip(bgv, 0, 1) * 255).astype(np.uint8))

yv, xv = np.mgrid[0:S, 0:S] / S
VIG = np.clip(1.35 - 1.0 * np.hypot(xv - 0.55, yv - 0.45), 0, 1)
RMASK = Image.new("L", (S, S)); ImageDraw.Draw(RMASK).rounded_rectangle([0, 0, S - 1, S - 1], 44, fill=255)


def view(img, zoom, cx, cy, rot=0.0):
    """camera crop: zoom 1 = whole image, (cx, cy) = centre in 0..1."""
    W = img.width
    cw = W / zoom
    x0 = min(max(0, cx * W - cw / 2), W - cw); y0 = min(max(0, cy * W - cw / 2), W - cw)
    pad = cw * 0.15 if rot else 0
    c = img.crop((int(x0 - pad), int(y0 - pad), int(x0 + cw + pad), int(y0 + cw + pad)))
    if rot:
        c = c.rotate(rot, resample=Image.BICUBIC)
        c = c.crop((int(pad), int(pad), int(pad + cw), int(pad + cw)))
    return c.resize((S, S), Image.LANCZOS)


def shot(zoom, cx, cy, bg_zoom=None, par=0.35, rot=0.0, blur=0, shake=(0, 0), flash=0.0, sweep=None):
    bgz = bg_zoom if bg_zoom else 1.0 + (zoom - 1) * 0.3
    bg = view(BG, bgz, 0.5 + (cx - 0.5) * par, 0.5 + (cy - 0.5) * par, rot * 0.5)
    fg = view(MOAI, zoom, cx, cy, rot)
    frame = bg.convert("L")
    frame.paste(fg.getchannel("L"), (0, 0), fg.getchannel("A"))
    a = np.asarray(frame).astype(float) / 255
    if sweep is not None:
        band = np.exp(-(((xv + yv * 0.5) - sweep) / 0.07) ** 2)
        a = a + 0.3 * band * (np.asarray(fg.getchannel("A")) / 255)
    if blur:  # horizontal motion blur for whip pans
        acc = np.zeros_like(a)
        for s in range(-blur, blur + 1, max(1, blur // 4)):
            acc += np.roll(a, s, axis=1)
        a = acc / len(range(-blur, blur + 1, max(1, blur // 4)))
    a = a * VIG + rnd.normal(0, 0.008, a.shape)
    a = np.clip(a + flash, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    if shake != (0, 0):
        big = out.resize((S + 30, S + 30))
        out = Image.new("L", (S, S)); out.paste(big, (-15 + shake[0], -15 + shake[1]))
    out = out.convert("RGBA"); out.putalpha(RMASK)
    return out




def moai_card(zoom=1.0, cx=0.5, cy=0.5):
    """static moai frame on the fog backdrop (no grain), rounded."""
    return shot(zoom, cx, cy)
