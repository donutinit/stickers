import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(7)
S, N = 512, 8
here = os.path.dirname(os.path.abspath(__file__))
em = lambda c, sz: Image.open(os.path.join(here, "emoji", c + ".png")).convert("RGBA").resize((sz, sz), Image.LANCZOS)
FONT = os.path.join(here, "Pacifico.ttf")

pinkie = Image.open(os.path.join(here, "Pinkie_Pie_high_resolution_from_HubWorld.png")).convert("RGBA")
pinkie = pinkie.crop(pinkie.getbbox())
pinkie.thumbnail((330, 330), Image.LANCZOS)


def fancy_text(txt, size, stops, shift):
    """cursive text: moving gradient fill, white outline, pink glow, drop shadow."""
    f = ImageFont.truetype(FONT, size)
    pad = 30
    l, t, r, b = f.getbbox(txt, stroke_width=8)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    org = (pad - l, pad - t)
    mask = Image.new("L", (w, h)); ImageDraw.Draw(mask).text(org, txt, font=f, fill=255)
    stroke = Image.new("L", (w, h)); ImageDraw.Draw(stroke).text(org, txt, font=f, fill=255, stroke_width=8, stroke_fill=255)

    # diagonal gradient that slides each frame (shimmer)
    x = np.linspace(0, 1, w)[None, :] + np.linspace(0, 0.4, h)[:, None] + shift
    x = (x % 1.0) * (len(stops) - 1)
    lo = np.floor(x).astype(int); fr = (x - lo)[..., None]
    cols = np.array(stops, float)
    grad = cols[lo] * (1 - fr) + cols[np.minimum(lo + 1, len(stops) - 1)] * fr
    grad = Image.fromarray(grad.astype(np.uint8), "RGB")

    out = Image.new("RGBA", (w, h))
    glow = Image.new("RGBA", (w, h), (255, 80, 200, 0)); glow.putalpha(stroke.filter(ImageFilter.GaussianBlur(9)))
    shadow = Image.new("RGBA", (w, h), (120, 0, 80, 0)); shadow.putalpha(stroke)
    out.alpha_composite(glow)
    out.alpha_composite(shadow, (4, 5))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 0)); white.putalpha(stroke)
    out.alpha_composite(white)
    fill = grad.convert("RGBA"); fill.putalpha(mask)
    out.alpha_composite(fill)
    return out


def sparkle(d, x, y, r, a):
    """4-point twinkle star."""
    if r < 2:
        return
    col = (255, 255, 255, a)
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22),
               (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=col)
    d.ellipse([x - r * .25, y - r * .25, x + r * .25, y + r * .25], fill=(255, 250, 200, a))


RAINBOW = [(255, 60, 170), (255, 150, 60), (255, 220, 40), (255, 110, 200), (190, 90, 255), (255, 60, 170)]
GOLD = [(255, 105, 180), (255, 215, 0), (255, 255, 190), (255, 170, 20), (255, 105, 180)]

SPARKS = [(random.randint(20, 492), random.randint(20, 492), random.uniform(8, 22), random.uniform(0, 2 * math.pi)) for _ in range(22)]
HEARTS = [(random.randint(40, 470), random.uniform(0, 1), random.choice(["1f496", "1f495"]), random.randint(34, 50)) for _ in range(5)]
FLOWERS = [("1f339", 92, (-8, 400), -15), ("1f338", 78, (60, 430), 10), ("1f33a", 88, (410, 395), 12),
           ("1f33c", 72, (350, 440), -8), ("1f33b", 70, (0, 330), 5), ("1f338", 64, (455, 320), -20)]
FLOWER_IMG = {k: em(k, sz).rotate(rot, expand=True, resample=Image.BICUBIC) for k, sz, _, rot in FLOWERS}
SUN = em("2600", 86)
BUTTERFLY = em("1f98b", 70)

frames = []
for i in range(N):
    t = i / N
    fr = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # soft pink halo behind Pinkie
    halo = Image.new("L", (S, S)); ImageDraw.Draw(halo).ellipse([70, 90, 442, 450], fill=150)
    halo_l = Image.new("RGBA", (S, S), (255, 200, 235, 0)); halo_l.putalpha(halo.filter(ImageFilter.GaussianBlur(40)))
    # halo dropped: too heavy for the 500KB sticker limit

    sun = SUN.rotate(-t * 90, resample=Image.BICUBIC)
    fr.alpha_composite(sun, (418, 88))

    bob = 0  # static Pinkie keeps frame diffs small
    fr.alpha_composite(pinkie, ((S - pinkie.width) // 2, 118 + bob))

    for k, sz, (x, y), rot in FLOWERS:
        fr.alpha_composite(FLOWER_IMG[k], (x, y))

    for x, ph, k, sz in HEARTS:  # hearts floating up
        p = (ph + t) % 1
        h = em(k, sz); h.putalpha(h.getchannel("A").point(lambda a: int(a * min(1, (1 - p) * 2.5))))
        fr.alpha_composite(h, (int(x + 12 * math.sin(p * 6)), int(430 - 330 * p)))

    bx, by = 40 + 20 * math.sin(2 * math.pi * t), 110 + 15 * math.cos(4 * math.pi * t)
    bf = BUTTERFLY.resize((70, int(70 * (0.6 + 0.4 * abs(math.cos(2 * math.pi * t * 2))))))
    fr.alpha_composite(bf, (int(bx), int(by)))

    top = fancy_text("Buenos Días", 76, GOLD, 0.15)
    fr.alpha_composite(top, ((S - top.width) // 2, -22))
    bot = fancy_text("¡Alegría!", 84, RAINBOW, 0.0)
    fr.alpha_composite(bot, ((S - bot.width) // 2, S - bot.height + 18))

    d = ImageDraw.Draw(fr)
    for x, y, r, ph in SPARKS:
        tw = max(0, math.sin(2 * math.pi * t * 2 + ph))
        sparkle(d, x, y, r * tw, int(255 * tw))

    frames.append(fr)

os.makedirs(os.path.join(here, "tframes"), exist_ok=True)
for i, f in enumerate(frames):
    f.save(os.path.join(here, "tframes", f"f{i:02d}.png"))
print("ok")
