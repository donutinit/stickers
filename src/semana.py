"""Kratos Chayanne for every day of the week, with real photos (Wikimedia Commons) for flowers and backgrounds."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import m6
from chayanne import text, head, sparkles, rand_pts, fredoka
from kratos import heart_mask

S = 512
N = 10
here = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(here, "fotos")
GOLD = [(255, 230, 120), (255, 170, 40), (255, 240, 170), (255, 230, 120)]
PINKS = [(255, 255, 255), (255, 210, 230), (255, 255, 255)]


def photo(name, blur=0, bright=1.0, sat=1.1, focus=(0.5, 0.5)):
    """cover-crop a photo to 512x512 around `focus`."""
    im = Image.open(os.path.join(FOTOS, name)).convert("RGB")
    W, H = im.size
    s = min(W, H)
    x0 = min(max(0, focus[0] * W - s / 2), W - s); y0 = min(max(0, focus[1] * H - s / 2), H - s)
    im = im.crop((int(x0), int(y0), int(x0 + s), int(y0 + s))).resize((S, S), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(sat)).enhance(bright)
    return im.convert("RGBA")


def cut(name, h=None, w=None):
    im = Image.open(os.path.join(FOTOS, name + "_cut.png")).convert("RGBA")
    sc = h / im.height if h else w / im.width
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def glow_behind(fr, im, xy, col=(255, 255, 255), r=12, a=200):
    g = Image.new("RGBA", (S, S))
    m = Image.new("L", (S, S)); m.paste(im.getchannel("A"), xy)
    g.putalpha(m.filter(ImageFilter.MaxFilter(r | 1)).filter(ImageFilter.GaussianBlur(r)).point(lambda v: v * a // 255))
    col_l = Image.new("RGBA", (S, S), col + (0,)); col_l.putalpha(g.getchannel("A"))
    fr.alpha_composite(col_l)


def cursive(fr, txt, y, size, stops, t, stroke=(255, 255, 255), glow=(255, 80, 200), shadow=(90, 0, 60)):
    im = m6.grad_text(txt, m6.PACIFICO, size, stops, t, stroke=stroke, glow=glow, shadow=shadow)
    fr.alpha_composite(im, ((S - im.width) // 2, y if y >= 0 else S - im.height + y))


def floaters(fr, t, codes, xs, y0=470, y1=80, sz=36):
    for k, x in enumerate(xs):
        p = (k / len(xs) + t) % 1
        e = m6.emoji(codes[k % len(codes)], sz).copy()
        e.putalpha(e.getchannel("A").point(lambda a: int(a * min(1, (1 - p) * 2.5))))
        fr.alpha_composite(e, (int(x + 8 * math.sin(p * 6)), int(y0 - (y0 - y1) * p)))


# ------------------------------------------------------------------ Lunes: Kratos-sun over a real sunrise
def lunes():
    bg = photo("amanecer.jpg", sat=1.25, focus=(0.55, 0.6))
    face = head("kratos_enojado.png", 190)
    a = np.asarray(face).astype(float)
    a[..., :3] = a[..., :3] * np.array([1.0, 0.88, 0.35]) + np.array([60, 50, 0])
    face = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    sun_l, sun_r = cut("girasol", w=170), cut("girasol", w=150).transpose(Image.FLIP_LEFT_RIGHT)
    cx, cy = 256, 225
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        lay = Image.new("RGBA", (S, S)); dl = ImageDraw.Draw(lay)
        dl.ellipse([cx - 190, cy - 190, cx + 190, cy + 190], fill=(255, 240, 150, 70))
        for k in range(16):
            ang = 2 * math.pi * (k / 16 + t / 16)
            L = 175 + (22 if k % 2 else 0)
            p1 = (cx + 105 * math.cos(ang - 0.12), cy + 105 * math.sin(ang - 0.12))
            p2 = (cx + 105 * math.cos(ang + 0.12), cy + 105 * math.sin(ang + 0.12))
            dl.polygon([p1, p2, (cx + L * math.cos(ang), cy + L * math.sin(ang))], fill=(255, 225, 60, 235))
        dl.ellipse([cx - 112, cy - 112, cx + 112, cy + 112], fill=(255, 230, 90, 255))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
        fr.alpha_composite(face, (cx - face.width // 2, cy - face.height // 2 + int(3 * math.sin(2 * math.pi * t))))
        sway = 4 * math.sin(2 * math.pi * t)
        for im, xy in ((sun_l, (-40, 300)), (sun_r, (390, 320))):
            r = im.rotate(sway, expand=True, resample=Image.BICUBIC)
            fr.alpha_composite(r, xy)
        text(fr, ["Feliz Lunes"], (S / 2, 46), 76, [(250, 205, 40, 255)], stroke=(40, 40, 60), shadow=(0, 0, 0))
        text(fr, ["Buen día", "gente madrugadora"], (S / 2, 412), 46, [(255, 245, 160, 255)], stroke=(60, 70, 30), shadow=(0, 0, 0))
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Martes: face in a real rose
def martes():
    bg = photo("tulipanes.jpg", blur=6, sat=1.2, bright=0.95)
    rose = cut("rosa", w=430)
    face = head("kratos_serio.png", 200)
    circ = Image.new("L", face.size); ImageDraw.Draw(circ).ellipse([0, 0, face.width, face.height], fill=255)
    face.putalpha(Image.fromarray(np.minimum(np.asarray(face.getchannel("A")), np.asarray(circ))))
    pts = rand_pts(12, 14, (100, 60, 420, 360))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        sway = 3 * math.sin(2 * math.pi * t)
        r = rose.rotate(sway, resample=Image.BICUBIC)
        rx, ry = (S - r.width) // 2, 70
        glow_behind(fr, r, (rx, ry), (255, 200, 230), 14, 180)
        fr.alpha_composite(r, (rx, ry))
        fr.alpha_composite(face.rotate(sway, expand=True, resample=Image.BICUBIC),
                           (int(rx + r.width * 0.52 - face.width / 2), int(ry + r.height * 0.47 - face.height / 2)))
        floaters(fr, t, ["1f496", "1f495"], [20, 70, 430, 470])
        fr.alpha_composite(m6.emoji("1f970", 90), (410, 380))
        cursive(fr, "Feliz Martes", 4, 84, GOLD, t, glow=(255, 120, 60), shadow=(90, 40, 0))
        cursive(fr, "¡Dios te bendiga!", 390, 58, PINKS, t, stroke=(200, 30, 90), glow=(255, 80, 150))
        sparkles(fr, t, pts)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Miércoles: cat filter in a daisy meadow
def cat_head(h):
    hd = head("kratos_serio.png", h)
    W, H = hd.size
    out = Image.new("RGBA", (W + 80, H + 90)); ox, oy = 40, 90
    d = ImageDraw.Draw(out)
    for cx, s in ((ox + W * 0.3, -1), (ox + W * 0.7, 1)):
        d.polygon([(cx - 50, oy + 55), (cx + s * 22, oy - 55), (cx + 50, oy + 45)], fill=(40, 30, 35, 255))
        d.polygon([(cx - 28, oy + 45), (cx + s * 15, oy - 25), (cx + 28, oy + 38)], fill=(255, 150, 190, 255))
    out.alpha_composite(hd, (ox, oy))
    bl = Image.new("RGBA", out.size); db = ImageDraw.Draw(bl)
    for cx in (ox + W * 0.27, ox + W * 0.73):
        db.ellipse([cx - 30, oy + H * 0.6 - 15, cx + 30, oy + H * 0.6 + 15], fill=(255, 90, 140, 130))
    out.alpha_composite(bl.filter(ImageFilter.GaussianBlur(5)))
    d.ellipse([ox + W * 0.5 - 9, oy + H * 0.56 - 6, ox + W * 0.5 + 9, oy + H * 0.56 + 6], fill=(255, 120, 160, 255))
    return out


def miercoles():
    bg = photo("margaritas.jpg", blur=2.5, sat=1.2, focus=(0.5, 0.6))  # slight blur keeps it under 500 KB
    kat = cat_head(300)
    bf = cut("mariposa", h=110)
    pts = rand_pts(13, 12, (0, 150, 330, 512))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        bob = int(5 * math.sin(2 * math.pi * t))
        glow_behind(fr, kat, (-20, S - kat.height + 40 + bob), (255, 255, 255), 10, 200)
        fr.alpha_composite(kat, (-20, S - kat.height + 40 + bob))
        flap = 0.55 + 0.45 * abs(math.cos(2 * math.pi * t * 2))
        b = bf.resize((int(bf.width * flap), bf.height))
        fr.alpha_composite(b, (int(390 + 25 * math.sin(2 * math.pi * t) - b.width / 2), int(300 + 20 * math.cos(4 * math.pi * t))))
        text(fr, ["Feliz Miércoles"], (S / 2, 44), 64, [(230, 60, 150, 255)])
        text(fr, ["¡YA VAMOS A", "LA MITAD!"], (S - 16, 150), 44, [(120, 60, 200, 255), (240, 130, 30, 255)], anchor="rm", maxw=260)
        sparkles(fr, t, pts)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Jueves: cafecito
def jueves():
    bg = photo("amanecer.jpg", blur=5, sat=1.3, bright=1.05, focus=(0.7, 0.5))
    hd = head("kratos_barba.png", 520).crop((0, 0, 99999, 330))
    hd = hd.crop(hd.getbbox())
    cup = cut("cafe", w=220)
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        hx = 10
        glow_behind(fr, hd, (hx, 105), (255, 240, 200), 12, 170)
        fr.alpha_composite(hd, (hx, 105))
        glow_behind(fr, cup, (290, 290), (255, 255, 255), 10, 220)
        fr.alpha_composite(cup, (290, 290))
        d = ImageDraw.Draw(fr)
        for k in range(3):  # steam
            p = (t + k / 3) % 1
            x = 400 + 18 * math.sin(p * 7 + k)
            y = 300 - 120 * p
            e = m6.emoji("1f495", int(30 + 20 * p)).copy()
            e.putalpha(e.getchannel("A").point(lambda a: int(a * (1 - p))))
            fr.alpha_composite(e, (int(x - e.width / 2), int(y - e.height / 2)))
        cursive(fr, "Feliz Jueves", 4, 86, GOLD, t, glow=(255, 150, 60), shadow=(80, 40, 0))
        text(fr, ["Un cafecito", "y a darle"], (130, 440), 42, [(255, 255, 255, 255)], stroke=(120, 60, 20), shadow=(40, 20, 0), maxw=250)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Viernes: party lights
def viernes():
    bg = photo("bokeh.jpg", sat=1.4, bright=1.1)
    body = head("kratos_grito.png", 360)
    rnd = random.Random(5)
    conf = [(rnd.randint(0, S), rnd.random(), rnd.choice([(255, 80, 160), (255, 210, 40), (80, 200, 255), (140, 230, 90)]), rnd.uniform(0, 6)) for _ in range(40)]
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        hop = abs(math.sin(2 * math.pi * t))
        bx, by = (S - body.width) // 2, int(110 - 18 * hop)
        glow_behind(fr, body, (bx, by), (255, 220, 255), 12, 190)
        fr.alpha_composite(body, (bx, by))
        d = ImageDraw.Draw(fr)
        for x, ph, col, sp in conf:
            y = ((ph + t) % 1) * (S + 40) - 20
            a = sp + y / 20
            d.polygon([(x - 7 * math.cos(a), y - 4), (x + 7 * math.cos(a), y - 4), (x + 7 * math.cos(a), y + 4), (x - 7 * math.cos(a), y + 4)], fill=col + (255,))
        fr.alpha_composite(m6.emoji("1f389", 90), (6, 400)); fr.alpha_composite(m6.emoji("1f389", 90).transpose(Image.FLIP_LEFT_RIGHT), (414, 400))
        cursive(fr, "¡Feliz Viernes!", 4, 84, [(255, 240, 120), (255, 120, 200), (120, 220, 255), (255, 240, 120)], t, glow=(255, 60, 200), shadow=(60, 0, 60))
        text(fr, ["Que se ponga bueno"], (S / 2, 470), 44, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(60, 0, 40))
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Sábado: bouquet at the beach
def sabado():
    bg = photo("playa.jpg", sat=1.2, focus=(0.5, 0.5))
    hd = head("kratos_serio.png", 300)
    ramo = cut("ramo", w=260)
    pts = rand_pts(16, 12, (90, 30, 420, 460))
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        bob = int(4 * math.sin(2 * math.pi * t))
        hx, hy = (S - hd.width) // 2, 95 + bob
        glow_behind(fr, hd, (hx, hy), (255, 255, 255), 10, 200)
        fr.alpha_composite(hd, (hx, hy))
        r = ramo.rotate(5 * math.sin(2 * math.pi * t), expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(r, ((S - r.width) // 2 + 120, 320))
        cursive(fr, "Feliz Sábado", 4, 86, [(255, 255, 255), (180, 240, 255), (255, 255, 255)], t, stroke=(20, 120, 180), glow=(80, 200, 255), shadow=(0, 50, 90))
        text(fr, ["A disfrutar", "el día"], (110, 430), 42, [(255, 255, 255, 255)], stroke=(20, 120, 180), shadow=(0, 40, 70), maxw=230)
        sparkles(fr, t, pts)
        frames.append(m6.rounded(fr))
    return frames


# ------------------------------------------------------------------ Domingo: squashed bobblehead on real pink roses
def domingo():
    bg = photo("rosas_pared.jpg", blur=2, sat=1.15, bright=1.05)
    hm = heart_mask(440)
    heart = Image.new("RGBA", (440, 440), (255, 120, 200, 0)); heart.putalpha(hm.point(lambda v: v * 150 // 255))
    rim = Image.new("RGBA", (440, 440), (255, 255, 255, 0)); rim.putalpha(hm.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(6)))
    bg.alpha_composite(rim, (36, 40)); bg.alpha_composite(heart, (36, 40))
    body = Image.open(os.path.join(here, "kratos", "kratos_cuerpo.webp")).convert("RGBA")
    body = body.crop(body.getbbox())
    W0, H0 = body.size
    ImageDraw.Draw(body).rectangle([int(0.52 * W0), 0, int(0.78 * W0), int(0.105 * H0)], fill=(0, 0, 0, 0))
    body = body.crop(body.getbbox())
    sx, sy = 1.34, 0.47
    body = body.resize((int(body.width * sx), int(body.height * sy)), Image.LANCZOS)
    neck_x = int(0.64 * W0 * sx)
    big = head("kratos_serio.png", int(0.25 * H0 * sx))
    ramo = cut("ramo", w=120)
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        bx, by = (S - body.width) // 2, 168
        fr.alpha_composite(body, (bx, by))
        h2 = big.rotate(15 * math.sin(2 * math.pi * t), expand=True, resample=Image.BICUBIC)
        hc = (bx + neck_x, by + 34 - big.height * 0.42)
        fr.alpha_composite(h2, (int(hc[0] - h2.width / 2), int(hc[1] - h2.height / 2)))
        fr.alpha_composite(ramo, (10, 330)); fr.alpha_composite(ramo.transpose(Image.FLIP_LEFT_RIGHT), (S - ramo.width - 10, 330))
        text(fr, ["Feliz Domingo Guapa"], (S / 2, 44), 58, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(80, 0, 50))
        text(fr, ["Que te vaya bien hoy y no", "se te olvide tomar agua"], (S / 2, 420), 36, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(80, 0, 50))
        fr.alpha_composite(m6.emoji("1f4a7", 46), (440, 450))
        frames.append(m6.rounded(fr))
    return frames


DAYS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

if __name__ == "__main__":
    for name in sys.argv[1:] or DAYS:
        frames = globals()[name]()
        d = os.path.join(here, "semframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(["110"] * len(frames)))
        print(name)
