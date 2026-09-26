"""Rainbow Dash 'ME VALE VERGA' animated stickers."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 512
here = os.path.dirname(os.path.abspath(__file__))
IMPACT = os.path.expanduser("~/.local/share/fonts/Impact.TTF")
RAINBOW = [(238, 64, 53), (243, 146, 55), (253, 246, 99), (103, 190, 90), (50, 150, 220), (110, 80, 180)]
TEXT = "ME VALE VERGA"


def pony(name, h=None, w=None, flip=False):
    im = Image.open(os.path.join(here, "rd", name + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    sc = h / im.height if h else w / im.width
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def meme_text(fr, scale=1.0, dx=0, dy=0, alpha=255, y=440):
    base = 92  # shrink until the resting size fits with its stroke
    while ImageFont.truetype(IMPACT, base).getbbox(TEXT, stroke_width=8)[2] > 484:
        base -= 2
    size = int(base * scale)
    f = ImageFont.truetype(IMPACT, size)
    lay = Image.new("RGBA", (S, S))
    ImageDraw.Draw(lay).text((S / 2 + dx, y + dy), TEXT, font=f, fill="white", stroke_width=max(4, int(8 * scale)),
                             stroke_fill="black", anchor="mm")
    if alpha < 255:
        lay.putalpha(lay.getchannel("A").point(lambda a: a * alpha // 255))
    fr.alpha_composite(lay)


def sky():
    yy = np.linspace(0, 1, S)[:, None, None]
    a, b = np.array([60, 150, 250.]), np.array([185, 225, 255.])
    img = Image.fromarray(np.repeat((a * (1 - yy) + b * yy), S, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    rnd = random.Random(5)
    for cx, cy in ((80, 120), (420, 200), (250, 60), (60, 330), (460, 380)):
        for _ in range(6):
            r = rnd.randint(22, 42)
            x, y = cx + rnd.randint(-45, 45), cy + rnd.randint(-12, 12)
            d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(255, 255, 255, 170))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))
    return img


def rings(fr, c, r, width, alpha=255):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for k, col in enumerate(RAINBOW):
        rr = r - k * width
        if rr > 0:
            d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], outline=col + (alpha,), width=int(width) + 1)
    fr.alpha_composite(lay)


def trail(fr, pts, width=8, alpha=255):
    """rainbow ribbon along a polyline (6 parallel bands)."""
    if len(pts) < 2:
        return
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for k, col in enumerate(RAINBOW):
        off = (k - 2.5) * width
        band = []
        for i, (x, y) in enumerate(pts):
            x2, y2 = pts[min(i + 1, len(pts) - 1)]
            x1, y1 = pts[max(i - 1, 0)]
            tx, ty = x2 - x1, y2 - y1
            n = math.hypot(tx, ty) or 1
            band.append((x - ty / n * off, y + tx / n * off))
        d.line(band, fill=col + (alpha,), width=int(width) + 2, joint="curve")
    fr.alpha_composite(lay)


def rays(fr, angle, alpha=150, n=12, c=(256, 230)):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for k in range(n):
        a0 = math.radians(angle + k * 360 / n); a1 = a0 + math.radians(360 / n / 2)
        col = RAINBOW[k % 6]
        d.polygon([c, (c[0] + 800 * math.cos(a0), c[1] + 800 * math.sin(a0)), (c[0] + 800 * math.cos(a1), c[1] + 800 * math.sin(a1))],
                  fill=col + (alpha,))
    fr.alpha_composite(lay)


def speedlines(fr, rnd, n=14, alpha=160):
    d = ImageDraw.Draw(fr)
    for _ in range(n):
        y = rnd.randint(0, S); x = rnd.randint(-100, S); L = rnd.randint(60, 180)
        d.line([(x, y), (x + L, y)], fill=(255, 255, 255, alpha), width=rnd.randint(2, 4))


def flash(fr, amt):
    a = fr.getchannel("A")
    out = Image.blend(fr.convert("RGB"), Image.new("RGB", (S, S), "white"), amt).convert("RGBA")
    out.putalpha(a)
    return out


def shake(fr, amt, rnd):
    if amt <= 0:
        return fr
    out = Image.new("RGBA", (S, S))
    big = fr.resize((S + 24, S + 24))
    out.alpha_composite(big, (-12 + rnd.randint(-amt, amt), -12 + rnd.randint(-amt, amt)))
    return out


def sparkle(d, x, y, r, a):
    if r < 2:
        return
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22),
               (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=(255, 255, 255, a))


# ---------------------------------------------------------------- 1: rainplosión
def rainplosion():
    rnd = random.Random(1)
    bg = sky()
    flyer = pony("FANMADE_Rainbow_Dash_Flying_downwards", w=230)
    stand = pony("MLP_The_Movie_Rainbow_Dash_official_artwork", h=440)
    boom_c = (256, 250)
    frames, delays = [], []
    INTRO = 4
    s0 = 0.3  # start partway in so she's visible from frame 0
    path = [(620 - 380 * (s0 + (1 - s0) * t / (INTRO - 1)), -80 + 330 * (s0 + (1 - s0) * t / (INTRO - 1))) for t in range(INTRO)]
    for i in range(INTRO + 16):
        fr = bg.copy()
        if i < INTRO:  # streak in
            speedlines(fr, rnd, 8 + i * 2)
            pts = [(620 - 380 * s, -80 + 330 * s) for s in np.linspace(0, s0 + (1 - s0) * i / (INTRO - 1), 12)]
            trail(fr, pts, width=6 + i)
            x, y = path[i]
            fr.alpha_composite(flyer, (int(x - flyer.width * .35), int(y - flyer.height * .5)))
            delays.append(70)
        else:
            k = i - INTRO
            if k < 8:  # sonic rainboom
                rings(fr, boom_c, 50 + 95 * k, 10 + 3 * k, alpha=int(255 * (1 - k / 8)))
                if k < 3:
                    rings(fr, boom_c, 20 + 60 * k, 6 + 2 * k)
            if k >= 1:
                rays(fr, i * 6, alpha=70 if k > 4 else 40)
            if k >= 1:  # epic landing with a little bounce
                sc = {1: 1.18, 2: 0.94, 3: 1.04}.get(k, 1.0)
                st = stand.resize((int(stand.width * sc), int(stand.height * sc)), Image.LANCZOS)
                fr.alpha_composite(st, ((S - st.width) // 2, S - st.height - 6))
                if k in (1, 2, 3):  # dust puffs
                    d = ImageDraw.Draw(fr)
                    for s in (-1, 1):
                        for j in range(4):
                            r = 18 + 10 * k + j * 4
                            cx = 256 + s * (160 + 25 * k + j * 22)
                            d.ellipse([cx - r, 470 - r * .6, cx + r, 470 + r * .6], fill=(255, 255, 255, 200 - 50 * k))
            if k >= 5:  # text slam
                sc = {5: 2.2, 6: 1.3, 7: 0.93}.get(k, 1.0)
                meme_text(fr, sc)
            if k >= 8:
                d = ImageDraw.Draw(fr)
                for j in range(6):
                    ph = (i * 0.9 + j * 1.3)
                    sparkle(d, 60 + j * 80, 60 + (j * 97) % 250, 14 * max(0, math.sin(ph)), 255)
            fr = shake(fr, {0: 16, 1: 12, 2: 8, 3: 5, 5: 10, 6: 5}.get(k, 0), rnd)
            if k == 0:
                fr = flash(fr, 0.85)
            elif k == 1:
                fr = flash(fr, 0.4)
            delays.append(700 if k == 15 else 70 if k < 8 else 90)
        frames.append(fr)
    return frames, delays


# ---------------------------------------------------------------- 2: chill con lentes
def chill():
    rnd = random.Random(2)
    dash = pony("FANMADE_Rainbow_Dash_chillin", h=470)
    frames, delays = [], []
    N = 12
    for i in range(N):
        t = i / N
        fr = Image.new("RGBA", (S, S))
        rays(fr, t * 30, alpha=255, n=12, c=(256, 220))
        m = Image.new("L", (S, S)); ImageDraw.Draw(m).ellipse([6, -30, 506, 470], fill=255)
        fr.putalpha(Image.fromarray(np.minimum(np.asarray(fr.getchannel("A")), np.asarray(m.filter(ImageFilter.GaussianBlur(6))))))
        bob = int(4 * math.sin(2 * math.pi * t))
        fr.alpha_composite(dash, ((S - dash.width) // 2, S - dash.height - 4 + bob))
        d = ImageDraw.Draw(fr)
        # glint sweeping across the sunglasses
        g = (i % 6) / 5
        sparkle(d, 250 + 130 * g, 150 + 10 * g, 26 * math.sin(math.pi * g), 255)
        meme_text(fr, 1.0 + 0.03 * math.sin(4 * math.pi * t))
        frames.append(fr); delays.append(90)
    return frames, delays


# ---------------------------------------------------------------- 3: vuelo con estela
def flyby():
    rnd = random.Random(3)
    dash = pony("MLP_The_Movie_Rainbow_Dash_official_artwork_2", h=250)
    N = 16
    frames, delays = [], []
    # figure-eight path
    P = lambda t: (256 + 175 * math.sin(2 * math.pi * t), 200 + 95 * math.sin(4 * math.pi * t))
    for i in range(N):
        t = i / N
        fr = Image.new("RGBA", (S, S))
        pts = [P(t - s) for s in np.linspace(0.42, 0, 40)]
        trail(fr, pts, width=7)
        x, y = P(t)
        vx = math.cos(2 * math.pi * t)
        im = dash if vx < 0 else dash.transpose(Image.FLIP_LEFT_RIGHT)  # face direction of travel
        tilt = -math.degrees(math.atan2(95 * 4 * math.pi * math.cos(4 * math.pi * t), 175 * 2 * math.pi * abs(vx) + 1e-3)) * 0.35
        im = im.rotate(tilt if vx >= 0 else -tilt, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        d = ImageDraw.Draw(fr)
        for j in range(5):
            sparkle(d, *pts[j * 7], 12 * abs(math.sin(i + j)), 255)
        meme_text(fr, 1.0, dx=rnd.randint(-2, 2), dy=rnd.randint(-2, 2))
        frames.append(fr); delays.append(80)
    return frames, delays


if __name__ == "__main__":
    for name in sys.argv[1:] or ["rainplosion", "chill", "flyby"]:
        frames, delays = globals()[name]()
        d = os.path.join(here, "dframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        with open(os.path.join(d, "delays.txt"), "w") as fh:
            fh.write(" ".join(map(str, delays)))
        print(name, len(frames))
