"""Black metal stickers: dark real imagery (Kittelsen, Holbein, winter forest), spiky logo... and a cute emoji."""
import io, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6

S = 512
here = os.path.dirname(os.path.abspath(__file__))
GOTHIC = os.path.join(here, "fonts", "NewRocker.ttf")  # readable blackletter; Fraktur k/d were illegible


def forest(seed):
    """night forest: fog + a few pale trunks, all very dark."""
    rnd = np.random.default_rng(seed)
    fog = np.zeros((S, S))
    for o, w in ((4, 1), (8, .5), (16, .25)):
        fog += w * np.asarray(Image.fromarray((rnd.random((o, o)) * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)) / 255
    img = Image.fromarray((np.clip(fog / 1.75 * 60, 0, 255)).astype(np.uint8))
    d = ImageDraw.Draw(img)
    r = random.Random(seed)
    for _ in range(9):
        x = r.randint(-20, S + 20); w = r.randint(6, 26); c = r.randint(30, 75)
        d.polygon([(x, -10), (x + w, -10), (x + w * 1.3 + r.randint(-10, 10), S + 10), (x - w * 0.3, S + 10)], fill=c)
        for _ in range(3):  # bare branches
            y = r.randint(20, 300); L = r.randint(30, 90); s = r.choice([-1, 1])
            d.line([(x + w / 2, y), (x + w / 2 + s * L, y - L * 0.6)], fill=c, width=r.randint(2, 4))
    return img.filter(ImageFilter.GaussianBlur(1.2))


def corpse_paint(im, eyes, mouth, seed):
    """black spiky patches around the eyes (eyes themselves kept) + a black grimace."""
    rnd = random.Random(seed)
    orig = im.copy()
    d = ImageDraw.Draw(im)
    for x, y, rx, ry in eyes:
        pts = []
        n = 18
        for k in range(n):
            a = 2 * math.pi * k / n
            rr = 1.18
            if math.sin(a) > 0.35 and k % 2 == 0:  # long drips down the cheek
                rr += 0.7 + rnd.random() * 0.7
            elif math.sin(a) < -0.5 and k % 3 == 0:  # a few short horns up the brow
                rr += 0.25 + rnd.random() * 0.2
            pts.append((x + rx * rr * math.cos(a), y + ry * rr * math.sin(a)))
        d.polygon(pts, fill=(0, 0, 0, 255))
    # put the eyes back so the pony still looks at you through the paint
    m = Image.new("L", im.size)
    md = ImageDraw.Draw(m)
    for x, y, rx, ry in eyes:
        md.ellipse([x - rx, y - ry, x + rx, y + ry], fill=255)
    im.paste(orig, (0, 0), m.filter(ImageFilter.GaussianBlur(1.5)))
    d = ImageDraw.Draw(im)
    if mouth:
        x, y, w = mouth
        d.polygon([(x - w, y), (x - w * 0.6, y - 5), (x, y - 3), (x + w * 0.6, y - 5), (x + w, y),
                   (x + w * 0.7, y + 9), (x + w * 0.35, y + 26), (x, y + 10), (x - w * 0.35, y + 28), (x - w * 0.7, y + 9)],
                  fill=(0, 0, 0, 255))
    return im


def spiky_logo(txt, width=490, seed=0):
    """white gothic phrase with a few short thorns and a dark halo so it stays readable; long phrases go on two lines."""
    rnd = random.Random(seed)
    words = txt.split()
    lines = [txt]
    if len(txt) > 11 and len(words) > 1:  # split into two balanced lines
        k = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
        lines = [" ".join(words[:k]), " ".join(words[k:])]
    f = ImageFont.truetype(GOTHIC, 150)
    while max(f.getlength(l) for l in lines) > width - 90 and f.size > 30:
        f = f.font_variant(size=f.size - 3)
    lh = int(f.size * 0.95)
    pad = 60
    W = int(max(f.getlength(l) for l in lines)) + 2 * pad
    H = lh * len(lines) + 2 * pad
    mask = Image.new("L", (W, H))
    md = ImageDraw.Draw(mask)
    for k, l in enumerate(lines):
        md.text((W / 2, pad + lh * k + lh / 2), l, font=f, fill=255, anchor="mm")
    letters = mask.copy()
    a = np.asarray(mask) > 128
    edge = a & ~np.asarray(mask.filter(ImageFilter.MinFilter(3))).astype(bool)
    ys, xs = np.nonzero(edge)
    blur = np.asarray(mask.filter(ImageFilter.GaussianBlur(4))).astype(float)
    gy, gx = np.gradient(blur)
    idx = list(range(len(xs))); rnd.shuffle(idx)
    placed = 0
    for i in idx:
        if placed >= 28:
            break
        x, y = xs[i], ys[i]
        nx, ny = -gx[y, x], -gy[y, x]
        n = math.hypot(nx, ny)
        line_top = pad + lh * ((y - pad) // lh) if y >= pad else pad
        if n < 1e-3 or ny / n > -0.8 or (y - line_top) > lh * 0.42:
            continue  # only upward thorns off the tops of letters: bowls and counters stay clean
        nx, ny = nx / n, ny / n
        L = rnd.uniform(8, 20)
        md.polygon([(x - 2.2, y), (x + 2.2, y), (x + nx * L, y + ny * L)], fill=255)
        placed += 1
    cy = H / 2
    for s_, x0 in ((-1, pad - 8), (1, W - pad + 8)):  # side thorns
        for dy, L in ((-10, 42), (8, 30)):
            md.polygon([(x0, cy + dy - 3), (x0, cy + dy + 3), (x0 + s_ * L, cy + dy)], fill=255)
    halo = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))
    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo.putalpha(halo.point(lambda v: min(255, v * 2)))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 0)); white.putalpha(mask)
    logo.alpha_composite(white)
    sc = min(1.0, width / W)
    return logo.resize((int(W * sc), int(H * sc)), Image.LANCZOS)


def flash_photo(subject, xy, seed, logo_txt, emojis, logo_y=6):
    bg = forest(seed).convert("RGBA")
    bg.alpha_composite(subject, xy)
    g = np.asarray(bg.convert("L")).astype(float) / 255
    g = np.clip((g - 0.06) / 0.8, 0, 1) ** 0.9  # hard on-camera flash
    yy, xx = np.mgrid[0:S, 0:S] / S
    flash = np.clip(1.35 - 1.5 * np.hypot(xx - 0.5, yy - 0.5), 0.15, 1)
    g = g * flash
    g = g + np.random.default_rng(seed).normal(0, 0.07, g.shape)  # heavy grain
    img = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=30); buf.seek(0)  # cheap-camera crunch
    img = Image.open(buf).convert("RGBA")
    logo = spiky_logo(logo_txt, seed=seed)
    img.alpha_composite(logo, ((S - logo.width) // 2, logo_y))
    for code, x, y, sz in emojis:
        img.alpha_composite(m6.emoji(code, sz), (x, y))
    return m6.rounded(img, 26)


def grim(img, crop, invert=False, gamma=1.0, gain=1.0, emojis=(), logo_txt="", seed=0, logo_y=6):
    """dark B&W treatment of a real image: square crop, crushed tones, flash falloff, grain, cheap JPEG, spiky logo."""
    im = Image.open(os.path.join(here, "bm", img)).convert("L")
    W, H = im.size
    im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H))).resize((S, S), Image.LANCZOS)
    g = np.asarray(im).astype(float) / 255
    if invert:
        g = 1 - g
    g = np.clip(g * gain, 0, 1) ** gamma
    yy, xx = np.mgrid[0:S, 0:S] / S
    g = g * np.clip(1.3 - 1.3 * np.hypot(xx - 0.5, yy - 0.5), 0.1, 1)
    g = g + np.random.default_rng(seed).normal(0, 0.06, g.shape)
    out = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
    buf = io.BytesIO(); out.save(buf, "JPEG", quality=30); buf.seek(0)
    out = Image.open(buf).convert("RGBA")
    logo = spiky_logo(logo_txt, seed=seed)
    y = logo_y if logo_y >= 0 else S - logo.height + logo_y  # negative = anchored to the bottom
    out.alpha_composite(logo, ((S - logo.width) // 2, y))
    for code, x, y, sz in emojis:
        out.alpha_composite(m6.emoji(code, sz), (x, y))
    return m6.rounded(out, 26)


PIECES = {
    # name: (image, crop, invert, gamma, gain, logo, emojis, logo_y)
    "pesta":     ("pesta.jpg", (0, 0.25, 1, 0.99), False, 1.6, 1.1, "ya voy", [("1f97a", 380, 380, 100)], 6),
    "nokken":    ("nokken.jpg", (0.22, 0, 0.88, 1), False, 2.2, 1.0, "nel", [("1f449", 330, 405, 80), ("1f448", 420, 405, 80)], 250),
    "abad":      ("holbein_abad.jpg", (0.05, 0.1, 0.95, 0.95), True, 1.4, 1.1, "me vale verga", [("1f495", 395, 395, 96)], 6),
    "dama":      ("holbein_dama.jpg", (0.04, 0.1, 0.96, 0.95), True, 1.4, 1.1, "te amo", [("1f97a", 380, 385, 100)], 6),
    "bosque":    ("bosque.jpg", (0.2, 0, 0.87, 1), True, 1.2, 1.0, "vete alv", [("1f97a", 30, 390, 100)], 6),
    "iglesia":   ("iglesia.jpg", (0, 0.1, 1, 0.85), False, 1.8, 1.0, "intrínseco", [("1f97a", 380, 390, 100)], 6),
    "sopa":      ("goya_sopa.jpg", (0.05, 0, 0.72, 1), False, 1.3, 1.25, "oki doki", [("1f97a", 390, 395, 100)], 6),
    "parcas":    ("goya_parcas.jpg", (0.28, 0, 0.78, 1), False, 1.3, 1.3, "no autorizo", [("1f449", 330, 410, 80), ("1f448", 420, 410, 80)], 6),
    "duelo":     ("goya_duelo.jpg", (0.02, 0, 0.52, 1), False, 1.2, 1.2, "es broma", [("1f97a", 390, 395, 100)], 6),
    "capricho":  ("goya_capricho43.jpg", (0.04, 0.05, 0.96, 0.66), True, 1.3, 1.1, "maravilloso", [("1f495", 30, 400, 90)], 6),
    "draugen":   ("kittelsen_draugen.jpg", (0.2, 0, 0.9, 1), True, 1.4, 1.1, "ni en su casa lo conocen", [("1f97a", 390, 400, 100)], 6),
    "grito":     ("munch_grito.jpg", (0.2, 0.32, 0.76, 0.754), False, 1.5, 0.85, "aterrado absoluto", [("1f97a", 400, 14, 96)], -2),
}


if __name__ == "__main__":
    out = os.path.join(here, "bmframes"); os.makedirs(out, exist_ok=True)
    for name in sys.argv[1:] or PIECES:
        img, crop, inv, gam, gain, logo, emo, ly = PIECES[name]
        grim(img, crop, inv, gam, gain, emo, logo, seed=len(name), logo_y=ly).save(os.path.join(out, "img_" + name + ".png"))
        print(name)
