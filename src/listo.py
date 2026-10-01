"""Pinkie Pie: 'listo', 'enterado' y 'gracias' en fijo (meme), animado y tía."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont
import m6
from tias import GOLD, RAINBOW, fluttering
from voluntad import tia

S = 512
here = os.path.dirname(os.path.abspath(__file__))
CONFETTI = [(255, 80, 160), (255, 210, 40), (80, 200, 255), (140, 230, 90), (190, 120, 255)]
HEARTS = ["1f496", "1f495", "1f497"]


def save_anim(name, frames, delays):
    d = os.path.join(here, "listoframes", name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"f{i:02d}.png"))
    open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))


def save_still(name, im):
    os.makedirs(os.path.join(here, "listoframes"), exist_ok=True)
    im.save(os.path.join(here, "listoframes", name + ".png"))


def pony(name, w):
    return m6.load(f"pp/{name}.t.png", w=w)


# ======================================================================= fijos (meme)
def listo_fijo():
    p = pony("FANMADE_Pinkie_Pie_celebrating_with_arms_up", 560)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(p, (S - p.width, S - p.height))  # the cut neck ends under the text
    m6.meme_text(fr, "¡LISTO!", size=112, y=440)
    return fr


def enterado_fijo():
    p = pony("FANMADE_Pinkie_glasses_by_j_brony", 500)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(p, ((S - p.width) // 2, 0))
    m6.meme_text(fr, "ENTERADO", size=120, y=454)
    return fr


def hug(fr, scale=1.0):
    """Pinkie hugging the screen: arms run off both edges, body off the bottom."""
    p = pony("FANMADE_Pinkie_hugging_screen", int(640 * scale))
    fr.alpha_composite(p, (int(S / 2 - 0.515 * p.width), S - p.height + int(8 * (scale - 1) * 10)))


def gracias_fijo():
    fr = Image.new("RGBA", (S, S))
    for code, xy, sz in (("1f496", (14, 150), 70), ("1f495", (96, 118), 50), ("1f497", (400, 112), 56)):
        fr.alpha_composite(m6.emoji(code, sz), xy)
    hug(fr)
    m6.meme_text(fr, "¡GRACIAS!", size=120, y=60)
    return fr


# ======================================================================= animados
def text_check(fr, txt, y, size, pop):
    """Impact text with a ✅ to its right, centered together."""
    f = m6.fit_font(m6.IMPACT, txt, size, 400, 8)
    l, t, r, b = f.getbbox(txt, stroke_width=8)
    ck = m6.emoji("2705", int(84 * pop))
    gap, tw = 10, r - l
    x0 = (S - (tw + gap + 84)) / 2
    ImageDraw.Draw(fr).text((x0 + tw / 2, y), txt, font=f, fill="white", stroke_width=8, stroke_fill="black", anchor="mm")
    fr.alpha_composite(ck, (int(x0 + tw + gap + 42 - ck.width / 2), int(y - ck.height / 2)))


def listo_anim():
    """dancing Pinkie rocks side to side under falling confetti."""
    p = pony("FANMADE_Pinkie_Pie_dancing", 425)
    pad = Image.new("RGBA", (S, 400))  # room to rock without clipping
    px, py = (S - p.width) // 2, 400 - p.height
    pad.alpha_composite(p, (px, py))
    pivot = (px + p.width * 0.56, 400)
    rnd = random.Random(30)
    bits = [(rnd.randint(0, S), rnd.random(), rnd.choice(CONFETTI), rnd.uniform(-1, 1)) for _ in range(44)]
    N = 12
    frames = []
    for i in range(N):
        t = i / N
        fr = Image.new("RGBA", (S, S))
        d = ImageDraw.Draw(fr)
        for x, ph, col, spin in bits:  # behind her, so nothing lands on her face
            yy = ((ph + t) % 1) * 420 - 20
            xx = x + 14 * math.sin(yy / 40 + ph * 6)
            a = math.radians((yy * 3 * spin) % 360)
            dx, dy = 10 * math.cos(a), 6
            d.polygon([(xx - dx, yy - dy), (xx + dx, yy - dy), (xx + dx, yy + dy), (xx - dx, yy + dy)], fill=col + (255,))
        hop = abs(math.sin(2 * math.pi * t))
        q = pad.rotate(6 * math.sin(2 * math.pi * t), center=pivot, resample=Image.BICUBIC)
        fr.alpha_composite(q, (0, int(-8 * hop)))
        text_check(fr, "¡LISTO!", 440, 112, 1 + 0.16 * hop)
        frames.append(fr)
    return frames, [85] * N


def enterado_anim():
    """salute snap: she dips, springs up, and the text punches with her."""
    p = pony("FANMADE_Pinkie_glasses_by_j_brony", 500)
    #       dy, text scale, star size, ms
    seq = [(0, 1.0, 0, 110), (6, 1.0, 0, 60), (16, 1.0, 0, 60), (3, 1.0, 0, 50),
           (-10, 1.1, 1.0, 60), (-5, 1.06, 0.85, 60), (-1, 1.02, 0.7, 70), (0, 1.0, 0.55, 90)] \
        + [(b, 1.0, s, 120) for b, s in ((1, .4), (2, .25), (1, .1), (0, 0), (-1, 0), (-2, 0), (-1, 0))]
    stars = [(44, 60, 30), (474, 52, 26), (30, 150, 16), (492, 132, 14)]  # top corners, clear of her face
    frames, delays = [], []
    for dy, sc, st, ms in seq:
        fr = Image.new("RGBA", (S, S))
        fr.alpha_composite(p, ((S - p.width) // 2, 12 + dy))
        d = ImageDraw.Draw(fr)
        for x, y, r in stars:
            if st:
                m6.sparkle(d, x, y, r * st + 5, 255, (0, 0, 0))
                m6.sparkle(d, x, y, r * st, 255, (255, 225, 60))
        m6.meme_text(fr, "ENTERADO", size=110, y=454, scale=sc, dy=-int(50 * (sc - 1)))
        frames.append(fr); delays.append(ms)
    return frames, delays


def gracias_anim():
    """she squeezes the hug twice per loop while hearts float up at the sides."""
    rnd = random.Random(31)
    hearts = [(rnd.randint(4, 44) if k % 2 else rnd.randint(418, 458), k / 8, HEARTS[k % 3], rnd.randint(40, 56)) for k in range(8)]
    N = 12
    frames = []
    for i in range(N):
        t = i / N
        beat = max(0, math.sin(2 * math.pi * t * 2)) ** 2
        fr = Image.new("RGBA", (S, S))
        hug(fr, 1 + 0.05 * beat)
        for x, ph, code, sz in hearts:
            p_ = (ph + t) % 1
            e = m6.emoji(code, sz).copy()
            e.putalpha(e.getchannel("A").point(lambda a: int(a * min(1, (1 - p_) * 3, p_ * 6))))
            fr.alpha_composite(e, (int(x + 10 * math.sin(p_ * 6 + ph * 9)), int(330 - 240 * p_)))
        m6.meme_text(fr, "¡GRACIAS!", size=120, y=62, scale=1 + 0.06 * beat)
        frames.append(fr)
    return frames, [90] * N


# ======================================================================= tías
def listo_tia():
    return tia("listo_tia", "FANMADE_Pinkie_Pie_wink_vector", ("h", 440), (22, 24), (0.10, 0.16, 0.40, 0.50),
               ((255, 248, 215), (255, 190, 215)), [("¡Listo!", 112, GOLD, 266), ("Con el favor de Dios", 62, RAINBOW, 392)], 41,
               [("2705", 84, (414, 22), 8), ("1f339", 90, (-8, 408), -15), ("1f490", 96, (418, 404), 12)],
               [fluttering("1f98b", 50, (300, 40))])


def enterado_tia():
    return tia("enterado_tia", "FANMADE_Pinkies_Listening_by_Quasdar", ("h", 410), (40, 2), (0.55, 0.25, 0.92, 0.62),
               ((240, 238, 255), (200, 205, 255)), [("Enterado", 104, GOLD, 240), ("Dios te bendiga", 72, RAINBOW, 361)], 42,
               [("1f44d", 84, (14, 20), -8), ("1f339", 90, (-8, 408), -15), ("1f490", 96, (418, 404), 12)],
               [fluttering("1f98b", 50, (150, 60))])


def gracias_tia():
    return tia("gracias_tia", "FANMADE_Pinkie_Pie_by_AtomicGreymon", ("h", 470), (38, 12), (0.52, 0.20, 0.92, 0.52),
               ((255, 235, 245), (255, 185, 215)), [("¡Gracias!", 106, GOLD, 240), ("Dios te lo pague", 70, RAINBOW, 364)], 43,
               [("1f64f", 80, (8, 30), 0), ("1f339", 90, (-8, 408), -15), ("1f490", 96, (418, 404), 12)],
               [fluttering("1f98b", 50, (130, 70))])


STILLS = ("listo_fijo", "enterado_fijo", "gracias_fijo")
ANIMS = ("listo_anim", "enterado_anim", "gracias_anim", "listo_tia", "enterado_tia", "gracias_tia")

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for n in STILLS:
        if not want or n in want:
            save_still(n, globals()[n]()); print(n)
    for n in ANIMS:
        if not want or n in want:
            save_anim(n, *globals()[n]()); print(n)
