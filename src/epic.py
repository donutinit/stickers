import io, math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

random.seed(420)
S = 512
N = 24
here = os.path.dirname(os.path.abspath(__file__))
base = Image.open(os.path.join(here, "flutter.png")).convert("RGBA")
font = ImageFont.truetype(os.path.expanduser("~/.local/share/fonts/Impact.TTF"), 120)
small = ImageFont.truetype(os.path.expanduser("~/.local/share/fonts/Impact.TTF"), 44)


def glasses(p=5):
    # pixel-art "deal with it" glasses
    W, H = 28, 6
    g = Image.new("RGBA", (W * p, H * p), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    px = lambda x, y, c: d.rectangle([x * p, y * p, x * p + p - 1, y * p + p - 1], fill=c)
    for x in range(W):
        px(x, 0, "black")
    for lens in (2, 16):
        for y in range(1, 5):
            inset = 1 if y == 4 else 0
            for x in range(lens + inset, lens + 10 - inset):
                px(x, y, "black")
        px(lens + 1, 1, "white"); px(lens + 2, 1, "white")
        px(lens + 2, 2, "white"); px(lens + 3, 2, "white")
    return g.rotate(-6, expand=True, resample=Image.NEAREST)


GL = glasses()


def dorito(size):
    t = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.polygon([(size / 2, 2), (size - 2, size - 2), (2, size - 2)], fill=(245, 140, 20), outline=(150, 60, 0))
    for _ in range(6):
        x, y = random.uniform(size * .35, size * .65), random.uniform(size * .45, size * .85)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(200, 40, 0))
    return t


DOR = dorito(90)


def hitmarker(d, x, y, r=36):
    for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        a, b = (x + dx * 8, y + dy * 8), (x + dx * r, y + dy * r)
        d.line([a, b], fill="black", width=9)
        d.line([a, b], fill="white", width=5)


def outlined(d, xy, txt, f, fill="white", sw=7, anchor="mm"):
    d.text(xy, txt, font=f, fill=fill, stroke_width=sw, stroke_fill="black", anchor=anchor)


def hue_shift(img, deg):
    h, s, v = img.convert("RGB").convert("HSV").split()
    h = h.point(lambda x: (x + int(deg / 360 * 255)) % 256)
    return Image.merge("HSV", (h, s, v)).convert("RGB")


def fry(rgba):
    alpha = rgba.getchannel("A").point(lambda a: 255 if a > 100 else 0)
    rgb = Image.new("RGB", rgba.size, (40, 0, 0))
    rgb.paste(rgba, mask=rgba.getchannel("A"))
    rgb = ImageEnhance.Color(rgb).enhance(3.2)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.7)
    rgb = ImageEnhance.Sharpness(rgb).enhance(10)
    arr = np.asarray(rgb).astype(np.int16)
    arr = arr + np.random.randint(-28, 28, arr.shape)
    arr[..., 0] += 25; arr[..., 2] -= 20  # deep-fried orange cast
    rgb = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    for q, sc in ((7, 0.55), (5, 0.8), (9, 1.0)):
        small_ = rgb.resize((int(S * sc), int(S * sc)), Image.BILINEAR)
        buf = io.BytesIO(); small_.save(buf, "JPEG", quality=q); buf.seek(0)
        rgb = Image.open(buf).convert("RGB").resize((S, S), Image.NEAREST)
    out = rgb.convert("RGBA"); out.putalpha(alpha)
    return out


def sunburst(angle, scale):
    n, R = 16, 300
    b = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    c = S / 2
    for k in range(n):
        a0 = math.radians(angle + k * 360 / n)
        a1 = a0 + math.radians(360 / n / 2)
        col = (255, 60, 0, 255) if k % 2 else (255, 200, 0, 255)
        d.polygon([(c, c), (c + R * scale * math.cos(a0), c + R * scale * math.sin(a0)),
                   (c + R * scale * math.cos(a1), c + R * scale * math.sin(a1))], fill=col)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([c - 250 * scale, c - 250 * scale, c + 250 * scale, c + 250 * scale], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(20))
    b.putalpha(Image.fromarray((np.asarray(b.getchannel("A")) * (np.asarray(mask) / 255)).astype(np.uint8)))
    return b


frames = []
for i in range(N):
    drop = i < 6
    intensity = 0.3 if drop else 1.5
    beat = (i - 6) % 6 if not drop else 99  # zoom punch every 6 frames
    zoom = 1.0 + ({0: 0.22, 1: 0.12, 2: 0.05}.get(beat, 0.03 * math.sin(i * 1.3)))
    frame = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if not drop:
        frame.alpha_composite(sunburst(i * 7.5, 1.25 if beat == 0 else 1.0))

    # pony + glasses on their own layer so they shake together
    pony = base.copy()
    gy = -60 + (175 * i / 5) if drop else 115
    pony.alpha_composite(GL, (int(122 - GL.width / 2), int(gy - GL.height / 2)))
    sz = int(S * zoom)
    pony = pony.resize((sz, sz), Image.BICUBIC).rotate(random.uniform(-7, 7) * intensity, resample=Image.BICUBIC)
    jx, jy = [int(random.uniform(-14, 14) * intensity) for _ in range(2)]
    frame.alpha_composite(pony, ((S - sz) // 2 + jx, (S - sz) // 2 + jy))

    d = ImageDraw.Draw(frame)
    if not drop:
        for k in range(2):  # spinning doritos
            dor = DOR.rotate(i * 47 + k * 120, expand=True)
            pos = [(400, 30), (20, 250)][k]
            frame.alpha_composite(dor, (pos[0] + random.randint(-6, 6), pos[1] + random.randint(-6, 6)))
        for _ in range(random.randint(2, 5)):
            hitmarker(d, random.randint(60, 450), random.randint(60, 360))
        if i % 3 == 0:
            outlined(d, (random.randint(110, 400), random.randint(200, 330)),
                     random.choice(["360 NOSCOPE", "REKT", "WOMBO COMBO"]), small,
                     fill=random.choice(["#00ff00", "#ff00ff", "#ffff00", "#00ffff"]), sw=4)

    t_j = 10 if not drop else 3
    outlined(d, (S / 2 + random.randint(-t_j, t_j), 440 + random.randint(-t_j, t_j)), "VETE ALV", font, sw=8)

    if not drop and i % 4 == 1:  # rainbow flashes
        a = frame.getchannel("A")
        frame = hue_shift(frame, (i * 97) % 360).convert("RGBA"); frame.putalpha(a)

    if beat == 0:  # impact flash
        a = frame.getchannel("A")
        frame = Image.blend(frame.convert("RGB"), Image.new("RGB", (S, S), "white"), 0.55).convert("RGBA")
        frame.putalpha(a)
    frames.append(fry(frame))

os.makedirs(os.path.join(here, "frames"), exist_ok=True)
for i, f in enumerate(frames):
    f.save(os.path.join(here, "frames", f"f{i:02d}.png"))
print("ok", len(frames))
