"""Kratos, but cute: huge background-removed Kratos head with bows, hearts and cursive text (plus one pastel card)."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import m6

S = 512
N = 12
here = os.path.dirname(os.path.abspath(__file__))
PINK = [(255, 90, 170), (255, 150, 200), (255, 200, 120), (255, 90, 170)]
LILAC = [(190, 110, 255), (255, 140, 210), (140, 170, 255), (190, 110, 255)]
GOLD = [(255, 170, 30), (255, 230, 120), (255, 140, 60), (255, 170, 30)]
NIGHT = [(200, 190, 255), (255, 255, 255), (180, 210, 255), (200, 190, 255)]


def heart_mask(size):
    """classic heart curve, filled."""
    m = Image.new("L", (size * 2, size * 2))
    pts = []
    for k in range(400):
        t = 2 * math.pi * k / 400
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((size + x * size / 17.5, size * 0.92 - y * size / 17.5))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.resize((size, size), Image.LANCZOS)


def circle_mask(size):
    m = Image.new("L", (size * 2, size * 2)); ImageDraw.Draw(m).ellipse([0, 0, size * 2 - 1, size * 2 - 1], fill=255)
    return m.resize((size, size), Image.LANCZOS)


def framed_photo(path, center, side, size, shape="heart"):
    """square crop around the face -> heart/circle with white border and pink glow."""
    im = Image.open(os.path.join(here, "kratos", path)).convert("RGB")
    W, H = im.size
    s = side * W
    cx, cy = center[0] * W, center[1] * H
    x0 = min(max(0, cx - s / 2), W - s); y0 = min(max(0, cy - s / 2), H - s)
    im = im.crop((int(x0), int(y0), int(x0 + s), int(y0 + s))).resize((size, size), Image.LANCZOS)
    mask = (heart_mask if shape == "heart" else circle_mask)(size)
    pad = 26
    out = Image.new("RGBA", (size + 2 * pad, size + 2 * pad))
    big = Image.new("L", out.size); big.paste(mask, (pad, pad))
    glow = Image.new("RGBA", out.size, (255, 110, 190, 0)); glow.putalpha(big.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(10)))
    border = Image.new("RGBA", out.size, (255, 255, 255, 0)); border.putalpha(big.filter(ImageFilter.MaxFilter(15)))
    photo = Image.new("RGBA", out.size); photo.paste(im, (pad, pad)); photo.putalpha(big)
    for lay in (glow, border, photo):
        out.alpha_composite(lay)
    return out


def cutout(path, h):
    im = Image.open(os.path.join(here, "kratos", path)).convert("RGBA")
    im = im.crop(im.getbbox())
    sc = h / im.height
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def card(subject, subject_xy, texts, bg, deco, seed, night=False):
    rnd = random.Random(seed)
    base = m6.vgrad(*bg)
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for _ in range(22):  # bokeh
        x, y, r = rnd.randint(0, S), rnd.randint(0, S), rnd.randint(10, 40)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(40, 90)))
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
    hearts = [(rnd.choice([rnd.randint(5, 70), rnd.randint(430, 475)]), rnd.random(), rnd.choice(["1f496", "1f495"] if not night else ["2b50", "1f31f"]), rnd.randint(30, 46)) for _ in range(6)]
    sparks = [(x, y, rnd.uniform(0, 6.3)) for x, y in ((rnd.randint(15, 497), rnd.randint(15, 497)) for _ in range(40))
              if not (120 < x < 390 and 50 < y < 340)][:18]  # keep sparkles off the face
    frames = []
    for i in range(N):
        t = i / N
        fr = base.copy()
        beat = 1 + 0.035 * max(0, math.sin(2 * math.pi * t * 2)) ** 2  # the frame "beats"
        sub = subject.resize((int(subject.width * beat), int(subject.height * beat)), Image.LANCZOS)
        fr.alpha_composite(sub, (int(subject_xy[0] - (sub.width - subject.width) / 2), int(subject_xy[1] - (sub.height - subject.height) / 2)))
        for code, sz, (x, y), rot in deco:
            fr.alpha_composite(m6.emoji(code, sz).rotate(rot, expand=True, resample=Image.BICUBIC), (x, y))
        for x, ph, code, sz in hearts:
            p = (ph + t) % 1
            e = m6.emoji(code, sz).copy()
            e.putalpha(e.getchannel("A").point(lambda a: int(a * min(1, (1 - p) * 2.5))))
            fr.alpha_composite(e, (int(x + 10 * math.sin(p * 6)), int(470 - 360 * p)))
        dd = ImageDraw.Draw(fr)
        for x, y, ph in sparks:
            s = max(0, math.sin(2 * math.pi * t * 2 + ph))
            m6.sparkle(dd, x, y, 12 * s, int(255 * s))
        for txt, size, stops, y in texts:
            im = m6.grad_text(txt, m6.PACIFICO, size, stops, t)
            fr.alpha_composite(im, ((S - im.width) // 2, y if y >= 0 else S - im.height + y))
        frames.append(m6.rounded(fr))
    return frames, [100] * N


PIECES = {
    "te_amo": dict(photo=("kratos_enojado.jpg", (0.5, 0.42), 0.9, 330, "heart"), xy=(65, 30),
                   texts=[("Te Amo", 110, PINK, -10)], bg=((255, 225, 240), (255, 180, 215)),
                   deco=[("1f380", 110, (190, -8), 0), ("1f339", 90, (-6, 330), -15), ("1f490", 96, (420, 320), 12)]),
    "estas_linda": dict(photo=("kratos_serio.jpg", (0.45, 0.33), 0.75, 320, "heart"), xy=(70, 30),
                        texts=[("Estás Linda", 94, LILAC, -12)], bg=((245, 230, 255), (215, 190, 255)),
                        deco=[("1f380", 100, (200, -6), 0), ("1f337", 84, (0, 320), -10), ("1f338", 80, (430, 330), 12)]),
    "muchas_gracias": dict(photo=("kratos_grito.jpg", (0.56, 0.22), 0.36, 300, "circle"), xy=(80, 70),
                           texts=[("¡Muchas", 84, GOLD, 0), ("Gracias!", 94, PINK, -10)], bg=((255, 245, 215), (255, 205, 180)),
                           deco=[("1f64f", 84, (22, 190), 0), ("1f490", 96, (410, 200), 10)]),
    "buenos_dias": dict(cut=("kratos_cuerpo.webp", 540), xy=(112, -6),  # full-height Kratos, text in front
                        texts=[("Buenos Días", 112, GOLD, -14)], bg=((255, 245, 210), (255, 200, 220)),
                        deco=[("2600", 110, (8, 12), 0), ("2615", 96, (408, 250), 0), ("1f33c", 74, (20, 240), 0)]),
    "cuidate": dict(photo=("kratos_parado.jpg", (0.5, 0.12), 0.34, 320, "heart"), xy=(70, 30),
                    texts=[("Cuídate Mucho", 86, PINK, -12)], bg=((225, 245, 255), (200, 225, 255)),
                    deco=[("1f98b", 80, (20, 30), -10), ("1f337", 84, (420, 300), 10), ("1f33a", 76, (0, 330), -10)]),
    "descansa": dict(photo=("kratos_barba.jpg", (0.47, 0.18), 0.5, 320, "circle"), xy=(70, 30),
                     texts=[("Descansa", 100, NIGHT, -12)], bg=((40, 30, 90), (110, 60, 150)), night=True,
                     deco=[("1f319", 100, (400, 10), 0), ("2b50", 50, (20, 40), 15), ("2b50", 40, (440, 300), -10)]),
    "lo_se": dict(photo=("kratos_serio.jpg", (0.45, 0.33), 0.75, 330, "circle"), xy=(65, 20),
                  texts=[("Lo sé.", 120, LILAC, -12)], bg=((245, 230, 255), (255, 200, 230)),
                  deco=[("1f485", 96, (410, 300), 0), ("2728", 70, (20, 40), 0)]),
    "lo_se_enojado": dict(photo=("kratos_enojado.jpg", (0.5, 0.42), 0.9, 330, "heart"), xy=(65, 26),
                          texts=[("Lo sé.", 120, PINK, -12)], bg=((255, 225, 240), (255, 190, 220)),
                          deco=[("1f380", 110, (190, -8), 0), ("1f485", 90, (410, 310), 0)]),
    "yo_tambien": dict(photo=("kratos_barba.jpg", (0.47, 0.15), 0.4, 320, "heart"), xy=(70, 24),
                       texts=[("Yo También", 100, PINK, -12)], bg=((255, 225, 240), (255, 185, 215)),
                       deco=[("1f380", 110, (190, -8), 0), ("1f495", 80, (420, 320), 10), ("1f339", 84, (0, 330), -15)]),
    "yo_tambien_grito": dict(photo=("kratos_grito.jpg", (0.56, 0.22), 0.36, 320, "heart"), xy=(70, 24),
                             texts=[("¡Yo También!", 96, LILAC, -12)], bg=((245, 230, 255), (215, 195, 255)),
                             deco=[("1f380", 110, (190, -8), 0), ("1f496", 80, (420, 320), 10), ("1f338", 84, (0, 330), -10)]),
}

def head(path, box, h):
    """background-removed Kratos, cropped to head (+shoulders) and scaled to height h."""
    im = Image.open(os.path.join(here, "kratos", "cut", path)).convert("RGBA")
    W, H = im.size
    im = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
    im = im.crop(im.getbbox())
    sc = h / im.height
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def cute(subject, texts, bow, deco, seed, night=False):
    """transparent sticker: huge Kratos head, bow on top, hearts/sparkles at the sides, cursive text under the chin."""
    rnd = random.Random(seed)
    hx = (S - subject.width) // 2
    floaters = [(rnd.choice([rnd.randint(0, 60), rnd.randint(440, 470)]), rnd.random(),
                 rnd.choice(["2b50", "1f31f"] if night else ["1f496", "1f495"]), rnd.randint(34, 48)) for _ in range(6)]
    sparks = [(rnd.choice([rnd.randint(15, 80), rnd.randint(432, 497)]), rnd.randint(20, 380), rnd.uniform(0, 6.3)) for _ in range(10)]
    frames = []
    n = 10
    for i in range(n):
        t = i / n
        fr = Image.new("RGBA", (S, S))
        bob = int(4 * math.sin(2 * math.pi * t))
        fr.alpha_composite(subject, (hx, 22 + bob))  # margin so the crown never touches the edge
        if bow:
            b = m6.emoji("1f380", bow[1]).rotate(bow[2] + 6 * math.sin(2 * math.pi * t), expand=True, resample=Image.BICUBIC)
            fr.alpha_composite(b, (hx + int(bow[0] * subject.width) - b.width // 2, max(0, 22 + bob - b.height // 3)))
        for code, sz, (x, y), rot in deco:
            fr.alpha_composite(m6.emoji(code, sz).rotate(rot, expand=True, resample=Image.BICUBIC), (x, y))
        for x, ph, code, sz in floaters:
            p = (ph + t) % 1
            e = m6.emoji(code, sz).copy()
            e.putalpha(e.getchannel("A").point(lambda a: int(a * min(1, (1 - p) * 2.5))))
            fr.alpha_composite(e, (int(x + 8 * math.sin(p * 6)), int(420 - 380 * p)))
        d = ImageDraw.Draw(fr)
        for x, y, ph in sparks:
            s_ = max(0, math.sin(2 * math.pi * t * 2 + ph))
            m6.sparkle(d, x, y, 13 * s_, int(255 * s_), (255, 215, 90))
        for txt, size, stops, y in texts:
            im = m6.grad_text(txt, m6.PACIFICO, size, stops, t)
            fr.alpha_composite(im, ((S - im.width) // 2, y if y >= 0 else S - im.height + y))
        frames.append(fr)
    return frames, [110] * n


HEADS = {
    # name: (cut file, crop box, head height, texts, bow (x frac, size, rot) or None, deco, night)
    "te_amo":          ("kratos_enojado.png", (0, 0, 1, 1), 360, [("Te Amo", 112, PINK, -4)], (0.62, 120, 12), [], False),
    "estas_linda":     ("kratos_serio.png", (0, 0, 1, 1), 360, [("Estás Linda", 100, LILAC, -4)], (0.35, 120, -12), [], False),
    "muchas_gracias":  ("kratos_grito.png", (0.28, 0, 0.78, 0.62), 380, [("¡Muchas Gracias!", 84, GOLD, -4)], None, [("1f64f", 90, (400, 250), 0)], False),
    "cuidate":         ("kratos_parado.png", (0.22, 0, 0.78, 0.36), 390, [("Cuídate Mucho", 92, PINK, -4)], (0.52, 110, 10), [], False),
    "descansa":        ("kratos_barba.png", (0.18, 0, 0.78, 0.42), 390, [("Descansa", 110, NIGHT, -4)], None, [("1f319", 100, (410, 10), 0)], True),
    "lo_se":           ("kratos_serio.png", (0, 0, 1, 1), 360, [("Lo sé.", 124, LILAC, -4)], None, [("1f485", 96, (410, 250), 0)], False),
    "lo_se_enojado":   ("kratos_enojado.png", (0, 0, 1, 1), 360, [("Lo sé.", 124, PINK, -4)], (0.62, 120, 12), [("1f485", 90, (410, 260), 0)], False),
    "yo_tambien":      ("kratos_barba.png", (0.18, 0, 0.78, 0.42), 390, [("Yo También", 104, PINK, -4)], (0.5, 110, 8), [], False),
    "tus_tetas":       ("kratos_serio.png", (0, 0, 1, 1), 300, [("Me gustan mucho", 84, LILAC, -96), ("tus tetas", 100, PINK, -4)],
                        (0.35, 104, -12), [("1f495", 80, (410, 150), 10)], False),
    "gracias_dios":    ("kratos_grito.png", (0.28, 0, 0.78, 0.62), 360, [("¡Gracias a Dios!", 88, GOLD, -4)], None,
                        [("1f64f", 96, (400, 230), 0), ("2728", 70, (30, 40), 0)], False),
    "yo_tambien_grito": ("kratos_grito.png", (0.28, 0, 0.78, 0.62), 380, [("¡Yo También!", 100, LILAC, -4)], None, [("1f496", 80, (410, 230), 10)], False),
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(HEADS) + ["buenos_dias"]
    for name in names:
        if name in HEADS:
            f, box, h, texts, bow, deco, night = HEADS[name]
            frames, delays = cute(head(f, box, h), texts, bow, deco, seed=len(name), night=night)
        else:  # card version (kept for buenos_dias)
            p = PIECES[name]
            subj = framed_photo(*p["photo"]) if "photo" in p else cutout(*p["cut"])
            frames, delays = card(subj, p["xy"], p["texts"], p["bg"], p["deco"], seed=len(name), night=p.get("night", False))
        d = os.path.join(here, "kratosframes", name); os.makedirs(d, exist_ok=True)
        for x in os.listdir(d):
            os.remove(os.path.join(d, x))
        for i, fr in enumerate(frames):
            fr.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
        print(name)
