"""Moai gigachad with a '?' slamming in on the vine-boom punch (overlays moai.py's frames)."""
import os
from PIL import Image
import m6

here = os.path.dirname(os.path.abspath(__file__))
src, dst = os.path.join(here, "moaiframes"), os.path.join(here, "moaiqframes")
os.makedirs(dst, exist_ok=True)
names = sorted(f for f in os.listdir(src) if f.endswith(".png"))
PUNCH = 14  # first vine-boom frame in moai.py
for i, n in enumerate(names):
    fr = Image.open(os.path.join(src, n)).convert("RGBA")
    k = i - PUNCH
    if k >= 0:
        m6.meme_text(fr, "?", scale={0: 2.0, 1: 1.3, 2: 0.95}.get(k, 1.0), size=260, y=300, dx=-150)  # over the back of the head, off the face
    fr.save(os.path.join(dst, n))
open(os.path.join(dst, "delays.txt"), "w").write(open(os.path.join(src, "delays.txt")).read())
print(len(names))
