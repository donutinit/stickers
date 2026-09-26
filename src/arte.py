"""Museum pieces: Goya / Doré in a frame with a gallery plaque carrying a very Mexican title."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 512
here = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(here, "fonts", n)


def font(name, size, weight=None):
    f = ImageFont.truetype(F(name), size)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def gold_frame(w, h, t=30):
    """baroque-ish gilt frame: dark rim, bevelled gold band, bead line, inner lip."""
    fr = Image.new("RGBA", (w, h))
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # distance to the outer edge -> position across the moulding (0 outer .. 1 inner)
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / t
    band = (d < 1)
    # light from top-left: top/left sides brighter
    side = np.where(np.minimum(xx, yy) < np.minimum(w - 1 - xx, h - 1 - yy), 1.0, 0.55)
    profile = 0.55 + 0.45 * np.sin(np.clip(d, 0, 1) * np.pi * 1.6)  # rounded moulding
    lum = np.clip(profile * side, 0, 1.1)
    base = np.array([196, 150, 62.])
    hi = np.array([255, 232, 160.])
    rgb = base * lum[..., None] + (hi - base) * np.clip(lum - 0.8, 0, 1)[..., None] * 2
    rgb[(d < 0.08)] = [70, 45, 12]   # dark outer rim
    rgb[(d > 0.9) & band] = [90, 60, 20]  # inner lip shadow
    a = (band * 255).astype(np.uint8)
    fr = Image.fromarray(np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), a]), "RGBA")
    dr = ImageDraw.Draw(fr)
    # bead line
    r = 2
    inset = int(t * 0.55)
    for x in range(inset, w - inset, 7):
        for y in (inset, h - 1 - inset):
            dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 238, 180, 255))
    for y in range(inset, h - inset, 7):
        for x in (inset, w - 1 - inset):
            dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 238, 180, 255))
    return fr


def print_frame(w, h, t=9, mat=20):
    """thin black frame with a white mat, for engravings."""
    fr = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(fr)
    d.rectangle([0, 0, w - 1, h - 1], fill=(22, 20, 20, 255))
    d.rectangle([t, t, w - 1 - t, h - 1 - t], fill=(246, 243, 236, 255))
    d.rectangle([t + mat - 2, t + mat - 2, w - t - mat + 1, h - t - mat + 1], outline=(200, 195, 185, 255), width=2)
    return fr, t + mat


def plaque(title, meta, style):
    """museum label: title + small meta line, brass (gold) or white card (print)."""
    if style == "gold":
        tf = font("EBGaramond-Italic.ttf", 44, 600)
        col, meta_col = (40, 26, 8), (70, 50, 20)
    else:
        tf = font("UnifrakturMaguntia.ttf", 44)
        col, meta_col = (20, 18, 18), (80, 76, 70)
    mf = font("EBGaramond.ttf", 17, 500)
    while tf.getlength(title) > 440:
        tf = tf.font_variant(size=tf.size - 2)
    tw = max(tf.getlength(title), mf.getlength(meta)) + 44
    th = 96
    w = int(min(480, tw))
    im = Image.new("RGBA", (w, th))
    d = ImageDraw.Draw(im)
    if style == "gold":
        g = np.linspace(0, 1, th)[:, None]
        rgb = np.array([236, 205, 130.]) * (1 - g) + np.array([190, 150, 70.]) * g
        card = Image.fromarray(np.repeat(rgb[:, None, :], w, 1).squeeze().astype(np.uint8).reshape(th, w, 3), "RGB").convert("RGBA")
        m = Image.new("L", (w, th)); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, th - 1], 8, fill=255)
        im.paste(card, (0, 0), m)
        d.rounded_rectangle([4, 4, w - 5, th - 5], 6, outline=(120, 85, 30, 255), width=2)
        for x, y in ((12, 12), (w - 13, 12), (12, th - 13), (w - 13, th - 13)):  # screws
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(150, 110, 45, 255))
    else:
        d.rectangle([0, 0, w - 1, th - 1], fill=(250, 248, 243, 255), outline=(30, 28, 28, 255), width=2)
    d.text((w / 2, 40), title, font=tf, fill=col, anchor="mm")
    d.text((w / 2, 78), meta, font=mf, fill=meta_col, anchor="mm")
    return im


def shadow(im, off=(0, 6), blur=8, alpha=120):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda a: a * alpha // 255))
    pad = blur * 3
    big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad))
    big.alpha_composite(sh, (pad, pad))
    return big.filter(ImageFilter.GaussianBlur(blur)), pad


def piece(img, title, meta, style, crop=None):
    art = Image.open(os.path.join(here, "arte", img)).convert("RGB")
    if crop:
        W, H = art.size
        art = art.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
    box_w, box_h = 480, 402  # room for frame + art above the plaque
    if style == "gold":
        t = 30
        inner = (box_w - 2 * t, box_h - 2 * t)
    else:
        t = 9 + 20
        inner = (box_w - 2 * t, box_h - 2 * t)
    sc = min(inner[0] / art.width, inner[1] / art.height)
    art = art.resize((int(art.width * sc), int(art.height * sc)), Image.LANCZOS)
    fw, fh = art.width + 2 * t, art.height + 2 * t
    if style == "gold":
        frame = gold_frame(fw, fh, t)
    else:
        frame, _ = print_frame(fw, fh)
    frame.paste(art, (t, t))

    out = Image.new("RGBA", (S, S))
    fx, fy = (S - fw) // 2, 4 + (box_h - fh) // 2
    sh, pad = shadow(frame)
    out.alpha_composite(sh, (fx - pad, fy - pad + 6))
    out.alpha_composite(frame, (fx, fy))
    pl = plaque(title, meta, style)
    py = S - pl.height - 2
    sh, pad = shadow(pl, blur=5, alpha=110)
    out.alpha_composite(sh, ((S - pl.width) // 2 - pad, py - pad + 4))
    out.alpha_composite(pl, ((S - pl.width) // 2, py))
    return out


PIECES = [
    ("arte_saturno", "goya_saturno.jpg", "Me lo como a besos", "Francisco de Goya · 1819–1823 · Óleo sobre revoco", "gold", (0, 0.02, 1, 0.9)),
    ("arte_aquelarre", "goya_aquelarre.jpg", "Cuando llego con el chisme", "Francisco de Goya · 1797–1798 · Óleo sobre lienzo", "gold", (0, 0.2, 1, 0.9)),
    ("arte_satan", "dore_satan.jpg", "Me vale verga", "Gustave Doré · 1866 · El paraíso perdido", "print", None),
    ("arte_satan_no", "dore_satan_despair.jpg", "No autorizo", "Gustave Doré · 1866 · El paraíso perdido", "print", None),
    ("arte_estigia", "dore_estigia.jpg", "Ya voy", "Gustave Doré · 1861 · Inferno, canto VIII", "print", None),
    ("arte_bosque", "dore_bosque.jpg", "¿Y este wey quién es?", "Gustave Doré · 1861 · Inferno, canto I", "print", None),
    ("arte_cuervo", "dore_cuervo.jpg", "Nel.", "Gustave Doré · 1884 · The Raven", "print", (0, 0.05, 1, 0.8)),
    ("arte_leviatan", "dore_leviatan.jpg", "Me turbo vale pito", "Gustave Doré · 1866 · La Biblia", "print", None),
]

if __name__ == "__main__":
    out = os.path.join(here, "artframes"); os.makedirs(out, exist_ok=True)
    for name, img, title, meta, style, crop in PIECES:
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        piece(img, title, meta, style, crop).save(os.path.join(out, name + ".png"))
        print(name)
