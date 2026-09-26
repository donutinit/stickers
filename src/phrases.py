"""Stickers for specific phrases."""
import colorsys, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import m6
import tias
from tias import GOLD, RAINBOW, bokeh, rays, floaters, fluttering, spinner
from deepfry import fry

S = 512
here = os.path.dirname(os.path.abspath(__file__))


def save(name, frames, delays):
    d = os.path.join(here, "phframes", name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"f{i:02d}.png"))
    open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))


# 1 --------------------------------------------------------------------- static, long two-part meme
def vergazo():
    rd = m6.load("rd/FANMADE_proud_Rainbow_Dash_vector.png", h=300)
    fr = Image.new("RGBA", (S, S))
    fr.alpha_composite(rd, ((S - rd.width) // 2, 112))
    m6.meme_block(fr, "NO TENGO NADA EN CONTRA TU PUNTO,", 6, top=True, size=56, max_lines=2)
    m6.meme_block(fr, "PERO ME ESTÁS HABLANDO COMO SI ME AGUANTARAS UN VERGAZO", 506, top=False, size=52, max_lines=3)
    return [fr], [0]


# 2 --------------------------------------------------------------------- turbo, fried, shaking
def turbo():
    rnd = random.Random(2)
    rd = m6.load("rd/FANMADE_Rainbow_Dash_Flying_downwards.png", w=470)
    N = 12
    frames = []
    # she flies to the left; tail end is at the upper right of the sprite
    tail = (0.93, 0.12)
    for i in range(N):
        fr = Image.new("RGBA", (S, S))
        d = ImageDraw.Draw(fr)
        for _ in range(14):  # speed lines, outlined so they read on light and dark chats
            x = rnd.randint(-60, 560); y = rnd.randint(20, 400); L = rnd.randint(90, 220)
            seg = [(x, y), (x + L, y - L * 0.12)]
            d.line(seg, fill=(20, 40, 90, 255), width=9); d.line(seg, fill=(200, 240, 255, 255), width=5)
        jx, jy = rnd.randint(-14, 14), rnd.randint(-10, 10)
        px, py = (S - rd.width) // 2 + jx, 120 + jy
        tx, ty = px + tail[0] * rd.width, py + tail[1] * rd.height
        for k in range(5):  # flame trail streaming out of her tail
            fl = m6.emoji("1f525", 110 - k * 14 + rnd.randint(-8, 8)).rotate(-80 + rnd.randint(-12, 12), expand=True, resample=Image.BICUBIC)
            fx, fy = tx + k * 52, ty - k * 8
            fr.alpha_composite(fl, (int(fx - fl.width / 2), int(fy - fl.height / 2)))
        fr.alpha_composite(rd, (px, py))
        pulse = 1.0 + 0.08 * (i % 2)
        m6.meme_text(fr, "ME TURBO VALE PITO", scale=pulse, dx=rnd.randint(-6, 6), dy=rnd.randint(-5, 5), size=78, y=452)
        if i % 4 == 2:  # hue flash
            a = fr.getchannel("A")
            h, s_, v = fr.convert("RGB").convert("HSV").split()
            fr = Image.merge("HSV", (h.point(lambda x: (x + 90) % 256), s_, v)).convert("RGBA"); fr.putalpha(a)
        frames.append(fry(fr))
    return frames, [70] * N


# 3 --------------------------------------------------------------------- tía card
def valga():
    cfg = dict(out="valga", seed=31, pony="MLP_The_Movie_Twilight_Sparkle_official_artwork_2", fit=("h", 470), pos=(118, 14),
               face=(0.28, 0.20, 0.72, 0.42),
               bg=((250, 235, 255), (205, 170, 255)), radial=True,
               decorate_bg=lambda bg: (rays(bg, (255, 240, 200), alpha=60, center=(256, 180)), bokeh(bg, [(255, 255, 255), (255, 200, 240)], 20, 31)),
               behind=[],
               corners=[("1f339", 92, (-8, 405), -15), ("1f490", 96, (418, 402), 12), ("1f338", 66, (10, 170), 5), ("1f337", 66, (440, 170), -10)],
               front=[floaters(["1f496", "1f495"], 5, 32), fluttering("1f98b", 54, (30, 40))],
               texts=[("Que te valga", 84, GOLD, 300), ("Verga", 104, RAINBOW, 372)])
    frames, face = tias.build(cfg)
    dbg = frames[0].copy(); ImageDraw.Draw(dbg).rectangle(face, outline="cyan", width=2)
    dbg.save(os.path.join(here, "phframes", "valga_dbg.png"))
    return frames, [110] * len(frames)


# 4 --------------------------------------------------------------------- te amo
def te_amo():
    fl = m6.load("m6/FANMADE_Excited_Fluttershy_vector_by_Myardius.png", w=440)
    rnd = random.Random(4)
    bg = m6.vgrad((255, 225, 240), (255, 170, 205))
    bokeh(bg, [(255, 255, 255), (255, 120, 180)], 22, 4)
    N = 12
    burst = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0.6, 1.0), rnd.choice(["1f496", "1f497", "1f495", "1f498"])) for _ in range(12)]
    frames = []
    for i in range(N):
        t = i / N
        fr = bg.copy()
        beat = 1 + 0.12 * max(0, math.sin(2 * math.pi * t * 2)) ** 3  # heartbeat
        big = m6.emoji("1f497", int(300 * beat))
        fr.alpha_composite(big, ((S - big.width) // 2, 150 - big.height // 2 + 20))
        for ang, sp, code in burst:  # hearts flying outwards
            r = 60 + 260 * ((t * sp + ang / 6.3) % 1)
            e = m6.emoji(code, 44)
            x, y = 256 + r * math.cos(ang), 170 + r * math.sin(ang) * 0.8
            if not (140 < x < 380 and 200 < y < 330):  # keep off her face
                fr.alpha_composite(e, (int(x - 22), int(y - 22)))
        fr.alpha_composite(fl, ((S - fl.width) // 2, 400 - fl.height + 10))
        tx = m6.grad_text("Te Amo", m6.PACIFICO, int(110 * (0.97 + 0.03 * beat)), [(255, 60, 140), (255, 140, 190), (255, 60, 140)], t)
        fr.alpha_composite(tx, ((S - tx.width) // 2, S - tx.height - 6))
        frames.append(m6.rounded(fr))
    return frames, [100] * N


# 5 --------------------------------------------------------------------- 80 años después
def gray_mane(im, amt):
    """desaturate Rarity's purple mane/tail by amt (0..1) and lighten it towards silver."""
    a = np.asarray(im).astype(float)
    rgb = a[..., :3] / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    purple = (b > g + 0.08) & (r > g + 0.02) & (sat > 0.25)
    lum = rgb @ np.array([0.3, 0.59, 0.11])
    silver = np.clip(lum * 1.35 + 0.2, 0, 1)[..., None].repeat(3, -1)
    w = (purple * amt)[..., None]
    rgb = rgb * (1 - w) + silver * w
    a[..., :3] = rgb * 255
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def sepia(im, amt):
    a = np.asarray(im).astype(float)
    lum = a[..., :3] @ np.array([0.3, 0.59, 0.11])
    sep = np.stack([lum * 1.07, lum * 0.87, lum * 0.62], -1)
    a[..., :3] = np.clip(a[..., :3] * (1 - amt) + sep * amt, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def ochenta():
    ra = m6.load("m6/FANMADE_Rarity_vector_by_almostfictional.png", h=330)
    ox, oy = (S - ra.width) // 2, 120
    frames, delays = [], []
    TOP = "TE PUEDO ESPERAR A LOS 80 AÑOS"
    BOT = "Y ME VAS A SEGUIR PELANDO LA VERGA"
    # (age, caption?, bottom text?, ms). Holds are split into <=750ms frames that differ slightly (tiny bob),
    # so the encoder can't merge them into one long frame, which WhatsApp tends to cut short.
    seq = [(0, False, False, 670)] * 3 \
        + [(k / 4, True, False, 360) for k in range(5)] \
        + [(1, False, False, 750)] * 2 \
        + [(1, False, True, 670)] * 6
    for i, (age, caption, bottom, ms) in enumerate(seq):
        bob = (0, 2, 0, -2)[i % 4]
        fr = Image.new("RGBA", (S, S))
        fr.alpha_composite(gray_mane(ra, age), (ox, oy + bob))
        if age >= 1:  # old-lady props
            fr.alpha_composite(m6.emoji("1f453", 78), (ox + int(0.50 * ra.width), oy + bob + int(0.10 * ra.height)))
            fr.alpha_composite(m6.emoji("1f9af", 110).rotate(-10, expand=True), (ox + ra.width - 40, oy + ra.height - 150))
        fr = sepia(fr, 0.4 * age)
        if caption:  # SpongeBob-style caption card
            cap = m6.grad_text("80 años después...", m6.PACIFICO, 64, [(255, 240, 120), (255, 190, 60), (255, 240, 120)], i / 6,
                               stroke=(90, 40, 0), glow=(255, 200, 80), shadow=(60, 30, 0))
            fr.alpha_composite(cap, ((S - cap.width) // 2, 230 - cap.height // 2))
        m6.meme_block(fr, TOP, 6, top=True, size=56, max_lines=2)
        if bottom:
            m6.meme_block(fr, BOT, 506, top=False, size=54, max_lines=2)
        frames.append(fr)
        delays.append(ms)
    return frames, delays


if __name__ == "__main__":
    os.makedirs(os.path.join(here, "phframes"), exist_ok=True)
    for name in sys.argv[1:] or ("vergazo", "turbo", "valga", "te_amo", "ochenta"):
        save(name, *globals()[name]())
        print(name)
