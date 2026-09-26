"""'Te valgo verga' in every style."""
import math, os, random, sys
from PIL import Image, ImageDraw
import m6, arte, blackmetal, buchon, kratos, minimal
import moai_common as mc
from tias import GOLD, RAINBOW, BLUE, fluttering
from voluntad import save_anim, save_still, tia, CORNERS

S = 512
FRASE = "te valgo verga"
here = os.path.dirname(os.path.abspath(__file__))


def fijo():
    ra = m6.load("kit/FANMADE_Rarity_not_amused.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(ra, ((S - ra.width) // 2, 0))
    m6.meme_text(fr, "TE VALGO VERGA", size=96, y=450)
    return fr


def arte_():
    return arte.piece("../bm/goya_sopa.jpg", "Te valgo verga", "Francisco de Goya · 1819–1823", "gold", (0.05, 0, 0.72, 1))


def minimal_():
    return minimal.card(20, "te valgo verga.", "loc. — autoestima en números rojos", minimal.YELLOW, minimal.BLACK, minimal.RED)


def blackmetal_():
    return blackmetal.grim("nokken.jpg", (0.22, 0, 0.88, 1), False, 2.2, 1.0, [("1f97a", 396, 14, 96)], FRASE, seed=20, logo_y=-4)


def moai_fijo():
    fr = mc.moai_card(1.15, 0.52, 0.42)
    m6.meme_text(fr, "TE VALGO VERGA", size=96, y=450)
    return fr


def pony_anim():
    """sad Fluttershy in the rain."""
    fl = m6.load("m6/FANMADE_Fluttershy_being_cute.png", w=480)
    rnd = random.Random(20)
    drops = [(rnd.randint(0, S), rnd.random(), rnd.randint(14, 26)) for _ in range(45)]
    frames = []
    for i in range(12):
        t = i / 12
        fr = Image.new("RGBA", (S, S))
        fr.alpha_composite(fl, ((S - fl.width) // 2, 110))
        d = ImageDraw.Draw(fr)
        for x, ph, L in drops:
            y = ((ph + t) % 1) * (S + 40) - 20
            d.line([(x, y), (x - 3, y + L)], fill=(120, 170, 230, 255), width=3)
        fr.alpha_composite(m6.emoji("2601", 130), (20, -10)); fr.alpha_composite(m6.emoji("2601", 110), (370, 0))
        m6.meme_text(fr, "TE VALGO VERGA", size=96, y=452)
        frames.append(fr)
    return frames, [90] * 12


def tia_():
    return tia("valgo_tia", "FANMADE_Fluttershy_Idle_Vector", ("h", 460), (40, 14), (0.06, 0.13, 0.42, 0.40),
               ((255, 240, 250), (230, 200, 240)), [("Ya sé que", 74, GOLD, 286), ("te valgo verga", 70, RAINBOW, 372)], 24, CORNERS,
               [fluttering("1f98b", 50, (400, 90))])


def buchon_():
    rd = m6.load("rd/FANMADE_Rainbow_Dash_chillin.png", h=360)
    def extras(fr, t, layer):
        if layer == "behind":
            m6.rays(fr, t * 50, [(212, 165, 50), (50, 38, 10)], alpha=90, n=18, c=(256, 230))
    return buchon.base_frames(rd, ((S - rd.width) // 2, 70), ((256, 280), 90, 38, 0.2, math.pi - 0.2),
                              [("Ya sé que", 86, 10), ("te valgo verga", 84, 408)], extras, seed=20, face=(150, 60, 400, 230))


def kratos_():
    return kratos.cute(kratos.head("kratos_enojado.png", (0, 0, 1, 1), 330), [("Te valgo verga", 100, kratos.PINK, -4)],
                       (0.62, 110, 12), [("1f97a", 96, (406, 230), 0)], seed=25)


def moai_anim():
    import moai  # regenerates moaiframes
    src = os.path.join(here, "moaiframes")
    frames = []
    for n in sorted(f for f in os.listdir(src) if f.endswith(".png")):
        fr = Image.open(os.path.join(src, n)).convert("RGBA")
        m6.meme_text(fr, "TE VALGO VERGA", size=96, y=450)
        frames.append(fr)
    return frames, list(map(int, open(os.path.join(src, "delays.txt")).read().split()))


STILLS = ("fijo", "arte_", "minimal_", "blackmetal_", "moai_fijo")
ANIMS = ("pony_anim", "tia_", "buchon_", "kratos_", "moai_anim")

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for n in STILLS:
        if not want or n in want:
            save_still("valgo_" + n.rstrip("_"), globals()[n]()); print(n)
    for n in ANIMS:
        if not want or n in want:
            save_anim("valgo_" + n.rstrip("_"), *globals()[n]()); print(n)
