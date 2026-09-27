"""Lotería: cartas estilo Don Clemente con los personajes de la galería (fijos)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from scipy import ndimage

S = 512
here = os.path.dirname(os.path.abspath(__file__))
RYE = os.path.join(here, "Rye.ttf")
OUT = os.path.join(here, "loteriaframes")

PAPER = (244, 236, 214)
INK = (22, 18, 16)
CW, CH = 360, 500            # carta
X0, Y0 = (S - CW) // 2, (S - CH) // 2
M = 14                       # margen de papel
NAME_H = 76                  # caja del nombre


def grain(size, seed, amt=7):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (size[1] // 3, size[0] // 3))
    n = np.asarray(Image.fromarray(((n * 0.5 + 2) * 60).clip(0, 255).astype(np.uint8)).resize(size, Image.BILINEAR), float)
    return (n - n.mean()) / 60 * amt


def outline(im, px=4, col=INK):
    """contorno de tinta alrededor de un recorte RGBA."""
    a = np.asarray(im.split()[-1]) > 40
    grown = ndimage.binary_dilation(a, iterations=px)
    base = Image.new("RGBA", im.size, col + (0,))
    base.putalpha(Image.fromarray((grown * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    base.alpha_composite(im)
    return base


def printed(im, levels=6):
    """pocos tonos, como litografía."""
    rgb, a = im.convert("RGB"), im.split()[-1]
    rgb = ImageOps.posterize(rgb.filter(ImageFilter.SMOOTH_MORE), 3)
    out = rgb.convert("RGBA"); out.putalpha(a)
    return out


def cut(path, black_bg=False):
    im = Image.open(os.path.join(here, path)).convert("RGBA")
    if black_bg:  # fondo negro pegado al borde -> transparente
        g = np.asarray(im.convert("L")) < 18
        lab, n = ndimage.label(g)
        sizes = ndimage.sum(g, lab, range(1, n + 1))
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        big = {i + 1 for i, v in enumerate(sizes) if v > 800}  # huecos negros grandes (entre cola y cuerpo)
        bg = np.isin(lab, list(edge | big))
        a = np.asarray(im.split()[-1]).copy(); a[bg] = 0
        im.putalpha(Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.6)))
    return im.crop(im.getbbox())


def moai():
    src = Image.open(os.path.join(here, "moai_big.jpg")).convert("L")
    mask = Image.open(os.path.join(here, "moai_mask.png")).convert("L")
    g = np.asarray(src).astype(float) / 255
    g = np.clip((g - 0.08) / 0.62, 0, 1) ** 1.1
    lum = Image.fromarray((g * 255).astype(np.uint8))
    im = Image.merge("RGBA", (lum, lum, lum, mask))
    return im.crop(im.getbbox())


def engraving(path, box=None):
    """grabado en papel -> tinta con alfa (lo claro se vuelve transparente)."""
    g = Image.open(os.path.join(here, path)).convert("L")
    if box:
        g = g.crop([int(v * s) for v, s in zip(box, (g.width, g.height, g.width, g.height))])
    a = np.asarray(ImageOps.autocontrast(g, cutoff=2), float) / 255
    a = np.clip((0.78 - a) / 0.5, 0, 1)
    im = Image.new("RGBA", g.size, INK + (0,))
    im.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return im


def card(num, name, subject, bg, fit=1.0, dy=0, flat=False, ink=4):
    c = Image.new("RGBA", (CW, CH), PAPER + (255,))
    d = ImageDraw.Draw(c)
    # ventana de la ilustración
    wx0, wy0, wx1, wy1 = M, M, CW - M, CH - M - NAME_H
    d.rectangle((wx0, wy0, wx1, wy1), fill=bg)
    ww, wh = wx1 - wx0, wy1 - wy0
    sub = subject if flat else outline(printed(subject), ink)
    sc = min((ww - 30) / sub.width, (wh - 44) / sub.height) * fit
    sub = sub.resize((int(sub.width * sc), int(sub.height * sc)), Image.LANCZOS)
    win = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    top = wh - sub.height - 8 if sub.height > sub.width * 0.9 else (wh - sub.height) // 2 + 14  # altos al piso, anchos al centro
    win.alpha_composite(sub, ((ww - sub.width) // 2, top + dy))
    c.alpha_composite(win, (wx0, wy0))
    # marcos de tinta
    d = ImageDraw.Draw(c)
    d.rectangle((wx0, wy0, wx1, wy1), outline=INK, width=5)
    d.rectangle((wx0, wy1, wx1, CH - M), outline=INK, width=5)
    # número arriba a la izquierda, en su cuadrito
    fn = ImageFont.truetype(RYE, 38)
    t = str(num)
    l, tt, r, b = fn.getbbox(t)
    bw, bh = r - l + 20, 50
    d.rectangle((wx0, wy0, wx0 + bw, wy0 + bh), fill=PAPER, outline=INK, width=5)
    d.text((wx0 + bw / 2 + 1, wy0 + bh / 2 + 2), t, font=fn, fill=INK, anchor="mm")
    # nombre
    size = 46
    while True:
        f = ImageFont.truetype(RYE, size)
        l, tt, r, b = f.getbbox(name)
        if r - l <= CW - 2 * M - 26 or size < 20:
            break
        size -= 1
    d.text((CW / 2, wy1 + (CH - M - wy1) / 2 + 3), name, font=f, fill=INK, anchor="mm")
    # papel viejito: grano + orilla un poco más oscura
    arr = np.asarray(c).astype(float)
    arr[..., :3] += grain((CW, CH), num)[..., None]
    yy, xx = np.mgrid[0:CH, 0:CW]
    e = np.minimum.reduce([xx, yy, CW - 1 - xx, CH - 1 - yy]).astype(float)
    arr[..., :3] *= (0.9 + 0.1 * np.clip(e / 18, 0, 1))[..., None]
    c = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), 14, outline=INK, width=3)
    m = Image.new("L", (CW, CH)); ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), 14, fill=255)
    c.putalpha(m)
    # sombra suave para que se lea sobre fondo oscuro y claro
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((X0 + 3, Y0 + 5, X0 + CW + 3, Y0 + CH + 5), 16, fill=(0, 0, 0, 110))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    out.alpha_composite(c, (X0, Y0))
    return out


CARDS = {
    "lot_moai": lambda: card(1, "EL MOAI", moai(), (86, 176, 170), fit=1.0),
    "lot_valiente": lambda: card(3, "EL VALIENTE", cut("kratos/cut/kratos_grito.png"), (214, 58, 44), fit=1.45),
    "lot_dama": lambda: card(4, "LA DAMA", cut("pp/MLP_The_Movie_Rarity_official_artwork.t.png"), (148, 98, 170)),
    "lot_muerte": lambda: card(14, "LA MUERTE", engraving("calacas/posada_catrina.jpg", (0.2, 0.0, 0.8, 0.97)), (236, 184, 60), flat=True, fit=1.0),
    "lot_casado": lambda: card(20, "EL CASADO", cut("kratos/cut/kratos_cadenas.png"), (60, 110, 180)),
    "lot_chismosa": lambda: card(27, "LA CHISMOSA", cut("pp/FANMADE_Pinkie_Pie_smiling.t.png"), (80, 170, 220)),
    "lot_crudo": lambda: card(33, "EL CRUDO", cut("kit/FANMADE_Applejack_is_not_amused_vector.png"), (110, 160, 70)),
    "lot_ya_voy": lambda: card(41, "EL YA VOY", cut("rd/FANMADE_Rainbow_Dash_flying.png"), (240, 140, 50)),
    "lot_dormilona": lambda: card(48, "LA DORMILONA", cut("kit/FANMADE_fluttershy_taking_a_nap.png", black_bg=True), (120, 80, 150), fit=1.3),
    "lot_mamona": lambda: card(52, "LA MAMONA", cut("m6/FANMADE_Twilight_Sparkle_reading_a_book_vector.png"), (236, 200, 70), fit=1.3),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, fn in CARDS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]:
            continue
        fn().save(os.path.join(OUT, k + ".png")); print(k)
