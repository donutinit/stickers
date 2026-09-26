"""'Gracias a Dios' tía cards for every pony + 'Que sea la voluntad de Dios' in every style."""
import math, os, random, sys
from PIL import Image, ImageDraw
import m6, tias, arte, blackmetal, buchon, kratos, minimal
import moai_common as mc
from tias import GOLD, RAINBOW, BLUE, bokeh, rays, floaters, fluttering

S = 512
here = os.path.dirname(os.path.abspath(__file__))
FRASE = "Que sea la voluntad de Dios"


def save_anim(name, frames, delays):
    d = os.path.join(here, "volframes", name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"f{i:02d}.png"))
    open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))


def save_still(name, im):
    os.makedirs(os.path.join(here, "volframes"), exist_ok=True)
    im.save(os.path.join(here, "volframes", name + ".png"))


def tia(out, pony, fit, pos, face, bg, texts, seed, corners, extra_front=()):
    im = Image.open(os.path.join(here, "pp", pony + ".t.png"))
    sc = fit[1] / (im.height if fit[0] == "h" else im.width)
    face_cx = pos[0] + (face[0] + face[2]) / 2 * im.width * sc
    # 🙏 goes in the top corner away from the face
    corners = [(c, sz, ((430, 24) if face_cx < 256 else (8, 24)) if c == "1f64f" else xy, r) for c, sz, xy, r in corners]
    cfg = dict(out=out, seed=seed, pony=pony, fit=fit, pos=pos, face=face, bg=bg, radial=True,
               decorate_bg=lambda b: (rays(b, (255, 240, 180), alpha=70, center=(256, 90)), bokeh(b, [(255, 255, 255), (255, 220, 170)], 20, seed)),
               behind=[], corners=corners,
               front=[floaters(["1f496", "2728"], 5, seed, y0=460, y1=260), *extra_front],
               texts=texts)
    frames, _ = tias.build(cfg)
    return frames, [110] * len(frames)


# ---------------------------------------------------------------- Gracias a Dios, tía style, every pony
GD = {
    "tia_gd_pinkie": ("MLP_The_Movie_Pinkie_Pie_official_artwork", ("h", 470), (40, 20), (0.10, 0.17, 0.55, 0.47),
                      ((255, 235, 245), (255, 190, 220)), [("Gracias a Dios", 80, GOLD, 296), ("¡Bendiciones!", 72, RAINBOW, 376)]),
    "tia_gd_applejack": ("MLP_The_Movie_Applejack_official_artwork_2", ("h", 460), (110, 14), (0.22, 0.10, 0.68, 0.40),
                         ((255, 245, 215), (255, 200, 160)), [("Gracias a Dios", 80, GOLD, 296), ("por Todo", 84, RAINBOW, 376)]),
    "tia_gd_twilight": ("MLP_The_Movie_Twilight_Sparkle_official_artwork_2", ("h", 460), (118, 10), (0.28, 0.20, 0.72, 0.42),
                        ((245, 235, 255), (210, 190, 255)), [("Gracias a Dios", 80, GOLD, 296), ("Amén", 92, RAINBOW, 376)]),
    "tia_gd_rarity": ("MLP_The_Movie_Rarity_official_artwork", ("h", 440), (40, 14), (0.18, 0.10, 0.55, 0.36),
                      ((250, 240, 255), (230, 200, 255)), [("Gracias a Dios", 80, GOLD, 296), ("Bendiciones", 76, RAINBOW, 376)]),
    "tia_gd_dash": ("FANMADE_Rainbow_Dash_standing_vector", ("h", 460), (120, 10), (0.25, 0.06, 0.65, 0.38),
                    ((225, 245, 255), (190, 225, 255)), [("Gracias a Dios", 80, GOLD, 296), ("Siempre", 88, BLUE, 376)]),
}
CORNERS = [("1f64f", 80, (8, 30), 0), ("1f339", 90, (-8, 408), -15), ("1f490", 96, (418, 404), 12), ("1f338", 64, (446, 170), -10)]


# ---------------------------------------------------------------- Que sea la voluntad de Dios, every style
def v_fijo():
    tw = m6.load("m6/MLP_The_Movie_Twilight_Sparkle_official_artwork_2.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(tw, ((S - tw.width) // 2, 0))
    m6.meme_block(fr, FRASE.upper(), 506, top=False, size=72, max_lines=2)
    return fr


def v_arte():
    return arte.piece("dore_paraiso_perdido.jpg", FRASE, "Gustave Doré · 1866 · El paraíso perdido", "print", (0, 0.05, 1, 0.85))


def v_minimal():
    return minimal.card(19, "que sea la voluntad de dios.", "loc. — juntos hacemos nuestra parte", minimal.BLACK, minimal.PAPER, minimal.YELLOW)


def v_blackmetal():
    return blackmetal.grim("iglesia.jpg", (0, 0.1, 1, 0.85), False, 1.8, 1.0, [("1f64f", 390, 400, 96)], "que sea la voluntad de dios", seed=19)


def v_moai_fijo():
    fr = mc.moai_card(1.15, 0.52, 0.42)
    m6.meme_block(fr, FRASE.upper(), 500, top=False, size=62, max_lines=2)
    return fr


def v_pony_anim():
    tw = m6.load("m6/MLP_The_Movie_Twilight_Sparkle_official_artwork_2.png", h=380)
    rnd = random.Random(9)
    frames = []
    for i in range(12):
        t = i / 12
        fr = Image.new("RGBA", (S, S))
        m6.rays(fr, t * 30, [(255, 230, 120), (255, 255, 230)], alpha=170, n=16, c=(256, 150))
        glow = Image.new("RGBA", (S, S)); ImageDraw.Draw(glow).ellipse([100, -40, 412, 280], fill=(255, 255, 220, 120))
        fr.alpha_composite(glow)
        bob = int(6 * math.sin(2 * math.pi * t))
        fr.alpha_composite(tw, ((S - tw.width) // 2, 8 + bob))
        d = ImageDraw.Draw(fr)
        for k in range(6):
            s = max(0, math.sin(2 * math.pi * (t * 2 + k / 6)))
            m6.sparkle(d, [60, 450, 40, 470, 90, 420][k], [60, 80, 200, 220, 320, 330][k], 16 * s, int(255 * s), (255, 240, 170))
        m6.meme_block(fr, FRASE.upper(), 506, top=False, size=70, max_lines=2)
        frames.append(fr)
    return frames, [100] * 12


def v_tia():
    return tia("v_tia", "MLP_The_Movie_Rarity_official_artwork", ("h", 430), (40, 10), (0.18, 0.10, 0.55, 0.36),
               ((255, 248, 225), (255, 210, 180)), [("Que sea la Voluntad", 70, GOLD, 300), ("de Dios", 90, RAINBOW, 374)], 21, CORNERS,
               [fluttering("1f98b", 50, (410, 90))])


def v_buchon():
    aj = m6.load("m6/MLP_The_Movie_Applejack_official_artwork.png", h=300)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 50, [(212, 165, 50), (50, 38, 10)], alpha=90, n=18, c=(256, 230))
        else:
            fr.alpha_composite(m6.emoji("1f64f", 84), (22, 300))
    return buchon.base_frames(aj, ((S - aj.width) // 2, 92), ((250, 215), 55, 30, 0.35, math.pi - 0.35),
                              [("Que sea la Voluntad", 70, 10), ("de Dios", 90, 408)], extras, seed=8, face=(170, 110, 340, 220))


def v_kratos():
    return kratos.cute(kratos.head("kratos_serio.png", (0, 0, 1, 1), 290), [("Que sea la voluntad", 70, kratos.GOLD, -92), ("de Dios", 100, kratos.LILAC, -4)],
                       None, [("1f64f", 90, (410, 150), 0), ("2728", 64, (30, 40), 0)], seed=23)


def v_moai_anim():
    import moai  # regenerates moaiframes (gigachad push-in + vine boom)
    src = os.path.join(here, "moaiframes")
    names = sorted(f for f in os.listdir(src) if f.endswith(".png"))
    frames = []
    for n in names:
        fr = Image.open(os.path.join(src, n)).convert("RGBA")
        m6.meme_block(fr, FRASE.upper(), 500, top=False, size=62, max_lines=2)
        frames.append(fr)
    return frames, list(map(int, open(os.path.join(src, "delays.txt")).read().split()))


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for name, (pony, fit, pos, face, bg, texts) in GD.items():
        if not want or name in want:
            save_anim(name, *tia(name, pony, fit, pos, face, bg, texts, len(name), CORNERS)); print(name)
    for name in ("v_fijo", "v_arte", "v_minimal", "v_blackmetal", "v_moai_fijo"):
        if not want or name in want:
            save_still(name, globals()[name]()); print(name)
    for name in ("v_pony_anim", "v_tia", "v_buchon", "v_kratos", "v_moai_anim"):
        if not want or name in want:
            save_anim(name, *globals()[name]()); print(name)
