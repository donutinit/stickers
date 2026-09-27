"""Calacas chidas: Santa Muerte y la parca con frase en minúsculas, sin contorno, con daño de jpeg (fijos)."""
import io, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

S = 512
here = os.path.dirname(os.path.abspath(__file__))
ROBOTO = os.path.join(here, "fonts", "Roboto.ttf")
OUT = os.path.join(here, "calacaframes")


def square(path, cx=0.5, top=None, zoom=1.0):
    """cuadrado del lado corto (entre zoom), centrado en cx; top = orilla de arriba relativa."""
    im = Image.open(os.path.join(here, "calacas", path)).convert("RGB")
    W, H = im.size
    side = min(W, H) / zoom
    if side > min(W, H):  # zoom < 1: se aleja y rellena con negro (fondos oscuros)
        pad = Image.new("RGB", (max(W, int(side)), max(H, int(side))), (0, 0, 0))
        pad.paste(im, ((pad.width - W) // 2, 0))
        im, W, H = pad, pad.width, pad.height
    x = min(max(cx * W - side / 2, 0), W - side)
    y = (H - side) / 2 if top is None else min(top * H, H - side)
    return im.crop((int(x), int(y), int(x + side), int(y + side))).resize((S, S), Image.LANCZOS)


def wrap(txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        cand = (cur + " " + w).strip()
        if f.getbbox(cand)[2] <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def caption(im, txt, cy=0.8, size=58, maxw=450):
    txt = txt.lower()
    while True:
        f = ImageFont.truetype(ROBOTO, size); f.set_variation_by_name("Medium")
        lines = wrap(txt, f, maxw)
        if len(lines) <= 2 or size < 30:
            break
        size -= 2
    lh = int(size * 1.12)
    y0 = cy * S - lh * (len(lines) - 1) / 2
    # nada de contorno: solo una sombra difusa muy leve para que no se pierda
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        ds.text((S / 2 + 1, y0 + i * lh + 3), ln, font=f, fill=(0, 0, 0, 170), anchor="mm")
    im = im.convert("RGBA"); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((S / 2, y0 + i * lh), ln, font=f, fill="white", anchor="mm")
    return im.convert("RGB")


def crunch(im, passes=((0.62, 14), (0.85, 22), (1.0, 30))):
    """daño de jpeg de meme reenviado mil veces: bloques, halos y color sangrado."""
    im = ImageEnhance.Sharpness(im).enhance(1.8)
    for sc, q in passes:
        small = im.resize((int(S * sc), int(S * sc)), Image.BILINEAR)
        buf = io.BytesIO(); small.save(buf, "JPEG", quality=q, subsampling=2); buf.seek(0)
        im = Image.open(buf).convert("RGB").resize((S, S), Image.BICUBIC)
    return im


def finish(im):
    im = im.convert("RGBA")
    m = Image.new("L", (S, S)); ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 36, fill=255)
    im.putalpha(m)
    return im


CALACAS = {
    "calaca_ya_alaverga_todo": lambda: caption(square("trono_rayos.jpg"), "Ya alaverga todo", cy=0.8),
    "calaca_bendiciones": lambda: caption(square("corona_roja.jpg"), "Bendiciones a todos menos a ti", cy=0.8),
    "calaca_me_cargo_el_payaso": lambda: caption(square("dedo_game_over.jpg", top=0.0), "Ya me cargó el payaso", cy=0.86),
    "calaca_no_me_busquen": lambda: caption(square("rosas_halo.jpg", top=0.06), "No me busquen", cy=0.84),
    "calaca_me_muero_de_risa": lambda: caption(square("calavera_dorada.jpg", top=0.1, zoom=0.56), "Me muero de risa", cy=0.87),
    "calaca_ya_voy": lambda: caption(square("reina_orbe.jpg", top=0.04), "Ya voy en camino", cy=0.84),
    "calaca_respeten_a_la_jefa": lambda: caption(square("roja_blanca.jpg", top=0.24), "Respeten a la jefa", cy=0.91),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    for k, fn in CALACAS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]:
            continue
        finish(crunch(fn())).save(os.path.join(OUT, k + ".png")); print(k)
