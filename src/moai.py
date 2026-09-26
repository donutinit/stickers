"""Moai gigachad: B&W, hard light, grain, slow push-in, vine-boom punch."""
import os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 512
here = os.path.dirname(os.path.abspath(__file__))
rnd = np.random.default_rng(7)

src = Image.open(os.path.join(here, "moai_big.jpg")).convert("L")
mask = Image.open(os.path.join(here, "moai_mask.png")).convert("L")
k = src.width / 400  # mask was traced on a 400px-wide preview

g = np.asarray(src).astype(float) / 255
g = np.clip((g - 0.08) / 0.62, 0, 1) ** 1.25  # crush blacks, punchy mids
h, w = g.shape
xx = np.linspace(0, 1, w)[None, :]
g = g * (0.35 + 0.6 * xx)  # key light from the right (face side)
g = np.clip(g, 0, 1) * (np.asarray(mask) / 255)
base = Image.fromarray((g * 255).astype(np.uint8))

# whole head incl. jaw, padded to a square on black
x0, y0, x1, y1 = [int(v * k) for v in (60, 12, 375, 592)]
side = y1 - y0
face = Image.new("L", (side, side))
face.paste(base.crop((x0, y0, x1, y1)), ((side - (x1 - x0)) // 2 + int(20 * k), 0))


def vignette():
    y, x = np.mgrid[0:S, 0:S] / S
    return np.clip(1.35 - 1.0 * np.hypot(x - 0.55, y - 0.45), 0, 1)


VIG = vignette()


def render(zoom, cx=0.5, cy=0.5, sweep=None, shake=(0, 0), flash=0.0):
    W = face.width
    cw = W / zoom
    x0 = cx * W - cw / 2; y0 = cy * W - cw / 2
    x0 = min(max(0, x0), W - cw); y0 = min(max(0, y0), W - cw)
    im = face.crop((int(x0), int(y0), int(x0 + cw), int(y0 + cw))).resize((S, S), Image.LANCZOS)
    a = np.asarray(im).astype(float) / 255
    if sweep is not None:  # specular band sliding across the stone
        y, x = np.mgrid[0:S, 0:S] / S
        band = np.exp(-(((x + y * 0.5) - sweep) / 0.07) ** 2)
        a = a + 0.35 * band * (a > 0.05)
    a = a * VIG
    a = a + rnd.normal(0, 0.018, a.shape)  # film grain
    a = np.clip(a + flash, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8)).convert("RGBA")
    if shake != (0, 0):
        big = out.resize((S + 30, S + 30))
        out = Image.new("RGBA", (S, S), (0, 0, 0, 255))
        out.paste(big, (-15 + shake[0], -15 + shake[1]))
    m = Image.new("L", (S, S)); ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], 44, fill=255)
    out.putalpha(m)
    return out


frames, delays = [], []
N = 14
for i in range(N):  # slow dramatic push-in with a light sweep
    t = i / (N - 1)
    frames.append(render(1.0 + 0.1 * t, 0.52, 0.5, sweep=-0.3 + 1.9 * t)); delays.append(90)
for i, (z, sh, fl) in enumerate([(1.55, (14, -10), 0.6), (1.5, (-9, 7), 0.25), (1.52, (5, -4), 0.08), (1.5, (0, 0), 0)]):
    frames.append(render(z * 0.85, 0.6, 0.38, shake=sh, flash=fl)); delays.append(70)
delays[-1] = 900

d = os.path.join(here, "moaiframes"); os.makedirs(d, exist_ok=True)
for f in os.listdir(d):
    os.remove(os.path.join(d, f))
for i, f in enumerate(frames):
    f.save(os.path.join(d, f"f{i:02d}.png"))
open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
print(len(frames))
