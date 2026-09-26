"""Mane six stickers: 6 'reply' statics (meme style) + 6 creative animations."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 512
here = os.path.dirname(os.path.abspath(__file__))
IMPACT = os.path.expanduser("~/.local/share/fonts/Impact.TTF")
PACIFICO = os.path.join(here, "Pacifico.ttf")
RYE = os.path.join(here, "Rye.ttf")
RAINBOW = [(238, 64, 53), (243, 146, 55), (253, 246, 99), (103, 190, 90), (50, 150, 220), (110, 80, 180)]


def load(path, h=None, w=None, box=None):
    im = Image.open(os.path.join(here, path)).convert("RGBA")
    im = im.crop(im.getbbox())
    if box:  # fit inside box
        sc = min(box[0] / im.width, box[1] / im.height)
    else:
        sc = h / im.height if h else w / im.width
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


_em = {}


def emoji(code, sz):
    k = (code, sz)
    if k not in _em:
        _em[k] = Image.open(os.path.join(here, "emoji", code + ".png")).convert("RGBA").resize((sz, sz), Image.LANCZOS)
    return _em[k]


def fit_font(path, txt, size, maxw, sw):
    while True:
        f = ImageFont.truetype(path, size)
        l, t, r, b = f.getbbox(txt, stroke_width=sw)
        if r - l <= maxw or size < 10:
            return f
        size -= 2


def meme_text(fr, txt, y=445, scale=1.0, dx=0, dy=0, size=100):
    f = fit_font(IMPACT, txt, int(size * scale), int(484 * scale), 8)
    ImageDraw.Draw(fr).text((S / 2 + dx, y + dy), txt, font=f, fill="white", stroke_width=max(4, int(8 * scale)),
                            stroke_fill="black", anchor="mm")


def grad_text(txt, font, size, stops, shift=0.0, stroke=(255, 255, 255), sw=8, glow=(255, 80, 200), shadow=(120, 0, 80), maxw=490):
    f = fit_font(font, txt, size, maxw, sw)
    pad = 30
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    org = (pad - l, pad - t)
    mask = Image.new("L", (w, h)); ImageDraw.Draw(mask).text(org, txt, font=f, fill=255)
    st = Image.new("L", (w, h)); ImageDraw.Draw(st).text(org, txt, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    x = np.linspace(0, 1, w)[None, :] + np.linspace(0, 0.4, h)[:, None] + shift
    x = (x % 1.0) * (len(stops) - 1)
    lo = np.floor(x).astype(int); fr_ = (x - lo)[..., None]
    cols = np.array(stops, float)
    grad = Image.fromarray((cols[lo] * (1 - fr_) + cols[np.minimum(lo + 1, len(stops) - 1)] * fr_).astype(np.uint8), "RGB")
    out = Image.new("RGBA", (w, h))
    layers = []
    if glow:
        g = Image.new("RGBA", (w, h), glow + (0,)); g.putalpha(st.filter(ImageFilter.GaussianBlur(9))); layers.append((g, (0, 0)))
    if shadow:
        s_ = Image.new("RGBA", (w, h), shadow + (0,)); s_.putalpha(st); layers.append((s_, (4, 5)))
    s2 = Image.new("RGBA", (w, h), stroke + (0,)); s2.putalpha(st); layers.append((s2, (0, 0)))
    fill = grad.convert("RGBA"); fill.putalpha(mask); layers.append((fill, (0, 0)))
    for lay, off in layers:
        out.alpha_composite(lay, off)
    bb = out.getbbox()
    return out.crop(bb)


def put_center(fr, im, cy, dx=0, scale=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    fr.alpha_composite(im, (int((S - im.width) / 2 + dx), int(cy - im.height / 2)))


def sparkle(d, x, y, r, a=255, col=(255, 255, 255)):
    if r < 2:
        return
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22),
               (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=col + (a,))


def vgrad(c0, c1):
    t = np.linspace(0, 1, S)[:, None, None]
    a, b = np.array(c0, float), np.array(c1, float)
    return Image.fromarray(np.repeat(a * (1 - t) + b * t, S, axis=1).astype(np.uint8), "RGB").convert("RGBA")


def rays(fr, angle, cols, alpha=90, n=16, c=(256, 256)):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for k in range(n):
        a0 = math.radians(angle + k * 360 / n); a1 = a0 + math.radians(360 / n / 2)
        d.polygon([c, (c[0] + 800 * math.cos(a0), c[1] + 800 * math.sin(a0)), (c[0] + 800 * math.cos(a1), c[1] + 800 * math.sin(a1))],
                  fill=cols[k % len(cols)] + (alpha,))
    fr.alpha_composite(lay)


def rounded(img, r=44):
    m = Image.new("L", (S, S)); ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], r, fill=255)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(m))))
    return img


# ======================================================================= replies (static)
REPLIES = [
    ("r_twilight", "m6/MLP_The_Movie_Twilight_Sparkle_official_artwork_3.png", "DE ACUERDO"),
    ("r_rarity", "m6/FANMADE_Rarity_vector_by_almostfictional.png", "ESTÁ BIEN"),
    ("r_applejack", "m6/MLP_The_Movie_Applejack_official_artwork.png", "SALE"),
    ("r_fluttershy", "m6/FANMADE_Excited_Fluttershy_vector_by_Myardius.png", "OKIS"),
    ("r_dash", "rd/FANMADE_proud_Rainbow_Dash_vector.png", "VA"),
    ("r_pinkie", "pp/MLP_The_Movie_Pinkie_Pie_official_artwork.png", "SIP"),
]


def reply(path, txt):
    p = load(path, box=(S, S))
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(p, ((S - p.width) // 2, S - p.height))
    meme_text(fr, txt, size=110)
    return [fr], [0]


# ======================================================================= creative (animated)
def twilight():
    tw = load("m6/FANMADE_Twilight_Sparkle_reading_a_book_vector.png", w=490)
    ox, oy = (S - tw.width) // 2, 150
    horn = (ox + 0.69 * tw.width, oy + 0.04 * tw.height)
    bg = vgrad((35, 15, 70), (95, 45, 140))
    rnd = random.Random(1)
    d0 = ImageDraw.Draw(bg)
    for _ in range(60):
        x, y, r = rnd.randint(0, S), rnd.randint(0, S), rnd.choice([1, 1, 2])
        d0.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 200))
    books = [("1f4da", 70, 0.0), ("1f4d6", 60, 0.33), ("1f4da", 56, 0.66)]
    stars = [(rnd.randint(20, 492), rnd.randint(20, 492), rnd.uniform(0, 6.28)) for _ in range(16)]
    N = 12
    frames = []
    top = [grad_text("Estoy en mi", PACIFICO, 64, [(255, 255, 255), (230, 190, 255), (255, 150, 230), (255, 255, 255)], i / N,
                     glow=(190, 90, 255), shadow=(60, 0, 110)) for i in range(N)]
    bot = [grad_text("Era Lectora", PACIFICO, 76, [(255, 110, 200), (190, 90, 255), (120, 150, 255), (255, 110, 200)], i / N,
                     glow=(190, 90, 255), shadow=(60, 0, 110)) for i in range(N)]
    for i in range(N):
        t = i / N
        fr = bg.copy()
        # magic aura around the horn
        pulse = 0.75 + 0.25 * math.sin(2 * math.pi * t * 2)
        glow = Image.new("RGBA", (S, S)); gd = ImageDraw.Draw(glow)
        r = 34 * pulse
        gd.ellipse([horn[0] - r, horn[1] - r, horn[0] + r, horn[1] + r], fill=(255, 120, 230, 200))
        fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
        # books orbiting behind/in front
        fr.alpha_composite(tw, (ox, oy))
        for (code, sz, ph), (bx, by) in zip(books, ((52, 215), (462, 150), (70, 330))):
            a = 2 * math.pi * (t + ph)
            im = emoji(code, sz).rotate(15 * math.sin(a), expand=True)
            fr.alpha_composite(im, (int(bx - im.width / 2), int(by + 14 * math.sin(a) - im.height / 2)))
        d = ImageDraw.Draw(fr)
        for x, y, ph in stars:
            tw_ = max(0, math.sin(2 * math.pi * t * 2 + ph))
            sparkle(d, x, y, 13 * tw_, int(255 * tw_), (255, 200, 255))
        fr.alpha_composite(top[i], ((S - top[i].width) // 2, 8))
        fr.alpha_composite(bot[i], ((S - bot[i].width) // 2, S - bot[i].height - 10))
        frames.append(rounded(fr))
    return frames, [100] * N


def rarity():
    ra = load("m6/MLP_The_Movie_Rarity_official_artwork.png", h=400)
    rnd = random.Random(2)
    bg = vgrad((60, 10, 50), (25, 5, 40))
    # spotlight cone
    lay = Image.new("RGBA", (S, S)); ImageDraw.Draw(lay).polygon([(200, -10), (312, -10), (470, 520), (42, 520)], fill=(255, 245, 220, 70))
    bg.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
    N = 12
    gems = [(rnd.choice([rnd.randint(0, 130), rnd.randint(380, 470)]), rnd.random(), rnd.randint(30, 52), rnd.uniform(-40, 40)) for _ in range(9)]  # keep off her face
    flashes = {i: [(rnd.choice([rnd.randint(10, 110), rnd.randint(400, 500)]), rnd.randint(40, 330)) for _ in range(rnd.randint(1, 2))] for i in range(N)}
    txt = [grad_text("Llegó la Diva", PACIFICO, 82, [(255, 255, 255), (220, 200, 255), (180, 120, 255), (255, 255, 255)], i / N,
                     glow=(200, 120, 255), shadow=(70, 0, 90)) for i in range(N)]
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        for x, ph, sz, rot in gems:
            p = (ph + t) % 1
            fr.alpha_composite(emoji("1f48e", sz).rotate(rot + 200 * p, expand=True), (x, int(-60 + 580 * p)))
        bob = int(5 * math.sin(2 * math.pi * t))
        fr.alpha_composite(ra, ((S - ra.width) // 2, 25 + bob))
        d = ImageDraw.Draw(fr)
        for x, y in flashes[i]:  # paparazzi flashes
            lay = Image.new("RGBA", (S, S)); ld = ImageDraw.Draw(lay)
            ld.ellipse([x - 55, y - 55, x + 55, y + 55], fill=(255, 255, 255, 170))
            fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18)))
            sparkle(d, x, y, 44, 255)
        # glint on her horn/mane
        g = (i % 4) / 3
        sparkle(d, 200 + 60 * g, 60 + 30 * g, 18 * math.sin(math.pi * g), 255)
        fr.alpha_composite(txt[i], ((S - txt[i].width) // 2, S - txt[i].height - 12))
        frames.append(rounded(fr))
    return frames, [100] * N


def applejack():
    aj = load("m6/MLP_The_Movie_Applejack_official_artwork_2.png", h=410)
    rnd = random.Random(3)
    bg = vgrad((255, 150, 60), (250, 90, 110))
    N = 12
    apples = [(rnd.choice([rnd.randint(-10, 150), rnd.randint(380, 470)]), rnd.random(), rnd.randint(40, 62)) for _ in range(10)]  # keep off her face
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        rays(fr, t * 30, [(255, 230, 120), (255, 180, 80)], alpha=90, c=(256, 330))
        sun = Image.new("RGBA", (S, S)); ImageDraw.Draw(sun).ellipse([176, 250, 336, 410], fill=(255, 235, 150, 255))
        fr.alpha_composite(sun.filter(ImageFilter.GaussianBlur(4)))
        # ground silhouette
        ImageDraw.Draw(fr).polygon([(0, 440), (140, 420), (300, 435), (512, 415), (512, 512), (0, 512)], fill=(90, 40, 20, 255))
        hop = abs(math.sin(2 * math.pi * t))
        fr.alpha_composite(aj, ((S - aj.width) // 2 + 10, int(30 + 30 * (1 - hop))))
        for x, ph, sz in apples:
            p = (ph + t) % 1
            fr.alpha_composite(emoji("1f34e", sz).rotate(360 * p, expand=True), (x, int(-70 + 600 * p)))
        wob = 4 * math.sin(2 * math.pi * t * 2)
        txt = grad_text("¡YIIIJAAA!", RYE, 86, [(255, 240, 150), (255, 200, 60), (255, 150, 40), (255, 240, 150)], t,
                        stroke=(70, 30, 10), glow=(255, 220, 120), shadow=(40, 15, 5)).rotate(wob, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(txt, ((S - txt.width) // 2, S - txt.height - 8))
        frames.append(rounded(fr))
    return frames, [90] * N


def fluttershy():
    fl = load("m6/FANMADE_Fluttershy_being_cute.png", w=450)
    rnd = random.Random(4)
    bg = vgrad((215, 245, 255), (200, 240, 190))
    ImageDraw.Draw(bg).ellipse([-120, 330, 632, 700], fill=(170, 225, 150, 255))
    for k, (code, x, y) in enumerate([("1f337", 20, 370), ("1f33c", 440, 390), ("1f338", 90, 440), ("1f33c", 380, 455), ("1f337", 470, 330)]):
        bg.alpha_composite(emoji(code, 50), (x - 25, y - 25))
    N = 12
    frames = []
    yay_f = ImageFont.truetype(PACIFICO, 30)
    for i in range(N):
        t = i / N
        fr = bg.copy()
        breathe = 1 + 0.015 * math.sin(2 * math.pi * t)
        q = fl.resize((int(fl.width * breathe), int(fl.height * breathe)))
        fr.alpha_composite(q, ((S - q.width) // 2, 400 - q.height + 20))
        # butterflies circling
        for k in range(2):
            a = 2 * math.pi * (t + k / 2)
            b = emoji("1f98b", 46)
            b = b.resize((46, int(46 * (0.55 + 0.45 * abs(math.cos(4 * math.pi * t + k))))))
            fr.alpha_composite(b, (int(256 + 190 * math.cos(a) - 23), int(95 + 40 * math.sin(a) - 23)))
        # bunny hopping across the grass
        bx = 20 + 470 * t
        by = 455 - 30 * abs(math.sin(2 * math.pi * t * 3))
        fr.alpha_composite(emoji("1f430", 44), (int(bx - 22), int(by - 22)))
        # the tiny "yay"
        d = ImageDraw.Draw(fr)
        s_ = 1 + 0.12 * max(0, math.sin(2 * math.pi * t * 2))
        f = ImageFont.truetype(PACIFICO, int(30 * s_))
        d.text((340, 250), "yay", font=f, fill=(255, 120, 190), stroke_width=3, stroke_fill="white", anchor="mm")
        sparkle(d, 372, 236, 8 * max(0, math.sin(2 * math.pi * t * 2)), 255, (255, 200, 230))
        frames.append(rounded(fr))
    return frames, [100] * N


def glasses(p):
    W, H = 28, 6
    g = Image.new("RGBA", (W * p, H * p))
    d = ImageDraw.Draw(g)
    px = lambda x, y, c: d.rectangle([x * p, y * p, x * p + p - 1, y * p + p - 1], fill=c)
    for x in range(W):
        px(x, 0, "black")
    for lens in (2, 16):
        for y in range(1, 5):
            inset = 1 if y == 4 else 0
            for x in range(lens + inset, lens + 10 - inset):
                px(x, y, "black")
        px(lens + 1, 1, "white"); px(lens + 2, 1, "white"); px(lens + 2, 2, "white"); px(lens + 3, 2, "white")
    return g


def dash():
    rd = load("rd/FANMADE_Rainbow_Dash_standing_vector.png", h=440)
    ox, oy = (S - rd.width) // 2 + 20, 8
    gl = glasses(6).rotate(-4, expand=True, resample=Image.NEAREST)
    gx = ox + 0.42 * rd.width - gl.width / 2
    gy_end = oy + 0.25 * rd.height - gl.height / 2
    frames, delays = [], []
    for i in range(20):
        fr = Image.new("RGBA", (S, S))
        if i >= 14:
            rays(fr, i * 8, RAINBOW, alpha=200, n=12, c=(256, 180))
            m = Image.new("L", (S, S)); ImageDraw.Draw(m).ellipse([6, -60, 506, 420], fill=255)
            fr.putalpha(Image.fromarray(np.minimum(np.asarray(fr.getchannel("A")), np.asarray(m))))
        fr.alpha_composite(rd, (ox, oy))
        d = ImageDraw.Draw(fr)
        if i < 10:  # coolness meter fills to 20%
            pct = int(20 * min(1, i / 8))
            d.rounded_rectangle([56, 400, 456, 440], 12, fill=(30, 30, 30, 255), outline="white", width=4)
            if pct:
                d.rounded_rectangle([62, 406, 62 + 388 * pct / 100, 434], 8, fill=(103, 190, 90, 255))
            f = ImageFont.truetype(IMPACT, 34)
            d.text((256, 380), f"NIVEL DE COOL: {pct}%", font=f, fill="white", stroke_width=4, stroke_fill="black", anchor="mm")
            d.text((256, 470), "CARGANDO...", font=ImageFont.truetype(IMPACT, 26), fill="white", stroke_width=3, stroke_fill="black", anchor="mm")
        if i >= 9:  # glasses drop
            k = min(1, (i - 9) / 4)
            fr.alpha_composite(gl, (int(gx), int(-80 + (gy_end + 80) * k)))
        if i >= 14:
            sc = {14: 1.8, 15: 1.2, 16: 0.95}.get(i, 1.0)
            meme_text(fr, "20% MÁS COOL", scale=sc, size=96)
        if i == 14:
            a = fr.getchannel("A")
            fr = Image.blend(fr.convert("RGB"), Image.new("RGB", (S, S), "white"), 0.5).convert("RGBA"); fr.putalpha(a)
        frames.append(fr)
        delays.append(1200 if i == 19 else 110 if i < 9 else 80)
    return frames, delays


def pinkie():
    pk = load("pp/MLP_The_Movie_Pinkie_Pie_official_artwork.png", h=380)
    rnd = random.Random(6)
    bg = vgrad((255, 170, 220), (255, 230, 120))
    N = 14
    CONF = [(255, 80, 160), (255, 210, 40), (80, 200, 255), (140, 230, 90), (190, 120, 255), (255, 255, 255)]
    # two cannon bursts per loop, particles with gravity
    parts = []
    for side, x0 in ((1, 40), (-1, 470)):
        for _ in range(45):
            ang = math.radians(rnd.uniform(55, 85))
            v = rnd.uniform(40, 56)
            parts.append((x0, 470, side * v * math.cos(ang), -v * math.sin(ang), rnd.choice(CONF), rnd.uniform(0, 6)))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        rays(fr, t * 40, [(255, 255, 255)], alpha=60, n=14, c=(256, 230))
        for code, x, y, ph in (("1f388", 10, 40, 0), ("1f388", 420, 20, .5), ("1f388", 440, 170, .25)):
            fr.alpha_composite(emoji(code, 80), (x, int(y + 10 * math.sin(2 * math.pi * (t + ph)))))
        hop = abs(math.sin(2 * math.pi * t))
        fr.alpha_composite(pk, ((S - pk.width) // 2, int(40 + 35 * (1 - hop))))
        d = ImageDraw.Draw(fr)
        tt = float(i % 7)  # two bursts per loop
        for x0, y0, vx, vy, col, spin in parts:
            x, y = x0 + vx * tt, y0 + vy * tt + 3.2 * tt * tt
            if y < 530:
                a = spin + tt * 0.9
                dx, dy = 8 * math.cos(a), 5
                d.polygon([(x - dx, y - dy), (x + dx, y - dy), (x + dx, y + dy), (x - dx, y + dy)], fill=col + (255,))
        kick = 1.3 if i % 7 < 2 else 1.0
        for x, flip in ((-6, False), (430, True)):
            c = emoji("1f389", int(90 * kick))
            fr.alpha_composite(c.transpose(Image.FLIP_LEFT_RIGHT) if flip else c, (x, 512 - c.height - 4))
        meme_text(fr, "¡FIESTAAA!", scale=1.0 + 0.07 * hop, dy=-int(8 * hop), y=445, size=104)
        frames.append(rounded(fr))
    return frames, [85] * N


def save(name, frames, delays):
    d = os.path.join(here, "m6frames", name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"f{i:02d}.png"))
    with open(os.path.join(d, "delays.txt"), "w") as fh:
        fh.write(" ".join(map(str, delays)))


if __name__ == "__main__":
    want = sys.argv[1:]
    for name, path, txt in REPLIES:
        if not want or name in want:
            save(name, *reply(path, txt)); print(name)
    for name in ("twilight", "rarity", "applejack", "fluttershy", "dash", "pinkie"):
        if not want or "c_" + name in want:
            save("c_" + name, *globals()[name]()); print("c_" + name)


def meme_block(fr, txt, anchor_y, top=True, size=64, maxw=490, max_lines=3, line_gap=0.95):
    """word-wrapped Impact block; grows down from anchor_y (top=True) or up from it."""
    words = txt.split()
    while True:
        f = ImageFont.truetype(IMPACT, size)
        lines, cur = [], ""
        for w in words:
            cand = (cur + " " + w).strip()
            if f.getbbox(cand, stroke_width=6)[2] <= maxw or not cur:
                cur = cand
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= max_lines or size < 20:
            break
        size -= 3
    lh = int(size * line_gap)
    y0 = anchor_y if top else anchor_y - lh * len(lines)
    d = ImageDraw.Draw(fr)
    for k, line in enumerate(lines):
        d.text((S / 2, y0 + k * lh + lh / 2), line, font=f, fill="white", stroke_width=6, stroke_fill="black", anchor="mm")
    return y0 + lh * len(lines) if top else y0
