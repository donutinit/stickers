"""More Pinkie Pie 'OKI DOKI!' stickers (meme style: full height, white Impact)."""
import math, os, random
from PIL import Image, ImageDraw
import dash

dash.TEXT = "OKI DOKI!"
S = dash.S
here = dash.here


def load(path, h=None, w=None):
    im = Image.open(os.path.join(here, path)).convert("RGBA")
    im = im.crop(im.getbbox())
    sc = h / im.height if h else w / im.width
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def emoji(code, sz):
    return Image.open(os.path.join(here, "emoji", code + ".png")).convert("RGBA").resize((sz, sz), Image.LANCZOS)


def wink():
    p = load("FANMADE_Pinkie_Pie_wink_vector.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(p, ((S - p.width) // 2, 0))
    dash.meme_text(fr, y=445)
    return [fr], [0]


CONFETTI = [(255, 80, 160), (255, 210, 40), (80, 200, 255), (140, 230, 90), (190, 120, 255)]


def bounce():
    rnd = random.Random(8)
    p = load("pp/FANMADE_Happy_Pinkie_Pie.png", h=470)
    balloons = [(emoji("1f388", 110), (4, 30), 0.0), (emoji("1f388", 90), (420, 60), 0.5)]
    bits = [(rnd.randint(0, S), rnd.random(), rnd.choice(CONFETTI), rnd.uniform(-1, 1)) for _ in range(40)]
    N = 12
    frames = []
    for i in range(N):
        t = i / N
        fr = Image.new("RGBA", (S, S))
        for b, (x, y), ph in balloons:
            fr.alpha_composite(b, (x, int(y + 12 * math.sin(2 * math.pi * (t + ph)))))
        hop = abs(math.sin(math.pi * t * 2))  # two hops per loop
        squash = 1 - 0.08 * (1 - hop) ** 4  # squash on landing
        q = p.resize((int(p.width * (2 - squash)), int(p.height * squash)))
        fr.alpha_composite(q, ((S - q.width) // 2 + 30, int(S - q.height - 70 * hop)))
        d = ImageDraw.Draw(fr)
        for x, ph, col, spin in bits:
            yy = ((ph + t) % 1) * (S + 40) - 20
            xx = x + 14 * math.sin(yy / 40 + ph * 6)
            a = math.radians((yy * 3 * spin) % 360)
            dx, dy = 7 * math.cos(a), 4
            d.polygon([(xx - dx, yy - dy), (xx + dx, yy - dy), (xx + dx, yy + dy), (xx - dx, yy + dy)], fill=col + (255,))
        dash.meme_text(fr, 1.0 + 0.06 * hop, dy=-int(10 * hop), y=445)
        frames.append(fr)
    return frames, [90] * N


def wobble():
    p = load("pp/FANMADE_Pinkie_Pie_smiling.png", w=600)
    N = 12
    frames = []
    for i in range(N):
        t = i / N
        ang = 9 * math.sin(2 * math.pi * t)
        q = p.rotate(ang, center=(p.width * 0.35, p.height * 0.9), resample=Image.BICUBIC)
        fr = Image.new("RGBA", (S, S))
        fr.alpha_composite(q, ((S - q.width) // 2 + 20, S - q.height + 75))
        dash.meme_text(fr, 1.0, dx=int(-6 * math.sin(2 * math.pi * t)), y=445)
        frames.append(fr)
    return frames, [80] * N


if __name__ == "__main__":
    for name in ("wink", "bounce", "wobble"):
        frames, delays = globals()[name]()
        d = os.path.join(here, "oframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        with open(os.path.join(d, "delays.txt"), "w") as fh:
            fh.write(" ".join(map(str, delays)))
        print(name, len(frames))
