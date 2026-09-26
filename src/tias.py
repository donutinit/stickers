"""Four tía-style Pinkie Pie stickers: full-bleed cards, decorations kept off her face."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S, N = 512, int(os.environ.get("FRAMES", 12))
TRANSPARENT = os.environ.get("TRANSPARENT") == "1"
here = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(here, "Pacifico.ttf")
_em = {}


def em(c, sz, rot=0):
    k = (c, sz, rot)
    if k not in _em:
        im = Image.open(os.path.join(here, "emoji", c + ".png")).convert("RGBA").resize((sz, sz), Image.LANCZOS)
        _em[k] = im.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else im
    return _em[k]


def fancy_text(txt, size, stops, shift=0.0, maxw=490):
    f = ImageFont.truetype(FONT, size)
    while f.getbbox(txt, stroke_width=8)[2] - f.getbbox(txt, stroke_width=8)[0] > maxw:
        size -= 3; f = ImageFont.truetype(FONT, size)
    pad = 30
    l, t, r, b = f.getbbox(txt, stroke_width=8)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    org = (pad - l, pad - t)
    mask = Image.new("L", (w, h)); ImageDraw.Draw(mask).text(org, txt, font=f, fill=255)
    stroke = Image.new("L", (w, h)); ImageDraw.Draw(stroke).text(org, txt, font=f, fill=255, stroke_width=8, stroke_fill=255)
    x = np.linspace(0, 1, w)[None, :] + np.linspace(0, 0.4, h)[:, None] + shift
    x = (x % 1.0) * (len(stops) - 1)
    lo = np.floor(x).astype(int); fr = (x - lo)[..., None]
    cols = np.array(stops, float)
    grad = Image.fromarray((cols[lo] * (1 - fr) + cols[np.minimum(lo + 1, len(stops) - 1)] * fr).astype(np.uint8), "RGB")
    out = Image.new("RGBA", (w, h))
    glow = Image.new("RGBA", (w, h), (255, 80, 200, 0)); glow.putalpha(stroke.filter(ImageFilter.GaussianBlur(9)))
    shadow = Image.new("RGBA", (w, h), (120, 0, 80, 0)); shadow.putalpha(stroke)
    white = Image.new("RGBA", (w, h), (255, 255, 255, 0)); white.putalpha(stroke)
    fill = grad.convert("RGBA"); fill.putalpha(mask)
    for layer, off in ((glow, (0, 0)), (shadow, (4, 5)), (white, (0, 0)), (fill, (0, 0))):
        out.alpha_composite(layer, off)
    # PIL pads top for Pacifico's tall ascenders; crop to visible pixels + margin
    bb = out.getbbox()
    return out.crop((bb[0], max(0, bb[1] - 4), bb[2], min(h, bb[3] + 4)))


def sparkle(d, x, y, r, a, col=(255, 255, 255)):
    if r < 2:
        return
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22),
               (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=col + (a,))
    d.ellipse([x - r * .25, y - r * .25, x + r * .25, y + r * .25], fill=(255, 250, 200, a))


def gradient_bg(c0, c1, radial=False):
    yy, xx = np.mgrid[0:S, 0:S] / S
    t = np.clip(np.hypot(xx - .5, yy - .45) * 1.5, 0, 1) if radial else yy
    a, b = np.array(c0, float), np.array(c1, float)
    return Image.fromarray((a * (1 - t[..., None]) + b * t[..., None]).astype(np.uint8), "RGB").convert("RGBA")


def bokeh(img, cols, n, seed):
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y, r = rnd.randint(0, S), rnd.randint(0, S), rnd.randint(12, 45)
        c = rnd.choice(cols)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (rnd.randint(40, 90),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))


def rays(img, col, n=18, alpha=60, center=(430, 60)):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    cx, cy = center
    for k in range(n):
        a0 = 2 * math.pi * k / n; a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + 900 * math.cos(a0), cy + 900 * math.sin(a0)), (cx + 900 * math.cos(a1), cy + 900 * math.sin(a1))],
                  fill=col + (alpha,))
    img.alpha_composite(lay)


def rounded(img, r=44):
    m = Image.new("L", (S, S)); ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], r, fill=255)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(m))))
    return img


def hits(box, x, y, pad=18):
    return box[0] - pad < x < box[2] + pad and box[1] - pad < y < box[3] + pad


def load_pony(name, fit, pos):
    im = Image.open(os.path.join(here, "pp", name + ".t.png")).convert("RGBA")
    if fit[0] == "h":
        sc = fit[1] / im.height
    else:
        sc = fit[1] / im.width
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS), pos


def build(cfg):
    rnd = random.Random(cfg["seed"])
    pony, (px, py) = load_pony(cfg["pony"], cfg["fit"], cfg["pos"])
    fx0, fy0, fx1, fy1 = cfg["face"]
    face = (px + fx0 * pony.width, py + fy0 * pony.height, px + fx1 * pony.width, py + fy1 * pony.height)

    if TRANSPARENT:
        bg = Image.new("RGBA", (S, S))
    else:
        bg = gradient_bg(*cfg["bg"], radial=cfg.get("radial", False))
        cfg["decorate_bg"](bg)


    # sparkles: fixed spots off the face
    sparks = []
    while len(sparks) < cfg.get("n_sparks", 22):
        x, y = rnd.randint(20, 492), rnd.randint(20, 492)
        if not hits(face, x, y, 25):
            sparks.append((x, y, rnd.uniform(8, 20), rnd.uniform(0, 2 * math.pi)))

    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        for layer in cfg.get("behind", []):
            layer(fr, t, face)
        fr.alpha_composite(pony, (px, py))
        for k, sz, (x, y), rot in cfg["corners"]:
            e = em(k, sz, rot)
            assert not any(hits(face, cx, cy, 0) for cx, cy in ((x, y), (x + e.width, y), (x, y + e.height), (x + e.width, y + e.height))), (cfg["out"], k)
            fr.alpha_composite(e, (x, y))
        for layer in cfg.get("front", []):
            layer(fr, t, face)
        for txt, sz, st, y in cfg["texts"]:  # gradient slides each frame (shimmer)
            im = fancy_text(txt, sz, st, t)
            fr.alpha_composite(im, ((S - im.width) // 2, y))
        d = ImageDraw.Draw(fr)
        for x, y, r, ph in sparks:
            tw = max(0, math.sin(2 * math.pi * t * 2 + ph))
            sparkle(d, x, y, r * tw, int(255 * tw), (255, 185, 20) if TRANSPARENT else cfg.get("spark_col", (255, 255, 255)))
        frames.append(fr if TRANSPARENT else rounded(fr))
    return frames, face


def floaters(codes, n, seed, y0=470, y1=90, size=(34, 50)):
    """emojis drifting upward; hidden while over her face."""
    rnd = random.Random(seed)
    items = [(rnd.randint(30, 470), rnd.random(), rnd.choice(codes), rnd.randint(*size)) for _ in range(n)]

    def layer(fr, t, face):
        for x, ph, c, sz in items:
            p = (ph + t) % 1
            xx, yy = int(x + 12 * math.sin(p * 6)), int(y0 - (y0 - y1) * p)
            if hits(face, xx + sz / 2, yy + sz / 2, sz / 2):
                continue
            e = em(c, sz).copy()
            e.putalpha(e.getchannel("A").point(lambda a: int(a * min(1, (1 - p) * 2.5))))
            fr.alpha_composite(e, (xx, yy))
    return layer


def spinner(code, sz, xy, deg=90):
    def layer(fr, t, face):
        fr.alpha_composite(em(code, sz).rotate(-t * deg, resample=Image.BICUBIC), xy)
    return layer


def fluttering(code, sz, xy, amp=(20, 15)):
    def layer(fr, t, face):
        e = em(code, sz)
        e = e.resize((sz, int(sz * (0.6 + 0.4 * abs(math.cos(4 * math.pi * t))))))
        fr.alpha_composite(e, (int(xy[0] + amp[0] * math.sin(2 * math.pi * t)), int(xy[1] + amp[1] * math.cos(4 * math.pi * t))))
    return layer


GOLD = [(255, 105, 180), (255, 215, 0), (255, 255, 190), (255, 170, 20), (255, 105, 180)]
RAINBOW = [(255, 60, 170), (255, 150, 60), (255, 220, 40), (255, 110, 200), (190, 90, 255), (255, 60, 170)]
SILVER = [(200, 170, 255), (255, 255, 255), (170, 210, 255), (255, 200, 250), (200, 170, 255)]
BLUE = [(40, 120, 255), (190, 90, 255), (255, 60, 170), (40, 120, 255)]

CONFIGS = [
    dict(out="st1_buenos_dias", seed=1, pony="MLP_The_Movie_Pinkie_Pie_official_artwork", fit=("h", 470), pos=(40, 42),
         face=(0.10, 0.17, 0.55, 0.47),
         bg=((255, 244, 214), (255, 180, 200)), radial=True,
         decorate_bg=lambda bg: (rays(bg, (255, 220, 120), alpha=70, center=(440, 70)), bokeh(bg, [(255, 255, 255), (255, 200, 120)], 18, 1)),
         behind=[spinner("2600", 100, (400, 18))],
         corners=[("1f339", 96, (-10, 400), -15), ("1f337", 80, (70, 432), 10), ("1f490", 100, (410, 400), 12), ("1f338", 70, (0, 300), 5)],
         front=[floaters(["1f496", "1f495"], 5, 11), fluttering("1f98b", 62, (25, 20))],
         texts=[("Buenos Días", 80, GOLD, 300), ("¡Bendiciones!", 70, RAINBOW, 385)]),
    dict(out="st2_fin_de_semana", seed=2, pony="FANMADE_Happy_Pinkie_Pie", fit=("h", 500), pos=(140, 12),
         face=(0.10, 0.15, 0.50, 0.42),
         bg=((245, 220, 255), (200, 150, 255)), radial=True,
         decorate_bg=lambda bg: bokeh(bg, [(255, 255, 255), (255, 170, 230), (180, 230, 255)], 22, 2),
         behind=[],
         corners=[("1f388", 110, (8, 10), 8), ("1f389", 90, (20, 150), -10), ("1f388", 80, (425, 330), -12), ("1f33c", 64, (60, 250), 0)],
         front=[floaters(["2b50", "1f496", "1f31f"], 6, 22)],
         texts=[("Feliz Fin", 84, RAINBOW, 285), ("de Semana", 80, BLUE, 375)]),
    dict(out="st3_buenas_noches", seed=3, pony="FANMADE_Pinkie_Pie_vector_2", fit=("h", 490), pos=(60, 22),
         face=(0.45, 0.18, 0.83, 0.47),
         bg=((25, 20, 80), (110, 50, 150)),
         decorate_bg=lambda bg: bokeh(bg, [(255, 255, 255), (200, 170, 255)], 30, 3),
         behind=[spinner("1f319", 120, (10, 8), 20)],
         corners=[("2b50", 56, (170, 30), 15), ("1f31f", 62, (18, 170), -10)],
         front=[floaters(["2b50", "1f31f"], 5, 33, size=(26, 40))],
         spark_col=(255, 245, 200), n_sparks=30,
         texts=[("Buenas Noches", 76, SILVER, 300), ("Dulces Sueños", 70, GOLD, 385)]),
    dict(out="st4_lindo_dia", seed=4, pony="FANMADE_Pinkie_Pie_smiling", fit=("w", 500), pos=(20, 88),
         face=(0.12, 0.22, 0.56, 0.72),
         bg=((190, 235, 255), (205, 255, 225)),
         decorate_bg=lambda bg: bokeh(bg, [(255, 255, 255)], 20, 4),
         behind=[spinner("2601", 90, (400, 110), 0)],
         corners=[("2615", 96, (405, 400), 8), ("1f339", 90, (320, 420), -10), ("1f337", 70, (455, 300), 12), ("1f64f", 64, (6, 430), 0)],
         front=[floaters(["1f496", "1f495"], 4, 44, y0=470, y1=250), fluttering("1f98b", 56, (420, 200))],
         texts=[("Que Tengas", 76, RAINBOW, 2), ("Un Lindo Día", 76, GOLD, 80)]),
]

if __name__ == "__main__":
    which = sys.argv[1:] or [c["out"] for c in CONFIGS]
    for cfg in CONFIGS:
        if cfg["out"].removesuffix("_transp") not in which:
            continue
        frames, face = build(cfg)
        cfg["out"] += "_transp" if TRANSPARENT else ""
        d = os.path.join(here, "sframes", cfg["out"]); os.makedirs(d, exist_ok=True)
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        # debug preview with face box
        p = frames[0].copy(); ImageDraw.Draw(p).rectangle(face, outline="cyan", width=2)
        p.save(os.path.join(here, "sframes", cfg["out"] + "_dbg.png"))
        print(cfg["out"], [int(v) for v in face])
