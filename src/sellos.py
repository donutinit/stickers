"""AUTORIZO / NO AUTORIZO: Twilight + rubber stamp slamming down."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import m6

S = 512
here = os.path.dirname(os.path.abspath(__file__))


def stamp(txt, col, w=440):
    """grungy double-bordered rubber stamp."""
    f = m6.fit_font(m6.IMPACT, txt, 110, w - 60, 0)
    l, t, r, b = f.getbbox(txt)
    h = (b - t) + 60
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, w - 5, h - 5], 18, outline=col + (255,), width=10)
    d.rounded_rectangle([18, 18, w - 19, h - 19], 10, outline=col + (255,), width=4)
    d.text((w / 2, h / 2), txt, font=f, fill=col + (255,), anchor="mm")
    rng = np.random.default_rng(len(txt))
    ink = (rng.random((h // 3 + 1, w // 3 + 1)) > 0.12).astype(np.uint8) * 255  # worn-ink speckle, 3px grains
    ink = np.asarray(Image.fromarray(ink).resize((w, h), Image.NEAREST)) / 255
    a = np.asarray(im.getchannel("A")) * (0.55 + 0.45 * ink)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def slam(pony, pony_xy, txt, col, rot, sy, flash_col):
    st = stamp(txt, col)
    frames, delays = [], []
    for i in range(14):
        fr = Image.new("RGBA", (S, S))
        k = i - 3  # stamp lands on k == 3
        sh = {3: (12, -9), 4: (-8, 6), 5: (4, -3)}.get(k, (0, 0))
        fr.alpha_composite(pony, (pony_xy[0] + sh[0], pony_xy[1] + sh[1]))
        if k >= 0:
            sc = {0: 2.6, 1: 1.9, 2: 1.35}.get(k, 1.0)
            s2 = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
            if k < 3:  # stamp still in the air: fainter
                s2.putalpha(s2.getchannel("A").point(lambda a: int(a * (0.35 + 0.2 * k))))
            fr.alpha_composite(s2, (int(S / 2 - s2.width / 2 + sh[0]), int(sy - s2.height / 2 + sh[1])))
        if k == 3:
            a = fr.getchannel("A")
            fl = Image.new("RGBA", (S, S), flash_col + (90,))
            fr.alpha_composite(fl); fr.putalpha(a.point(lambda v: max(v, 90)))
        frames.append(fr)
        delays.append(400 if i == 0 else 1800 if i == 13 else 70)
    return frames, delays


def autorizo():
    tw = m6.load("m6/MLP_The_Movie_Twilight_Sparkle_official_artwork_2.png", h=S)
    return slam(tw, ((S - tw.width) // 2, 0), "AUTORIZO", (20, 150, 50), 8, 425, (120, 255, 140))


def no_autorizo():
    tw = Image.open(os.path.join(here, "m6/FANMADE_Twilight_Sparkle_reading_a_book_vector.png")).convert("RGBA")
    tw = tw.crop(tw.getbbox())
    W, H = tw.size
    head = tw.crop((int(0.30 * W), 0, int(0.95 * W), int(0.85 * H)))
    sc = min(S / head.width, S / head.height)
    head = head.resize((int(head.width * sc), int(head.height * sc)), Image.LANCZOS)
    return slam(head, ((S - head.width) // 2, -40), "NO AUTORIZO", (210, 20, 25), -7, 450, (255, 90, 90))


# ---------------------------------------------------------------- static earrape versions
EYES = {"autorizo": [(150, 195), (215, 175)], "no_autorizo": [(233, 130), (298, 125)]}
EMOJI_SPOTS = {"autorizo": [("1f480", 400, 40, 15), ("1f525", 30, 300, -10), ("1f4af", 390, 230, 12), ("1f62d", 20, 20, -15)],
               "no_autorizo": [("1f480", 20, 250, -12), ("1f5ff", 420, 190, 10), ("1f525", 380, 260, 8), ("1f62d", 440, 20, 15)]}


def bulge(img, cx, cy, r, k=1.9):
    """fisheye: magnify everything within r of (cx, cy)."""
    a = np.asarray(img)
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(float)
    dx, dy = x - cx, y - cy
    dist = np.hypot(dx, dy)
    f = np.where(dist < r, (dist / r) ** (k - 1), 1.0)
    sx = np.clip(cx + dx * f, 0, w - 1).astype(int)
    sy = np.clip(cy + dy * f, 0, h - 1).astype(int)
    return Image.fromarray(a[sy, sx])


def lens_flare(fr, x, y, col):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for r, a in ((34, 90), (18, 170), (7, 255)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
    for L, w in ((150, 4), (90, 3)):
        d.line([(x - L, y), (x + L, y)], fill=(255, 255, 255, 230), width=w)
        d.line([(x, y - L * .45), (x, y + L * .45)], fill=(255, 255, 255, 200), width=w - 1)
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))


def earrape(name):
    from deepfry import fry
    frames, _ = globals()[name]()
    fr = frames[-1].copy()
    (x1, y1), (x2, y2) = EYES[name]
    cx, cy, R, K = (x1 + x2) / 2, (y1 + y2) / 2, 120, 1.7
    fr = bulge(fr, cx, cy, R, K)

    def moved(x, y):  # where a point lands after the bulge (inverse of its sampling map)
        dx, dy = x - cx, y - cy
        ds = math.hypot(dx, dy)
        if ds == 0 or ds >= R:
            return x, y
        dd = (ds * R ** (K - 1)) ** (1 / K)
        return cx + dx / ds * dd, cy + dy / ds * dd

    for code, x, y, rot in EMOJI_SPOTS[name]:
        fr.alpha_composite(m6.emoji(code, 96).rotate(rot, expand=True, resample=Image.BICUBIC), (x, y))
    col = (255, 30, 30) if name == "no_autorizo" else (40, 255, 80)
    for x, y in EYES[name]:
        lens_flare(fr, *moved(x, y), col)
    return fry(fr)


if __name__ == "__main__":
    for name in ("autorizo", "no_autorizo"):
        frames, delays = globals()[name]()
        d = os.path.join(here, "selloframes", name); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
        print(name)
        earrape(name).save(os.path.join(here, "selloframes", name + "_earrape.png"))
