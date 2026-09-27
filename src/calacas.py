"""Calacas chidas: Santa Muerte, Posada, Posada y catrinas con frase blanca en negritas (fijos)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

S = 512
here = os.path.dirname(os.path.abspath(__file__))
ROBOTO = os.path.join(here, "fonts", "Roboto.ttf")
OUT = os.path.join(here, "calacaframes")
yy, xx = np.mgrid[0:S, 0:S] / S


def crop(path, box):
    im = Image.open(os.path.join(here, "calacas", path)).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = box[0] * W, box[1] * H, box[2] * W, box[3] * H
    side = min(x1 - x0, y1 - y0)  # cuadrado centrado en la caja
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return im.crop((int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2))).resize((S, S), Image.LANCZOS)


def vignette(im, k=0.75, c=(0.5, 0.42)):
    a = np.asarray(im).astype(float)
    r = np.sqrt((xx - c[0]) ** 2 + ((yy - c[1]) * 1.1) ** 2)
    a *= np.clip(1.15 - k * r ** 1.6 * 2.2, 0.15, 1.05)[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def grade(im, warm=(1.08, 0.94, 0.9), con=1.15, sat=1.1):
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(sat)).enhance(con)
    a = np.asarray(im).astype(float) * np.array(warm)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def photo(path, box, **kw):
    return vignette(grade(crop(path, box), **kw))


def posada(path, box, glow=(150, 20, 20), bone=(242, 232, 208), ink_col=(28, 6, 10)):
    """grabado en hueso y tinta oscura, orillas quemadas hacia el color de la vela."""
    g = ImageOps.autocontrast(crop(path, box).convert("L"), cutoff=1)
    ink = np.clip((0.78 - np.asarray(g, float) / 255) / 0.45, 0, 1)[..., None]
    r = np.sqrt((xx - 0.5) ** 2 + (yy - 0.42) ** 2)[..., None]
    paper = np.array(bone, float) * (1 - np.clip(r * 1.5 - 0.25, 0, 1)) + np.array(glow, float) * np.clip(r * 1.5 - 0.25, 0, 1)
    out = paper * (1 - ink) + np.array(ink_col, float) * ink
    return vignette(Image.fromarray(out.clip(0, 255).astype(np.uint8)), k=0.55)


def wrap(txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        cand = (cur + " " + w).strip()
        if f.getbbox(cand, stroke_width=4)[2] <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def caption(im, txt, cy=0.76, size=62, maxw=460):
    while True:
        f = ImageFont.truetype(ROBOTO, size); f.set_variation_by_name("Bold")
        lines = wrap(txt, f, maxw)
        if len(lines) <= 2 or size < 30:
            break
        size -= 2
    lh = int(size * 1.08)
    y0 = cy * S - lh * len(lines) / 2 + lh / 2
    # sombra suave y luego texto con contorno fino, como el de WhatsApp
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        ds.text((S / 2 + 2, y0 + i * lh + 4), ln, font=f, fill=(0, 0, 0, 200), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 200))
    im = im.convert("RGBA"); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((S / 2, y0 + i * lh), ln, font=f, fill="white", anchor="mm", stroke_width=3, stroke_fill=(20, 10, 10))
    return im


def finish(im):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, S - 2, S - 2), 34, outline=(25, 20, 20), width=5)
    m = Image.new("L", (S, S)); ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 36, fill=255)
    im.putalpha(m)
    return im


CALACAS = {
    "calaca_ya_alaverga_todo": lambda: caption(photo("santa_muerte_negra.jpg", (0.0, 0.08, 1.0, 1.0), warm=(1.1, 0.92, 0.86)), "Ya alaverga todo", cy=0.8),
    "calaca_bendiciones": lambda: caption(photo("santa_muerte_color.jpg", (0.0, 0.08, 1.0, 1.0)), "Bendiciones a todos menos a ti", cy=0.8),
    "calaca_muerto_bailando": lambda: caption(posada("posada_oaxaquena.jpg", (0.3, 0.1, 0.7, 0.9)), "Muerto pero bailando", cy=0.82),
    "calaca_me_cargo_el_payaso": lambda: caption(posada("posada_electrica.jpg", (0.02, 0.05, 0.5, 0.95), glow=(120, 30, 150)), "Ya me cargó el payaso", cy=0.8),
    "calaca_me_muero_de_risa": lambda: caption(photo("mariachi.jpg", (0.0, 0.0, 1.0, 0.7)), "Me muero de risa", cy=0.82),
    "calaca_ya_voy": lambda: caption(posada("posada_quijote.jpg", (0.14, 0.1, 0.86, 0.8), glow=(190, 60, 20)), "Ya voy en camino", cy=0.84),
    "calaca_catrina_pobre": lambda: caption(posada("posada_catrina.jpg", (0.15, 0.0, 0.85, 1.0), glow=(200, 90, 20)), "Muy catrina pero bien pobre", cy=0.82),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, fn in CALACAS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]:
            continue
        finish(fn()).save(os.path.join(OUT, k + ".png")); print(k)
