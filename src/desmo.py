"""Desmotivaciones: foto con filo blanco sobre negro, texto en la foto y título + subtítulo abajo (fijos)."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

S = 512
here = os.path.dirname(os.path.abspath(__file__))
ROBOTO = os.path.join(here, "fonts", "Roboto.ttf")
TINOS = os.path.join(here, "fonts", "Tinos.ttf")
OUT = os.path.join(here, "desmoframes")
PX0, PY0, PX1, PY1 = 38, 22, S - 38, 362   # foto


def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        f.set_variation_by_name(var)
    return f


def fit(path, txt, size, maxw, var=None, sw=0):
    while size > 12:
        f = font(path, size, var)
        l, t, r, b = f.getbbox(txt, stroke_width=sw)
        if r - l <= maxw:
            return f
        size -= 1
    return f


def cover(path, w, h, focus=(0.5, 0.5), zoom=1.0):
    im = Image.open(os.path.join(here, path)).convert("RGB")
    sc = max(w / im.width, h / im.height) * zoom
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x = int((im.width - w) * focus[0]); y = int((im.height - h) * focus[1])
    return im.crop((x, y, x + w, y + h))


def contain(path, w, h, dx=0):
    """foto vertical completa sobre la misma foto desenfocada."""
    bg = cover(path, w, h).filter(ImageFilter.GaussianBlur(14))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    im = Image.open(os.path.join(here, path)).convert("RGB")
    im = im.crop((0, int(im.height * 0.06), im.width, int(im.height * 0.86)))  # sin la base
    hh = int(h * 0.8)
    im = im.resize((round(im.width * hh / im.height), hh), Image.LANCZOS)
    bg.paste(im, ((w - im.width) // 2 + dx, 0))
    return bg


def poster(photo, overlay, title, sub, focus=(0.5, 0.5), zoom=1.0, oy=0.80, full=False):
    fr = Image.new("RGB", (S, S), (0, 0, 0))
    w, h = PX1 - PX0, PY1 - PY0
    ph = contain(photo, w, h, 60) if full else cover(photo, w, h, focus, zoom)
    ph = ImageEnhance.Contrast(ph).enhance(1.05)
    # texto encima de la foto, estilo meme de celular: blanco, negritas, contorno negro
    d = ImageDraw.Draw(ph)
    f = fit(ROBOTO, overlay, 70, w - 30, "Bold", 5)
    d.text((w / 2, h * oy), overlay, font=f, fill="white", stroke_width=5, stroke_fill="black", anchor="mm")
    fr.paste(ph, (PX0, PY0))
    d = ImageDraw.Draw(fr)
    d.rectangle((PX0 - 5, PY0 - 5, PX1 + 4, PY1 + 4), outline="white", width=2)
    # título y subtítulo
    f = fit(TINOS, title, 60, S - 40)
    d.text((S / 2, 418), title, font=f, fill="white", anchor="mm")
    f = fit(TINOS, sub, 26, S - 50)
    d.text((S / 2, 470), sub, font=f, fill=(235, 235, 235), anchor="mm")
    return fr


POSTERS = {
    "desmo_ok_punetas": lambda: poster("desmo/soldado.jpg", "Ok puñetas", "Ok puñetas", "Ok puñetas", focus=(0.62, 0.3), zoom=1.25),
    "desmo_que_pedo": lambda: poster("desmo/tlacuache.jpg", "Qué pedo", "Qué pedo", "no sé pero ya me enojé", focus=(0.75, 0.2), zoom=1.1, oy=0.15),
    "desmo_ni_madres": lambda: poster("desmo/gato.jpg", "Ni madres", "Ni madres", "ni aunque me paguen. Bueno, ¿cuánto?", focus=(0.3, 0.4)),
    "desmo_te_estoy_viendo": lambda: poster("desmo/chihuahua.jpg", "Te estoy viendo", "Te estoy viendo", "y no me gusta lo que veo", focus=(0.3, 0.45), zoom=1.3),
    "desmo_si_jalo": lambda: poster("kratos/kratos_serio.jpg", "Sí jalo", "Sí jalo", "nomás no me digan a qué hora", focus=(0.5, 0.3), oy=0.87),
    "desmo_ahorita_voy": lambda: poster("moai_big.jpg", "Ahorita voy", "Ahorita voy", "dijo, y nunca fue", full=True, oy=0.9),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, fn in POSTERS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]:
            continue
        fn().save(os.path.join(OUT, k + ".png")); print(k)
