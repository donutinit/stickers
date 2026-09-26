"""deepfry.py <in_dir> <out_dir> — deep-fry every frame (same recipe as the Fluttershy MLG sticker)."""
import io, os, shutil, sys
import numpy as np
from PIL import Image, ImageEnhance

S = 512
np.random.seed(69)


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
        small = rgb.resize((int(S * sc), int(S * sc)), Image.BILINEAR)
        buf = io.BytesIO(); small.save(buf, "JPEG", quality=q); buf.seek(0)
        rgb = Image.open(buf).convert("RGB").resize((S, S), Image.NEAREST)
    out = rgb.convert("RGBA"); out.putalpha(alpha)
    return out


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if f.endswith(".png"):
            fry(Image.open(os.path.join(src, f)).convert("RGBA")).save(os.path.join(dst, f))
    shutil.copy(os.path.join(src, "delays.txt"), dst)
    print(dst)
