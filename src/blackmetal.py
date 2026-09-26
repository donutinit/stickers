"""Black metal stickers: grainy B&W flash photo, corpse paint, spiky unreadable logo... and a cute emoji."""
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


def fluttershy():
    fl = Image.open(os.path.join(here, "flutter.png")).convert("RGBA")
    fl = corpse_paint(fl, [(85, 125, 17, 24), (145, 135, 24, 30)], (92, 168, 12), 1)
    fl = fl.resize((440, 440), Image.LANCZOS)
    return flash_photo(fl, (60, 90), 1, "vete alv", [("1f97a", 330, 380, 110)])


def pinkie():
    pk = m6.load("pp/MLP_The_Movie_Pinkie_Pie_official_artwork.t.png", h=500)
    off = (S - pk.width) // 2  # coords were measured with the sprite centred in 512
    pk = corpse_paint(pk, [(112 - off, 140, 12, 22), (168 - off, 170, 26, 32)], (102 - off, 207, 14), 2)
    pk = pk.resize((int(pk.width * 0.92), int(pk.height * 0.92)), Image.LANCZOS)
    return flash_photo(pk, (70, 90), 2, "oki doki", [("1f449", 310, 400, 84), ("1f448", 410, 400, 84)])


def twilight():
    tw = Image.open(os.path.join(here, "m6/FANMADE_Twilight_Sparkle_reading_a_book_vector.png")).convert("RGBA")
    tw = tw.crop(tw.getbbox())
    W, H = tw.size
    head = tw.crop((int(0.30 * W), 0, int(0.95 * W), int(0.85 * H)))
    sc = min(S / head.width, S / head.height)
    head = head.resize((int(head.width * sc), int(head.height * sc)), Image.LANCZOS)
    # eye/mouth coords measured on the NO AUTORIZO frame, where the head sits at y = -40
    head = corpse_paint(head, [(233, 170, 22, 26), (298, 165, 20, 24)], (285, 212, 14), 3)
    return flash_photo(head, ((S - head.width) // 2, 40), 3, "intrínseco", [("1f97a", 30, 390, 100)])


def dash():
    rd = m6.load("rd/FANMADE_Rainbow_Dash_standing_vector.png", h=500)
    off = (S - rd.width) // 2
    rd = corpse_paint(rd, [(198 - off, 132, 22, 30), (258 - off, 122, 26, 34)], (220 - off, 172, 14), 4)
    rd = rd.resize((int(rd.width * 0.9), int(rd.height * 0.9)), Image.LANCZOS)
    return flash_photo(rd, ((S - rd.width) // 2, 70), 4, "me vale verga", [("1f495", 380, 390, 96)])


def moai():
    import moai_common as mc
    card = mc.shot(1.15, 0.5, 0.45)
    im = card.convert("RGBA")
    im.putalpha(255)
    g = np.asarray(im.convert("L")).astype(float) / 255
    g = np.clip(g * 1.1 + np.random.default_rng(5).normal(0, 0.07, g.shape), 0, 1)
    img = Image.fromarray((g * 255).astype(np.uint8))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=30); buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    logo = spiky_logo("nel", width=330, seed=5)
    img.alpha_composite(logo, ((S - logo.width) // 2 - 40, 6))
    img.alpha_composite(m6.emoji("1f97a", 110), (330, 380))
    return m6.rounded(img, 26)


if __name__ == "__main__":
    out = os.path.join(here, "bmframes"); os.makedirs(out, exist_ok=True)
    for name in sys.argv[1:] or ("fluttershy", "pinkie", "twilight", "dash", "moai"):
        globals()[name]().save(os.path.join(out, name + ".png"))
        print(name)
