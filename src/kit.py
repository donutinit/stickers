"""Everyday reply kit (static): YA VOY, JAJAJA, NO., GRACIAS, ?, AH BUENO, ME VOY A DORMIR, NEL."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6
from deepfry import fry

S = 512
here = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(here, "kitframes")


def key_out_black(path):
    """flood-fill the black backdrop from the corners -> transparent."""
    im = Image.open(os.path.join(here, path)).convert("RGBA")
    rgb = im.convert("RGB")
    for c in ((0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)):
        ImageDraw.floodfill(rgb, c, (255, 0, 255), thresh=40)
    a = np.asarray(rgb)
    alpha = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
    im.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)))
    return im.crop(im.getbbox())


def fit(im, box):
    sc = min(box[0] / im.width, box[1] / im.height)
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def ya_voy():
    rnd = random.Random(1)
    rd = m6.load("rd/FANMADE_Rainbow_Dash_flying.png", h=430).rotate(-18, expand=True, resample=Image.BICUBIC)
    fr = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(fr)
    for _ in range(16):  # speed lines
        y = rnd.randint(20, 400); x = rnd.randint(-40, 200); L = rnd.randint(80, 200)
        d.line([(x, y), (x + L, y)], fill=(90, 160, 230, 255), width=rnd.randint(3, 6))
    for k, col in enumerate(m6.RAINBOW):  # rainbow trail from the left edge into her tail
        d.line([(-10, 250 + k * 9), (210, 215 + k * 9)], fill=col + (255,), width=10)
    fr.alpha_composite(rd, (S - rd.width + 20, -10))
    m6.meme_text(fr, "YA VOY", size=110)
    return fr


def jajaja():
    pk = m6.load("pp/FANMADE_Happy_Pinkie_Pie.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(pk, ((S - pk.width) // 2 + 30, 0))
    m6.meme_text(fr, "JAJAJA", size=120)
    return fry(fr)


def no():
    tw = Image.open(os.path.join(here, "m6/FANMADE_Twilight_Sparkle_reading_a_book_vector.png")).convert("RGBA")
    tw = tw.crop(tw.getbbox())
    W, H = tw.size  # close-up on the frowning face
    head = tw.crop((int(0.30 * W), 0, int(0.95 * W), int(0.85 * H)))
    head = fit(head, (S, S))
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(head, ((S - head.width) // 2, S - head.height))
    m6.meme_text(fr, "NO.", size=130, y=452)
    return fr


def gracias():
    fl = m6.load("m6/FANMADE_Fluttershy_being_cute.png", w=500)
    fr = Image.new("RGBA", (S, S))
    for code, xy, sz in (("1f496", (30, 40), 70), ("1f495", (400, 20), 80), ("1f496", (440, 170), 50), ("1f338", (10, 190), 60)):
        fr.alpha_composite(m6.emoji(code, sz), xy)
    fr.alpha_composite(fl, ((S - fl.width) // 2, 105))
    t = m6.grad_text("¡Gracias!", m6.PACIFICO, 100, [(255, 90, 170), (255, 150, 200), (255, 200, 90), (255, 90, 170)], 0.1)
    fr.alpha_composite(t, ((S - t.width) // 2, S - t.height - 8))
    return fr


def moai_q():
    import moai_common as mc
    fr = mc.moai_card(zoom=1.25, cx=0.55, cy=0.45)
    m6.meme_text(fr, "?", size=220, y=400)
    return fr


def ah_bueno():
    ra = m6.load("kit/FANMADE_Rarity_not_amused.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(ra, ((S - ra.width) // 2, 0))
    m6.meme_text(fr, "AH BUENO", size=110)
    return fr


def dormir():
    fl = fit(key_out_black("kit/FANMADE_fluttershy_taking_a_nap.png"), (500, 330))
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(fl, ((S - fl.width) // 2, 110))
    for sz, xy in ((60, (330, 70)), (80, (380, 10)), (46, (300, 110))):
        fr.alpha_composite(m6.emoji("1f4a4", sz), xy)
    m6.meme_text(fr, "ME VOY A DORMIR", size=90, y=462)
    return fr


def nel():
    aj = m6.load("kit/FANMADE_Applejack_is_not_amused_vector.png", h=S)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(aj, ((S - aj.width) // 2, 0))
    m6.meme_text(fr, "NEL", size=140, y=440)
    return fr


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in ("ya_voy", "jajaja", "no", "gracias", "moai_q", "ah_bueno", "dormir", "nel"):
        globals()[name]().save(os.path.join(OUT, name + ".png"))
        print(name)
