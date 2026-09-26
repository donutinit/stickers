"""Kratos in the style of the tía 'Chayanne' good-morning images: cat filter, rose, Teletubbies sun, bobblehead in a heart."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6
from kratos import heart_mask

S = 512
N = 10
here = os.path.dirname(os.path.abspath(__file__))
FREDOKA = os.path.join(here, "fonts", "Fredoka.ttf")


def fredoka(size, weight=700):
    f = ImageFont.truetype(FREDOKA, size)
    f.set_variation_by_axes([weight, 100])
    return f


def text(fr, lines, xy, size, fills, anchor="mm", sw=7, stroke=(255, 255, 255), shadow=(90, 20, 60), maxw=480, lh=1.05):
    """chunky rounded tía text: coloured fill, thick white outline, soft drop shadow. `fills` cycles per line."""
    f = fredoka(size)
    while max(f.getlength(l) for l in lines) + 2 * sw > maxw:
        f = fredoka(f.size - 2)
    x, y = xy
    step = f.size * lh
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", (S, S)); ds = ImageDraw.Draw(sh)
    for k, l in enumerate(lines):
        ds.text((x + 3, y + k * step + 4), l, font=f, fill=shadow + (170,), stroke_width=sw, stroke_fill=shadow + (170,), anchor=anchor)
        d.text((x, y + k * step), l, font=f, fill=fills[k % len(fills)], stroke_width=sw, stroke_fill=stroke, anchor=anchor)
    fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    fr.alpha_composite(lay)


def head(name, h):
    im = Image.open(os.path.join(here, "kratos", "cut", name)).convert("RGBA")
    sc = h / im.height
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def sparkles(fr, t, pts, col=(255, 255, 255)):
    d = ImageDraw.Draw(fr)
    for x, y, ph in pts:
        s = max(0, math.sin(2 * math.pi * t * 2 + ph))
        m6.sparkle(d, x, y, 13 * s, int(255 * s), col)


def bokeh_bg(c0, c1, cols, n, seed):
    bg = m6.vgrad(c0, c1)
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y, r = rnd.randint(0, S), rnd.randint(0, S), rnd.randint(10, 42)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice(cols) + (rnd.randint(50, 110),))
    bg.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))
    return bg


def rand_pts(seed, n, avoid):
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rnd.randint(15, 497), rnd.randint(15, 497)
        if not (avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]):
            out.append((x, y, rnd.uniform(0, 6.3)))
    return out


# ------------------------------------------------------------------ 1. cat filter
def gatito():
    bg = bokeh_bg((255, 225, 240), (255, 200, 225), [(255, 255, 255), (255, 170, 210), (200, 230, 255)], 26, 1)
    for code, sz, xy, r in (("1f308", 70, (20, 150), -10), ("1f496", 44, (250, 180), 10), ("1f495", 50, (200, 240), -10)):
        bg.alpha_composite(m6.emoji(code, sz).rotate(r, expand=True), xy)
    hd = head("kratos_serio.png", 330)
    W, H = hd.size
    # cat filter: ears + blush + whisker dots, drawn onto the head layer
    hd2 = Image.new("RGBA", (W + 80, H + 90)); ox, oy = 40, 90
    d = ImageDraw.Draw(hd2)
    for cx, s in ((ox + W * 0.3, -1), (ox + W * 0.7, 1)):  # ears sit on the crown
        d.polygon([(cx - 50, oy + 55), (cx + s * 22, oy - 55), (cx + 50, oy + 45)], fill=(40, 30, 35, 255))
        d.polygon([(cx - 28, oy + 45), (cx + s * 15, oy - 25), (cx + 28, oy + 38)], fill=(255, 150, 190, 255))
    hd2.alpha_composite(hd, (ox, oy))
    bl = Image.new("RGBA", hd2.size); db = ImageDraw.Draw(bl)
    for cx in (ox + W * 0.27, ox + W * 0.73):
        db.ellipse([cx - 30, oy + H * 0.6 - 15, cx + 30, oy + H * 0.6 + 15], fill=(255, 90, 140, 130))
    hd2.alpha_composite(bl.filter(ImageFilter.GaussianBlur(5)))
    d.ellipse([ox + W * 0.5 - 9, oy + H * 0.56 - 6, ox + W * 0.5 + 9, oy + H * 0.56 + 6], fill=(255, 120, 160, 255))  # nose
    pts = rand_pts(1, 14, (0, 190, 300, 512))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        bob = int(5 * math.sin(2 * math.pi * t))
        fr.alpha_composite(hd2, (-30, S - hd2.height + 40 + bob))
        fr.alpha_composite(m6.emoji("1f425", 110).rotate(8 * math.sin(2 * math.pi * t), expand=True), (390, 390))
        text(fr, ["QUE EL CAMINO DE HOY", "NOS CONDUZCA", "HACIA LA FELICIDAD"], (S - 14, 42), 40, [(120, 60, 200, 255), (230, 60, 150, 255), (240, 130, 30, 255)], anchor="rm")
        text(fr, ["¡BONITO DÍA!"], (S - 14, 250), 52, [(80, 170, 70, 255)], anchor="rm", maxw=300)
        sparkles(fr, t, pts)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ 2. face in a rose
def rosa():
    bg = bokeh_bg((60, 90, 40), (140, 150, 70), [(255, 240, 180), (255, 200, 220), (255, 255, 255)], 30, 2)
    rose = m6.emoji("1f339", 470)
    face = head("kratos_serio.png", 250)
    circ = Image.new("L", face.size); ImageDraw.Draw(circ).ellipse([0, 0, face.width, face.height], fill=255)
    face.putalpha(Image.fromarray(np.minimum(np.asarray(face.getchannel("A")), np.asarray(circ))))
    hearts = [(random.Random(k).choice([random.Random(k).randint(10, 90), random.Random(k + 50).randint(400, 470)]), k / 7) for k in range(7)]  # off the face
    pts = rand_pts(2, 16, (140, 60, 380, 330))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        sway = 3 * math.sin(2 * math.pi * t)
        r = rose.rotate(sway, resample=Image.BICUBIC)
        fr.alpha_composite(r, ((S - r.width) // 2, 30))
        # bloom centre of the Twemoji rose sits at ~ (0.40, 0.33) of the glyph
        fr.alpha_composite(face.rotate(sway, expand=True, resample=Image.BICUBIC), (int(S / 2 - 470 * 0.10 - face.width / 2), int(20 + 470 * 0.30 - face.height / 2)))
        for x, ph in hearts:
            p = (ph + t) % 1
            fr.alpha_composite(m6.emoji("1f496", 34), (x, int(470 - 400 * p)))
        fr.alpha_composite(m6.emoji("1f970", 96), (390, 230))
        fr.alpha_composite(m6.emoji("1f425", 100), (6, 400))
        fr.alpha_composite(m6.emoji("1f60a", 96), (408, 404))
        tt = m6.grad_text("Buenos Días!", m6.PACIFICO, 80, [(255, 230, 120), (255, 170, 40), (255, 240, 170), (255, 230, 120)], t,
                          glow=(255, 120, 60), shadow=(90, 40, 0))
        fr.alpha_composite(tt, ((S - tt.width) // 2, -4))
        tb = m6.grad_text("¡Dios te bendiga!", m6.PACIFICO, 58, [(255, 255, 255), (255, 210, 230), (255, 255, 255)], t,
                          stroke=(200, 30, 90), glow=(255, 80, 150), shadow=(90, 0, 40))
        fr.alpha_composite(tb, ((S - tb.width) // 2, 340))
        sparkles(fr, t, pts)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ 3. Teletubbies sun
def sol():
    t_ = np.linspace(0, 1, S)[:, None, None]
    sky = np.array([80, 160, 245.]) * (1 - t_) + np.array([200, 235, 255.]) * t_
    bg = Image.fromarray(np.repeat(sky, S, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(bg)
    d.ellipse([-200, 330, 420, 760], fill=(110, 200, 70, 255))
    d.ellipse([200, 360, 800, 760], fill=(90, 180, 60, 255))
    for x, y in ((40, 380), (110, 420), (300, 440), (420, 400), (470, 450)):
        bg.alpha_composite(m6.emoji(random.Random(x).choice(["1f33c", "1f33b"]), 50), (x - 25, y - 25))
    face = head("kratos_enojado.png", 200)
    a = np.asarray(face).astype(float)
    a[..., :3] = a[..., :3] * np.array([1.0, 0.88, 0.35]) + np.array([60, 50, 0])  # sunny yellow tint
    face = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    cx, cy = 256, 238
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        lay = Image.new("RGBA", (S, S)); dl = ImageDraw.Draw(lay)
        for k in range(16):
            ang = 2 * math.pi * (k / 16 + t / 16)
            L = 150 + (18 if k % 2 else 0)
            p1 = (cx + 90 * math.cos(ang - 0.12), cy + 90 * math.sin(ang - 0.12))
            p2 = (cx + 90 * math.cos(ang + 0.12), cy + 90 * math.sin(ang + 0.12))
            dl.polygon([p1, p2, (cx + (L + 30) * math.cos(ang), cy + (L + 30) * math.sin(ang))], fill=(255, 225, 60, 230))
        dl.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=(255, 230, 90, 255))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.5)))
        fr.alpha_composite(face, (cx - face.width // 2, cy - face.height // 2 + int(3 * math.sin(2 * math.pi * t))))
        text(fr, ["Feliz Lunes"], (S / 2, 46), 74, [(250, 205, 40, 255)], stroke=(40, 40, 60), shadow=(0, 0, 0))
        text(fr, ["Buen día", "gente madrugadora"], (S / 2, 410), 46, [(255, 245, 160, 255)], stroke=(60, 70, 30), shadow=(0, 0, 0))
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ 4. bobblehead in a heart
def domingo():
    bg = bokeh_bg((255, 180, 225), (230, 80, 170), [(255, 255, 255), (255, 200, 240)], 24, 4)
    hm = heart_mask(440)
    heart = Image.new("RGBA", (440, 440), (255, 120, 200, 0))
    heart.putalpha(hm.point(lambda v: v * 200 // 255))
    glow = Image.new("RGBA", (440, 440), (255, 255, 255, 0)); glow.putalpha(hm.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(8)))
    bg.alpha_composite(glow, (36, 40)); bg.alpha_composite(heart, (36, 40))
    body = Image.open(os.path.join(here, "kratos", "kratos_cuerpo.webp")).convert("RGBA")
    body = body.crop(body.getbbox())
    body = body.resize((int(body.width * 250 / body.height), 250), Image.LANCZOS)
    big = head("kratos_serio.png", 185)
    for code, xy, r in (("1f339", (-10, 330), -15), ("1f339", (430, 320), 15), ("1f338", (440, 150), 0), ("1f338", (8, 160), 0)):
        bg.alpha_composite(m6.emoji(code, 76).rotate(r, expand=True), xy)
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        bx, by = (S - body.width) // 2, 135
        fr.alpha_composite(body, (bx, by))
        wob = 10 * math.sin(2 * math.pi * t)  # bobblehead wobble
        h2 = big.rotate(wob, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(h2, (int(S / 2 + 4 - h2.width / 2), int(by + 10 - h2.height * 0.72)))
        text(fr, ["Feliz Domingo Guapa"], (S / 2, 44), 58, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(80, 0, 50))
        text(fr, ["Que te vaya bien hoy y no", "se te olvide tomar agua"], (S / 2, 420), 36, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(80, 0, 50))
        fr.alpha_composite(m6.emoji("1f4a7", 46), (440, 450))
        frames.append(m6.rounded(fr))
    return frames


if __name__ == "__main__":
    for name in sys.argv[1:] or ("gatito", "rosa", "sol", "domingo"):
        frames = globals()[name]()
        d = os.path.join(here, "chayframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(["110"] * len(frames)))
        print(name)
