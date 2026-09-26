"""10 'Buenos Días' Kratos stickers: tía aesthetics + real photos + every Kratos cut-out."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw
import m6
from chayanne import text, head, sparkles, rand_pts
from semana import photo, cut, glow_behind, cursive, floaters, cat_head, GOLD, PINKS

S = 512
N = 10
here = os.path.dirname(os.path.abspath(__file__))
SKY = [(255, 255, 255), (180, 240, 255), (255, 255, 255)]
RAIN = [(255, 240, 120), (255, 120, 200), (120, 220, 255), (255, 240, 120)]


def body(name, h=None, w=None):
    im = Image.open(os.path.join(here, "kratos", "cut", f"kratos_{name}.png")).convert("RGBA")
    sc = h / im.height if h else w / im.width
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def run(draw, n=N):
    return [m6.rounded(draw(i / n, i)) for i in range(n)]


def sun_rays(fr, t, c, r0, r1, col=(255, 230, 120), a=120, n=18):
    lay = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lay)
    for k in range(n):
        ang = 2 * math.pi * (k / n + t / n)
        d.polygon([(c[0] + r0 * math.cos(ang - .1), c[1] + r0 * math.sin(ang - .1)), (c[0] + r0 * math.cos(ang + .1), c[1] + r0 * math.sin(ang + .1)),
                   (c[0] + r1 * math.cos(ang), c[1] + r1 * math.sin(ang))], fill=col + (a,))
    fr.alpha_composite(lay)


# 1. leaping across the sunrise
def salto():
    bg = photo("amanecer.jpg", sat=1.3, focus=(0.6, 0.5)); k = body("salto", w=420); pts = rand_pts(1, 12, (0, 0, 0, 0))
    def f(t, i):
        fr = bg.copy(); sun_rays(fr, t, (400, 110), 40, 420)
        x = int(10 + 70 * t); y = int(110 - 30 * math.sin(math.pi * t))
        glow_behind(fr, k, (x, y), (255, 240, 200), 10, 180); fr.alpha_composite(k, (x, y))
        cursive(fr, "¡Buenos Días!", 4, 90, GOLD, t, glow=(255, 150, 60), shadow=(80, 40, 0))
        text(fr, ["Arriba que ya amaneció"], (S / 2, 470), 42, [(255, 255, 255, 255)], stroke=(160, 80, 20), shadow=(40, 20, 0))
        sparkles(fr, t, pts, (255, 240, 170)); return fr
    return run(f)


# 2. chains of fire in a tulip field
def cadenas():
    bg = photo("tulipanes.jpg", blur=3, sat=1.25, focus=(0.5, 0.6)); k = body("cadenas", h=430)  # blur keeps it < 500 KB
    def f(t, i):
        fr = bg.copy(); sun_rays(fr, t, (330, 60), 30, 400, (255, 200, 90), 90)
        k2 = k.rotate(4 * math.sin(2 * math.pi * t), expand=True, resample=Image.BICUBIC)
        glow_behind(fr, k2, (60, 60), (255, 220, 150), 12, 200); fr.alpha_composite(k2, (60, 60))
        cursive(fr, "Buenos Días", 4, 88, GOLD, t, glow=(255, 100, 40), shadow=(80, 20, 0))
        text(fr, ["Con toda la actitud"], (S / 2, 470), 44, [(255, 255, 255, 255)], stroke=(200, 40, 40), shadow=(60, 0, 0))
        return fr
    return run(f)


# 3. blades + bouquet on real roses
def espadas():
    bg = photo("rosas_pared.jpg", blur=3, sat=1.1, bright=1.05); k = body("espadas", h=420); ramo = cut("ramo", w=190)
    def f(t, i):
        fr = bg.copy()
        glow_behind(fr, k, (40, 70), (255, 255, 255), 10, 210); fr.alpha_composite(k, (40, 70))
        r = ramo.rotate(6 * math.sin(2 * math.pi * t), expand=True, resample=Image.BICUBIC); fr.alpha_composite(r, (310, 250))
        floaters(fr, t, ["1f496", "1f495"], [20, 440, 470])
        cursive(fr, "Buenos Días", 4, 90, PINKS, t, stroke=(200, 30, 90), glow=(255, 80, 150))
        text(fr, ["Con cariño para ti"], (S / 2, 470), 44, [(255, 255, 255, 255)], stroke=(200, 30, 120), shadow=(80, 0, 50))
        return fr
    return run(f)


# 4. gauntlets at the beach
def guanteletes():
    bg = photo("playa.jpg", sat=1.2); k = body("guanteletes", h=390)
    def f(t, i):
        fr = bg.copy(); hop = abs(math.sin(2 * math.pi * t))
        x, y = (S - k.width) // 2, int(100 - 14 * hop)
        glow_behind(fr, k, (x, y), (255, 255, 255), 10, 200); fr.alpha_composite(k, (x, y))
        fr.alpha_composite(m6.emoji("1f4aa", 80), (20, 330)); fr.alpha_composite(m6.emoji("1f4aa", 80).transpose(Image.FLIP_LEFT_RIGHT), (412, 330))
        cursive(fr, "Buenos Días", 4, 90, SKY, t, stroke=(20, 120, 180), glow=(80, 200, 255), shadow=(0, 50, 90))
        text(fr, ["A darle con todo"], (S / 2, 470), 46, [(255, 255, 255, 255)], stroke=(20, 120, 180), shadow=(0, 40, 70))
        return fr
    return run(f)


# 5. armour, lying in daisies
def armadura():
    bg = photo("margaritas.jpg", blur=2.5, sat=1.2, focus=(0.5, 0.6)); k = body("armadura", w=470); pts = rand_pts(5, 10, (20, 150, 490, 380))
    def f(t, i):
        fr = bg.copy()
        y = 170 + int(3 * math.sin(2 * math.pi * t))
        glow_behind(fr, k, ((S - k.width) // 2, y), (255, 255, 255), 10, 200); fr.alpha_composite(k, ((S - k.width) // 2, y))
        for j, (x, yy) in enumerate(((330, 120), (370, 90), (410, 60))):  # zzz
            p = (t + j / 3) % 1
            e = m6.emoji("1f4a4", int(30 + 16 * j)).copy(); e.putalpha(e.getchannel("A").point(lambda a: int(a * (1 - p * .6))))
            fr.alpha_composite(e, (x, int(yy - 20 * p)))
        cursive(fr, "Buenos Días", 4, 90, GOLD, t, glow=(255, 120, 200), shadow=(80, 0, 60))
        text(fr, ["Ya me levanté", "(más o menos)"], (S / 2, 430), 42, [(255, 255, 255, 255), (255, 220, 240, 255)], stroke=(200, 40, 130), shadow=(60, 0, 40))
        sparkles(fr, t, pts); return fr
    return run(f)


# 6. face in a real sunflower
def girasol():
    bg = photo("amanecer.jpg", blur=5, sat=1.3, focus=(0.5, 0.4)); flor = cut("girasol", w=540)
    face = head("kratos_serio.png", 195)
    circ = Image.new("L", face.size); ImageDraw.Draw(circ).ellipse([0, 0, face.width, face.height], fill=255)
    face.putalpha(Image.fromarray(np.minimum(np.asarray(face.getchannel("A")), np.asarray(circ))))
    def f(t, i):
        fr = bg.copy(); sw = 3 * math.sin(2 * math.pi * t)
        fl = flor.rotate(sw, resample=Image.BICUBIC); fx, fy = (S - fl.width) // 2, 30
        fr.alpha_composite(fl, (fx, fy))
        fr.alpha_composite(face.rotate(sw, expand=True, resample=Image.BICUBIC), (int(fx + fl.width * 0.465 - face.width / 2), int(fy + fl.height * 0.34 - face.height / 2)))
        floaters(fr, t, ["2728", "1f496"], [20, 70, 440])
        cursive(fr, "Buenos Días", 4, 90, GOLD, t, glow=(255, 150, 40), shadow=(80, 40, 0))
        cursive(fr, "Que Dios te bendiga", -8, 58, PINKS, t, stroke=(200, 110, 0), glow=(255, 180, 60), shadow=(90, 50, 0))
        return fr
    return run(f)


# 7. primero el cafecito
def cafe():
    bg = photo("tulipanes.jpg", blur=6, sat=1.2); hd = head("kratos_enojado.png", 290); cup = cut("cafe", w=230)
    def f(t, i):
        fr = bg.copy()
        glow_behind(fr, hd, (30, 90), (255, 255, 255), 10, 200); fr.alpha_composite(hd, (30, 90))
        glow_behind(fr, cup, (270, 300), (255, 255, 255), 10, 220); fr.alpha_composite(cup, (270, 300))
        for j in range(3):
            p = (t + j / 3) % 1
            e = m6.emoji("2615" if j == 1 else "1f495", int(28 + 18 * p)).copy(); e.putalpha(e.getchannel("A").point(lambda a: int(a * (1 - p))))
            fr.alpha_composite(e, (int(385 + 16 * math.sin(p * 7 + j) - e.width / 2), int(300 - 130 * p)))
        cursive(fr, "Buenos Días", 4, 90, GOLD, t, glow=(255, 150, 60), shadow=(80, 40, 0))
        text(fr, ["Primero el cafecito"], (S / 2, 478), 42, [(255, 255, 255, 255)], stroke=(120, 60, 20), shadow=(40, 20, 0))
        return fr
    return run(f)


# 8. butterfly lands on his head
def mariposa():
    bg = photo("margaritas.jpg", blur=4, sat=1.2); hd = head("kratos_barba.png", 520).crop((0, 0, 99999, 360)); hd = hd.crop(hd.getbbox())
    bf = cut("mariposa", h=130); pts = rand_pts(8, 12, (80, 60, 440, 440))
    def f(t, i):
        fr = bg.copy(); hx = (S - hd.width) // 2
        glow_behind(fr, hd, (hx, 110), (255, 255, 255), 10, 200); fr.alpha_composite(hd, (hx, 110))
        land = min(1, t * 1.6)
        x = 420 - (420 - (hx + hd.width * 0.5)) * land; y = 90 + (130 - 90) * land - 40 * math.sin(math.pi * land)
        flap = 0.5 + 0.5 * abs(math.cos(2 * math.pi * t * (3 if land < 1 else 1)))
        b = bf.resize((int(bf.width * flap), bf.height)); fr.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
        cursive(fr, "Buenos Días", 4, 90, [(255, 200, 80), (255, 140, 60), (255, 220, 140), (255, 200, 80)], t, glow=(255, 120, 60), shadow=(80, 30, 0))
        text(fr, ["Hermosa mañana"], (S / 2, 474), 46, [(255, 255, 255, 255)], stroke=(200, 90, 20), shadow=(60, 20, 0))
        sparkles(fr, t, pts); return fr
    return run(f)


# 9. screaming good morning to the world
def grito():
    bg = photo("amanecer.jpg", sat=1.35, focus=(0.5, 0.35)); k = head("kratos_grito.png", 400)
    def f(t, i):
        fr = bg.copy(); sun_rays(fr, t, (256, 200), 60, 460, (255, 240, 150), 110, 24)
        s = 1 + 0.03 * abs(math.sin(2 * math.pi * t * 2)); k2 = k.resize((int(k.width * s), int(k.height * s)))
        x, y = (S - k2.width) // 2, S - k2.height + 10
        glow_behind(fr, k2, (x, y), (255, 240, 200), 12, 200); fr.alpha_composite(k2, (x, y))
        cursive(fr, "¡BUENOS DÍAS!", 4, 88, RAIN, t, glow=(255, 60, 200), shadow=(60, 0, 60))
        text(fr, ["MUNDO"], (S / 2, 150), 64, [(255, 255, 255, 255)], stroke=(200, 60, 20), shadow=(60, 20, 0))
        return fr
    return run(f)


# 10. cat filter, sin ganas pero con fe
def gatito():
    bg = photo("rosas_pared.jpg", blur=3, sat=1.1, bright=1.05); kat = cat_head(300); pts = rand_pts(10, 12, (0, 180, 330, 512))
    def f(t, i):
        fr = bg.copy(); bob = int(5 * math.sin(2 * math.pi * t))
        glow_behind(fr, kat, (-20, S - kat.height + 40 + bob), (255, 255, 255), 10, 200); fr.alpha_composite(kat, (-20, S - kat.height + 40 + bob))
        fr.alpha_composite(m6.emoji("1f64f", 84), (400, 400))
        cursive(fr, "Buenos Días", 4, 90, PINKS, t, stroke=(200, 30, 90), glow=(255, 80, 150))
        text(fr, ["SIN GANAS", "PERO CON FE"], (S - 16, 200), 44, [(120, 60, 200, 255), (230, 60, 150, 255)], anchor="rm", maxw=250)
        sparkles(fr, t, pts); return fr
    return run(f)


ALL = ("salto", "cadenas", "espadas", "guanteletes", "armadura", "girasol", "cafe", "mariposa", "grito", "gatito")

if __name__ == "__main__":
    for name in sys.argv[1:] or ALL:
        frames = globals()[name]()
        d = os.path.join(here, "bdframes", name); os.makedirs(d, exist_ok=True)
        for x in os.listdir(d):
            os.remove(os.path.join(d, x))
        for i, fr in enumerate(frames):
            fr.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(["110"] * len(frames)))
        print(name)
