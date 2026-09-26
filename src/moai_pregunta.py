"""Moai gigachad with a '?' at the bottom (overlays moai.py's frames)."""
import os
from PIL import Image
import m6

here = os.path.dirname(os.path.abspath(__file__))
src, dst = os.path.join(here, "moaiframes"), os.path.join(here, "moaiqframes")
os.makedirs(dst, exist_ok=True)
names = sorted(f for f in os.listdir(src) if f.endswith(".png"))
for i, n in enumerate(names):
    fr = Image.open(os.path.join(src, n)).convert("RGBA")
    m6.meme_text(fr, "?", size=120, y=452)  # same moai, just a "?" at the bottom
    fr.save(os.path.join(dst, n))
open(os.path.join(dst, "delays.txt"), "w").write(open(os.path.join(src, "delays.txt")).read())
print(len(names))
