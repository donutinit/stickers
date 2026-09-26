"""Buchón stickers inspired by "Chico Enamorado" (El Ezequiel): black + gold, gothic gold letters, money rain."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6

S = 512
N = 12
here = os.path.dirname(os.path.abspath(__file__))
GOTHIC = os.path.join(here, "fonts", "NewRocker.ttf")  # Fraktur V read as B
GOLD_STOPS = [(255, 240, 170), (212, 160, 40), (255, 225, 120), (150, 100, 20), (255, 240, 170)]


def gold_text(txt, size, t=0.0, maxw=480):
    """gothic letters, metallic gold gradient (vertical bands + moving glint), black outline, drop shadow."""
    f = m6.fit_font(GOTHIC, txt, size, maxw, 7)
    pad = 24
    l, tp, r, b = f.getbbox(txt, stroke_width=7)
    w, h = r - l + 2 * pad, b - tp + 2 * pad
    org = (pad - l, pad - tp)
    mask = Image.new("L", (w, h)); ImageDraw.Draw(mask).text(org, txt, font=f, fill=255)
    st = Image.new("L", (w, h)); ImageDraw.Draw(st).text(org, txt, font=f, fill=255, stroke_width=7, stroke_fill=255)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    k = (y * 1.0 + x * 0.15) * (len(GOLD_STOPS) - 1)
    k = np.clip(k, 0, len(GOLD_STOPS) - 1.001)
    lo = k.astype(int); fr_ = (k - lo)[..., None]
    cols = np.array(GOLD_STOPS, float)
    rgb = cols[lo] * (1 - fr_) + cols[lo + 1] * fr_
    glint = np.exp(-(((x - y * 0.3) - (t * 1.6 - 0.3)) / 0.05) ** 2)[..., None]  # light sweep
    rgb = np.clip(rgb + 120 * glint, 0, 255)
    fill = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA"); fill.putalpha(mask)
    out = Image.new("RGBA", (w, h))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sh.putalpha(st.filter(ImageFilter.GaussianBlur(4)))
    out.alpha_composite(sh, (3, 5))
    blk = Image.new("RGBA", (w, h), (10, 8, 5, 0)); blk.putalpha(st)
    out.alpha_composite(blk)
    out.alpha_composite(fill)
    return out.crop(out.getbbox())


def greek_key_bg():
    """black velvet with a gold Versace-style meander border."""
    t = np.linspace(0, 1, S)
    yy, xx = np.meshgrid(t, t, indexing="ij")
    v = 18 + 30 * np.exp(-((xx - .5) ** 2 + (yy - .45) ** 2) * 5)
    bg = Image.fromarray(np.dstack([v, v * 0.9, v * 0.6]).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(bg)
    g = (212, 165, 50, 255)
    u, band = 6, 6 * 6  # unit and band width
    for side in range(4):
        lay = Image.new("RGBA", (S, band)); ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 0, S, 2], fill=g); ld.rectangle([0, band - 3, S, band], fill=g)
        for x0 in range(0, S, 5 * u):  # meander motif
            pts = [(x0, band - 1.5 * u), (x0, 1.5 * u), (x0 + 4 * u, 1.5 * u), (x0 + 4 * u, band - 2.5 * u),
                   (x0 + 2 * u, band - 2.5 * u), (x0 + 2 * u, 2.5 * u + u)]
            ld.line(pts, fill=g, width=3)
            ld.line([(x0, band - 1.5 * u), (x0 + 5 * u, band - 1.5 * u)], fill=g, width=3)
        lay = lay.rotate(-90 * side, expand=True)
        pos = [(0, 0), (S - band, 0), (0, S - band), (0, 0)][side]
        bg.alpha_composite(lay, pos)
    return bg


def gold_chain(fr, center, rx, ry, a0, a1, link=14, t=0.0):
    """chain of gold links along an elliptical arc (a0..a1 radians), with a medallion at the bottom."""
    d = ImageDraw.Draw(fr)
    n = int(abs(a1 - a0) * (rx + ry) / 2 / (link * 0.8))
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        x, y = center[0] + rx * math.cos(a), center[1] + ry * math.sin(a)
        rot = a + math.pi / 2
        ex, ey = link * 0.62, link * 0.36
        pts = [(x + ex * math.cos(rot + k * 0.5) * math.cos(k * 0.5) - ey * math.sin(rot) * math.sin(k * 0.5),
                y + ex * math.sin(rot + k * 0.5) * math.cos(k * 0.5) + ey * math.cos(rot) * math.sin(k * 0.5)) for k in range(13)]
        shade = (255, 215, 90) if i % 2 else (190, 140, 30)
        d.line(pts + [pts[0]], fill=(60, 40, 5, 255), width=6)
        d.line(pts + [pts[0]], fill=shade + (255,), width=3)
    # medallion
    mx, my = center[0] + rx * math.cos((a0 + a1) / 2), center[1] + ry * math.sin((a0 + a1) / 2)
    d.ellipse([mx - 20, my - 4, mx + 20, my + 36], fill=(60, 40, 5, 255))
    d.ellipse([mx - 17, my - 1, mx + 17, my + 33], fill=(235, 190, 70, 255))
    m6.sparkle(d, mx - 6, my + 10, 12 * abs(math.sin(math.pi * 2 * t)), 255)


def money_rain(fr, t, rnd_items):
    for x, ph, sz, spin, code in rnd_items:
        p = (ph + t) % 1
        e = m6.emoji(code, sz).rotate(spin * 360 * p, expand=True, resample=Image.BICUBIC)
        fr.alpha_composite(e, (int(x + 18 * math.sin(p * 9)), int(-80 + 640 * p)))


def base_frames(pony, pony_xy, chain, text_lines, extras=None, seed=0, rain=("1f4b5",), face=None):
    rnd = random.Random(seed)
    bg = greek_key_bg()
    items = []
    while len(items) < 9:
        x, ph = rnd.randint(40, 440), rnd.random()
        if face and face[0] - 40 < x < face[2]:
            continue  # bills fall beside the face, never across it
        items.append((x, ph, rnd.randint(46, 64), rnd.choice([-1, 1]) * rnd.uniform(0.3, 0.8), rnd.choice(rain)))
    sparks = [(rnd.randint(40, 470), rnd.randint(40, 300), rnd.uniform(0, 6.3)) for _ in range(12)]
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        if extras:
            extras(fr, t, "behind")
        money_rain(fr, t, items[:4])
        fr.alpha_composite(pony, pony_xy)
        if chain:
            gold_chain(fr, *chain, t=t)
        if extras:
            extras(fr, t, "front")
        money_rain(fr, t, items[4:])
        d = ImageDraw.Draw(fr)
        for x, y, ph in sparks:
            if face and face[0] < x < face[2] and face[1] < y < face[3]:
                continue
            s = max(0, math.sin(2 * math.pi * t * 2 + ph))
            m6.sparkle(d, x, y, 14 * s, int(255 * s), (255, 230, 150))
        for txt, size, y in text_lines:
            im = gold_text(txt, size, t)
            fr.alpha_composite(im, ((S - im.width) // 2, y))
        frames.append(m6.rounded(fr))
    return frames, [90] * N


def enamorado():
    rd = m6.load("rd/FANMADE_Rainbow_Dash_chillin.png", h=400)
    def extras(fr, t, layer):
        if layer == "front":
            for k, (x, y) in enumerate(((40, 250), (420, 260))):
                s = 1 + 0.15 * max(0, math.sin(2 * math.pi * (t * 2 + k * 0.5)))
                h = m6.emoji("1f496", int(64 * s))
                fr.alpha_composite(h, (x - h.width // 2 + 30, y - h.height // 2))
            fr.alpha_composite(m6.emoji("1f339", 80).rotate(20, expand=True), (330, 360))
    return base_frames(rd, ((S - rd.width) // 2, 50), ((256, 300), 95, 40, 0.15, math.pi - 0.15),
                       [("Soy un Chico", 74, 14), ("Enamorado", 92, 405)], extras, seed=1, face=(150, 60, 400, 230))


def hummers():
    aj = m6.load("m6/MLP_The_Movie_Applejack_official_artwork.png", h=330)
    suv = m6.emoji("1f699", 60)
    def extras(fr, t, layer):
        if layer == "front":
            for k in range(7):  # seven Hummers parked in a row, bouncing to the beat
                bob = int(4 * abs(math.sin(2 * math.pi * (t * 2 + k / 7))))
                fr.alpha_composite(suv, (40 + k * 62, 392 - bob))
    return base_frames(aj, ((S - aj.width) // 2, 70), ((250, 200), 55, 30, 0.35, math.pi - 0.35),
                       [("Tengo Siete Hummers", 80, 10)], extras, seed=2, rain=("1f4b5", "1f4b0"), face=(170, 90, 340, 200))


def bien_loco():
    pk = m6.load("pp/FANMADE_Pinkie_Pie_smiling.png", w=470)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 60, [(212, 165, 50), (60, 45, 10)], alpha=90, n=16, c=(220, 250))
    return base_frames(pk, (10, S - pk.height + 30), ((180, 380), 110, 60, 0.4, math.pi - 0.4),
                       [("Ando Bien Loco", 92, 12)], extras, seed=3, face=(60, 170, 320, 400))


def tu_boca():
    ra = m6.load("m6/FANMADE_Rarity_vector_by_almostfictional.png", h=380)
    kisses = [(60, 120, -15), (420, 200, 20), (70, 330, 10)]
    def extras(fr, t, layer):
        if layer == "front":
            for k, (x, y, rot) in enumerate(kisses):
                a = max(0, math.sin(2 * math.pi * (t + k / 3)))
                e = m6.emoji("1f48b", 70).rotate(rot, expand=True)
                e.putalpha(e.getchannel("A").point(lambda v: int(v * (0.35 + 0.65 * a))))
                fr.alpha_composite(e, (x - 35, y - 35))
            fr.alpha_composite(m6.emoji("1f339", 86).rotate(-25, expand=True), (380, 330))
    return base_frames(ra, ((S - ra.width) // 2 + 10, 40), ((270, 190), 60, 30, 0.3, math.pi - 0.3),
                       [("Me Falta tu Boca", 86, 408)], extras, seed=4, face=(230, 40, 400, 170))


def culiacan():
    tw = m6.load("m6/MLP_The_Movie_Twilight_Sparkle_official_artwork_2.png", h=360)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 40, [(212, 165, 50), (40, 30, 8)], alpha=80, n=18, c=(256, 230))
        else:
            g = m6.emoji("1f413", 96)
            flap = 1 + 0.06 * math.sin(2 * math.pi * t * 3)
            g = g.resize((int(96 * flap), int(96 / flap)))
            fr.alpha_composite(g, (30, 300))
            fr.alpha_composite(m6.emoji("1f1f2-1f1fd", 76), (410, 312))
    return base_frames(tw, ((S - tw.width) // 2, 48), None,
                       [("Puro Culiacán", 86, 10), ("Sinaloa", 96, 405)], extras, seed=5, face=(170, 90, 330, 200))


def arremangado():
    pk = m6.load("pp/FANMADE_Pinkie_Pie_vector_2.t.png", h=340)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 50, [(212, 165, 50), (50, 38, 10)], alpha=80, n=16, c=(180, 280))
        else:
            for k, (x, y) in enumerate(((60, 210), (70, 330))):  # hearts pointing at the flank
                s = 1 + 0.18 * max(0, math.sin(2 * math.pi * (t * 2 + k * 0.5)))
                h = m6.emoji("1f496", int(56 * s))
                fr.alpha_composite(h, (x - h.width // 2, y - h.height // 2))
            fr.alpha_composite(m6.emoji("1f525", 64), (20, 250))
    return base_frames(pk, ((S - pk.width) // 2 + 20, 76), None,
                       [("Soy Fan de tu", 80, 10), ("Culito Arremangado", 80, 412)], extras, seed=6, face=(250, 100, 420, 220))


def gracias_dios():
    rd = m6.load("rd/FANMADE_proud_Rainbow_Dash_vector.png", h=330)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 50, [(212, 165, 50), (50, 38, 10)], alpha=90, n=18, c=(256, 230))
        else:
            fr.alpha_composite(m6.emoji("1f64f", 90), (20, 300))
            fr.alpha_composite(m6.emoji("1f4b0", 80), (410, 300))
    return base_frames(rd, ((S - rd.width) // 2, 70), ((250, 250), 70, 35, 0.35, math.pi - 0.35),
                       [("Gracias a Dios", 84, 10), ("y a la Virgen", 76, 412)], extras, seed=7, face=(170, 80, 360, 230))


if __name__ == "__main__":
    for name in sys.argv[1:] or ("enamorado", "hummers", "bien_loco", "tu_boca", "culiacan", "arremangado", "gracias_dios"):
        frames, delays = globals()[name]()
        d = os.path.join(here, "buchframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
        print(name)
