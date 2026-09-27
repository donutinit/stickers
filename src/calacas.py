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


def caption(im, txt, cy=0.8, size=58, maxw=450, max_lines=2, halo=False):
    txt = txt.lower()
    while True:
        f = ImageFont.truetype(ROBOTO, size); f.set_variation_by_name("Medium")
        lines = wrap(txt, f, maxw)
        if len(lines) <= max_lines or size < 30:
            break
        size -= 2
    lh = int(size * 1.12)
    y0 = cy * S - lh * (len(lines) - 1) / 2
    # nada de contorno: solo una sombra difusa muy leve para que no se pierda
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        ds.text((S / 2 + 1, y0 + i * lh + 3), ln, font=f, fill=(0, 0, 0, 170), anchor="mm")
    im = im.convert("RGBA")
    if halo:  # fondo ruidoso: sombra ancha y difusa detrás de todo el renglón (sigue sin contorno)
        hl = Image.new("RGBA", (S, S), (0, 0, 0, 0)); dh = ImageDraw.Draw(hl)
        for i, ln in enumerate(lines):
            dh.text((S / 2, y0 + i * lh + 2), ln, font=f, fill=(0, 0, 0, 150), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0, 150))
        im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
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
    # romanticones
    "calaca_t_amo_mailob": lambda: caption(square("corazon_manos.jpg", top=0.1), "t amo mailob", cy=0.88, halo=True),
    "calaca_te_kiero": lambda: caption(square("abrazo_rosas.jpg", top=0.0), "te kiero", cy=0.87, halo=True),
    "calaca_m_gustas_un_vergo": lambda: caption(square("ojos_corazon.jpg", top=0.0, zoom=0.8), "m gustas un vergo", cy=0.86),
    "calaca_me_engruesas": lambda: caption(square("flor_ofrenda.jpg", top=1.0, zoom=0.74), "me engruesas tanto la verga que si la mando a la escuela le hacen bullyng por gorda", cy=0.23, size=46, maxw=460, max_lines=5),
    "calaca_me_traes_bien_muerto": lambda: caption(square("catrines.jpg"), "me traes bien muerto", cy=0.87, halo=True),
    "calaca_hasta_los_huesos": lambda: caption(square("luna_pareja.jpg"), "te amo hasta los huesos", cy=0.87),
    "calaca_rigor_mortis": lambda: caption(square("rey_beso.jpg", top=0.0, zoom=0.72), "me pones más tieso que el rigor mortis", cy=0.89, halo=True),
    "calaca_me_muero_otra_vez": lambda: caption(square("corazon_espada.jpg"), "si me dejas me muero otra vez", cy=0.86),
    "calaca_tuetano": lambda: caption(square("corazon_pecho.jpg", top=0.04), "te extraño hasta el tuétano", cy=0.87, halo=True),
    "calaca_te_doy_mi_hueso": lambda: caption(square("beso_teal.jpg", top=0.0), "te voy a dar mi hueso", cy=0.13, halo=True),
    "calaca_amor_de_mi_muerte": lambda: caption(square("beso_rayos.jpg"), "eres el amor de mi muerte", cy=0.87, halo=True),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) == 1:  # todo de nuevo: fuera los viejos
        for f in os.listdir(OUT):
            os.remove(os.path.join(OUT, f))
    for k, fn in CALACAS.items():
        if len(sys.argv) > 1 and k not in sys.argv[1:]:
            continue
        finish(crunch(fn())).save(os.path.join(OUT, k + ".png")); print(k)
