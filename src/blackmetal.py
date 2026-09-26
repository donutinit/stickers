"""Black metal stickers: dark real imagery (Kittelsen, Holbein, winter forest), spiky logo... and a cute emoji."""
import io, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6

S = 512
here = os.path.dirname(os.path.abspath(__file__))
GOTHIC = os.path.join(here, "fonts", "UnifrakturMaguntia.ttf")


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
    """white gothic word grown into a thorny, barely readable black-metal logo."""
    rnd = random.Random(seed)
    f = m6.fit_font(GOTHIC, txt, 150, width - 60, 0)
    l, t, r, b = f.getbbox(txt)
    pad = 70
    W, H = r - l + 2 * pad, b - t + 2 * pad
    mask = Image.new("L", (W, H))
    ImageDraw.Draw(mask).text((pad - l, pad - t), txt, font=f, fill=255)
    a = np.asarray(mask) > 128
    edge = a & ~np.asarray(mask.filter(ImageFilter.MinFilter(3))).astype(bool)
    ys, xs = np.nonzero(edge)
    blur = np.asarray(mask.filter(ImageFilter.GaussianBlur(4))).astype(float)
    gy, gx = np.gradient(blur)
    d = ImageDraw.Draw(mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    for i in idx[:90]:
        x, y = xs[i], ys[i]
        nx, ny = -gx[y, x], -gy[y, x]
        n = math.hypot(nx, ny)
        if n < 1e-3:
            continue
        nx, ny = nx / n, ny / n
        vertical = abs(ny) > 0.6
        if not vertical and rnd.random() < 0.7:
            continue  # thorns mostly grow up and down
        L = rnd.uniform(6, 14) + (rnd.uniform(8, 30) if vertical else 0)
        ex, ey = x + nx * L, y + ny * L
        px, py = -ny * 2.6, nx * 2.6  # base half-width
        d.polygon([(x + px, y + py), (x - px, y - py), (ex, ey)], fill=255)
    # long symmetric thorns off both ends of the word
    cy = H / 2
    for s_, x0 in ((-1, pad - 6), (1, W - pad + 6)):
        for k, (dy, L) in enumerate(((-18, 60), (0, 70), (16, 50))):
            d.polygon([(x0, cy + dy - 3), (x0, cy + dy + 3), (x0 + s_ * L, cy + dy + s_ * rnd.uniform(-8, 8))], fill=255)
    logo = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    logo.putalpha(mask)
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
    out.alpha_composite(logo, ((S - logo.width) // 2, logo_y))
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
}


if __name__ == "__main__":
    out = os.path.join(here, "bmframes"); os.makedirs(out, exist_ok=True)
    for name in sys.argv[1:] or PIECES:
        img, crop, inv, gam, gain, logo, emo, ly = PIECES[name]
        grim(img, crop, inv, gam, gain, emo, logo, seed=len(name), logo_y=ly).save(os.path.join(out, "img_" + name + ".png"))
        print(name)
